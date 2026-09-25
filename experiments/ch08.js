/* experiments/ch08.js — 第 8 课:实验 + 线程池拒绝链路动画(注册表) */
(function () {
  'use strict';

  /* ===== 动画:Fixed 池队列满 → EsAbortPolicy → 429 =====
     数字以本机 12 核实测为例:size = ((12*3)/2)+1 = 19,queue = 19*1000 = 19000 */
  var THREADS = 19;
  var QUEUE_MAX = 19000;

  function stepSvg(cfg) {
    var s = '<svg viewBox="0 0 760 252" xmlns="http://www.w3.org/2000/svg">';
    s += '<defs><marker id="ah08r" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
      + '<path d="M 0 0 L 10 5 L 0 10 z" class="fig-arrowhead"/></marker></defs>';

    /* 客户端 */
    s += '<rect x="10" y="34" width="112" height="56" rx="9" class="fig-box"/>';
    s += '<text x="66" y="56" text-anchor="middle" class="fig-name">客户端</text>';
    s += '<text x="66" y="76" text-anchor="middle" class="fig-sub">并发 _search</text>';

    /* 提交箭头(拒绝发生后变警示色) */
    s += '<line x1="122" y1="62" x2="146" y2="62" ' + (cfg.reject
      ? 'class="fig-arrow" style="stroke: rgb(var(--warn))"'
      : 'class="fig-arrow"') + ' marker-end="url(#ah08r)"/>';

    /* search 池 */
    s += '<rect x="150" y="16" width="380" height="152" rx="10" class="fig-box"/>';
    s += '<text x="340" y="40" text-anchor="middle" class="fig-name">search 池 · Fixed</text>';

    /* 线程槽:前两条 + 省略号 */
    var slotX = [170, 286, 402];
    for (var i = 0; i < 3; i++) {
      var busy = cfg.busy[i];
      var label = i < 2
        ? (i + 1) + '/' + THREADS + (busy ? ' 忙' : ' 空闲')
        : '… 共 ' + THREADS + ' 条';
      s += '<rect x="' + slotX[i] + '" y="56" width="106" height="30" rx="6" class="'
        + (busy ? 'fig-box-hot fp-pop' : 'fig-box') + '"/>';
      s += '<text x="' + (slotX[i] + 53) + '" y="75" text-anchor="middle" class="fig-sub">' + label + '</text>';
    }

    /* 队列:外框 + 水位 */
    s += '<rect x="170" y="100" width="336" height="32" rx="6" class="fig-box"/>';
    if (cfg.queue > 0) {
      var w = Math.max(4, Math.round(cfg.queue / QUEUE_MAX * 328));
      s += '<rect x="174" y="104" width="' + w + '" height="24" rx="4" class="fig-box-hot fp-slide-right"/>';
    }
    var qLabel = 'queue ' + cfg.queue + ' / ' + QUEUE_MAX;
    s += '<text x="338" y="121" text-anchor="middle" class="' + (cfg.full
      ? 'fig-key fp-pulse" style="fill: rgb(var(--warn))'
      : 'fig-key') + '">' + qLabel + '</text>';
    s += '<text x="340" y="152" text-anchor="middle" class="fig-sub">queue_size = size × 1000 = ' + QUEUE_MAX + '</text>';

    /* 右侧:拒绝链 */
    if (cfg.reject) {
      s += '<line x1="532" y1="62" x2="544" y2="62" class="fig-arrow" style="stroke: rgb(var(--warn))" marker-end="url(#ah08r)"/>';
      s += '<rect x="548" y="30" width="200" height="58" rx="9" class="fig-box-hot fp-pop"/>';
      s += '<text x="648" y="52" text-anchor="middle" class="fig-name">EsAbortPolicy</text>';
      s += '<text x="648" y="72" text-anchor="middle" class="fig-sub">incrementRejections()</text>';
      s += '<line x1="648" y1="90" x2="648" y2="108" class="fig-arrow" marker-end="url(#ah08r)"/>';
      s += '<rect x="548" y="112" width="200" height="58" rx="9" class="fig-box-hot' + (cfg.four29 ? ' fp-glow' : '') + '"/>';
      s += '<text x="648" y="134" text-anchor="middle" class="fig-name">429 Too Many Requests</text>';
      s += '<text x="648" y="154" text-anchor="middle" class="fig-sub">EsRejectedExecutionException</text>';
    }

    s += '<text x="380" y="236" text-anchor="middle" class="fig-sub">Fixed 有界队列满 → EsAbortPolicy → 429;Scaling(generic/flush 等)正常运行不拒绝</text>';
    s += '</svg>';
    return s;
  }

  var STEPS = [
    {
      busy: [1, 0, 0], queue: 0,
      note: '起步:线程还有空闲,execute() 直接把任务交给空闲线程,队列是空的。注意 Fixed 池线程数钉死(图中以 12 核节点的 19 条为例)——它靠队列和拒绝扛峰值,不靠扩容。'
    },
    {
      busy: [1, 1, 1], queue: 1500,
      note: '19 条线程全部在跑 Lucene 查询,新到的搜索只能进 SizeBlockingQueue 排队。此刻请求既不占线程、也没被拒绝,但排队本身就在涨尾延迟。'
    },
    {
      busy: [1, 1, 1], queue: 12500,
      note: '到达速率持续大于完成速率,水位一路上探。队列买的是「削峰」的时间,不是吞吐;峰不停,总有到顶的一刻。'
    },
    {
      busy: [1, 1, 1], queue: QUEUE_MAX, full: 1,
      note: '队列 19000 满:这次 submit 的 offer 失败,任务不会再等。下一步不是扩线程(Fixed 不扩),而是走拒绝策略。'
    },
    {
      busy: [1, 1, 1], queue: QUEUE_MAX, full: 1, reject: 1,
      note: 'EsAbortPolicy.rejectedExecution:先 incrementRejections()——就是 _cat/thread_pool 的 rejected 列;再 throw EsRejectedExecutionException。带 forceExecution 标记的内部任务才会被强行塞回队列。'
    },
    {
      busy: [1, 1, 1], queue: QUEUE_MAX, full: 1, reject: 1, four29: 1,
      note: 'ExceptionsHelper.status 认出这个异常,映射 RestStatus.TOO_MANY_REQUESTS → HTTP 429。客户端该退避、换节点、降速;想改队列大小?thread_pool.* 不是 Dynamic,只能改 yml 重启。'
    }
  ];

  window.ESFLOWS = window.ESFLOWS || {};
  window.ESFLOWS['ch08-reject'] = {
    version: 1,
    id: 'ch08-reject',
    title: '线程池拒绝链路:队列水位满 → 429',
    speed: 2000,
    steps: STEPS.map(function (st) { return { svg: stepSvg(st), note: st.note }; })
  };

  /* ===== 实验 ===== */
  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};
  window.ESEXPERIMENTS['ch08-00-pools'] = {
    version: 1, id: 'ch08-00-pools',
    title: '实验 0 · 看关键池:type / size / queue_size',
    method: 'GET',
    path: '/_cat/thread_pool/search,search_coordination,write,write_coordination,get,analyze,cluster_coordination,generic,management?v&h=name,type,size,queue_size,active,queue,rejected',
    body: null,
    predict: '先猜:type 一列有几种取值?cluster_coordination 的 size 和 queue_size 分别是多少?search 和 write 谁的队列大?',
    expect: '只有 fixed 和 scaling 两种。以 12 核节点为例:search 19/19000、write 12/10000(你的 N 不同则按公式变)——旧文档「write 队列比 search 大一个数量级」在 9.4.0 已经反了。cluster_coordination 是 1/-1:单线程、无界队列。'
  };
  window.ESEXPERIMENTS['ch08-01-processors'] = {
    version: 1, id: 'ch08-01-processors',
    title: '实验 1 · 拿到 N,自己算一遍线程数',
    method: 'GET',
    path: '/_nodes/os?filter_path=nodes.*.os.available_processors,nodes.*.os.allocated_processors',
    body: null,
    predict: '你的 N 是多少?算 ((N*3)/2)+1,和实验 0 的 search.size 对得上吗?',
    expect: '拿你的 N 验算:((N*3)/2)+1 应等于 search/get 的 size,N 等于 write 的 size,(N+1)/2 等于 search_coordination(12 核:19 / 12 / 6)。公式在 ThreadPool.searchOrGetThreadPoolSize 与 DefaultBuiltInExecutorBuilders,数字别背旧文档。'
  };
  window.ESEXPERIMENTS['ch08-02-defaults'] = {
    version: 1, id: 'ch08-02-defaults',
    title: '实验 2 · 默认值里的队列口径',
    method: 'GET',
    path: '/_cluster/settings?include_defaults=true&filter_path=defaults.thread_pool.search,defaults.thread_pool.write,defaults.thread_pool.cluster_coordination',
    body: null,
    predict: 'search 的 queue_size 是固定 1000,还是 size×1000?cluster_coordination 的 queue_size 呢?',
    expect: 'search.queue_size = size×1000(12 核节点是 "19000"),不是旧文档的固定 1000;cluster_coordination.queue_size = "-1"(无界)。这些值经 include_defaults 才可见——yml 里其实一个字都没写。'
  };
  window.ESEXPERIMENTS['ch08-03-put-queue'] = {
    version: 1, id: 'ch08-03-put-queue',
    title: '实验 3 · 踹墙:运行时改小 search 队列',
    method: 'PUT',
    path: '/_cluster/settings',
    body: { transient: { 'thread_pool.search.queue_size': 1 } },
    predict: '第 5 课的 Dynamic 集群设置能在线改。线程池队列也是设置,这次 PUT 会成功吗?状态码多少?',
    expect: '400:transient setting [thread_pool.search.queue_size], not dynamically updateable。FixedExecutorBuilder 登记这个 key 时只标 Property.NodeScope、没有 Dynamic——背压参数属于「启动时想清楚」,不是运行时旋钮。想改:改 yml 再重启。'
  };
  window.ESEXPERIMENTS['ch08-04-setup'] = {
    version: 1, id: 'ch08-04-setup',
    title: '实验 4 · 建索引 tut-l08-docs(1 分片 0 副本)',
    method: 'PUT',
    path: '/tut-l08-docs',
    body: { settings: { number_of_shards: 1, number_of_replicas: 0 } },
    predict: '单节点 + 0 副本,这次集群是 green 还是 yellow?',
    expect: 'green——副本数是 0,没有放不下的分片。这个索引只用来制造几次可观测的搜索流量。'
  };
  window.ESEXPERIMENTS['ch08-05-doc'] = {
    version: 1, id: 'ch08-05-doc',
    title: '实验 5 · 写一篇文档(带 refresh)',
    method: 'POST',
    path: '/tut-l08-docs/_doc?refresh=true',
    body: { title: 'async invariant' },
    predict: '这一次写入会让哪个池的 completed +1?search 池会动吗?',
    expect: 'result: created。写入落在 write 池;refresh=true 顺带让 refresh 池多跑一次任务。search 池与此无关——「隔离」就是从计数上读出来的。'
  };
  window.ESEXPERIMENTS['ch08-06-search'] = {
    version: 1, id: 'ch08-06-search',
    title: '实验 6 · 搜一次,想想路径',
    method: 'POST',
    path: '/tut-l08-docs/_search',
    body: { query: { match: { title: 'invariant' } } },
    predict: '这条搜索在本节点上依次经过哪些池?(对照正文图 2)',
    expect: 'hits 命中 1。路径:DIRECT 上跑过滤器链 → search_coordination 做 rewrite → search 池跑 Lucene → 回调里合并。单节点身兼协调与数据两角,两个池的计数都会动。'
  };
  window.ESEXPERIMENTS['ch08-07-counters'] = {
    version: 1, id: 'ch08-07-counters',
    title: '实验 7 · 用 completed 验证隔离',
    method: 'GET',
    path: '/_cat/thread_pool/search,search_coordination,write,get?v&h=name,active,queue,rejected,completed',
    body: null,
    predict: '做完实验 5、6 再看:涨的是哪几行?write 的 completed 还会涨吗?',
    expect: 'search 与 search_coordination 的 completed 因搜索上涨;write 停在写入那一刻——搜索流量没有泄漏进写池。active/queue 平时是 0:任务来得快、走得也快,水位只在过载时停留。'
  };
  window.ESEXPERIMENTS['ch08-08-rejected'] = {
    version: 1, id: 'ch08-08-rejected',
    title: '实验 8 · 看 rejected 列(应为 0)',
    method: 'GET',
    path: '/_cat/thread_pool/search,write,get,generic,management,flush,refresh,cluster_coordination?v&h=name,type,queue,rejected',
    body: null,
    predict: '哪些池有可能 rejected > 0?generic/refresh 这些 scaling 池会拒绝吗?',
    expect: '全是 0(除非集群真的在扛过载)。fixed + 有界队列的 search/write/get 才会经 EsAbortPolicy 拒绝;scaling 池走 ForceQueuePolicy,正常运行只是塞回无界队列,不会 429。别在教程集群上压测这个数字,看懂列就行。'
  };
  window.ESEXPERIMENTS['ch08-09-cleanup'] = {
    version: 1, id: 'ch08-09-cleanup',
    title: '清理 · 删除实验索引',
    method: 'DELETE',
    path: '/tut-l08-docs',
    body: null,
    predict: '实验 3 那次失败的 PUT 留下了 transient 设置吗?需要清理吗?',
    expect: 'acknowledged: true。不需要:那次 PUT 被整体拒绝,transient 里什么都没写进去——可以 GET /_cluster/settings 验证为空。'
  };
})();
