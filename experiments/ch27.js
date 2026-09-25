/* experiments/ch27.js — 第 27 课:管道查询语言(ES|QL)实验 + 一条管道的执行动画 */
(function () {
  'use strict';

  /* ===== 动画:FROM | WHERE | STATS 怎么变成 200.0 ===== */
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
  function arrow(id, x1, y1, x2, y2) {
    return '<line x1="' + x1 + '" y1="' + y1 + '" x2="' + x2 + '" y2="' + y2 + '" class="fig-arrow" marker-end="url(#' + id + ')"/>';
  }
  function bottom(title, sub) {
    var s = rect(15, 240, 730, 48, 'fig-box-hot', 'fp-pop');
    s += txt(380, 261, title, 'fig-name');
    s += txt(380, 281, sub, 'fig-sub');
    return s;
  }

  /* 步骤 1:你写的一行就是执行模型 */
  function step1() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('q1');
    s += rect(15, 15, 730, 56, 'fig-box-hot');
    s += txt(380, 38, 'FROM tut-l27-pages | WHERE views > 100 | STATS avg(views)', 'fig-name');
    s += txt(380, 60, '竖杠 = Unix pipe:左边产出的表,是右边的输入', 'fig-sub');
    s += rect(15, 88, 355, 76, 'fig-box');
    s += txt(192, 112, '不是阶段墙', 'fig-name');
    s += txt(192, 136, '没有 Parser→Analyzer→Optimizer', 'fig-sub');
    s += txt(192, 156, '→Planner→Executor 五段先背', 'fig-sub');
    s += rect(390, 88, 355, 76, 'fig-box');
    s += txt(567, 112, '你写的一行', 'fig-name');
    s += txt(567, 136, '已经是执行模型:表怎么一步步', 'fig-sub');
    s += txt(567, 156, '变瘦、变少列', 'fig-sub');
    s += rect(15, 180, 730, 44, 'fig-box');
    s += txt(380, 200, '工作单元:FROM 给出行,WHERE 丢行,STATS 收成一行', 'fig-sub');
    s += txt(380, 217, '客户端拿到 columns + values 一张表——没有 hits.hits', 'fig-sub');
    s += bottom('忘掉「先造 Lucene Query 再 Query Then Fetch」', '那是 /_search(第 16 课);这是另一条 REST 入口');
    return s + '</svg>';
  }

  /* 步骤 2:REST 只有一条路由 */
  function step2() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('q2');
    s += rect(15, 15, 355, 96, 'fig-box');
    s += txt(192, 39, 'POST /_query', 'fig-name');
    s += txt(192, 63, 'RestEsqlQueryAction.routes() 唯一', 'fig-sub');
    s += txt(192, 83, 'body 文本字段叫 "query"', 'fig-sub');
    s += txt(192, 103, '异步:POST /_query/async 另一条', 'fig-sub');
    s += rect(390, 15, 355, 96, 'fig-box');
    s += txt(567, 39, '动作名却带 esql', 'fig-name');
    s += txt(567, 63, 'indices:data/read/esql', 'fig-sub');
    s += txt(567, 83, 'URL 里没有 esql——别拿动作名猜路由', 'fig-sub');
    s += txt(567, 103, '插件:EsqlPlugin(getRestHandlers)', 'fig-sub');
    s += rect(15, 128, 730, 92, 'fig-box');
    s += txt(380, 152, '实测对照:POST /_esql → 405', 'fig-key', true);
    s += txt(380, 176, 'Incorrect HTTP method ... allowed: [GET, PUT, DELETE, HEAD]', 'fig-sub');
    s += txt(380, 196, '/_esql 被裸索引路由 /{index} 捕获(POST 不在其中)', 'fig-sub');
    s += txt(380, 216, '镜像:GET /_query → 405 allowed: [POST]', 'fig-sub');
    s += bottom('REST 只适配不干活:造 EsqlQueryRequest 交给动作层(第 7 课)', '真正解析执行的是插件 createComponents 造的 PlanExecutor + ExchangeService');
    return s + '</svg>';
  }

  /* 步骤 3:竖杠的解析语义 */
  function step3() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('q3');
    s += rect(15, 15, 730, 56, 'fig-box');
    s += txt(380, 38, 'visitCompositeQuery:先递归解析左边,右边是 PlanFactory', 'fig-name');
    s += txt(380, 60, 'makePlan.apply(input) —— 左边的计划喂给右边,层层包裹', 'fig-sub');
    s += rect(15, 88, 222, 92, 'fig-box');
    s += txt(126, 112, 'FROM tut', 'fig-name');
    s += txt(126, 136, 'UnresolvedRelation', 'fig-sub');
    s += txt(126, 156, '(分析后 EsRelation,', 'fig-sub');
    s += txt(126, 176, '挂着字段表)', 'fig-sub');
    s += rect(269, 88, 222, 92, 'fig-box');
    s += txt(380, 112, 'WHERE ...', 'fig-name');
    s += txt(380, 136, 'Filter(condition)', 'fig-sub');
    s += txt(380, 156, '没有叫 Where 的节点', 'fig-sub');
    s += txt(380, 176, 'SQL 的 WHERE 就是它', 'fig-sub');
    s += rect(523, 88, 222, 92, 'fig-box');
    s += txt(634, 112, 'STATS ...', 'fig-name');
    s += txt(634, 136, 'Aggregate', 'fig-sub');
    s += txt(634, 156, '没有 BY → 空分组', 'fig-sub');
    s += txt(634, 176, '没有叫 Stats 的节点', 'fig-sub');
    s += rect(15, 196, 730, 30, 'fig-box');
    s += txt(380, 215, '树形 = Aggregate(Filter(EsRelation)):嵌套即管道,顺序即语义', 'fig-key');
    s += bottom('三个命令三种节点,ANTLR 只是机械的「字符串 → 树」', 'views 必须在分析期能认成数值字段,否则 avg(views) 过不了 verifier');
    return s + '</svg>';
  }

  /* 步骤 4:优化——推下去,但不改语义 */
  function step4() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('q4');
    s += rect(15, 15, 355, 96, 'fig-box');
    s += txt(192, 39, '过滤下推', 'fig-name');
    s += txt(192, 63, 'PushDownAndCombineFilters', 'fig-sub');
    s += txt(192, 83, '把 views>100 推到数据源', 'fig-sub');
    s += txt(192, 103, '变成 Lucene range query', 'fig-sub');
    s += rect(390, 15, 355, 96, 'fig-box');
    s += txt(567, 39, 'avg 的代数改写', 'fig-name');
    s += txt(567, 63, 'Avg.surrogate → Sum / Count', 'fig-sub');
    s += txt(567, 83, '没有叫 AvgOperator 的类', 'fig-sub');
    s += txt(567, 103, '列名仍是你写的 avg(views)', 'fig-sub');
    s += rect(15, 128, 730, 92, 'fig-box');
    s += txt(380, 152, '不变量:源码管道仍是 FROM → WHERE → STATS', 'fig-key');
    s += txt(380, 176, '优化器可以少算(被丢的行不进 Page),不能改「先过滤再平均」', 'fig-sub');
    s += txt(380, 196, '下推之后 profile 里可以没有 FilterOperator——不是丢了,是换地方死了', 'fig-sub');
    s += txt(380, 216, '其余规则(常量折叠/Limit 变 TopN...)存在,不必背名单', 'fig-sub');
    s += bottom('「50+ 规则」不是心智模型:这条查询只关心推下去 + 改写', 'verifier 兜底:优化后的树必须仍能通过校验');
    return s + '</svg>';
  }

  /* 步骤 5:数据节点 Driver(实测算子链) */
  function step5() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('q5');
    s += rect(15, 15, 730, 30, 'fig-box');
    s += txt(380, 34, '数据节点 Driver(单线程传送带,Page 按列流动)', 'fig-key');
    s += rect(15, 54, 355, 50, 'fig-box');
    s += txt(192, 74, 'LuceneSourceOperator', 'fig-name');
    s += txt(192, 94, 'query 已是 range,不是 match_all', 'fig-sub');
    s += arrow('q5', 192, 104, 192, 114);
    s += rect(15, 114, 355, 44, 'fig-box');
    s += txt(192, 132, 'ValuesSourceReaderOperator[views]', 'fig-name');
    s += txt(192, 150, '抽列:Page 里只剩 views 这一列', 'fig-sub');
    s += arrow('q5', 192, 158, 192, 168);
    s += rect(15, 168, 355, 44, 'fig-box');
    s += txt(192, 186, 'AggregationOperator[Sum,Count]', 'fig-name');
    s += txt(192, 204, 'mode=INITIAL:局部聚合 600 / 3', 'fig-sub');
    s += rect(390, 54, 355, 158, 'fig-box-hot');
    s += txt(567, 78, '列式 Page,不是 _source', 'fig-name');
    s += txt(567, 102, 'views 同列挨在一个 Block 里', 'fig-sub');
    s += txt(567, 122, '过滤后:150, 200, 250', 'fig-sub');
    s += txt(567, 146, '100 那行:>不含等于,没进来', 'fig-sub', true);
    s += txt(567, 170, 'TARGET_PAGE_SIZE ≈ 256KB 切批', 'fig-sub');
    s += txt(567, 194, '5 行看不见切批,生产日志量才看得出', 'fig-sub');
    s += bottom('ExchangeSinkOperator:局部聚合的中间态送回协调节点', '一个 Driver 一条链;分布式发生在多个 Driver 上');
    return s + '</svg>';
  }

  /* 步骤 6:协调节点 FINAL + 除法 */
  function step6() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('q6');
    s += rect(15, 15, 730, 30, 'fig-box');
    s += txt(380, 34, '协调节点 Driver(实测 profile:ExchangeSource 起,OutputOperator 终)', 'fig-key');
    s += rect(15, 54, 355, 50, 'fig-box');
    s += txt(192, 74, 'ExchangeSourceOperator', 'fig-name');
    s += txt(192, 94, '接住数据节点送回的 Page', 'fig-sub');
    s += arrow('q6', 192, 104, 192, 114);
    s += rect(15, 114, 355, 50, 'fig-box');
    s += txt(192, 134, 'AggregationOperator mode=FINAL', 'fig-name');
    s += txt(192, 154, '合并局部 Sum/Count → 全局 600 / 3', 'fig-sub');
    s += arrow('q6', 192, 164, 192, 174);
    s += rect(15, 174, 355, 44, 'fig-box-hot', 'fp-pop');
    s += txt(192, 192, 'Eval: DivDoublesEvaluator', 'fig-name');
    s += txt(192, 210, 'sum ÷ count = 600 ÷ 3 = 200.0', 'fig-sub');
    s += rect(390, 54, 355, 164, 'fig-box');
    s += txt(567, 78, '为什么必须阻塞?', 'fig-name');
    s += txt(567, 102, 'AggregationOperator:所有输入到齐', 'fig-sub');
    s += txt(567, 122, '才吐那一行(javadoc)', 'fig-sub');
    s += txt(567, 146, '均值的分母是过滤后的全部行数', 'fig-sub');
    s += txt(567, 166, '不是 Top-10 hits 的平均(思考题 2)', 'fig-sub', true);
    s += txt(567, 190, '可以先局部后合并——仍是全集', 'fig-sub');
    s += txt(567, 210, '与第 19 课聚合不进 Fetch 同因', 'fig-sub');
    s += bottom('中间还有 Project / Limit[999/1000] / Output 等小算子', 'Limit 999/1000 是默认结果窗口;列名 avg(views) 在 Output 上');
    return s + '</svg>';
  }

  /* 步骤 7:响应与两条路的分工 */
  function step7() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('q7');
    s += rect(15, 15, 355, 150, 'fig-box-hot');
    s += txt(192, 39, 'ES|QL 的响应', 'fig-name');
    s += txt(192, 63, 'columns: [avg(views)/double]', 'fig-sub');
    s += txt(192, 83, 'values: [[200.0]]', 'fig-sub');
    s += txt(192, 107, '一行一列的一张表', 'fig-sub');
    s += txt(192, 127, '没有 hits、没有 _score', 'fig-sub');
    s += txt(192, 147, 'is_partial:false(全集到齐)', 'fig-sub');
    s += rect(390, 15, 355, 150, 'fig-box');
    s += txt(567, 39, 'Query DSL 的响应', 'fig-name');
    s += txt(567, 63, 'hits.total=3, hits.hits=[](size:0)', 'fig-sub');
    s += txt(567, 83, 'aggregations.avg_views.value=200.0', 'fig-sub');
    s += txt(567, 107, '同一数学,两棵 JSON 树的形状', 'fig-sub');
    s += txt(567, 127, '漏 size:0 → 多搬 3 篇 _source', 'fig-sub');
    s += txt(567, 147, 'ES|QL 根本不产 hits', 'fig-sub');
    s += rect(15, 180, 730, 44, 'fig-box');
    s += txt(380, 200, '分工:全文 match / BM25 / highlight / _explain 仍走 _search(第 16-18 课)', 'fig-sub');
    s += txt(380, 217, '扫描、过滤、聚合一张表——管道顺序即语义,ES|QL 的主场', 'fig-sub');
    s += bottom('你写的一行,已经是执行模型', 'FROM 给行 → WHERE 丢行 → STATS 收行;竖杠把三步钉成一条链');
    return s + '</svg>';
  }

  window.ESFLOWS = window.ESFLOWS || {};
  window.ESFLOWS['ch27-esql-pipeline'] = {
    version: 1,
    id: 'ch27-esql-pipeline',
    title: '一条管道从文本到 200.0',
    speed: 2400,
    steps: [
      { svg: step1(), note: '你写的一行就是执行模型:竖杠 = Unix pipe,左边产出的表是右边输入。工作单元是表怎么变瘦变少列——不是「先造 Lucene Query 再 Query Then Fetch」那套。' },
      { svg: step2(), note: 'REST 只有 POST /_query(RestEsqlQueryAction.routes);动作名 indices:data/read/esql 带 esql,URL 没有。实测 POST /_esql 是 405:被裸索引路由 /{index} 捕获,POST 不在 allowed 里——不是 404。' },
      { svg: step3(), note: 'visitCompositeQuery:左边计划喂给右边 PlanFactory。FROM→UnresolvedRelation(分析后 EsRelation)、WHERE→Filter、STATS→Aggregate——没有叫 Where/Stats 的节点;嵌套即管道。' },
      { svg: step4(), note: '优化器把 views>100 推进 Lucene(源算子的 query 不再是 match_all),avg 改写成 Sum/Count。不变量:源码管道仍是 FROM→WHERE→STATS,优化器只能少算,不能改「先过滤再平均」。' },
      { svg: step5(), note: '数据节点 Driver:LuceneSourceOperator(WHERE 已下推)→ ValuesSourceReader 抽 views 列 → AggregationOperator[Sum,Count] mode=INITIAL(局部 600/3)→ ExchangeSink 送回。中间态是列式 Page,150/200/250;100 那行 > 不含等于。' },
      { svg: step6(), note: '协调节点:ExchangeSource → AggregationOperator mode=FINAL 合并成全局 600/3 → Eval 的 DivDoublesEvaluator 除出 200.0。聚合必须阻塞到输入结束——均值分母是全集行数,不是 Top-N hits。' },
      { svg: step7(), note: '响应是 columns+values 一张表,没有 hits 没有 _score;同一数学的 Query DSL 回 hits+aggregations 两棵树。全文排名仍走 _search;扫描过滤聚合一张表,是 ES|QL 的主场。' }
    ]
  };

  /* ===== 实验 ===== */
  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};

  window.ESEXPERIMENTS['ch27-01-setup'] = {
    version: 1, id: 'ch27-01-setup',
    title: '实验 1 · 建 tut-l27-pages(1 分片,views 为 long)',
    method: 'PUT', path: '/tut-l27-pages',
    body: { settings: { number_of_shards: 1, number_of_replicas: 0 }, mappings: { properties: { title: { type: 'keyword' }, views: { type: 'long' } } } },
    predict: 'ES|QL 的 FROM 读的是实时还是已 refresh 的数据?',
    expect: 'acknowledged: true。与第 16 课同一条不变量:FROM 只看见已 refresh 的 EXTERNAL searcher——所以后续 bulk 都带 refresh=true。views 必须是数值类型,否则 avg(views) 在分析期过不了 verifier。'
  };

  window.ESEXPERIMENTS['ch27-02-bulk'] = {
    version: 1, id: 'ch27-02-bulk',
    title: '实验 2 · 灌 5 行:50/100/150/200/250',
    method: 'POST', path: '/tut-l27-pages/_bulk?refresh=true',
    body: '{"index":{"_id":"1"}}\n{"title":"a","views":50}\n{"index":{"_id":"2"}}\n{"title":"b","views":100}\n{"index":{"_id":"3"}}\n{"title":"c","views":150}\n{"index":{"_id":"4"}}\n{"title":"d","views":200}\n{"index":{"_id":"5"}}\n{"title":"e","views":250}\n',
    predict: 'views=100 这一行是故意放的:WHERE views > 100 会留下它吗?',
    expect: 'errors: false,5 items。不会——> 不含等于,100 被丢掉;留下 150/200/250,均值 200。五行全平均是 150(实验 7 对照)。'
  };

  window.ESEXPERIMENTS['ch27-03-main'] = {
    version: 1, id: 'ch27-03-main',
    title: '实验 3 · 主查询:POST /_query 跑那条管道',
    method: 'POST', path: '/_query?filter_path=columns,values',
    body: { query: 'FROM tut-l27-pages | WHERE views > 100 | STATS avg(views)' },
    predict: '先猜:列名是 avg(views) 还是 avg_views?values 几行几列?均值 200 还是 150?响应里有 hits 吗?',
    expect: 'columns=[{name:"avg(views)",type:"double"}](列名跟源码文本走),values=[[200.0]] 一行一列,没有 hits。猜 150 的是把 > 当 >= 或忘了 WHERE;猜响应像 _search 的,是把两条 REST 入口当成了同一个引擎。'
  };

  window.ESEXPERIMENTS['ch27-04-wrong-path'] = {
    version: 1, id: 'ch27-04-wrong-path',
    title: '实验 4 · 破坏:POST /_esql 是 405,不是 404',
    method: 'POST', path: '/_esql',
    body: { query: 'FROM tut-l27-pages | LIMIT 1' },
    predict: '不存在的路由应该回什么?400 / 404 / 405?',
    expect: '405:Incorrect HTTP method for uri [/_esql] and method [POST], allowed: [GET, PUT, DELETE, HEAD]。/_esql 不是「无 handler」——它撞上了裸索引路由 /{index}(POST 不在 allowed)。镜像对照:GET /_query → 405 allowed: [POST]。第 7 课的错误码阶梯在这里活用。'
  };

  window.ESEXPERIMENTS['ch27-05-case'] = {
    version: 1, id: 'ch27-05-case',
    title: '实验 5 · STATS AVG(views):大写只改列名',
    method: 'POST', path: '/_query?filter_path=columns,values',
    body: { query: 'FROM tut-l27-pages | WHERE views > 100 | STATS AVG(views)' },
    predict: '函数名大写,列名和均值会变吗?',
    expect: '列名变成 AVG(views)(跟源码文本),均值仍 200.0——大小写不改数学,改的是列名字符串。ES|QL 关键字不区分大小写,标识符按你写的呈现。'
  };

  window.ESEXPERIMENTS['ch27-06-gte'] = {
    version: 1, id: 'ch27-06-gte',
    title: '实验 6 · WHERE views >= 100:把 100 算进去',
    method: 'POST', path: '/_query?filter_path=columns,values',
    body: { query: 'FROM tut-l27-pages | WHERE views >= 100 | STATS avg(views)' },
    predict: '均值是多少?和实验 3 差在哪一行?',
    expect: '(100+150+200+250)/4 = 175.0。差在 views=100 那一行:>= 放它进来,> 丢掉它。边界条件的对照就是教程故意放 100 的原因。'
  };

  window.ESEXPERIMENTS['ch27-07-nowhere'] = {
    version: 1, id: 'ch27-07-nowhere',
    title: '实验 7 · 去掉 WHERE:五行之平均',
    method: 'POST', path: '/_query?filter_path=columns,values',
    body: { query: 'FROM tut-l27-pages | STATS avg(views)' },
    predict: '没有 WHERE,均值是多少?管道还成立吗?',
    expect: '(50+100+150+200+250)/5 = 150.0。仍成立:Aggregate 直接包住 EsRelation,少一层 Filter——管道可长可短,顺序即语义。'
  };

  window.ESEXPERIMENTS['ch27-08-profile'] = {
    version: 1, id: 'ch27-08-profile',
    title: '实验 8 · profile:亲眼看见算子链与下推',
    method: 'POST', path: '/_query?filter_path=profile.drivers.operators.operator,values',
    body: { query: 'FROM tut-l27-pages | WHERE views > 100 | STATS avg(views)', profile: true },
    predict: '链上有 FilterOperator 吗?聚合器叫 Avg 还是 Sum/Count?除法发生在哪一端?',
    expect: '数据节点:LuceneSourceOperator → ValuesSourceReaderOperator[views] → AggregationOperator[SumLong/Count,mode=INITIAL] → ExchangeSink——没有 FilterOperator(WHERE 已推入 Lucene 的 query)。协调端:ExchangeSource → Aggregation[FINAL] → Limit[999/1000] → Eval DivDoublesEvaluator(sum÷count) → Output。没有叫 AvgOperator 的类。'
  };

  window.ESEXPERIMENTS['ch27-09-dsl-avg'] = {
    version: 1, id: 'ch27-09-dsl-avg',
    title: '实验 9 · 同等 Query DSL:size:0 + range + aggs',
    method: 'POST',
    path: '/tut-l27-pages/_search?filter_path=hits.total,hits.hits,aggregations.avg_views.value',
    body: { size: 0, query: { range: { views: { gt: 100 } } }, aggs: { avg_views: { avg: { field: 'views' } } } },
    predict: 'avg_views.value 与实验 3 一致吗?hits.hits 几条?',
    expect: '200.0,完全同一数学;size:0 让 hits.hits 为空。要同时记住三件分开的事:不要 hits(过滤在 query、平均在 aggs)——ES|QL 把它们收成三个命令。'
  };

  window.ESEXPERIMENTS['ch27-10-dsl-hits'] = {
    version: 1, id: 'ch27-10-dsl-hits',
    title: '实验 10 · 漏写 size:0:hits 把 _source 搬回来',
    method: 'POST',
    path: '/tut-l27-pages/_search?filter_path=hits.hits._id,aggregations.avg_views.value',
    body: { query: { range: { views: { gt: 100 } } }, aggs: { avg_views: { avg: { field: 'views' } } } },
    predict: '默认 size=10,会带回几篇文档?均值变吗?',
    expect: '带回 _id 3/4/5 三篇 _source,均值仍 200——「哪些文档当 hits」和「聚合看哪些文档」是两棵树,聚合看的是过滤后的全集,不是 hits 窗口。ES|QL 的 STATS 干脆不产 hits。'
  };

  window.ESEXPERIMENTS['ch27-11-dsl-gte'] = {
    version: 1, id: 'ch27-11-dsl-gte',
    title: '实验 11 · DSL 的 gte 对照:175',
    method: 'POST',
    path: '/tut-l27-pages/_search?filter_path=aggregations.avg_views.value',
    body: { size: 0, query: { range: { views: { gte: 100 } } }, aggs: { avg_views: { avg: { field: 'views' } } } },
    predict: '与实验 6 的 175.0 对得上吗?',
    expect: '175.0,对上。range.gt ⇔ WHERE >、range.gte ⇔ WHERE >=、aggs.avg ⇔ STATS avg——语义一一对应,形状完全不同(嵌套 JSON 树 vs 管道文本)。'
  };

  window.ESEXPERIMENTS['ch27-12-sort-keep'] = {
    version: 1, id: 'ch27-12-sort-keep',
    title: '实验 12 · 管道还能接:SORT · KEEP · LIMIT',
    method: 'POST', path: '/_query?filter_path=columns,values',
    body: { query: 'FROM tut-l27-pages | SORT views DESC | KEEP title, views | LIMIT 2' },
    predict: '结果几行几列?还是 hits 形状吗?',
    expect: '两行两列:[["e",250],["d",200]]。SORT 排行、KEEP 挑列、LIMIT 截尾——每个命令继续把表变瘦变少列。列名跟 KEEP 的顺序走(title 在前)。'
  };

  window.ESEXPERIMENTS['ch27-13-async-route'] = {
    version: 1, id: 'ch27-13-async-route',
    title: '实验 13 · 异步路由的存在性:GET /_query/async',
    method: 'GET', path: '/_query/async',
    body: null,
    predict: '这条 GET 会 404(路由不存在)还是 405(路由存在,方法不对)?',
    expect: '405 allowed: [POST]——/_query/async 路由存在但只收 POST(RestEsqlAsyncQueryAction)。与实验 4 的 allowed [GET,PUT,DELETE,HEAD] 对读:allowed 列表就是「这条路谁认领」的指纹。'
  };

  window.ESEXPERIMENTS['ch27-14-cleanup'] = {
    version: 1, id: 'ch27-14-cleanup',
    title: '清理 · 删 tut-l27-pages',
    method: 'DELETE', path: '/tut-l27-pages',
    predict: '一句话总结本课?',
    expect: 'acknowledged: true。ES|QL 的心智模型是管道:你写的一行就是执行模型;POST /_query 是唯一同步入口;WHERE→Filter(可下推)、STATS→Aggregate(Sum/Count 改写)、FROM→LuceneSourceOperator;Driver 单线程传列式 Page;响应是 columns+values,不是 hits。'
  };
})();
