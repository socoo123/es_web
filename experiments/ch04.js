/* experiments/ch04.js — 第 4 课:实验 */
(function () {
  'use strict';
  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};

  window.ESEXPERIMENTS['ch04-01-loaded'] = {
    version: 1, id: 'ch04-01-loaded',
    title: '实验 1 · 这个节点把什么当 module 加载',
    method: 'GET', path: '/_nodes/plugins?filter_path=nodes.*.modules.name,nodes.*.plugins.name',
    predict: 'modules 数组里能找到 reindex 吗?plugins 数组是空的还是有东西?',
    expect: 'modules 里有一长串:reindex、lang-painless、transport-netty4、ingest-common、analysis-common…(随发行版打包);plugins 为空——你一个都没装。注意 _cat/plugins 只列 plugin,判断不了 module。'
  };
  window.ESEXPERIMENTS['ch04-02-reindex-400'] = {
    version: 1, id: 'ch04-02-reindex-400',
    title: '实验 2 · 空 body 打 /_reindex',
    method: 'POST', path: '/_reindex',
    body: {},
    predict: 'POST /_reindex 空 body,返回 404 还是 400?这个状态码说明什么?',
    expect: '400(validation_exception 之类)——路由在,只是 body 不合法。这条路由来自 modules/reindex 的 ActionPlugin.getRestHandlers,经 filterPlugins 交给 ActionModule。若删掉 modules/reindex 再启动:扫不到 bundle → 没有 handler → 404;而 GET /_search 在 server 里,不受影响。'
  };
})();
