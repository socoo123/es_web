/* experiments/ch09.js — 第 9 课：传输层；源码预期与 API 实测分开记录 */
(function () {
  'use strict';
  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};

  window.ESEXPERIMENTS["ch09-00-version"] = {
  "version": 1,
  "id": "ch09-00-version",
  "title": "A1 · 固定版本与节点身份",
  "method": "GET",
  "path": "/",
  "body": null,
  "predict": "发行号与 TransportVersion 是同一个数吗？",
  "expect": "本课预期 version.number=9.4.0、lucene_version=10.4.0。记录节点名与 cluster_uuid；根 API 不给出完整帧契约，也不能用发行号直接替代 stream 的 TransportVersion。版本或部署不符时先核对。"
};
  window.ESEXPERIMENTS["ch09-01-ports"] = {
  "version": 1,
  "id": "ch09-01-ports",
  "title": "A2 · CAT 的两个发布端口",
  "method": "GET",
  "path": "/_cat/nodes?v&full_id=true&h=id,name,port,http_address",
  "body": null,
  "predict": "port 一定是 9300，http_address 一定是 9200 吗？",
  "expect": "port 实际取 DiscoveryNode 的 transport 发布地址端口；http_address 取 HTTP 发布地址。默认 transport.port 范围 9300-9399，实际绑定/发布可配置；不能把描述中的 bound 当作实现取值。用 A3 看 bound_address 与 publish_address。"
};
  window.ESEXPERIMENTS["ch09-01-addresses"] = {
  "version": 1,
  "id": "ch09-01-addresses",
  "title": "A3 · 分开绑定地址与发布地址",
  "method": "GET",
  "path": "/_nodes/_local/http,transport?filter_path=_nodes.failed,nodes.*.name,nodes.*.transport.bound_address,nodes.*.transport.publish_address,nodes.*.http.bound_address,nodes.*.http.publish_address",
  "body": null,
  "predict": "对外公布的地址必须等于每个监听地址吗？",
  "expect": "读取本 HTTP 端点所在节点的两个协议。bound_address 是监听地址列表，publish_address 是对端应连接的公布地址；配置、容器映射可令二者不同。看到 transport 地址只证明服务被配置，不证明本课 GET 跨了节点。_nodes.failed 预期 0。"
};
  window.ESEXPERIMENTS["ch09-05-defaults"] = {
  "version": 1,
  "id": "ch09-05-defaults",
  "title": "A4 · 设置值与角色修正后的连接画像",
  "method": "GET",
  "path": "/_cluster/settings?include_defaults=true&flat_settings=true&filter_path=**.transport.connections_per_node.recovery,**.transport.connections_per_node.bulk,**.transport.connections_per_node.reg,**.transport.connections_per_node.state,**.transport.connections_per_node.ping,**.transport.compress,**.transport.compression_scheme,**.transport.ping_schedule,**.transport.port",
  "body": null,
  "predict": "defaults 中 recovery=2，是否每个节点都实际建两条恢复连接？",
  "expect": "无覆盖的默认自管 9.4.0：2/3/6/1/1，compress=INDEXING_DATA、scheme=LZ4、ping_schedule=-1、port=9300-9399。defaults 可含响应节点本地配置；画像再按本地 data/master 角色将 recovery/state 置 0。13 是特定默认画像的通道数，不是当前或累计出站统计。"
};
  window.ESEXPERIMENTS["ch09-02-no-cat"] = {
  "version": 1,
  "id": "ch09-02-no-cat",
  "title": "A5 · 未注册的 REST 路由",
  "method": "GET",
  "path": "/_cat/transport",
  "body": null,
  "predict": "这是 Transport 协议错误，还是 HTTP 路由错误？",
  "expect": "在本课标准自管 9.4.0、无新增该路由的插件前提下，预期 HTTP 400；顶层 error 字符串含 no handler found for uri [/_cat/transport] and method [GET]。这是 REST 查路由失败，不是发过 Transport 帧。地址用 A3，统计用 B4/B6；401/403 先核对认证。"
};
  window.ESEXPERIMENTS["ch09-00-setup"] = {
  "version": 1,
  "id": "ch09-00-setup",
  "title": "B1 · 建立本课单分片索引",
  "method": "PUT",
  "path": "/tut-l09-docs",
  "body": {
    "settings": {
      "number_of_shards": 1,
      "number_of_replicas": 0,
      "refresh_interval": "-1"
    },
    "mappings": {
      "dynamic": "strict",
      "properties": {
        "title": {
          "type": "keyword"
        }
      }
    }
  },
  "predict": "创建 acknowledged=true 等于分片已可读、整个集群 green 吗？",
  "expect": "索引不存在且无匹配模板/默认 ingest pipeline 时，预期 acknowledged=true；shards_acknowledged 还取决于等待。B2 明确等待本课索引。周期刷新关闭，title 显式 keyword。重复创建预期 400 resource_already_exists_exception；确认是自己的本课资源后清理，再从 B1 重做。"
};
  window.ESEXPERIMENTS["ch09-00-health"] = {
  "version": 1,
  "id": "ch09-00-health",
  "title": "B2 · 等待本课索引就绪",
  "method": "GET",
  "path": "/_cluster/health/tut-l09-docs?wait_for_status=green&timeout=5s",
  "body": null,
  "predict": "单节点的零副本索引是否不需要等待？",
  "expect": "预期 status=green、timed_out=false、active_primary_shards=1、active_shards=1。这里只等 tut-l09-docs，不保证其他索引健康；若超时先检查分片分配/资源，再重复 B2，别继续假定前提成立。"
};
  window.ESEXPERIMENTS["ch09-03-doc"] = {
  "version": 1,
  "id": "ch09-03-doc",
  "title": "B3 · 固定 ID 写入并显式刷新",
  "method": "PUT",
  "path": "/tut-l09-docs/_doc/1?refresh=true",
  "body": {
    "title": "transport-frame"
  },
  "predict": "重复运行后 _version 仍是 1 吗？",
  "expect": "首次预期 201/result=created；重复固定 ID 写入通常 200/result=updated，_version 增加。记录本次 _version，B5 应读到同一值与 title。refresh=true 使本次写入可搜索，但不证明发生远程传输，也不承诺任何线程池或 transport 计数精确 +1。"
};
  window.ESEXPERIMENTS["ch09-04-before"] = {
  "version": 1,
  "id": "ch09-04-before",
  "title": "B4 · 记录 GET 之前的传输基线",
  "method": "GET",
  "path": "/_nodes/_local/stats/transport?filter_path=_nodes.failed,nodes.*.name,nodes.*.transport.server_open,nodes.*.transport.total_outbound_connections,nodes.*.transport.rx_count,nodes.*.transport.rx_size_in_bytes,nodes.*.transport.tx_count,nodes.*.transport.tx_size_in_bytes",
  "body": null,
  "predict": "server_open、total_outbound_connections、rx/tx 是同一种量吗？",
  "expect": "按响应节点 ID 保存基线。server_open 是当前接受的通道数；total_outbound_connections 是累计成功建立的 NodeChannels 连接组数；rx/tx 是全节点网络消息累计值。安静单节点可能为 0，已有连接/探测或后台流量也可能非 0；基线不要求清零。"
};
  window.ESEXPERIMENTS["ch09-04-get"] = {
  "version": 1,
  "id": "ch09-04-get",
  "title": "B5 · 实际执行本课 GET",
  "method": "GET",
  "path": "/tut-l09-docs/_doc/1?realtime=true",
  "body": null,
  "predict": "HTTP 收到文档就证明 GetRequest.writeTo 被调用了吗？",
  "expect": "预期 found=true、_id=1、_source.title=transport-frame，_version 与 B3 本次写入相同。本课单节点下分片就在该节点，源码 localNodeConnection 跳过请求/响应 wire 序列化；本请求成功不能验证跨节点帧或混合版本兼容。重复 GET 不修改文档。"
};
  window.ESEXPERIMENTS["ch09-04-stats"] = {
  "version": 1,
  "id": "ch09-04-stats",
  "title": "B6 · 对比 GET 前后，限定结论",
  "method": "GET",
  "path": "/_nodes/_local/stats/transport?filter_path=_nodes.failed,nodes.*.name,nodes.*.transport.server_open,nodes.*.transport.total_outbound_connections,nodes.*.transport.rx_count,nodes.*.transport.rx_size_in_bytes,nodes.*.transport.tx_count,nodes.*.transport.tx_size_in_bytes",
  "body": null,
  "predict": "一次 GET 后计数没变，是否足以证明没有任何序列化 bug？",
  "expect": "与 B4 同一节点对照。满足安静单节点前提时，B5 本地路径不增加网络 rx/tx，历史总值仍可非零。若变化，检查探测、后台/其他客户端流量和节点拓扑；节点 ID 改变则重取基线。零增量不能代替远程或混合版本序列化测试；不要用累计连接组数与 13 个通道比较。"
};
  window.ESEXPERIMENTS["ch09-06-cleanup"] = {
  "version": 1,
  "id": "ch09-06-cleanup",
  "title": "清理 · 点名删除本课索引",
  "method": "DELETE",
  "path": "/tut-l09-docs",
  "body": null,
  "predict": "删除索引会清除传输历史或关闭所有 TCP 连接吗？",
  "expect": "只删除 tut-l09-docs，预期 acknowledged=true；重复删除通常 404 index_not_found_exception。删除不重置节点累计统计。重做按 B1→B2→B3→B4→B5→B6→清理，每次保存新基线；A 组是只读观察与预期错误，可重复执行。"
};
})();
