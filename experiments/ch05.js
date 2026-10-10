/* 第 5 课：专用单节点学习集群；persistent 更新须显式清理。 */
(function () {
  'use strict';
  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};

  window.ESEXPERIMENTS['ch05-00-setup'] = {
    version: 1, id: 'ch05-00-setup',
    title: 'B1 · 建索引 tut-l05-docs（1 主分片 / 1 副本）',
    method: 'PUT', path: '/tut-l05-docs',
    body: {
      settings: { number_of_shards: 1, number_of_replicas: 1, auto_expand_replicas: false },
      mappings: { dynamic: 'strict', properties: {} }
    },
    predict: '单个 data 节点能把副本分配到主分片所在节点吗？重复创建会怎样？',
    expect: '首次创建成功；1 个副本在单节点无法分配，本章索引可为 yellow。默认创建等待主分片，不必等副本；分别查看 acknowledged 与 shards_acknowledged。重复创建报 resource_already_exists_exception，先执行 B6 清理再建。'
  };
  window.ESEXPERIMENTS['ch05-01-default'] = {
    version: 1, id: 'ch05-01-default',
    title: 'A1 · 检查已有覆盖与回退值',
    method: 'GET', path: '/_cluster/settings?include_defaults=true&flat_settings=true&filter_path=**.cluster.max_shards_per_node',
    predict: 'transient、persistent 有没有同名 key？defaults 一定是代码默认吗？',
    expect: '本课前提：两层覆盖均无此 key，defaults.cluster.max_shards_per_node 为 "1000"。defaults 还可能含处理请求节点的本地配置。若已有覆盖或回退不同，先记录原值并调整恢复方案；不要把本课清理当成恢复任意环境。'
  };
  window.ESEXPERIMENTS['ch05-02-invalid'] = {
    version: 1, id: 'ch05-02-invalid',
    title: 'A2 · 非法值 0 在发布前被拒绝',
    method: 'PUT', path: '/_cluster/settings',
    body: { persistent: { 'cluster.max_shards_per_node': 0 } },
    predict: '默认 1000、最小值 1；0 会先进入有效集群状态吗？',
    expect: '预期 HTTP 400，reason 指向 cluster.max_shards_per_node 且要求 >= 1；本次非法更新不会成功发布。修正为下一张卡的 2000 后继续。此前若已有合法覆盖，它不会被此失败更新替换。'
  };
  window.ESEXPERIMENTS['ch05-02-put'] = {
    version: 1, id: 'ch05-02-put',
    title: 'A3 · persistent 更新为 2000',
    method: 'PUT', path: '/_cluster/settings',
    body: { persistent: { 'cluster.max_shards_per_node': 2000 } },
    predict: '更新会改节点的 yml 文件吗？这个值能跨完整集群重启保存吗？',
    expect: '正常学习节点预期 acknowledged: true、persistent 回显 "2000"。更新进入持久化集群元数据，节点通过消费者应用，不改写 yml。图 2 省略确认超时与 reroute；acknowledged 不是所有业务后果已完成的通用保证。'
  };
  window.ESEXPERIMENTS['ch05-03-after'] = {
    version: 1, id: 'ch05-03-after',
    title: 'A4 · 读回集群覆盖层',
    method: 'GET', path: '/_cluster/settings?flat_settings=true&filter_path=**.cluster.max_shards_per_node',
    predict: '2000 出现在哪层？若同时有 transient，谁优先？',
    expect: '本课预期 persistent.cluster.max_shards_per_node = "2000"，transient 没有同名 key。若有 transient，它仍优先于 persistent；API 分层回显不是合并后的单一最终值，也不能证明所有业务线程瞬间切换。'
  };
  window.ESEXPERIMENTS['ch05-04-final'] = {
    version: 1, id: 'ch05-04-final',
    title: 'B2 · Final 拒绝直接改主分片数',
    method: 'PUT', path: '/tut-l05-docs/_settings',
    body: { 'index.number_of_shards': 5 },
    predict: '请求被拒后，原来的主分片数会变化吗？',
    expect: '预期 HTTP 400，reason 包含 final、index.number_of_shards 与 not updateable。设置仍为 1，已有路由不因失败而改变；Final 在关闭索引后也拒绝。不同布局可按条件使用 resize 或 reindex 到新索引。'
  };
  window.ESEXPERIMENTS['ch05-05-replicas'] = {
    version: 1, id: 'ch05-05-replicas',
    title: 'B3 · Dynamic 把副本数改为 0',
    method: 'PUT', path: '/tut-l05-docs/_settings',
    body: { 'index.number_of_replicas': 0 },
    predict: '同一个 _settings 端点为什么这次允许更新？',
    expect: '正常学习节点预期 acknowledged: true。number_of_replicas 为 Dynamic + IndexScope，可在开放索引在线更新；主分片数仍是 1。之后先读回设置，再对本章索引等待 green，不据此承诺整个集群变绿。'
  };
  window.ESEXPERIMENTS['ch05-05-verify'] = {
    version: 1, id: 'ch05-05-verify',
    title: 'B4 · 对照读回两个索引设置',
    method: 'GET', path: '/tut-l05-docs/_settings?flat_settings=true&filter_path=**.index.number_of_shards,**.index.number_of_replicas',
    predict: 'Final 的失败和 Dynamic 的成功，分别留下什么值？',
    expect: 'tut-l05-docs.settings 中 index.number_of_shards = "1"、index.number_of_replicas = "0"。主分片更新没有部分生效；副本更新确已写入索引设置。'
  };
  window.ESEXPERIMENTS['ch05-05-health'] = {
    version: 1, id: 'ch05-05-health',
    title: 'B5 · 等待本章索引 green（最多等待 10s）',
    method: 'GET', path: '/_cluster/health/tut-l05-docs?wait_for_status=green&timeout=10s',
    predict: '没有副本后，还要看哪些字段才能确认主分片已分配？',
    expect: '本课正常单节点预期 timed_out: false、status: "green"、active_primary_shards: 1、unassigned_shards: 0。若超时，检查本章索引的主分片分配与节点条件，不反复盲改设置；其他索引不决定这个限定索引的健康结果。'
  };
  window.ESEXPERIMENTS['ch05-06-reset'] = {
    version: 1, id: 'ch05-06-reset',
    title: 'A5 · null 删除本课 persistent 覆盖',
    method: 'PUT', path: '/_cluster/settings',
    body: { persistent: { 'cluster.max_shards_per_node': null } },
    predict: 'null 表示数值归零，还是移除这一层的 key？',
    expect: '移除 persistent 层的同名 key；正常节点预期 acknowledged: true。只在本课无其他覆盖的前提下回退为 1000。若原来有 persistent 值，须恢复记录的原值；如果存在 transient 或本地覆盖，null 不会把它们一起删掉。'
  };
  window.ESEXPERIMENTS['ch05-06-verify'] = {
    version: 1, id: 'ch05-06-verify',
    title: 'A6 · 清理后重新检查回退',
    method: 'GET', path: '/_cluster/settings?include_defaults=true&flat_settings=true&filter_path=**.cluster.max_shards_per_node',
    predict: '清理后响应应怎样与 A1 对照？',
    expect: '本课前提下，两层覆盖均无同名 key，defaults 回到 "1000"，与 A1 一致。若恢复的是环境原有值，则按原记录对照。清理本课 key 不清空整个 persistent 对象。'
  };
  window.ESEXPERIMENTS['ch05-07-cleanup'] = {
    version: 1, id: 'ch05-07-cleanup',
    title: 'B6 · 显式删除 tut-l05-docs',
    method: 'DELETE', path: '/tut-l05-docs',
    predict: '哪些资源会被删除？重复清理会怎样？',
    expect: '首次预期 acknowledged: true，只删除 tut-l05-docs 及其索引设置 / 数据，不删除其他索引。重复删除不存在目标通常回 404；确认目标不存在即可。重做先完成 A5 / A6 与本卡，再从 A1 / B1 开始。'
  };
})();
