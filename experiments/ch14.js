/* experiments/ch14.js — 第 14 课:实验 + 第一旗舰动画(写入全路径) */
(function () {
  'use strict';

  /* ===== 第一旗舰动画:一次写入的完整旅程 ===== */
  /* 舞台:上行 = 请求链(客户端 → 协调节点路由 → 主分片);
     下行 = 主分片内部与外围(index buffer / segments / translog / 副本),
     底部 = GET 与 SEARCH 两个视角 + 本步结局。
     与 ch01(只到可见性)、ch13(只到 bulk 分发)不重复:这里画完整存储生命周期。 */

  var OUTCOMES = [
    'PUT /idx/_doc/1 发出 · 存储层还没被碰过',
    'murmur3("1") % 5 → shard 0 · 只锁定主分片',
    'version 检查通过 → indexWriter.addDocuments · 尚不可搜',
    'translog.add → ensureSynced(fsync)· 按 seqNo 复制给副本',
    '201 Created 返回 · GET 已可见,SEARCH 仍 0 hits',
    'refresh:buffer → seg1 · buffer 清空 · translog 不动',
    'merge:小段并大段 · 软删除的旧文档被物理回收',
    'flush:IndexWriter.commit → segments_N · translog 归零'
  ];

  var NOTES = [
    '起点只有一件事:客户端把 PUT /idx/_doc/1 发向集群。第 13 课的接力棒在这里交接——之前所有层都没碰存储;接下来每一步都在回答同一个问题:这篇文档现在躺在哪。',
    '协调节点不存数据:解析请求,按 murmur3(有效键) % 主分片数 算出唯一落点(有 routing 用 routing,没有就用 _id),动作转成 indices:data/write/index[p] 发往持有主分片的节点。bulk 的每一行都是独立这么算的。',
    '主分片上 InternalEngine.index 开工:先 version 检查(indexingStrategyForOperation,冲突根本不写),再 indexWriter.addDocuments 进内存缓冲。注意顺序——先 Lucene 后 translog,与教科书 WAL 相反;此刻两种存放开始分头服务两种保证。',
    'translog.add 在 Lucene 成功之后:记下这条 Index 操作。默认 durability=request,TransportWriteAction 的 AsyncAfterWriteAction 要等 ensureSynced fsync 完才放行 201;同时按同 seqNo 把操作复制给副本,副本本地再走一遍写入。',
    '201 返回了。此刻这篇文档同时躺在:内存 buffer、translog(已 fsync)、VersionMap。GET(realtime)第一站问 VersionMap,立即可见;SEARCH 只认 EXTERNAL searcher,而没有任何 segment 装着它——0 hits。fsync 管的是耐久,不是可见性。',
    'refresh_interval 到点或手动 _refresh:maybeRefreshBlocking 把 buffer 做成一个 NRT segment,EXTERNAL searcher 换新快照——SEARCH 看得见了。buffer 清空;translog 原封不动:refresh 不 commit、不裁日志,这正是它与 flush 的分界线。',
    '每次 refresh 都可能留下小 segment,写得多段就多。Lucene 后台 merge 把小段合成大段:搜索打开的文件变少,软删除的旧版本文档在合并中物理丢弃。合并落后时 IndexThrottle 卡写入线程——背压,不是错误。',
    'flush 才是 Lucene commit:rollGeneration 冻结旧日志 → IndexWriter.commit 写出 segments_N(commit user data 带 local checkpoint)→ 内部 refresh 清 VersionMap → trim 删掉不再需要的 .tlog。崩溃恢复从最后 commit 打开,只重放其后的日志。'
  ];

  var ROW_A = [
    { x: 10, w: 150, sub: '① 客户端', main: 'PUT /idx/_doc/1', cls: 'fig-key' },
    { x: 196, w: 180, sub: '② 协调节点', main: 'murmur3(_id) % 5', cls: 'fig-key' },
    { x: 412, w: 180, sub: '③ 主分片 shard 0', main: 'InternalEngine.index', cls: 'fig-key' }
  ];
  var HOT_A = [0, 1, 2, 2, 3, 3, 3, 3]; /* 3 = 全亮,链路走完 */

  /* 下行四块存放:buffer / segments / translog / replica */
  var BOXES = [
    { x: 15, w: 140, sub: 'IndexWriter 内存', name: 'index buffer' },
    { x: 215, w: 190, sub: 'SEARCH 只看这里', name: 'segments' },
    { x: 427, w: 150, sub: '预写日志 · 耐久', name: 'translog' },
    { x: 599, w: 145, sub: '副本 · 同 seqNo', name: 'replica' }
  ];
  var B_STATE = [
    ['dim', 'dim', 'dim', 'dim'],
    ['dim', 'dim', 'dim', 'dim'],
    ['hot', 'dim', 'dim', 'dim'],
    ['lit', 'dim', 'hot', 'lit'],
    ['lit', 'lit', 'dim', 'lit'],
    ['hot', 'lit', 'hot', 'lit'],
    ['lit', 'lit', 'hot', 'lit'],
    ['lit', 'hot', 'hot', 'lit']
  ];
  function keyOf(step) {
    return [
      step < 2 ? '空' : (step < 5 ? 'Doc1(addDocuments)' : 'refresh 后清空'),
      step < 5 ? '无 segment'
        : (step === 5 ? 'seg1(NRT·未 commit)'
        : (step === 6 ? 'seg1+2 → merge 中' : 'segments_N(commit)')),
      step < 3 ? '空' : (step < 5 ? 'Index Doc1 + fsync' : (step < 7 ? 'refresh 不动它' : '已裁剪(flush)')),
      step < 3 ? '等待复制' : 'Doc1(同 seqNo)'
    ];
  }

  function stepSvg(step) {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">';
    s += '<defs><marker id="ah14z" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
      + '<path d="M 0 0 L 10 5 L 0 10 z" class="fig-arrowhead"/></marker></defs>';

    /* 上行:请求链 */
    var hotA = HOT_A[step];
    for (var i = 0; i < ROW_A.length; i++) {
      var a = ROW_A[i];
      if (i < ROW_A.length - 1) {
        s += '<line x1="' + (a.x + a.w + 4) + '" y1="47" x2="' + (ROW_A[i + 1].x - 6)
          + '" y2="47" class="fig-arrow" marker-end="url(#ah14z)"'
          + (i < hotA ? '' : ' opacity="0.35"') + '/>';
      }
      var hot = i === hotA;
      s += '<g opacity="' + (i <= hotA ? 1 : 0.4) + '">';
      s += '<rect x="' + a.x + '" y="16" width="' + a.w + '" height="62" rx="9" class="'
        + (hot ? 'fig-box-hot fp-pop' : 'fig-box') + '"/>';
      s += '<text x="' + (a.x + a.w / 2) + '" y="40" text-anchor="middle" class="fig-sub">' + a.sub + '</text>';
      s += '<text x="' + (a.x + a.w / 2) + '" y="62" text-anchor="middle" class="' + a.cls + '">' + a.main + '</text>';
      s += '</g>';
    }

    /* 换轨:主分片 → 存储层(step2 起,先指 buffer;step3 起分叉到 translog) */
    if (step >= 2) {
      s += '<path d="M 502 82 L 502 104 L 92 104 L 92 144" class="fig-arrow fp-draw" pathLength="1" marker-end="url(#ah14z)"/>';
      s += '<text x="290" y="98" text-anchor="middle" class="fig-sub">下层 = 主分片内部与副本</text>';
    }
    if (step >= 3) {
      s += '<line x1="502" y1="104" x2="502" y2="144" class="fig-arrow fp-draw" pathLength="1" marker-end="url(#ah14z)"/>';
      s += '<path d="M 585 80 C 655 95 700 120 671 144" class="fig-arrow fp-draw" pathLength="1" marker-end="url(#ah14z)"/>';
      s += '<text x="688" y="112" text-anchor="middle" class="fig-sub">同 seqNo 复制</text>';
    }

    /* 下行:四块存放 */
    var st = B_STATE[step];
    var keys = keyOf(step);
    for (var j = 0; j < 4; j++) {
      var b = BOXES[j];
      var state = st[j];
      s += '<g opacity="' + (state === 'dim' ? 0.35 : 1) + '">';
      s += '<rect x="' + b.x + '" y="150" width="' + b.w + '" height="92" rx="9" class="'
        + (state === 'hot' ? 'fig-box-hot fp-pop' : 'fig-box') + '"/>';
      s += '<text x="' + (b.x + b.w / 2) + '" y="176" text-anchor="middle" class="fig-sub">' + b.sub + '</text>';
      s += '<text x="' + (b.x + b.w / 2) + '" y="200" text-anchor="middle" class="fig-name">' + b.name + '</text>';
      s += '<text x="' + (b.x + b.w / 2) + '" y="224" text-anchor="middle" class="fig-key">' + keys[j] + '</text>';
      s += '</g>';
    }

    /* refresh 箭头:buffer → segments(step5 起) */
    if (step >= 5) {
      s += '<line x1="157" y1="196" x2="211" y2="196" class="fig-arrow fp-draw" pathLength="1" marker-end="url(#ah14z)"/>';
      s += '<text x="184" y="186" text-anchor="middle" class="fig-sub">refresh</text>';
    }
    /* merge 小弧:segments 内部(step6 起) */
    if (step >= 6) {
      s += '<path d="M 377 180 A 15 15 0 1 0 377 210" class="fig-arrow fp-draw" pathLength="1" marker-end="url(#ah14z)"/>';
    }

    /* 两个可见性视角 */
    var getPill = step < 2 ? 'GET:还没写进来' : (step < 5 ? 'GET:可见(VersionMap)' : 'GET:可见(searcher)');
    var srPill = step < 5 ? 'SEARCH:不可见(0 hits)' : 'SEARCH:可见(EXTERNAL)';
    s += '<rect x="110" y="248" width="240" height="22" rx="11" class="fig-box"/>';
    s += '<text x="230" y="263" text-anchor="middle" class="fig-key">' + getPill + '</text>';
    s += '<rect x="410" y="248" width="240" height="22" rx="11" class="fig-box"/>';
    s += '<text x="530" y="263" text-anchor="middle" class="fig-key">' + srPill + '</text>';

    /* 底部:本步结局 */
    s += '<text x="380" y="292" text-anchor="middle" class="fig-key">' + OUTCOMES[step] + '</text>';
    s += '</svg>';
    return s;
  }

  window.ESFLOWS = window.ESFLOWS || {};
  window.ESFLOWS['ch14-write-path'] = {
    version: 1,
    id: 'ch14-write-path',
    title: '一次写入的完整旅程:从内存缓冲到 commit 点',
    speed: 2200,
    steps: NOTES.map(function (note, i) { return { svg: stepSvg(i), note: note }; })
  };

  /* ===== 实验 1:关掉定时 refresh,拆开「可见」与「已 commit」 ===== */
  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};
  window.ESEXPERIMENTS['ch14-00-nrt-setup'] = {
    version: 1, id: 'ch14-00-nrt-setup',
    title: '实验 1 · 建索引 tut-l14-nrt(关定时 refresh)',
    method: 'PUT', path: '/tut-l14-nrt',
    body: { settings: { number_of_shards: 1, number_of_replicas: 0, refresh_interval: -1 } },
    predict: 'refresh_interval=-1 关掉的是谁的时钟?GET 会被拖慢吗?',
    expect: 'created/acknowledged: true。关的是 SEARCH 的可见性时钟(不再自动把 buffer 变 segment);GET 走 realtime 路径,一毫秒都不多等(第 10 课)。0 副本让单节点保持 green,排除复制干扰。'
  };
  window.ESEXPERIMENTS['ch14-01-nrt-put'] = {
    version: 1, id: 'ch14-01-nrt-put',
    title: '实验 1 · 写入 _id=1(不带 refresh)',
    method: 'PUT', path: '/tut-l14-nrt/_doc/1',
    body: { title: 'engine-nrt', views: 14 },
    predict: 'result 是什么?此刻这篇文档同时躺在哪几处?',
    expect: 'result: created。三处:IndexWriter 内存缓冲、translog 的一条 Index 操作、VersionMap 条目;任何 segment 里都没有。回 201 之前,TransportWriteAction.AsyncAfterWriteAction 已按 durability=request 完成一次 fsync——耐久已经定了,可见性还没有。'
  };
  window.ESEXPERIMENTS['ch14-02-nrt-get'] = {
    version: 1, id: 'ch14-02-nrt-get',
    title: '实验 1 · 立刻 GET(默认 realtime)',
    method: 'GET', path: '/tut-l14-nrt/_doc/1?filter_path=found,_id,_version,_source',
    body: null,
    predict: '还没 refresh,拿得到吗?_version 是多少?',
    expect: 'found: true,_version: 1,带完整 _source。realtime 路径第一站是 LiveVersionMap;trackTranslogLocation 默认 false,第一次 GET 常由 refreshIfNeeded("realtime_get") 推 INTERNAL searcher 从段读,并顺手打开跟踪——第 10 课走过完整链,这里只确认它不依赖 EXTERNAL。'
  };
  window.ESEXPERIMENTS['ch14-03-nrt-search'] = {
    version: 1, id: 'ch14-03-nrt-search',
    title: '实验 1 · 立刻 SEARCH(应扑空)',
    method: 'POST', path: '/tut-l14-nrt/_search?filter_path=hits.total',
    body: { query: { match: { title: 'engine-nrt' } } },
    predict: 'GET 都拿到了,match title:engine-nrt 呢?',
    expect: 'hits.total.value = 0。SEARCH 只认 EXTERNAL searcher;refresh_interval=-1 把「可能扑空」变成「一定扑空」。注意:此刻文档早已 fsync——耐久与可见性互不代言。'
  };
  window.ESEXPERIMENTS['ch14-04-nrt-refresh'] = {
    version: 1, id: 'ch14-04-nrt-refresh',
    title: '实验 1 · 手动 _refresh',
    method: 'POST', path: '/tut-l14-nrt/_refresh?filter_path=_shards',
    body: null,
    predict: 'refresh 做了什么、没做什么?猜猜下一步 translog 统计会不会变。',
    expect: '_shards.successful = 1。InternalEngine.refresh(source) 固定 EXTERNAL + 阻塞:maybeRefreshBlocking 把 buffer 做成 NRT segment、换外部 searcher;不 commit、不裁 translog——分界线马上用数字验证。'
  };
  window.ESEXPERIMENTS['ch14-05-nrt-search-hit'] = {
    version: 1, id: 'ch14-05-nrt-search-hit',
    title: '实验 1 · 再 SEARCH(命中)',
    method: 'POST', path: '/tut-l14-nrt/_search?filter_path=hits.total',
    body: { query: { match: { title: 'engine-nrt' } } },
    predict: 'hits.total 这次是多少?',
    expect: '1。新 segment 进入 EXTERNAL 快照,buffer 已清空。但 translog 一条没少——下一步看统计。'
  };
  window.ESEXPERIMENTS['ch14-06-nrt-stats'] = {
    version: 1, id: 'ch14-06-nrt-stats',
    title: '实验 1 · _stats/translog:refresh 之后日志还在',
    method: 'GET', path: '/tut-l14-nrt/_stats/translog?filter_path=indices.tut-l14-nrt.primaries.translog',
    body: null,
    predict: '刚 refresh 过,uncommitted_operations 是 0 吗?',
    expect: '不是:operations / uncommitted_operations ≥ 1(以你的返回为准)。字段名出自 TranslogStats.toXContent;uncommitted_* 统计 safe commit 的 local checkpoint 之后的 generation(Translog.stats()),refresh 不推进 commit,只有 flush 才能把它裁掉。'
  };

  /* ===== 实验 2:_stats 读 uncommitted_operations ===== */
  window.ESEXPERIMENTS['ch14-10-tlog-setup'] = {
    version: 1, id: 'ch14-10-tlog-setup',
    title: '实验 2 · 建索引 tut-l14-tlog',
    method: 'PUT', path: '/tut-l14-tlog',
    body: { settings: { number_of_shards: 1, number_of_replicas: 0, refresh_interval: -1 } },
    predict: '为什么这组要先 flush 一次打底?',
    expect: 'acknowledged: true。建索引自带一次空 commit,但为了把计数基线钉死在干净的 0,下一步再手动 flush 一次——之后的 +1 才可归因到我们的写入。'
  };
  window.ESEXPERIMENTS['ch14-11-tlog-flush'] = {
    version: 1, id: 'ch14-11-tlog-flush',
    title: '实验 2 · flush 打底',
    method: 'POST', path: '/tut-l14-tlog/_flush?filter_path=_shards',
    body: null,
    predict: 'flush 内部按什么顺序动 translog 和 Lucene?',
    expect: '_shards.successful = 1。flushHoldingLock 四步:rollGeneration → commitIndexWriter(IndexWriter.commit,commit user data 带 local checkpoint)→ refresh("version_table_flush",INTERNAL)→ trimUnreferencedReaders。对照图 3。'
  };
  window.ESEXPERIMENTS['ch14-12-tlog-zero'] = {
    version: 1, id: 'ch14-12-tlog-zero',
    title: '实验 2 · 打底后的基线',
    method: 'GET', path: '/tut-l14-tlog/_stats/translog?filter_path=indices.tut-l14-tlog.primaries.translog',
    body: null,
    predict: 'uncommitted_operations 现在是多少?',
    expect: '0(或个位数,以你的返回为准)。没有未 commit 操作可统计。记住字段全名 primaries.translog.uncommitted_operations——不存在叫 uncommitted 的短键。'
  };
  window.ESEXPERIMENTS['ch14-13-tlog-put'] = {
    version: 1, id: 'ch14-13-tlog-put',
    title: '实验 2 · 写入一条',
    method: 'PUT', path: '/tut-l14-tlog/_doc/1',
    body: { title: 'before-flush' },
    predict: '201 回来时,这条写已经 fsync 了吗?已经 commit 了吗?',
    expect: 'result: created。两问两答:REQUEST 耐久下回 201 前 syncAfterWrite → ensureSynced,fsync 完成;Lucene 没有 commit。fsync 管「掉电不丢」,commit 管「恢复起点」——两个不同动作。'
  };
  window.ESEXPERIMENTS['ch14-14-tlog-one'] = {
    version: 1, id: 'ch14-14-tlog-one',
    title: '实验 2 · 再看统计(+1)',
    method: 'GET', path: '/tut-l14-tlog/_stats/translog?filter_path=indices.tut-l14-tlog.primaries.translog',
    body: null,
    predict: 'operations 和 uncommitted_operations 各是多少?会一样吗?',
    expect: '通常都是 1(以你的返回为准)。这条操作记在当前 generation,还没被任何 commit 覆盖,两个口径都算它;等 flush 之后才分道扬镳。'
  };
  window.ESEXPERIMENTS['ch14-15-tlog-async'] = {
    version: 1, id: 'ch14-15-tlog-async',
    title: '实验 2 · durability 换成 async',
    method: 'PUT', path: '/tut-l14-tlog/_settings',
    body: { 'index.translog.durability': 'async' },
    predict: '这个设置能在线改吗?改完之后「201」的含义变了吗?',
    expect: 'acknowledged: true(IndexSetting,IndexScope Dynamic)。async 下 AsyncAfterWriteAction 不在这条请求上 fsync,由 translog 的 sync_interval(默认 5s)批量补——201 不再等于「已在盘上」,窗口内掉电可能丢最近几条。日志类索引可接受,「写后立刻 GET 确认」的接口不能开。删索引即清理,无需改回。'
  };

  /* ===== 实验 3:refresh 之后、flush 之前 ===== */
  window.ESEXPERIMENTS['ch14-20-fl-setup'] = {
    version: 1, id: 'ch14-20-fl-setup',
    title: '实验 3 · 建索引 tut-l14-flush',
    method: 'PUT', path: '/tut-l14-flush',
    body: { settings: { number_of_shards: 1, number_of_replicas: 0, refresh_interval: -1 } },
    predict: '这组要对照的窗口是哪一段?',
    expect: 'acknowledged: true。固定变量:1 主 0 副、关定时 refresh——让「refresh 之后、flush 之前」这一窗口完全由我们手动控制,可见性与 commit 的对照才干净。'
  };
  window.ESEXPERIMENTS['ch14-21-fl-put'] = {
    version: 1, id: 'ch14-21-fl-put',
    title: '实验 3 · 写入 _id=1',
    method: 'PUT', path: '/tut-l14-flush/_doc/1',
    body: { title: 'before-flush' },
    predict: '这篇现在在 buffer、translog、segment 各几处?',
    expect: 'result: created。buffer 一份、translog 一条(已 fsync);segment 零份。动画第 4 步的状态。'
  };
  window.ESEXPERIMENTS['ch14-22-fl-refresh'] = {
    version: 1, id: 'ch14-22-fl-refresh',
    title: '实验 3 · 手动 _refresh',
    method: 'POST', path: '/tut-l14-flush/_refresh?filter_path=_shards',
    body: null,
    predict: 'refresh 之后 SEARCH 能看到了;translog 呢?',
    expect: '_shards.successful = 1。buffer → 新 NRT segment,EXTERNAL 换快照;translog 不动——这就是第 5 步与第 7 步动画之间的那条分界线。'
  };
  window.ESEXPERIMENTS['ch14-23-fl-stats-refresh'] = {
    version: 1, id: 'ch14-23-fl-stats-refresh',
    title: '实验 3 · refresh 后看统计',
    method: 'GET', path: '/tut-l14-flush/_stats/translog?filter_path=indices.tut-l14-flush.primaries.translog',
    body: null,
    predict: '都能搜到了,uncommitted_operations 归零了吗?',
    expect: '没有:仍 ≥ 1(以你的返回为准)。「可见 ≠ 已 commit」的数字形态——refresh 换的是 searcher,没碰 commit 点,translog 一条不少。'
  };
  window.ESEXPERIMENTS['ch14-24-fl-search'] = {
    version: 1, id: 'ch14-24-fl-search',
    title: '实验 3 · flush 前再 SEARCH(命中)',
    method: 'GET', path: '/tut-l14-flush/_search?q=before-flush&filter_path=hits.total',
    body: null,
    predict: 'flush 还没做,能搜到吗?',
    expect: 'hits.total.value = 1。可搜索由 EXTERNAL searcher 决定;此刻这篇的耐久在 translog 的 fsync 里,commit 还欠着——两条轴各自独立走到各自的位置。'
  };
  window.ESEXPERIMENTS['ch14-25-fl-flush'] = {
    version: 1, id: 'ch14-25-fl-flush',
    title: '实验 3 · 手动 _flush',
    method: 'POST', path: '/tut-l14-flush/_flush?filter_path=_shards',
    body: null,
    predict: '哪个计数会归零?Lucene 这边多出什么文件?',
    expect: '_shards.successful = 1。IndexWriter.commit 写出新的 segments_N(commit user data 带 local_checkpoint / max_seq_no);translog.rollGeneration 冻结旧代,trimUnreferencedReaders 删掉不再被引用的 .tlog。'
  };
  window.ESEXPERIMENTS['ch14-26-fl-stats-flush'] = {
    version: 1, id: 'ch14-26-fl-stats-flush',
    title: '实验 3 · flush 后看统计(归零)',
    method: 'GET', path: '/tut-l14-flush/_stats/translog?filter_path=indices.tut-l14-flush.primaries.translog',
    body: null,
    predict: 'uncommitted_operations 现在?如果不是 0 呢?',
    expect: '0(1 主 0 副本通常一次到位;以你的返回为准)。若仍 >0,再 flush 一次——safe commit 还要 global checkpoint 跟上,rest api 测试 20_translog.yml 正是 flush 两次后才断言 0。对照实验 1:同一个字段,refresh 推不动,flush 一推就动。'
  };

  /* ===== 实验 4:_segments 看段的生老病死 ===== */
  window.ESEXPERIMENTS['ch14-30-seg-setup'] = {
    version: 1, id: 'ch14-30-seg-setup',
    title: '实验 4 · 建索引 tut-l14-seg',
    method: 'PUT', path: '/tut-l14-seg',
    body: { settings: { number_of_shards: 1, number_of_replicas: 0, refresh_interval: -1 } },
    predict: '为什么这组要关定时 refresh?',
    expect: 'acknowledged: true。让段只在我们的 ?refresh=true 时产生:每写一批、刷一次 → 一个段,段数可控、前后可对照。'
  };
  window.ESEXPERIMENTS['ch14-31-seg-bulk-a'] = {
    version: 1, id: 'ch14-31-seg-bulk-a',
    title: '实验 4 · 第 1 批 bulk(3 篇,顺手 refresh)',
    method: 'POST', path: '/tut-l14-seg/_bulk?refresh=true',
    body: '{"index":{"_id":"1"}}\n{"title":"seg-a","n":1}\n{"index":{"_id":"2"}}\n{"title":"seg-b","n":2}\n{"index":{"_id":"3"}}\n{"title":"seg-c","n":3}\n',
    predict: '一批 bulk + 一次 refresh,会造出几个段?',
    expect: 'items 三条 created。这一批进同一个新 segment(refresh=true 是「写完顺手刷」,生产不要当默认;bulk 每行独立路由,1 个分片所以都在本地)。'
  };
  window.ESEXPERIMENTS['ch14-32-seg-bulk-b'] = {
    version: 1, id: 'ch14-32-seg-bulk-b',
    title: '实验 4 · 第 2 批 bulk(再 3 篇,再 refresh)',
    method: 'POST', path: '/tut-l14-seg/_bulk?refresh=true',
    body: '{"index":{"_id":"4"}}\n{"title":"seg-d","n":4}\n{"index":{"_id":"5"}}\n{"title":"seg-e","n":5}\n{"index":{"_id":"6"}}\n{"title":"seg-f","n":6}\n',
    predict: '第二个段会和第一个合并吗?什么时候合?',
    expect: 'items 三条 created。又一个新段。TieredMergePolicy 在后台择机合并——不是 refresh 时同步做,所以你有可能在下一步看到 2 段,也可能已被并成 1 段(以你的返回为准,两种都说明「refresh 造段、merge 收段」)。'
  };
  window.ESEXPERIMENTS['ch14-33-seg-segments'] = {
    version: 1, id: 'ch14-33-seg-segments',
    title: '实验 4 · _segments:数一数段',
    method: 'GET', path: '/tut-l14-seg/_segments',
    body: null,
    predict: '有几个 segment?每段几篇文档、多大?',
    expect: '常见 2 个段、每段 3 篇(也可能后台 merge 已并成 1 段 6 篇——以你的返回为准)。每段看 generation、num_docs、size;这份「多段底片」留给 merge 对照。'
  };
  window.ESEXPERIMENTS['ch14-34-seg-update'] = {
    version: 1, id: 'ch14-34-seg-update',
    title: '实验 4 · 更新 _id=1(软删除旧版本)',
    method: 'POST', path: '/tut-l14-seg/_update/1?refresh=true',
    body: { doc: { n: 99 } },
    predict: 'Lucene 有原地更新吗?旧版本去哪了?',
    expect: 'result: updated,_version: 2。没有原地更新:indexWriter.softUpdateDocument 给旧 uid 打软删除标记,再写入新文档;旧文档仍躺在老段里占空间,只是搜索不可见——回收要等 merge。'
  };
  window.ESEXPERIMENTS['ch14-35-seg-deleted'] = {
    version: 1, id: 'ch14-35-seg-deleted',
    title: '实验 4 · _segments:看 deleted_docs',
    method: 'GET', path: '/tut-l14-seg/_segments',
    body: null,
    predict: '删除标记体现在哪个字段?',
    expect: '某个段出现 deleted_docs ≥ 1(或 deleted_in_bytes > 0,以你的返回为准)。软删除的文档在搜索里不可见但要等合并才物理回收——「更新很便宜,回收有延迟」。'
  };
  window.ESEXPERIMENTS['ch14-36-seg-forcemerge'] = {
    version: 1, id: 'ch14-36-seg-forcemerge',
    title: '实验 4 · _forcemerge 到 1 段',
    method: 'POST', path: '/tut-l14-seg/_forcemerge?max_num_segments=1',
    body: null,
    predict: '段数和 deleted_docs 各变成多少?这一步贵在哪?',
    expect: '无 body,提交后合并(可能要等一会儿)。所有段并成 1 个,软删除文档被物理丢弃。注意:这是全量重写,只适合归档只读索引;写入还在继续时会立刻再裂出新段,白付一次 CPU/IO。'
  };
  window.ESEXPERIMENTS['ch14-37-seg-after'] = {
    version: 1, id: 'ch14-37-seg-after',
    title: '实验 4 · _segments:合并后对照',
    method: 'GET', path: '/tut-l14-seg/_segments',
    body: null,
    predict: '现在几个段?num_docs 总共几篇?deleted 呢?',
    expect: '1 个段,num_docs = 6,deleted_docs = 0(以你的返回为准)。对照第 33/35 步的多段与 deleted——merge 的两个收益(文件变少、删除回收)一次看全。'
  };

  /* ===== 清理 ===== */
  window.ESEXPERIMENTS['ch14-90-cleanup'] = {
    version: 1, id: 'ch14-90-cleanup',
    title: '清理 · 删除全部 tut-l14-* 索引',
    method: 'DELETE', path: '/tut-l14-nrt,tut-l14-tlog,tut-l14-flush,tut-l14-seg',
    body: null,
    predict: '四个索引一条 DELETE 能全删吗?durability=async 的设置呢?',
    expect: 'acknowledged: true(逗号分隔多索引)。segment、translog、VersionMap 随分片生命周期一起消失;索引级设置(async)随索引删除,不残留。'
  };
})();
