/* experiments/ch09.js — 第 9 课:传输层(单节点即可完成;观察两个端口与传输计数) */
(function () {
  'use strict';
  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};

  window.ESEXPERIMENTS['ch09-00-setup'] = {
    version: 1, id: 'ch09-00-setup',
    title: '实验 0 · 建索引 tut-l09-docs(1 分片 0 副本)',
    method: 'PUT', path: '/tut-l09-docs',
    body: { settings: { number_of_shards: 1, number_of_replicas: 0 } },
    predict: '先猜:副本给 1 的话,单节点集群健康色会是什么?本课为什么要一个「干净的单分片」?',
    expect: '索引创建成功(1 副本会 yellow,副本无处安放)。这一课只跟踪一次 GET 的走向,不想让分片状态抢戏;后面几个实验都在这个索引上观察传输层。'
  };
  window.ESEXPERIMENTS['ch09-01-ports'] = {
    version: 1, id: 'ch09-01-ports',
    title: '实验 1 · 一个节点两个端口:port 列是哪一个',
    method: 'GET', path: '/_cat/nodes?v&h=name,port,http_address,id',
    predict: '先猜:port 列会打印 9200 还是别的数?http_address 和它一样吗?',
    expect: 'port = 9300,http_address 才是 9200。port 列的文档定义就是 bound transport port:节点间二进制帧的 TCP 口(transport.port 默认范围 9300-9399)。单节点上传输层同样存在,只是很少被用到 —— 这就是它在 HTTP 之外的第二个监听。'
  };
  window.ESEXPERIMENTS['ch09-02-no-cat'] = {
    version: 1, id: 'ch09-02-no-cat',
    title: '实验 2 · 负面对照:并不存在的 _cat/transport',
    method: 'GET', path: '/_cat/transport',
    predict: '先猜:这张 cat 表存在吗?状态码是 200、404,还是别的?',
    expect: '400:no handler found for uri [/_cat/transport] and method [GET]。ES 对完全不认识的路径回 400(REST 层惯例),不是 404。传输层没有 cat 表:看地址用 _nodes/transport 或实验 1 的 port 列;看收发计数用实验 4 的 _nodes/stats/transport。'
  };
  window.ESEXPERIMENTS['ch09-03-doc'] = {
    version: 1, id: 'ch09-03-doc',
    title: '实验 3 · 写一篇文档(给实验 4 当输入)',
    method: 'PUT', path: '/tut-l09-docs/_doc/1?refresh=true',
    body: { title: 'transport-frame' },
    predict: '先猜:这次写入会经过传输层吗?_nodes/stats/transport 的 tx_count 会因为它 +1 吗?',
    expect: '写入成功,_version = 1。分片在本节点,写路径同样不出节点、不产生传输层计数。这一步只是给下一实验准备一个可以 GET 的 _id;先记住此刻计数全是 0。'
  };
  window.ESEXPERIMENTS['ch09-04-stats'] = {
    version: 1, id: 'ch09-04-stats',
    title: '实验 4 · GET 之后再看:传输计数仍然全 0',
    method: 'GET',
    path: '/_nodes/stats/transport?filter_path=nodes.*.name,nodes.*.transport.server_open,nodes.*.transport.total_outbound_connections,nodes.*.transport.rx_count,nodes.*.transport.tx_count',
    predict: '先去控制台 GET /tut-l09-docs/_doc/1,再回来运行本实验。猜:rx_count / tx_count 涨了吗?total_outbound_connections 更接近 0 还是 13?',
    expect: '全是 0。shard 在本节点,TransportService.getConnection 返回 localNodeConnection,sendLocalRequest 在同一个 JVM 里直接调 handler:不走 writeTo、不过 TCP,计数自然不动。13 是「连远端时按画像一次建满」的上限(见实验 5),不是启动就连自己 13 条。推论:序列化错位这类 bug,单节点测试永远抓不到。'
  };
  window.ESEXPERIMENTS['ch09-05-defaults'] = {
    version: 1, id: 'ch09-05-defaults',
    title: '实验 5 · 连接画像与压缩的默认值(对照正文 § 6 表)',
    method: 'GET',
    path: '/_cluster/settings?include_defaults=true&flat_settings=true&filter_path=**.transport.connections_per_node.recovery,**.transport.connections_per_node.bulk,**.transport.connections_per_node.reg,**.transport.connections_per_node.state,**.transport.connections_per_node.ping,**.transport.compress,**.transport.compression_scheme,**.transport.ping_schedule,**.transport.port',
    predict: '先猜:对同一个远端节点,recovery / bulk / reg / state / ping 各默认几条?compress 是 true / false 还是某个枚举名?',
    expect: 'defaults 里:recovery = 2、bulk = 3、reg = 6、state = 1、ping = 1 —— master+data 节点对一个对端的出站上限 2+3+6+1+1 = 13(非数据节点 recovery 为 0,非 master-eligible 节点 state 为 0)。compress = INDEXING_DATA(有索引数据才压),compression_scheme = LZ4,ping_schedule = -1(不按点发 keep-alive),port = 9300-9399。这些全是 NodeScope,启动时钉死。'
  };
  window.ESEXPERIMENTS['ch09-06-cleanup'] = {
    version: 1, id: 'ch09-06-cleanup',
    title: '清理 · 删除实验索引',
    method: 'DELETE', path: '/tut-l09-docs',
    predict: '删除索引会惊动传输层吗?',
    expect: 'acknowledged: true。单节点上建索引、写文档、GET、删除全程不出节点 —— 传输计数从头到尾都是 0,这正是 localNodeConnection 优化存在的证据。'
  };
})();
