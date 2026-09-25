/* experiments/ch06.js — 第 6 课:REST 入口层的可观察行为(单节点、xpack 安全关闭、免认证) */
(function () {
  'use strict';
  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};

  window.ESEXPERIMENTS['ch06-00-setup'] = {
    version: 1, id: 'ch06-00-setup',
    title: '实验 0 · 建索引并写入一篇文档',
    method: 'PUT', path: '/tut-l06-docs/_doc/1',
    body: { title: 'rest-layer', views: 6 },
    predict: '先猜:索引还不存在,这次 PUT 会因为「没有索引」报错吗?result 字段会是什么?',
    expect: 'result: created——索引不存在就自动建(动态映射)。REST 层只负责把 PUT /{index}/_doc/{id} 路由到对应 Action 并造出 IndexRequest,「索引在不在」是 Action 层之后才检查的事,入口层不拦。'
  };
  window.ESEXPERIMENTS['ch06-01-nohandler'] = {
    version: 1, id: 'ch06-01-nohandler',
    title: '实验 1 · 多段未注册路径:400 而不是 404',
    method: 'GET', path: '/_this_path_is_not_registered/at/all',
    body: null,
    predict: '先猜:状态码是 404 还是 400?响应是标准的 error.root_cause 对象,还是一条扁平的 error 字符串?',
    expect: '400,正文是 {"error":"no handler found for uri [...] and method [GET]"}——PathTrie 四种匹配模式全落空,RestController.handleBadRequest 直接回话。注意它不是标准错误对象:请求根本没进任何 Handler。猜 404 的人把「HTTP 资源不存在」和「路由表没有这个模式」混成了同一件事。'
  };
  window.ESEXPERIMENTS['ch06-02-single-segment'] = {
    version: 1, id: 'ch06-02-single-segment',
    title: '实验 2 · 对照:单段路径会命中 GET /{index}',
    method: 'GET', path: '/tut-l06-no-such-index',
    body: null,
    predict: '先猜:单段路径也会是 no handler found 吗?错误 type 会是什么?',
    expect: '不是。/{index} 是注册过的模式(RestGetIndicesAction 的 GET /{index}),tut-l06-no-such-index 走通配进了 Handler,返回 404 + index_not_found_exception 的标准错误对象——失败发生在业务层。排障口诀:扁平 error 字符串 = 路由没接住;结构化 error.type = 路由接住了、后面出的错。'
  };
  window.ESEXPERIMENTS['ch06-03-405'] = {
    version: 1, id: 'ch06-03-405',
    title: '实验 3 · Method 不对:405,Allow 头点名合法方法',
    method: 'DELETE', path: '/_cat/health',
    body: null,
    predict: '先猜:对 /_cat/health 发 DELETE,状态码是多少?浏览器跨域预检的 OPTIONS 又会得到什么?',
    expect: '405:路径命中了,但 MethodHandlers 里没有 DELETE,handleUnsupportedHttpMethod 把合法方法写进 Allow: GET(curl -D - 可见)。OPTIONS 对同一路径会得 200 + Allow,由 RestController 内部处理、不许注册。405 与 400 的分工:前者「路径对、动词错」,后者「整条路由没接住」。'
  };
  window.ESEXPERIMENTS['ch06-04-pretty'] = {
    version: 1, id: 'ch06-04-pretty',
    title: '实验 4 · 全局参数:pretty 与 filter_path 不归 Handler 管',
    method: 'GET', path: '/tut-l06-docs/_doc/1?pretty&filter_path=_id,_source.title',
    body: null,
    predict: '先猜:?pretty、?filter_path 从没在 RestGetAction 里被 param() 读过,它们会触发未消费参数的 400 吗?',
    expect: '200。format / filter_path / pretty / human 在 BaseRestHandler.ALWAYS_SUPPORTED 里,所有 Handler 自动放行;filter_path 在响应写出阶段处理,输出只剩 _id 和 _source.title。RestGetAction 不需要认识它们——这就是「全局参数」与「接口自己的参数」的分界线。'
  };
  window.ESEXPERIMENTS['ch06-05-typo'] = {
    version: 1, id: 'ch06-05-typo',
    title: '实验 5 · 拼错参数:400 + did you mean',
    method: 'GET', path: '/tut-l06-docs/_doc/1?realtimee=false',
    body: null,
    predict: '先猜:多打一个 e 的 realtimee 会被静默忽略,还是 400?报错里会带建议吗?',
    expect: '400,标准错误对象:request [...] contains unrecognized parameter: [realtimee] -> did you mean [realtime]?。机制:param(key) 每取一次值就记进 consumedParams;prepareRequest 读过 realtime、从没读 realtimee,BaseRestHandler 检查 unconsumedParams,再用 Levenshtein(阈值 >0.5)从候选里挑最近的——拼错永远不会被静默吞掉。'
  };
  window.ESEXPERIMENTS['ch06-06-fields'] = {
    version: 1, id: 'ch06-06-fields',
    title: '实验 6 · 对照:旧参数 fields 是显式拒绝,不是拼写建议',
    method: 'GET', path: '/tut-l06-docs/_doc/1?fields=title',
    body: null,
    predict: '先猜:同样返回 400,这次的报错和实验 5 一样吗?',
    expect: '不一样:the parameter [fields] is no longer supported, please use [stored_fields] or [_source]。fields 在 RestGetAction.prepareRequest 里被 param("fields") 消费后立刻 throw——参数是「已消费」的,不走未消费检查,是 Handler 主动拒绝 7.x 旧参数。两类 400,机制完全不同。'
  };
  window.ESEXPERIMENTS['ch06-07-doc404'] = {
    version: 1, id: 'ch06-07-doc404',
    title: '实验 7 · 文档不存在:Handler 决定的 404',
    method: 'GET', path: '/tut-l06-docs/_doc/missing-id',
    body: null,
    predict: '先猜:状态码?body 里的 found 是什么?和实验 1 那个 400 长得像吗?',
    expect: '404 + {"_index":…,"found":false}。路由命中、Action 也执行了,状态码是 RestGetAction 返回的监听器里 r -> r.isExists() ? OK : NOT_FOUND 选的——业务结果,不是路由错误。三种失败就此凑齐:400 路由没接住、405 动词不对、404 资源没有。'
  };
  window.ESEXPERIMENTS['ch06-08-routes'] = {
    version: 1, id: 'ch06-08-routes',
    title: '实验 8 · 从 _nodes/stats/http 看见 PathTrie 上的模式',
    method: 'GET', path: '/_nodes/stats/http?filter_path=nodes.*.http.routes',
    body: null,
    predict: '先猜:routes 的键是你打过的完整 URL(tut-l06-docs/_doc/1),还是 /{index}/_doc/{id} 这样的路由模式?',
    expect: '是模式:/{index}/_doc/{id}、/{index}、/_cluster/health 这类 key——统计挂在 PathTrie 节点的 MethodHandlers(statsTracker)上,请求按模式归账;没有流量的模式不出现(getStats 只输出计数 >0 的项)。这一眼等于把那棵路由树拍平了给你看。'
  };
  window.ESEXPERIMENTS['ch06-09-cleanup'] = {
    version: 1, id: 'ch06-09-cleanup',
    title: '清理 · 删除实验索引',
    method: 'DELETE', path: '/tut-l06-docs',
    body: null,
    predict: '先猜:索引删掉之后,实验 8 里 /{index}/_doc/{id} 的计数会清零吗?',
    expect: 'acknowledged: true。计数不清零——那是进程内累计统计,索引没了,路由模式还挂在树上。想清零只能重启节点。'
  };
})();
