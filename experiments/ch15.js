/* experiments/ch15.js — 第 15 课:旗舰动画 #3(路由公式演算)+ 实验 */
(function () {
  'use strict';

  /* ===== 旗舰动画 #3:hash(routing) % number_of_primary_shards 演算 ===== */
  var H_BROWN = 741580288;    // murmur3("brown") — 与实验 2/5 的落点严格一致
  var SHARD = 1;              // Math.floorMod(H_BROWN, 3)

  var PNAMES = ['① 取 _routing', '② murmur3 哈希', '③ floorMod(h,3)', '④ 查路由表'];
  var PSUBS = ['"brown"', '741580288', 'shard = 1', 'shard 1 的副本们'];

  function chip(x, y, w, h, cls, op) {
    return '<rect x="' + x + '" y="' + y + '" width="' + w + '" height="' + h + '" rx="7" class="' + cls + '"' +
      (op != null ? ' opacity="' + op + '"' : '') + '/>';
  }
  function txt(x, y, cls, t, op) {
    return '<text x="' + x + '" y="' + y + '" text-anchor="middle" class="' + cls + '"' +
      (op != null ? ' opacity="' + op + '"' : '') + '>' + t + '</text>';
  }

  /* 顶部流水线:lit = 已点亮的格子数(0..4),最新点亮的一格 fp-pop */
  function pipeline(lit, popNewest) {
    var s = '', xs = [15, 205, 395, 585], w = 160;
    for (var i = 0; i < 4; i++) {
      if (i < 3) {
        var aLit = i < lit - 1;
        s += '<line x1="' + (xs[i] + w + 4) + '" y1="48" x2="' + (xs[i + 1] - 6) + '" y2="48" class="fig-arrow"' +
          (aLit ? '' : ' opacity="0.3"') + ' marker-end="url(#ah15rt)"/>';
      }
      var isHot = i === lit - 1;
      s += '<g opacity="' + (i < lit ? 1 : 0.38) + '">';
      s += chip(xs[i], 16, w, 64, isHot ? 'fig-box-hot' + (isHot && popNewest ? ' fp-pop' : '') : 'fig-box');
      s += txt(xs[i] + w / 2, 40, 'fig-name', PNAMES[i]);
      s += txt(xs[i] + w / 2, 60, 'fig-key', PSUBS[i]);
      s += '</g>';
    }
    return s;
  }

  /* 中部演算区:纯文本行 */
  function midText(lines) {
    var ys = [124, 150, 176, 200], s = '';
    for (var i = 0; i < lines.length; i++) {
      s += txt(380, ys[i], lines[i][0], lines[i][1]);
    }
    return s;
  }

  /* 中部演算区:cluster state 路由表小图。mode: healthy | ars | single */
  function table(mode) {
    var compact = mode !== 'healthy';
    var ys = compact ? [126, 160, 194] : [130, 168, 206];
    var rh = compact ? 28 : 34;
    var s = txt(340, 116, 'fig-sub', 'cluster state:IndexRoutingTable["tut-l15-route"]');
    if (mode === 'healthy') {
      s += txt(676, 116, 'fig-sub', 'P=主分片 R=副本');
    }
    for (var r = 0; r < 3; r++) {
      var y = ys[r], cy = y + rh / 2 + 4;
      var hot = r === SHARD;
      s += '<g opacity="' + (hot ? 1 : 0.55) + '">';
      s += chip(45, y, 86, rh, hot ? 'fig-box-hot' + (mode === 'healthy' ? ' fp-pop' : '') : 'fig-box');
      s += txt(88, cy, 'fig-key', 'shard ' + r);
      s += chip(145, y, 170, rh, 'fig-box');
      s += txt(230, cy, 'fig-sub', 'P · node-1');
      if (mode === 'single') {
        s += chip(325, y, 170, rh, 'fig-box', 0.45);
        s += txt(410, cy, 'fig-sub', 'R · UNASSIGNED');
      } else {
        s += chip(325, y, 170, rh, 'fig-box');
        s += txt(410, cy, 'fig-sub', 'R · node-2');
      }
      s += '</g>';
      if (mode === 'ars' && hot) {
        s += txt(600, cy, 'fig-sub', '← 谁快挑谁');
      }
    }
    if (mode === 'ars') {
      s += txt(380, 244, 'fig-sub', 'ARS:按历史响应时间 + 队列长度挑一份;主副一视同仁,写路径除外(先主)');
    } else if (mode === 'single') {
      s += txt(380, 244, 'fig-sub', '单节点:副本无处放 → yellow;除数想变?Final 拒绝(ch05 的墙),reindex 才是正道');
    }
    return s;
  }

  function stepSvg(k) {
    var lit = k === 0 ? 0 : Math.min(k, 4);
    var s = '<svg viewBox="0 0 760 262" xmlns="http://www.w3.org/2000/svg">';
    s += '<defs><marker id="ah15rt" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">' +
      '<path d="M 0 0 L 10 5 L 0 10 z" class="fig-arrowhead"/></marker></defs>';
    s += pipeline(lit, k <= 4);
    if (k === 0) {
      s += midText([
        ['fig-name', 'PUT /tut-l15-route/_doc/brown-1?routing=brown'],
        ['fig-key fp-pulse', 'shard = floorMod( murmur3(_routing), 3 )'],
        ['fig-sub', '三个可变点:钥匙 _routing、哈希 murmur3、除数 3'],
        ['fig-sub', '除数一旦定下,终身不改——本课的暗线']
      ]);
    } else if (k === 1) {
      s += midText([
        ['fig-key', 'effectiveRouting = routing != null ? routing : id'],
        ['fig-sub', '带了 routing=brown → 用 "brown";不带 → 用 _id'],
        ['fig-sub', '自动 _id 是随机串,散列后近似均匀铺开'],
        ['fig-sub', '写、GET、搜索必须同一把钥匙(ch13 的双钥匙图)']
      ]);
    } else if (k === 2) {
      s += midText([
        ['fig-key', 'h = murmur3("brown") = 741580288'],
        ['fig-sub', '32 位有符号整数,可能是负——所以下一步不是 %'],
        ['fig-sub', '不用 String.hashCode:JDK 换版本可能变,murmur3 不会'],
        ['fig-sub', '同一字符串永远同一 h,永远同一片']
      ]);
    } else if (k === 3) {
      s += midText([
        ['fig-key', 'shard = Math.floorMod(741580288, 3) = 1'],
        ['fig-sub', '负哈希对照:"brown-1" 的 h = -616020358'],
        ['fig-key', 'h % 3 = -1,没有 -1 号分片;floorMod(h,3) = 2'],
        ['fig-sub', '除数 3 = number_of_primary_shards:Property.Final']
      ]);
    } else if (k === 4) {
      s += table('healthy');
    } else if (k === 5) {
      s += table('ars');
    } else {
      s += table('single');
    }
    s += '</svg>';
    return s;
  }

  var NOTES = [
    '写入篇最后一块拼图:一篇文档到底住哪。请求带着 _id=brown-1、routing=brown 进来,片号完全由公式决定——钥匙、哈希、除数。先亮全貌,下面逐步演算。',
    '第一步取钥匙。_routing 不传就用 _id——自动生成的随机串,散列后近似均匀。注意:钥匙不是优化项,同一篇文档此后每次读写都得是同一把,否则片号就变了。',
    'murmur3 把任意字符串压成一个 32 位有符号整数,"brown" 得 741580288。选它而不是 String.hashCode,要的是跨版本、跨语言都稳定:片号不能依赖 JDK 实现。',
    '取模登场。Java 的 % 遇负数返回负数——"brown-1" 的哈希是 -616020358,% 会算出 -1 号分片;floorMod 保证落在 [0,3)。除数 3 就是 number_of_primary_shards,第 5 课那道 Final 墙的机制本体。',
    '片号只是编号,还要换算成「哪台机器上的哪份拷贝」。答案不在节点上现算,而是查 cluster state 的路由表:每片一组,主副本各在哪台。shard 1 这一组被点亮。',
    '一组里选谁?没有 preference 时走自适应副本选择(ARS,默认开):按各节点历史响应时间与队列长度估计谁最快,主副一视同仁——只读请求读谁都是同一份数据。写路径例外:必须先主后副(第 13 课)。',
    '对照组:单节点 + 1 副本,副本 UNASSIGNED,选片时永远只剩 primary,集群 yellow。而除数 N 是 Final:N 一变,所有旧钥匙全部算出新片号,文档就地蒸发——想要不同分片数,只能 reindex 到新索引。'
  ];

  window.ESFLOWS = window.ESFLOWS || {};
  window.ESFLOWS['ch15-routing-formula'] = {
    version: 1,
    id: 'ch15-routing-formula',
    title: '路由公式演算:从一把钥匙到一片分片',
    speed: 2000,
    steps: NOTES.map(function (note, i) { return { svg: stepSvg(i), note: note }; })
  };

  /* ===== 实验 ===== */
  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};
  window.ESEXPERIMENTS['ch15-00-setup'] = {
    version: 1, id: 'ch15-00-setup',
    title: '实验 0 · 建索引 tut-l15-route(3 主 1 副)',
    method: 'PUT', path: '/tut-l15-route',
    body: { settings: { number_of_shards: 3, number_of_replicas: 1 } },
    predict: '单节点、3 主 1 副:集群 health 会是什么色?6 份分片拷贝里几份能落上节点?',
    expect: 'acknowledged + shards_acknowledged 都是 true。集群从此 yellow:3 个主分片都在本节点 STARTED,3 个副本无处放——第 1 课的结构性黄,不是故障。这份数据还没动,先当路由公式的实验品。'
  };
  window.ESEXPERIMENTS['ch15-01-shards'] = {
    version: 1, id: 'ch15-01-shards',
    title: '实验 1 · _cat/shards:state 列是哪套枚举',
    method: 'GET', path: '/_cat/shards/tut-l15-route?v&h=index,shard,prirep,state,docs,store,node',
    predict: '先猜:6 行里 prirep=p 和 r 各自的 state 是什么?这一列里会不会出现 CREATED、RECOVERING、CLOSED?',
    expect: '6 行:p 三行 STARTED、r 三行 UNASSIGNED(没有 node 名、没有 docs/store 数字)。state 列来自 RestShardsAction 的 table.addCell(shard.state()),是 ShardRoutingState——永远只有 UNASSIGNED/INITIALIZING/STARTED/RELOCATING 四个词。UNASSIGNED 不是 CLOSED:本节点根本没为那份副本 new IndexShard。CREATED→STARTED 只有几十毫秒,这列抓不住。'
  };
  window.ESEXPERIMENTS['ch15-02-put-routing'] = {
    version: 1, id: 'ch15-02-put-routing',
    title: '实验 2 · 带 routing 写一篇(动画同款钥匙)',
    method: 'PUT', path: '/tut-l15-route/_doc/brown-1?routing=brown&refresh=true',
    body: { body: 'the quick brown fox' },
    predict: 'routing=brown、3 个主分片:这篇会落哪片?副本 UNASSIGNED 会挡住写入吗?_shards 里 total/successful/failed 各是多少?',
    expect: '201,result: created。_shards: total 2(复制组 = 1 主 + 1 副)、successful 1(主分片)、failed 0——UNASSIGNED 的副本不在复制组里,写照样成功。OperationRouting.generateShardId:钥匙是 "brown"(不是 _id),落在 shard 1。refresh=true 让下一步的 docs 计数立刻可见。'
  };
  window.ESEXPERIMENTS['ch15-03-cat-docs'] = {
    version: 1, id: 'ch15-03-cat-docs',
    title: '实验 3 · 落点对照:docs 只在一片上 +1',
    method: 'GET', path: '/_cat/shards/tut-l15-route?v&h=shard,prirep,state,docs',
    predict: 'brown-1 写进 shard 1:哪个主分片的 docs 是 1?再写一篇 ?routing=brown 的文档,docs 会怎么变?',
    expect: 'shard 1 的 primary docs=1,shard 0/2 的 primary docs=0;UNASSIGNED 的 replica 行没有数字。再写一篇同钥匙的,还是这片(docs 变 2)——同一把钥匙永远同一片,这是确定性不是巧合。docs 按片统计,因为分片就是各管各的 Lucene 索引(图 1)。'
  };
  window.ESEXPERIMENTS['ch15-04-ss-all'] = {
    version: 1, id: 'ch15-04-ss-all',
    title: '实验 4 · _search_shards 不带钥匙:全部片',
    method: 'GET', path: '/tut-l15-route/_search_shards',
    predict: '不带 routing,一次搜索要打几片?每个片组里有几份拷贝?',
    expect: 'shards 数组 3 组(shard 0/1/2),此刻每组只有 primary(副本 UNASSIGNED)。不带 routing 的搜索要广播全部主分片——第 16 课 Query Then Fetch 的第一步就是这么来的;这也解释了为什么 routing 能省 fan-out。'
  };
  window.ESEXPERIMENTS['ch15-05-ss-routing'] = {
    version: 1, id: 'ch15-05-ss-routing',
    title: '实验 5 · _search_shards 带 routing(对答案)',
    method: 'GET', path: '/tut-l15-route/_search_shards?routing=brown',
    predict: '带 routing=brown 会剩几组?和实验 2/3 的落点(动画算出的 shard 1)一致吗?',
    expect: '只剩 1 组:shard 1。OperationRouting.generateShardId:effectiveRouting = "brown" → Murmur3HashFunction.hash → Math.floorMod(h, 3)——与写入 brown-1 时算的是同一个数,所以 _search_shards 就是路由公式的「对答案」端点。这个片号从建索引那天起终身不变。'
  };
  window.ESEXPERIMENTS['ch15-06-get-miss'] = {
    version: 1, id: 'ch15-06-get-miss',
    title: '实验 6 · 钥匙错了:不带 routing 的 GET 扑空',
    method: 'GET', path: '/tut-l15-route/_doc/brown-1',
    predict: '文档明明写成功了,不带 routing 去 GET,found 是 true 还是 false?状态码呢?',
    expect: 'HTTP 404 + found:false。不带 routing 时 effectiveRouting = _id:murmur3("brown-1") = -616020358,floorMod 得 shard 2——钥匙错了,GET 敲了 shard 2 的门,那片当然没有这篇。注意这是「查无此文档」的 404,不是路由不存在的 400:门敲对了,屋里没这个人。'
  };
  window.ESEXPERIMENTS['ch15-07-get-hit'] = {
    version: 1, id: 'ch15-07-get-hit',
    title: '实验 7 · 带钥匙直取一片',
    method: 'GET', path: '/tut-l15-route/_doc/brown-1?routing=brown',
    predict: '只多一个 query 参数,这次 found 呢?响应里哪个字段会回显你的钥匙?',
    expect: 'found:true,响应里的 _routing: "brown" 会把钥匙回显给你。GET 带 routing 只打 shard 1 一片;片内的主/副由自适应副本选择挑(单节点只有 primary 可选)。对比实验 6:不带钥匙是「算错片」,带上是「直取一片」。'
  };
  window.ESEXPERIMENTS['ch15-08-replicas-0'] = {
    version: 1, id: 'ch15-08-replicas-0',
    title: '实验 8 · 副本数在线归零(Dynamic)',
    method: 'PUT', path: '/tut-l15-route/_settings',
    body: { number_of_replicas: 0 },
    predict: 'number_of_replicas 能在线改吗?改成 0 会删数据、会重启吗?',
    expect: 'acknowledged: true,数据一个不动。它是 Dynamic + IndexScope(第 5 课实验 5 同款),改的是 ClusterState 里的索引设置;主分片一个不少,只是不再要求副本。隔壁 number_of_shards 是取模的除数,连试的机会都没有——实验 11 见。'
  };
  window.ESEXPERIMENTS['ch15-09-health-green'] = {
    version: 1, id: 'ch15-09-health-green',
    title: '实验 9 · yellow → green',
    method: 'GET', path: '/_cluster/health/tut-l15-route?v',
    predict: '副本归零后,这个索引的健康状态?unassigned_shards 还剩几个?',
    expect: 'status: green,unassigned_shards: 0——yellow 的病因(副本无处放)被拔掉了。想再看 yellow:把 number_of_replicas 改回 1(同一条命令换个数字),health 立刻变回 yellow。0↔1 在线往返、不动任何数据,这正是 Dynamic 与 Final 的分界线。'
  };
  window.ESEXPERIMENTS['ch15-10-segments'] = {
    version: 1, id: 'ch15-10-segments',
    title: '实验 10 · _cat/segments:每片自己的 Lucene 段',
    method: 'GET', path: '/_cat/segments/tut-l15-route?v&h=index,shard,prirep,segment,generation,size',
    predict: '3 个主分片,各有几个 segment?没写过文档的分片呢?',
    expect: 'segment 按分片分组列出:收过文档的 shard 1 有一段(_0 一类),没写过文档的分片没有段(以你的返回为准)。副本归零后列表里只剩 primary。每段属于一个分片、merge 也在片内做——「分片即独立 Lucene 索引」的直接佐证。'
  };
  window.ESEXPERIMENTS['ch15-11-final-wall'] = {
    version: 1, id: 'ch15-11-final-wall',
    title: '实验 11 · 再撞 Final 的墙:改主分片数',
    method: 'PUT', path: '/tut-l15-route/_settings',
    body: { 'index.number_of_shards': 5 },
    predict: '状态码?报错文案里会出现哪个词?这次你能说出机制了吗?',
    expect: '400:final index setting [index.number_of_shards], not updateable——第 5 课实验 4 撞过的同一道墙。机制在本课:它是 floorMod 的除数,N 一变,brown-1 的片号就从 1 变成别的数,按新除数再也算不到它住的那片。ES 没有在线重散列,所以 Property.Final 干脆拒绝;要 5 片,建新索引 reindex。'
  };
  window.ESEXPERIMENTS['ch15-12-req-create'] = {
    version: 1, id: 'ch15-12-req-create',
    title: '实验 12 · 建一个强制钥匙的索引(_routing.required)',
    method: 'PUT', path: '/tut-l15-req',
    body: { mappings: { _routing: { required: true } } },
    predict: '把 required 写进 mappings,等于把钥匙从「约定」升级成什么?',
    expect: 'acknowledged: true。从此这个索引的每个写请求必须带 routing——用映射把钥匙合同显式化,忘带不会「静默落错片」(它本来也落不错,只是会用 _id 兜底),而是直接被拒。下一步看拒成什么样。'
  };
  window.ESEXPERIMENTS['ch15-13-req-missing'] = {
    version: 1, id: 'ch15-13-req-missing',
    title: '实验 13 · 不带钥匙写:400 routing_missing_exception',
    method: 'PUT', path: '/tut-l15-req/_doc/1',
    body: { title: 'no routing here' },
    predict: '状态码 400 还是 404?异常叫什么?这次失败发生在路由计算之前还是之后?',
    expect: '400,type: routing_missing_exception(routing is missing for [tut-l15-req])。检查在 IndexRequest 进分片之前(mappingLookup.routingRequired()),根本轮不到 generateShardId——错误阶梯里「请求本身不合格」的 400 档,和实验 6「资源查无」的 404 档分清楚。'
  };
  window.ESEXPERIMENTS['ch15-14-cleanup-route'] = {
    version: 1, id: 'ch15-14-cleanup-route',
    title: '清理 1 · 删除 tut-l15-route',
    method: 'DELETE', path: '/tut-l15-route',
    predict: '删除会连带删掉什么?',
    expect: 'acknowledged: true。3 个主分片连同各自的 segments/translog 全部消失;replicas=0 的设置随索引一起埋葬,不留集群级残留。'
  };
  window.ESEXPERIMENTS['ch15-15-cleanup-req'] = {
    version: 1, id: 'ch15-15-cleanup-req',
    title: '清理 2 · 删除 tut-l15-req',
    method: 'DELETE', path: '/tut-l15-req',
    predict: '这个只写过一次失败写入的索引,删掉后还剩什么?',
    expect: 'acknowledged: true。实验 13 那篇根本没写进去(400 在进分片前就被拦下),索引是空壳;删除后本课零残留。'
  };
})();
