/* 第 6 课：ES 9.4.0 REST 入口；专用单节点、普通索引，无同名模板/资源。
 * 保留原有 10 个 ID；显式创建 → 写入 → 对照 → 点名清理 → 重做。
 */
(function () {
  'use strict';
  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};
  var cards = [
    {
      id: 'ch06-00-create', title: '准备 · 显式创建本课索引',
      method: 'PUT', path: '/tut-l06-docs',
      body: { settings: { number_of_shards: 1, number_of_replicas: 0, auto_expand_replicas: false }, mappings: { dynamic: 'strict', _source: { enabled: true }, properties: { title: { type: 'keyword' }, views: { type: 'integer' } } } },
      predict: '索引不存在时创建成功；重复运行会怎样？',
      expect: '预期首次 acknowledged:true。重复创建返回 resource_already_exists_exception；先执行本课清理，再从此卡重做。显式配置一主片、零副本与字段类型，避免依赖自动建索引和动态映射。'
    },
    {
      id: 'ch06-00-setup', title: '准备 · 写入文档 1 并等待 refresh',
      method: 'PUT', path: '/tut-l06-docs/_doc/1?refresh=wait_for', body: { title: 'rest-layer', views: 6 },
      predict: '显式建好索引后，首次与重复写入的 result 一样吗？',
      expect: '预期首次 result:created，重复写同一 ID 为 updated。refresh=wait_for 等待这次写入可供搜索；本课默认 realtime GET 本身不依赖这一步。不要跳过创建卡：关闭自动建索引的环境下直接写入会失败。'
    },
    {
      id: 'ch06-00-get', title: '基线 · GET 已存在的文档',
      method: 'GET', path: '/tut-l06-docs/_doc/1', body: null,
      predict: '状态码、found 和 _source.title 分别是什么？',
      expect: '预期 200、found:true、_source.title 为 rest-layer。路由命中只决定处理器，文档存在性仍由 Action 执行结果提供；后面的 HEAD 对照使用同一资源。'
    },
    {
      id: 'ch06-01-nohandler', title: '路由 · 多段未注册路径返回 400',
      method: 'GET', path: '/_this_path_is_not_registered/at/all', body: null,
      predict: '默认 REST 注册集合下，状态码与 error 的形状是什么？',
      expect: '预期 400，error 是含 no handler found for uri 的字符串；没有进入业务 Handler。这依赖该模式未被额外插件注册；若结果不同，先检查端点、版本与插件。'
    },
    {
      id: 'ch06-02-single-segment', title: '路由 · 单段路径命中索引元数据接口',
      method: 'GET', path: '/tut-l06-no-such-index', body: null,
      predict: '确认此索引不存在后，它是路由 400 还是业务 404？',
      expect: '预期 404 + index_not_found_exception。GET /{index} 已注册，错误发生在索引元数据 Action。若同名索引已存在则返回 200；不要把一个已有资源当作缺失基线。'
    },
    {
      id: 'ch06-03-405', title: '路由 · DELETE /_cat/health 方法不匹配',
      method: 'DELETE', path: '/_cat/health', body: null,
      predict: '路径已注册但没有 DELETE，会返回什么？',
      expect: '预期 405 + Incorrect HTTP method，Allow 包含 GET。它不会删除索引。本卡显示状态与正文；完整响应头用正文中的 curl -i 查看，浏览器跨域可读头受 CORS 配置影响。'
    },
    {
      id: 'ch06-07-doc404', title: '结果 · 索引存在但文档不存在',
      method: 'GET', path: '/tut-l06-docs/_doc/missing-id', body: null,
      predict: '404 正文是 error 对象还是 found:false？',
      expect: '预期 404，正文含 _index、_id 和 found:false。这是成功完成 GET Action 后的缺失结果，由 RestGetAction 的 listener 选择 NOT_FOUND；若索引本身没建好，会变成另一种 404。'
    },
    {
      id: 'ch06-08-routes', title: '观测 · 按节点查看已记账路由模式',
      method: 'GET', path: '/_nodes/stats/http?filter_path=_nodes.failed,nodes.*.name,nodes.*.http.routes', body: null,
      predict: '统计键是具体 URL，还是 /{index}/_doc/{id} 这样的模式？',
      expect: '预期返回已产生请求或响应统计的路由模式；GET/HEAD 等共享同一路径的 tracker。它不是完整路由注册表，也不是本课专属统计。多个节点、其他客户端流量和节点重启会影响结果；核对节点名与 _nodes.failed。'
    },
    {
      id: 'ch06-04-pretty', title: '参数 · pretty 与 filter_path 控制输出',
      method: 'GET', path: '/tut-l06-docs/_doc/1?pretty&filter_path=_id,_source.title', body: null,
      predict: 'Handler 没有读取这两个键，为什么不会报未消费？',
      expect: '预期 200，仅保留 _id 与 _source.title。AbstractRestChannel 构造时已消费 format/filter_path/pretty/human；BaseRestHandler 的可选白名单也接受它们。filter_path 筛选响应结构，不修改字段 mapping。'
    },
    {
      id: 'ch06-05-typo', title: '参数 · realtimee 是未消费的拼写错误',
      method: 'GET', path: '/tut-l06-docs/_doc/1?realtimee=false', body: null,
      predict: '拼错的参数会被忽略还是拒绝？',
      expect: '预期 400，reason 含 unrecognized parameter: [realtimee] 与 realtime 的建议。prepareRequest 消费 realtime，未消费检查在 accept 前发现 realtimee。建议只在候选相似度足够时出现，不保证每个拼错的键都有建议。'
    },
    {
      id: 'ch06-06-fields', title: '参数 · fields 被 Handler 显式拒绝',
      method: 'GET', path: '/tut-l06-docs/_doc/1?fields=title', body: null,
      predict: '它与 realtimee 的 400 走同一检查吗？',
      expect: '预期 400，reason 含 the parameter [fields] is no longer supported。RestGetAction 读取 fields 后立即抛错，尚未返回 consumer；查看 _source 用下一卡，stored_fields 需要字段 mapping 明确 store:true。'
    },
    {
      id: 'ch06-06-source', title: '参数 · 用 _source 取代旧 fields 请求',
      method: 'GET', path: '/tut-l06-docs/_doc/1?_source=title', body: null,
      predict: '返回的 _source 只剩 title；原文档 views 会被删除吗？',
      expect: '预期 200、found:true、_source 只含 title；这是本次请求的返回过滤。再运行基线 GET，views:6 仍在。keyword 字段不因类型是 keyword 就自动支持 stored_fields。'
    },
    {
      id: 'ch06-07-head', title: '响应 · HEAD 已存在的文档',
      method: 'HEAD', path: '/tut-l06-docs/_doc/1', body: null,
      predict: '是否需要执行 GET Action，状态与正文是什么？',
      expect: '预期 200、正文为空。HEAD 与 GET 共用 RestGetAction/GetRequest，由 DefaultRestChannel 去掉响应体；空正文是正确结果，不是实验失败。常规非分块响应仍可报告表示长度，完整响应头用 curl -I 核对。'
    },
    {
      id: 'ch06-07-head404', title: '响应 · HEAD 缺失文档',
      method: 'HEAD', path: '/tut-l06-docs/_doc/missing-id', body: null,
      predict: 'HEAD 没有正文，能否判断文档缺失？',
      expect: '预期 404、正文为空；在索引存在、无权限/网络错误的本课条件下，可与 GET 的 found:false 对照。不能把任何 HEAD 404 都解释为文档缺失，例如索引不存在也可返回 404。'
    },
    {
      id: 'ch06-08-encoded-write', title: '编码 · 写入带斜杠的文档 ID',
      method: 'PUT', path: '/tut-l06-docs/_doc/http%3A%2F%2Fexample.test%2Fa?refresh=wait_for', body: { title: 'encoded-id', views: 6 },
      predict: '%2F 会变成额外路径段，导致找不到 Handler 吗？',
      expect: '直接连接 ES 时预期首次 created，重复为 updated，_id 为 http://example.test/a。路径匹配使用 rawPath，捕获后才解码；反向代理若提前解码或拒绝编码斜杠，会改变结果。'
    },
    {
      id: 'ch06-08-encoded-get', title: '编码 · GET 同一个编码 ID',
      method: 'GET', path: '/tut-l06-docs/_doc/http%3A%2F%2Fexample.test%2Fa', body: null,
      predict: '_id 是编码串还是解码后的 http://example.test/a？',
      expect: '直接连接 ES 时预期 200、found:true、_id 为 http://example.test/a，title 为 encoded-id。编码保持这整个 ID 作为一个路径段，避免在匹配前按解码后的斜杠拆分。'
    },
    {
      id: 'ch06-09-cleanup', title: '清理 · 点名删除本课索引',
      method: 'DELETE', path: '/tut-l06-docs', body: null,
      predict: '删除索引会清掉 HTTP 路由累计计数吗？',
      expect: '预期 acknowledged:true，删除 tut-l06-docs 及两篇本课文档，不删除其他索引。重复清理可返回 index_not_found_exception，说明资源已不存在。删除索引不清零节点路由统计；重做从显式创建卡开始。'
    }
  ];
  cards.forEach(function (card) {
    card.version = 1;
    window.ESEXPERIMENTS[card.id] = card;
  });
})();
