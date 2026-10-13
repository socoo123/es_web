/* 第27课：ES9.4.0固定版本实验与七步机制。 */
(function(){'use strict';
const snapshots=[
  [
    "命令顺序规定结果",
    [
      [
        "FROM",
        "五篇：50/100/150/200/250"
      ],
      [
        "WHERE views > 100",
        "留下150/200/250"
      ],
      [
        "STATS avg(views)",
        "600/3 → 200.0"
      ],
      [
        "优化后的计划",
        "不要求一命令对应一算子"
      ]
    ],
    "竖杠连接表的输入与输出，物理计划可等价改写。"
  ],
  [
    "REST 入口与方法",
    [
      [
        "同步提交",
        "POST /_query，body含query"
      ],
      [
        "动作适配",
        "REST交给EsqlQueryAction"
      ],
      [
        "错误路径",
        "POST /_esql → 405"
      ],
      [
        "异步提交",
        "POST /_query/async"
      ]
    ],
    "405是路由的方法冲突，不是查询执行结果。"
  ],
  [
    "解析与分析",
    [
      [
        "组合逻辑计划",
        "左侧计划喂给右侧PlanFactory"
      ],
      [
        "WHERE / STATS",
        "普通索引：Filter / Aggregate"
      ],
      [
        "FROM 字段解析",
        "绑定字段与类型，views为long"
      ],
      [
        "类型失败",
        "AVG(keyword)在运行前拒绝"
      ]
    ],
    "本图限定普通索引，无BY；时序索引另有分支。"
  ],
  [
    "等价优化保留语义",
    [
      [
        "可下推的数值条件",
        "进入Lucene query"
      ],
      [
        "不可下推的条件",
        "保留需要计算的过滤"
      ],
      [
        "本课 AVG(long)",
        "改写为SUM/COUNT与除法"
      ],
      [
        "观察边界",
        "无FilterOperator不是WHERE失效"
      ]
    ],
    "profile算子名称不能单独证明Lucene query的具体范围。"
  ],
  [
    "Driver 传递列式 Page",
    [
      [
        "Lucene 源与读取",
        "文档位置 → 提取views"
      ],
      [
        "INITIAL 聚合",
        "本例部分sum=600、count=3"
      ],
      [
        "Exchange 中转",
        "可能同节点、多Driver"
      ],
      [
        "工作单位",
        "Page含Block[]与行数"
      ]
    ],
    "256KiB是估算目标，不是每个Page的固定长度或上限。"
  ],
  [
    "合并状态再做除法",
    [
      [
        "FINAL 聚合",
        "合并部分SUM/COUNT状态"
      ],
      [
        "Eval 除法",
        "600/3=200.0"
      ],
      [
        "AVG有效值计数",
        "缺失/null不算，多值都计入"
      ],
      [
        "空输入无BY",
        "一行null；COUNT(*)为0"
      ]
    ],
    "无分组聚合在finish后出结果，早于STATS的LIMIT改变输入。"
  ],
  [
    "输出表与搜索能力",
    [
      [
        "本课默认JSON",
        "columns + values，一行一列"
      ],
      [
        "DSL size:0",
        "hits空，aggs.avg=200.0"
      ],
      [
        "ES|QL 也支持评分",
        "MATCH配METADATA _score"
      ],
      [
        "搜索可见性",
        "未refresh：GET可见，FROM旧视图"
      ]
    ],
    "本课STATS不请求分数；响应没有hits不等于引擎没有_score。"
  ]
];
function escapeText(s){return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
function snapshot(step,i){
 const id='ch27-step-'+(i+1);
 let s='<svg viewBox="0 0 760 350" xmlns="http://www.w3.org/2000/svg"><defs><marker id="'+id+'" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10z" class="fig-arrowhead"/></marker></defs>';
 s+='<rect x="15" y="10" width="730" height="40" rx="9" class="fig-box-hot"/><text x="380" y="35" text-anchor="middle" class="fig-name">'+escapeText(step[0])+'</text>';
 step[1].forEach((card,n)=>{const x=15+(n%2)*375,y=70+Math.floor(n/2)*100;s+='<rect x="'+x+'" y="'+y+'" width="355" height="76" rx="9" class="fig-box fp-pop"/><text x="'+(x+177.5)+'" y="'+(y+28)+'" text-anchor="middle" class="fig-name">'+escapeText(card[0])+'</text><text x="'+(x+177.5)+'" y="'+(y+55)+'" text-anchor="middle" class="fig-sub">'+escapeText(card[1])+'</text>';});
 s+='<rect x="15" y="275" width="730" height="60" rx="9" class="fig-box-hot"/><text x="380" y="310" text-anchor="middle" class="fig-sub">'+escapeText(step[2])+'</text></svg>';return s;
}
window.ESFLOWS=window.ESFLOWS||{};
window.ESFLOWS['ch27-esql-pipeline']={version:1,id:'ch27-esql-pipeline',title:'从管道语义到200.0',speed:2400,steps:snapshots.map((s,i)=>({svg:snapshot(s,i),note:s[2]}))};
window.ESEXPERIMENTS=window.ESEXPERIMENTS||{};
[
  {
    "version": 1,
    "id": "ch27-pre-version",
    "title": "前置 · 确认 ES / Lucene 版本",
    "method": "GET",
    "path": "/",
    "body": null,
    "predict": "节点是否为 9.4.0 / 10.4.0？",
    "expect": "本章固定版本应为 ES9.4.0、Lucene10.4.0；单节点学习端点 localhost:9200。其他版本须重新核对，启用安全时选择有索引 read/write/create/delete 与 ES|QL 权限的认证。"
  },
  {
    "version": 1,
    "id": "ch27-pre-pages",
    "title": "前置 · 确认 tut-l27-pages 不存在",
    "method": "HEAD",
    "path": "/tut-l27-pages",
    "body": null,
    "predict": "为何先要求空白资源？",
    "expect": "预期404、HEAD无响应体。200表示已有资源；仅当你确认它属于本课且可删除，先执行清理再从前置重做，避免旧文档影响均值。"
  },
  {
    "version": 1,
    "id": "ch27-pre-values",
    "title": "前置 · 确认 tut-l27-values 不存在",
    "method": "HEAD",
    "path": "/tut-l27-values",
    "body": null,
    "predict": "为何先要求空白资源？",
    "expect": "预期404、HEAD无响应体。200表示已有资源；仅当你确认它属于本课且可删除，先执行清理再从前置重做，避免旧文档影响均值。"
  },
  {
    "version": 1,
    "id": "ch27-01-setup",
    "title": "A1 · 建主索引，关闭自动 refresh",
    "method": "PUT",
    "path": "/tut-l27-pages",
    "body": {
      "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
        "auto_expand_replicas": "false",
        "refresh_interval": "-1"
      },
      "mappings": {
        "dynamic": "strict",
        "_source": {
          "enabled": true
        },
        "properties": {
          "title": {
            "type": "keyword",
            "doc_values": true
          },
          "description": {
            "type": "text",
            "analyzer": "standard"
          },
          "views": {
            "type": "long",
            "doc_values": true
          }
        }
      }
    },
    "predict": "关闭自动刷新后，bulk refresh=true 还会使数据可见吗？",
    "expect": "200 acknowledged=true。本课普通索引1主0副、strict、数值Doc Values与standard显式配置；refresh_interval=-1用于D组消除自动刷新竞态。重复创建400 resource_already_exists_exception，不会清空原数据。"
  },
  {
    "version": 1,
    "id": "ch27-a-health",
    "title": "A2 · 等待本索引 green",
    "method": "GET",
    "path": "/_cluster/health/tut-l27-pages?wait_for_status=green&wait_for_no_initializing_shards=true&wait_for_no_relocating_shards=true&timeout=30s",
    "body": null,
    "predict": "acknowledged 能否替代分片就绪？",
    "expect": "status=green、timed_out=false、active_primary_shards=1。请求限定本课索引；超时先诊断，不能直接继续灌数据。"
  },
  {
    "version": 1,
    "id": "ch27-a-config",
    "title": "A3 · 读回配置与字段",
    "method": "GET",
    "path": "/tut-l27-pages?filter_path=*.settings.index,*.mappings",
    "body": null,
    "predict": "演示字段是什么类型，自动刷新是否仍关闭？",
    "expect": "number_of_shards=1、replicas=0、auto_expand=false、refresh_interval=-1；views为long、title为keyword、description为text/standard、dynamic=strict。序列化可省略默认true选项，按字段默认语义解释。"
  },
  {
    "version": 1,
    "id": "ch27-02-bulk",
    "title": "A4 · 固定 ID 写五行并显式刷新",
    "method": "POST",
    "path": "/tut-l27-pages/_bulk?refresh=true",
    "body": "{\"index\":{\"_id\":\"1\"}}\n{\"title\":\"a\",\"description\":\"quick brown fox\",\"views\":50}\n{\"index\":{\"_id\":\"2\"}}\n{\"title\":\"b\",\"description\":\"quick fox\",\"views\":100}\n{\"index\":{\"_id\":\"3\"}}\n{\"title\":\"c\",\"description\":\"slow turtle\",\"views\":150}\n{\"index\":{\"_id\":\"4\"}}\n{\"title\":\"d\",\"description\":\"quick brown\",\"views\":200}\n{\"index\":{\"_id\":\"5\"}}\n{\"title\":\"e\",\"description\":\"brown bear\",\"views\":250}\n",
    "predict": "views=100会被 >100 留下吗？",
    "expect": "首次errors=false，5个items均created/201；重复相同bulk为updated/200且不增加文档数。refresh=true保证后续搜索可见；>不含100，留下150/200/250。HTTP200还必须检查每项与errors。"
  },
  {
    "version": 1,
    "id": "ch27-a-count",
    "title": "A5 · 确认恰有五篇",
    "method": "GET",
    "path": "/tut-l27-pages/_count",
    "body": null,
    "predict": "固定ID能否防止重复写入变成十篇？",
    "expect": "count=5、_shards.failed=0。若不同，先点名清理重建，不把受污染数据当作公式证据。"
  },
  {
    "version": 1,
    "id": "ch27-03-main",
    "title": "A6 · 先过滤再平均",
    "method": "POST",
    "path": "/_query?allow_partial_results=false&filter_path=columns,values,is_partial",
    "body": {
      "query": "FROM tut-l27-pages | WHERE views > 100 | STATS avg(views)"
    },
    "predict": "列名、行数、均值分别是什么？",
    "expect": "columns=[avg(views)/double]、values=[[200.0]]，一行一列。本查询is_partial=false，没有hits；未请求_score不代表ES|QL不能评分。filter_path只裁剪响应。"
  },
  {
    "version": 1,
    "id": "ch27-05-case",
    "title": "A7 · 大写 AVG 保持数学",
    "method": "POST",
    "path": "/_query?allow_partial_results=false&filter_path=columns,values,is_partial",
    "body": {
      "query": "FROM tut-l27-pages | WHERE views > 100 | STATS AVG(views)"
    },
    "predict": "函数大写会改变字段名吗？",
    "expect": "列名AVG(views)、值200.0。函数名/命令关键字不区分大小写；未显式起别名的输出名沿用表达式文本。不要据此推断字段标识符不区分大小写。"
  },
  {
    "version": 1,
    "id": "ch27-06-gte",
    "title": "A8 · >= 包含100",
    "method": "POST",
    "path": "/_query?allow_partial_results=false&filter_path=columns,values,is_partial",
    "body": {
      "query": "FROM tut-l27-pages | WHERE views >= 100 | STATS avg(views)"
    },
    "predict": "加入100后分母是多少？",
    "expect": "四个单值：(100+150+200+250)/4=175.0。"
  },
  {
    "version": 1,
    "id": "ch27-07-nowhere",
    "title": "A9 · 五行全平均",
    "method": "POST",
    "path": "/_query?allow_partial_results=false&filter_path=columns,values,is_partial",
    "body": {
      "query": "FROM tut-l27-pages | STATS avg(views)"
    },
    "predict": "不加WHERE会得到哪个均值？",
    "expect": "750/5=150.0；普通索引Aggregate直接接数据源。命令顺序决定语义，物理优化仍须保持结果。"
  },
  {
    "version": 1,
    "id": "ch27-12-sort-keep",
    "title": "A10 · SORT / KEEP / LIMIT",
    "method": "POST",
    "path": "/_query?allow_partial_results=false&filter_path=columns,values,is_partial",
    "body": {
      "query": "FROM tut-l27-pages | SORT views DESC | KEEP title, views | LIMIT 2"
    },
    "predict": "KEEP和LIMIT各改变什么？",
    "expect": "columns顺序title、views；values=[[e,250],[d,200]]。本例views互异，排序稳定；KEEP挑列，LIMIT截行，并非每个命令都让表变小。"
  },
  {
    "version": 1,
    "id": "ch27-08-profile",
    "title": "A11 · 查看本次完整 profile",
    "method": "POST",
    "path": "/_query?allow_partial_results=false",
    "body": {
      "query": "FROM tut-l27-pages | WHERE views > 100 | STATS avg(views)",
      "profile": true
    },
    "predict": "一定只有两条Driver，或一定有FilterOperator吗？",
    "expect": "值200.0；本轮真实观测含INITIAL、FINAL、SumLong、Count与DivDoublesEvaluator，且无FilterOperator。还出现Exchange中转Driver；数量/顺序/描述不是API稳定契约。Lucene源名称本身不足以证明具体range，须结合下推源码和结果边界。"
  },
  {
    "version": 1,
    "id": "ch27-a-limit-before",
    "title": "A12 · 聚合前 LIMIT 2",
    "method": "POST",
    "path": "/_query?allow_partial_results=false&filter_path=columns,values,is_partial",
    "body": {
      "query": "FROM tut-l27-pages | WHERE views > 100 | SORT views DESC | LIMIT 2 | STATS avg(views)"
    },
    "predict": "算的是三行还是排序后的两行？",
    "expect": "(250+200)/2=225.0。显式LIMIT在STATS前，主动缩小输入集合；不能声称所有聚合都扫描原始索引全集。"
  },
  {
    "version": 1,
    "id": "ch27-a-limit-after",
    "title": "A13 · 聚合后 LIMIT 1",
    "method": "POST",
    "path": "/_query?allow_partial_results=false&filter_path=columns,values,is_partial",
    "body": {
      "query": "FROM tut-l27-pages | WHERE views > 100 | STATS avg(views) | LIMIT 1"
    },
    "predict": "LIMIT1会只取一个原始值求均值吗？",
    "expect": "仍200.0，LIMIT作用于STATS输出的一行，不截掉聚合输入。普通FROM默认/最大输出限制与此处显式前置LIMIT是不同条件。"
  },
  {
    "version": 1,
    "id": "ch27-a-type-error",
    "title": "A14 · keyword不能直接 AVG",
    "method": "POST",
    "path": "/_query?allow_partial_results=false&filter_path=columns,values,is_partial",
    "body": {
      "query": "FROM tut-l27-pages | STATS avg(title)"
    },
    "predict": "值长得像数字就一定可平均吗？",
    "expect": "400 verification_exception：AVG要求支持的数值/聚合类型，title是keyword。修复查询或字段mapping，不必删掉正确的主数据；之后正确主查询仍应200.0。"
  },
  {
    "version": 1,
    "id": "ch27-09-dsl-avg",
    "title": "B1 · DSL过滤后AVG",
    "method": "POST",
    "path": "/tut-l27-pages/_search?request_cache=false&filter_path=hits.total,hits.hits,aggregations.avg_views.value",
    "body": {
      "query": {
        "range": {
          "views": {
            "gt": 100
          }
        }
      },
      "aggs": {
        "avg_views": {
          "avg": {
            "field": "views"
          }
        }
      },
      "size": 0
    },
    "predict": "hits有几篇、AVG看哪个集合？",
    "expect": "200.0；hits为空。request_cache=false只控制本请求结果缓存，不改索引配置。"
  },
  {
    "version": 1,
    "id": "ch27-10-dsl-hits",
    "title": "B2 · 同时返回源文档",
    "method": "POST",
    "path": "/tut-l27-pages/_search?request_cache=false&filter_path=hits.total,hits.hits,aggregations.avg_views.value",
    "body": {
      "query": {
        "range": {
          "views": {
            "gt": 100
          }
        }
      },
      "aggs": {
        "avg_views": {
          "avg": {
            "field": "views"
          }
        }
      },
      "sort": [
        {
          "views": "desc"
        }
      ]
    },
    "predict": "hits有几篇、AVG看哪个集合？",
    "expect": "200.0；默认size10返回5/4/3三篇源文档。request_cache=false只控制本请求结果缓存，不改索引配置。"
  },
  {
    "version": 1,
    "id": "ch27-11-dsl-gte",
    "title": "B3 · DSL >= 对照",
    "method": "POST",
    "path": "/tut-l27-pages/_search?request_cache=false&filter_path=hits.total,hits.hits,aggregations.avg_views.value",
    "body": {
      "query": {
        "range": {
          "views": {
            "gte": 100
          }
        }
      },
      "aggs": {
        "avg_views": {
          "avg": {
            "field": "views"
          }
        }
      },
      "size": 0
    },
    "predict": "hits有几篇、AVG看哪个集合？",
    "expect": "175.0、hits为空。request_cache=false只控制本请求结果缓存，不改索引配置。"
  },
  {
    "version": 1,
    "id": "ch27-b-size-one",
    "title": "B4 · hits窗口不改变聚合",
    "method": "POST",
    "path": "/tut-l27-pages/_search?request_cache=false&filter_path=hits.total,hits.hits,aggregations.avg_views.value",
    "body": {
      "query": {
        "range": {
          "views": {
            "gt": 100
          }
        }
      },
      "aggs": {
        "avg_views": {
          "avg": {
            "field": "views"
          }
        }
      },
      "size": 1,
      "sort": [
        {
          "views": "desc"
        }
      ]
    },
    "predict": "hits有几篇、AVG看哪个集合？",
    "expect": "200.0；只回_id=5的一篇源文档，AVG仍看三篇。request_cache=false只控制本请求结果缓存，不改索引配置。"
  },
  {
    "version": 1,
    "id": "ch27-04-wrong-path",
    "title": "B5 · 错路径返回405",
    "method": "POST",
    "path": "/_esql",
    "body": {
      "query": "FROM tut-l27-pages | LIMIT 1"
    },
    "predict": "无ES|QL路由就一定404吗？",
    "expect": "405 Incorrect HTTP method，allowed含GET/PUT/DELETE/HEAD；裸索引路由/{index}发生方法冲突，查询没有执行。allowed不是功能授权列表。"
  },
  {
    "version": 1,
    "id": "ch27-b-wrong-method",
    "title": "B6 · 正确路径的错误方法",
    "method": "GET",
    "path": "/_query",
    "body": null,
    "predict": "GET能提交同步查询吗？",
    "expect": "405 allowed:[POST]。无body；改回POST并提供query恢复。"
  },
  {
    "version": 1,
    "id": "ch27-13-async-route",
    "title": "B7 · 异步提交路径的错误方法",
    "method": "GET",
    "path": "/_query/async",
    "body": null,
    "predict": "这张卡有没有真的提交异步任务？",
    "expect": "405 allowed:[POST]，只验证方法冲突。实际异步提交是POST /_query/async，取回/删除还需要带id的独立路由；本课没有创建异步结果需要清理。"
  },
  {
    "version": 1,
    "id": "ch27-c-setup",
    "title": "C1 · 单独建立空值/多值索引",
    "method": "PUT",
    "path": "/tut-l27-values",
    "body": {
      "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
        "auto_expand_replicas": "false",
        "refresh_interval": "-1"
      },
      "mappings": {
        "dynamic": "strict",
        "properties": {
          "title": {
            "type": "keyword"
          },
          "views": {
            "type": "long",
            "doc_values": true
          }
        }
      }
    },
    "predict": "为什么不把新值混入主查询五篇？",
    "expect": "200 acknowledged=true；隔离数据保护A组均值。重复创建400，清理后重建。普通数值mapping仍可容纳数组和缺失值。"
  },
  {
    "version": 1,
    "id": "ch27-c-health",
    "title": "C2 · 等待值索引 green",
    "method": "GET",
    "path": "/_cluster/health/tut-l27-values?wait_for_status=green&wait_for_no_initializing_shards=true&timeout=30s",
    "body": null,
    "predict": "另一个索引也要等待吗？",
    "expect": "green、timed_out=false、1个主分片，继续C3。"
  },
  {
    "version": 1,
    "id": "ch27-c-bulk",
    "title": "C3 · 写单值、多值、缺失、null",
    "method": "POST",
    "path": "/tut-l27-values/_bulk?refresh=true",
    "body": "{\"index\":{\"_id\":\"1\"}}\n{\"title\":\"single\",\"views\":10}\n{\"index\":{\"_id\":\"2\"}}\n{\"title\":\"multi\",\"views\":[20,40]}\n{\"index\":{\"_id\":\"3\"}}\n{\"title\":\"missing\"}\n{\"index\":{\"_id\":\"4\"}}\n{\"title\":\"null\",\"views\":null}\n",
    "predict": "四篇文档有几个有效数值？",
    "expect": "首次4项created/201、errors=false；有效值10/20/40共3个，缺失与显式null未配置null_value，因此不产生数值。重复写updated/200仍4篇。"
  },
  {
    "version": 1,
    "id": "ch27-c-count",
    "title": "C4 · 文档总数为4",
    "method": "GET",
    "path": "/tut-l27-values/_count",
    "body": null,
    "predict": "文档总数能直接当AVG分母吗？",
    "expect": "count=4；后卡COUNT(views)=3，区别是有效值与文档。"
  },
  {
    "version": 1,
    "id": "ch27-c-values",
    "title": "C5 · AVG分母是有效值数",
    "method": "POST",
    "path": "/_query?allow_partial_results=false&filter_path=columns,values,is_partial",
    "body": {
      "query": "FROM tut-l27-values | STATS mean=AVG(views), total=SUM(views), value_count=COUNT(views), rows=COUNT(*)"
    },
    "predict": "70除以4还是3？",
    "expect": "列顺序mean/total/value_count/rows；values约[[23.333333333333332,70,3,4]]。AVG忽略null/缺失、计入多值；仅单值且非空时COUNT(field)才等于行数。浮点数按容差比较。"
  },
  {
    "version": 1,
    "id": "ch27-c-empty",
    "title": "C6 · 空输入的无分组STATS",
    "method": "POST",
    "path": "/_query?allow_partial_results=false&filter_path=columns,values,is_partial",
    "body": {
      "query": "FROM tut-l27-values | WHERE views > 1000 | STATS mean=AVG(views), rows=COUNT(*)"
    },
    "predict": "空输入返回零行还是一行null？",
    "expect": "values=[[null,0]]，无BY仍输出一行；AVG不是0，没有可用值；不能拿0/0的普通算术模拟实现的null/seen状态。"
  },
  {
    "version": 1,
    "id": "ch27-d-score",
    "title": "D1 · MATCH 与 _score",
    "method": "POST",
    "path": "/_query?allow_partial_results=false&filter_path=columns,values,is_partial",
    "body": {
      "query": "FROM tut-l27-pages METADATA _score | WHERE MATCH(description, \"fox\") | SORT _score DESC, title ASC | KEEP title, _score | LIMIT 2"
    },
    "predict": "ES|QL一定没有评分能力吗？",
    "expect": "两行title为a和b、_score为正数，本轮列类型double；本轮顺序b/a。评分数值依字段统计和版本，不写死。9.4支持全文函数与评分；没有_search的hits包装与不能评分是两回事。"
  },
  {
    "version": 1,
    "id": "ch27-d-write",
    "title": "D2 · 不刷新写第六篇",
    "method": "PUT",
    "path": "/tut-l27-pages/_doc/6?refresh=false",
    "body": {
      "title": "pending",
      "description": "quick fox",
      "views": 300
    },
    "predict": "自动refresh=-1且无其他刷新时，GET与FROM会一致吗？",
    "expect": "首次201 created；重复200 updated。只改本课索引，refresh=false不触发刷新；起步要求A组count5。D组连续完成，若有外部refresh须重置D6并从D2重做。"
  },
  {
    "version": 1,
    "id": "ch27-d-get",
    "title": "D3 · realtime GET可读",
    "method": "GET",
    "path": "/tut-l27-pages/_doc/6",
    "body": null,
    "predict": "GET已看到300，FROM必然也看到吗？",
    "expect": "200 found=true、_source.views=300。默认realtime GET可读未刷新写入，不证明搜索读者可见。"
  },
  {
    "version": 1,
    "id": "ch27-d-before",
    "title": "D4 · 刷新前FROM仍五篇",
    "method": "POST",
    "path": "/_query?allow_partial_results=false&filter_path=columns,values,is_partial",
    "body": {
      "query": "FROM tut-l27-pages | STATS rows=COUNT(*)"
    },
    "predict": "新文档进搜索视图了吗？",
    "expect": "在本课关闭自动刷新且无外部刷新的前提下values=[[5]]。结果6表示前提已被刷新打破，不能当GET和FROM等价的证据。"
  },
  {
    "version": 1,
    "id": "ch27-d-refresh",
    "title": "D5 · 显式刷新主索引",
    "method": "POST",
    "path": "/tut-l27-pages/_refresh",
    "body": null,
    "predict": "刷新会修改文档还是打开新搜索视图？",
    "expect": "200 _shards.failed=0；推进搜索可见性，不等同fsync或持久化提交。"
  },
  {
    "version": 1,
    "id": "ch27-d-after",
    "title": "D6 · 刷新后四个值平均",
    "method": "POST",
    "path": "/_query?allow_partial_results=false&filter_path=columns,values,is_partial",
    "body": {
      "query": "FROM tut-l27-pages | WHERE views > 100 | STATS avg(views)"
    },
    "predict": "150/200/250/300均值是多少？",
    "expect": "values=[[225.0]]，第六篇已可见；此时A组主值临时改变。"
  },
  {
    "version": 1,
    "id": "ch27-d-reset",
    "title": "D7 · 删除第六篇并刷新",
    "method": "DELETE",
    "path": "/tut-l27-pages/_doc/6?refresh=true",
    "body": null,
    "predict": "怎样恢复A组五篇前提？",
    "expect": "200 result=deleted；refresh=true使搜索视图也去掉第六篇。重复删除404 not_found，本课不依赖执行得快。"
  },
  {
    "version": 1,
    "id": "ch27-d-restored",
    "title": "D8 · 读回主值与行数",
    "method": "POST",
    "path": "/_query?allow_partial_results=false&filter_path=columns,values,is_partial",
    "body": {
      "query": "FROM tut-l27-pages | WHERE views > 100 | STATS mean=AVG(views), rows=COUNT(*)"
    },
    "predict": "复原成功的证据是什么？",
    "expect": "values=[[200.0,3]]。D2以后中断时先执行D7，再从D2重新开始；完整重做须执行末尾两索引清理并回到前置。"
  },
  {
    "version": 1,
    "id": "ch27-14-cleanup",
    "title": "清理1 · 点名删主索引",
    "method": "DELETE",
    "path": "/tut-l27-pages",
    "body": null,
    "predict": "清理删除什么？",
    "expect": "200 acknowledged=true，删除本课主索引及六号文档（若仍在），不修改集群设置。再次清理404。确认资源属于本课后才执行。"
  },
  {
    "version": 1,
    "id": "ch27-clean-pages",
    "title": "清理2 · 主索引确实不存在",
    "method": "HEAD",
    "path": "/tut-l27-pages",
    "body": null,
    "predict": "清理成功的读回证据？",
    "expect": "404、无body；然后删除值索引。"
  },
  {
    "version": 1,
    "id": "ch27-clean-values-delete",
    "title": "清理3 · 点名删值索引",
    "method": "DELETE",
    "path": "/tut-l27-values",
    "body": null,
    "predict": "能用通配符批删吗？",
    "expect": "200 acknowledged=true；本课显式点名，避免通配符破坏限制及误删。重复404。"
  },
  {
    "version": 1,
    "id": "ch27-clean-values",
    "title": "清理4 · 确认值索引不存在",
    "method": "HEAD",
    "path": "/tut-l27-values",
    "body": null,
    "predict": "下一轮从哪里开始？",
    "expect": "404；重做从前置版本/两HEAD → A → B → C → D → 清理，先确认单节点、认证和数据空白条件。"
  }
].forEach(e=>{window.ESEXPERIMENTS[e.id]=e;});
})();
