/* 第 7 课：两组实验 / 15 张操作卡；ES 9.4.0，专用单节点。预期不是本轮实测。 */
(function () {
  'use strict';
  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};

  window.ESEXPERIMENTS['ch07-00-setup'] = {
    version: 1, id: 'ch07-00-setup', title: 'A1 · 显式创建本课索引',
    method: 'PUT', path: '/tut-l07-docs',
    body: {
      settings: { number_of_shards: 1, number_of_replicas: 0, refresh_interval: '1s' },
      mappings: { dynamic: 'strict', properties: { title: { type: 'keyword' } } }
    },
    predict: '先猜：为什么先清理、显式创建，而不让写入自动建索引？',
    expect: '首次创建预期 acknowledged:true。1 分片、0 副本，title 明确映射为 keyword。索引已存在会报 resource_already_exists_exception；先运行末尾点名清理再重做。分片就绪由下一卡确认。'
  };
  window.ESEXPERIMENTS['ch07-00-health'] = {
    version: 1, id: 'ch07-00-health', title: 'A2 · 只等待本课索引就绪',
    method: 'GET', path: '/_cluster/health/tut-l07-docs?wait_for_status=green&timeout=5s', body: null,
    predict: '先猜：集群里其他索引 yellow，会让本课索引的检查也 yellow 吗？',
    expect: '在专用单节点与上述设置下，预期 status:green、timed_out:false。这里限定 tut-l07-docs；若超时或索引不存在，先恢复创建与分片前提，不继续解释后续 GET。'
  };
  window.ESEXPERIMENTS['ch07-01-doc'] = {
    version: 1, id: 'ch07-01-doc', title: 'A3 · 写入文档并等待刷新',
    method: 'PUT', path: '/tut-l07-docs/_doc/1?refresh=true', body: { title: 'action-framework' },
    predict: '先猜：PUT 的 REST 计数键会叫 indices:data/write/index 吗？',
    expect: '新索引首次写入预期 201、result:created；重复同 ID 写入通常 200、updated。refresh=true 完成刷新。该 REST 处理器计数名是 document_index_action；内部 client.index 使用 indices:data/write/index，之后委托单元素 bulk。'
  };
  window.ESEXPERIMENTS['ch07-01-usage-before'] = {
    version: 1, id: 'ch07-01-usage-before', title: 'A4 · GET 之前记录每个节点的 REST 计数',
    method: 'GET', path: '/_nodes/usage?filter_path=nodes.*.rest_actions', body: null,
    predict: '先猜：document_get_action 没出现，是否证明动作没有登记？',
    expect: '预期 200。记录各节点 document_get_action 为基线 N；从未计数的键可省略，按 0 对照。此处是正数使用计数，不是注册表。不要把不同节点或节点重启前后的数值相减。'
  };
  window.ESEXPERIMENTS['ch07-02-get'] = {
    version: 1, id: 'ch07-02-get', title: 'A5 · 执行一次文档 GET',
    method: 'GET', path: '/tut-l07-docs/_doc/1?pretty', body: null,
    predict: '先猜：client.get 是直接读 Engine，还是先选择动作并登记 Task？',
    expect: '预期 200、found:true、_source.title 为 action-framework。对照图 1 查表 → 登记 Task，再对照图 2 校验与过滤。GET 的协调 doExecute 在 TransportSingleShardAction；分片读取细节见第 10 课。'
  };
  window.ESEXPERIMENTS['ch07-03-usage'] = {
    version: 1, id: 'ch07-03-usage', title: 'A6 · 对照 GET 后的 REST 计数',
    method: 'GET', path: '/_nodes/usage?filter_path=nodes.*.rest_actions', body: null,
    predict: '先猜：刚才那次 GET 把哪个键加一？为什么不找 indices:data/read/get？',
    expect: '专用单节点、无其他 GET 且未重启时，document_get_action 应为 N+1；重跑 A5 后再查会继续增加。内置 Handler 的键来自 getName，不是 ActionType.name。若有其他请求，只解释累计计数，不宣称精确增量。'
  };
  window.ESEXPERIMENTS['ch07-03-get-tasks'] = {
    version: 1, id: 'ch07-03-get-tasks', title: 'A7 · GET 完成后再查对应 Task',
    method: 'GET', path: '/_tasks?actions=indices:data/read/get*&group_by=none&detailed=true', body: null,
    predict: '先猜：上一卡计数还在，为什么这里却可能没有 GET？',
    expect: '预期 200；无并发匹配操作时 tasks:[]。完成的 GET 已注销，_tasks 不是历史记录。若有条目，它们是采样时仍运行的匹配任务；看 action、id 与 parent_task_id，不能据此证明上一张 GET 卡仍在运行。'
  };
  window.ESEXPERIMENTS['ch07-04-tasks-self'] = {
    version: 1, id: 'ch07-04-tasks-self', title: 'B1 · 通配匹配任务列表动作',
    method: 'GET', path: '/_tasks?actions=cluster:monitor/tasks/lists*&group_by=none', body: null,
    predict: '先猜：末尾 * 会同时匹配 lists 和 lists[n] 吗？',
    expect: '预期 200。普通单节点上可观察列表动作 cluster:monitor/tasks/lists 及节点子动作 …lists[n]，后者通过 parent_task_id 关联父任务。具体 ID、时长和条目数随采样变化；这里验证名称形态与通配匹配，不固定整份 JSON。'
  };
  window.ESEXPERIMENTS['ch07-04-tasks-exact'] = {
    version: 1, id: 'ch07-04-tasks-exact', title: 'B2 · 去掉星号，只匹配完整名称',
    method: 'GET', path: '/_tasks?actions=cluster:monitor/tasks/lists&group_by=none', body: null,
    predict: '先猜：没有 *，…lists[n] 还会出现在结果里吗？',
    expect: '预期 200，返回条目的 action 必须等于 cluster:monitor/tasks/lists；不匹配 …lists[n]。普通节点上列表父任务可被自身查询观察。数量与 ID 不固定，需同时检查 node_failures/task_failures。'
  };
  window.ESEXPERIMENTS['ch07-04-tasks-prefix'] = {
    version: 1, id: 'ch07-04-tasks-prefix', title: 'B3 · 截短名字但不加星号',
    method: 'GET', path: '/_tasks?actions=cluster:monitor/tasks/list&group_by=none', body: null,
    predict: '先猜：list 是 lists 的前缀，默认就会匹配吗？',
    expect: '默认动作集合下预期 200、tasks:[]。Regex.simpleMatch 没有 * 时按完整字符串相等；此处 list 不等于 lists。要做前缀匹配，需显式写 list*。'
  };
  window.ESEXPERIMENTS['ch07-05-fake-action'] = {
    version: 1, id: 'ch07-05-fake-action', title: 'B4 · 假动作名仍只是列表过滤条件',
    method: 'GET', path: '/_tasks?actions=indices:data/read/not_a_real_get&group_by=none', body: null,
    predict: '先猜：会执行这个名字并触发 failed to find action 吗？',
    expect: '默认动作集合且无节点失败时预期 200、tasks:[]。actions 只匹配当前 Task，不检查动作注册表，也不执行给定动作。内部查表失败来自 NodeClient.executeLocally；常用 client.execute 路径将该异常送入 listener.onFailure。'
  };
  window.ESEXPERIMENTS['ch07-06-bad-path'] = {
    version: 1, id: 'ch07-06-bad-path', title: 'B5 · 未注册 URL 在 REST 层失败',
    method: 'GET', path: '/tut-l07-docs/_not_an_action/1', body: null,
    predict: '先猜：错误会说 no handler found，还是 failed to find action？',
    expect: '默认自管 REST 路由集合下，预期 HTTP 400，顶层 error 字符串含 no handler found for uri，没有 error.reason。尚未到 NodeClient 的动作查表；GET /_cat/actions 也没有内置入口。404 还可能来自缺失索引或文档，需读具体响应。'
  };
  window.ESEXPERIMENTS['ch07-07-empty-id'] = {
    version: 1, id: 'ch07-07-empty-id', title: 'B6 · 缺 id 的 GET 先被方法匹配拦下',
    method: 'GET', path: '/tut-l07-docs/_doc/', body: null,
    predict: '先猜：能通过这个 URL 看到 GetRequest.validate 的 id is missing 吗？',
    expect: '预期 405、Incorrect HTTP method，允许方法为 POST。尾斜杠归一后对应自动生成 ID 的 POST /{index}/_doc；GET 不匹配。它没有构造一个空 ID 的 GetRequest，不能作为内部请求校验失败的实测。'
  };
  window.ESEXPERIMENTS['ch07-07-missing-doc'] = {
    version: 1, id: 'ch07-07-missing-doc', title: 'B7 · 已注册路径上的缺失文档',
    method: 'GET', path: '/tut-l07-docs/_doc/missing-id', body: null,
    predict: '先猜：id 不存在会使动作查表失败吗？',
    expect: '确认索引存在、missing-id 未写入时，预期 404、found:false，_id 为 missing-id。路由与 GetRequest 校验通过，动作表命中；这是业务存在性结果。此请求也增加 document_get_action 计数，计数不是成功率。'
  };
  window.ESEXPERIMENTS['ch07-08-cleanup'] = {
    version: 1, id: 'ch07-08-cleanup', title: '清理 · 只删除本课索引',
    method: 'DELETE', path: '/tut-l07-docs', body: null,
    predict: '先猜：删除索引会把 REST 计数也清零吗？',
    expect: '首次清理预期 acknowledged:true；重复清理可返回 404 index_not_found_exception。删除本课全部文档，保留进程内累计 REST 计数。重做按 A1 → A7 → B1 → B7 → 清理，重新记录基线 N；节点重启则另建计数基线。'
  };
})();
