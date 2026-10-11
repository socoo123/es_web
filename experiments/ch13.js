/* 第13课 · 固定9.4.0源码推导；本轮真实API未运行。 */
(function () {
  "use strict";
  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};
  window.ESEXPERIMENTS["ch13-39-version"] = {
  "version": 1,
  "id": "ch13-39-version",
  "title": "A1 · 确认运行版本",
  "method": "GET",
  "path": "/?filter_path=version.number,cluster_name",
  "body": null,
  "predict": "当前连接是否确实为 9.4.0？",
  "expect": "预期 version.number=9.4.0。本章单节点、一个 data 节点；以下卡片为源码推导预期，本轮 API 未运行。版本不同先核对差异。"
};
  window.ESEXPERIMENTS["ch13-00-setup"] = {
  "version": 1,
  "id": "ch13-00-setup",
  "title": "A2 · 显式创建条目实验索引",
  "method": "PUT",
  "path": "/tut-l13-items",
  "body": {
    "settings": {
      "index.mode": "standard",
      "index.mapping.source.mode": "stored",
      "number_of_shards": 2,
      "number_of_replicas": 0,
      "auto_expand_replicas": "false",
      "routing_partition_size": 1,
      "refresh_interval": "-1",
      "default_pipeline": "_none",
      "final_pipeline": "_none",
      "write.wait_for_active_shards": "1",
      "translog.durability": "request"
    },
    "mappings": {
      "_source": {
        "enabled": true
      },
      "dynamic": "strict",
      "properties": {
        "title": {
          "type": "keyword"
        },
        "tag": {
          "type": "keyword"
        }
      }
    }
  },
  "predict": "建索引成功是否等于两份 primary 已可写？",
  "expect": "首次预期 HTTP 200、acknowledged:true；还须执行 A3 等待。重复创建为 400 resource_already_exists_exception，不会重置数据。standard、2 主 0 副、strict keyword、stored source、refresh=-1、无管道；要求无匹配模板。"
};
  window.ESEXPERIMENTS["ch13-13-health-items"] = {
  "version": 1,
  "id": "ch13-13-health-items",
  "title": "A3 · 等待两份 primary 就绪",
  "method": "GET",
  "path": "/_cluster/health/tut-l13-items?wait_for_status=green&wait_for_no_initializing_shards=true&timeout=30s&filter_path=status,timed_out,active_primary_shards,unassigned_shards",
  "body": null,
  "predict": "0 副本下应有几个 active primary？",
  "expect": "预期 timed_out:false、status:green、active_primary_shards:2、unassigned_shards:0；超时先排查分配，本组后续请求依赖就绪。检查只限本课索引。"
};
  window.ESEXPERIMENTS["ch13-01-mixed"] = {
  "version": 1,
  "id": "ch13-01-mixed",
  "title": "A4 · 六项混批，按操作序号核对结果",
  "method": "POST",
  "path": "/_bulk?refresh=false",
  "body": "{\"index\":{\"_index\":\"tut-l13-items\",\"_id\":\"ok-a\"}}\n{\"title\":\"good A\"}\n{\"create\":{\"_index\":\"tut-l13-items\",\"_id\":\"dup\"}}\n{\"title\":\"first\"}\n{\"create\":{\"_index\":\"tut-l13-items\",\"_id\":\"dup\"}}\n{\"title\":\"again\"}\n{\"update\":{\"_index\":\"tut-l13-items\",\"_id\":\"ok-a\"}}\n{\"doc\":{\"tag\":\"t1\"}}\n{\"delete\":{\"_index\":\"tut-l13-items\",\"_id\":\"bye\"}}\n{\"index\":{\"_index\":\"tut-l13-items\",\"_id\":\"ok-b\"}}\n{\"title\":\"good B\"}\n",
  "predict": "首次六项 status、result、error 各是什么？delete 404 是否计入 errors？",
  "expect": "首次预期 HTTP 200；items 顺序为 index201、create201、create409、update200、delete404/not_found、index201，errors:true 来自 create 的 error。delete not_found 无 error。重复时两个 create 都409，两个 index 都200/updated；update 仍在同 ID 的 index 后加 tag。"
};
  window.ESEXPERIMENTS["ch13-14-get-mixed"] = {
  "version": 1,
  "id": "ch13-14-get-mixed",
  "title": "A5 · realtime GET 读回更新后的文档",
  "method": "GET",
  "path": "/tut-l13-items/_doc/ok-a?filter_path=found,_source",
  "body": null,
  "predict": "未 refresh，GET 能否读到同批 update 的 tag？",
  "expect": "预期 HTTP 200、found:true、_source 为 title:\"good A\",tag:\"t1\"。默认 realtime GET 与搜索视图不同；这证明同 ID 的前项已写入后再更新，不证明跨 shard 的全局执行顺序。"
};
  window.ESEXPERIMENTS["ch13-02-bad-source"] = {
  "version": 1,
  "id": "ch13-02-bad-source",
  "title": "A6 · index 坏 JSON 夹在两个好条目之间",
  "method": "POST",
  "path": "/_bulk?refresh=false",
  "body": "{\"index\":{\"_index\":\"tut-l13-items\",\"_id\":\"ok-c\"}}\n{\"title\":\"good C\"}\n{\"index\":{\"_index\":\"tut-l13-items\",\"_id\":\"bad\"}}\n{this is not json}\n{\"index\":{\"_index\":\"tut-l13-items\",\"_id\":\"ok-d\"}}\n{\"title\":\"good D\"}\n",
  "predict": "index 第二行原样切片后，后面的好条目是否继续？",
  "expect": "无管道、standard 配置下预期 HTTP 200、errors:true；bad 一项400/解析类 error，两个好项首次201、重复200。index/create 第二行在 bulk 解析阶段只切字节；普通写入文档解析再报条级错误。update 第二行规则不同，见 A8。",
  "allowInvalidBody": true
};
  window.ESEXPERIMENTS["ch13-15-get-afterbad"] = {
  "version": 1,
  "id": "ch13-15-get-afterbad",
  "title": "A7 · 读回坏条目之后的好文档",
  "method": "GET",
  "path": "/tut-l13-items/_doc/ok-d?filter_path=found,_source",
  "body": null,
  "predict": "坏条目之后的 ok-d 是否被写入？",
  "expect": "预期 HTTP 200、found:true、title:\"good D\"。与 A6 的 bad.error 对照，确认该错误没有阻止好项执行。"
};
  window.ESEXPERIMENTS["ch13-16-bad-update"] = {
  "version": 1,
  "id": "ch13-16-bad-update",
  "title": "A8 · update 的坏第二行在入口报错",
  "method": "POST",
  "path": "/_bulk",
  "body": "{\"update\":{\"_index\":\"tut-l13-items\",\"_id\":\"ok-a\"}}\n{this is not json}\n",
  "predict": "同样是第二行坏 JSON，update 会不会得到 items 内的 error？",
  "expect": "预期请求级 HTTP 400、解析类 error，没有正常 items 数组。BulkRequestParser 直接调用 UpdateRequest.fromXContent；本卡只有这一项，尚无更早已执行块。随后 A9 读回原文档。",
  "allowInvalidBody": true
};
  window.ESEXPERIMENTS["ch13-17-get-after-update"] = {
  "version": 1,
  "id": "ch13-17-get-after-update",
  "title": "A9 · 失败的 update 没有改动原文档",
  "method": "GET",
  "path": "/tut-l13-items/_doc/ok-a?filter_path=found,_source",
  "body": null,
  "predict": "A8 报错后 title 与 tag 是否保持 A5 的值？",
  "expect": "预期 HTTP 200、title:\"good A\",tag:\"t1\"。若已做其他写入，先清理并从 A1 重做；不能从任意大流式 bulk 的400推断前缀也未写入。"
};
  window.ESEXPERIMENTS["ch13-03-unknown-index"] = {
  "version": 1,
  "id": "ch13-03-unknown-index",
  "title": "A10 · 普通 delete 指向不存在的索引",
  "method": "POST",
  "path": "/_bulk",
  "body": "{\"delete\":{\"_index\":\"tut-l13-nope\",\"_id\":\"x\"}}\n{\"index\":{\"_index\":\"tut-l13-items\",\"_id\":\"ok-e\"}}\n{\"title\":\"good E\"}\n",
  "predict": "不存在的索引与存在索引内不存在的 ID，其404有什么区别？",
  "expect": "要求 tut-l13-nope 不存在。预期 HTTP 200、errors:true；delete 项404/index_not_found_exception，ok-e 首次201、重复200。普通内部版本 delete 不触发自动建索引；外部版本 delete 另有路径。本卡没有外部版本参数。"
};
  window.ESEXPERIMENTS["ch13-18-head-nope"] = {
  "version": 1,
  "id": "ch13-18-head-nope",
  "title": "A11 · 确认普通 delete 没有自动建索引",
  "method": "HEAD",
  "path": "/tut-l13-nope",
  "body": null,
  "predict": "HEAD 的 HTTP 状态能否验证目标未被创建？",
  "expect": "预期 HTTP 404、无响应 body。若200，本课初始条件已被其他操作改变；先查明来源，再使用独立环境或清理本课资源重做。"
};
  window.ESEXPERIMENTS["ch13-04-malformed"] = {
  "version": 1,
  "id": "ch13-04-malformed",
  "title": "A12 · 缺末尾换行，请求级400",
  "method": "POST",
  "path": "/_bulk",
  "body": "{\"index\":{\"_index\":\"tut-l13-items\",\"_id\":\"no-nl\"}}\n{\"title\":\"missing terminator\"}",
  "predict": "仅一个未完成项，没有末尾换行，是否已经写入？",
  "expect": "预期 HTTP 400，reason 含 The bulk request must be terminated by a newline；没有正常 items。这一项尚未完成切片，下一卡应404。大增量请求若早先块已执行，后续400不会将其回滚。",
  "allowInvalidBody": true
};
  window.ESEXPERIMENTS["ch13-19-get-no-nl"] = {
  "version": 1,
  "id": "ch13-19-get-no-nl",
  "title": "A13 · 读回未完成项，确认没有写入",
  "method": "GET",
  "path": "/tut-l13-items/_doc/no-nl?filter_path=found,_id",
  "body": null,
  "predict": "单项 A12 的 no-nl 是否存在？",
  "expect": "新鲜资源下预期 HTTP404、found:false。这只验证本卡未完成项，不是所有请求级错误都无副作用的证明。"
};
  window.ESEXPERIMENTS["ch13-20-bad-action"] = {
  "version": 1,
  "id": "ch13-20-bad-action",
  "title": "A14 · 非对象的 action 行在入口被拒",
  "method": "POST",
  "path": "/_bulk",
  "body": "[]\n",
  "predict": "action 行若为数组，能否形成条目？",
  "expect": "预期 HTTP400，Malformed action/metadata line 类 reason，没有正常 items。错误位于第一行，因此无先前执行块；不要把请求级错误扩展为事务回滚。",
  "allowInvalidBody": true
};
  window.ESEXPERIMENTS["ch13-05-setup-routed"] = {
  "version": 1,
  "id": "ch13-05-setup-routed",
  "title": "B1 · 显式创建路由实验索引",
  "method": "PUT",
  "path": "/tut-l13-routed",
  "body": {
    "settings": {
      "index.mode": "standard",
      "index.mapping.source.mode": "stored",
      "number_of_shards": 2,
      "number_of_replicas": 0,
      "auto_expand_replicas": "false",
      "routing_partition_size": 1,
      "refresh_interval": "-1",
      "default_pipeline": "_none",
      "final_pipeline": "_none",
      "write.wait_for_active_shards": "1",
      "translog.durability": "request"
    },
    "mappings": {
      "_source": {
        "enabled": true
      },
      "dynamic": "strict",
      "properties": {
        "title": {
          "type": "keyword"
        },
        "tag": {
          "type": "keyword"
        }
      }
    }
  },
  "predict": "两个主分片是否保证任意三篇均匀轮转？",
  "expect": "首次预期200、acknowledged:true；重复400/resource_already_exists_exception。9.4.0 新建普通 standard、非分区路由、strict title/tag keyword、2主0副、refresh=-1、无管道；数据保持只含下面的三个固定 ID。"
};
  window.ESEXPERIMENTS["ch13-21-health-routed"] = {
  "version": 1,
  "id": "ch13-21-health-routed",
  "title": "B2 · 等待路由实验索引 green",
  "method": "GET",
  "path": "/_cluster/health/tut-l13-routed?wait_for_status=green&wait_for_no_initializing_shards=true&timeout=30s&filter_path=status,timed_out,active_primary_shards",
  "body": null,
  "predict": "两份 primary 是否都 active？",
  "expect": "预期 timed_out:false、status:green、active_primary_shards:2；超时先恢复分配再执行 B3。"
};
  window.ESEXPERIMENTS["ch13-06-bulk-write"] = {
  "version": 1,
  "id": "ch13-06-bulk-write",
  "title": "B3 · 固定 ID 1/2/3 写入并刷新",
  "method": "POST",
  "path": "/_bulk?refresh=true",
  "body": "{\"index\":{\"_index\":\"tut-l13-routed\",\"_id\":\"1\"}}\n{\"title\":\"id-1\"}\n{\"index\":{\"_index\":\"tut-l13-routed\",\"_id\":\"2\"}}\n{\"title\":\"id-2\"}\n{\"index\":{\"_index\":\"tut-l13-routed\",\"_id\":\"3\"}}\n{\"title\":\"id-3\"}\n",
  "predict": "有效键是字符串 ID；三个条目分别进哪片？",
  "expect": "首次预期三个201/created、errors:false；重复为200/updated，仍三篇。键1、2进 shard1，键3进 shard0。refresh=true 作用于本批实际触及的分片，不刷新所有索引/未触及分片；它不修改 refresh_interval。"
};
  window.ESEXPERIMENTS["ch13-07-search-shards"] = {
  "version": 1,
  "id": "ch13-07-search-shards",
  "title": "B4 · 合并路由键1和3的搜索选片",
  "method": "GET",
  "path": "/tut-l13-routed/_search_shards?routing=1,3&filter_path=shards.shard",
  "body": null,
  "predict": "逗号列表表示两个键的选片并集，还是顺序执行？",
  "expect": "预期返回 shard0 与1，不依赖返回排序。这是搜索选择集合，不能证明文档实际位置；下面分开核对每把键。不带 routing 时会返回两片。"
};
  window.ESEXPERIMENTS["ch13-22-shard-one"] = {
  "version": 1,
  "id": "ch13-22-shard-one",
  "title": "B5 · 单独核对键1的落点",
  "method": "GET",
  "path": "/tut-l13-routed/_search_shards?routing=1&filter_path=shards.shard",
  "body": null,
  "predict": "hash(\"1\") 为负，Java % 能否正确选片？",
  "expect": "预期仅 shard1。按 ES 的 UTF-16LE、seed0 Murmur3，hash(\"1\")=-126235597，floorMod(…,2)=1。公式限定本课新建非分区普通索引；旧创建版本另有分支。"
};
  window.ESEXPERIMENTS["ch13-23-shard-three"] = {
  "version": 1,
  "id": "ch13-23-shard-three",
  "title": "B6 · 单独核对键3的落点",
  "method": "GET",
  "path": "/tut-l13-routed/_search_shards?routing=3&filter_path=shards.shard",
  "body": null,
  "predict": "ID3 是否因为数字大小而落 shard1？",
  "expect": "预期仅 shard0。hash(\"3\")=-1151172406，floorMod(…,2)=0；按字符串哈希分布，不是数字取模。"
};
  window.ESEXPERIMENTS["ch13-08-cat-shards"] = {
  "version": 1,
  "id": "ch13-08-cat-shards",
  "title": "B7 · 查看刷新后的 primary 文档数",
  "method": "GET",
  "path": "/_cat/shards/tut-l13-routed?v&h=shard,prirep,state,docs",
  "body": null,
  "predict": "这里只有三篇无 nested 的文档，docs 是否为2:1？",
  "expect": "前提满足时预期 shard1 的 p/STARTED/docs2，shard0 的 p/STARTED/docs1，行序不定。CAT docs 是 Lucene 计数；本课无 nested、无外部写入且已刷新，才可与三篇文档直接对应。bulk 不提供轮转均衡。"
};
  window.ESEXPERIMENTS["ch13-24-no-refresh"] = {
  "version": 1,
  "id": "ch13-24-no-refresh",
  "title": "C1 · 关闭周期刷新时写 v0",
  "method": "POST",
  "path": "/_bulk?refresh=false",
  "body": "{\"index\":{\"_index\":\"tut-l13-items\",\"_id\":\"v0\"}}\n{\"title\":\"unrefreshed\"}\n",
  "predict": "首次写入 v0，是否已经能被搜索？",
  "expect": "要求 A 组配置 refresh=-1、v0 从未写入/刷新，且无外部 refresh。预期201/created、errors:false。重复为200/updated；若旧 v0 已进入搜索视图，C2 的0预期失效，须清理后完整重做。false 只表示本请求不要求刷新。"
};
  window.ESEXPERIMENTS["ch13-25-count-before"] = {
  "version": 1,
  "id": "ch13-25-count-before",
  "title": "C2 · 搜索视图尚无 v0",
  "method": "POST",
  "path": "/tut-l13-items/_count",
  "body": {
    "query": {
      "ids": {
        "values": [
          "v0"
        ]
      }
    }
  },
  "predict": "禁用周期刷新后的精确 ID 计数是多少？",
  "expect": "新鲜前提下预期 count:0、_shards.failed:0。无时间竞赛：refresh=-1、没有外部 refresh。若已有旧视图或设置未恢复，不能套用0预期。"
};
  window.ESEXPERIMENTS["ch13-26-get-realtime"] = {
  "version": 1,
  "id": "ch13-26-get-realtime",
  "title": "C3 · realtime GET 已能读到 v0",
  "method": "GET",
  "path": "/tut-l13-items/_doc/v0?filter_path=found,_source",
  "body": null,
  "predict": "与 C2 count0 是否矛盾？",
  "expect": "预期HTTP200、found:true、title:\"unrefreshed\"。默认 realtime GET 可读当前写入；搜索须使用刷新后的 reader，两种可见性条件不同。"
};
  window.ESEXPERIMENTS["ch13-27-refresh-items"] = {
  "version": 1,
  "id": "ch13-27-refresh-items",
  "title": "C4 · 显式刷新本课索引",
  "method": "POST",
  "path": "/tut-l13-items/_refresh",
  "body": null,
  "predict": "本请求修改 refresh_interval 吗？",
  "expect": "预期 _shards.failed:0；本课两主0副通常 total/successful 为2。只刷新 tut-l13-items，并不改 refresh_interval=-1。成功后进行 C5。"
};
  window.ESEXPERIMENTS["ch13-28-count-after"] = {
  "version": 1,
  "id": "ch13-28-count-after",
  "title": "C5 · 刷新后搜索到 v0",
  "method": "POST",
  "path": "/tut-l13-items/_count",
  "body": {
    "query": {
      "ids": {
        "values": [
          "v0"
        ]
      }
    }
  },
  "predict": "同一查询刷新后是否变化？",
  "expect": "预期count:1、_shards.failed:0。C1/C2/C3/C4/C5 将写完成、realtime可读与搜索可见分开验证。"
};
  window.ESEXPERIMENTS["ch13-29-enable-periodic"] = {
  "version": 1,
  "id": "ch13-29-enable-periodic",
  "title": "C6 · wait_for 前显式启用1s周期刷新",
  "method": "PUT",
  "path": "/tut-l13-items/_settings",
  "body": {
    "index": {
      "refresh_interval": "1s"
    }
  },
  "predict": "在 refresh=-1 下直接 wait_for 会有什么风险？",
  "expect": "预期acknowledged:true。本组临时将周期设为1s，避免无外部刷新时无限等待；1s是调度周期，不是可见性或请求耗时上限。若 wait_for 卡住，可另一控制台显式执行 C4，再检查运行环境。"
};
  window.ESEXPERIMENTS["ch13-09-waitfor"] = {
  "version": 1,
  "id": "ch13-09-waitfor",
  "title": "C7 · wait_for 等覆盖本次写入的刷新",
  "method": "POST",
  "path": "/_bulk?refresh=wait_for",
  "body": "{\"index\":{\"_index\":\"tut-l13-items\",\"_id\":\"w1\"}}\n{\"title\":\"waited\"}\n",
  "predict": "wait_for 是等待 reader 覆盖写入，还是保证只等自动刷新？",
  "expect": "首次预期201、errors:false，重复200/updated。正常完成后 w1 可搜；可由自动或外部 refresh 满足，监听槽用尽还可能强制刷新。不承诺固定 took 或一定比 true 快；政策只覆盖触及分片，未修改索引设置。"
};
  window.ESEXPERIMENTS["ch13-10-count"] = {
  "version": 1,
  "id": "ch13-10-count",
  "title": "C8 · wait_for 完成后计数",
  "method": "POST",
  "path": "/tut-l13-items/_count",
  "body": {
    "query": {
      "ids": {
        "values": [
          "w1"
        ]
      }
    }
  },
  "predict": "C7 成功返回后，count 是否为1？",
  "expect": "预期count:1、_shards.failed:0；即使重复 w1，仍一篇。不能把该结论推广为其他未触及分片上的旧写入也已可搜。"
};
  window.ESEXPERIMENTS["ch13-30-restore-refresh"] = {
  "version": 1,
  "id": "ch13-30-restore-refresh",
  "title": "C9 · 恢复本课受控配置",
  "method": "PUT",
  "path": "/tut-l13-items/_settings",
  "body": {
    "index": {
      "refresh_interval": "-1"
    }
  },
  "predict": "恢复设置会撤销已刷新文档吗？",
  "expect": "预期acknowledged:true。停止后续周期调度，已打开的搜索视图不会清空；如要重复 C2 的count0，必须先删索引并从 A1 重做。"
};
  window.ESEXPERIMENTS["ch13-31-setup-waiting"] = {
  "version": 1,
  "id": "ch13-31-setup-waiting",
  "title": "D1 · 单 data 节点创建1主1副索引",
  "method": "PUT",
  "path": "/tut-l13-waiting",
  "body": {
    "settings": {
      "index.mode": "standard",
      "index.mapping.source.mode": "stored",
      "number_of_shards": 1,
      "number_of_replicas": 1,
      "auto_expand_replicas": "false",
      "routing_partition_size": 1,
      "refresh_interval": "-1",
      "default_pipeline": "_none",
      "final_pipeline": "_none",
      "write.wait_for_active_shards": "1",
      "translog.durability": "request"
    },
    "mappings": {
      "_source": {
        "enabled": true
      },
      "dynamic": "strict",
      "properties": {
        "title": {
          "type": "keyword"
        },
        "tag": {
          "type": "keyword"
        }
      }
    }
  },
  "predict": "单 data 节点能否分配同片的 replica？",
  "expect": "首次预期200、acknowledged:true；重复400。只有一个 data 节点、auto_expand=false 时 replica 无法与 primary 同节点，接下来等 yellow。多 data 节点下本组503预期不适用，不修改集群设置。"
};
  window.ESEXPERIMENTS["ch13-32-health-waiting"] = {
  "version": 1,
  "id": "ch13-32-health-waiting",
  "title": "D2 · 确认 primary active、replica 未分配",
  "method": "GET",
  "path": "/_cluster/health/tut-l13-waiting?wait_for_status=yellow&wait_for_no_initializing_shards=true&timeout=30s&filter_path=status,timed_out,active_primary_shards,active_shards,unassigned_shards",
  "body": null,
  "predict": "yellow 是否意味着不能写？",
  "expect": "单 data 节点预期 timed_out:false、status:yellow、active_primary_shards:1、active_shards:1、unassigned_shards:1。若green，环境不符合本组条件；先确认节点数，不能据此演示 all 不足。"
};
  window.ESEXPERIMENTS["ch13-33-mixed-active"] = {
  "version": 1,
  "id": "ch13-33-mixed-active",
  "title": "D3 · 同批 all：yellow一项超时，green一项成功",
  "method": "POST",
  "path": "/_bulk?wait_for_active_shards=all&timeout=1s&refresh=false",
  "body": "{\"index\":{\"_index\":\"tut-l13-waiting\",\"_id\":\"blocked\"}}\n{\"title\":\"needs replica\"}\n{\"index\":{\"_index\":\"tut-l13-items\",\"_id\":\"pass\"}}\n{\"title\":\"primary ready\"}\n",
  "predict": "all 在整个 bulk 检查一次，还是各分片分别检查？",
  "expect": "单 data 节点且 D2 yellow 时，预期HTTP200、errors:true；waiting项503/unavailable_shards_exception，items项首次201、重复200。green且0副的目标已满足all，不随另一片失败。1s是请求超时参数，不是实际耗时精确承诺。"
};
  window.ESEXPERIMENTS["ch13-34-get-blocked"] = {
  "version": 1,
  "id": "ch13-34-get-blocked",
  "title": "D4 · 写前门槛失败，blocked不存在",
  "method": "GET",
  "path": "/tut-l13-waiting/_doc/blocked?filter_path=found,_id",
  "body": null,
  "predict": "primary active，为何这一项仍未写入？",
  "expect": "新鲜索引下预期404、found:false。all门槛在primary.perform前未满足，不执行该写入；与后续复制失败或写后失败的副作用范围不同。"
};
  window.ESEXPERIMENTS["ch13-35-get-pass"] = {
  "version": 1,
  "id": "ch13-35-get-pass",
  "title": "D5 · 另一分片的成功项已经可读",
  "method": "GET",
  "path": "/tut-l13-items/_doc/pass?filter_path=found,_source",
  "body": null,
  "predict": "同批有503是否会撤销 pass？",
  "expect": "预期200、found:true、title:\"primary ready\"。不同 ShardId 可独立完成，bulk不提供跨项回滚。"
};
  window.ESEXPERIMENTS["ch13-36-wait-one"] = {
  "version": 1,
  "id": "ch13-36-wait-one",
  "title": "D6 · 同一yellow索引显式只等1份active",
  "method": "POST",
  "path": "/_bulk?wait_for_active_shards=1&refresh=false",
  "body": "{\"index\":{\"_index\":\"tut-l13-waiting\",\"_id\":\"one\"}}\n{\"title\":\"primary is enough\"}\n",
  "predict": "未分配replica会不会使条目失败？",
  "expect": "单 data 节点预期HTTP200、errors:false；首次201、重复200。_shards.total通常2、successful1、failed0：未分配拷贝不等于一次RPC失败。显式1只规定写前门槛；它不设置副本数、不禁用复制、不把集群变green。"
};
  window.ESEXPERIMENTS["ch13-37-get-waiting"] = {
  "version": 1,
  "id": "ch13-37-get-waiting",
  "title": "D7 · 读回成功项",
  "method": "GET",
  "path": "/tut-l13-waiting/_doc/one?filter_path=found,_source",
  "body": null,
  "predict": "黄色集群中的成功写是否可 realtime GET？",
  "expect": "预期200、found:true、title:\"primary is enough\"。本组仅演示active等待门槛与未分配副本；没有运行多节点复制故障实验，不能声称验证故障恢复。"
};
  window.ESEXPERIMENTS["ch13-11-cleanup-items"] = {
  "version": 1,
  "id": "ch13-11-cleanup-items",
  "title": "清理 · 删除 tut-l13-items",
  "method": "DELETE",
  "path": "/tut-l13-items?ignore_unavailable=true",
  "body": null,
  "predict": "此请求只删除哪个本课索引？",
  "expect": "预期acknowledged:true；缺失时ignore_unavailable允许重做清理。显式点名删除索引及全部数据。三张清理卡完成后，从 A1 到 D7完整重做，不能只重跑建索引恢复新鲜搜索视图。tut-l13-nope按前提未创建，不删其他索引。"
};
  window.ESEXPERIMENTS["ch13-12-cleanup-routed"] = {
  "version": 1,
  "id": "ch13-12-cleanup-routed",
  "title": "清理 · 删除 tut-l13-routed",
  "method": "DELETE",
  "path": "/tut-l13-routed?ignore_unavailable=true",
  "body": null,
  "predict": "此请求只删除哪个本课索引？",
  "expect": "预期acknowledged:true；缺失时ignore_unavailable允许重做清理。显式点名删除索引及全部数据。三张清理卡完成后，从 A1 到 D7完整重做，不能只重跑建索引恢复新鲜搜索视图。tut-l13-nope按前提未创建，不删其他索引。"
};
  window.ESEXPERIMENTS["ch13-38-cleanup-waiting"] = {
  "version": 1,
  "id": "ch13-38-cleanup-waiting",
  "title": "清理 · 删除 tut-l13-waiting",
  "method": "DELETE",
  "path": "/tut-l13-waiting?ignore_unavailable=true",
  "body": null,
  "predict": "此请求只删除哪个本课索引？",
  "expect": "预期acknowledged:true；缺失时ignore_unavailable允许重做清理。显式点名删除索引及全部数据。三张清理卡完成后，从 A1 到 D7完整重做，不能只重跑建索引恢复新鲜搜索视图。tut-l13-nope按前提未创建，不删其他索引。"
};
  window.ESFLOWS = window.ESFLOWS || {};
  window.ESFLOWS["ch13-bulk-group"] = {
  "version": 1,
  "id": "ch13-bulk-group",
  "title": "一次 _bulk:切条目、算路由、按 shard 分组",
  "speed": 2200,
  "steps": [
    {
      "svg": "<svg viewBox=\"0 0 760 300\" xmlns=\"http://www.w3.org/2000/svg\"><defs><marker id=\"ah13s1\" viewBox=\"0 0 10 10\" refX=\"9\" refY=\"5\" markerWidth=\"7\" markerHeight=\"7\" orient=\"auto-start-reverse\"><path d=\"M 0 0 L 10 5 L 0 10 z\" class=\"fig-arrowhead\"/></marker></defs><rect x=\"15\" y=\"25\" width=\"390\" height=\"240\" rx=\"9\" class=\"fig-box-hot fp-pop\"/><text x=\"210\" y=\"50\" text-anchor=\"middle\" class=\"fig-key\">POST /_bulk</text><text x=\"210\" y=\"82\" text-anchor=\"middle\" class=\"fig-sub\">{\"index\":{\"_index\":\"t\",\"_id\":\"1\"}}</text><text x=\"210\" y=\"106\" text-anchor=\"middle\" class=\"fig-sub\">{\"title\":\"A\"}</text><text x=\"210\" y=\"130\" text-anchor=\"middle\" class=\"fig-sub\">{\"create\":{\"_index\":\"t\",\"_id\":\"2\"}}</text><text x=\"210\" y=\"154\" text-anchor=\"middle\" class=\"fig-sub\">{\"title\":\"B\"}</text><text x=\"210\" y=\"178\" text-anchor=\"middle\" class=\"fig-sub\">{\"delete\":{\"_index\":\"t\",\"_id\":\"3\"}}</text><text x=\"210\" y=\"208\" text-anchor=\"middle\" class=\"fig-sub\">(delete 没有 source 行)</text><text x=\"210\" y=\"238\" text-anchor=\"middle\" class=\"fig-sub\">每行(含最后一行)以 \\n 结尾</text><rect x=\"425\" y=\"25\" width=\"320\" height=\"110\" rx=\"9\" class=\"fig-box\"/><text x=\"585\" y=\"50\" text-anchor=\"middle\" class=\"fig-name\">先读 action 再决定行数</text><text x=\"585\" y=\"72\" text-anchor=\"middle\" class=\"fig-sub\">action 行:做什么、写到哪</text><text x=\"585\" y=\"94\" text-anchor=\"middle\" class=\"fig-sub\">source 行:文档 JSON(delete 除外)</text><rect x=\"425\" y=\"155\" width=\"320\" height=\"110\" rx=\"9\" class=\"fig-box\"/><text x=\"585\" y=\"180\" text-anchor=\"middle\" class=\"fig-name\">五行 = 三个条目</text><text x=\"585\" y=\"202\" text-anchor=\"middle\" class=\"fig-sub\">index / create / delete 混批</text><text x=\"585\" y=\"224\" text-anchor=\"middle\" class=\"fig-sub\">条目之间互不担保</text></svg>",
      "note": "演示前提：9.4.0 新建普通 standard、两主、无管道、非分区路由索引 t；_id=2 已存在，1与3不存在。这里只画三项，body 共五行，delete 无第二行。每条完整行含最后一行都以换行结束；不按奇偶固定分组。"
    },
    {
      "svg": "<svg viewBox=\"0 0 760 300\" xmlns=\"http://www.w3.org/2000/svg\"><defs><marker id=\"ah13s2\" viewBox=\"0 0 10 10\" refX=\"9\" refY=\"5\" markerWidth=\"7\" markerHeight=\"7\" orient=\"auto-start-reverse\"><path d=\"M 0 0 L 10 5 L 0 10 z\" class=\"fig-arrowhead\"/></marker></defs><rect x=\"230\" y=\"15\" width=\"300\" height=\"52\" rx=\"9\" class=\"fig-box\"/><text x=\"380\" y=\"37\" text-anchor=\"middle\" class=\"fig-name\">BulkRequestParser 按行切</text><text x=\"380\" y=\"57\" text-anchor=\"middle\" class=\"fig-sub\">action 行此刻解析,非法即 400</text><line x1=\"340\" y1=\"67\" x2=\"137\" y2=\"91\" class=\"fig-arrow\" marker-end=\"url(#ah13s2)\"/><line x1=\"380\" y1=\"67\" x2=\"377\" y2=\"91\" class=\"fig-arrow\" marker-end=\"url(#ah13s2)\"/><line x1=\"420\" y1=\"67\" x2=\"617\" y2=\"91\" class=\"fig-arrow\" marker-end=\"url(#ah13s2)\"/><rect x=\"15\" y=\"95\" width=\"225\" height=\"110\" rx=\"9\" class=\"fig-box-hot fp-pop\"/><text x=\"127\" y=\"120\" text-anchor=\"middle\" class=\"fig-name\">条目[0] index</text><text x=\"127\" y=\"147\" text-anchor=\"middle\" class=\"fig-key\">_id = \"1\"</text><text x=\"127\" y=\"172\" text-anchor=\"middle\" class=\"fig-sub\">source 原样收下</text><text x=\"127\" y=\"192\" text-anchor=\"middle\" class=\"fig-sub\">此刻不解析 JSON</text><rect x=\"265\" y=\"95\" width=\"225\" height=\"110\" rx=\"9\" class=\"fig-box\"/><text x=\"377\" y=\"120\" text-anchor=\"middle\" class=\"fig-name\">条目[1] create</text><text x=\"377\" y=\"147\" text-anchor=\"middle\" class=\"fig-key\">_id = \"2\"</text><text x=\"377\" y=\"172\" text-anchor=\"middle\" class=\"fig-sub\">已存在则 409</text><text x=\"377\" y=\"192\" text-anchor=\"middle\" class=\"fig-sub\">source 原样收下</text><rect x=\"515\" y=\"95\" width=\"225\" height=\"110\" rx=\"9\" class=\"fig-box\"/><text x=\"627\" y=\"120\" text-anchor=\"middle\" class=\"fig-name\">条目[2] delete</text><text x=\"627\" y=\"147\" text-anchor=\"middle\" class=\"fig-key\">_id = \"3\"</text><text x=\"627\" y=\"172\" text-anchor=\"middle\" class=\"fig-sub\">无 source 行</text><text x=\"627\" y=\"192\" text-anchor=\"middle\" class=\"fig-sub\">单行成项</text><rect x=\"15\" y=\"235\" width=\"730\" height=\"55\" rx=\"9\" class=\"fig-box\"/><text x=\"380\" y=\"258\" text-anchor=\"middle\" class=\"fig-sub\">此例 index/create 切字节；update 第二行会立即解析</text><text x=\"380\" y=\"280\" text-anchor=\"middle\" class=\"fig-sub\">按操作序号回填；delete 只有一行</text></svg>",
      "note": "此例 index/create 第二行只切字节，普通无管道写入再解析文档；update 的第二行会直接解析，坏 JSON 可在入口报400。入口支持增量拆批，后续解析失败不会回滚先前已执行块。每项保留操作编号，不是物理行号。"
    },
    {
      "svg": "<svg viewBox=\"0 0 760 300\" xmlns=\"http://www.w3.org/2000/svg\"><defs><marker id=\"ah13s3\" viewBox=\"0 0 10 10\" refX=\"9\" refY=\"5\" markerWidth=\"7\" markerHeight=\"7\" orient=\"auto-start-reverse\"><path d=\"M 0 0 L 10 5 L 0 10 z\" class=\"fig-arrowhead\"/></marker></defs><rect x=\"15\" y=\"15\" width=\"225\" height=\"64\" rx=\"9\" class=\"fig-box\"/><text x=\"127\" y=\"38\" text-anchor=\"middle\" class=\"fig-name\">index · _id=\"1\"</text><text x=\"127\" y=\"58\" text-anchor=\"middle\" class=\"fig-sub\">无 routing,键 = _id</text><line x1=\"127\" y1=\"79\" x2=\"127\" y2=\"103\" class=\"fig-arrow\" marker-end=\"url(#ah13s3)\"/><rect x=\"15\" y=\"107\" width=\"225\" height=\"58\" rx=\"9\" class=\"fig-box\"/><text x=\"127\" y=\"130\" text-anchor=\"middle\" class=\"fig-key\">Murmur3(\"1\")</text><text x=\"127\" y=\"150\" text-anchor=\"middle\" class=\"fig-sub\">-126235597</text><line x1=\"127\" y1=\"165\" x2=\"127\" y2=\"191\" class=\"fig-arrow\" marker-end=\"url(#ah13s3)\"/><rect x=\"15\" y=\"195\" width=\"225\" height=\"56\" rx=\"9\" class=\"fig-box\"/><text x=\"127\" y=\"218\" text-anchor=\"middle\" class=\"fig-key\">floorMod(…,2)</text><text x=\"127\" y=\"238\" text-anchor=\"middle\" class=\"fig-sub\">= 1 → shard 1</text><rect x=\"265\" y=\"15\" width=\"225\" height=\"64\" rx=\"9\" class=\"fig-box\"/><text x=\"377\" y=\"38\" text-anchor=\"middle\" class=\"fig-name\">create · _id=\"2\"</text><text x=\"377\" y=\"58\" text-anchor=\"middle\" class=\"fig-sub\">无 routing,键 = _id</text><line x1=\"377\" y1=\"79\" x2=\"377\" y2=\"103\" class=\"fig-arrow\" marker-end=\"url(#ah13s3)\"/><rect x=\"265\" y=\"107\" width=\"225\" height=\"58\" rx=\"9\" class=\"fig-box\"/><text x=\"377\" y=\"130\" text-anchor=\"middle\" class=\"fig-key\">Murmur3(\"2\")</text><text x=\"377\" y=\"150\" text-anchor=\"middle\" class=\"fig-sub\">-303927213</text><line x1=\"377\" y1=\"165\" x2=\"377\" y2=\"191\" class=\"fig-arrow\" marker-end=\"url(#ah13s3)\"/><rect x=\"265\" y=\"195\" width=\"225\" height=\"56\" rx=\"9\" class=\"fig-box\"/><text x=\"377\" y=\"218\" text-anchor=\"middle\" class=\"fig-key\">floorMod(…,2)</text><text x=\"377\" y=\"238\" text-anchor=\"middle\" class=\"fig-sub\">= 1 → shard 1</text><rect x=\"515\" y=\"15\" width=\"225\" height=\"64\" rx=\"9\" class=\"fig-box\"/><text x=\"627\" y=\"38\" text-anchor=\"middle\" class=\"fig-name\">delete · _id=\"3\"</text><text x=\"627\" y=\"58\" text-anchor=\"middle\" class=\"fig-sub\">无 routing,键 = _id</text><line x1=\"627\" y1=\"79\" x2=\"627\" y2=\"103\" class=\"fig-arrow\" marker-end=\"url(#ah13s3)\"/><rect x=\"515\" y=\"107\" width=\"225\" height=\"58\" rx=\"9\" class=\"fig-box\"/><text x=\"627\" y=\"130\" text-anchor=\"middle\" class=\"fig-key\">Murmur3(\"3\")</text><text x=\"627\" y=\"150\" text-anchor=\"middle\" class=\"fig-sub\">-1151172406</text><line x1=\"627\" y1=\"165\" x2=\"627\" y2=\"191\" class=\"fig-arrow\" marker-end=\"url(#ah13s3)\"/><rect x=\"515\" y=\"195\" width=\"225\" height=\"56\" rx=\"9\" class=\"fig-box-hot fp-pop\"/><text x=\"627\" y=\"218\" text-anchor=\"middle\" class=\"fig-key\">floorMod(…,2)</text><text x=\"627\" y=\"238\" text-anchor=\"middle\" class=\"fig-sub\">= 0 → shard 0</text><text x=\"380\" y=\"282\" text-anchor=\"middle\" class=\"fig-sub\">新建普通非分区索引；键 = routing ?? _id</text></svg>",
      "note": "限定本例新建普通非分区索引：有效键 routing ?? _id，UTF-16LE seed0 Murmur3 后 floorMod(hash,2)。1与2落shard1，3落shard0。旧创建版本、分区路由、其他 index.mode 与 resharding 不能套用本图公式。"
    },
    {
      "svg": "<svg viewBox=\"0 0 760 300\" xmlns=\"http://www.w3.org/2000/svg\"><defs><marker id=\"ah13s4\" viewBox=\"0 0 10 10\" refX=\"9\" refY=\"5\" markerWidth=\"7\" markerHeight=\"7\" orient=\"auto-start-reverse\"><path d=\"M 0 0 L 10 5 L 0 10 z\" class=\"fig-arrowhead\"/></marker></defs><rect x=\"15\" y=\"15\" width=\"225\" height=\"44\" rx=\"9\" class=\"fig-box\"/><text x=\"127\" y=\"42\" text-anchor=\"middle\" class=\"fig-sub\">条目[0] _id=\"1\"</text><rect x=\"265\" y=\"15\" width=\"225\" height=\"44\" rx=\"9\" class=\"fig-box\"/><text x=\"377\" y=\"42\" text-anchor=\"middle\" class=\"fig-sub\">条目[1] _id=\"2\"</text><rect x=\"515\" y=\"15\" width=\"225\" height=\"44\" rx=\"9\" class=\"fig-box\"/><text x=\"627\" y=\"42\" text-anchor=\"middle\" class=\"fig-sub\">条目[2] _id=\"3\"</text><line x1=\"150\" y1=\"59\" x2=\"235\" y2=\"103\" class=\"fig-arrow\" marker-end=\"url(#ah13s4)\"/><line x1=\"377\" y1=\"59\" x2=\"320\" y2=\"103\" class=\"fig-arrow\" marker-end=\"url(#ah13s4)\"/><line x1=\"604\" y1=\"59\" x2=\"560\" y2=\"103\" class=\"fig-arrow\" marker-end=\"url(#ah13s4)\"/><rect x=\"15\" y=\"107\" width=\"360\" height=\"92\" rx=\"9\" class=\"fig-box-hot fp-pop\"/><text x=\"195\" y=\"132\" text-anchor=\"middle\" class=\"fig-name\">ShardId(t, 1)</text><text x=\"195\" y=\"157\" text-anchor=\"middle\" class=\"fig-key\">BulkShardRequest</text><text x=\"195\" y=\"180\" text-anchor=\"middle\" class=\"fig-sub\">条目[0] + 条目[1]</text><rect x=\"385\" y=\"107\" width=\"360\" height=\"92\" rx=\"9\" class=\"fig-box-hot fp-pop\"/><text x=\"565\" y=\"132\" text-anchor=\"middle\" class=\"fig-name\">ShardId(t, 0)</text><text x=\"565\" y=\"157\" text-anchor=\"middle\" class=\"fig-key\">BulkShardRequest</text><text x=\"565\" y=\"180\" text-anchor=\"middle\" class=\"fig-sub\">条目[2]</text><line x1=\"195\" y1=\"199\" x2=\"195\" y2=\"223\" class=\"fig-arrow\" marker-end=\"url(#ah13s4)\"/><line x1=\"565\" y1=\"199\" x2=\"565\" y2=\"223\" class=\"fig-arrow\" marker-end=\"url(#ah13s4)\"/><rect x=\"15\" y=\"227\" width=\"360\" height=\"52\" rx=\"9\" class=\"fig-box\"/><text x=\"195\" y=\"250\" text-anchor=\"middle\" class=\"fig-name\">shard 1 primary</text><text x=\"195\" y=\"270\" text-anchor=\"middle\" class=\"fig-sub\">并行发出</text><rect x=\"385\" y=\"227\" width=\"360\" height=\"52\" rx=\"9\" class=\"fig-box\"/><text x=\"565\" y=\"250\" text-anchor=\"middle\" class=\"fig-name\">shard 0 primary</text><text x=\"565\" y=\"270\" text-anchor=\"middle\" class=\"fig-sub\">并行发出</text><text x=\"380\" y=\"294\" text-anchor=\"middle\" class=\"fig-sub\">executeLocally 在本节点启动;ReroutePhase 转发到 primary 所在节点</text></svg>",
      "note": "管道处理在路由分组之前。本例无管道，BulkOperation 按完整 ShardId 分组；保留各项编号，不同组可并发推进。executeLocally 先启动本地 action，再路由到primary；协调与primary可在同一节点。本图省略增量拆批与重试。"
    },
    {
      "svg": "<svg viewBox=\"0 0 760 300\" xmlns=\"http://www.w3.org/2000/svg\"><defs><marker id=\"ah13s5\" viewBox=\"0 0 10 10\" refX=\"9\" refY=\"5\" markerWidth=\"7\" markerHeight=\"7\" orient=\"auto-start-reverse\"><path d=\"M 0 0 L 10 5 L 0 10 z\" class=\"fig-arrowhead\"/></marker></defs><rect x=\"15\" y=\"20\" width=\"440\" height=\"170\" rx=\"9\" class=\"fig-box\"/><text x=\"35\" y=\"45\" class=\"fig-name\">shard 1 primary 逐项执行</text><text x=\"35\" y=\"75\" class=\"fig-sub\">条目[0] index _id=\"1\"</text><text x=\"35\" y=\"95\" class=\"fig-key\">→ 201 created,由 primary 分配 seq_no</text><text x=\"35\" y=\"120\" class=\"fig-sub\">条目[1] create _id=\"2\"(已存在)</text><text x=\"35\" y=\"140\" class=\"fig-key\" style=\"fill: rgb(var(--warn))\">→ 409 版本冲突,未领 seq_no</text><text x=\"35\" y=\"165\" class=\"fig-sub\">失败也 advance(),继续下一项</text><rect x=\"475\" y=\"20\" width=\"270\" height=\"170\" rx=\"9\" class=\"fig-box\"/><text x=\"495\" y=\"45\" class=\"fig-name\">shard 0 primary</text><text x=\"495\" y=\"75\" class=\"fig-sub\">条目[2] delete _id=\"3\"</text><text x=\"495\" y=\"95\" class=\"fig-key\" style=\"fill: rgb(var(--warn))\">→ 404 not_found</text><text x=\"495\" y=\"120\" class=\"fig-sub\">delete 一个不存在的 _id</text><text x=\"495\" y=\"140\" class=\"fig-sub\">不是 failure(无 error 字段)</text><rect x=\"15\" y=\"215\" width=\"730\" height=\"70\" rx=\"9\" class=\"fig-box-hot\"/><text x=\"380\" y=\"238\" text-anchor=\"middle\" class=\"fig-name\">一项失败 ≠ 整批失败</text><text x=\"380\" y=\"260\" text-anchor=\"middle\" class=\"fig-sub\">BulkPrimaryExecutionContext:FAILURE 也 advance() 进下一项</text><text x=\"380\" y=\"278\" text-anchor=\"middle\" class=\"fig-sub\">成功项之后带 正常写入后复制同一 seq_no(细节下一课)</text></svg>",
      "note": "本例混合 delete 的 shard组走逐项路径：index1新建，create2因预存文档409，delete3为404/not_found且无error。成功写由primary分配序号，未领号失败不复制；已领号失败可用noop补齐。没有固定seq_no=0承诺。"
    },
    {
      "svg": "<svg viewBox=\"0 0 760 300\" xmlns=\"http://www.w3.org/2000/svg\"><defs><marker id=\"ah13s6\" viewBox=\"0 0 10 10\" refX=\"9\" refY=\"5\" markerWidth=\"7\" markerHeight=\"7\" orient=\"auto-start-reverse\"><path d=\"M 0 0 L 10 5 L 0 10 z\" class=\"fig-arrowhead\"/></marker></defs><rect x=\"15\" y=\"20\" width=\"730\" height=\"56\" rx=\"9\" class=\"fig-box-hot fp-pop\"/><text x=\"380\" y=\"43\" text-anchor=\"middle\" class=\"fig-name\">HTTP 200 · errors: true</text><text x=\"380\" y=\"65\" text-anchor=\"middle\" class=\"fig-sub\">errors 来自 BulkResponse.hasFailures() 扫 items</text><line x1=\"127\" y1=\"76\" x2=\"127\" y2=\"104\" class=\"fig-arrow\" marker-end=\"url(#ah13s6)\"/><line x1=\"377\" y1=\"76\" x2=\"377\" y2=\"104\" class=\"fig-arrow\" marker-end=\"url(#ah13s6)\"/><line x1=\"627\" y1=\"76\" x2=\"627\" y2=\"104\" class=\"fig-arrow\" marker-end=\"url(#ah13s6)\"/><rect x=\"15\" y=\"108\" width=\"225\" height=\"110\" rx=\"9\" class=\"fig-box\"/><text x=\"127\" y=\"133\" text-anchor=\"middle\" class=\"fig-name\">items[0] · 201</text><text x=\"127\" y=\"158\" text-anchor=\"middle\" class=\"fig-key\">index _id=\"1\"</text><text x=\"127\" y=\"180\" text-anchor=\"middle\" class=\"fig-sub\">created</text><text x=\"127\" y=\"200\" text-anchor=\"middle\" class=\"fig-sub\">正常写入后复制同一 seq_no</text><rect x=\"265\" y=\"108\" width=\"225\" height=\"110\" rx=\"9\" class=\"fig-box\"/><text x=\"377\" y=\"133\" text-anchor=\"middle\" class=\"fig-name\" style=\"fill: rgb(var(--warn))\">items[1] · 409</text><text x=\"377\" y=\"158\" text-anchor=\"middle\" class=\"fig-key\">create 撞已有 _id</text><text x=\"377\" y=\"180\" text-anchor=\"middle\" class=\"fig-sub\">error: version_conflict</text><text x=\"377\" y=\"200\" text-anchor=\"middle\" class=\"fig-sub\">失败只记这一项</text><rect x=\"515\" y=\"108\" width=\"225\" height=\"110\" rx=\"9\" class=\"fig-box\"/><text x=\"627\" y=\"133\" text-anchor=\"middle\" class=\"fig-name\">items[2] · 404</text><text x=\"627\" y=\"158\" text-anchor=\"middle\" class=\"fig-key\">delete _id=\"3\"</text><text x=\"627\" y=\"180\" text-anchor=\"middle\" class=\"fig-sub\">result: not_found</text><text x=\"627\" y=\"200\" text-anchor=\"middle\" class=\"fig-sub\">无 error 字段,不算失败</text><rect x=\"15\" y=\"238\" width=\"730\" height=\"48\" rx=\"9\" class=\"fig-box\"/><text x=\"380\" y=\"268\" text-anchor=\"middle\" class=\"fig-sub\">items 按操作序号回填；逐项检查 error 与 result</text></svg>",
      "note": "正常收集完成后HTTP200、errors:true来自create冲突。delete404/not_found无error，不能仅按status≥400算顶层errors。items按操作序号回填；这不等于跨分片执行顺序。通常副本故障另记_shards，写后/任期故障仍可失败或重试。"
    }
  ]
};
})();
