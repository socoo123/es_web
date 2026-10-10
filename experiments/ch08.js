/* experiments/ch08.js — 第 8 课:实验 + 线程池拒绝链路动画(注册表) */
(function () {
  'use strict';

  /* ===== 动画:Fixed 池队列满 → EsAbortPolicy → 429 =====
     概念快照：9.4.0 默认自管节点 N=12，无线程池覆盖；不是本轮压测记录 */
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
      s += '<text x="648" y="154" text-anchor="middle" class="fig-sub">拒绝异常（见解说）</text>';
    }

    s += '<text x="380" y="236" text-anchor="middle" class="fig-sub">普通有界任务：队列满 → 拒绝；本图假定异常最终成为 REST 错误</text>';
    s += '</svg>';
    return s;
  }

  var STEPS = [
    {
      busy: [1, 0, 0], queue: 0,
      note: "默认自管节点示例 N=12：search 固定大小 19，默认队列容量 19000。线程尚有余量时，已建立的空闲 worker 可从队列接走工作；execute 不是永远绕过队列直接交接。此图是概念快照，未做压测。"
    },
    {
      busy: [1, 1, 1], queue: 1500,
      note: "假定 19 个 worker 都忙，新任务进入有界队列等待。排队不为每个任务占一条 worker，但会占用请求对象和内存；异步不能消除排队延迟。"
    },
    {
      busy: [1, 1, 1], queue: 12500,
      note: "到达速率持续超过处理速率，队列上涨。增大容量只能多容纳等待中的任务，不保证吞吐提高，也会增加延迟与内存压力。"
    },
    {
      busy: [1, 1, 1], queue: QUEUE_MAX, full: 1,
      note: "假定 worker 均忙、队列容量 19000 已用尽，普通新任务的 offer 失败；Fixed 不继续扩容。并发完成可能改变瞬时结果，本快照固定住这个触发条件。"
    },
    {
      busy: [1, 1, 1], queue: QUEUE_MAX, full: 1, reject: 1,
      note: "EsAbortPolicy：节点未 shutdown 且任务 isForceExecution 时尝试强制入队；否则增加 rejected 并产生 EsRejectedExecutionException。该异常也可能被 AbstractRunnable 通过 onRejection 送入失败回调。"
    },
    {
      busy: [1, 1, 1], queue: QUEUE_MAX, full: 1, reject: 1, four29: 1,
      note: "ExceptionsHelper.status 将 EsRejectedExecutionException 映射为 429。整条请求最终以该错误返回时才是 HTTP 429；Bulk 项目错误、搜索部分失败不能一概推断顶层状态。客户端降低并发并退避重试；参数修改需节点配置与重启。"
    }
  ];

  window.ESFLOWS = window.ESFLOWS || {};
  window.ESFLOWS['ch08-reject'] = {
    version: 1,
    id: 'ch08-reject',
    title: '线程池背压：有界队列与拒绝错误',
    speed: 2000,
    steps: STEPS.map(function (st) { return { svg: stepSvg(st), note: st.note }; })
  };

  /* ===== 实验：源码预期，不冒充本轮 API 实测 ===== */
  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};
  window.ESEXPERIMENTS["ch08-00-version"] = {
  "version": 1,
  "id": "ch08-00-version",
  "title": "A1 · 先核对节点版本",
  "method": "GET",
  "path": "/",
  "body": null,
  "predict": "端点是否为本课单节点自管 ES 9.4.0？",
  "expect": "应读到 version.number=9.4.0、version.lucene_version=10.4.0。不是对应版本时先切换实验端点；线程池表与源码不应跨版本套用。"
};
  window.ESEXPERIMENTS["ch08-01-processors"] = {
  "version": 1,
  "id": "ch08-01-processors",
  "title": "A2 · 用 allocated_processors 计算默认大小",
  "method": "GET",
  "path": "/_nodes/os?filter_path=nodes.*.name,nodes.*.os.available_processors,nodes.*.os.allocated_processors",
  "body": null,
  "predict": "N 取 available 还是 allocated？奇数 N 的除法怎样取整？",
  "expect": "取各节点 allocated_processors，它已向上取整；Java 整数除法下 search/get=floor(3N/2)+1，search_coordination=floor((N+1)/2)，write=N。仅无线程池覆盖的默认自管节点适用，按同一节点对照 A3。"
};
  window.ESEXPERIMENTS["ch08-00-pools"] = {
  "version": 1,
  "id": "ch08-00-pools",
  "title": "A3 · 对照池类型、配置大小与实时水位",
  "method": "GET",
  "path": "/_cat/thread_pool/search,search_coordination,write,write_coordination,get,analyze,cluster_coordination,generic,management?v&h=node_name,node_id,name,type,size,core,max,queue_size,active,queue,rejected,completed",
  "body": null,
  "predict": "size 和 active 是同一件事吗？Scaling 看哪两列？",
  "expect": "默认自管 N=12：search 19/19000、write 12/10000；cluster_coordination 固定 1、queue_size=-1。Fixed 的 size 是配置大小，Scaling 用 core/max 看范围；active/queue 是瞬时统计，rejected/completed 自本次节点进程启动累计。"
};
  window.ESEXPERIMENTS["ch08-02-defaults"] = {
  "version": 1,
  "id": "ch08-02-defaults",
  "title": "A4 · 对照处理请求节点的设置视图",
  "method": "GET",
  "path": "/_cluster/settings?include_defaults=true&filter_path=defaults.thread_pool.search,defaults.thread_pool.write,defaults.thread_pool.cluster_coordination",
  "body": null,
  "predict": "defaults 一定是纯硬编码默认值吗？",
  "expect": "无节点覆盖时预期 search.queue_size 为默认 search 大小×1000，cluster_coordination.queue_size=-1。defaults 也可带处理 REST 请求节点的本地设置，不能推出所有节点相同；改 search.size 不保证默认 queue_size 随之重算，二者是独立设置。"
};
  window.ESEXPERIMENTS["ch08-03-settings-before"] = {
  "version": 1,
  "id": "ch08-03-settings-before",
  "title": "A5 · 记录线程池集群覆盖视图",
  "method": "GET",
  "path": "/_cluster/settings?filter_path=persistent.thread_pool,transient.thread_pool",
  "body": null,
  "predict": "失败更新前 persistent/transient 有没有本课键？",
  "expect": "保存响应作为 A7 的对照。干净实验节点通常没有匹配键，filter_path 可能得到空对象；它不含节点 yml 设置，也不代表集群全部设置为空。"
};
  window.ESEXPERIMENTS["ch08-03-put-queue"] = {
  "version": 1,
  "id": "ch08-03-put-queue",
  "title": "A6 · 尝试动态改 search 队列",
  "method": "PUT",
  "path": "/_cluster/settings",
  "body": {
    "transient": {
      "thread_pool.search.queue_size": 1
    }
  },
  "predict": "NodeScope 就能经集群 API 动态更新吗？",
  "expect": "本课自管 9.4.0 预期 HTTP 400，reason 含 transient setting [thread_pool.search.queue_size], not dynamically updateable；此键已注册但没有 Dynamic。若是 401/403 或 not recognized，先核对认证、部署和版本，不能当作相同验证结果。"
};
  window.ESEXPERIMENTS["ch08-03-settings-after"] = {
  "version": 1,
  "id": "ch08-03-settings-after",
  "title": "A7 · 确认失败没有留下本课覆盖",
  "method": "GET",
  "path": "/_cluster/settings?filter_path=persistent.thread_pool,transient.thread_pool",
  "body": null,
  "predict": "A6 的失败会留下队列大小 1 吗？",
  "expect": "与 A5 的本课键一致：被拒绝的更新未写入该 transient 覆盖。不宣称整个 transient 对象为空；其他设置可能原本存在或并发变化。本课没有成功修改集群设置，无须写 null 清理。"
};
  window.ESEXPERIMENTS["ch08-08-rejected"] = {
  "version": 1,
  "id": "ch08-08-rejected",
  "title": "A8 · 读累计拒绝计数，保留基线",
  "method": "GET",
  "path": "/_cat/thread_pool/search,write,get,generic,management,flush,refresh,cluster_coordination?v&h=node_name,node_id,name,type,queue,rejected,completed",
  "body": null,
  "predict": "没有当前排队，rejected 就必须是 0 吗？",
  "expect": "保存同一 node_id 的 rejected 基线；当前 queue=0 不会清除历史拒绝。新启动且无过载的节点常为 0，已有值不表示本课触发。Scaling 无有界队列满拒绝不代表无资源压力；其他层也可能产生 429。此实验不做压测。"
};
  window.ESEXPERIMENTS["ch08-04-setup"] = {
  "version": 1,
  "id": "ch08-04-setup",
  "title": "B1 · 创建本课索引与显式 mapping",
  "method": "PUT",
  "path": "/tut-l08-docs",
  "body": {
    "settings": {
      "number_of_shards": 1,
      "number_of_replicas": 0,
      "refresh_interval": "-1"
    },
    "mappings": {
      "dynamic": "strict",
      "properties": {
        "title": {
          "type": "text",
          "analyzer": "standard"
        }
      }
    }
  },
  "predict": "创建成功能否立即推出整个集群 green？",
  "expect": "首次预期 acknowledged=true；不以此判断分片已 green，继续 B2。索引已存在时通常 400 resource_already_exists_exception；确认仅含本课数据后点名清理，再从 B1 重做。refresh_interval=-1 停止周期刷新，B3 显式 refresh。"
};
  window.ESEXPERIMENTS["ch08-04-health"] = {
  "version": 1,
  "id": "ch08-04-health",
  "title": "B2 · 等待本课主分片就绪",
  "method": "GET",
  "path": "/_cluster/health/tut-l08-docs?wait_for_status=green&timeout=5s",
  "body": null,
  "predict": "0 副本能否消除所有分配问题？",
  "expect": "在节点可分配且无资源阻塞时，预期 status=green、timed_out=false、active_primary_shards=1。超时或非 green 时先排查分片/磁盘条件，不继续按正常前提实验；只限定本课索引，其他索引可让整个集群非 green。"
};
  window.ESEXPERIMENTS["ch08-05-doc"] = {
  "version": 1,
  "id": "ch08-05-doc",
  "title": "B3 · 固定 ID 写入并显式刷新",
  "method": "PUT",
  "path": "/tut-l08-docs/_doc/1?refresh=true",
  "body": {
    "title": "async invariant"
  },
  "predict": "重复运行会增加文档数吗？refresh 池必然 +1 吗？",
  "expect": "首次通常 201 created，重写 ID 1 通常 200 updated；文档数不随重复写入增长。refresh=true 令该写入完成后可搜索，不承诺 refresh 池 completed +1。写入与刷新后再取 B4 基线。"
};
  window.ESEXPERIMENTS["ch08-05-baseline"] = {
  "version": 1,
  "id": "ch08-05-baseline",
  "title": "B4 · 搜索前保存线程池基线",
  "method": "GET",
  "path": "/_cat/thread_pool/search,search_coordination,write,get,refresh?v&h=node_name,node_id,name,active,queue,rejected,completed",
  "body": null,
  "predict": "为什么要在写入完成后再取 completed？",
  "expect": "保存同一 node_id 的 completed/rejected；不要把写入期间的任务算作搜索差值。它们是节点所有工作累计统计，包含预热和后台任务；没有请求级归因，也没有承诺每个 HTTP 请求对应一个线程池任务。"
};
  window.ESEXPERIMENTS["ch08-06-search"] = {
  "version": 1,
  "id": "ch08-06-search",
  "title": "B5 · 搜索一次，核对结果与调度边界",
  "method": "POST",
  "path": "/tut-l08-docs/_search",
  "body": {
    "request_cache": false,
    "track_total_hits": true,
    "query": {
      "match": {
        "title": "invariant"
      }
    }
  },
  "predict": "只有一个分片时，query 与 fetch 总是分开发两轮吗？",
  "expect": "本课只有 ID 1 时预期 hits.total.value=1、relation=eq、命中 _id=1。普通单分片、无 rank 的搜索可以合并 query/fetch；回调不保证每段都切线程。关闭本次请求缓存仍不把全节点 completed 变成精确请求计数。"
};
  window.ESEXPERIMENTS["ch08-07-counters"] = {
  "version": 1,
  "id": "ch08-07-counters",
  "title": "B6 · 读后差值，避免精确归因",
  "method": "GET",
  "path": "/_cat/thread_pool/search,search_coordination,write,get,refresh?v&h=node_name,node_id,name,active,queue,rejected,completed",
  "body": null,
  "predict": "search_coordination 必定 +1、write 必定不变吗？",
  "expect": "与 B4 按 node_id 对照。search 工作通常增加，search_coordination 增量受同步完成/调度路径影响；write/refresh 也可能有后台变化。completed 是累计执行任务数，active/queue 是快照，不能用单次统计证明隔离或推断 listener 的线程。"
};
  window.ESEXPERIMENTS["ch08-09-cleanup"] = {
  "version": 1,
  "id": "ch08-09-cleanup",
  "title": "清理 · 点名删除本课索引",
  "method": "DELETE",
  "path": "/tut-l08-docs",
  "body": null,
  "predict": "删除索引会清空线程池累计计数吗？",
  "expect": "仅删除 tut-l08-docs，预期 acknowledged=true；重复删除已不存在的索引通常 404 index_not_found_exception。累计计数不归零。重做顺序 B1→B2→B3→B4→B5→B6→清理，并重新记录基线；A6 未成功写入设置。"
};
})();
