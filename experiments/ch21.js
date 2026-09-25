/* experiments/ch21.js — 第 21 课:集群状态实验 */
(function () {
  'use strict';

  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};

  window.ESEXPERIMENTS['ch21-00-setup'] = {
    version: 1, id: 'ch21-00-setup',
    title: '实验 0 · 建 tut-l21-docs(1 主 0 副)',
    method: 'PUT', path: '/tut-l21-docs',
    body: {
      settings: { number_of_shards: 1, number_of_replicas: 0 },
      mappings: { properties: { title: { type: 'keyword' } } }
    },
    predict: '建索引这件事,会动 ClusterState 的哪几块?',
    expect: 'acknowledged: true。建索引 = Master 提交一次新 ClusterState:Metadata 多一个索引定义,RoutingTable 多一行分片放置。shards/replicas 这些设置从此躺在 metadata.indices.tut-l21-docs.settings 里。'
  };

  window.ESEXPERIMENTS['ch21-01-metrics-no-version'] = {
    version: 1, id: 'ch21-01-metrics-no-version',
    title: '实验 1 · 只点名 metadata,routing_table',
    method: 'GET',
    path: '/_cluster/state/metadata,routing_table?filter_path=cluster_uuid,cluster_name,version,state_uuid,master_node,metadata.indices.tut-l21-docs.settings.index.number_of_shards,metadata.indices.tut-l21-docs.settings.index.number_of_replicas,metadata.indices.tut-l21-docs.mappings,routing_table.indices.tut-l21-docs.shards',
    body: null,
    predict: 'filter_path 里写了 version、state_uuid、master_node——它们会出现吗?number_of_shards 在 metadata 还是 routing_table?',
    expect: 'version / state_uuid / master_node 三个都缺席:toXContentChunked 只在 metric 含 version 时写 version、state_uuid,含 master_node 时写 master_node——filter_path 裁剪的是已经写出的 JSON,变不出没序列化的字段。cluster_uuid 在(header 无条件写)。number_of_shards=1 在 metadata(套了 index 这一层);分片放置在 routing_table:shards["0"] 数组里 state=STARTED、primary=true、node=<本机 id>。'
  };

  window.ESEXPERIMENTS['ch21-02-metrics-with-version'] = {
    version: 1, id: 'ch21-02-metrics-with-version',
    title: '实验 2 · 把 version、master_node 加进 metric',
    method: 'GET',
    path: '/_cluster/state/version,metadata,routing_table,master_node?filter_path=version,state_uuid,master_node,metadata.indices.tut-l21-docs.settings.index.number_of_shards,routing_table.indices.tut-l21-docs.shards',
    body: null,
    predict: '同一批 filter_path,这次顶层三件套会出现吗?',
    expect: '出现:version(一个不小的整数)、state_uuid(随机串)、master_node(node id)。对比实验 1——变的是 URL 里的 metric 列表,不是 filter_path。「metric 决定写不写,filter_path 决定留不留」就是这两跑的全部差别。'
  };

  window.ESEXPERIMENTS['ch21-03-master-node'] = {
    version: 1, id: 'ch21-03-master-node',
    title: '实验 3 · master_node:最省的 metric',
    method: 'GET',
    path: '/_cluster/state/master_node?filter_path=master_node,cluster_uuid',
    body: null,
    predict: '只想知道谁是 Master,有没有比拉 nodes map 更省的路?',
    expect: '只回 master_node 和 cluster_uuid——master_node 是独立 metric,不必拖整份 nodes。DiscoveryNodes 里存的是 masterNodeId 指针;单节点集群它就是本机 id,和实验 2 看到的一致。'
  };

  window.ESEXPERIMENTS['ch21-04-blocks-empty'] = {
    version: 1, id: 'ch21-04-blocks-empty',
    title: '实验 4 · blocks:空对象也是证据',
    method: 'GET',
    path: '/_cluster/state/blocks',
    body: null,
    predict: '健康集群的 blocks 长什么样?',
    expect: 'blocks: {} ——空也是证据:没有集群级/索引级阻断。磁盘水位超限、cluster.blocks.read_only、恢复未完成都会在这里出现条目。第 5 课的动态设置一旦把集群推成只读,这张表立刻非空。'
  };

  window.ESEXPERIMENTS['ch21-05-term-in-metadata'] = {
    version: 1, id: 'ch21-05-term-in-metadata',
    title: '实验 5 · term 住在 Metadata 里',
    method: 'GET',
    path: '/_cluster/state/metadata?filter_path=metadata.cluster_coordination.term,metadata.cluster_coordination.config',
    body: null,
    predict: 'term 是 ClusterState 的顶层字段吗?',
    expect: 'term=1,藏在 metadata.cluster_coordination 里——term() 只是转调 coordinationMetadata().term(),它不是 ClusterState 的字段。config 是投票配置(单节点集群一行)。term 每次 Master 换届加一,第 22 课的主角。'
  };

  window.ESEXPERIMENTS['ch21-06-pending-tasks'] = {
    version: 1, id: 'ch21-06-pending-tasks',
    title: '实验 6 · pending_tasks:还没算的队列',
    method: 'GET',
    path: '/_cluster/pending_tasks',
    body: null,
    predict: '空闲集群上它返回什么?它统计的是「历史更新次数」吗?',
    expect: 'tasks: []。它列的是 Master 优先级队列里还没算的批——空闲就是空数组,不是坏了。要警惕的反而是持续非空:状态更新堵了,insertOrder/timeInQueue 会一直涨。'
  };

  window.ESEXPERIMENTS['ch21-07-v1'] = {
    version: 1, id: 'ch21-07-v1',
    title: '实验 7 · 记下 V1(version + state_uuid)',
    method: 'GET',
    path: '/_cluster/state/version?filter_path=version,state_uuid,cluster_uuid',
    body: null,
    predict: '记下这两个值(下面三跑要用):version 是多少?state_uuid 长什么样?',
    expect: 'version 是一个整数,state_uuid 是一串随机 Base64。注意响应里还有 cluster_uuid——它在 header chunk 里无条件写出,不受 metric 控制(和实验 1 印证)。把 V1 和 uuid 抄下来。'
  };

  window.ESEXPERIMENTS['ch21-08-create-index'] = {
    version: 1, id: 'ch21-08-create-index',
    title: '实验 8 · 建一个新索引 tut-l21-ver',
    method: 'PUT', path: '/tut-l21-ver',
    body: { settings: { number_of_shards: 1, number_of_replicas: 0 } },
    predict: '这次 PUT 会让 version +1、+好几还是不变?state_uuid 会换吗?',
    expect: 'acknowledged: true。这是一次货真价实的 Master 状态更新(Metadata + RoutingTable 都变)——下一跑对照。'
  };

  window.ESEXPERIMENTS['ch21-09-v2'] = {
    version: 1, id: 'ch21-09-v2',
    title: '实验 9 · V2:version 加一,UUID 换新',
    method: 'GET',
    path: '/_cluster/state/version?filter_path=version,state_uuid',
    body: null,
    predict: '对照实验 7 抄下的 V1:version 动了没有?state_uuid 是同一个串吗?',
    expect: 'version 比 V1 大(通常正好 +1;若期间还有别的集群任务会跳更多,但方向一定变大),state_uuid 换成了完全不同的串——incrementVersion 把 UUID 打回 _na_,build() 再随机生成,不是在旧串上改字符。手动对照:V2.version - V1.version ≥ 1,uuid ≠ uuid。'
  };

  window.ESEXPERIMENTS['ch21-10-write-doc'] = {
    version: 1, id: 'ch21-10-write-doc',
    title: '实验 10 · 写一篇 mapping 已声明的文档',
    method: 'PUT', path: '/tut-l21-docs/_doc/1?refresh=true',
    body: { title: 'cluster-state-is-a-snapshot' },
    predict: '写入走的是数据平面还是元数据平面?version 会涨吗?',
    expect: 'created / _shards.success=1。title 是 keyword、mapping 已声明,不触发动态映射——这次写入只走 Engine/Translog(第 10、14 课),不提交新的 ClusterState。'
  };

  window.ESEXPERIMENTS['ch21-11-v3'] = {
    version: 1, id: 'ch21-11-v3',
    title: '实验 11 · V3:写文档不涨 version',
    method: 'GET',
    path: '/_cluster/state/version?filter_path=version,state_uuid',
    body: null,
    predict: 'V3 和实验 9 的 V2 什么关系?',
    expect: 'V3 = V2:version、state_uuid 都没动。文档数据平面和集群元数据平面是两条路——「每写一篇文档 version +1」是把两个平面当成同一块黑板。若你的集群恰好跑了 ILM 之类后台任务偶发 +1,看 state_uuid 是否也换了:换了才是又一次状态更新,和这篇文档无关。'
  };

  window.ESEXPERIMENTS['ch21-12-settings'] = {
    version: 1, id: 'ch21-12-settings',
    title: '实验 12 · 改集群设置(第 5 课回马枪)',
    method: 'PUT', path: '/_cluster/settings',
    body: { persistent: { 'cluster.max_shards_per_node': 1200 } },
    predict: '第 5 课说动态设置改的是 ClusterState 里的 Metadata——这次 PUT 会不会又是一次状态更新?',
    expect: 'acknowledged: true,设置进了 metadata.persistent_settings。这是又一次 Master 状态更新:下一跑同时看两套计数器。'
  };

  window.ESEXPERIMENTS['ch21-13-two-counters'] = {
    version: 1, id: 'ch21-13-two-counters',
    title: '实验 13 · 两套计数器并排',
    method: 'GET',
    path: '/_cluster/state/version,metadata?filter_path=version,state_uuid,metadata.version',
    body: null,
    predict: '顶层 version 和 metadata.version 各是多少?谁加得快?',
    expect: '顶层 version 比实验 11 又大了(设置更新 +1);metadata.version 也在,但它只统计 Metadata 变了的批次——比顶层小(patchVersions 只在 metadata 对象身份变了时才 withIncrementedVersion)。两个数字不相等正是「两套计数器」的证据;wait_for_metadata_version 等的是后者。'
  };

  window.ESEXPERIMENTS['ch21-14-cleanup-docs'] = {
    version: 1, id: 'ch21-14-cleanup-docs',
    title: '清理 · 删 tut-l21-docs',
    method: 'DELETE', path: '/tut-l21-docs',
    predict: '删索引算不算一次状态更新?',
    expect: 'acknowledged: true——而且它自己就是又一次 N→N+1(Metadata 和 RoutingTable 都要改)。删完再看一眼 version metric,数字应该又大了一号。'
  };

  window.ESEXPERIMENTS['ch21-15-cleanup-ver'] = {
    version: 1, id: 'ch21-15-cleanup-ver',
    title: '清理 · 删 tut-l21-ver(顺手还原设置)',
    method: 'DELETE', path: '/tut-l21-ver',
    predict: '一句话总结本课?',
    expect: 'acknowledged: true。想还原实验 12 的设置:PUT /_cluster/settings 把 cluster.max_shards_per_node 置 null(注意:那又是一次状态更新、version 又 +1)。快照不可变、version 只在 Master 手里加一、算和应用各一条队列。'
  };
})();
