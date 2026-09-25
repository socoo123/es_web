/* experiments/ch16.js — 第 16 课:Query Then Fetch 实验 + 两阶段搜索旗舰动画(注册表) */
(function () {
  'use strict';

  /* ===== 旗舰动画:一次 _search 的 Query / Fetch 两阶段 ===== */
  function defs(id) {
    return '<defs><marker id="' + id + '" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
      + '<path d="M 0 0 L 10 5 L 0 10 z" class="fig-arrowhead"/></marker></defs>';
  }
  function rect(x, y, w, h, cls, anim) {
    return '<rect x="' + x + '" y="' + y + '" width="' + w + '" height="' + h + '" rx="9" class="' + cls + (anim ? ' ' + anim : '') + '"/>';
  }
  function txt(x, y, s, cls, warn, anim) {
    var st = warn ? ' style="fill: rgb(var(--warn))"' : '';
    return '<text x="' + x + '" y="' + y + '" text-anchor="middle" class="' + cls + (anim ? ' ' + anim : '') + '"' + st + '>' + s + '</text>';
  }
  function line(x1, y1, x2, y2, id) {
    return '<line x1="' + x1 + '" y1="' + y1 + '" x2="' + x2 + '" y2="' + y2 + '" class="fig-arrow" marker-end="url(#' + id + ')"/>';
  }

  /* 步骤 1:请求到达协调节点 */
  function step1() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('ah16s1');
    s += rect(15, 25, 730, 64, 'fig-box');
    s += txt(380, 50, 'POST /tut-l16-qtf/_search', 'fig-key');
    s += txt(380, 72, '{"size":10,"query":{"match":{"title":"elasticsearch"}}}', 'fig-sub');
    s += line(380, 89, 380, 118, 'ah16s1');
    s += rect(230, 122, 300, 58, 'fig-box-hot', 'fp-pop');
    s += txt(380, 146, '协调节点', 'fig-name');
    s += txt(380, 168, '默认 SearchType = QUERY_THEN_FETCH', 'fig-sub');
    s += txt(380, 212, 'REST 只造 SearchRequest,不跑 Lucene', 'fig-sub');
    s += txt(380, 234, '真正跑 Lucene 的是各 shard 上的 SearchService', 'fig-sub');
    s += txt(380, 268, 'TransportSearchAction:indices:data/read/search', 'fig-sub');
    return s + '</svg>';
  }

  /* 步骤 2:扇出 Query,发完即返回 */
  function step2() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('ah16s2');
    s += rect(230, 15, 300, 52, 'fig-box');
    s += txt(380, 38, 'doRun:一个 for 循环', 'fig-name');
    s += txt(380, 58, '发完就返回,不 await', 'fig-sub');
    s += line(280, 67, 137, 105, 'ah16s2');
    s += line(380, 67, 380, 105, 'ah16s2');
    s += line(480, 67, 633, 105, 'ah16s2');
    for (var i = 0; i < 3; i++) {
      var x = 15 + i * 250, cx = x + 112;
      s += rect(x, 109, 225, 64, 'fig-box');
      s += txt(cx, 131, 'shard ' + i, 'fig-name');
      s += txt(cx, 151, 'phase/query', 'fig-key');
      s += txt(cx, 171, '回 (docId,score)', 'fig-sub');
    }
    s += rect(15, 186, 730, 70, 'fig-box');
    s += txt(380, 210, 'outstandingShards = 3', 'fig-key');
    s += txt(380, 232, '协调线程已释放:倒数到 0 才进 Fetch 阶段', 'fig-sub');
    s += txt(380, 254, '真正占 search 池的是数据节点上的查询 CPU', 'fig-sub');
    return s + '</svg>';
  }

  /* 步骤 3:各 shard 本地收 from+size 条 */
  function step3() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('ah16s3');
    var rows = [
      ['doc=7  s=9.41', 'doc=1  s=9.39', 'doc=6  s=9.44'],
      ['doc=19 s=9.38', 'doc=8  s=9.35', 'doc=15 s=9.36'],
      ['doc=2  s=9.31', 'doc=22 s=9.30', 'doc=11 s=9.29']
    ];
    for (var i = 0; i < 3; i++) {
      var x = 15 + i * 250, cx = x + 112;
      s += rect(x, 15, 225, 170, 'fig-box');
      s += txt(cx, 38, 'shard ' + i + ' · EXTERNAL', 'fig-name');
      s += txt(cx, 60, '本地 Top-10', 'fig-sub');
      s += txt(cx, 84, rows[0][i], 'fig-key');
      s += txt(cx, 104, rows[1][i], 'fig-key');
      s += txt(cx, 124, rows[2][i], 'fig-key');
      s += txt(cx, 148, '…', 'fig-sub');
      s += txt(cx, 168, '共 from+size=10 条', 'fig-sub');
    }
    s += rect(15, 198, 730, 74, 'fig-box-hot', 'fp-pop');
    s += txt(380, 222, '每个 shard 回 from+size 条', 'fig-name');
    s += txt(380, 244, 'doc 是 shard 内的 Lucene 文档号,不是 _id', 'fig-sub');
    s += txt(380, 264, '只看已 refresh 的快照,buffer 里的文档不存在', 'fig-sub');
    return s + '</svg>';
  }

  /* 步骤 4:倒数到 0,全局归并 */
  function step4() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('ah16s4');
    s += rect(15, 15, 730, 56, 'fig-box');
    s += txt(380, 38, 'outstandingShards:3 → 2 → 1 → 0', 'fig-key');
    s += txt(380, 58, '归并发生在最后一份回调所在的线程上', 'fig-sub');
    s += line(127, 124, 310, 150, 'ah16s4');
    s += line(380, 124, 380, 150, 'ah16s4');
    s += line(633, 124, 450, 150, 'ah16s4');
    for (var i = 0; i < 3; i++) {
      var x = 15 + i * 250, cx = x + 112;
      s += rect(x, 80, 225, 44, 'fig-box');
      s += txt(cx, 98, 'shard ' + i + ' · 10 条', 'fig-sub');
      s += txt(cx, 116, '(docId,score)', 'fig-sub');
    }
    s += rect(205, 154, 350, 64, 'fig-box-hot', 'fp-pop');
    s += txt(380, 178, '全局归并:30 选 10', 'fig-name');
    s += txt(380, 200, 'sortDocs · mergeTopDocs', 'fig-key');
    s += rect(15, 232, 730, 50, 'fig-box');
    s += txt(380, 255, 'Query 阶段网上只走了 30 条轻量元组', 'fig-sub');
    s += txt(380, 275, '此刻一篇 _source 都还没搬过', 'fig-sub');
    return s + '</svg>';
  }

  /* 步骤 5:fillDocIdsToLoad 按 shardIndex 分组 */
  function step5() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('ah16s5');
    s += rect(15, 15, 730, 50, 'fig-box');
    s += txt(380, 38, 'fillDocIdsToLoad:按 shardIndex 分组', 'fig-name');
    s += txt(380, 58, '全局 Top-10 的每个 doc 回到自己的 shard', 'fig-sub');
    var groups = [
      { n: 'shard 0', ids: 'doc 4, 17, 21', c: '3 篇待取' },
      { n: 'shard 1', ids: 'doc 1, 8, 9, 22, 30', c: '5 篇待取', hot: true },
      { n: 'shard 2', ids: 'doc 6, 15', c: '2 篇待取' }
    ];
    for (var i = 0; i < 3; i++) {
      var g = groups[i], x = 15 + i * 250, cx = x + 112;
      s += rect(x, 80, 225, 96, g.hot ? 'fig-box-hot' : 'fig-box', g.hot ? 'fp-pop' : null);
      s += txt(cx, 104, g.n, 'fig-name');
      s += txt(cx, 128, g.ids, 'fig-key');
      s += txt(cx, 152, g.c, 'fig-sub');
    }
    s += rect(15, 192, 730, 60, 'fig-box');
    s += txt(380, 214, '某 shard 一条都没进全局 Top-10 → 槽位 null', 'fig-sub');
    s += txt(380, 236, '不发 Fetch,只释放它的 reader context', 'fig-sub');
    s += txt(380, 256, 'Fetch 扇出宽度 ≤ 持有命中文档的 shard 数', 'fig-sub');
    return s + '</svg>';
  }

  /* 步骤 6:Fetch 只向持有者发 docId 列表 */
  function step6() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('ah16s6');
    s += rect(15, 60, 250, 90, 'fig-box-hot');
    s += txt(140, 92, 'FetchSearchPhase', 'fig-name');
    s += txt(140, 114, 'sendExecuteFetch', 'fig-key');
    s += txt(140, 136, '按分组发 docId 列表', 'fig-sub');
    s += line(265, 105, 300, 45, 'ah16s6');
    s += line(265, 105, 300, 115, 'ah16s6');
    s += line(265, 105, 300, 185, 'ah16s6');
    var targets = [
      { y: 20, n: 'shard 0 · 取 3 篇 _source', k: '[phase/fetch/id] doc=4,17,21' },
      { y: 90, n: 'shard 1 · 取 5 篇 _source', k: '[phase/fetch/id] doc=1,8,9,22,30' },
      { y: 160, n: 'shard 2 · 取 2 篇 _source', k: '[phase/fetch/id] doc=6,15' }
    ];
    for (var i = 0; i < 3; i++) {
      var t = targets[i];
      s += rect(300, t.y, 445, 50, 'fig-box');
      s += txt(522, t.y + 22, t.n, 'fig-name');
      s += txt(522, t.y + 40, t.k, 'fig-sub');
    }
    s += rect(15, 230, 730, 54, 'fig-box-hot', 'fp-pop');
    s += txt(380, 252, '网上只搬 10 篇 _source,不是 30 篇', 'fig-name');
    s += txt(380, 274, '一阶段方案会把 20 篇进不了响应的正文也搬回来', 'fig-sub');
    return s + '</svg>';
  }

  /* 步骤 7:组装响应,对照 GET */
  function step7() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('ah16s7');
    s += rect(15, 15, 730, 54, 'fig-box-hot', 'fp-pop');
    s += txt(380, 38, 'merge 组装最终 hits', 'fig-name');
    s += txt(380, 60, '每条带 _index / _id / _score / _source', 'fig-sub');
    s += rect(15, 90, 355, 112, 'fig-box');
    s += txt(192, 112, 'GET(第 10 课)', 'fig-name');
    s += txt(192, 136, '按 _id 只打 1 个 shard', 'fig-sub');
    s += txt(192, 158, 'Realtime:未 refresh 也读得到', 'fig-sub');
    s += txt(192, 180, '返回这一篇 _source', 'fig-sub');
    s += rect(390, 90, 355, 112, 'fig-box');
    s += txt(567, 112, 'SEARCH(本课)', 'fig-name');
    s += txt(567, 136, '默认打全部 shard 组', 'fig-sub');
    s += txt(567, 158, '只看已 refresh 的 EXTERNAL 快照', 'fig-sub');
    s += txt(567, 180, '先比分,再取正文', 'fig-sub');
    s += rect(15, 218, 730, 58, 'fig-box');
    s += txt(380, 240, '_shards.total = 3 · hits.hits = 10', 'fig-key');
    s += txt(380, 262, '两列之间没有箭头:GET 失败不会改走 SEARCH', 'fig-sub');
    return s + '</svg>';
  }

  window.ESFLOWS = window.ESFLOWS || {};
  window.ESFLOWS['ch16-qtf'] = {
    version: 1,
    id: 'ch16-qtf',
    title: '一次搜索的两阶段:Query Then Fetch',
    speed: 2400,
    steps: [
      { svg: step1(), note: '一次 _search 到达协调节点。默认 SearchType 就是 QUERY_THEN_FETCH:REST 层只负责造 SearchRequest,离开 REST 的是 TransportSearchAction——动作名 indices:data/read/search,与 GET 的 indices:data/read/get 同一命名家族。' },
      { svg: step2(), note: '协调节点 doRun 是一个 for 循环:对每个 shard 组发出 phase/query,循环结束方法就返回——没有 Future.get(),没有 latch.await(),扇出本身不占线程(第 8 课不变量)。outstandingShards 从 3 开始倒数。' },
      { svg: step3(), note: '每个数据节点用已 refresh 的 EXTERNAL searcher 跑 Lucene,collector 只收 from+size 条(0+10=10)。回给协调节点的是 (doc,score):doc 是 shard 内的 Lucene 文档号,同一个 doc=5 在不同 shard 是两篇文档。' },
      { svg: step4(), note: '每份应答回来都 finishOneShard:outstandingShards 3→2→1→0,归并发生在最后一份回调所在的线程上。sortDocs / mergeTopDocs 从 30 条候选里截全局窗口——此刻一篇 _source 都还没搬过。' },
      { svg: step5(), note: 'fillDocIdsToLoad 按 shardIndex 把全局 Top-10 的 doc 分组。某 shard 一条都没进全局 Top-N,槽位是 null——不发 Fetch,直接释放它的 reader context。所以 Fetch 的扇出宽度 ≤ 真正持有命中文档的 shard 数。' },
      { svg: step6(), note: 'FetchSearchPhase 只向仍持有这 10 个 doc 的 shard 发 phase/fetch/id,请求体是 docId 列表,不是「再搜一遍」。一阶段方案会搬 30 篇正文、丢 20 篇;两阶段只搬恰好进响应的 10 篇 _source。' },
      { svg: step7(), note: 'SearchPhaseController.merge 按全局顺序组装 hits,每条带 _index/_id/_score/_source。对照第 10 课:GET 按 _id 打一个 shard、Realtime 可读未 refresh;SEARCH 打全部 shard、只看已 refresh——两者之间没有退化路径。' }
    ]
  };

  /* ===== 实验 ===== */
  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};

  window.ESEXPERIMENTS['ch16-00-setup'] = {
    version: 1, id: 'ch16-00-setup',
    title: '实验 0 · 建 tut-l16-qtf:3 主分片,冻结自动 refresh',
    method: 'PUT', path: '/tut-l16-qtf',
    body: {
      settings: { index: { number_of_shards: 3, number_of_replicas: 0, refresh_interval: '-1' } },
      mappings: { properties: { title: { type: 'text' }, n: { type: 'integer' } } }
    },
    predict: '3 个主分片对一次搜索意味着什么?refresh_interval=-1 又冻结了什么?',
    expect: 'acknowledged: true。3 primary:一次 _search 默认扇出到 3 个 shard 组。refresh_interval=-1 关掉 1 秒自动 refresh,让「可搜 = 显式 refresh」完全可控——实验 9-12 靠这条分界线;写入可见性一律 ?refresh=true 手动触发。'
  };
  window.ESEXPERIMENTS['ch16-01-bulk'] = {
    version: 1, id: 'ch16-01-bulk',
    title: '实验 1 · 30 篇文档一次性写入(?refresh=true)',
    method: 'POST', path: '/_bulk?refresh=true',
    body: '{"index":{"_index":"tut-l16-qtf","_id":"1"}}\n{"title":"document number 1 about elasticsearch","n":1}\n{"index":{"_index":"tut-l16-qtf","_id":"2"}}\n{"title":"document number 2 about elasticsearch","n":2}\n{"index":{"_index":"tut-l16-qtf","_id":"3"}}\n{"title":"document number 3 about elasticsearch","n":3}\n{"index":{"_index":"tut-l16-qtf","_id":"4"}}\n{"title":"document number 4 about elasticsearch","n":4}\n{"index":{"_index":"tut-l16-qtf","_id":"5"}}\n{"title":"document number 5 about elasticsearch","n":5}\n{"index":{"_index":"tut-l16-qtf","_id":"6"}}\n{"title":"document number 6 about elasticsearch","n":6}\n{"index":{"_index":"tut-l16-qtf","_id":"7"}}\n{"title":"document number 7 about elasticsearch","n":7}\n{"index":{"_index":"tut-l16-qtf","_id":"8"}}\n{"title":"document number 8 about elasticsearch","n":8}\n{"index":{"_index":"tut-l16-qtf","_id":"9"}}\n{"title":"document number 9 about elasticsearch","n":9}\n{"index":{"_index":"tut-l16-qtf","_id":"10"}}\n{"title":"document number 10 about elasticsearch","n":10}\n{"index":{"_index":"tut-l16-qtf","_id":"11"}}\n{"title":"document number 11 about elasticsearch","n":11}\n{"index":{"_index":"tut-l16-qtf","_id":"12"}}\n{"title":"document number 12 about elasticsearch","n":12}\n{"index":{"_index":"tut-l16-qtf","_id":"13"}}\n{"title":"document number 13 about elasticsearch","n":13}\n{"index":{"_index":"tut-l16-qtf","_id":"14"}}\n{"title":"document number 14 about elasticsearch","n":14}\n{"index":{"_index":"tut-l16-qtf","_id":"15"}}\n{"title":"document number 15 about elasticsearch","n":15}\n{"index":{"_index":"tut-l16-qtf","_id":"16"}}\n{"title":"document number 16 about elasticsearch","n":16}\n{"index":{"_index":"tut-l16-qtf","_id":"17"}}\n{"title":"document number 17 about elasticsearch","n":17}\n{"index":{"_index":"tut-l16-qtf","_id":"18"}}\n{"title":"document number 18 about elasticsearch","n":18}\n{"index":{"_index":"tut-l16-qtf","_id":"19"}}\n{"title":"document number 19 about elasticsearch","n":19}\n{"index":{"_index":"tut-l16-qtf","_id":"20"}}\n{"title":"document number 20 about elasticsearch","n":20}\n{"index":{"_index":"tut-l16-qtf","_id":"21"}}\n{"title":"document number 21 about elasticsearch","n":21}\n{"index":{"_index":"tut-l16-qtf","_id":"22"}}\n{"title":"document number 22 about elasticsearch","n":22}\n{"index":{"_index":"tut-l16-qtf","_id":"23"}}\n{"title":"document number 23 about elasticsearch","n":23}\n{"index":{"_index":"tut-l16-qtf","_id":"24"}}\n{"title":"document number 24 about elasticsearch","n":24}\n{"index":{"_index":"tut-l16-qtf","_id":"25"}}\n{"title":"document number 25 about elasticsearch","n":25}\n{"index":{"_index":"tut-l16-qtf","_id":"26"}}\n{"title":"document number 26 about elasticsearch","n":26}\n{"index":{"_index":"tut-l16-qtf","_id":"27"}}\n{"title":"document number 27 about elasticsearch","n":27}\n{"index":{"_index":"tut-l16-qtf","_id":"28"}}\n{"title":"document number 28 about elasticsearch","n":28}\n{"index":{"_index":"tut-l16-qtf","_id":"29"}}\n{"title":"document number 29 about elasticsearch","n":29}\n{"index":{"_index":"tut-l16-qtf","_id":"30"}}\n{"title":"document number 30 about elasticsearch","n":30}\n',
    predict: 'refresh=true 之后 SEARCH 立刻能看见几篇?每篇落哪个 shard 由什么决定?',
    expect: 'errors: false、30 项全 201。refresh 把这批文档编进 segment,EXTERNAL searcher 立即可搜。落点由第 15 课的路由公式决定(_id 字符串的 Murmur3 取模),下一个实验直接看分布。'
  };
  window.ESEXPERIMENTS['ch16-02-shards'] = {
    version: 1, id: 'ch16-02-shards',
    title: '实验 2 · _cat/shards:3 个 primary 的文档分布',
    method: 'GET', path: '/_cat/shards/tut-l16-qtf?v&h=shard,prirep,state,docs',
    predict: '30 篇在 3 个 shard 上是整齐的 10/10/10 吗?',
    expect: '3 行 STARTED 的 p,docs 大致 10/10/10 但不必精确均匀——哈希路由不是轮转(第 13 课见过 2:1)。这个分布决定了下面每次搜索的 Query 扇出宽度就是 3。'
  };
  window.ESEXPERIMENTS['ch16-03-search'] = {
    version: 1, id: 'ch16-03-search',
    title: '实验 3 · from=0&size=10:hits 是 10,不是 30',
    method: 'POST', path: '/tut-l16-qtf/_search?filter_path=_shards,hits.total,hits.hits._id,hits.hits._score',
    body: { from: 0, size: 10, query: { match: { title: 'elasticsearch' } } },
    predict: 'hits.hits 几条?_shards.total 是 1 还是 3?每个 shard 内部回了几条(响应里看不到,用公式算)?',
    expect: 'hits 10 条、_shards.total = successful = 3。30 条 (docId,score) 候选只存在于 Query 阶段;协调节点截全局 Top-10,Fetch 只搬这 10 篇 _source。若你猜 30,是把每 shard 的 Query 窗口当成了最终响应;若猜 _shards.total=1,是把 SEARCH 当成了 GET。'
  };
  window.ESEXPERIMENTS['ch16-04-profile'] = {
    version: 1, id: 'ch16-04-profile',
    title: '实验 4 · profile:true:searches 与 fetch 两段',
    method: 'POST', path: '/tut-l16-qtf/_search?filter_path=profile.shards.id,profile.shards.fetch.time_in_nanos,hits.hits._id',
    body: { profile: true, size: 10, query: { match: { title: 'elasticsearch' } } },
    predict: '3 个 shard 都有 searches(query 段)吗?都有 fetch 段吗?每个 fetch 是加载 10 篇吗?',
    expect: '每个参与 Query 的 shard 都有 searches(Lucene query/collector 的树);fetch 只有真正执行了 Fetch 的 shard 才有。三个 fetch 加起来加载的正是全局 Top-10 那 10 个 doc——不是每个 shard 各 10 篇。'
  };
  window.ESEXPERIMENTS['ch16-05-profile-size1'] = {
    version: 1, id: 'ch16-05-profile-size1',
    title: '实验 5 · size=1:谁的 fetch 消失了',
    method: 'POST', path: '/tut-l16-qtf/_search?filter_path=profile.shards.id,profile.shards.fetch.time_in_nanos,hits.hits._id',
    body: { profile: true, size: 1, query: { match: { title: 'elasticsearch' } } },
    predict: '全局第 1 名只住在一个 shard 上——另外两个 shard 的 profile 里还会出现 fetch 吗?',
    expect: '只有一个 shard 带 fetch(它包办了全局第 1)。另外两个 shard 的候选全部出局,fillDocIdsToLoad 里槽位是 null,不发 Fetch——但它们仍出现在 searches 里,因为 Query 阶段照打不误。'
  };
  window.ESEXPERIMENTS['ch16-06-deep-fail'] = {
    version: 1, id: 'ch16-06-deep-fail',
    title: '实验 6 · from=10000&size=10:踩 max_result_window',
    method: 'POST', path: '/tut-l16-qtf/_search',
    body: { from: 10000, size: 10, query: { match_all: {} } },
    predict: '按公式每个 shard 要回几条?这次请求能走到 Fetch 阶段吗?',
    expect: 'HTTP 400 illegal_argument_exception:Result window is too large,from + size(10010)超过 index.max_result_window(默认 10000)。注意「公式要 10010」和「闸门卡 10000」是两件事:闸门在分片 preProcess 就抛,请求到不了 Fetch。'
  };
  window.ESEXPERIMENTS['ch16-07-window-edge'] = {
    version: 1, id: 'ch16-07-window-edge',
    title: '实验 7 · from=9990&size=10:恰好过闸',
    method: 'POST', path: '/tut-l16-qtf/_search?filter_path=hits.total,hits.hits._id',
    body: { from: 9990, size: 10, query: { match_all: {} } },
    predict: '窗口 9990+10=10000,能过闸吗?只有 30 篇文档,hits 会是几条?',
    expect: '过闸(等于 10000,不超),hits.hits 为 0——不是被拒,是「没有那么深的文档」;total.value=30。每个 shard 仍按 10000 条窗口准备候选,再被本地 totalNumDocs=实际文档数截断。'
  };
  window.ESEXPERIMENTS['ch16-08-last-page'] = {
    version: 1, id: 'ch16-08-last-page',
    title: '实验 8 · from=20&size=10:30 篇里的最后一页',
    method: 'POST', path: '/tut-l16-qtf/_search?filter_path=hits.hits._id,hits.hits._source.n',
    body: { from: 20, size: 10, query: { match_all: {} }, sort: [{ n: 'asc' }] },
    predict: '会返回哪 10 个 _id?这一页每个 shard 的 Query 窗口是多少条?',
    expect: '_id 21..30(按 n 升序)。每 shard 窗口 from+size=30 条候选(再被本地文档数截断),Fetch 只搬最终 10 篇——from 涨的是 Query 窗口,不是 hits。'
  };
  window.ESEXPERIMENTS['ch16-09-nrt-write'] = {
    version: 1, id: 'ch16-09-nrt-write',
    title: '实验 9 · 写一篇不 refresh 的文档',
    method: 'PUT', path: '/tut-l16-qtf/_doc/nrt',
    body: { title: 'written but not refreshed' },
    predict: '本课索引冻结了自动 refresh:写入返回 201 之后,SEARCH 能看到它吗?GET 呢?',
    expect: 'result: created、_version 1。文档进了 translog 与内存 buffer;因为 refresh_interval=-1 且没带 refresh 参数,它还不在任何 segment 的 EXTERNAL 快照里。下两个实验分别问 GET 和 SEARCH。'
  };
  window.ESEXPERIMENTS['ch16-10-nrt-get'] = {
    version: 1, id: 'ch16-10-nrt-get',
    title: '实验 10 · 同一篇,GET 立刻读得到',
    method: 'GET', path: '/tut-l16-qtf/_doc/nrt?filter_path=found,_id,_version',
    predict: 'SEARCH(马上做实验 11)搜不到的这篇,GET 能读到手吗?',
    expect: 'found: true。GET 是 Realtime 路径:先查 VersionMap、再查 translog(第 10 课),不必等 refresh。这是 GET 与 SEARCH 的第二处分野(第一处是打几个 shard)。'
  };
  window.ESEXPERIMENTS['ch16-11-nrt-count'] = {
    version: 1, id: 'ch16-11-nrt-count',
    title: '实验 11 · 同一篇,SEARCH 数不到',
    method: 'GET', path: '/tut-l16-qtf/_count?q=_id:nrt&filter_path=count',
    predict: 'count 是 0 还是 1?',
    expect: 'count: 0。SEARCH 只看已 refresh 的 EXTERNAL searcher,buffer 里的文档对它不存在。普通集群这里有个 1 秒竞态(自动 refresh 会追上),本课索引把它冻住了,所以 0 是确定的——第 1 课的「近实时」缺口就在这里。'
  };
  window.ESEXPERIMENTS['ch16-12-refresh'] = {
    version: 1, id: 'ch16-12-refresh',
    title: '实验 12 · 手动 _refresh,回去重数',
    method: 'POST', path: '/tut-l16-qtf/_refresh?filter_path=_shards',
    predict: 'refresh 之后重跑实验 11,count 会变多少?',
    expect: '_shards.successful = 3(3 个 primary 各自 refresh)。回去再跑实验 11:count 变 1——一篇文档从「GET 可见」到「SEARCH 可见」,中间隔的就是一次 refresh。'
  };
  window.ESEXPERIMENTS['ch16-13-cleanup'] = {
    version: 1, id: 'ch16-13-cleanup',
    title: '清理 · 删除 tut-l16-qtf',
    method: 'DELETE', path: '/tut-l16-qtf',
    predict: '冻结的 refresh_interval 需要恢复吗?',
    expect: 'acknowledged: true。索引连同设置一起删除,refresh_interval 冻结随之消失——它只活在 tut-l16-qtf 的 settings 里,从没碰过集群全局。'
  };
})();
