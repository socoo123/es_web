/* experiments/ch05.js — 第 5 课:实验(全程 transient,重启即还原) */
(function () {
  'use strict';
  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};

  window.ESEXPERIMENTS['ch05-00-setup'] = {
    version: 1, id: 'ch05-00-setup',
    title: '实验 0 · 建索引 tut-l05-docs(1 分片 1 副本)',
    method: 'PUT', path: '/tut-l05-docs',
    body: { settings: { number_of_shards: 1, number_of_replicas: 1 } },
    predict: '副本 1 在单节点上会怎样?(回忆第 1 课)',
    expect: '索引创建成功;副本 UNASSIGNED、集群 yellow——不影响本课,我们要的是把它当 Dynamic 设置的实验品。'
  };
  window.ESEXPERIMENTS['ch05-01-default'] = {
    version: 1, id: 'ch05-01-default',
    title: '实验 1 · 改前:看默认值(带 include_defaults)',
    method: 'GET', path: '/_cluster/settings?include_defaults=true&flat_settings=true&filter_path=**.cluster.max_shards_per_node',
    predict: '默认值是多少?它会出现在 transient、persistent 还是 defaults 里?',
    expect: 'defaults.cluster.max_shards_per_node = "1000",transient/persistent 都没有——这就是「还没人盖过 yml 和代码默认」。'
  };
  window.ESEXPERIMENTS['ch05-02-put'] = {
    version: 1, id: 'ch05-02-put',
    title: '实验 2 · transient 改成 2000',
    method: 'PUT', path: '/_cluster/settings',
    body: { transient: { 'cluster.max_shards_per_node': 2000 } },
    predict: 'acknowledged 会是 true 吗?这个值写到哪去了?',
    expect: 'acknowledged: true,transient 里回显 2000。走的是图 2:Master 写进 ClusterState 的 Metadata,各节点 applySettings 后 listener 把限额字段改成 2000——没有任何节点去改 yml。'
  };
  window.ESEXPERIMENTS['ch05-03-after'] = {
    version: 1, id: 'ch05-03-after',
    title: '实验 3 · 改后:看生效值(不带 include_defaults)',
    method: 'GET', path: '/_cluster/settings?flat_settings=true&filter_path=**.cluster.max_shards_per_node',
    predict: '这次值出现在哪一层?',
    expect: 'transient.cluster.max_shards_per_node = "2000",persistent 为空。「集群设置」和「重启后还在」是两回事:transient 重启就丢。'
  };
  window.ESEXPERIMENTS['ch05-04-final'] = {
    version: 1, id: 'ch05-04-final',
    title: '实验 4 · 踩 Final 的墙:改主分片数',
    method: 'PUT', path: '/tut-l05-docs/_settings',
    body: { 'index.number_of_shards': 5 },
    predict: '状态码 400 还是 200?报错文案会提到什么词?',
    expect: '400:final index setting [index.number_of_shards], not updateable——直接对应 Property.Final(不是旧文档那句 can not change the number of shards)。原因在第 1 课:它是路由哈希的除数。'
  };
  window.ESEXPERIMENTS['ch05-05-replicas'] = {
    version: 1, id: 'ch05-05-replicas',
    title: '实验 5 · 对照:副本数是 Dynamic,能改',
    method: 'PUT', path: '/tut-l05-docs/_settings',
    body: { 'index.number_of_replicas': 0 },
    predict: '同一个 _settings 端点,副本数能改吗?',
    expect: 'acknowledged: true。number_of_replicas 声明是 Dynamic + IndexScope,所以在线可改;顺带把单节点的 yellow 治好了。'
  };
  window.ESEXPERIMENTS['ch05-06-reset'] = {
    version: 1, id: 'ch05-06-reset',
    title: '清理 1 · transient 置 null(还原限额)',
    method: 'PUT', path: '/_cluster/settings',
    body: { transient: { 'cluster.max_shards_per_node': null } },
    predict: 'null 在这里是什么意思?',
    expect: '「删除这层覆盖」,回到代码默认 1000。transient 里不再有这个 key。'
  };
  window.ESEXPERIMENTS['ch05-07-cleanup'] = {
    version: 1, id: 'ch05-07-cleanup',
    title: '清理 2 · 删除实验索引',
    method: 'DELETE', path: '/tut-l05-docs',
    predict: '删除后 replica 设置也一起没了?',
    expect: 'acknowledged: true。索引级设置随索引删除;集群级 transient 已在上一步还原。'
  };
})();
