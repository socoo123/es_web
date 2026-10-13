/* 第28课：40操作卡；固定ID、显式文档门槛、两组可重做实验。 */
(function(){
'use strict';
window.ESEXPERIMENTS=window.ESEXPERIMENTS||{};
window.ESEXPERIMENTS["ch28-00-version"]={
  "version": 1,
  "id": "ch28-00-version",
  "title": "前置 · 核对节点与 Lucene 版本",
  "method": "GET",
  "path": "/",
  "body": null,
  "predict": "本课是哪一版？",
  "expect": "version.number=9.4.0、lucene_version=10.4.0。本课使用 localhost:9200 匿名单节点专用学习集群；有认证时沿用控制台当前凭据。"
};
window.ESEXPERIMENTS["ch28-00-mode"]={
  "version": 1,
  "id": "ch28-00-mode",
  "title": "前置 · ILM 是否运行",
  "method": "GET",
  "path": "/_ilm/status",
  "body": null,
  "predict": "STOPPED 时还会自动 rollover 吗？",
  "expect": "operation_mode=RUNNING。若不是，先在专用学习集群恢复运行再开始；本课不主动停止全局 ILM。"
};
window.ESEXPERIMENTS["ch28-00-settings"]={
  "version": 1,
  "id": "ch28-00-settings",
  "title": "前置 · 记录 poll 原值与默认空索引保护",
  "method": "GET",
  "path": "/_cluster/settings?include_defaults=true&flat_settings=true",
  "body": null,
  "predict": "null 恢复会揭示哪一层？",
  "expect": "先保存 transient/persistent 的 poll_interval。无覆盖时默认 10m、only_if_has_documents=true。下文假定 poll 无自定义覆盖；如有，清理时把实验20的 null 改回原 transient 值，不能抹掉已有配置。"
};
window.ESEXPERIMENTS["ch28-01-poll"]={
  "version": 1,
  "id": "ch28-01-poll",
  "title": "A1 · 临时将 poll 调为 15s",
  "method": "PUT",
  "path": "/_cluster/settings",
  "body": {
    "transient": {
      "indices.lifecycle.poll_interval": "15s"
    }
  },
  "predict": "15s 是完成时限吗？",
  "expect": "acknowledged=true。15s 只是周期调度间隔；异步动作、重试与负载会使推进超过一轮。仅用于本课专用学习集群，课末恢复原值。"
};
window.ESEXPERIMENTS["ch28-02-policy"]={
  "version": 1,
  "id": "ch28-02-policy",
  "title": "A2 · 建策略：1m 且至少两篇，再等 2h / 24h",
  "method": "PUT",
  "path": "/_ilm/policy/tut-l28-policy",
  "body": {
    "policy": {
      "phases": {
        "hot": {
          "min_age": "0ms",
          "actions": {
            "rollover": {
              "max_age": "1m",
              "min_docs": 2
            }
          }
        },
        "warm": {
          "min_age": "2h",
          "actions": {
            "readonly": {}
          }
        },
        "delete": {
          "min_age": "24h",
          "actions": {
            "delete": {}
          }
        }
      }
    }
  },
  "predict": "max_age 与 min_docs 怎么组合？",
  "expect": "acknowledged=true；首次创建策略 version=1（需实验9读取）。至少一项 max_* 满足，且全部 min_* 满足。本课 min_docs=2 是显式实验门槛；warm 2h、delete 24h 均从同一个 rollover 零点起算。"
};
window.ESEXPERIMENTS["ch28-03-template"]={
  "version": 1,
  "id": "ch28-03-template",
  "title": "A3 · 模板接力：lifecycle settings 与显式索引配置",
  "method": "PUT",
  "path": "/_index_template/tut-l28-tpl",
  "body": {
    "index_patterns": [
      "tut-l28-logs-*"
    ],
    "priority": 280,
    "template": {
      "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
        "refresh_interval": "-1",
        "index.lifecycle.name": "tut-l28-policy",
        "index.lifecycle.rollover_alias": "tut-l28-logs"
      },
      "mappings": {
        "dynamic": "strict",
        "properties": {
          "msg": {
            "type": "keyword"
          }
        }
      }
    }
  },
  "predict": "新一代如何继续托管？",
  "expect": "模板注入 1P0R、关闭自动 refresh、strict msg mapping 和 lifecycle settings。模板不得再声明 tut-l28-logs 这个 rollover alias 本体；其他别名不在此禁令内。新索引按匹配模板配置，不靠复制旧索引 settings。"
};
window.ESEXPERIMENTS["ch28-04-index"]={
  "version": 1,
  "id": "ch28-04-index",
  "title": "A4 · 首索引显式绑定 write alias",
  "method": "PUT",
  "path": "/tut-l28-logs-000001",
  "body": {
    "aliases": {
      "tut-l28-logs": {
        "is_write_index": true
      }
    }
  },
  "predict": "只写 aliases，配置从哪里来？",
  "expect": "首次200 acknowledged=true；settings/mappings 来自模板。重复创建400 resource_already_exists_exception，须完成清理后重做。名称以数字结尾。本课显式 true；单目标经典 alias 未设置 is_write_index 的兼容分支仍可能是写索引，不能说缺 true 一律失败。"
};
window.ESEXPERIMENTS["ch28-21-health"]={
  "version": 1,
  "id": "ch28-21-health",
  "title": "A5 · 等本章首索引 green",
  "method": "GET",
  "path": "/_cluster/health/tut-l28-logs-000001?wait_for_status=green&timeout=30s",
  "body": null,
  "predict": "单节点为什么能 green？",
  "expect": "status=green、timed_out=false；模板显式0副本。失败先修复分片前提，不能按秒数继续。"
};
window.ESEXPERIMENTS["ch28-22-settings"]={
  "version": 1,
  "id": "ch28-22-settings",
  "title": "A6 · 核对模板落到索引上",
  "method": "GET",
  "path": "/tut-l28-logs-000001/_settings?flat_settings=true",
  "body": null,
  "predict": "哪两条 setting 决定托管与 rollover 目标？",
  "expect": "index.lifecycle.name=tut-l28-policy、index.lifecycle.rollover_alias=tut-l28-logs；1主片0副本、refresh_interval=-1。这不是 ILM 状态，状态用 explain。"
};
window.ESEXPERIMENTS["ch28-23-dry-empty"]={
  "version": 1,
  "id": "ch28-23-dry-empty",
  "title": "A7 · 空索引 dry-run：不创建新一代",
  "method": "POST",
  "path": "/tut-l28-logs/_rollover?dry_run=true",
  "body": {
    "conditions": {
      "max_age": "1m",
      "min_docs": 2
    }
  },
  "predict": "时间到了，空索引就会滚吗？",
  "expect": "dry_run=true、rolled_over=false；min_docs=2 为 false。max_age 的真假随创建年龄变化。请求局部条件只用于本次 dry-run，不修改 ILM 策略；直接 Rollover API 不自动套用 ILM 的默认条件。"
};
window.ESEXPERIMENTS["ch28-05-doc"]={
  "version": 1,
  "id": "ch28-05-doc",
  "title": "A8 · 固定ID写第一篇并 refresh",
  "method": "PUT",
  "path": "/tut-l28-logs/_doc/one?refresh=true",
  "body": {
    "msg": "l28-one"
  },
  "predict": "已有一篇，为什么还不会滚？",
  "expect": "首次201 created；在 rollover 前重复同ID是200 updated，不增文档数。当前策略显式 min_docs=2，只有一篇会持续等待；刷新消除文档统计视图竞态。"
};
window.ESEXPERIMENTS["ch28-06-explain-new"]={
  "version": 1,
  "id": "ch28-06-explain-new",
  "title": "A9 · 观察初始化或已到 Hot 的快照",
  "method": "GET",
  "path": "/tut-l28-logs-000001/_ilm/explain",
  "body": null,
  "predict": "立刻调用必须返回 new 吗？",
  "expect": "managed=true。可能尚在 new，也可能已到 hot；集群状态变化也能推动初始化，不能把 new 当稳定预期。下一卡等待明确的 hot/rollover/check-rollover-ready。"
};
window.ESEXPERIMENTS["ch28-07-explain-hot"]={
  "version": 1,
  "id": "ch28-07-explain-hot",
  "title": "A10 · 重查直到 check-rollover-ready",
  "method": "GET",
  "path": "/tut-l28-logs-000001/_ilm/explain",
  "body": null,
  "predict": "phase_execution 是策略全文吗？",
  "expect": "等待 hot/rollover/check-rollover-ready，phase_execution.version=1，当前相只有 rollover（含 min_docs=2；可有隐式最大分片文档条件）。没有 warm/delete。只有一篇，故无需抢一分钟。ERROR 时先读 step_info；不要继续改策略。"
};
window.ESEXPERIMENTS["ch28-24-dry-one"]={
  "version": 1,
  "id": "ch28-24-dry-one",
  "title": "A11 · 一篇 dry-run：年龄条件与文档门槛分开",
  "method": "POST",
  "path": "/tut-l28-logs/_rollover?dry_run=true",
  "body": {
    "conditions": {
      "max_age": "1m",
      "min_docs": 2
    }
  },
  "predict": "超过一分钟后 rolled_over 会变 true 吗？",
  "expect": "dry_run=true、rolled_over=false。即使 max_age=true，min_docs=false 仍阻止 rollover；不创建000002。若要验证年龄条件为true，重查直到它为true，再做下一步；不改变策略。"
};
window.ESEXPERIMENTS["ch28-08-policy-v2"]={
  "version": 1,
  "id": "ch28-08-policy-v2",
  "title": "A12 · 添加 Hot forcemerge，制造缓存分叉",
  "method": "PUT",
  "path": "/_ilm/policy/tut-l28-policy",
  "body": {
    "policy": {
      "phases": {
        "hot": {
          "min_age": "0ms",
          "actions": {
            "rollover": {
              "max_age": "1m",
              "min_docs": 2
            },
            "forcemerge": {
              "max_num_segments": 1
            }
          }
        },
        "warm": {
          "min_age": "2h",
          "actions": {
            "readonly": {}
          }
        },
        "delete": {
          "min_age": "24h",
          "actions": {
            "delete": {}
          }
        }
      }
    }
  },
  "predict": "StepKey 集合变化会覆盖正在运行的相吗？",
  "expect": "acknowledged=true。策略内容变化，version 1→2；本课在 hot/check-rollover-ready 才修改。forcemerge 增加当前相步骤，缓存保留 v1；新索引进入 Hot 用 v2。"
};
window.ESEXPERIMENTS["ch28-09-policy-get"]={
  "version": 1,
  "id": "ch28-09-policy-get",
  "title": "A13 · 读取活策略版本与 Hot actions",
  "method": "GET",
  "path": "/_ilm/policy/tut-l28-policy",
  "body": null,
  "predict": "相同策略再 PUT 一次一定+1吗？",
  "expect": "version=2、Hot 有 rollover 与 forcemerge。相同策略与相同安全headers可视为 no-op，版本不增；这里只对实际内容变更预期+1。全文的 warm/delete 与下条缓存相对照。"
};
window.ESEXPERIMENTS["ch28-10-explain-after"]={
  "version": 1,
  "id": "ch28-10-explain-after",
  "title": "A14 · 老索引继续执行 v1 的 Hot",
  "method": "GET",
  "path": "/tut-l28-logs-000001/_ilm/explain",
  "body": null,
  "predict": "缓存是否仍只有 rollover？",
  "expect": "仍 check-rollover-ready、phase_execution.version=1、actions 只有 rollover。当前step仍存在但该相 StepKey 集合不同，故不安全刷新；单篇门槛保证观察稳定。"
};
window.ESEXPERIMENTS["ch28-25-release"]={
  "version": 1,
  "id": "ch28-25-release",
  "title": "A15 · 固定ID第二篇：放行文档门槛",
  "method": "PUT",
  "path": "/tut-l28-logs/_doc/two?refresh=true",
  "body": {
    "msg": "l28-two"
  },
  "predict": "所有 min_* 满足后还需什么？",
  "expect": "首次201 created；当前000001有两篇且显式刷新。此前已确认 max_age=true，则下一轮可检查满足；异步多步推进不承诺80秒内完成。放行后不要重复前面的写卡，等实际 alias 和 explain。"
};
window.ESEXPERIMENTS["ch28-26-count"]={
  "version": 1,
  "id": "ch28-26-count",
  "title": "A16 · 核对旧索引两篇文档",
  "method": "GET",
  "path": "/tut-l28-logs-000001/_count",
  "body": null,
  "predict": "rollover 后旧索引的两篇会迁走吗？",
  "expect": "count=2。rollover 创建新的写索引，旧文档保留在000001；它不会把文档搬到000002。"
};
window.ESEXPERIMENTS["ch28-11-wait-cat"]={
  "version": 1,
  "id": "ch28-11-wait-cat",
  "title": "A17 · 重查直到两个明确索引出现",
  "method": "GET",
  "path": "/_cat/indices/tut-l28-logs-000001,tut-l28-logs-000002?v&h=index,docs.count,status,health",
  "body": null,
  "predict": "应看到两个还是三个索引？",
  "expect": "等待两行：000001两篇、000002零篇。只要新索引为空且 min_docs=2 就不会继续滚；若尚只有一行继续查。不要以固定80秒代替条件。"
};
window.ESEXPERIMENTS["ch28-12-alias-flip"]={
  "version": 1,
  "id": "ch28-12-alias-flip",
  "title": "A18 · 写指针是否翻转",
  "method": "GET",
  "path": "/tut-l28-logs/_alias",
  "body": null,
  "predict": "旧索引还在 alias 下吗？",
  "expect": "000001 aliases.tut-l28-logs.is_write_index=false；000002为true。旧索引仍是读别名的一部分；写入以新一代为目标。"
};
window.ESEXPERIMENTS["ch28-13-explain-both"]={
  "version": 1,
  "id": "ch28-13-explain-both",
  "title": "A19 · 等老相 complete 与新相 v2 同屏",
  "method": "GET",
  "path": "/tut-l28-logs-000001,tut-l28-logs-000002/_ilm/explain",
  "body": null,
  "predict": "两条索引会共享一份 phase_execution 吗？",
  "expect": "等待000001 hot/complete、缓存v1且只有rollover；000002 managed=true、hot/check-rollover-ready、缓存v2含forcemerge。老索引 lifecycle_date_millis 已取 rollover 时刻；warm/delete 尚未到期。本课不等待真实2h/24h动作。"
};
window.ESEXPERIMENTS["ch28-27-old-settings"]={
  "version": 1,
  "id": "ch28-27-old-settings",
  "title": "A20 · indexing_complete 与新代配置",
  "method": "GET",
  "path": "/tut-l28-logs-000001,tut-l28-logs-000002/_settings?flat_settings=true",
  "body": null,
  "predict": "indexing_complete 是只读开关吗？",
  "expect": "旧索引 index.lifecycle.indexing_complete=true；新索引仍由模板托管。该标记不是 index.blocks.write；有权限时直接写旧索引仍可能成功，本课只经 write alias 写。"
};
window.ESEXPERIMENTS["ch28-28-new-doc"]={
  "version": 1,
  "id": "ch28-28-new-doc",
  "title": "A21 · 经 alias 写到新一代",
  "method": "PUT",
  "path": "/tut-l28-logs/_doc/after?refresh=true",
  "body": {
    "msg": "l28-after"
  },
  "predict": "响应 _index 是谁？",
  "expect": "首次201 created、_index=tut-l28-logs-000002，新代一篇仍未满足min_docs=2。重复200 updated。与旧两篇对照；再加文档可能继续滚，清理前不要增加其他文档。"
};
window.ESEXPERIMENTS["ch28-14-delete-inuse"]={
  "version": 1,
  "id": "ch28-14-delete-inuse",
  "title": "A22 · 策略被引用：删除预期400",
  "method": "DELETE",
  "path": "/_ilm/policy/tut-l28-policy",
  "body": null,
  "predict": "模板引用与索引引用是同一个检查吗？",
  "expect": "400 illegal_argument_exception，reason含 in use by one or more indices；本课索引仍设置该策略名。检查遍历索引元数据的策略名，不是单独维护的引用计数。"
};
window.ESEXPERIMENTS["ch28-15-wildcard"]={
  "version": 1,
  "id": "ch28-15-wildcard",
  "title": "A23 · 默认禁止通配符删除",
  "method": "DELETE",
  "path": "/tut-l28-*",
  "body": null,
  "predict": "默认保护开启时是什么状态？",
  "expect": "本课专用学习节点 destructive_requires_name=true，400且 reason 含 Wildcard expressions or all indices are not allowed。如该保护被关闭，此操作会删除本章索引；先核对节点配置。本课不修改该保护开关。"
};
window.ESEXPERIMENTS["ch28-29-safe-policy"]={
  "version": 1,
  "id": "ch28-29-safe-policy",
  "title": "B1 · 独立策略：同一组步骤的条件更新",
  "method": "PUT",
  "path": "/_ilm/policy/tut-l28-safe-policy",
  "body": {
    "policy": {
      "phases": {
        "hot": {
          "actions": {
            "rollover": {
              "max_age": "1m",
              "min_docs": 2
            }
          }
        }
      }
    }
  },
  "predict": "B组是否影响A组？",
  "expect": "首次策略版本1。使用另一个策略名和索引/alias，不改A组；空索引由显式min_docs2保持等待。"
};
window.ESEXPERIMENTS["ch28-30-safe-index"]={
  "version": 1,
  "id": "ch28-30-safe-index",
  "title": "B2 · 独立空索引，显式配置",
  "method": "PUT",
  "path": "/tut-l28-safe-000001",
  "body": {
    "settings": {
      "number_of_shards": 1,
      "number_of_replicas": 0,
      "refresh_interval": "-1",
      "index.lifecycle.name": "tut-l28-safe-policy",
      "index.lifecycle.rollover_alias": "tut-l28-safe"
    },
    "mappings": {
      "dynamic": "strict",
      "properties": {
        "msg": {
          "type": "keyword"
        }
      }
    },
    "aliases": {
      "tut-l28-safe": {
        "is_write_index": true
      }
    }
  },
  "predict": "空索引能否稳定停在rollover等待？",
  "expect": "首次200，配置1P0R。该名称不匹配A组模板；B组不实际rollover，无需接力模板。重复创建400；结束时显式删该索引再删策略。"
};
window.ESEXPERIMENTS["ch28-31-safe-hot"]={
  "version": 1,
  "id": "ch28-31-safe-hot",
  "title": "B3 · 等独立索引缓存v1",
  "method": "GET",
  "path": "/tut-l28-safe-000001/_ilm/explain",
  "body": null,
  "predict": "当前StepKey是哪一组？",
  "expect": "重查直到hot/rollover/check-rollover-ready、phase_execution.version=1、max_age=1m。无需写文档；ERROR先修复。"
};
window.ESEXPERIMENTS["ch28-32-safe-update"]={
  "version": 1,
  "id": "ch28-32-safe-update",
  "title": "B4 · 只改 max_age 为10m",
  "method": "PUT",
  "path": "/_ilm/policy/tut-l28-safe-policy",
  "body": {
    "policy": {
      "phases": {
        "hot": {
          "actions": {
            "rollover": {
              "max_age": "10m",
              "min_docs": 2
            }
          }
        }
      }
    }
  },
  "predict": "StepKey集合改变吗？",
  "expect": "acknowledged=true，实际内容变更至v2。步骤集合不变且当前步骤仍在，缓存可以安全刷新；空索引仍未放行。"
};
window.ESEXPERIMENTS["ch28-33-safe-explain"]={
  "version": 1,
  "id": "ch28-33-safe-explain",
  "title": "B5 · 验证缓存也刷新为v2/10m",
  "method": "GET",
  "path": "/tut-l28-safe-000001/_ilm/explain",
  "body": null,
  "predict": "与A组加forcemerge的结果相反吗？",
  "expect": "重查直到仍check-rollover-ready、phase_execution.version=2、max_age=10m。这里只改本策略条件，下一次周期检查采用新条件；不承诺已经发出的异步操作立即撤销。"
};
window.ESEXPERIMENTS["ch28-34-safe-del-index"]={
  "version": 1,
  "id": "ch28-34-safe-del-index",
  "title": "B6 · 点名删除B组索引",
  "method": "DELETE",
  "path": "/tut-l28-safe-000001",
  "body": null,
  "predict": "需要先删除策略吗？",
  "expect": "200 acknowledged=true；先去除索引引用。重复404 index_not_found_exception，须核对已不存在。"
};
window.ESEXPERIMENTS["ch28-35-safe-del-policy"]={
  "version": 1,
  "id": "ch28-35-safe-del-policy",
  "title": "B7 · 删除B组策略",
  "method": "DELETE",
  "path": "/_ilm/policy/tut-l28-safe-policy",
  "body": null,
  "predict": "B组引用是否已清？",
  "expect": "200 acknowledged=true；重复404 resource_not_found_exception。本课没有B组接力模板需要清理。"
};
window.ESEXPERIMENTS["ch28-16-del-1"]={
  "version": 1,
  "id": "ch28-16-del-1",
  "title": "清理1 · 显式删除000001",
  "method": "DELETE",
  "path": "/tut-l28-logs-000001",
  "body": null,
  "predict": "需要先摘alias吗？",
  "expect": "200 acknowledged=true，alias对应条目一起移除。重复404代表已不存在；若中途终止仍须清理其他本章资源。"
};
window.ESEXPERIMENTS["ch28-17-del-2"]={
  "version": 1,
  "id": "ch28-17-del-2",
  "title": "清理2 · 显式删除000002",
  "method": "DELETE",
  "path": "/tut-l28-logs-000002",
  "body": null,
  "predict": "最后一条alias会如何？",
  "expect": "200 acknowledged=true，最后一条alias一起移除。若未rollover该索引404，仍继续删模板与策略；若生成更多代，先GET本章索引列出精确名称再逐个清理。"
};
window.ESEXPERIMENTS["ch28-18-del-tpl-policy"]={
  "version": 1,
  "id": "ch28-18-del-tpl-policy",
  "title": "清理3 · 删除接力模板",
  "method": "DELETE",
  "path": "/_index_template/tut-l28-tpl",
  "body": null,
  "predict": "该请求同时删策略吗？",
  "expect": "200 acknowledged=true，仅删除模板；策略由下一卡删除。模板删除不回改已经存在的索引配置。重复404表示模板已不存在。"
};
window.ESEXPERIMENTS["ch28-19-del-policy"]={
  "version": 1,
  "id": "ch28-19-del-policy",
  "title": "清理4 · 删除A组策略",
  "method": "DELETE",
  "path": "/_ilm/policy/tut-l28-policy",
  "body": null,
  "predict": "与A22相同请求为什么能200？",
  "expect": "200 acknowledged=true，已无索引引用。重复404代表策略已不存在；400则列出仍引用本策略的索引再按明确名称清理。"
};
window.ESEXPERIMENTS["ch28-20-restore"]={
  "version": 1,
  "id": "ch28-20-restore",
  "title": "清理5 · 恢复原poll配置",
  "method": "PUT",
  "path": "/_cluster/settings",
  "body": {
    "transient": {
      "indices.lifecycle.poll_interval": null
    }
  },
  "predict": "null 总是回默认10m吗？",
  "expect": "无persistent或节点覆盖时回默认10m；有覆盖则揭示下一层值。若开始有自定义transient，请把body改回记录的值。本课不把旧配置抹成默认。"
};
window.ESEXPERIMENTS["ch28-36-final-head"]={
  "version": 1,
  "id": "ch28-36-final-head",
  "title": "清理6 · 三个实验索引均应不存在",
  "method": "HEAD",
  "path": "/tut-l28-logs-000001,tut-l28-logs-000002,tut-l28-safe-000001",
  "body": null,
  "predict": "HEAD有JSON响应体吗？",
  "expect": "404且无响应体。该合并请求不能单独证明每个名字不存在；验收脚本还逐个HEAD404。重做前也可通过CAT核对本章命名空间没有遗留代。"
};
window.ESEXPERIMENTS["ch28-37-settings-check"]={
  "version": 1,
  "id": "ch28-37-settings-check",
  "title": "清理7 · 验证poll已恢复原值",
  "method": "GET",
  "path": "/_cluster/settings?include_defaults=true&flat_settings=true",
  "body": null,
  "predict": "可以开始完整重做了吗？",
  "expect": "与前置记录对照：本课15s覆盖已去除或恢复原值；模板/策略/索引均清理后从前置→A1开始。固定ID重复写不增加文档，但重复创建不是完整重做。"
};
function box(x,y,w,h,hot){return '<rect x="'+x+'" y="'+y+'" width="'+w+'" height="'+h+'" rx="9" class="'+(hot?'fig-box-hot':'fig-box')+'"/>';}
function text(x,y,s,cls){return '<text x="'+x+'" y="'+y+'" text-anchor="middle" class="'+cls+'">'+s+'</text>';}
function snapshot(d){return '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">'+box(15,12,730,46,true)+text(380,41,d[0],'fig-name')+box(15,76,355,96,false)+text(192,99,d[1],'fig-name')+text(192,126,d[2],'fig-sub')+text(192,153,d[3],'fig-sub')+box(390,76,355,96,false)+text(567,99,d[4],'fig-name')+text(567,126,d[5],'fig-sub')+text(567,153,d[6],'fig-sub')+box(15,190,730,42,false)+text(380,216,d[7],'fig-sub')+box(15,246,730,40,true)+text(380,271,d[8],'fig-sub')+'</svg>';}
window.ESFLOWS=window.ESFLOWS||{};
window.ESFLOWS['ch28-ilm-rollover']={version:1,id:'ch28-ilm-rollover',title:'一分钟条件与受控rollover：七步机制',speed:2400,steps:[{"d": ["搭好前提", "策略与模板", "max_age=1m，min_docs=2", "首索引绑定 write alias", "专用学习集群", "1主片0副本，strict mapping", "poll临时15s，记录原值", "15s是调度周期，不是完成时限", "缩短poll只用于学习；所有写入显式refresh。"], "note": "缩短poll只用于学习；所有写入显式refresh。"}, {"d": ["观察稳定的等待", "首索引000001", "初始化可能已经到hot", "等待 check-rollover-ready", "当前相缓存v1", "phase_execution只有Hot", "不能当成策略全文", "先写一篇，min_docs2仍不满足", "稳定观察无需抢一分钟；new是瞬时快照，不是必经响应。"], "note": "稳定观察无需抢一分钟；new是瞬时快照，不是必经响应。"}, {"d": ["拆开两种条件", "rollover年龄条件", "max_age从索引创建起算", "至少一项max条件成立", "显式文档门槛", "全部min条件都要成立", "本课min_docs2，一篇不够", "dry-run只评估，不建000002", "无显式min_docs/min_primary_shard_docs时，ILM默认补min_docs1。"], "note": "无显式min_docs/min_primary_shard_docs时，ILM默认补min_docs1。"}, {"d": ["先分叉，再放行", "活策略更新v2", "在Hot添加forcemerge", "StepKey集合发生变化", "老索引保留v1", "当前缓存仍只有rollover", "新索引入Hot读取v2", "再写第二篇并refresh，放行文档门槛", "条件满足后依次执行rollover及收尾；不承诺固定80秒。"], "note": "条件满足后依次执行rollover及收尾；不承诺固定80秒。"}, {"d": ["新旧索引各有职责", "000002接写", "匹配模板注入lifecycle设置", "alias写指针=true", "000001收尾", "等待新片→更新生命周期零点", "indexing_complete=true", "该标记不是只读开关；直接写旧索引仍可能成功", "rollover不搬旧文档。只经alias写；本课不直接写旧索引。"], "note": "rollover不搬旧文档。只经alias写；本课不直接写旧索引。"}, {"d": ["同一个生命周期零点", "warm门槛", "rollover零点+2h", "还需前相步骤完成", "delete门槛", "同一个rollover零点+24h", "不是进入warm后再加24h", "未来相门槛从活策略读取；换相装入该相最新定义", "本课不等待真实2h/24h；显式origination_date会改变阶段计时口径。"], "note": "本课不等待真实2h/24h；显式origination_date会改变阶段计时口径。"}, {"d": ["条件更新与清理", "只改max_age", "B组StepKey集合不变", "缓存安全刷新v2/10m", "按序恢复", "显式删索引→模板→策略", "poll恢复前置记录原值", "相同策略PUT可no-op；null可能揭示persistent覆盖", "重新运行须清完本章所有资源；data stream仍需ILM模板配置。"], "note": "重新运行须清完本章所有资源；data stream仍需ILM模板配置。"}].map(function(s){return {svg:snapshot(s.d),note:s.note};})};
})();
