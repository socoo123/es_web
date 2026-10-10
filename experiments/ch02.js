/* experiments/ch02.js — 第 2 课:实验(结构课,HTTP 侧只有版本/节点两面镜子) */
(function () {
  'use strict';
  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};

  window.ESEXPERIMENTS['ch02-01-version'] = {
    version: 1, id: 'ch02-01-version',
    title: '实验 1 · 核对正在运行的 ES 与 Lucene',
    method: 'GET', path: '/',
    predict: '先确认连接的节点。version.number 和 version.lucene_version 是否与本课源码版本相同?',
    expect: '本课基线为 ES 9.4.0 / Lucene 10.4.0。GET / 证明当前节点报告的运行版本；源码的 version.properties 则是构建版本依据，两者不能互相替代。若响应不同，先切换到 9.4.0 节点再对照本课。'
  };
  window.ESEXPERIMENTS['ch02-02-nodes'] = {
    version: 1, id: 'ch02-02-nodes',
    title: '实验 2 · 查看实际节点角色与 JVM',
    method: 'GET', path: '/_nodes?filter_path=nodes.*.roles,nodes.*.version,nodes.*.jvm.version,nodes.*.jvm.vm_version,nodes.*.jvm.using_bundled_jdk',
    predict: '先看 node.roles 是否被显式配置、是否使用捆绑 JDK，再预测返回的 roles 与 jvm.version。',
    expect: '未改 node.roles 的普通节点通常兼任 master、data、ingest、remote_cluster_client 等角色；显式配置或运行环境可能不同。捆绑 JDK 基线为 26.0.1+8，jvm.version 为 26.0.1；完整 JVM 版本看 vm_version，是否使用捆绑 JVM 看 using_bundled_jdk。自选 JVM 应以实际响应为准。'
  };
})();
