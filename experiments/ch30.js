/* ch30: fixed ES 9.4.0, reproducible search evidence and seven-step review. */
(function () {
  'use strict';
  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};
  function exp(id, title, method, path, body, predict, expect) {
    window.ESEXPERIMENTS[id] = { version: 1, id: id, title: title, method: method,
      path: path, body: body, predict: predict, expect: expect,
      endpoint: 'http://localhost:9200', auth: null };
  }
  exp('ch30-01-setup', 'A1 · 创建受控索引', 'PUT', '/tut-l30-docs', {
    settings: { number_of_shards: 1, number_of_replicas: 0, refresh_interval: '-1', max_result_window: 10000 },
    mappings: { dynamic: 'strict', properties: { title: { type: 'text', analyzer: 'standard' } } }
  }, '为何同时固定 mapping、窗口与 refresh？',
  '200，acknowledged=true。一主片零副本、strict title:text/standard；关闭定时 refresh。重复创建为400 resource_already_exists_exception；先用E1点名清理，再从A1重做。实验期间不要在其他窗口 refresh 或改本索引。');
  exp('ch30-15-health', 'A2 · 等待本章主分片可用', 'GET', '/_cluster/health/tut-l30-docs?wait_for_status=green&timeout=10s', null,
    '本索引 green 能代表整个集群吗？', '200，timed_out=false、status=green、active_primary_shards=1。仅判断 tut-l30-docs；其他索引可使整个集群仍 yellow。若超时，先解决分配，再继续。');
  exp('ch30-02-doc1', 'A3 · 写 doc 1 并显式刷新', 'PUT', '/tut-l30-docs/_doc/1?refresh=true', { title: 'the quick brown fox' },
    '写入响应完成后，下一次普通搜索是否可见？', '首次201 result=created、forced_refresh=true；重复写入200 updated。refresh=true 是本次写请求参数，未改 refresh_interval=-1；显式刷新后新搜索可见。');
  exp('ch30-14-usage-before', 'A4 · 记录 search_action 基线 N', 'GET', '/_nodes/usage?filter_path=nodes.*.name,nodes.*.rest_actions.search_action', null,
    '未用过搜索的节点会有零值 key 吗？', '200。按节点记录 N；未出现 search_action 时记0。计数是节点累计 REST usage，含其他流量；它不是动作注册表。单节点、无并发搜索时才能精确比较本课增量。');
  exp('ch30-03-search-brown', 'A5 · match brown 得到 doc 1', 'POST', '/tut-l30-docs/_search?filter_path=hits.total,hits.hits._id,hits.hits._score', { query: { match: { title: 'brown' } } },
    '这个响应能证明发生两次网络往返吗？', '200，hits.total.value=1、_id=1、正 _score。单个 brown token 可直接成为词项查询，不能推断一定生成 SHOULD BooleanQuery。本例默认 BM25 得分约0.13076457；响应不证明多节点或独立 Fetch 往返。');
  exp('ch30-04-no-route', 'B1 · 无 handler 的路径', 'GET', '/tut-l30-docs/_not_a_real_endpoint', null,
    '状态码和错误字段各是什么形状？', '400，顶层 error 是含 no handler found for uri 的字符串。此具体路径/方法无 handler；不要泛化所有未知 URL，其他路径可能撞上索引路由或得到405。');
  exp('ch30-05-illegal-type', 'B2 · 非法 search_type 在解析时失败', 'POST', '/tut-l30-docs/_search?search_type=some_search_type', {},
    '这次400会增加 search_action usage 吗？', '400，reason含 No search type for [some_search_type]。prepareRequest 抛异常，尚未到 usageCount.increment；不增加 search_action。与 RestSearchActionTests.testIllegalSearchType 的断言对照。');
  exp('ch30-06-window', 'B3 · 10010 超过显式窗口10000', 'POST', '/tut-l30-docs/_search?from=10000&size=10&filter_path=error.type,error.root_cause,error.failed_shards,status', {},
    '同为400，是否也发生在 REST 解析层？', '400，error.type=search_phase_execution_exception，failed_shards 指向 tut-l30-docs；reason含 [10000] but was [10010]。分片 DefaultSearchContext.preProcess 检查，主Query前失败；已通过REST准备，usage增加。rank等搜索不可无条件套用普通from+size公式。');
  exp('ch30-07-doc2', 'C1 · 写 doc 2，不刷新', 'PUT', '/tut-l30-docs/_doc/2', { title: 'purple lion' },
    '下一次搜索是否能看见？', '首次201 created，重复200 updated。固定mapping与关闭定时refresh，避免动态mapping或定时刷新干扰。本实验还要求无外部刷新；重做必须先清理，已刷新过的doc2不会自动退回不可见。');
  exp('ch30-08-search-purple', 'C2 · 普通搜索 purple：0', 'POST', '/tut-l30-docs/_search?filter_path=hits.total', { query: { match: { title: 'purple' } } },
    '这能证明文档没写成功吗？', '200，hits.total.value=0。新搜索取得的外部搜索读者尚未包含doc2；不意味着写入失败，也不意味着所有写入字节只在buffer内。');
  exp('ch30-09-get-doc2', 'C3 · realtime GET：found=true', 'GET', '/tut-l30-docs/_doc/2?filter_path=found,_id,_source', null,
    '相同索引的GET会与搜索一致吗？', '200，found=true、_id=2、_source.title=purple lion。默认realtime GET可读取尚未对普通搜索可见的写入；本例可走实时路径，但响应不能证明必从translog读取。');
  exp('ch30-17-get-nrt', 'C4 · 非实时GET：found=false', 'GET', '/tut-l30-docs/_doc/2?realtime=false&filter_path=found,_id', null,
    '只改这个请求的realtime，结果会怎样？', '404，found=false、_id=2。本次GET使用搜索可见视图；未改索引配置。refresh_interval=-1且无外部refresh时结果受控。下一张显式refresh后再搜索。');
  exp('ch30-10-refresh', 'C5 · 显式刷新本索引', 'POST', '/tut-l30-docs/_refresh?filter_path=_shards', null,
    '响应键是_shard还是_shards？', '200，_shards.total=1、successful=1、failed=0。是复数_shards；成功刷新后下一次新搜索可见doc2。不保证每次refresh都产生新段，也不是flush/持久化提交证明。');
  exp('ch30-11-search-purple2', 'C6 · 同一查询：1', 'POST', '/tut-l30-docs/_search?filter_path=hits.total,hits.hits._id', { query: { match: { title: 'purple' } } },
    '查询不变，哪个前提改变了？', '200，hits.total.value=1、_id=2。改变的是新搜索取得的读者视图；旧PIT等保留读者不会因此切换。本课未打开PIT。');
  exp('ch30-18-count', 'D1 · 限定本索引的count', 'GET', '/tut-l30-docs/_count', null,
    '调用内部搜索的REST入口名是否也算search_action？', '200，count=2。REST入口是count，不增加search_action；内部复用搜索机制与HTTP Handler usage是不同层。');
  exp('ch30-16-default-search', 'D2 · 空body的普通搜索', 'POST', '/tut-l30-docs/_search', {},
    '只有两篇文档能验证默认size=10吗？', '200，hits.total.value=2、两条hits。省略query按match_all；默认from=0、size=10由源码确认，两条hits不足以单独证明size上限。本卡增加search_action一次。');
  exp('ch30-20-tasks', 'D3 · 采样搜索Task', 'GET', '/_tasks?actions=indices%3Adata%2Fread%2Fsearch%2A&detailed=true', null,
    '空任务列表能证明搜索Action没注册吗？', '200；先前搜索已完成且无其他搜索时通常nodes={}。actions按通配匹配，星号包含分片相位；Task是运行中采样，空列表不是未注册或从未执行的证据。');
  exp('ch30-12-usage', 'D4 · 对照usage：本课增量5', 'GET', '/_nodes/usage?filter_path=nodes.*.name,nodes.*.rest_actions.search_action', null,
    'B2解析400、B3窗口400哪个被计入？', '200。单节点无其他搜索、每卡一次时为N+5：A5/B3/C2/C6/D2；B2 prepare失败不计，B1无handler不计，count也不计。计数点在REST准备与后置检查后、consumer执行前；无法由累计值推断成功数。');
  exp('ch30-13-cleanup', 'E1 · 点名删除本章索引', 'DELETE', '/tut-l30-docs', null,
    '删除会清零search_action吗？', '200 acknowledged=true。只删tut-l30-docs；不重置节点usage。清理后从A1按顺序重做，并重新记录基线N。');
  exp('ch30-19-cleanup-again', 'E2 · 重复清理的预期404', 'DELETE', '/tut-l30-docs', null,
    '这是清理失败，还是资源已不存在？', '404 index_not_found_exception，说明本章索引已经不存在。不使用通配删除，不掩盖这个预期错误；下一轮从A1重建。');

  function esc(s) { return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
  function text(x, y, s, cls) { return '<text x="' + x + '" y="' + y + '" text-anchor="middle" class="' + cls + '">' + esc(s) + '</text>'; }
  function box(x, title, lines, hot) {
    var s = '<rect x="' + x + '" y="90" width="350" height="134" rx="10" class="' + (hot ? 'fig-box-hot' : 'fig-box') + '"/>';
    s += text(x + 175, 115, title, 'fig-name');
    lines.forEach(function (line, i) { s += text(x + 175, 140 + i * 23, line, 'fig-sub'); });
    return s;
  }
  var frames = [
    ['从受控请求开始', 'A1–A5：明确数据与环境', ['ES 9.4.0 / Lucene 10.4.0', '一主片零副本；strict mapping', '定时refresh关闭；doc1显式刷新'], '先写可验证的笔记', ['路径 /tut-l30-docs/_search', '本例是单节点、单分片', '不能据此证明多节点网络两跳'], '证据先限定前提，再解释机制。'],
    ['REST 接头：路径、TYPE 与三套名字', 'HTTP 适配', ['routes() 确认路径与方法', 'prepareRequest 构造内部请求', 'execute(TransportSearchAction.TYPE)'], '三套名字', ['REST usage：search_action', 'Action：indices:data/read/search', '相位：query / fetch 等后缀'], '安全开启时：HTTP认证与后续Action授权是不同边界。'],
    ['协调入口：一份状态快照', '选本次搜索目标', ['clusterService.state()', '用取得的状态解析索引与分片', '快照不代表所有节点同时最新'], '单分片与多分片', ['搜索通常选每个目标分片一份副本', '本地执行不一定走网络', '普通单分片可在Query内完成Fetch'], '图1展示多分片职责；本课API只验证单分片响应。'],
    ['同为400，发生位置不同', 'B2：解析失败', ['非法search_type', 'prepareRequest抛异常', '未到usage计数点'], 'B3：分片预处理失败', ['from+size=10010 > 10000', 'DefaultSearchContext.preProcess', '已通过REST准备，会增加usage'], '窗口检查在分片主Query前；不能写成协调扇出前。'],
    ['Query 与 Fetch：保留目标，再取字段', '普通分页 Query', ['读取外部搜索视图', '分片候选受from+size等条件约束', '返回条数可少于窗口'], '协调归并与 Fetch', ['普通多分片归并候选', '按持有者分组目标docId', 'Fetch可取_source及其他字段'], 'void + listener表示结果协议，不单独保证换线程或非阻塞。'],
    ['C1–C6：把可见性差异变成证据', '显式refresh前', ['SEARCH purple：0', '默认realtime GET：found=true', 'realtime=false GET：404'], '显式refresh后', ['_shards.successful=1', '新SEARCH purple：1', '查询不变，新读者视图改变'], 'GET响应不证明必从translog读；refresh不保证每次产生新段。'],
    ['方法回放：源码、测试、API 各有用途', '查到约束', ['REST解析：RestSearchActionTests', 'HTTP窗口：search/30_limits.yml', '归并：SearchPhaseControllerTests'], '记录与重做', ['对照状态、error.type、失败分片', 'usage基线N → N+5', '点名清理；重建并重记N'], '看见差异，回到实际检查点；存在测试不等于已运行测试。']
  ];
  window.ESFLOWS = window.ESFLOWS || {};
  window.ESFLOWS['ch30-finale'] = { version: 1, id: 'ch30-finale', title: '一次搜索的职责与证据 · 七步回放', speed: 2400,
    steps: frames.map(function (f, i) {
      var id = 'ch30-finale-arrow-' + (i + 1);
      var svg = '<svg viewBox="0 0 760 310" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="' + esc(f[0]) + '">';
      svg += '<defs><marker id="' + id + '" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10z" class="fig-arrowhead"/></marker></defs>';
      svg += '<rect x="20" y="14" width="720" height="56" rx="10" class="fig-box-hot"/>' + text(380, 47, f[0], 'fig-name');
      svg += box(20, f[1], f[2], true) + box(390, f[3], f[4], false);
      svg += '<rect x="20" y="244" width="720" height="48" rx="10" class="fig-box"/>' + text(380, 273, f[5], 'fig-sub');
      return { svg: svg + '</svg>', note: f[5] + ' ' + f[2].join('；') + '。' };
    }) };
})();
