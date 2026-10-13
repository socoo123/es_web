/* ch26 · ES 9.4.0 / Lucene 10.4.0；操作卡顺序与章节一致。 */
(function () {
  'use strict';
  var operations = [
  {
    "version": 1,
    "id": "ch26-pre-version",
    "title": "前置 1 · 核对节点与 Lucene 版本",
    "method": "GET",
    "path": "/",
    "body": null,
    "predict": "是否为本课的 9.4.0 节点？",
    "expect": "version.number 应为 9.4.0，lucene_version 为 10.4.0。使用本地隔离学习节点；本轮云端 API 未实测。"
  },
  {
    "version": 1,
    "id": "ch26-pre-cluster-settings",
    "title": "前置 2 · 保存 expensive 设置的两层来源",
    "method": "GET",
    "path": "/_cluster/settings?flat_settings=true&include_defaults=true",
    "body": null,
    "predict": "transient 与 persistent 有原值吗？",
    "expect": "保存完整响应。E 组仅在该键两层均不存在、节点有效基线为 true 时执行；有原值则跳过 E 与相应设置清理，不能覆盖后用 null 假装恢复。"
  },
  {
    "version": 1,
    "id": "ch26-pre-node-settings",
    "title": "前置 3 · 核对单节点、角色与脚本限制",
    "method": "GET",
    "path": "/_nodes/settings?flat_settings=true&include_defaults=true",
    "body": null,
    "predict": "当前节点是否允许 inline 脚本、score/field/update/ingest/painless_test？",
    "expect": "确认仅一学习节点且有 ingest 角色，脚本类型/context 未被禁用。保存节点 search.allow_expensive_queries 的配置/默认；E 组要求基线 true。"
  },
  {
    "version": 1,
    "id": "ch26-pre-index",
    "title": "前置 4 · 本章索引须不存在",
    "method": "HEAD",
    "path": "/tut-l26-score",
    "body": null,
    "predict": "资源应当存在还是不存在？",
    "expect": "起步应 HTTP 404。若已存在，先核对它确属本章上轮资源再按清理顺序重做；不在未知数据上直接覆盖。"
  },
  {
    "version": 1,
    "id": "ch26-pre-pipeline",
    "title": "前置 5 · 正常管道须不存在",
    "method": "GET",
    "path": "/_ingest/pipeline/tut-l26-script",
    "body": null,
    "predict": "是否有上轮管道？",
    "expect": "起步 404。若存在先核对归属，再执行本章点名清理；PUT 同名管道会更新，不能把未知管道当空白。"
  },
  {
    "version": 1,
    "id": "ch26-pre-bad-pipeline",
    "title": "前置 6 · 失败演示的名字也须不存在",
    "method": "GET",
    "path": "/_ingest/pipeline/tut-l26-file",
    "body": null,
    "predict": "失败 PUT 是否可能留下旧管道？",
    "expect": "起步 404；若已存在，先处理旧资源再做 C 组。后续编译失败不会证明同名旧资源不存在。"
  },
  {
    "version": 1,
    "id": "ch26-01-setup",
    "title": "A1 · 建一主零副本、显式 mapping 的索引",
    "method": "PUT",
    "path": "/tut-l26-score",
    "body": {
      "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
        "auto_expand_replicas": "false"
      },
      "mappings": {
        "dynamic": "strict",
        "properties": {
          "title": {
            "type": "keyword"
          },
          "popularity": {
            "type": "long"
          },
          "price": {
            "type": "double"
          },
          "views": {
            "type": "long"
          }
        }
      }
    },
    "predict": "数字脚本读什么数据？",
    "expect": "acknowledged=true；数值字段有 doc values，views 先声明以适配 strict。text 默认既无 doc values 又禁 fielddata，不能直接把它当数值 .value；keyword 才适合未分析字符串。重复建索引会 400。"
  },
  {
    "version": 1,
    "id": "ch26-a-health",
    "title": "A2 · 等待本章索引可用",
    "method": "GET",
    "path": "/_cluster/health/tut-l26-score?wait_for_status=green&timeout=30s",
    "body": null,
    "predict": "整个集群 yellow 会影响本章结论吗？",
    "expect": "只确认本索引 timed_out=false、status=green、主分片已分配；其他索引状态不构成本章测量。超时先解决分配，再写入。"
  },
  {
    "version": 1,
    "id": "ch26-a-config",
    "title": "A3 · 回看创建版本、settings 与 mapping",
    "method": "GET",
    "path": "/tut-l26-score",
    "body": null,
    "predict": "是否真是一主零副本与数值字段？",
    "expect": "核对 index.version.created、1/0/auto_expand=false、dynamic=strict、title keyword 与三个数值字段。模板可能叠加别的配置；核对后才继续。"
  },
  {
    "version": 1,
    "id": "ch26-02-bulk",
    "title": "A4 · 固定 ID 写两篇文档并刷新",
    "method": "POST",
    "path": "/tut-l26-score/_bulk?refresh=true",
    "body": "{\"index\":{\"_id\":\"cheap\"}}\n{\"title\":\"obscure\",\"popularity\":10,\"price\":100.0}\n{\"index\":{\"_id\":\"popular\"}}\n{\"title\":\"hit\",\"popularity\":100,\"price\":80.0}\n",
    "predict": "首次与重复写入是否增加文档数？",
    "expect": "errors=false；首次 created，重复 updated，固定 ID 仍只有两篇。此卡会以原文档替换旧 _source（去掉旧 views），refresh=true 消除搜索可见性竞态；不靠自动刷新时钟。"
  },
  {
    "version": 1,
    "id": "ch26-a-count",
    "title": "A5 · 确认两篇已可搜索",
    "method": "GET",
    "path": "/tut-l26-score/_count",
    "body": null,
    "predict": "写第二遍 count 会是 4 吗？",
    "expect": "count=2。若不同，停止后续分数对照；索引或数据不满足起步条件。"
  },
  {
    "version": 1,
    "id": "ch26-03-score-pop",
    "title": "A6 · _score × popularity / 100",
    "method": "POST",
    "path": "/tut-l26-score/_search?request_cache=false",
    "body": {
      "size": 2,
      "query": {
        "script_score": {
          "query": {
            "match_all": {}
          },
          "script": {
            "source": "_score * doc['popularity'].value / 100"
          }
        }
      }
    },
    "predict": "match_all 的分数怎样参与？",
    "expect": "query 显式 match_all，默认 boost=1：popular 1.0 在前，cheap 约 0.1。脚本返回评分；这里显式读取 _score 才组合内层分数。REST _score 为 float，注意小数表示。"
  },
  {
    "version": 1,
    "id": "ch26-04-score-price",
    "title": "A7 · 仅按 price × 0.9 评分",
    "method": "POST",
    "path": "/tut-l26-score/_search?request_cache=false",
    "body": {
      "size": 2,
      "query": {
        "script_score": {
          "query": {
            "match_all": {}
          },
          "script": {
            "source": "doc['price'].value * 0.9"
          }
        }
      }
    },
    "predict": "price 与 popularity 谁决定结果？",
    "expect": "cheap 90、popular 72；这句未读 _score 或 popularity。默认外层 boost=1 时分数就是脚本返回值；function_score 的组合由 boost_mode 等决定，不总是乘法。"
  },
  {
    "version": 1,
    "id": "ch26-05-script-fields",
    "title": "A8 · field context 返回折扣价",
    "method": "POST",
    "path": "/tut-l26-score/_search?request_cache=false",
    "body": {
      "size": 2,
      "query": {
        "match_all": {}
      },
      "sort": [
        {
          "title": "asc"
        }
      ],
      "track_scores": true,
      "script_fields": {
        "discounted_price": {
          "script": {
            "source": "doc['price'].value * params.discount",
            "params": {
              "discount": 0.8
            }
          }
        }
      }
    },
    "predict": "返回字段会改原文档或分数吗？",
    "expect": "按 title 升序：popular fields.discounted_price=[64.0]、cheap=[80.0]；track_scores=true 保留 match_all 的 1.0。这是响应计算字段，不把 discounted_price 写进 _source。"
  },
  {
    "version": 1,
    "id": "ch26-a-field-param",
    "title": "A9 · 同一 field 源码，discount 改 0.9",
    "method": "POST",
    "path": "/tut-l26-score/_search?request_cache=false",
    "body": {
      "size": 2,
      "query": {
        "match_all": {}
      },
      "sort": [
        {
          "title": "asc"
        }
      ],
      "track_scores": true,
      "script_fields": {
        "discounted_price": {
          "script": {
            "source": "doc['price'].value * params.discount",
            "params": {
              "discount": 0.9
            }
          }
        }
      }
    },
    "predict": "换 params 是否形成新编译键？",
    "expect": "popular [72.0]、cheap [90.0]；分数仍 1.0。source/context/options 不变，params 不进编译键；是否命中还取决于同节点缓存是否保留。"
  },
  {
    "version": 1,
    "id": "ch26-06-update",
    "title": "A10 · update context 赋值 views=1",
    "method": "POST",
    "path": "/tut-l26-score/_update/cheap?refresh=true",
    "body": {
      "script": {
        "source": "ctx._source.views = params.count",
        "params": {
          "count": 1
        }
      }
    },
    "predict": "和 script_fields 的修改对象相同吗？",
    "expect": "成功后 views=1，更新经过文档重索引。不要写死 _version=2：重复 bulk/update 都可能改变版本；这里只比较 _source。"
  },
  {
    "version": 1,
    "id": "ch26-07-get-cheap",
    "title": "A11 · 回看持久文档源",
    "method": "GET",
    "path": "/tut-l26-score/_doc/cheap?filter_path=_source",
    "body": null,
    "predict": "折扣价也写入了吗？",
    "expect": "_source 含 views=1、popularity=10、price=100、title=obscure；没有 discounted_price。ingest 的字段写 ctx 顶层，update 是 ctx._source，不能混用。"
  },
  {
    "version": 1,
    "id": "ch26-08-pipeline-put",
    "title": "B1 · inline ingest 脚本在建管道时验证",
    "method": "PUT",
    "path": "/_ingest/pipeline/tut-l26-script",
    "body": {
      "processors": [
        {
          "script": {
            "source": "ctx.fullname = ctx.first_name + ' ' + ctx.last_name"
          }
        }
      ]
    },
    "predict": "等第一条文档才编译吗？",
    "expect": "预期 acknowledged=true。创建 ScriptProcessor 会调用 compile（缓存可命中）；inline processor 保留预编译 factory，stored processor 不长期持有它。"
  },
  {
    "version": 1,
    "id": "ch26-09-simulate",
    "title": "B2 · 模拟拼接 fullname",
    "method": "POST",
    "path": "/_ingest/pipeline/tut-l26-script/_simulate",
    "body": {
      "docs": [
        {
          "_index": "tut-l26-score",
          "_id": "simulate-only",
          "_source": {
            "first_name": "Grace",
            "last_name": "Hopper"
          }
        }
      ]
    },
    "predict": "simulate 会把这篇写进索引吗？",
    "expect": "docs[0].doc._source.fullname=\"Grace Hopper\"，结果路径包含 doc。模拟运行 processor，不做真实索引写入，也不以索引 mapping 验证这些测试字段；count 仍为 2。"
  },
  {
    "version": 1,
    "id": "ch26-10-file-execute",
    "title": "C1 · new File：直接观察完整错误链",
    "method": "POST",
    "path": "/_scripts/painless/_execute",
    "body": {
      "script": {
        "source": "return new java.io.File(\"/tmp/painless-should-not-exist\");"
      }
    },
    "predict": "构造 File 就等于创建磁盘文件吗？",
    "expect": "源码预期 400、compile error、Not a type [java.io.File].，带 script_stack。失败在 visitNewObj，未到 IR/ASM。Java 的 File 构造本身也不创建文件；本轮未做 API 或磁盘实测。"
  },
  {
    "version": 1,
    "id": "ch26-11-file-search",
    "title": "C2 · 同一句放入 script_score",
    "method": "POST",
    "path": "/tut-l26-score/_search?request_cache=false",
    "body": {
      "size": 2,
      "query": {
        "script_score": {
          "query": {
            "match_all": {}
          },
          "script": {
            "source": "return new java.io.File(\"/tmp/x\");"
          }
        }
      }
    },
    "predict": "错误的外层包装与 _execute 相同吗？",
    "expect": "预期搜索失败（通常 400），沿 root_cause/failed_shards/caused_by 找 compile error 与 Not a type。外层错误取决于搜索阶段和包装；不要只凭最外层 reason 判定拒绝位置。"
  },
  {
    "version": 1,
    "id": "ch26-12-file-pipeline",
    "title": "C3 · 坏 inline 脚本在 PUT 管道时被拒",
    "method": "PUT",
    "path": "/_ingest/pipeline/tut-l26-file",
    "body": {
      "processors": [
        {
          "script": {
            "source": "ctx.f = new java.io.File(\"/tmp/x\")"
          }
        }
      ]
    },
    "predict": "管道能够先建好再等待写入失败吗？",
    "expect": "源码预期 PUT 400、配置错误链包含 compile error 与 Not a type。创建 processor 时已验证编译；仅在前置确认不存在时，后续 404 才能说明没创建新管道。"
  },
  {
    "version": 1,
    "id": "ch26-c-bad-absent",
    "title": "C4 · 验证失败管道仍不存在",
    "method": "GET",
    "path": "/_ingest/pipeline/tut-l26-file",
    "body": null,
    "predict": "失败 PUT 会留下资源吗？",
    "expect": "前置 404 且 C3 确实编译失败时，这里应 404。若出现 200，核对已有资源或实际环境的允许列表扩展，停止按预期继续清理。"
  },
  {
    "version": 1,
    "id": "ch26-13-decl",
    "title": "C5 · 声明 File 类型",
    "method": "POST",
    "path": "/_scripts/painless/_execute",
    "body": {
      "script": {
        "source": "java.io.File f = null; return 1;"
      }
    },
    "predict": "报错是否仍叫 Not a type？",
    "expect": "预期 compile error，原因 invalid declaration: cannot resolve type [java.io.File]。声明与 new 的语义入口不同；位置只辅助定位，不硬编码 offset=13。"
  },
  {
    "version": 1,
    "id": "ch26-14-getclass",
    "title": "C6 · 静态 String 调 getClass",
    "method": "POST",
    "path": "/_scripts/painless/_execute",
    "body": {
      "script": {
        "source": "String s = \"x\"; return s.getClass();"
      }
    },
    "predict": "拒绝发生在什么时候？",
    "expect": "预期 compile error：member method [java.lang.String, getClass/0] not found。默认允许列表没有该成员；静态类型在语义分析时查表。"
  },
  {
    "version": 1,
    "id": "ch26-c-def-getclass",
    "title": "C7 · def 调 getClass 的运行期对照",
    "method": "POST",
    "path": "/_scripts/painless/_execute",
    "body": {
      "script": {
        "source": "def x = 1; return x.getClass();"
      }
    },
    "predict": "def 能跳过允许列表吗？",
    "expect": "预期 runtime error：dynamic method [java.lang.Integer, getClass/0] not found。编译可产出动态调用，执行时仍查 runtime Lookup；不能说执行期没有任何查表。"
  },
  {
    "version": 1,
    "id": "ch26-15-context-classes",
    "title": "C8 · 查看实际 score context 的允许列表",
    "method": "GET",
    "path": "/_scripts/painless/_context?context=score",
    "body": null,
    "predict": "classes 数量固定为 404 吗？",
    "expect": "默认发行版应有 java.lang.String，没有 java.io.File/java.lang.Runtime/java.lang.Class；classes 数量由版本与扩展决定，不写死。该 API 是内部调试入口，输出不是长期稳定契约。"
  },
  {
    "version": 1,
    "id": "ch26-d-stats-before",
    "title": "D1 · 保存本节点脚本编译统计",
    "method": "GET",
    "path": "/_nodes/_local/stats/script?filter_path=nodes.*.name,nodes.*.script",
    "body": null,
    "predict": "累计编译数应从 0 开始吗？",
    "expect": "保存节点 ID 与 script.compilations/cache_evictions/compilation_limit_triggered。此前实验已编译过脚本；这些累计值不随删索引清零。"
  },
  {
    "version": 1,
    "id": "ch26-d-param-2",
    "title": "D2 · 固定 source，只换 multiplier=2",
    "method": "POST",
    "path": "/_scripts/painless/_execute",
    "body": {
      "script": {
        "source": "return params.multiplier * 26;",
        "params": {
          "multiplier": 2
        }
      }
    },
    "predict": "结果与编译次数都应怎样变化？",
    "expect": "默认 painless_test context 的 result 被序列化为字符串 \"52\"。首次该键可编译也可已缓存；第二次仅改 params，在缓存仍保留时复用 factory。"
  },
  {
    "version": 1,
    "id": "ch26-d-stats-2",
    "title": "D3 · 对比参数请求后的累计值",
    "method": "GET",
    "path": "/_nodes/_local/stats/script?filter_path=nodes.*.name,nodes.*.script",
    "body": null,
    "predict": "前后增加能否全部归因于本卡？",
    "expect": "比较同一节点相邻快照；无并发、无淘汰/过期/配置切换且请求成功时，第二次仅换 params 不新增编译。第一次可能早已命中；其他脚本、节点重启会污染对照，不能强求历史计数。"
  },
  {
    "version": 1,
    "id": "ch26-d-param-3",
    "title": "D4 · 固定 source，只换 multiplier=3",
    "method": "POST",
    "path": "/_scripts/painless/_execute",
    "body": {
      "script": {
        "source": "return params.multiplier * 26;",
        "params": {
          "multiplier": 3
        }
      }
    },
    "predict": "结果与编译次数都应怎样变化？",
    "expect": "默认 painless_test context 的 result 被序列化为字符串 \"78\"。首次该键可编译也可已缓存；第二次仅改 params，在缓存仍保留时复用 factory。"
  },
  {
    "version": 1,
    "id": "ch26-d-stats-3",
    "title": "D5 · 对比参数请求后的累计值",
    "method": "GET",
    "path": "/_nodes/_local/stats/script?filter_path=nodes.*.name,nodes.*.script",
    "body": null,
    "predict": "前后增加能否全部归因于本卡？",
    "expect": "比较同一节点相邻快照；无并发、无淘汰/过期/配置切换且请求成功时，第二次仅换 params 不新增编译。第一次可能早已命中；其他脚本、节点重启会污染对照，不能强求历史计数。"
  },
  {
    "version": 1,
    "id": "ch26-16-expensive-off",
    "title": "E1 · 条件满足时设置 expensive=false",
    "method": "PUT",
    "path": "/_cluster/settings",
    "body": {
      "transient": {
        "search.allow_expensive_queries": false
      }
    },
    "predict": "允许列表通过就一定可用 script_score 吗？",
    "expect": "仅在前置两层均无覆盖、节点基线 true 的隔离节点执行。此设置影响全节点查询；成功后 E2 确认，再 E3 测试，立即 E4 恢复；不满足前提则整组跳过。"
  },
  {
    "version": 1,
    "id": "ch26-e-confirm-off",
    "title": "E2 · 确认 transient false 已出现",
    "method": "GET",
    "path": "/_cluster/settings?flat_settings=true&include_defaults=true",
    "body": null,
    "predict": "设置层真的生效了吗？",
    "expect": "确认该键 transient=false；记录原 persistent 仍无覆盖。读取结果不符时停止 E3，并处理刚执行的设置恢复。"
  },
  {
    "version": 1,
    "id": "ch26-17-expensive-reject",
    "title": "E3 · 无害评分脚本也会拒绝",
    "method": "POST",
    "path": "/tut-l26-score/_search?request_cache=false",
    "body": {
      "size": 2,
      "query": {
        "script_score": {
          "query": {
            "match_all": {}
          },
          "script": {
            "source": "return 1.0;"
          }
        }
      }
    },
    "predict": "此处会调用编译器吗？",
    "expect": "预期错误链含 [script score] queries cannot be executed when search.allow_expensive_queries is set to false。doToQuery 先检查设置，再 compile；不是对脚本危险性的分析。保留完整错误，不隐藏关键层。"
  },
  {
    "version": 1,
    "id": "ch26-18-restore",
    "title": "E4 · 立即移除本次 transient 覆盖",
    "method": "PUT",
    "path": "/_cluster/settings",
    "body": {
      "transient": {
        "search.allow_expensive_queries": null
      }
    },
    "predict": "null 具体删掉哪一层？",
    "expect": "仅 E1 执行后运行；null 移除这个 transient 键，不把 persistent 或节点配置重写为 true。因为起步两层均无覆盖且节点基线 true，本组才可以称恢复基线。"
  },
  {
    "version": 1,
    "id": "ch26-e-confirm-restored",
    "title": "E5 · 核对恢复后的来源",
    "method": "GET",
    "path": "/_cluster/settings?flat_settings=true&include_defaults=true",
    "body": null,
    "predict": "只见 acknowledged 足够吗？",
    "expect": "确认 transient 键已消失、persistent 仍无该键，对照前置保存的节点/default true。若原本有其他来源则本组应跳过，而不是删除未知设置。"
  },
  {
    "version": 1,
    "id": "ch26-e-score-restored",
    "title": "E6 · 同一脚本重新建查询",
    "method": "POST",
    "path": "/tut-l26-score/_search?request_cache=false",
    "body": {
      "size": 2,
      "query": {
        "script_score": {
          "query": {
            "match_all": {}
          },
          "script": {
            "source": "return 1.0;"
          }
        }
      }
    },
    "predict": "恢复后是不是分数又乘了 popularity？",
    "expect": "两篇均 _score=1.0、hits.total.value=2（默认 boost=1）。同分顺序不承诺；用 _id 对照。若仍拒绝，回到有效设置与脚本限制检查。"
  },
  {
    "version": 1,
    "id": "ch26-clean-setting",
    "title": "清理 1 · 若 E1 已执行，再确认移除本次覆盖",
    "method": "PUT",
    "path": "/_cluster/settings",
    "body": {
      "transient": {
        "search.allow_expensive_queries": null
      }
    },
    "predict": "如果 E 组跳过也应执行吗？",
    "expect": "仅 E1 曾执行时运行；删除同一临时键可重复，不动其他设置。E 组跳过则此卡也跳过，避免移除原有 transient 值。"
  },
  {
    "version": 1,
    "id": "ch26-clean-settings-check",
    "title": "清理 2 · 对照起步设置来源",
    "method": "GET",
    "path": "/_cluster/settings?flat_settings=true&include_defaults=true",
    "body": null,
    "predict": "还原哪个基线？",
    "expect": "比较前置完整响应与节点基线；不能只看 defaults=true。设置条件不满足的读者应看到原覆盖值保持原样。"
  },
  {
    "version": 1,
    "id": "ch26-19-cleanup",
    "title": "清理 3 · 点名删除本章索引",
    "method": "DELETE",
    "path": "/tut-l26-score",
    "body": null,
    "predict": "删除索引会清空脚本缓存统计吗？",
    "expect": "首次 acknowledged=true，重复通常 404。只删除 tut-l26-score 两篇学习文档；编译缓存与节点累计统计不因此清零。"
  },
  {
    "version": 1,
    "id": "ch26-clean-index-absent",
    "title": "清理 4 · 验证索引消失",
    "method": "HEAD",
    "path": "/tut-l26-score",
    "body": null,
    "predict": "资源应当存在还是不存在？",
    "expect": "HTTP 404。重做从前置开始，然后 A1 建索引；不要靠旧 _source 或历史版本值当证据。"
  },
  {
    "version": 1,
    "id": "ch26-20-cleanup-pipeline",
    "title": "清理 5 · 点名删除正常管道",
    "method": "DELETE",
    "path": "/_ingest/pipeline/tut-l26-script",
    "body": null,
    "predict": "模拟结果有需要删除的文档吗？",
    "expect": "首次 acknowledged=true，重复通常 404。simulate 没有写入文档；只删本章正常管道，不对管道做通配符清理。"
  },
  {
    "version": 1,
    "id": "ch26-clean-pipeline-absent",
    "title": "清理 6 · 验证正常管道消失",
    "method": "GET",
    "path": "/_ingest/pipeline/tut-l26-script",
    "body": null,
    "predict": "管道是否真的清理？",
    "expect": "预期 404。重做 B1 会创建新的 processor；不能拿旧管道配置推断当前编译行为。"
  },
  {
    "version": 1,
    "id": "ch26-clean-bad-absent",
    "title": "清理 7 · 再确认失败演示名字不存在",
    "method": "GET",
    "path": "/_ingest/pipeline/tut-l26-file",
    "body": null,
    "predict": "需要删坏管道吗？",
    "expect": "前置 404、C3 编译失败且中间无人创建时仍 404；本实验没有创建这个管道。如果出现 200，先核对归属与实际失败结果，再处理，勿盲删。"
  }
];
  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};
  operations.forEach(function (e) { window.ESEXPERIMENTS[e.id] = e; });
  function esc(s) { return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
  function text(x, y, s, cls) { return '<text x="'+x+'" y="'+y+'" text-anchor="middle" class="'+cls+'">'+esc(s)+'</text>'; }
  function snapshot(n, title, sub, panels) {
    var s='<svg viewBox="0 0 760 350" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="'+esc(title)+'">';
    s+='<title>'+esc(title)+'</title><rect x="15" y="15" width="730" height="65" rx="9" class="fig-box-hot"/>';
    s+=text(380,42,title,'fig-name')+text(380,65,sub,'fig-sub');
    panels.forEach(function (p,i) { var y=95+i*80;s+='<rect x="15" y="'+y+'" width="730" height="65" rx="9" class="fig-box"/>';s+=text(380,y+25,p[0],'fig-key')+text(380,y+49,p[1],'fig-sub'); });
    return s+'</svg>';
  }
  var content = [
  [
    "选择上下文与检查入口",
    "script_score 在 doToQuery 先检查 expensive 开关",
    [
      [
        "评分请求",
        "默认 boost=1；内层 query 显式给出"
      ],
      [
        "编译服务",
        "先用 project / language / source / context / options 查缓存"
      ],
      [
        "本例范围",
        "以下编译步骤仅在缓存未命中时发生"
      ]
    ],
    "score context 由调用方选定。开关为 false 时在 compile 之前拒绝；通过入口也可能直接复用缓存。"
  ],
  [
    "解析与上下文 Lookup",
    "引擎按 context 取 Compiler 与 Lookup",
    [
      [
        "表的来源",
        "基础允许列表 + 该 context 的资源与扩展"
      ],
      [
        "解析",
        "Walker / ANTLR 把语法变成用户树 SClass"
      ],
      [
        "语义分析",
        "类型、构造器、静态方法在此检查"
      ]
    ],
    "一套编译器实现按不同 context 配置接口与允许列表。插件扩展可增加允许项，不把默认列表泛化成所有部署。"
  ],
  [
    "File 在语义检查被拒",
    "new java.io.File 的默认类型查找返回 null",
    [
      [
        "查找",
        "visitNewObj → canonicalTypeNameToType"
      ],
      [
        "结果",
        "Not a type [java.io.File]."
      ],
      [
        "退出",
        "compile error；本次没有进入 IR 或 ASM"
      ]
    ],
    "这证明拒绝点，不是一次磁盘操作测试。Java File 构造本身也不会创建文件；声明类型走另一个错误入口。"
  ],
  [
    "正常源码继续生成字节码",
    "通过语义检查 → IR → 优化 → ASM",
    [
      [
        "中间表示",
        "用户树转为 ClassNode"
      ],
      [
        "生成",
        "ASM 输出 JVM byte[]"
      ],
      [
        "定义",
        "Loader extends ClassLoader；定义脚本并生成 factory"
      ]
    ],
    "9.4.0 Loader 继承 ClassLoader，有父加载器委派。不能把 findClass 描述成对整个 JVM 可加载类的封闭限制。"
  ],
  [
    "缓存 factory，params 在执行时传入",
    "同节点且键相同、缓存未失效时可复用",
    [
      [
        "缓存键",
        "project · lang · source · context · options"
      ],
      [
        "执行参数",
        "params 不属于上述编译键"
      ],
      [
        "生命周期",
        "淘汰、过期、重启与配置替换可能触发重编译"
      ]
    ],
    "编译缓存不是结果缓存。score 的 factory 接收 params 与 lookup，再创建叶级实例；stored 脚本会重新解析最新源码。"
  ],
  [
    "评分返回值与上下文分工",
    "match_all 默认 _score=1.0；脚本明确读它才组合",
    [
      [
        "popularity 脚本",
        "popular 1.0；cheap 约 0.1"
      ],
      [
        "price × 0.9",
        "cheap 90；popular 72（默认外层 boost=1）"
      ],
      [
        "其他上下文",
        "field 计算返回值；update 改 _source；ingest 改 ctx"
      ]
    ],
    "function_score 的组合由 boost_mode 等决定。评分热路径仍有计算与数据读取；不需要分数时存在跳过评分执行的分支。"
  ],
  [
    "def 的允许列表检查可以发生在执行期",
    "动态 getClass 对照静态 String.getClass",
    [
      [
        "静态 String",
        "编译期 member method ... not found"
      ],
      [
        "def x = 1",
        "运行期 dynamic method ... not found"
      ],
      [
        "共同约束",
        "默认列表没有该方法；def 没有绕过允许列表"
      ]
    ],
    "执行期并非完全没有查表。静态缺失方法与动态缺失方法使用不同拒绝入口；只缓存 factory 不会消掉动态执行成本。"
  ]
];
  window.ESFLOWS = window.ESFLOWS || {};
  window.ESFLOWS['ch26-script-compile'] = {version:1,id:'ch26-script-compile',title:'脚本的编译、缓存与执行边界',speed:2400,steps:content.map(function (p,i) {return {svg:snapshot(i+1,p[0],p[1],p[2]),note:p[3]};})};
})();
