/* 第 12 课：固定 9.4.0 源码预期；真实 API 本轮未运行。 */
(function () {
  'use strict';
  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};
  window.ESEXPERIMENTS['ch12-00-version'] = {
  "version": 1,
  "id": "ch12-00-version",
  "title": "A0 · 核对节点版本",
  "method": "GET",
  "path": "/",
  "body": null,
  "predict": "先猜：应看到哪个 ES / Lucene 版本？",
  "expect": "对照：节点应为 9.4.0、Lucene 10.4.0；不同版本先停止按本课固定预期推断。此请求只核对版本，不证明节点具有 ingest 角色或写入权限。"
};

  window.ESEXPERIMENTS['ch12-01-put-fields'] = {
  "version": 1,
  "id": "ch12-01-put-fields",
  "title": "A1 · 注册 set + rename 管道",
  "method": "PUT",
  "path": "/_ingest/pipeline/tut-l12-fields",
  "body": {
    "description": "ch12: set then rename",
    "field_access_pattern": "classic",
    "processors": [
      {
        "set": {
          "field": "environment",
          "value": "production"
        }
      },
      {
        "rename": {
          "field": "hostname",
          "target_field": "host",
          "override": false,
          "ignore_missing": false
        }
      }
    ]
  },
  "predict": "先猜：这一步会创建索引或写入文档吗？",
  "expect": "对照：正常返回 acknowledged:true。定义写入集群状态的 IngestMetadata；节点据此构造本地 Pipeline。只 PUT 管道不建索引、不写文档；同名相同定义可重复，同名不同定义会更新，时间元数据可能变化。"
};

  window.ESEXPERIMENTS['ch12-02-simulate-fields'] = {
  "version": 1,
  "id": "ch12-02-simulate-fields",
  "title": "A2 · 模拟完整输出",
  "method": "POST",
  "path": "/_ingest/pipeline/tut-l12-fields/_simulate",
  "body": {
    "docs": [
      {
        "_index": "tut-l12-probe",
        "_id": "1",
        "_source": {
          "hostname": "web-01",
          "level": "INFO"
        }
      }
    ]
  },
  "predict": "先猜：hostname 会消失吗？会创建 tut-l12-probe 吗？",
  "expect": "对照：HTTP 200，docs[0].doc._source 为 host:web-01、environment:production、level:INFO，无 hostname。_index 只是模拟元数据，不会创建索引或写入；_ingest.timestamp 也不自动进入 _source。"
};

  window.ESEXPERIMENTS['ch12-03-simulate-verbose'] = {
  "version": 1,
  "id": "ch12-03-simulate-verbose",
  "title": "A3 · verbose 看中间状态",
  "method": "POST",
  "path": "/_ingest/pipeline/tut-l12-fields/_simulate?verbose=true",
  "body": {
    "docs": [
      {
        "_index": "tut-l12-probe",
        "_id": "1",
        "_source": {
          "hostname": "web-01",
          "level": "INFO"
        }
      }
    ]
  },
  "predict": "先猜：set 完成时 hostname 是否还在？",
  "expect": "对照：HTTP 200，processor_results 顺序为 set、rename；第一份快照有 hostname 与 environment，第二份有 host 无 hostname。时间与额外元数据以实际返回为准；模拟结果不证明路由 / mapping / final 约束通过。"
};

  window.ESEXPERIMENTS['ch12-04-grok-inline'] = {
  "version": 1,
  "id": "ch12-04-grok-inline",
  "title": "A4 · 内联 grok，再 remove",
  "method": "POST",
  "path": "/_ingest/pipeline/_simulate",
  "body": {
    "pipeline": {
      "description": "parse one log line, inline",
      "processors": [
        {
          "grok": {
            "field": "message",
            "patterns": [
              "%{TIMESTAMP_ISO8601:log_timestamp} %{LOGLEVEL:level} %{GREEDYDATA:log_message}"
            ]
          }
        },
        {
          "remove": {
            "field": "message"
          }
        }
      ]
    },
    "docs": [
      {
        "_source": {
          "message": "2024-01-15T10:30:00 ERROR Out of memory exception"
        }
      },
      {
        "_source": {
          "message": "2024-01-15T10:31:00 INFO Application recovered"
        }
      }
    ]
  },
  "predict": "先猜：两行日志分别拆出哪些字段？",
  "expect": "对照：HTTP 200，两篇 _source 含 log_timestamp、level、log_message，message 被 remove。grok 只捕获字符串，不等于 date 转换或建 date mapping；本请求不创建持久管道或索引。"
};

  window.ESEXPERIMENTS['ch12-05-onfailure-inline'] = {
  "version": 1,
  "id": "ch12-05-onfailure-inline",
  "title": "A5 · 处理器补救后继续下一步",
  "method": "POST",
  "path": "/_ingest/pipeline/_simulate",
  "body": {
    "pipeline": {
      "processors": [
        {
          "date": {
            "field": "raw_date",
            "target_field": "@timestamp",
            "formats": [
              "yyyy-MM-dd"
            ],
            "timezone": "UTC",
            "tag": "parse-date",
            "on_failure": [
              {
                "set": {
                  "field": "date_parse_error",
                  "value": "{{_ingest.on_failure_message}}"
                }
              }
            ]
          }
        },
        {
          "set": {
            "field": "after_date",
            "value": true
          }
        }
      ]
    },
    "docs": [
      {
        "_source": {
          "raw_date": "2024-01-15"
        }
      },
      {
        "_source": {
          "raw_date": "not-a-date"
        }
      }
    ]
  },
  "predict": "先猜：坏日期会有 after_date 吗？失败元数据会自动存入 _source 吗？",
  "expect": "对照：HTTP 200，两篇都有 after_date:true。好日期生成 UTC @timestamp；坏日期没有 @timestamp，有 date_parse_error 包含 unable to parse date。处理器级补救成功后主链继续；临时 _ingest.on_failure_* 清理，复制的普通字段保留。"
};

  window.ESEXPERIMENTS['ch12-05-probe-missing'] = {
  "version": 1,
  "id": "ch12-05-probe-missing",
  "title": "A6 · 模拟之后检查索引不存在",
  "method": "HEAD",
  "path": "/tut-l12-probe",
  "body": null,
  "predict": "先猜：A2 的 _index 指定了名字，HEAD 会找到它吗？",
  "expect": "对照：首次前提下 HTTP 404、无 body：模拟没有创建 tut-l12-probe。若 200，说明同名索引已存在，先核对来源；本课不删除这个探针索引。重复模拟仍不改变其存在状态。"
};

  window.ESEXPERIMENTS['ch12-05-unhandled-inline'] = {
  "version": 1,
  "id": "ch12-05-unhandled-inline",
  "title": "A7 · 未处理失败：看逐文档 error",
  "method": "POST",
  "path": "/_ingest/pipeline/_simulate",
  "body": {
    "pipeline": {
      "processors": [
        {
          "date": {
            "field": "raw_date",
            "target_field": "@timestamp",
            "formats": [
              "yyyy-MM-dd"
            ],
            "timezone": "UTC",
            "tag": "parse-date"
          }
        },
        {
          "set": {
            "field": "after_date",
            "value": true
          }
        }
      ]
    },
    "docs": [
      {
        "_index": "tut-l12-probe",
        "_id": "1",
        "_source": {
          "raw_date": "not-a-date"
        }
      }
    ]
  },
  "predict": "先猜：外层 HTTP 200 是否等于文档成功？",
  "expect": "对照：合法请求的逐文档执行失败仍可 HTTP 200；docs[0].error 的 reason / caused_by 包含 unable to parse date。不是 doc 成功输出，after_date 不执行。请求解析错误、无 ingest 节点等可直接失败；不能只按状态码判断。"
};

  window.ESEXPERIMENTS['ch12-05-ignore-inline'] = {
  "version": 1,
  "id": "ch12-05-ignore-inline",
  "title": "A8 · ignore_failure 优先于同层补救",
  "method": "POST",
  "path": "/_ingest/pipeline/_simulate",
  "body": {
    "pipeline": {
      "processors": [
        {
          "date": {
            "field": "raw_date",
            "target_field": "@timestamp",
            "formats": [
              "yyyy-MM-dd"
            ],
            "timezone": "UTC",
            "tag": "parse-date",
            "ignore_failure": true,
            "on_failure": [
              {
                "set": {
                  "field": "should_not_run",
                  "value": true
                }
              }
            ]
          }
        },
        {
          "set": {
            "field": "after_date",
            "value": true
          }
        }
      ]
    },
    "docs": [
      {
        "_index": "tut-l12-probe",
        "_id": "1",
        "_source": {
          "raw_date": "not-a-date"
        }
      }
    ]
  },
  "predict": "先猜：同时配置 ignore_failure 和 on_failure，哪一条生效？",
  "expect": "对照：HTTP 200，doc._source 有 after_date:true、raw_date，没有 @timestamp 或 should_not_run。该处理器的 ignore_failure 优先，跳过其 on_failure；只说明忽略本次失败，不承诺回滚其他处理器已写的字段。"
};

  window.ESEXPERIMENTS['ch12-05-pipeline-failure-inline'] = {
  "version": 1,
  "id": "ch12-05-pipeline-failure-inline",
  "title": "A9 · 管道级补救结束当前主链",
  "method": "POST",
  "path": "/_ingest/pipeline/_simulate",
  "body": {
    "pipeline": {
      "processors": [
        {
          "date": {
            "field": "raw_date",
            "target_field": "@timestamp",
            "formats": [
              "yyyy-MM-dd"
            ],
            "timezone": "UTC",
            "tag": "parse-date"
          }
        },
        {
          "set": {
            "field": "after_date",
            "value": true
          }
        }
      ],
      "on_failure": [
        {
          "set": {
            "field": "pipeline_error",
            "value": "{{_ingest.on_failure_message}}"
          }
        }
      ]
    },
    "docs": [
      {
        "_index": "tut-l12-probe",
        "_id": "1",
        "_source": {
          "raw_date": "not-a-date"
        }
      }
    ]
  },
  "predict": "先猜：和 A5 对比，after_date 还会出现吗？",
  "expect": "对照：HTTP 200，doc._source 有 pipeline_error 包含日期失败原因，无 @timestamp、after_date。根 on_failure 成功就返回当前文档，主 processors 不从失败位置往下恢复；普通 pipeline_error 保留，临时失败元数据清理。"
};

  window.ESEXPERIMENTS['ch12-06-create-index'] = {
  "version": 1,
  "id": "ch12-06-create-index",
  "title": "B1 · 创建字段变换索引",
  "method": "PUT",
  "path": "/tut-l12-docs",
  "body": {
    "settings": {
      "index.mode": "standard",
      "index.mapping.source.mode": "stored",
      "number_of_shards": 1,
      "number_of_replicas": 0,
      "refresh_interval": "-1",
      "routing_partition_size": 1,
      "default_pipeline": "_none",
      "final_pipeline": "_none"
    },
    "mappings": {
      "dynamic": true,
      "date_detection": false,
      "numeric_detection": false,
      "dynamic_templates": [],
      "properties": {}
    }
  },
  "predict": "先猜：显式 _none 的两个槽意味着什么？",
  "expect": "对照：首次创建正常 HTTP 200、acknowledged:true；等 B2 确认分片就绪。重复创建 HTTP 400 resource_already_exists_exception，不能覆盖设置，先清理再完整重做。动态普通字符串按本配置建 text + keyword。"
};

  window.ESEXPERIMENTS['ch12-06-health'] = {
  "version": 1,
  "id": "ch12-06-health",
  "title": "B2 · 等待本课索引就绪",
  "method": "GET",
  "path": "/_cluster/health/tut-l12-docs?wait_for_status=green&wait_for_no_initializing_shards=true&timeout=30s",
  "body": null,
  "predict": "先猜：副本为 0 会保证创建瞬间 green 吗？",
  "expect": "对照：在单节点具备数据角色且可分配时，等待成功 status:green、timed_out:false、initializing_shards:0。若超时或未分配，先解决再继续；不能把创建响应视为就绪证明。"
};

  window.ESEXPERIMENTS['ch12-07-write-pipelined'] = {
  "version": 1,
  "id": "ch12-07-write-pipelined",
  "title": "B3 · 请求管道写入 id=1",
  "method": "PUT",
  "path": "/tut-l12-docs/_doc/1?pipeline=tut-l12-fields&refresh=true",
  "body": {
    "hostname": "web-01",
    "level": "INFO"
  },
  "predict": "先猜：存储内容来自哪份 JSON？GET 需要 refresh 吗？",
  "expect": "对照：首次正常 HTTP 201、created；重复固定 ID 正常 HTTP 200、updated、版本增加。成功保留后回写 source，再路由 / mapping / Engine。refresh=true 为搜索可见性；默认 realtime GET 不依赖它。"
};

  window.ESEXPERIMENTS['ch12-08-get-doc1'] = {
  "version": 1,
  "id": "ch12-08-get-doc1",
  "title": "B4 · 读取处理后的 source",
  "method": "GET",
  "path": "/tut-l12-docs/_doc/1?filter_path=_id,_source",
  "body": null,
  "predict": "先猜：是 host 还是 hostname？",
  "expect": "对照：正常 HTTP 200，_id:1，_source 含 host:web-01、environment:production、level:INFO，无 hostname。stored source 保存摄取后的内容；该 GET 不验证搜索刷新，更不证明模拟会写入。"
};

  window.ESEXPERIMENTS['ch12-09-write-plain'] = {
  "version": 1,
  "id": "ch12-09-write-plain",
  "title": "B5 · 无默认管道，写入 id=2",
  "method": "PUT",
  "path": "/tut-l12-docs/_doc/2?refresh=true",
  "body": {
    "hostname": "web-02",
    "level": "WARN"
  },
  "predict": "先猜：同索引的上一次 ?pipeline= 会成为默认吗？",
  "expect": "对照：首次正常 201 created、重复 200 updated。本索引 default / final 均显式 _none；本次也没有请求 pipeline，保存 hostname:web-02、level:WARN。B6 读回对照；refresh=true 服务后续搜索。"
};

  window.ESEXPERIMENTS['ch12-09-get-plain'] = {
  "version": 1,
  "id": "ch12-09-get-plain",
  "title": "B6 · 读回未经过管道的文档",
  "method": "GET",
  "path": "/tut-l12-docs/_doc/2?filter_path=_id,_source",
  "body": null,
  "predict": "先猜：有没有 host 或 environment？",
  "expect": "对照：正常 HTTP 200，_source 为 hostname:web-02、level:WARN，无 host 或 environment。请求级 pipeline 只属于 B3；在有索引默认 / final 的其他配置中，不带参数也可能经过管道。"
};

  window.ESEXPERIMENTS['ch12-10-get-mapping'] = {
  "version": 1,
  "id": "ch12-10-get-mapping",
  "title": "B7 · 映射看到了哪套字段？",
  "method": "GET",
  "path": "/tut-l12-docs/_mapping",
  "body": null,
  "predict": "先猜：host 与 hostname 会互相替换吗？",
  "expect": "对照：正常 HTTP 200，environment、host、hostname、level 都是 text + keyword。限定本课 standard / dynamic:true、检测关闭、无模板配置；两套字段都能留下，pipeline 不是已有 mapping 的重命名，也不回填旧文档。"
};

  window.ESEXPERIMENTS['ch12-11-create-routed'] = {
  "version": 1,
  "id": "ch12-11-create-routed",
  "title": "C1 · 创建普通非分区路由索引",
  "method": "PUT",
  "path": "/tut-l12-routed",
  "body": {
    "settings": {
      "index.mode": "standard",
      "index.mapping.source.mode": "stored",
      "number_of_shards": 5,
      "number_of_replicas": 0,
      "refresh_interval": "-1",
      "routing_partition_size": 1,
      "default_pipeline": "_none",
      "final_pipeline": "_none"
    },
    "mappings": {
      "dynamic": "strict",
      "date_detection": false,
      "numeric_detection": false,
      "dynamic_templates": [],
      "properties": {
        "title": {
          "type": "keyword"
        }
      }
    }
  },
  "predict": "先猜：五个分片能保证两把键落在不同 shard 吗？",
  "expect": "对照：首次正常 200、重复 400 resource_already_exists_exception。五分片、0 副本只是拉开路由桶，不保证不同键不碰撞；新建 9.4.0 普通非分区索引使用当前取模路由分支，旧创建版本公式可能不同。"
};

  window.ESEXPERIMENTS['ch12-12-put-routing-pipeline'] = {
  "version": 1,
  "id": "ch12-12-put-routing-pipeline",
  "title": "C2 · 管道改 _routing",
  "method": "PUT",
  "path": "/_ingest/pipeline/tut-l12-routing",
  "body": {
    "description": "overwrite _routing before shard selection",
    "processors": [
      {
        "set": {
          "field": "_routing",
          "value": "tenant-a"
        }
      }
    ]
  },
  "predict": "先猜：_routing 与 _source.routing 相同吗？",
  "expect": "对照：正常 acknowledged:true；同定义 PUT 可重复。_routing 是 String / null 的可写文档元数据，set 会在 ingest 成功后写回 request.routing；普通 routing 字段不会自动变成分片键。"
};

  window.ESEXPERIMENTS['ch12-12-health'] = {
  "version": 1,
  "id": "ch12-12-health",
  "title": "C3 · 等待五个主分片就绪",
  "method": "GET",
  "path": "/_cluster/health/tut-l12-routed?wait_for_status=green&wait_for_no_initializing_shards=true&timeout=30s",
  "body": null,
  "predict": "先猜：五个分片能否分配到同一节点？",
  "expect": "对照：可在同一数据节点分配五个主分片。须看到 green、timed_out:false、initializing_shards:0；失败先处理分配再继续。副本为 0，不要求五个节点。"
};

  window.ESEXPERIMENTS['ch12-13-shards-by-id'] = {
  "version": 1,
  "id": "ch12-13-shards-by-id",
  "title": "C4 · 比较有效键 1",
  "method": "GET",
  "path": "/tut-l12-routed/_search_shards?routing=1&filter_path=shards.shard",
  "body": null,
  "predict": "先猜：没有文档也能计算分片吗？",
  "expect": "对照：正常 200，shards 显示 routing=1 选中的分片号。对本课新建普通非分区索引，这模拟无 routing 时有效键 _id=1；查询只计算目标，不证明文档已写入。记下实际 shard 号。"
};

  window.ESEXPERIMENTS['ch12-14-shards-by-tenant'] = {
  "version": 1,
  "id": "ch12-14-shards-by-tenant",
  "title": "C5 · 比较有效键 tenant-a",
  "method": "GET",
  "path": "/tut-l12-routed/_search_shards?routing=tenant-a&filter_path=shards.shard",
  "body": null,
  "predict": "先猜：和 C4 的分片号一定不同吗？",
  "expect": "对照：正常 200，记下 tenant-a 的实际分片号。只有五个结果桶，两号可能相同；若碰撞，C7 可能命中，不应宣称必然 404。想演示 miss，另选管道 value 并同步修改全部相关请求，先重新比较。"
};

  window.ESEXPERIMENTS['ch12-15-write-routed'] = {
  "version": 1,
  "id": "ch12-15-write-routed",
  "title": "C6 · URL 无 routing，管道写入",
  "method": "PUT",
  "path": "/tut-l12-routed/_doc/1?pipeline=tut-l12-routing&refresh=true",
  "body": {
    "title": "routed-by-pipeline"
  },
  "predict": "先猜：路由读旧值还是更新后的请求？",
  "expect": "对照：首次正常 201 created、重复 200 updated。成功管道把 tenant-a 写回 request.routing，BulkOperation 后续 route 用它选 shard；refresh=true 使 C9 的搜索可见。没有请求参数不代表最后没有 routing。"
};

  window.ESEXPERIMENTS['ch12-16-get-miss'] = {
  "version": 1,
  "id": "ch12-16-get-miss",
  "title": "C7 · 不带 routing 的 GET",
  "method": "GET",
  "path": "/tut-l12-routed/_doc/1?filter_path=found,_id,_routing",
  "body": null,
  "predict": "先猜：C4 / C5 同号与异号会有什么不同？",
  "expect": "对照：异号时 HTTP 404、found:false；同号时可 200、found:true。GET 仅向 _id=1 的分片查找，遇到取模碰撞也能命中。别用单次 404 或 200 推断管道是否生效；和 C8 返回的 _routing 一起判断。"
};

  window.ESEXPERIMENTS['ch12-17-get-hit'] = {
  "version": 1,
  "id": "ch12-17-get-hit",
  "title": "C8 · 带同一把 routing 读回",
  "method": "GET",
  "path": "/tut-l12-routed/_doc/1?routing=tenant-a&filter_path=found,_id,_routing,_source",
  "body": null,
  "predict": "先猜：元数据回显与 source 字段如何区分？",
  "expect": "对照：正常 HTTP 200、found:true、_routing:tenant-a，_source.title:routed-by-pipeline。存储的元数据被 GET 回显，写读键一致；用不同 routing 也可能因分片碰撞命中，不能只按键字符串断言 miss。"
};

  window.ESEXPERIMENTS['ch12-18-search-fanout'] = {
  "version": 1,
  "id": "ch12-18-search-fanout",
  "title": "C9 · 搜索全部分片",
  "method": "GET",
  "path": "/tut-l12-routed/_search?q=_id:1&filter_path=hits.total,hits.hits._id,hits.hits._routing",
  "body": null,
  "predict": "先猜：为何不带 routing 仍可查到？",
  "expect": "对照：正常 HTTP 200，首次完整流程中 hits.total.value:1、命中 id=1、_routing:tenant-a。C6 已显式刷新，搜索无 routing 面向全部五个主分片的可用拷贝；GET 则只查询按键选出的分片。"
};

  window.ESEXPERIMENTS['ch12-21-put-default'] = {
  "version": 1,
  "id": "ch12-21-put-default",
  "title": "D1 · 注册默认管道",
  "method": "PUT",
  "path": "/_ingest/pipeline/tut-l12-default",
  "body": {
    "description": "ch12 default marker",
    "processors": [
      {
        "set": {
          "field": "stage",
          "value": "default"
        }
      }
    ]
  },
  "predict": "先猜：它能取代请求显式指定的管道吗？",
  "expect": "对照：正常 acknowledged:true；这里只注册定义，D3 才绑定索引。该管道写 stage:default；同定义重复 PUT 可重用。"
};

  window.ESEXPERIMENTS['ch12-22-put-final'] = {
  "version": 1,
  "id": "ch12-22-put-final",
  "title": "D2 · 注册 final 管道",
  "method": "PUT",
  "path": "/_ingest/pipeline/tut-l12-final",
  "body": {
    "description": "ch12 final audit marker",
    "processors": [
      {
        "set": {
          "field": "audited",
          "value": true
        }
      }
    ]
  },
  "predict": "先猜：final 会在请求 _none 时失效吗？",
  "expect": "对照：正常 acknowledged:true；管道写 audited:true。索引绑定 final 后，成功保留的普通 index 文档即使请求 pipeline=_none，也继续执行 final；前链失败 / drop 时提前停止。"
};

  window.ESEXPERIMENTS['ch12-23-create-policy'] = {
  "version": 1,
  "id": "ch12-23-create-policy",
  "title": "D3 · 索引绑定 default 与 final",
  "method": "PUT",
  "path": "/tut-l12-policy",
  "body": {
    "settings": {
      "index.mode": "standard",
      "index.mapping.source.mode": "stored",
      "number_of_shards": 1,
      "number_of_replicas": 0,
      "refresh_interval": "-1",
      "routing_partition_size": 1,
      "default_pipeline": "tut-l12-default",
      "final_pipeline": "tut-l12-final"
    },
    "mappings": {
      "dynamic": "strict",
      "date_detection": false,
      "numeric_detection": false,
      "dynamic_templates": [],
      "properties": {
        "hostname": {
          "type": "keyword"
        },
        "host": {
          "type": "keyword"
        },
        "environment": {
          "type": "keyword"
        },
        "stage": {
          "type": "keyword"
        },
        "audited": {
          "type": "boolean"
        }
      }
    }
  },
  "predict": "先猜：两个槽会同时选择 default 和请求管道吗？",
  "expect": "对照：首次正常 200、重复 400 索引已存在。strict 映射显式接受本组字段。第一槽选请求 pipeline 或 default，第二槽独立 final；不是 default → 请求 → final 三条依次执行。"
};

  window.ESEXPERIMENTS['ch12-24-policy-health'] = {
  "version": 1,
  "id": "ch12-24-policy-health",
  "title": "D4 · 等待优先级实验索引",
  "method": "GET",
  "path": "/_cluster/health/tut-l12-policy?wait_for_status=green&wait_for_no_initializing_shards=true&timeout=30s",
  "body": null,
  "predict": "先猜：什么时候继续三种写入对照？",
  "expect": "对照：green、timed_out:false、initializing_shards:0 才继续。索引已存在时本卡不确认其设置等于 D3；配置不符需清理、按 D1 起完整重做。"
};

  window.ESEXPERIMENTS['ch12-25-write-default'] = {
  "version": 1,
  "id": "ch12-25-write-default",
  "title": "D5 · 不指定请求管道",
  "method": "PUT",
  "path": "/tut-l12-policy/_doc/1?refresh=true",
  "body": {
    "hostname": "policy-01"
  },
  "predict": "先猜：会得到 stage、audited，还是 host？",
  "expect": "对照：首次正常 201 created、重复 200 updated。default 写 stage:default；final 写 audited:true；hostname:policy-01 保留，无 host / environment。D8 搜索汇总三篇 source。"
};

  window.ESEXPERIMENTS['ch12-26-write-override'] = {
  "version": 1,
  "id": "ch12-26-write-override",
  "title": "D6 · 显式请求管道替代 default",
  "method": "PUT",
  "path": "/tut-l12-policy/_doc/2?pipeline=tut-l12-fields&refresh=true",
  "body": {
    "hostname": "policy-02"
  },
  "predict": "先猜：default 还会写 stage 吗？",
  "expect": "对照：首次正常 201 created、重复 200 updated。fields 写 environment:production、host:policy-02 并移除 hostname；final 写 audited:true；default 被替代，无 stage。"
};

  window.ESEXPERIMENTS['ch12-27-write-none'] = {
  "version": 1,
  "id": "ch12-27-write-none",
  "title": "D7 · _none 跳过第一槽",
  "method": "PUT",
  "path": "/tut-l12-policy/_doc/3?pipeline=_none&refresh=true",
  "body": {
    "hostname": "policy-03"
  },
  "predict": "先猜：会连 final 一起跳过吗？",
  "expect": "对照：首次正常 201 created、重复 200 updated。hostname:policy-03 保留、audited:true；无 stage / host / environment。_none 只替代本请求的第一槽，不修改索引默认配置。"
};

  window.ESEXPERIMENTS['ch12-28-policy-search'] = {
  "version": 1,
  "id": "ch12-28-policy-search",
  "title": "D8 · 按 ID 对照三份 source",
  "method": "POST",
  "path": "/tut-l12-policy/_search?filter_path=hits.total,hits.hits._id,hits.hits._source",
  "body": {
    "size": 3,
    "query": {
      "ids": {
        "values": [
          "1",
          "2",
          "3"
        ]
      }
    }
  },
  "predict": "先猜：三篇都有哪些相同字段？",
  "expect": "对照：正常 200、total.value:3。逐 _id 比较：1 hostname+stage+audited；2 host+environment+audited；3 hostname+audited。不依赖 hits 顺序；三次写入显式 refresh=true。"
};

  window.ESEXPERIMENTS['ch12-29-delete-bound-final'] = {
  "version": 1,
  "id": "ch12-29-delete-bound-final",
  "title": "D9 · 删除仍被索引引用的 final",
  "method": "DELETE",
  "path": "/_ingest/pipeline/tut-l12-final",
  "body": null,
  "predict": "先猜：删定义能否绕过绑定的 final？",
  "expect": "对照：预期 HTTP 400，illegal_argument_exception、reason 含 cannot be deleted / final pipeline；索引仍引用该定义，删除被拒。不是 acknowledged 成功。先删索引或解除引用才能删除；本组继续使用它。"
};

  window.ESEXPERIMENTS['ch12-30-put-drop'] = {
  "version": 1,
  "id": "ch12-30-put-drop",
  "title": "D10 · 注册 drop 管道",
  "method": "PUT",
  "path": "/_ingest/pipeline/tut-l12-drop",
  "body": {
    "processors": [
      {
        "drop": {}
      }
    ]
  },
  "predict": "先猜：null 返回值会让后续管道继续吗？",
  "expect": "对照：正常 acknowledged:true；DropProcessor 返回 null，IngestService 把该项标成 dropped，提前返回，不继续当前项的 final 和分片写入。"
};

  window.ESEXPERIMENTS['ch12-31-write-drop'] = {
  "version": 1,
  "id": "ch12-31-write-drop",
  "title": "D11 · drop 也是成功响应的一种结果",
  "method": "PUT",
  "path": "/tut-l12-policy/_doc/4?pipeline=tut-l12-drop&refresh=true",
  "body": {
    "hostname": "dropped"
  },
  "predict": "先猜：看到成功响应，是否必然存在文档？",
  "expect": "对照：预期 result:noop，不写入新文档；首次前提下 id=4 不存在，D12 应 404。重复仍 noop；若此前同 ID 已有文档，drop 不会删除它。本实验使用全新 id，响应里的伪分片等元数据不证明落盘。"
};

  window.ESEXPERIMENTS['ch12-32-get-dropped'] = {
  "version": 1,
  "id": "ch12-32-get-dropped",
  "title": "D12 · 确认 drop 没写入新 ID",
  "method": "GET",
  "path": "/tut-l12-policy/_doc/4?filter_path=found,_id,_source",
  "body": null,
  "predict": "先猜：noop 后 GET 能找到吗？",
  "expect": "对照：首次完整流程下 HTTP 404、found:false。drop 不是 DELETE；有旧文档时会留存。确认初始资源不存在，避免把旧文档当成本次写入结果。"
};

  window.ESEXPERIMENTS['ch12-33-final-change-index'] = {
  "version": 1,
  "id": "ch12-33-final-change-index",
  "title": "D13 · 临时修改 final，尝试改目标索引",
  "method": "PUT",
  "path": "/_ingest/pipeline/tut-l12-final",
  "body": {
    "processors": [
      {
        "set": {
          "field": "_index",
          "value": "tut-l12-docs"
        }
      }
    ]
  },
  "predict": "先猜：PUT 会拒绝，还是执行到真实写入时拒绝？",
  "expect": "对照：定义正常 acknowledged:true，set _index 本身是合法处理器。final 的禁改目标约束在 IngestService 执行后检查，不由这次 PUT 判定；D14 故意触发，D16 恢复。"
};

  window.ESEXPERIMENTS['ch12-34-final-write-error'] = {
  "version": 1,
  "id": "ch12-34-final-write-error",
  "title": "D14 · 写入触发 final 约束",
  "method": "PUT",
  "path": "/tut-l12-policy/_doc/5?pipeline=_none",
  "body": {
    "hostname": "blocked"
  },
  "predict": "先猜：合法的管道定义能保证这次写入成功吗？",
  "expect": "对照：预期错误，reason / caused_by 含 final pipeline [tut-l12-final] can't change the target index；IllegalStateException 路径通常 HTTP 500，以真实响应核对。请求在 ingest 失败，不会往 policy 或 docs 写入 id=5；D16 恢复后其他写入才正常。"
};

  window.ESEXPERIMENTS['ch12-35-final-error-missing'] = {
  "version": 1,
  "id": "ch12-35-final-error-missing",
  "title": "D15 · 原目标的失败新 ID 不存在",
  "method": "GET",
  "path": "/tut-l12-policy/_doc/5?filter_path=found,_id",
  "body": null,
  "predict": "先猜：失败会留下部分写入吗？",
  "expect": "对照：首次前提下 HTTP 404、found:false。该约束在 route / Engine 前阻止本项；不会写入半篇文档。若 id=5 原来存在，失败不会自动删除旧文档，因此必须使用本组初始条件。"
};

  window.ESEXPERIMENTS['ch12-36-restore-final'] = {
  "version": 1,
  "id": "ch12-36-restore-final",
  "title": "D16 · 恢复本课 final 定义",
  "method": "PUT",
  "path": "/_ingest/pipeline/tut-l12-final",
  "body": {
    "description": "ch12 final audit marker",
    "processors": [
      {
        "set": {
          "field": "audited",
          "value": true
        }
      }
    ]
  },
  "predict": "先猜：已有文档 audited 会被重新计算吗？",
  "expect": "对照：正常 acknowledged:true；后续成功保留的写入再运行 audited:true。已索引文档不回填、不重跑；若中断在 D13–D15，应先运行本卡恢复，再清理或重做。"
};

  window.ESEXPERIMENTS['ch12-19-clean-indices'] = {
  "version": 1,
  "id": "ch12-19-clean-indices",
  "title": "清理 1 · 点名删除三个索引",
  "method": "DELETE",
  "path": "/tut-l12-docs,tut-l12-routed,tut-l12-policy?ignore_unavailable=true",
  "body": null,
  "predict": "先猜：为什么先删索引，再删绑定的管道？",
  "expect": "对照：正常 acknowledged:true；删除 docs、routed、policy 的数据 / mapping / 索引设置，解除 default / final 引用。ignore_unavailable=true 允许部分或全部不存在；保留其他资源，之后继续逐条清理管道。"
};

  window.ESEXPERIMENTS['ch12-20-clean-pipelines'] = {
  "version": 1,
  "id": "ch12-20-clean-pipelines",
  "title": "清理 2 · 删除 fields 管道",
  "method": "DELETE",
  "path": "/_ingest/pipeline/tut-l12-fields",
  "body": null,
  "predict": "先猜：DELETE 支持逗号列表和 GET 一样的规则吗？",
  "expect": "对照：存在时 acknowledged:true；不存在时 HTTP 404 pipeline missing，可继续后续清理。删除 API 把 id 当单个名称 / 简单通配模式，不按逗号拆列表；所以逐条点名删。索引已删除，本课没有绑定引用。"
};

  window.ESEXPERIMENTS['ch12-37-clean-routing'] = {
  "version": 1,
  "id": "ch12-37-clean-routing",
  "title": "清理 · 删除 routing 管道",
  "method": "DELETE",
  "path": "/_ingest/pipeline/tut-l12-routing",
  "body": null,
  "predict": "先猜：不存在或仍被引用时会怎样？",
  "expect": "对照：存在且无引用时 acknowledged:true；重复或初次未创建时 HTTP 404 pipeline missing，可继续。若 400 cannot be deleted，核对索引引用，先完成索引清理；只删除这个本课专属名字。"
};

  window.ESEXPERIMENTS['ch12-38-clean-default'] = {
  "version": 1,
  "id": "ch12-38-clean-default",
  "title": "清理 · 删除 default 管道",
  "method": "DELETE",
  "path": "/_ingest/pipeline/tut-l12-default",
  "body": null,
  "predict": "先猜：不存在或仍被引用时会怎样？",
  "expect": "对照：存在且无引用时 acknowledged:true；重复或初次未创建时 HTTP 404 pipeline missing，可继续。若 400 cannot be deleted，核对索引引用，先完成索引清理；只删除这个本课专属名字。"
};

  window.ESEXPERIMENTS['ch12-39-clean-final'] = {
  "version": 1,
  "id": "ch12-39-clean-final",
  "title": "清理 · 删除 final 管道",
  "method": "DELETE",
  "path": "/_ingest/pipeline/tut-l12-final",
  "body": null,
  "predict": "先猜：不存在或仍被引用时会怎样？",
  "expect": "对照：存在且无引用时 acknowledged:true；重复或初次未创建时 HTTP 404 pipeline missing，可继续。若 400 cannot be deleted，核对索引引用，先完成索引清理；只删除这个本课专属名字。"
};

  window.ESEXPERIMENTS['ch12-40-clean-drop'] = {
  "version": 1,
  "id": "ch12-40-clean-drop",
  "title": "清理 · 删除 drop 管道",
  "method": "DELETE",
  "path": "/_ingest/pipeline/tut-l12-drop",
  "body": null,
  "predict": "先猜：不存在或仍被引用时会怎样？",
  "expect": "对照：存在且无引用时 acknowledged:true；重复或初次未创建时 HTTP 404 pipeline missing，可继续。若 400 cannot be deleted，核对索引引用，先完成索引清理；只删除这个本课专属名字。"
};

})();
