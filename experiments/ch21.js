/* 第21课：3组29张操作卡；保留全部16个原实验ID。 */
(function () {
  'use strict';
  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};
  window.ESEXPERIMENTS["ch21-16-environment"] = {
  "version": 1,
  "id": "ch21-16-environment",
  "title": "A1 · 核对节点版本",
  "method": "GET",
  "path": "/",
  "body": null,
  "predict": "本课锚定哪个 ES / Lucene 版本？",
  "expect": "应为 ES 9.4.0、Lucene 10.4.0；实验使用已运行的匿名学习端点 localhost:9200。受认证保护的端点需有相应权限。"
};
  window.ESEXPERIMENTS["ch21-00-setup"] = {
  "version": 1,
  "id": "ch21-00-setup",
  "title": "A2 · 建 tut-l21-docs",
  "method": "PUT",
  "path": "/tut-l21-docs",
  "body": {
    "settings": {
      "number_of_shards": 1,
      "number_of_replicas": 0,
      "auto_expand_replicas": "false",
      "refresh_interval": "1s",
      "default_pipeline": "_none",
      "final_pipeline": "_none"
    },
    "mappings": {
      "dynamic": "strict",
      "_source": {
        "enabled": true
      },
      "properties": {
        "title": {
          "type": "keyword"
        }
      }
    }
  },
  "predict": "建索引会增加哪些控制信息？",
  "expect": "acknowledged、shards_acknowledged 通常 true；显式 1 主 0 副、strict keyword 与 refresh=1s。创建后还可能有分配/启动更新，不承诺只加一次 version。已存在时 400，应先完成末尾清理再重做。"
};
  window.ESEXPERIMENTS["ch21-17-health"] = {
  "version": 1,
  "id": "ch21-17-health",
  "title": "A3 · 等本课主分片就绪",
  "method": "GET",
  "path": "/_cluster/health/tut-l21-docs?wait_for_status=green&wait_for_no_relocating_shards=true&wait_for_no_initializing_shards=true&timeout=10s",
  "body": null,
  "predict": "主分片已经 STARTED 了吗？",
  "expect": "timed_out=false、status=green、active_primary_shards=1；检查失败时先解决分配条件再继续。仅限定本课索引，不能代表其他索引健康。"
};
  window.ESEXPERIMENTS["ch21-01-metrics-no-version"] = {
  "version": 1,
  "id": "ch21-01-metrics-no-version",
  "title": "A4 · metric 未点名 version",
  "method": "GET",
  "path": "/_cluster/state/metadata,routing_table/tut-l21-docs?filter_path=cluster_uuid,version,state_uuid,master_node,metadata.indices.tut-l21-docs.settings.index.number_of_shards,metadata.indices.tut-l21-docs.settings.index.number_of_replicas,metadata.indices.tut-l21-docs.mappings,routing_table.indices.tut-l21-docs.shards",
  "body": null,
  "predict": "filter_path 写了 version、state_uuid、master_node，它们会出现吗？",
  "expect": "三个都缺席；cluster_uuid 保留。number_of_shards=1/replicas=0 在 metadata；路由表里 shards[\"0\"] 有 primary=true、state=STARTED、node。filter_path 不能创造未序列化字段。"
};
  window.ESEXPERIMENTS["ch21-02-metrics-with-version"] = {
  "version": 1,
  "id": "ch21-02-metrics-with-version",
  "title": "A5 · 点名 version 与 master_node",
  "method": "GET",
  "path": "/_cluster/state/version,metadata,routing_table,master_node/tut-l21-docs?filter_path=version,state_uuid,master_node,metadata.indices.tut-l21-docs.settings.index.number_of_shards,routing_table.indices.tut-l21-docs.shards",
  "body": null,
  "predict": "与 A4 相比哪些字段新增？",
  "expect": "version、state_uuid、master_node 出现；改变的是 metric 列表。索引限定限制 metadata/路由的索引范围，不把集群版本变成索引版本。"
};
  window.ESEXPERIMENTS["ch21-03-master-node"] = {
  "version": 1,
  "id": "ch21-03-master-node",
  "title": "A6 · 单独查看主节点 ID",
  "method": "GET",
  "path": "/_cluster/state/master_node?filter_path=master_node,cluster_uuid",
  "body": null,
  "predict": "不取 nodes map，仍能指认主节点吗？",
  "expect": "返回 master_node 与 cluster_uuid。单节点时主 ID 与 A9 的节点 ID 一致；有主资格不等于当前主节点。"
};
  window.ESEXPERIMENTS["ch21-04-blocks-empty"] = {
  "version": 1,
  "id": "ch21-04-blocks-empty",
  "title": "A7 · 看本课与全局阻断",
  "method": "GET",
  "path": "/_cluster/state/blocks/tut-l21-docs",
  "body": null,
  "predict": "green 是否保证没有任何 block？",
  "expect": "本例无 block 时 blocks={}；green 描述分片可用性，不证明可写。索引范围只过滤索引级阻断，仍可包含全局阻断；实际条目依环境判断。"
};
  window.ESEXPERIMENTS["ch21-05-term-in-metadata"] = {
  "version": 1,
  "id": "ch21-05-term-in-metadata",
  "title": "A8 · term 与两份投票配置",
  "method": "GET",
  "path": "/_cluster/state/metadata?filter_path=metadata.cluster_coordination",
  "body": null,
  "predict": "term 是顶层字段吗？投票配置叫 config 吗？",
  "expect": "term 位于 metadata.cluster_coordination，数值随选举历史变化；本次参考实测为 1，不是固定默认。字段是 last_committed_config、last_accepted_config 和 voting_config_exclusions，没有 config。"
};
  window.ESEXPERIMENTS["ch21-18-nodes"] = {
  "version": 1,
  "id": "ch21-18-nodes",
  "title": "A9 · 节点角色与当前主分开",
  "method": "GET",
  "path": "/_cluster/state/nodes,master_node?filter_path=nodes.*.name,nodes.*.roles,master_node",
  "body": null,
  "predict": "nodes 中 master 角色就是当前主吗？",
  "expect": "nodes 的键是节点 ID、roles 表示资格；master_node 指认当选主。单节点学习环境一个节点，多节点不能将所有有 master 角色的节点都当成主。"
};
  window.ESEXPERIMENTS["ch21-06-pending-tasks"] = {
  "version": 1,
  "id": "ch21-06-pending-tasks",
  "title": "A10 · 待处理与正在执行的任务",
  "method": "GET",
  "path": "/_cluster/pending_tasks",
  "body": null,
  "predict": "它统计历史更新次数吗？executing=true 意味着什么？",
  "expect": "空闲参考 tasks=[]；列表也可包含 executing=true 的当前批次任务，字段为 insert_order、time_in_queue_millis。不是文档写入队列或历史计数；一次空读不能证明一直没有阻塞。"
};
  window.ESEXPERIMENTS["ch21-07-v1"] = {
  "version": 1,
  "id": "ch21-07-v1",
  "title": "B1 · 记录 V1 与 UUID",
  "method": "GET",
  "path": "/_cluster/state/version?filter_path=version,state_uuid,cluster_uuid",
  "body": null,
  "predict": "记下建第二索引之前的版本。",
  "expect": "记录 V1.version 与 V1.state_uuid；这是本节点的已应用状态，不是文档 _version。后续比较要求同一主任期、没有无关并发状态任务。"
};
  window.ESEXPERIMENTS["ch21-08-create-index"] = {
  "version": 1,
  "id": "ch21-08-create-index",
  "title": "B2 · 建 tut-l21-ver",
  "method": "PUT",
  "path": "/tut-l21-ver",
  "body": {
    "settings": {
      "number_of_shards": 1,
      "number_of_replicas": 0,
      "auto_expand_replicas": "false",
      "refresh_interval": "1s",
      "default_pipeline": "_none",
      "final_pipeline": "_none"
    },
    "mappings": {
      "dynamic": "strict",
      "_source": {
        "enabled": true
      },
      "properties": {
        "title": {
          "type": "keyword"
        }
      }
    }
  },
  "predict": "一次建索引对应一次状态发布吗？",
  "expect": "通常 acknowledged/shards_acknowledged=true；索引创建、分配、启动可能分多批更新。不要预设 V2−V1=1；重复创建 400 后需先清理重做。"
};
  window.ESEXPERIMENTS["ch21-19-health-ver"] = {
  "version": 1,
  "id": "ch21-19-health-ver",
  "title": "B3 · 等第二索引稳定",
  "method": "GET",
  "path": "/_cluster/health/tut-l21-ver?wait_for_status=green&wait_for_no_relocating_shards=true&wait_for_no_initializing_shards=true&timeout=10s",
  "body": null,
  "predict": "为什么不能立刻把创建响应当稳定基线？",
  "expect": "timed_out=false、green、1 个活动主分片；先等 STARTED，再记录后续写入的基线，以减小启动任务干扰。仍不保证其他后台任务停止。"
};
  window.ESEXPERIMENTS["ch21-09-v2"] = {
  "version": 1,
  "id": "ch21-09-v2",
  "title": "B4 · 记录 V2：允许多次递增",
  "method": "GET",
  "path": "/_cluster/state/version?filter_path=version,state_uuid,cluster_uuid",
  "body": null,
  "predict": "比较 V1：版本差一定是 1 吗？",
  "expect": "在本例同主任期下 V2>V1，UUID 不同；差值可大于 1，实际差值应自行记录。一个已改变的状态批次加一，一个 API 不等于一个批次。"
};
  window.ESEXPERIMENTS["ch21-10-write-doc"] = {
  "version": 1,
  "id": "ch21-10-write-doc",
  "title": "B5 · 写已声明的 keyword 字段",
  "method": "PUT",
  "path": "/tut-l21-docs/_doc/1?refresh=true",
  "body": {
    "title": "cluster-state-is-a-snapshot"
  },
  "predict": "strict mapping 下的普通写入需要改集群状态吗？",
  "expect": "首次 201/result=created、_shards.successful=1，重复 200/updated；已有字段不触发 mapping 更新。refresh 发布搜索读者，与集群状态版本递增是不同机制。"
};
  window.ESEXPERIMENTS["ch21-11-v3"] = {
  "version": 1,
  "id": "ch21-11-v3",
  "title": "B6 · 记录 V3：数据写入对照",
  "method": "GET",
  "path": "/_cluster/state/version?filter_path=version,state_uuid,cluster_uuid",
  "body": null,
  "predict": "没有其他状态任务时 V3 与 V2 如何比较？",
  "expect": "本轮参考 V3=V2，UUID 相同；仅说明本窗口未观察到新状态。若变大，不能由版本/UUID 判断具体原因，需核对动态映射、后台任务和节点变化。"
};
  window.ESEXPERIMENTS["ch21-20-get-doc"] = {
  "version": 1,
  "id": "ch21-20-get-doc",
  "title": "B7 · 文档版本确实增长",
  "method": "GET",
  "path": "/tut-l21-docs/_doc/1",
  "body": null,
  "predict": "集群版本不动，文档是否已经存下？",
  "expect": "found=true、_source.title 与 B5 相同；首次文档 _version=1，重复写同 ID 后增加。文档 _version、ClusterState.version、内部 Metadata.version 分属不同对象。"
};
  window.ESEXPERIMENTS["ch21-12-settings"] = {
  "version": 1,
  "id": "ch21-12-settings",
  "title": "C1 · 只改本课索引的动态设置",
  "method": "PUT",
  "path": "/tut-l21-docs/_settings",
  "body": {
    "index": {
      "refresh_interval": "5s"
    }
  },
  "predict": "与 B5 写文档相比，这次变了哪个平面？",
  "expect": "acknowledged=true；refresh_interval 从显式 1s 改为 5s，IndexMetadata 随控制状态更新。本卡不改 cluster.max_shards_per_node；C7 显式恢复 1s。"
};
  window.ESEXPERIMENTS["ch21-13-two-counters"] = {
  "version": 1,
  "id": "ch21-13-two-counters",
  "title": "C2 · 顶层版本与隐藏的元数据版本",
  "method": "GET",
  "path": "/_cluster/state/version,metadata/tut-l21-docs?filter_path=version,state_uuid,metadata.version,metadata.indices.tut-l21-docs.settings.index.refresh_interval",
  "body": null,
  "predict": "请求 metadata.version，REST 就会输出内部计数器吗？",
  "expect": "version 比 B6 大、UUID 换新，refresh_interval=5s；metadata.version 缺席。9.4.0 API 上下文不序列化它，不能用 filter_path 造出来或拿顶层 version 替代它。"
};
  window.ESEXPERIMENTS["ch21-21-settings-noop"] = {
  "version": 1,
  "id": "ch21-21-settings-noop",
  "title": "C3 · 重复提交相同设置",
  "method": "PUT",
  "path": "/tut-l21-docs/_settings",
  "body": {
    "index": {
      "refresh_interval": "5s"
    }
  },
  "predict": "acknowledged=true 是否保证产生新状态？",
  "expect": "acknowledged=true；本例值未变可沿用原状态，不发布。下一卡与 C2 比较；响应成功与版本增加是两个不同判断。"
};
  window.ESEXPERIMENTS["ch21-22-after-noop"] = {
  "version": 1,
  "id": "ch21-22-after-noop",
  "title": "C4 · 对照相同设置前后版本",
  "method": "GET",
  "path": "/_cluster/state/version?filter_path=version,state_uuid,cluster_uuid",
  "body": null,
  "predict": "C3 没改值，C4 应与 C2 比较什么？",
  "expect": "本轮版本与 UUID 均相同；仅在没有其他状态任务时可作 no-op 证据。内部计数器并不要求不同数值，也不能当成永恒大小关系。"
};
  window.ESEXPERIMENTS["ch21-23-wait-satisfied"] = {
  "version": 1,
  "id": "ch21-23-wait-satisfied",
  "title": "C5 · 元数据等待：已满足的门槛",
  "method": "GET",
  "path": "/_cluster/state/version?wait_for_metadata_version=1&wait_for_timeout=1ms",
  "body": null,
  "predict": "1 这个门槛会请求修改状态吗？",
  "expect": "HTTP 200、wait_for_timed_out=false，并带当前 version/state_uuid；等待检查的是内部 Metadata.version≥1，不修改状态，也不输出该内部版本。"
};
  window.ESEXPERIMENTS["ch21-24-wait-timeout"] = {
  "version": 1,
  "id": "ch21-24-wait-timeout",
  "title": "C6 · 元数据等待：极高门槛超时",
  "method": "GET",
  "path": "/_cluster/state/version?wait_for_metadata_version=9223372036854775807&wait_for_timeout=1ms",
  "body": null,
  "predict": "超时会是 HTTP 错误吗？顶层 version 还能读到吗？",
  "expect": "HTTP 200、wait_for_timed_out=true，只有 cluster_name 与超时标志，无状态 version/UUID。1ms 是等待参数，不是整个请求耗时上限；这个极高门槛仅用于有界超时演示。"
};
  window.ESEXPERIMENTS["ch21-26-restore-setting"] = {
  "version": 1,
  "id": "ch21-26-restore-setting",
  "title": "C7 · 显式恢复本课初始设置",
  "method": "PUT",
  "path": "/tut-l21-docs/_settings",
  "body": {
    "index": {
      "refresh_interval": "1s"
    }
  },
  "predict": "恢复设置是否也会更新控制状态？",
  "expect": "acknowledged=true；恢复从 5s 到本章创建时明确设置的 1s，又会更新元数据。不要把 null 或删另一个索引理解成已恢复此设置。"
};
  window.ESEXPERIMENTS["ch21-27-settings-readback"] = {
  "version": 1,
  "id": "ch21-27-settings-readback",
  "title": "C8 · 核对恢复结果",
  "method": "GET",
  "path": "/tut-l21-docs/_settings?filter_path=tut-l21-docs.settings.index.refresh_interval",
  "body": null,
  "predict": "恢复响应成功后，实际值是什么？",
  "expect": "index.refresh_interval=1s。全套重做仍要按末尾点名删除两个索引，再从 A1 开始；整轮没有写入集群级设置。"
};
  window.ESEXPERIMENTS["ch21-14-cleanup-docs"] = {
  "version": 1,
  "id": "ch21-14-cleanup-docs",
  "title": "清理 1 · 删除 tut-l21-docs",
  "method": "DELETE",
  "path": "/tut-l21-docs",
  "body": null,
  "predict": "会删除哪些资源？",
  "expect": "acknowledged=true；删除 tut-l21-docs 及其文档，元数据与路由随之更新。再次删除 404/index_not_found_exception 是资源已清理的结果。"
};
  window.ESEXPERIMENTS["ch21-15-cleanup-ver"] = {
  "version": 1,
  "id": "ch21-15-cleanup-ver",
  "title": "清理 2 · 删除 tut-l21-ver",
  "method": "DELETE",
  "path": "/tut-l21-ver",
  "body": null,
  "predict": "删除这个索引会顺手还原集群设置吗？",
  "expect": "acknowledged=true；只删除 tut-l21-ver。本版未改集群设置；若曾运行旧版，先 GET /_cluster/settings 核对 cluster.max_shards_per_node，并根据原值单独恢复。"
};
  window.ESEXPERIMENTS["ch21-25-cleanup-docs-check"] = {
  "version": 1,
  "id": "ch21-25-cleanup-docs-check",
  "title": "清理 3 · 核对文档索引已不存在",
  "method": "HEAD",
  "path": "/tut-l21-docs",
  "body": null,
  "predict": "清理后第一次创建应该碰到旧资源吗？",
  "expect": "HTTP 404、空响应正文；确认删除后从 A1 重做。HEAD 的 404 是本卡预期结果。"
};
  window.ESEXPERIMENTS["ch21-28-cleanup-ver-check"] = {
  "version": 1,
  "id": "ch21-28-cleanup-ver-check",
  "title": "清理 4 · 核对第二索引已不存在",
  "method": "HEAD",
  "path": "/tut-l21-ver",
  "body": null,
  "predict": "两个专属资源都删了吗？",
  "expect": "HTTP 404、空正文。只点名本课两个索引，不用通配符、不删除其他章节资源。"
};
})();
