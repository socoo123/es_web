/* experiments/ch02.js — 第 2 课:实验(结构课,HTTP 侧只有版本/节点两面镜子) */
(function () {
  'use strict';
  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};

  window.ESEXPERIMENTS['ch02-01-version'] = {
    version: 1, id: 'ch02-01-version',
    title: '实验 1 · 版本核对:version.properties 的活证据',
    method: 'GET', path: '/',
    predict: '这个节点会报什么版本?version.number 和 version.lucene_version 各是多少?',
    expect: '9.4.0 / 10.4.0——正是 v9.4.0 tag 的 version.properties 钉死的两个数(lucene = 10.4.0)。教程里所有「线程池多大、队列多长」都以这组版本为准,不是网上旧文档。'
  };
  window.ESEXPERIMENTS['ch02-02-nodes'] = {
    version: 1, id: 'ch02-02-nodes',
    title: '实验 2 · 节点角色与捆绑 JDK',
    method: 'GET', path: '/_nodes?filter_path=nodes.*.roles,nodes.*.version,nodes.*.jvm.version',
    predict: 'docker 单节点:roles 里会有哪些角色?jvm 版本是多少?',
    expect: 'roles 含 master、data、ingest、remote_cluster_client 等——一个进程多角色(第 1 课「节点可兼职」的实证);jvm.version 为 26.0.1,对应发行版捆绑的 JDK 26.0.1+8(version.properties 的 bundled_jdk,API 不带回 +8 构建号)。'
  };
})();
