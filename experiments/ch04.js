/* experiments/ch04.js — 第 4 课:实验 */
(function () {
  'use strict';
  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};

  window.ESEXPERIMENTS['ch04-01-loaded'] = {
    version: 1, id: 'ch04-01-loaded',
    title: '实验 1 · 按节点区分 modules 与 plugins',
    method: 'GET', path: '/_nodes/plugins?filter_path=_nodes,nodes.*.name,nodes.*.modules.name,nodes.*.plugins.name',
    predict: '先核对节点名称与失败数量：modules 是否包含 reindex？plugins 是否为空由安装状态决定吗？',
    expect: '标准发行版通常在 modules 中包含 reindex、lang-painless、analysis-common 等；plugins 取决于各节点安装状态，不保证为空。逐节点核对；_cat/plugins 不列 modules。401/403 或节点失败不能当作缺少插件。此请求只读，可重复，无需清理。'
  };
  window.ESEXPERIMENTS['ch04-02-reindex-400'] = {
    version: 1, id: 'ch04-02-reindex-400',
    title: '实验 2 · 用空对象检查 Reindex 参数验证',
    method: 'POST', path: '/_reindex',
    body: {},
    predict: '保留 {}：正常加载并获准访问时，会出现哪种验证错误？单看 400 能证明命中 Reindex 吗？',
    expect: 'Reindex 处理器收到 {} 后，因源索引上下文与目标索引缺失，预期 400 action_request_validation_exception；核对 reason（如 index must be specified）。无 handler 也可返回 400，所以结合实验 1 与错误正文判断。权限失败另查认证；本请求不执行有效 reindex，不创建资源，可重复，无需清理。'
  };
})();
