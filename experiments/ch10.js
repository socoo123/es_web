/* experiments/ch10.js — 第 10 课:实验 + 旗舰动画(realtime GET) */
(function () {
  'use strict';

  /* ===== 旗舰动画:GET 为什么读得到未 refresh 的文档 ===== */
  /* 舞台:上行 = 处理链(REST → Action → Engine),下行 = 分片内存储
     (VersionMap / translog / segment 倒排表),底部 = 本步结局。 */

  var OUTCOMES = [
    'PUT _doc/1 → 201 Created · 尚未 refresh',
    'REST 产出:GetRequest(realtime=true),没有 Lucene',
    'murmur3("1") % 主分片数 → 唯一 shard,动作名换成 get[s]',
    'VersionMap 命中 uid=1,带出 translog 位置',
    'found: true · _source 组装自 translog',
    'SEARCH hits: 0 · EXTERNAL 快照里还没有 Doc1',
    '_refresh 后 SEARCH hits: 1;GET 从未等过 refresh'
  ];

  var NOTES = [
    '写入刚落地:Index 操作进了 translog,VersionMap 记下 uid=1 的最新版本。refresh_interval=-1,任何 segment 的倒排表里都还没有这篇——GET 与 SEARCH 的可见性差异从这里开始。',
    'GET 进来。PathTrie 把 /{index}/_doc/{id} 配给 RestGetAction,它只把路径参数与查询串收进 GetRequest(realtime 默认 true)就交给 client.get()——REST 层没有一行 Lucene。',
    'Action 层:不带自定义 routing 时,有效键就是 _id 的字符串。murmur3 取模算出唯一 shard,动作名换成 indices:data/read/get[s] 发往持有该分片的节点——GET 只打这一个 shard。',
    'Engine 收到后按 uid 查 VersionMap:堆内的 O(1) 索引,记录「这篇最近写过没有、删没删、写在 translog 哪个位置」。注意它不是倒排表——不分词、不做 term → 文档。',
    '按 location 调 translog.readOperation 还原这条 Index 操作,在内存里为这一篇搭临时 reader,再走与 segment 同一套 fetch 取 _source。第 1 课的伏笔在此收回:写完立刻读得到,不靠 refresh。',
    '同一时刻换 SEARCH:它只认 EXTERNAL searcher——refresh 之后的那份 segment 快照。Doc1 还没被 refresh 编进倒排表,0 hits。写入成功 ≠ 可搜索。',
    '_refresh 让内存 buffer 变成新 segment,EXTERNAL 换新快照,SEARCH 命中;GET 一路 found: true。近实时是 SEARCH 的属性,不是 GET 的——两套可见性时钟,就此分清。'
  ];

  var ROW_A = [
    { x: 10, w: 120, sub: '① 客户端', main: 'GET _doc/1', cls: 'fig-name' },
    { x: 160, w: 164, sub: '② REST 层', main: 'RestGetAction', cls: 'fig-key' },
    { x: 354, w: 164, sub: '③ Action 层', main: 'TransportGetAction', cls: 'fig-key' },
    { x: 548, w: 164, sub: '④ Engine 层', main: 'InternalEngine.get', cls: 'fig-key' }
  ];
  var HOT_A = [-1, 1, 2, 3, 3, 4, 4]; /* -1 全暗(请求未到),4 全亮(链路走完) */

  /* 下行三块存储的状态:hot 高亮 / lit 正常 / dim 压暗 / warn 示警 */
  var B_STATE = [
    ['hot', 'hot', 'dim'],
    ['lit', 'lit', 'dim'],
    ['lit', 'lit', 'dim'],
    ['hot', 'lit', 'dim'],
    ['lit', 'hot', 'dim'],
    ['lit', 'lit', 'warn'],
    ['lit', 'lit', 'hot']
  ];

  function stepSvg(step) {
    var s = '<svg viewBox="0 0 760 288" xmlns="http://www.w3.org/2000/svg">';
    s += '<defs><marker id="ah10a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
      + '<path d="M 0 0 L 10 5 L 0 10 z" class="fig-arrowhead"/></marker></defs>';

    /* 上行:处理链 */
    var hotA = HOT_A[step];
    for (var i = 0; i < ROW_A.length; i++) {
      var a = ROW_A[i];
      if (i < ROW_A.length - 1) {
        s += '<line x1="' + (a.x + a.w + 4) + '" y1="47" x2="' + (ROW_A[i + 1].x - 6)
          + '" y2="47" class="fig-arrow" marker-end="url(#ah10a)"'
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

    /* Engine → 存储层的换轨线 */
    var elbowOp = step >= 3 ? 1 : 0.25;
    s += '<g opacity="' + elbowOp + '">';
    s += '<path d="M 630 82 L 630 104 L 125 104 L 125 144" class="fig-arrow" marker-end="url(#ah10a)"/>';
    s += '<text x="380" y="98" text-anchor="middle" class="fig-sub">shardOperation:数据节点上按 _id 取这一篇</text>';
    s += '</g>';

    /* 下行:分片内的三块存储 */
    var st = B_STATE[step];
    var boxes = [
      { x: 30, w: 190, sub: '堆内 uid 索引', name: 'VersionMap', key: 'uid=1 → location' },
      { x: 300, w: 190, sub: '尚未 refresh 的写', name: 'translog', key: 'Index Doc1 @loc' },
      { x: 540, w: 200, sub: 'refresh 后才可见', name: 'segment 倒排表',
        key: step < 6 ? 'Doc1: 不在' : 'Doc1: 已在' }
    ];
    for (var j = 0; j < 3; j++) {
      var b = boxes[j];
      var state = st[j];
      var warn = state === 'warn';
      s += '<g opacity="' + (state === 'dim' ? 0.35 : 1) + '">';
      s += '<rect x="' + b.x + '" y="150" width="' + b.w + '" height="92" rx="9" class="'
        + (state === 'hot' ? 'fig-box-hot fp-pop' : 'fig-box') + '"/>';
      s += '<text x="' + (b.x + b.w / 2) + '" y="176" text-anchor="middle" class="fig-sub">' + b.sub + '</text>';
      s += '<text x="' + (b.x + b.w / 2) + '" y="200" text-anchor="middle" class="fig-name">' + b.name + '</text>';
      s += '<text x="' + (b.x + b.w / 2) + '" y="224" text-anchor="middle" class="fig-key'
        + (warn ? ' fp-pulse' : '') + '"' + (warn ? ' style="fill: rgb(var(--warn))"' : '')
        + '>' + b.key + '</text>';
      s += '</g>';
    }

    /* VersionMap → translog 的 location 指针 */
    var locOp = step >= 4 ? 1 : 0.3;
    s += '<g opacity="' + locOp + '">';
    s += '<line x1="224" y1="196" x2="294" y2="196" class="fig-arrow" marker-end="url(#ah10a)"/>';
    s += '<text x="259" y="188" text-anchor="middle" class="fig-sub">location</text>';
    s += '</g>';

    /* SEARCH 对照入口(后两步出现) */
    if (step >= 5) {
      s += '<text x="640" y="128" text-anchor="middle" class="fig-sub">SEARCH 只看这里(EXTERNAL)</text>';
      s += '<line x1="640" y1="133" x2="640" y2="144" class="fig-arrow" marker-end="url(#ah10a)"/>';
    }

    /* 底部:本步结局 */
    s += '<text x="380" y="272" text-anchor="middle" class="fig-key">' + OUTCOMES[step] + '</text>';
    s += '</svg>';
    return s;
  }

  window.ESFLOWS = window.ESFLOWS || {};
  window.ESFLOWS['ch10-realtime-get'] = {
    version: 1,
    id: 'ch10-realtime-get',
    title: 'Realtime GET:不 refresh 为什么也读得到',
    speed: 2000,
    steps: NOTES.map(function (note, i) { return { svg: stepSvg(i), note: note }; })
  };

  /* ===== 实验 1:关 refresh 后对照 realtime GET ===== */
  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};
  window.ESEXPERIMENTS['ch10-00-setup'] = {
    version: 1, id: 'ch10-00-setup',
    title: '实验 1 · 第 0 步:建索引 tut-l10-nrt(1 分片,关自动 refresh)',
    method: 'PUT', path: '/tut-l10-nrt',
    body: { settings: { number_of_shards: 1, number_of_replicas: 0, refresh_interval: -1 } },
    predict: '把 refresh_interval 设成 -1,关掉的是谁的可见性?GET 会被它拖慢吗?',
    expect: '关的是 SEARCH 的时钟:不再自动把内存 buffer 变成 segment。GET 的 realtime 读不依赖 refresh,一毫秒都不多等。0 副本让单节点保持 green,也免去副本迭代的干扰。'
  };
  window.ESEXPERIMENTS['ch10-01-put'] = {
    version: 1, id: 'ch10-01-put',
    title: '实验 1 · 第 1 步:写入 _id=1(不带 refresh)',
    method: 'PUT', path: '/tut-l10-nrt/_doc/1',
    body: { title: 'nrt-get', views: 10 },
    predict: 'result 是 created 还是 updated?此刻这篇文档同时存在于哪几处?',
    expect: 'result: created。同一时刻它在:translog 的一条 Index 操作 + VersionMap 里 uid=1 的版本条目 + 内存 buffer;不在任何 segment 的倒排表里——这是后面所有对照的起点。'
  };
  window.ESEXPERIMENTS['ch10-02-get'] = {
    version: 1, id: 'ch10-02-get',
    title: '实验 1 · 第 2 步:立刻 GET(默认 realtime)',
    method: 'GET', path: '/tut-l10-nrt/_doc/1?filter_path=found,_id,_version,_source',
    body: null,
    predict: '还没 refresh,GET 能拿到吗?_version 是多少?',
    expect: 'found: true,_version: 1,带完整 _source。路径即动画第 3-4 步:InternalEngine.get 走 realtimeGetUnderLock → VersionMap 命中 → translog 读出原始操作。全程没碰倒排表。'
  };
  window.ESEXPERIMENTS['ch10-03-search-miss'] = {
    version: 1, id: 'ch10-03-search-miss',
    title: '实验 1 · 第 3 步:立刻 SEARCH(应扑空)',
    method: 'POST', path: '/tut-l10-nrt/_search?filter_path=hits.total',
    body: { query: { match: { title: 'nrt-get' } } },
    predict: 'GET 都拿到了,match title:nrt-get 呢?',
    expect: 'hits.total.value = 0。SEARCH 只认 EXTERNAL searcher——refresh 之后那份 segment 快照。refresh_interval=-1 把「可能扑空」变成「一定扑空」,这正是第 1 课实验 3 的可复现版。'
  };
  window.ESEXPERIMENTS['ch10-04-nonrealtime'] = {
    version: 1, id: 'ch10-04-nonrealtime',
    title: '实验 1 · 第 4 步:GET ?realtime=false(自愿放弃实时)',
    method: 'GET', path: '/tut-l10-nrt/_doc/1?realtime=false&filter_path=found,_id',
    body: null,
    predict: '同一个 _id、同一个时刻,把 realtime 关掉还拿得到吗?HTTP 状态码是几?',
    expect: 'found: false,HTTP 404。realtime=false 时 InternalEngine.get 不进 realtime 分支,只读 EXTERNAL searcher——和 SEARCH 同源:要 refresh 才可见。404 是 Handler 自己选的,不是路由错了。'
  };
  window.ESEXPERIMENTS['ch10-05-refresh-flag'] = {
    version: 1, id: 'ch10-05-refresh-flag',
    title: '实验 1 · 第 5 步(陷阱):只加 ?refresh=true',
    method: 'GET', path: '/tut-l10-nrt/_doc/1?refresh=true&filter_path=found,_id',
    body: null,
    predict: 'refresh=true 会不会顺手把索引刷新了,让下一步 SEARCH 立刻可见?',
    expect: '这一步本身 found: true(200),但默认 realtime=true 时 TransportGetAction 的 asyncGet 根本不执行 externalRefresh——refresh 参数被无视。证据在下一步。'
  };
  window.ESEXPERIMENTS['ch10-06-search-still-miss'] = {
    version: 1, id: 'ch10-06-search-still-miss',
    title: '实验 1 · 第 6 步:再 SEARCH(仍然扑空)',
    method: 'POST', path: '/tut-l10-nrt/_search?filter_path=hits.total',
    body: { query: { match: { title: 'nrt-get' } } },
    predict: '刚做过一次 ?refresh=true 的 GET,这次 hits 是多少?',
    expect: '仍是 0。源码条件是 refresh=true 且 realtime=false 才 externalRefresh。旧直觉「GET 带 refresh=true 就会刷新索引」在默认 realtime 下不成立——这是本课最值钱的一次踩坑。'
  };
  window.ESEXPERIMENTS['ch10-07-refresh-nonrealtime'] = {
    version: 1, id: 'ch10-07-refresh-nonrealtime',
    title: '实验 1 · 第 7 步:refresh=true 且 realtime=false',
    method: 'GET', path: '/tut-l10-nrt/_doc/1?refresh=true&realtime=false&filter_path=found,_id',
    body: null,
    predict: '两个参数都给,这次会额外发生什么?',
    expect: 'realtime=false 时 asyncGet 才检查 refresh 标志:先 externalRefresh(生成新 segment、EXTERNAL 换快照)再读。found: true。它等价于「先 _refresh 再按搜索可见性读」。'
  };
  window.ESEXPERIMENTS['ch10-08-search-hit'] = {
    version: 1, id: 'ch10-08-search-hit',
    title: '实验 1 · 第 8 步:再 SEARCH(命中)',
    method: 'POST', path: '/tut-l10-nrt/_search?filter_path=hits.total',
    body: { query: { match: { title: 'nrt-get' } } },
    predict: 'hits.total 这次是多少?',
    expect: '1。Doc1 终于进了 EXTERNAL 快照。对照实验 2:GET 从第 0 秒起就是 true。两条可见性时钟彻底分开,是本课唯一的重点。'
  };
  window.ESEXPERIMENTS['ch10-09-source-filter'] = {
    version: 1, id: 'ch10-09-source-filter',
    title: '实验 1 · 第 9 步:_source 过滤(_source_includes)',
    method: 'GET', path: '/tut-l10-nrt/_doc/1?_source_includes=title&filter_path=found,_source',
    body: null,
    predict: '只想要 title 字段,_source 会变成什么样?这会另开一条 Engine 路径吗?',
    expect: '_source 只剩 title。过滤发生在 ShardGetService.innerGetFetch 的 SourceFilter;translog 路径与 segment 路径最后都汇到同一套 SourceLoader——不是另一条 Engine 路径。'
  };

  /* ===== 实验 2:routing 换掉 hash 的键 ===== */
  window.ESEXPERIMENTS['ch10-10-routing-setup'] = {
    version: 1, id: 'ch10-10-routing-setup',
    title: '实验 2 · 第 0 步:建 5 分片索引 tut-l10-routed',
    method: 'PUT', path: '/tut-l10-routed',
    body: { settings: { number_of_shards: 5, number_of_replicas: 0 } },
    predict: '5 个主分片对 routing 实验意味着什么?',
    expect: 'floorMod(hash, 5) 有 5 个落点,两把不同的键大概率落在不同 shard——「带 routing 写、忘带 routing 读」的 404 才容易复现。若碰巧撞车,换个 routing 值再写一篇即可。'
  };
  window.ESEXPERIMENTS['ch10-11-routing-put'] = {
    version: 1, id: 'ch10-11-routing-put',
    title: '实验 2 · 第 1 步:带 routing 写入 _id=3',
    method: 'PUT', path: '/tut-l10-routed/_doc/3?routing=user123&refresh=true',
    body: { title: 'routed-doc', owner: 'user123' },
    predict: '这次选 shard 的有效键是 _id 的 "3",还是 "user123"?',
    expect: '是 user123。IndexRouting.shardId:hash(routing != null ? routing : id)——有 routing 就完全替换,不混入 _id。写完顺手 refresh=true,让 SEARCH 立即可见,排除干扰变量。'
  };
  window.ESEXPERIMENTS['ch10-12-shards-key-id'] = {
    version: 1, id: 'ch10-12-shards-key-id',
    title: '实验 2 · 第 2 步:查「忘带 routing」会打到哪个 shard',
    method: 'GET', path: '/tut-l10-routed/_search_shards?routing=3&filter_path=shards.shard',
    body: null,
    predict: 'routing=3 在模拟谁?返回的 shard 号和 user123 的一样吗?',
    expect: '模拟不带自定义 routing 的读取:此时有效键恰好是 _id 字符串 "3"。本站验证环境实测落在 shard 4(以你的返回为准)——不是 user123 所在的那个。'
  };
  window.ESEXPERIMENTS['ch10-13-shards-key-routing'] = {
    version: 1, id: 'ch10-13-shards-key-routing',
    title: '实验 2 · 第 3 步:查 user123 这把键的 shard',
    method: 'GET', path: '/tut-l10-routed/_search_shards?routing=user123&filter_path=shards.shard',
    body: null,
    predict: '和上一步的 shard 号相同吗?',
    expect: '不同——本站验证环境实测 shard 2。两把键 murmur3 哈希取模后落点不同,这就是「写在一个 shard、读去另一个 shard」的由来。以真实返回为准,不要背具体数字。'
  };
  window.ESEXPERIMENTS['ch10-14-get-no-routing'] = {
    version: 1, id: 'ch10-14-get-no-routing',
    title: '实验 2 · 第 4 步:GET 不带 routing(扑空)',
    method: 'GET', path: '/tut-l10-routed/_doc/3?filter_path=found,_id',
    body: null,
    predict: '文档明明存在(第 6 步马上能搜到),这次 GET 返回什么?',
    expect: 'found: false,HTTP 404。GET 只打 hash("3") 那一个 shard(TransportSingleShardAction),不广播、不换 shard 号重试,失败只在同一 shard 的副本间换。打错拷贝,就表现为「不存在」。'
  };
  window.ESEXPERIMENTS['ch10-15-get-with-routing'] = {
    version: 1, id: 'ch10-15-get-with-routing',
    title: '实验 2 · 第 5 步:GET 带上写入时同一把键',
    method: 'GET', path: '/tut-l10-routed/_doc/3?routing=user123&filter_path=found,_id,_routing',
    body: null,
    predict: '补上 routing=user123 后呢?响应里会多出什么字段?',
    expect: 'found: true,响应回显 _routing: "user123"。读和写用同一把有效键,hash 落回同一 shard——「routing 是替换 hash 输入,不是可选提示」说的就是这件事。'
  };
  window.ESEXPERIMENTS['ch10-16-search-fanout'] = {
    version: 1, id: 'ch10-16-search-fanout',
    title: '实验 2 · 第 6 步:SEARCH 不带 routing(仍命中)',
    method: 'GET', path: '/tut-l10-routed/_search?q=_id:3&filter_path=hits.total,hits.hits._id,hits.hits._routing',
    body: null,
    predict: '同一个 _id,SEARCH 不带 routing 能找到吗?',
    expect: '能:1 hit,且回显 _routing: "user123"。SEARCH 扇出全部 5 个 shard,routing 对它只是可选的收窄。GET 精确一击、SEARCH 广撒网——两种读取模型。'
  };

  /* ===== 清理 ===== */
  window.ESEXPERIMENTS['ch10-17-cleanup'] = {
    version: 1, id: 'ch10-17-cleanup',
    title: '清理 1 · 删除 tut-l10-nrt',
    method: 'DELETE', path: '/tut-l10-nrt',
    body: null,
    predict: '删除会连带清掉哪些「可见性时钟」的痕迹?',
    expect: 'acknowledged: true。segment、translog、VersionMap 随分片一起消失——三个存储组件同属一个分片的生命周期。'
  };
  window.ESEXPERIMENTS['ch10-18-cleanup'] = {
    version: 1, id: 'ch10-18-cleanup',
    title: '清理 2 · 删除 tut-l10-routed',
    method: 'DELETE', path: '/tut-l10-routed',
    body: null,
    predict: 'routing 关系存在哪里?删索引后还剩什么?',
    expect: 'acknowledged: true。routing 只是写入时的 hash 输入,不单独存储;索引删了,「哪把键对应哪个 shard」自然无从谈起。'
  };
})();
