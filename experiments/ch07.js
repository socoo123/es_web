/* experiments/ch07.js — 第 7 课:实验(动作框架:REST 名 / Action 名 / 两层失败) */
(function () {
  'use strict';
  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};

  window.ESEXPERIMENTS['ch07-00-setup'] = {
    version: 1, id: 'ch07-00-setup',
    title: '实验 0 · 建索引 tut-l07-docs(1 分片 0 副本)',
    method: 'PUT', path: '/tut-l07-docs',
    body: { settings: { number_of_shards: 1, number_of_replicas: 0 } },
    predict: '先猜:单节点上副本给 0 是图什么?(回忆第 1 课的 yellow)',
    expect: 'acknowledged: true。副本 0 让单节点保持 green,本课只做 GET 实验,不想让 yellow 噪音混进观察。'
  };
  window.ESEXPERIMENTS['ch07-01-doc'] = {
    version: 1, id: 'ch07-01-doc',
    title: '实验 1 · 写入靶子文档 _doc/1',
    method: 'PUT', path: '/tut-l07-docs/_doc/1',
    body: { title: 'action-framework' },
    predict: '先猜:这次 PUT 会在 _nodes/usage 里给哪个键 +1?叫 indices:data/write/index 吗?',
    expect: 'result: created。usage 记的是 REST Handler 名——document_index_action,不是那串 Action 名。这正是本课要拆的两个名字空间。'
  };
  window.ESEXPERIMENTS['ch07-02-get'] = {
    version: 1, id: 'ch07-02-get',
    title: '实验 2 · 显微镜下的那次 GET',
    method: 'GET', path: '/tut-l07-docs/_doc/1?pretty',
    body: null,
    predict: '先猜:这几十毫秒里请求走完了哪几站才拿到 _source?',
    expect: '200,found: true。对照图 3 六步:RestGetAction 造 GetRequest → client.get 填 TYPE → NodeClient 查表 → TaskManager 登记 → RequestFilterChain → AsyncSingleAction(TransportSingleShardAction)选 shard 读 Engine。'
  };
  window.ESEXPERIMENTS['ch07-03-usage'] = {
    version: 1, id: 'ch07-03-usage',
    title: '实验 3 · REST 名:usage 里的计数键',
    method: 'GET', path: '/_nodes/usage?filter_path=nodes.*.rest_actions',
    body: null,
    predict: '先猜:刚才那次 GET,计数加在哪个键上?indices:data/read/get 会出现吗?',
    expect: 'document_get_action ≥ 1,而 indices:data/read/get 在这份 JSON 里永远找不到。usage 数的是 RestHandler 被调次数(RestGetAction.getName() 返回 document_get_action);Action 名活在 _tasks、授权和跨节点帧里,是另一个名字空间。'
  };
  window.ESEXPERIMENTS['ch07-04-tasks-self'] = {
    version: 1, id: 'ch07-04-tasks-self',
    title: '实验 4 · Action 名:_tasks 抓到自己',
    method: 'GET', path: '/_tasks?actions=cluster:monitor/tasks/lists*&group_by=none',
    body: null,
    predict: '先猜:列表任务是瞬时操作,返回会是空数组吗?action 字段长得像 REST 路径还是像 indices:data/read/get?',
    expect: '列表任务自己也是 Task:action = cluster:monitor/tasks/lists,还带着 node 级子任务 …lists[n](parent_task_id 指回它)——它正等各节点回包,被自己抓个正着。_tasks 说的一直是 Action 名;cancellable: true 就是 _cancel 的作用对象。'
  };
  window.ESEXPERIMENTS['ch07-05-fake-action'] = {
    version: 1, id: 'ch07-05-fake-action',
    title: '实验 5 · 假 Action 名只是过滤器',
    method: 'GET', path: '/_tasks?actions=indices:data/read/not_a_real_get&group_by=none',
    body: null,
    predict: '先猜:这个名字从没登记过,会报错吗?400、404 还是别的?',
    expect: '{"tasks":[]}——actions= 只是按前缀过滤列表,不执行任何动作;名字登记没登记,这里既不知道也不关心。真正执行未登记名字的报错(IllegalStateException: failed to find action)只出现在 NodeClient 内部查表时,REST 调不出来。'
  };
  window.ESEXPERIMENTS['ch07-06-bad-path'] = {
    version: 1, id: 'ch07-06-bad-path',
    title: '实验 6 · 坏路径死在哪一层',
    method: 'GET', path: '/tut-l07-docs/_not_an_action/1',
    body: null,
    predict: '先猜:状态码多少?错误文案里会出现 failed to find action 吗?',
    expect: '400:no handler found for uri —— 死在第 6 课 RestController 的路由匹配,请求根本到不了 NodeClient。404 是「路由命中、文档不存在」的语义;failed to find action 是另一层的病,别混。(_cat/actions 同样是这个 400,ActionType 表从不外泄。)'
  };
  window.ESEXPERIMENTS['ch07-07-empty-id'] = {
    version: 1, id: 'ch07-07-empty-id',
    title: '实验 7 · 空 id 撞上的是路由,不是校验',
    method: 'GET', path: '/tut-l07-docs/_doc/',
    body: null,
    predict: '先猜:URL 里 id 这段空着,会看到 GetRequest 校验的 id is missing 吗?状态码多少?',
    expect: '405:Incorrect HTTP method——/{index}/_doc(带不带尾斜杠)命中的是「无 id 自动生成」的 POST 路由,GET 不在允许方法里。GetRequest.validate() 的 id is missing 挡的是内部/Transport 调用者构造的空 id 请求:TransportAction.handleExecution 的校验在过滤器之前,但 REST 路由层先把球拦下了。'
  };
  window.ESEXPERIMENTS['ch07-08-cleanup'] = {
    version: 1, id: 'ch07-08-cleanup',
    title: '清理 · 删除实验索引',
    method: 'DELETE', path: '/tut-l07-docs',
    body: null,
    predict: '先猜:删除后 usage 里的 document_get_action 计数会归零吗?',
    expect: 'acknowledged: true。不会归零——_nodes/usage 是进程级累计计数,删索引不清空;它数的是「RestHandler 被调过几次」,不是「哪些对象还在」。'
  };
})();
