/* experiments/ch30.js — 第 30 课:全景回顾自测清单 + 收官动画(六篇接到一次请求上) */
(function () {
  'use strict';

  /* ===== 动画:一次 POST /_search 的全链回放(全站收官) ===== */
  function rect(x, y, w, h, cls, anim) {
    return '<rect x="' + x + '" y="' + y + '" width="' + w + '" height="' + h + '" rx="9" class="' + cls + (anim ? ' ' + anim : '') + '"/>';
  }
  function txt(x, y, s, cls, warn, anim) {
    var st = warn ? ' style="fill: rgb(var(--warn))"' : '';
    return '<text x="' + x + '" y="' + y + '" text-anchor="middle" class="' + cls + (anim ? ' ' + anim : '') + '"' + st + '>' + s + '</text>';
  }
  function defs(id) {
    return '<defs><marker id="' + id + '" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
      + '<path d="M 0 0 L 10 5 L 0 10 z" class="fig-arrowhead"/></marker></defs>';
  }
  function bottom(title, sub) {
    var s = rect(15, 240, 730, 48, 'fig-box-hot', 'fp-pop');
    s += txt(380, 261, title, 'fig-name');
    s += txt(380, 281, sub, 'fig-sub');
    return s;
  }

  /* 步骤 1:这一次请求 */
  function step1() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('f1');
    s += rect(15, 15, 730, 56, 'fig-box-hot');
    s += txt(380, 38, 'POST /tut-l30-docs/_search {"query":{"match":{"title":"brown"}}}', 'fig-name');
    s += txt(380, 60, '收官不把 29 课贴成墙:六篇的职责全挂在这条链上', 'fig-sub');
    s += rect(15, 88, 355, 76, 'fig-box');
    s += txt(192, 112, '输入的前提', 'fig-name');
    s += txt(192, 136, 'doc 1 已写入且已 refresh', 'fig-sub');
    s += txt(192, 156, '1 分片 0 副本,refresh_interval=-1', 'fig-sub');
    s += txt(192, 176, '(把运气冻住,只剩原理)', 'fig-sub');
    s += rect(390, 88, 355, 76, 'fig-box');
    s += txt(567, 112, '你将看到', 'fig-name');
    s += txt(567, 136, '认证 → 路由 → 动作名', 'fig-sub');
    s += txt(567, 156, '→ 快照选 shard → 两阶段', 'fig-sub');
    s += txt(567, 176, '→ EXTERNAL searcher → hits', 'fig-sub');
    s += rect(15, 180, 730, 44, 'fig-box');
    s += txt(380, 200, '六篇不是 30 个并列目录,是同一条请求上的不同角色', 'fig-key');
    s += txt(380, 217, '你还不会追的那一层,就是下一份要打开的模块', 'fig-sub');
    s += bottom('一次请求,换几次身份、碰几块存储', '类名不进方块——每一格都是数据变成了什么');
    return s + '</svg>';
  }

  /* 步骤 2:第 29/6/7 课:闸与门 */
  function step2() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('f2');
    s += rect(15, 15, 355, 96, 'fig-box');
    s += txt(192, 39, '认证闸(第 29 课)', 'fig-name');
    s += txt(192, 63, '开安全的节点:先 401 后 200', 'fig-sub');
    s += txt(192, 83, '本站 9200:匿名直过', 'fig-sub');
    s += txt(192, 103, '凭据过了才进 handler', 'fig-sub');
    s += rect(390, 15, 355, 96, 'fig-box');
    s += txt(567, 39, '路由门(第 6 课)', 'fig-name');
    s += txt(567, 63, 'PathTrie 命中', 'fig-sub');
    s += txt(567, 83, 'POST /{index}/_search', 'fig-sub');
    s += txt(567, 103, '未注册路径 → 400 no handler', 'fig-sub');
    s += rect(15, 128, 730, 92, 'fig-box');
    s += txt(380, 152, '动作名接头(第 7 课)', 'fig-key');
    s += txt(380, 176, 'execute(TransportSearchAction.TYPE) —— HTTP 层到协调层的桥是 ActionType', 'fig-sub');
    s += txt(380, 196, '两套名字:rest usage 的 search_action ≠ action 的 indices:data/read/search', 'fig-sub', true);
    s += txt(380, 216, '分片相位再挂后缀:[phase/query] 与 [phase/fetch/id]', 'fig-sub');
    s += bottom('REST 只适配:把 JSON 填进 SearchRequest,不查 Lucene 不碰 Engine', 'HTTP 断开时 RestCancellableNodeClient 负责取消 task——仍是适配层职责');
    return s + '</svg>';
  }

  /* 步骤 3:第 21/15 课:快照与 shard */
  function step3() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('f3');
    s += rect(15, 15, 730, 50, 'fig-box');
    s += txt(380, 36, 'executeRequest 第一件事:clusterService.state() 拿快照', 'fig-name');
    s += txt(380, 56, '读的是不可变 ClusterState(第 21 课),不是会原地改的黑板', 'fig-sub');
    s += rect(15, 80, 355, 96, 'fig-box');
    s += txt(192, 104, 'RoutingTable 列 shard', 'fig-name');
    s += txt(192, 128, '本例:只有 s0(1 分片 0 副本)', 'fig-sub');
    s += txt(192, 148, 'doc 1 当初怎么进的 s0?', 'fig-sub');
    s += txt(192, 168, '第 15 课:hash(routing) % N', 'fig-sub');
    s += rect(390, 80, 355, 96, 'fig-box');
    s += txt(567, 104, '副本约束(第 22/23 课)', 'fig-name');
    s += txt(567, 128, 'RoutingTable 是已 commit 的', 'fig-sub');
    s += txt(567, 148, '共识产物(谁当 leader', 'fig-sub');
    s += txt(567, 168, '决定了你读的是不是真理)', 'fig-sub');
    s += rect(15, 192, 730, 34, 'fig-box');
    s += txt(380, 212, '多分片时:副本不会与同号 primary 同节点——那是分配期(第 23 课)的事,搜索期不再决定', 'fig-sub');
    s += bottom('协调节点拿一份快照,决定 Query 阶段打哪些 shard', '单节点扇出可能不出网——但模型仍是 Query Then Fetch');
    return s + '</svg>';
  }

  /* 步骤 4:第 16/17 课:两阶段 */
  function step4() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('f4');
    s += rect(15, 15, 355, 96, 'fig-box');
    s += txt(192, 39, 'QUERY 阶段', 'fig-name');
    s += txt(192, 63, '各 shard 回 (docId, score)', 'fig-sub');
    s += txt(192, 83, '每个 shard 回 from+size 条', 'fig-sub');
    s += txt(192, 103, 'getTopDocsSize = 0+10 = 10', 'fig-sub');
    s += rect(390, 15, 355, 96, 'fig-box');
    s += txt(567, 39, 'FETCH 阶段', 'fig-name');
    s += txt(567, 63, '协调节点先选全局 Top-N', 'fig-sub');
    s += txt(567, 83, '只向持有者要 N 篇 _source', 'fig-sub');
    s += txt(567, 103, 'fillDocIdsToLoad 分组(第 16 课)', 'fig-sub');
    s += rect(15, 128, 730, 92, 'fig-box');
    s += txt(380, 152, '防御性拒绝:from=10000&size=10 → 10010 撞窗', 'fig-key');
    s += txt(380, 176, '实测 400:Result window is too large ... [10000] but was [10010]', 'fig-sub');
    s += txt(380, 196, '那两个数字就是 getTopDocsSize 算出来的——窗口在扇出前就检查', 'fig-sub');
    s += txt(380, 216, '聚合内存尖峰同理:熔断 429 杀请求不杀节点(第 25 课)', 'fig-sub');
    s += bottom('先比分,再取正文——SEARCH 不是放大的 GET', '单 shard 可跳过第二次往返,但两阶段语义不变');
    return s + '</svg>';
  }

  /* 步骤 5:第 14/10 课:数据节点这一跳 */
  function step5() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('f5');
    s += rect(15, 15, 730, 50, 'fig-box');
    s += txt(380, 36, 'SearchService.executeQueryPhase(ShardSearchRequest, task, listener)', 'fig-name');
    s += txt(380, 56, '返回值 void,结果从 listener 回去——等待不占线程(第 8 课的形状)', 'fig-sub');
    s += rect(15, 80, 355, 96, 'fig-box-hot');
    s += txt(192, 104, 'SEARCH 这条路', 'fig-name');
    s += txt(192, 128, 'acquireSearcher 默认 EXTERNAL', 'fig-sub');
    s += txt(192, 148, '只看见上次 refresh 的快照', 'fig-sub');
    s += txt(192, 168, '未 refresh → 0 hits(实测)', 'fig-sub', true);
    s += rect(390, 80, 355, 96, 'fig-box');
    s += txt(567, 104, 'GET 那条路(第 10 课)', 'fig-name');
    s += txt(567, 128, 'realtime:VersionMap → Translog', 'fig-sub');
    s += txt(567, 148, '未 refresh 也立刻可见', 'fig-sub');
    s += txt(567, 168, '不要去 InternalEngine.get 找 SEARCH', 'fig-sub', true);
    s += rect(15, 192, 730, 34, 'fig-box');
    s += txt(380, 212, '实验 7-11 的实测:doc2 未 refresh 时 SEARCH 0 hits、GET 200、refresh 后 SEARCH 1 hit', 'fig-sub');
    s += bottom('同一份索引,两条请求读两个世界', 'Engine.acquireSearcher 的一个默认参数,就是近实时的全部秘密');
    return s + '</svg>';
  }

  /* 步骤 6:第 3 步:测试钉不变量 */
  function step6() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('f6');
    s += rect(15, 15, 730, 50, 'fig-box');
    s += txt(380, 36, '源码说「会怎么走」;测试说「作者认为怎样算对、必须怎样失败」', 'fig-name');
    s += txt(380, 56, '按命名找,不全仓库瞎搜:生产类同包 *Tests;HTTP 契约找 yaml', 'fig-sub');
    s += rect(15, 80, 355, 96, 'fig-box');
    s += txt(192, 104, 'RestSearchActionTests', 'fig-name');
    s += txt(192, 128, '.testIllegalSearchType', 'fig-sub');
    s += txt(192, 148, '钉住:No search type for', 'fig-sub');
    s += txt(192, 168, '[some_search_type](实测同文案)', 'fig-sub');
    s += rect(390, 80, 355, 96, 'fig-box');
    s += txt(567, 104, 'yaml search/30_limits.yml', 'fig-name');
    s += txt(567, 128, 'catch: + from:10000', 'fig-sub');
    s += txt(567, 148, '断言文案含 10010', 'fig-sub');
    s += txt(567, 168, '找的是 catch 文案,不是 80 行 hits', 'fig-sub');
    s += rect(15, 192, 730, 34, 'fig-box');
    s += txt(380, 212, '测试基类分工:ESTestCase 单测 / ESSingleNode 单节点 / ESInteg 多节点 / yaml 走真实 HTTP', 'fig-sub');
    s += bottom('看见 catch: 就知道它在钉错误文案', '补测试往往比改实现更接近第 3 步——也是贡献的起点');
    return s + '</svg>';
  }

  /* 步骤 7:收官 */
  function step7() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('f7');
    s += rect(15, 15, 730, 50, 'fig-box-hot');
    s += txt(380, 38, '阅读主链:REST → TransportAction → 测试', 'fig-name');
    s += txt(380, 60, '入口永远是一条 HTTP 路径(RestXxxAction.routes()),不是一个包名', 'fig-sub');
    s += rect(15, 80, 355, 96, 'fig-box');
    s += txt(192, 104, '三个工具', 'fig-name');
    s += txt(192, 128, '先接口后实现(Engine 抽象在前)', 'fig-sub');
    s += txt(192, 148, '用命名跳文件(Rest/Transport/', 'fig-sub');
    s += txt(192, 168, 'Service/Internal/Abstract)', 'fig-sub');
    s += rect(390, 80, 355, 96, 'fig-box');
    s += txt(567, 104, '哲学当过滤器', 'fig-name');
    s += txt(567, 128, '分片最小执行 / 近实时 / 全异步', 'fig-sub');
    s += txt(567, 148, '快照不可变 / 先过滤后平衡', 'fig-sub');
    s += txt(567, 168, '防御性拒绝 / 可插拔', 'fig-sub');
    s += rect(15, 192, 730, 34, 'fig-box');
    s += txt(380, 212, '下一个模块:向量 kNN、ES|QL(POST /_query)、某个 x-pack——从一条真实路径走进去', 'fig-sub');
    s += bottom('30 课收官:你已经能从 curl 追到倒排表', '迷路时问:这段代码在保护哪条不变量?');
    return s + '</svg>';
  }

  window.ESFLOWS = window.ESFLOWS || {};
  window.ESFLOWS['ch30-finale'] = {
    version: 1,
    id: 'ch30-finale',
    title: '一次 POST /_search 的全链回放',
    speed: 2400,
    steps: [
      { svg: step1(), note: '收官回放:索引已有 doc 1 且已 refresh,客户端发 POST /tut-l30-docs/_search。六篇不是 30 个并列目录,是同一条请求上的不同角色;你还不会追的那一层,就是下一份要打开的模块。' },
      { svg: step2(), note: '第 29/6/7 课:凭据过闸才进 handler(9200 匿名直过、9201 世界里 401 在前);PathTrie 命中 POST /{index}/_search,未注册是 400 no handler;REST 只适配,把 JSON 填进 SearchRequest 交给 execute(TYPE)。' },
      { svg: step3(), note: '第 21/15/22/23 课:executeRequest 开头拿不可变 ClusterState 快照,RoutingTable 列出 shard;doc 当初靠 hash(routing)%N 进的 s0;你读的是已 commit 的共识产物——分配约束在分配期就定了。' },
      { svg: step4(), note: '第 16/17 课:QUERY 各 shard 回 from+size 条 (docId,score)(getTopDocsSize=0+10),协调选全局 Top-N 后 FETCH 只取 N 篇 _source。from=10000 → 10010 撞窗 400,数字就是 getTopDocsSize 算的。' },
      { svg: step5(), note: '第 8/10/14 课:executeQueryPhase 返回 void、结果走 listener——等待不占线程。SEARCH 走 acquireSearcher 默认的 EXTERNAL(只看 refresh 后快照);realtime GET 走 VersionMap→Translog 是另一条路。实测:未 refresh 时 SEARCH 0 hits、GET 200。' },
      { svg: step6(), note: '第 3 步:用测试钉不变量。同包 RestSearchActionTests.testIllegalSearchType 钉 No search type 文案(实测同款);yaml search/30_limits.yml 用 catch: 断言 10010——测试是约束清单,不是小说。' },
      { svg: step7(), note: '收官:主链三步 REST → TransportAction → 测试;三个工具(先接口后实现、命名跳文件、哲学当过滤器)。下一个模块从一条真实 REST 路径走进去——入口永远是 routes(),不是包名。' }
    ]
  };

  /* ===== 自测清单实验(9200,全链可复现) ===== */
  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};

  window.ESEXPERIMENTS['ch30-01-setup'] = {
    version: 1, id: 'ch30-01-setup',
    title: '实验 1 · 建 tut-l30-docs:refresh_interval=-1',
    method: 'PUT', path: '/tut-l30-docs',
    body: { settings: { number_of_shards: 1, number_of_replicas: 0, refresh_interval: '-1' } },
    predict: '为什么收官清单要把自动 refresh 关掉?',
    expect: 'acknowledged: true。默认约 1 秒的 refresh 会让「未 refresh 不可见」实验赌运气——第 16 课同款纪律:冻住自动 refresh,可见性就只剩原理。后面实验 7-11 依赖这一点做到零竞态。'
  };

  window.ESEXPERIMENTS['ch30-02-doc1'] = {
    version: 1, id: 'ch30-02-doc1',
    title: '实验 2 · 写 doc 1(brown fox),显式 refresh',
    method: 'PUT', path: '/tut-l30-docs/_doc/1?refresh=true',
    body: { title: 'the quick brown fox' },
    predict: 'refresh=true 之后,SEARCH 立刻能看见它吗?',
    expect: 'result: created,forced_refresh: true。能——SEARCH 看 EXTERNAL searcher,显式 refresh 把新段纳入快照(第 14 课)。这一次写入也走了完整写入路径:ingest(无管道)→ 路由 s0 → buffer → refresh 开段。'
  };

  window.ESEXPERIMENTS['ch30-03-search-brown'] = {
    version: 1, id: 'ch30-03-search-brown',
    title: '实验 3 · POST _search match brown:hits 1',
    method: 'POST', path: '/tut-l30-docs/_search?filter_path=hits.total,hits.hits._id,hits.hits._score',
    body: { query: { match: { title: 'brown' } } },
    predict: 'hits.total 是几?_score 为什么不是 1.0?',
    expect: '1 命中,_id=1。match 把 brown 切成单个 token 走 SHOULD(第 18 课),BM25 给出非 1 分(第 20 课)——这就是图 1 最底下那格:客户端拿到 hits。接下来整课追的都是这一次 POST。'
  };

  window.ESEXPERIMENTS['ch30-04-no-route'] = {
    version: 1, id: 'ch30-04-no-route',
    title: '实验 4 · 自测 1:未注册路径是 400,不是 404',
    method: 'GET', path: '/tut-l30-docs/_not_a_real_endpoint',
    body: null,
    predict: '随手编的路径,回 404 还是 400?',
    expect: '400 + no handler found for uri——PathTrie 一个 Handler 都配不上是「路由没认领」(第 6/7 课口径);404 留给「路由命中、资源不存在」(GET 不存在的索引/文档)。分清这两个,排障少绕一圈。'
  };

  window.ESEXPERIMENTS['ch30-05-illegal-type'] = {
    version: 1, id: 'ch30-05-illegal-type',
    title: '实验 5 · 自测 1:非法 search_type,REST 层就拒',
    method: 'POST', path: '/tut-l30-docs/_search?search_type=some_search_type',
    body: {},
    predict: '这个胡写的参数会在哪一层被拒?文案是什么?',
    expect: '400 + No search type for [some_search_type]——Handler 在 prepareRequest 里校验,还没到 Lucene。这正是 RestSearchActionTests.testIllegalSearchType 钉的同一条约束(测试与实测文案一字不差):解析边界在 REST 层。'
  };

  window.ESEXPERIMENTS['ch30-06-window'] = {
    version: 1, id: 'ch30-06-window',
    title: '实验 6 · 自测 4:from=10000 撞窗口,文案里有 10010',
    method: 'POST', path: '/tut-l30-docs/_search?from=10000&size=10&filter_path=error.root_cause.reason',
    body: {},
    predict: 'from+size=10010 > max_result_window=10000,错误文案里会出现哪个数字?',
    expect: '400:Result window is too large, from + size must be less than or equal to: [10000] but was [10010].——10010 正是 SearchPhaseController.getTopDocsSize 算出的「每个 shard 要回多少条」;窗口在扇出前检查。yaml search/30_limits.yml 的 catch: 钉的就是这条文案。'
  };

  window.ESEXPERIMENTS['ch30-07-doc2'] = {
    version: 1, id: 'ch30-07-doc2',
    title: '实验 7 · 写 doc 2(purple lion),这次不 refresh',
    method: 'PUT', path: '/tut-l30-docs/_doc/2',
    body: { title: 'purple lion' },
    predict: '没有 refresh(且自动 refresh 已关),SEARCH 和 GET 分别能看见它吗?',
    expect: 'result: created。文档进了 index buffer + translog(第 14 课),但还没进「已打开供搜索的段」——下面两个实验把 SEARCH 与 GET 的分道扬镳当场演一遍。'
  };

  window.ESEXPERIMENTS['ch30-08-search-purple'] = {
    version: 1, id: 'ch30-08-search-purple',
    title: '实验 8 · 立刻 SEARCH purple:0 hits',
    method: 'POST', path: '/tut-l30-docs/_search?filter_path=hits.total',
    body: { query: { match: { title: 'purple' } } },
    predict: '几命中?为什么?',
    expect: '0——acquireSearcher 默认 SearcherScope.EXTERNAL:只看见上次 refresh 后的快照,doc 2 还在 buffer 里。SEARCH 不是放大的 GET;近实时的「近」就在这一个默认参数上。'
  };

  window.ESEXPERIMENTS['ch30-09-get-doc2'] = {
    version: 1, id: 'ch30-09-get-doc2',
    title: '实验 9 · 同一瞬间 GET doc 2:200,立刻可见',
    method: 'GET', path: '/tut-l30-docs/_doc/2?filter_path=found,_id,_source',
    body: null,
    predict: 'SEARCH 刚说看不见,GET 呢?',
    expect: 'found: true,带 _source——realtime GET 走 VersionMap → Translog(第 10 课),根本不看 EXTERNAL searcher。同一毫秒、同一份索引、两条请求两个世界:不要把它们并进同一张调用链,也不要去 InternalEngine.get 里找 SEARCH。'
  };

  window.ESEXPERIMENTS['ch30-10-refresh'] = {
    version: 1, id: 'ch30-10-refresh',
    title: '实验 10 · 显式 refresh:把 doc 2 纳入快照',
    method: 'POST', path: '/tut-l30-docs/_refresh?filter_path=_shard.successful,_shard.total',
    body: null,
    predict: 'refresh 会把整个 index buffer 开成新段——_shard 计数是几?',
    expect: 'successful=1, total=1(单分片)。refresh 建议所有 shard 各开一次段(第 14 课写入全路径的分叉点);下一次 SEARCH 的 EXTERNAL searcher 将看见这份新快照。'
  };

  window.ESEXPERIMENTS['ch30-11-search-purple2'] = {
    version: 1, id: 'ch30-11-search-purple2',
    title: '实验 11 · 再 SEARCH purple:1 hit,闭环',
    method: 'POST', path: '/tut-l30-docs/_search?filter_path=hits.total,hits.hits._id',
    body: { query: { match: { title: 'purple' } } },
    predict: '查询一字未改,这次几命中?',
    expect: '1 命中(_id=2)。同一条查询 refresh 前后 0⇄1:变的不是查询,是 EXTERNAL searcher 脚下的快照。至此第 10/14/16 课的近实时三角(写入/GET/SEARCH)在一条时间线上闭环。'
  };

  window.ESEXPERIMENTS['ch30-12-usage'] = {
    version: 1, id: 'ch30-12-usage',
    title: '实验 12 · 自测 2:两套名字——rest_actions 里叫 search_action',
    method: 'GET', path: '/_nodes/usage?filter_path=nodes.*.rest_actions.search_action',
    body: null,
    predict: '计数器下的 key 会是 indices:data/read/search 还是 search_action?它等于几次 _search?',
    expect: 'key 是 search_action(RestSearchAction.getName() 的 REST usage 名),计数 ≥ 本课实验 3/5/6/8/11 的 _search 次数。另一套名字 indices:data/read/search 是 TransportSearchAction.TYPE.name(),出现在 _tasks 里;分片相位再挂 [phase/query] / [phase/fetch/id] 后缀。三套名字不混,追丢率减半。'
  };

  window.ESEXPERIMENTS['ch30-13-cleanup'] = {
    version: 1, id: 'ch30-13-cleanup',
    title: '清理 · 删 tut-l30-docs,30 课收官',
    method: 'DELETE', path: '/tut-l30-docs',
    predict: '一句话收官?',
    expect: 'acknowledged: true。六篇接到一次请求上:认证 → REST 适配 → 快照选 shard → Query Then Fetch → EXTERNAL searcher → hits;阅读主链三步 REST → TransportAction → 测试;入口永远是一条 HTTP 路径,不是一个包名。下一个模块,从一条真实路径走进去。'
  };
})();
