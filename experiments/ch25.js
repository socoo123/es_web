/* 第 25 课：可重复操作与七步熔断机制示意。 */
(function () {
  'use strict';
  var operations = [
  {
    "version": 1,
    "id": "ch25-version",
    "title": "前提 1 · 确认 ES 9.4.0",
    "method": "GET",
    "path": "/",
    "body": null,
    "predict": "运行节点是哪一版？",
    "expect": "version.number 应为 9.4.0、lucene_version 为 10.4.0。版本或端点不同先停；本轮云端服务启动失败，这些是待实测预期。"
  },
  {
    "version": 1,
    "id": "ch25-node-settings",
    "title": "前提 2 · 单节点与节点级 breaker 配置",
    "method": "GET",
    "path": "/_nodes/settings,jvm?flat_settings=true&filter_path=nodes.*.name,nodes.*.settings.indices.breaker.*,nodes.*.settings.network.breaker.*,nodes.*.settings.indexing_pressure.*,nodes.*.jvm.mem.heap_max_in_bytes",
    "body": null,
    "predict": "节点数、堆和节点配置能满足对照吗？",
    "expect": "必须只有本地专用教程节点；记录 heap_max_in_bytes 与节点级配置。无相关键不代表没有默认值；默认值和集群覆盖还要看下一张卡。"
  },
  {
    "version": 1,
    "id": "ch25-settings-before",
    "title": "前提 3 · 记录原值，确认允许重置到原点",
    "method": "GET",
    "path": "/_cluster/settings?include_defaults=true&flat_settings=true&filter_path=persistent.indices.breaker.*,transient.indices.breaker.*,defaults.indices.breaker.*",
    "body": null,
    "predict": "原先 transient / persistent 有覆盖吗？",
    "expect": "本组仅在 request.limit 的两层集群覆盖均不存在、节点使用默认 memory 类型和 overhead=1 时继续。保存响应和实际限额；已有覆盖就跳过 B 组，另用干净教程节点，不覆盖原值。"
  },
  {
    "version": 1,
    "id": "ch25-00-stats",
    "title": "前提 4 · 读取底层字节账与跳闸基线",
    "method": "GET",
    "path": "/_nodes/_local/stats/breaker?filter_path=nodes.*.name,nodes.*.breakers",
    "body": null,
    "predict": "estimated 已乘 overhead 吗？Parent 是子账总和吗？",
    "expect": "子账 estimated_size_in_bytes 是原始 used；overhead 单列。Parent 默认是真实堆的采样，false 模式才汇总所有子账 used×overhead。记录 request.tripped 和限额；并非总共只有四种 breaker。"
  },
  {
    "version": 1,
    "id": "ch25-01-cat",
    "title": "前提 5 · CAT 按节点辨认账本",
    "method": "GET",
    "path": "/_cat/circuit_breaker?v&h=node_id,breaker,limit_bytes,estimated_bytes,tripped,overhead",
    "body": null,
    "predict": "同样名字出现多次代表什么？",
    "expect": "每个节点各一行；只在单节点前提下直接对照。Parent 与子账来自不同统计口径，且采样有时差，不要求 Parent 必大于三子之和。"
  },
  {
    "version": 1,
    "id": "ch25-head-before",
    "title": "A1 · 确认专属索引不存在",
    "method": "HEAD",
    "path": "/tut-l25-card",
    "body": null,
    "predict": "200 还是 404？",
    "expect": "404 是起点。200 时先完成本章清理再重做 A；不要在旧数据上继续。"
  },
  {
    "version": 1,
    "id": "ch25-02-setup",
    "title": "A2 · 建立 1P0R keyword 索引",
    "method": "PUT",
    "path": "/tut-l25-card",
    "body": {
      "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
        "auto_expand_replicas": "false"
      },
      "mappings": {
        "dynamic": "strict",
        "properties": {
          "user_id": {
            "type": "keyword"
          }
        }
      }
    },
    "predict": "配置哪里限定单分片数据集？",
    "expect": "acknowledged=true；单主分片、零副本且关闭自动扩副本。keyword 支持 terms；并不承诺只走某一种收集实现。已存在的索引会失败，回 A1。"
  },
  {
    "version": 1,
    "id": "ch25-wait-green",
    "title": "A3 · 等本章主分片就绪",
    "method": "GET",
    "path": "/_cluster/health/tut-l25-card?wait_for_status=green&timeout=30s",
    "body": null,
    "predict": "是否 timed_out？",
    "expect": "status=green 且 timed_out=false 后继续。这里只观察本章索引；不是全节点内存健康结论。"
  },
  {
    "version": 1,
    "id": "ch25-03-bulk",
    "title": "A4 · 固定 ID 写入 20 文档并 refresh",
    "method": "POST",
    "path": "/tut-l25-card/_bulk?refresh=true",
    "body": "{\"index\":{\"_id\":\"1\"}}\n{\"user_id\":\"u-1\"}\n{\"index\":{\"_id\":\"2\"}}\n{\"user_id\":\"u-2\"}\n{\"index\":{\"_id\":\"3\"}}\n{\"user_id\":\"u-3\"}\n{\"index\":{\"_id\":\"4\"}}\n{\"user_id\":\"u-4\"}\n{\"index\":{\"_id\":\"5\"}}\n{\"user_id\":\"u-5\"}\n{\"index\":{\"_id\":\"6\"}}\n{\"user_id\":\"u-6\"}\n{\"index\":{\"_id\":\"7\"}}\n{\"user_id\":\"u-7\"}\n{\"index\":{\"_id\":\"8\"}}\n{\"user_id\":\"u-8\"}\n{\"index\":{\"_id\":\"9\"}}\n{\"user_id\":\"u-9\"}\n{\"index\":{\"_id\":\"10\"}}\n{\"user_id\":\"u-10\"}\n{\"index\":{\"_id\":\"11\"}}\n{\"user_id\":\"u-11\"}\n{\"index\":{\"_id\":\"12\"}}\n{\"user_id\":\"u-12\"}\n{\"index\":{\"_id\":\"13\"}}\n{\"user_id\":\"u-13\"}\n{\"index\":{\"_id\":\"14\"}}\n{\"user_id\":\"u-14\"}\n{\"index\":{\"_id\":\"15\"}}\n{\"user_id\":\"u-15\"}\n{\"index\":{\"_id\":\"16\"}}\n{\"user_id\":\"u-16\"}\n{\"index\":{\"_id\":\"17\"}}\n{\"user_id\":\"u-17\"}\n{\"index\":{\"_id\":\"18\"}}\n{\"user_id\":\"u-18\"}\n{\"index\":{\"_id\":\"19\"}}\n{\"user_id\":\"u-19\"}\n{\"index\":{\"_id\":\"20\"}}\n{\"user_id\":\"u-20\"}\n",
    "predict": "首次和重复点击的 items.result 有何不同？",
    "expect": "检查 errors=false、20 items。首次 created，重复点击 updated；固定 ID 保持 20 文档。refresh=true 明确搜索可见；任一 item 错误先恢复前提再重做。"
  },
  {
    "version": 1,
    "id": "ch25-count",
    "title": "A5 · 核对可见数据恰为 20",
    "method": "GET",
    "path": "/tut-l25-card/_count",
    "body": null,
    "predict": "重复点击 bulk 会变成 40 吗？",
    "expect": "count=20 且 _shards.failed=0；固定 ID 不重复增文档。禁止其他客户端写入本章索引，数量不符就清理重做 A。"
  },
  {
    "version": 1,
    "id": "ch25-04-terms-ok",
    "title": "A6 · 基线限额下 terms 返回两个桶",
    "method": "POST",
    "path": "/tut-l25-card/_search?request_cache=false&filter_path=aggregations.users.buckets,aggregations.users.sum_other_doc_count",
    "body": {
      "size": 0,
      "aggs": {
        "users": {
          "terms": {
            "field": "user_id",
            "size": 2,
            "shard_size": 20,
            "order": {
              "_key": "asc"
            }
          }
        }
      }
    },
    "predict": "size=2 能否给全部收集内存设上限？",
    "expect": "在基线堆有余量时 200，桶 u-1、u-10 各 doc_count=1，sum_other_doc_count=18。按 _key 升序并显式 shard_size=20；响应窗口不是总内存限额。失败时不进入 B。"
  },
  {
    "version": 1,
    "id": "ch25-05-limit-1kb",
    "title": "B1 · 临时将 request 限额设为 1kb",
    "method": "PUT",
    "path": "/_cluster/settings",
    "body": {
      "transient": {
        "indices.breaker.request.limit": "1kb"
      }
    },
    "predict": "改变的是本章索引还是整个集群的各节点？",
    "expect": "只在专用单节点并确认前提 3 无原覆盖后执行。acknowledged=true；这是集群级动态覆盖，会影响其他请求，不是索引参数。必须执行 B6 / 清理，不依赖重启恢复。"
  },
  {
    "version": 1,
    "id": "ch25-settings-limited",
    "title": "B2 · 确认集群覆盖来源",
    "method": "GET",
    "path": "/_cluster/settings?include_defaults=true&flat_settings=true&filter_path=persistent.indices.breaker.*,transient.indices.breaker.*,defaults.indices.breaker.*",
    "body": null,
    "predict": "1kb 出现在哪一层？",
    "expect": "transient.indices.breaker.request.limit=1kb，persistent 仍无该覆盖。若状态与预期不同先清理恢复，不执行熔断请求。"
  },
  {
    "version": 1,
    "id": "ch25-stats-limited",
    "title": "B3 · 记录拒绝前的节点账本",
    "method": "GET",
    "path": "/_nodes/_local/stats/breaker?filter_path=nodes.*.name,nodes.*.breakers",
    "body": null,
    "predict": "limit 字节数和 tripped 基线是多少？",
    "expect": "request.limit_size_in_bytes=1024；记录此时 tripped。只有前提满足且无并发请求、无节点重启，之后才把增量归到 B4。"
  },
  {
    "version": 1,
    "id": "ch25-06-terms-break",
    "title": "B4 · 同一条 terms 触发低限额拒绝",
    "method": "POST",
    "path": "/tut-l25-card/_search?request_cache=false",
    "body": {
      "size": 0,
      "aggs": {
        "users": {
          "terms": {
            "field": "user_id",
            "size": 2,
            "shard_size": 20,
            "order": {
              "_key": "asc"
            }
          }
        }
      }
    },
    "predict": "哪一层拒绝，错误包装怎样查？",
    "expect": "预期 HTTP 429；在 error、root_cause 或 failed_shards 的 reason 链中找 circuit_breaking_exception、[request] 与 preallocate[aggregations]、bytes_limit=1024、TRANSIENT。默认单 agg 先预留 6144 字节，子账在 CAS 前拒绝。若 Parent / 其他错误先发生，恢复并排查前提，不当成同一证据。"
  },
  {
    "version": 1,
    "id": "ch25-07-tripped",
    "title": "B5 · 与拒绝前的计数比较",
    "method": "GET",
    "path": "/_nodes/_local/stats/breaker?filter_path=nodes.*.name,nodes.*.breakers",
    "body": null,
    "predict": "request.tripped 比 B3 增加多少？",
    "expect": "无并发且节点未重启时，request.tripped 应增加；不能把历史 >=1 当成本次实验的证据，也不写死一次 REST 请求只加 1。失败的预留不进入本笔 used；其他活动仍可能改变统计。随后立即 B6。"
  },
  {
    "version": 1,
    "id": "ch25-08-restore",
    "title": "B6 · 删除本轮 transient 覆盖",
    "method": "PUT",
    "path": "/_cluster/settings",
    "body": {
      "transient": {
        "indices.breaker.request.limit": null
      }
    },
    "predict": "null 删除覆盖后一定回 60% 吗？",
    "expect": "acknowledged=true。null 删除 transient 这一层；通常回到 persistent、节点配置或默认。仅本组原先无覆盖且节点默认的前提下应回 60%。若未执行 B1，无需这步；已有原配置的环境不适用本组。"
  },
  {
    "version": 1,
    "id": "ch25-settings-restored",
    "title": "B7 · 确认覆盖已删除",
    "method": "GET",
    "path": "/_cluster/settings?include_defaults=true&flat_settings=true&filter_path=persistent.indices.breaker.*,transient.indices.breaker.*,defaults.indices.breaker.*",
    "body": null,
    "predict": "清理后 transient 和 persistent 是什么？",
    "expect": "本组 request.limit 两层覆盖均应不存在，节点配置保持原值。响应与前提 3 对照；不能只凭 PUT acknowledged 就宣称恢复了实际限额。"
  },
  {
    "version": 1,
    "id": "ch25-09-stats-restored",
    "title": "B8 · 核对实际限额恢复到基线",
    "method": "GET",
    "path": "/_nodes/_local/stats/breaker?filter_path=nodes.*.name,nodes.*.breakers",
    "body": null,
    "predict": "tripped 清零了吗，限额与前提 4 相同吗？",
    "expect": "request.limit_size_in_bytes 应等于前提 4 基线；tripped 在同一 breaker 实例上保持累计，不因 null 清零。用实际堆和字节值比较，不把 1GiB 的 60% 写成 600MiB。"
  },
  {
    "version": 1,
    "id": "ch25-10-terms-ok2",
    "title": "B9 · 再跑同一条 terms",
    "method": "POST",
    "path": "/tut-l25-card/_search?request_cache=false&filter_path=aggregations.users.buckets,aggregations.users.sum_other_doc_count",
    "body": {
      "size": 0,
      "aggs": {
        "users": {
          "terms": {
            "field": "user_id",
            "size": 2,
            "shard_size": 20,
            "order": {
              "_key": "asc"
            }
          }
        }
      }
    },
    "predict": "查询未改，恢复后是否成功？",
    "expect": "在堆有余量、覆盖删除且数据仍为 20 文档时回 200、两个桶与 sum_other=18。恢复限额不保证所有并发或内存状态下都成功；确认 B7、B8 后再解释对照。"
  },
  {
    "version": 1,
    "id": "ch25-11-matchall",
    "title": "B10 · tripped 是历史计数",
    "method": "POST",
    "path": "/tut-l25-card/_search?request_cache=false&filter_path=hits.total",
    "body": {
      "size": 0,
      "track_total_hits": true,
      "query": {
        "match_all": {}
      }
    },
    "predict": "历史计数会直接锁住后续搜索吗？",
    "expect": "预期 hits.total.value=20、relation=eq。tripped 不作准入开关；成功说明该请求此刻通过检查，不能证明 match_all 不耗内存或永远不会触发 Parent。"
  },
  {
    "version": 1,
    "id": "ch25-pressure-before",
    "title": "C1 · 写入压力 current / total 基线",
    "method": "GET",
    "path": "/_nodes/_local/stats/indexing_pressure?human=false",
    "body": null,
    "predict": "累计字节与当前占用能混看吗？",
    "expect": "记录 memory.current、memory.total、rejections 和 limit_in_bytes。节点级统计含其他索引；本组仅在无别的写入时比较。请求完成后 current 可下降、total 累积，不保证立刻为零。"
  },
  {
    "version": 1,
    "id": "ch25-thread-pools",
    "title": "C2 · 读取线程池当前与累计拒绝",
    "method": "GET",
    "path": "/_nodes/_local/stats/thread_pool?filter_path=nodes.*.name,nodes.*.thread_pool.write,nodes.*.thread_pool.write_coordination,nodes.*.thread_pool.search",
    "body": null,
    "predict": "queue 和 rejected 表示同一种数量吗？",
    "expect": "queue 是排队任务数，rejected 是累计拒绝数，不能与字节压力直接相加。429 要结合 error.type / reason 与当时节点指标定位。此卡不主动制造线程池拒绝。"
  },
  {
    "version": 1,
    "id": "ch25-pressure-bulk",
    "title": "C3 · 重写固定 ID，观察另一套账",
    "method": "POST",
    "path": "/tut-l25-card/_bulk?refresh=true",
    "body": "{\"index\":{\"_id\":\"1\"}}\n{\"user_id\":\"u-1\"}\n{\"index\":{\"_id\":\"2\"}}\n{\"user_id\":\"u-2\"}\n{\"index\":{\"_id\":\"3\"}}\n{\"user_id\":\"u-3\"}\n{\"index\":{\"_id\":\"4\"}}\n{\"user_id\":\"u-4\"}\n{\"index\":{\"_id\":\"5\"}}\n{\"user_id\":\"u-5\"}\n{\"index\":{\"_id\":\"6\"}}\n{\"user_id\":\"u-6\"}\n{\"index\":{\"_id\":\"7\"}}\n{\"user_id\":\"u-7\"}\n{\"index\":{\"_id\":\"8\"}}\n{\"user_id\":\"u-8\"}\n{\"index\":{\"_id\":\"9\"}}\n{\"user_id\":\"u-9\"}\n{\"index\":{\"_id\":\"10\"}}\n{\"user_id\":\"u-10\"}\n{\"index\":{\"_id\":\"11\"}}\n{\"user_id\":\"u-11\"}\n{\"index\":{\"_id\":\"12\"}}\n{\"user_id\":\"u-12\"}\n{\"index\":{\"_id\":\"13\"}}\n{\"user_id\":\"u-13\"}\n{\"index\":{\"_id\":\"14\"}}\n{\"user_id\":\"u-14\"}\n{\"index\":{\"_id\":\"15\"}}\n{\"user_id\":\"u-15\"}\n{\"index\":{\"_id\":\"16\"}}\n{\"user_id\":\"u-16\"}\n{\"index\":{\"_id\":\"17\"}}\n{\"user_id\":\"u-17\"}\n{\"index\":{\"_id\":\"18\"}}\n{\"user_id\":\"u-18\"}\n{\"index\":{\"_id\":\"19\"}}\n{\"user_id\":\"u-19\"}\n{\"index\":{\"_id\":\"20\"}}\n{\"user_id\":\"u-20\"}\n",
    "predict": "普通小 bulk 是否必然增加 rejections？",
    "expect": "先完成 B 的恢复检查；errors=false、20 updated，文档数仍 20。小写入用于观察正常计数，不触发背压，也不能用它验证拆 Bulk 的水位分支。"
  },
  {
    "version": 1,
    "id": "ch25-pressure-after",
    "title": "C4 · 对照写入压力累计与当前量",
    "method": "GET",
    "path": "/_nodes/_local/stats/indexing_pressure?human=false",
    "body": null,
    "predict": "total 增长是否等于内存泄漏？",
    "expect": "无其他写入且节点未重启时，coordinating / primary 累计量应增加；current 随资源释放下降。1P0R 不需要产生副本写入压力；rejections 没增加也不能证明未来不会拒绝。"
  },
  {
    "version": 1,
    "id": "ch25-12-restore-again",
    "title": "清理 1 · 已执行 B 时再次删除覆盖",
    "method": "PUT",
    "path": "/_cluster/settings",
    "body": {
      "transient": {
        "indices.breaker.request.limit": null
      }
    },
    "predict": "中途失败能跳过恢复吗？",
    "expect": "如果本轮按前提执行过 B1，这步必须做；删除本轮 transient 覆盖可重复。未执行 B1 或原先有配置就跳过本组变更卡；本章不删除 persistent 或未知原值。"
  },
  {
    "version": 1,
    "id": "ch25-settings-clean",
    "title": "清理 2 · 验证设置与实际限额",
    "method": "GET",
    "path": "/_cluster/settings?include_defaults=true&flat_settings=true&filter_path=persistent.indices.breaker.*,transient.indices.breaker.*,defaults.indices.breaker.*",
    "body": null,
    "predict": "该设置还残留吗？",
    "expect": "与前提 3 对照；本组两层覆盖应无 request.limit。再执行前提 4 的节点统计卡确认基线字节值；设置读取与运行时限额两项都核对后清理索引。"
  },
  {
    "version": 1,
    "id": "ch25-13-cleanup",
    "title": "清理 3 · 点名删除本章索引",
    "method": "DELETE",
    "path": "/tut-l25-card",
    "body": null,
    "predict": "会删除哪些资源？",
    "expect": "仅删除 tut-l25-card 的 20 文档；存在时 acknowledged=true，已删时 404 可接受。先恢复设置，再删索引；没有通配符，其他章节资源不受影响。"
  },
  {
    "version": 1,
    "id": "ch25-head-clean",
    "title": "清理 4 · 核对干净索引起点",
    "method": "HEAD",
    "path": "/tut-l25-card",
    "body": null,
    "predict": "重做前应返回什么？",
    "expect": "404。完整重做从前提 1–5 开始，重新建索引、等 Green 和写入 20 文档；tripped、写入累计量不会因删索引归零，重新记录基线。"
  }
];
  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};
  operations.forEach(function (op) { window.ESEXPERIMENTS[op.id] = op; });
  function escape(s) { return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
  function snapshot(lines, number) {
    var id = 'ch25-step-' + number + '-arrow';
    var s = '<svg viewBox="0 0 760 350" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="' + escape(lines[0]) + '"><defs><marker id="' + id + '" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M 0 0 L 10 5 L 0 10 z" class="fig-arrowhead"/></marker></defs>';
    s += '<rect x="15" y="15" width="730" height="54" rx="9" class="fig-box-hot"/><text x="380" y="47" text-anchor="middle" class="fig-name">' + escape(lines[0]) + '</text>';
    [[15,88],[395,88]].forEach(function (xy, i) {
      s += '<rect x="' + xy[0] + '" y="' + xy[1] + '" width="350" height="136" rx="9" class="fig-box"/>';
      for (var k=0;k<3;k++) s += '<text x="' + (xy[0]+175) + '" y="' + (xy[1]+33+k*34) + '" text-anchor="middle" class="' + (k===0?'fig-key':'fig-sub') + '">' + escape(lines[1+i*3+k]) + '</text>';
    });
    s += '<rect x="15" y="250" width="730" height="76" rx="9" class="fig-box-hot fp-pop"/><text x="380" y="279" text-anchor="middle" class="fig-sub">' + escape(lines[7]) + '</text><text x="380" y="308" text-anchor="middle" class="fig-sub">' + escape(lines[8] || '固定 ES 9.4.0；完整细节见正文与源码入口') + '</text>';
    return s + '</svg>';
  }
  var frames = [["示例家底", "堆容量 H = 1000MiB", "request：50 / 600MiB", "真实堆采样：900MiB", "Parent 默认限额：950MiB", "数值用于算术；实际限额看 API", "不是把 1GiB 当成 1000MiB", "演示正数增量与正限额"], ["提出一笔记账", "原始 bytes = 500MiB", "overhead = 1.0", "由调用方提交估计与 label", "示例合并了多次可能的增量", "6KB 预留会覆盖缓冲内的 5KB", "不能把二者重复相加", "实际分配可有先后两类路径"], ["子账检查与 CAS", "(50 + 500) × 1.0 = 550MiB", "550 ≤ 600MiB：本关通过", "CAS：50 → 550MiB", "冲突时重读 used 并重新比较", "子账超限在 CAS 前拒绝", "本笔不入账；子计数增加", "此时还须继续问 Parent"], ["Parent 测量与复核", "默认总量：900 + 500 = 1400MiB", "首次 1400 > 950MiB", "调用超限策略复核", "G1 模式可尝试 GC 后重新采样", "本例假定复核仍超限", "Parent tripped 增加", "durability 根据全部子账占比"], ["撤销本笔，传递异常", "addWithoutBreaking(-500MiB)", "request：550 → 50MiB", "使用原始 bytes，不乘 overhead", "不再检查子限额或 Parent", "然后向上传递 Parent 异常", "释放账额不等于立即回收堆", "并发活动可改变其他占用"], ["分清拒绝来源", "CircuitBreakingException → 429", "本例 reason 标明 [parent]", "子拒绝会标明 [request] 等", "搜索错误可能包装在 root_cause", "写入压力与线程池可同为 429", "按 type / reason / 指标定位", "健康色衡量分片可用性"], ["恢复与新的准入判断", "删除本轮覆盖并核对原基线", "null 不必然等于默认 60%", "原本有覆盖时不能覆盖再清空", "tripped 累计，不作锁定开关", "下次请求重新接受当前检查", "缩小查询范围、控制并发", "计数需求才考虑 cardinality"]];
  var notes = ["演示 H=1000MiB，request 原始 used=50MiB，overhead=1，子限额600MiB、Parent950MiB，堆采样900MiB。数值为算术示意，非 1GiB 的精确限额；省略其他子账。", "500MiB 是教学用原始记账增量，不代表每次 terms 都预估这么多。6KB 聚合预留会覆盖后续缓冲内的 5KB，不能重复相加。BigArrays 有分配前检查，也有分配后核算。", "550MiB 通过子限额检查，CAS 将本笔记入；冲突会重新检查。若子限额已超，在 CAS 前抛异常，本笔未入账。-1 只跳过子限额检查，仍需问 Parent；0 会立即拒绝。", "默认测量真实堆加本笔预留，false 模式才汇总全部子账 used×overhead。首次超限后策略复核，本例假定仍超限才拒绝。Parent durability 由所有子账估算的 transient / permanent 占比决定。", "Child 捕获 Parent 的异常后，用原始 -bytes 回滚本笔记账，再抛出原异常。此回滚与 JVM GC 不同；拒绝只避免这条受检查路径继续，不保证节点绝无 OOM。", "本例是 Parent 拒绝，reason 必须是 [parent]；低限额实验主要是 [request] 在预留时拒绝。两者 HTTP 都可为429，写入压力与队列拒绝也可为429；必须继续读错误链。", "实验删除本轮 transient 覆盖后，核对两层设置和实际限额与原基线一致。tripped 不锁住下一次请求；成功仍取决于当前占用。cardinality 只在需要近似去重计数时考虑，不等价替换 terms 桶。"];
  window.ESFLOWS = window.ESFLOWS || {};
  window.ESFLOWS['ch25-breaker'] = { version:1, id:'ch25-breaker', title:'一笔记账：子账通过，Parent 拒绝后回滚', speed:2600, steps:frames.map(function (f,i) { return {svg:snapshot(f,i+1),note:notes[i]}; }) };
})();
