/* experiments/ch19.js — 第 19 课:聚合框架实验 + cherry 丢失演算动画(注册表) */
(function () {
  'use strict';

  /* ===== 动画:cherry 是怎么丢的 ===== */
  function defs(id) {
    return '<defs><marker id="' + id + '" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
      + '<path d="M 0 0 L 10 5 L 0 10 z" class="fig-arrowhead"/></marker></defs>';
  }
  function rect(x, y, w, h, cls, anim) {
    return '<rect x="' + x + '" y="' + y + '" width="' + w + '" height="' + h + '" rx="9" class="' + cls + (anim ? ' ' + anim : '') + '"/>';
  }
  function txt(x, y, s, cls, warn, anim) {
    var st = warn ? ' style="fill: rgb(var(--warn))"' : '';
    return '<text x="' + x + '" y="' + y + '" text-anchor="middle" class="' + cls + (anim ? ' ' + anim : '') + '"' + st + '>' + s + '</text>';
  }
  function line(x1, y1, x2, y2, id) {
    return '<line x1="' + x1 + '" y1="' + y1 + '" x2="' + x2 + '" y2="' + y2 + '" class="fig-arrow" marker-end="url(#' + id + ')"/>';
  }

  /* 步骤 1:请求到达 */
  function step1() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('ah19s1');
    s += rect(15, 25, 730, 60, 'fig-box');
    s += txt(380, 49, '{"size":0,"aggs":{"top":{"terms":{"field":"fruit","size":2}}}}', 'fig-key');
    s += txt(380, 71, '两个单分片索引 s0 + s1 合搜 = 两个分片组参与 Query，协调角色归并结果', 'fig-sub');
    s += rect(15, 112, 730, 58, 'fig-box-hot', 'fp-pop');
    s += txt(380, 134, '聚合跟 hits 同一趟 Query 相位回来', 'fig-name');
    s += txt(380, 156, '塞进 QuerySearchResult.aggregations;普通桶/数值聚合不靠 hits Fetch；top_hits 另有取字段工作', 'fig-sub');
    s += txt(380, 204, 'size: 0 表示不要 hits,只要聚合——本课只关心桶', 'fig-sub');
    s += txt(380, 228, '主线:每个 shard 送几个桶,决定协调节点能看见谁', 'fig-sub');
    s += txt(380, 262, 'size 是客户端要的全局桶数,不是每个 shard 的配额', 'fig-sub');
    return s + '</svg>';
  }

  /* 步骤 2:shard 本地计数 */
  function step2() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('ah19s2');
    s += rect(15, 20, 355, 118, 'fig-box');
    s += txt(192, 44, 'shard 0 · 局部词频', 'fig-name');
    s += txt(192, 72, 'apple:6 banana:3 cherry:2', 'fig-key');
    s += txt(192, 96, 'cherry 本地第 3', 'fig-sub');
    s += txt(192, 120, '11 篇,3 个值', 'fig-sub');
    s += rect(390, 20, 355, 118, 'fig-box');
    s += txt(567, 44, 'shard 1 · 局部词频', 'fig-name');
    s += txt(567, 72, 'date:4 apple:4 cherry:3', 'fig-key');
    s += txt(567, 96, 'cherry 本地第 3', 'fig-sub');
    s += txt(567, 120, '11 篇,3 个值', 'fig-sub');
    s += rect(15, 158, 730, 62, 'fig-box', 'fp-pop');
    s += txt(380, 182, '逻辑上统计全部合格字段值', 'fig-name');
    s += txt(380, 204, '状态受基数与执行策略影响；size 不是内存额度', 'fig-sub');
    s += txt(380, 250, 'cherry 在两片都是本地第 3——但全局真实计数 5,是第 2 名', 'fig-sub', true);
    return s + '</svg>';
  }

  /* 步骤 3:shard_size=2 只送 Top-2 */
  function step3() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('ah19s3');
    s += rect(15, 20, 355, 142, 'fig-box');
    s += txt(192, 44, 'shard 0 只送 Top-2', 'fig-name');
    s += txt(192, 74, 'apple:6 上送 / banana:3 上送', 'fig-key');
    s += txt(192, 104, 'cherry:2 丢弃', 'fig-key', true);
    s += txt(192, 130, '挤进本片 sum_other', 'fig-sub', true);
    s += rect(390, 20, 355, 142, 'fig-box');
    s += txt(567, 44, 'shard 1 只送 Top-2', 'fig-name');
    s += txt(567, 74, 'date:4 上送 / apple:4 上送', 'fig-key');
    s += txt(567, 104, 'cherry:3 丢弃', 'fig-key', true);
    s += txt(567, 130, '挤进本片 sum_other', 'fig-sub', true);
    s += rect(15, 182, 730, 58, 'fig-box-hot', 'fp-pop');
    s += txt(380, 204, 'shard_size=2 的语义', 'fig-name');
    s += txt(380, 226, '用户显式写了 shard_size,启发式不跑;优先队列长度 = min(值数, 2)', 'fig-sub');
    s += txt(380, 268, '普通路径在 buildAggregations 选候选，并非只统计 2 个值', 'fig-sub');
    return s + '</svg>';
  }

  /* 步骤 4:reduce 看不见 cherry */
  function step4() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('ah19s4');
    s += rect(15, 20, 730, 66, 'fig-box');
    s += txt(380, 44, '协调节点 reduce:同 key 相加', 'fig-name');
    s += txt(380, 72, 'apple 6+4=10 banana 3 date 4;cherry 两片都没送，不存在这个候选', 'fig-key');
    s += rect(15, 112, 730, 66, 'fig-box-hot', 'fp-pop');
    s += txt(380, 136, '截 size=2:apple:10、date:4', 'fig-name');
    s += txt(380, 164, '全局第 2 名 cherry:5 失踪,date:4 顶了上去', 'fig-sub', true);
    s += rect(15, 200, 730, 58, 'fig-box');
    s += txt(380, 222, '账本留痕,不补回', 'fig-name');
    s += txt(380, 244, 'sum_other=8；聚合误差上界=7，不补回桶', 'fig-sub');
    s += txt(380, 284, '协调节点看不见的 key,reduce 永远加不回来', 'fig-sub', true);
    return s + '</svg>';
  }

  /* 步骤 5:默认启发式 13 */
  function step5() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('ah19s5');
    s += rect(15, 25, 730, 64, 'fig-box');
    s += txt(380, 49, 'BucketUtils.suggestShardSideQueueSize', 'fig-name');
    s += txt(380, 77, 'shardSize = size * 1.5 + 10 = 2*1.5+10 = 13', 'fig-key');
    s += rect(15, 112, 730, 62, 'fig-box-hot', 'fp-pop');
    s += txt(380, 136, '容量 13 大于本例每片 3 个值', 'fig-name');
    s += txt(380, 158, 'cherry 两边都进得了队列——过采样保护的就是「本地第 3」', 'fig-sub');
    s += txt(380, 206, '只在用户没写 shard_size 且不是按 _key 排序时套用', 'fig-sub');
    s += txt(380, 228, 'ensureValidity 兜底:shardSize 至少抬到等于 size', 'fig-sub');
    s += txt(380, 262, '+10 是小 size 的常数垫；本例容量 3 已覆盖全部值', 'fig-sub');
    return s + '</svg>';
  }

  /* 步骤 6:final 截 2 + 对照 hits */
  function step6() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('ah19s6');
    s += rect(15, 20, 730, 62, 'fig-box-hot', 'fp-pop');
    s += txt(380, 44, 'final reduce 截 size=2', 'fig-name');
    s += txt(380, 70, 'apple:10、cherry:5 —— 全局第 2 回来了', 'fig-key');
    s += rect(15, 104, 355, 96, 'fig-box');
    s += txt(192, 128, 'terms 的窗口', 'fig-name');
    s += txt(192, 154, 'shardSize 过采样', 'fig-key');
    s += txt(192, 178, '近似保排名,压小误差上界', 'fig-sub');
    s += rect(390, 104, 355, 96, 'fig-box');
    s += txt(567, 128, 'hits 的窗口', 'fig-name');
    s += txt(567, 154, 'from + size', 'fig-key');
    s += txt(567, 178, '固定排名键：全局前 k 来自局部前 k', 'fig-sub');
    s += txt(380, 234, 'range 给定区间；histogram 按值和间隔算 key，无 Top-terms 截断', 'fig-sub');
    s += txt(380, 262, '固定排序键的 hits 窗口，与 terms 的跨片计数候选不同', 'fig-sub');
    return s + '</svg>';
  }

  window.ESFLOWS = window.ESFLOWS || {};
  window.ESFLOWS['ch19-shard-size'] = {
    version: 1,
    id: 'ch19-shard-size',
    title: 'cherry 是怎么丢的:shardSize 演算',
    speed: 2400,
    steps: [
      { svg: step1(), note: 'terms 的 size=2 是客户端要的全局桶数,不是每个 shard 的配额。普通桶/数值聚合统计主query范围，不依赖主hits Fetch；未进入Top-N的文档仍可贡献桶。' },
      { svg: step2(), note: 'shard 0:apple:6 banana:3 cherry:2;shard 1:date:4 apple:4 cherry:3。逻辑统计覆盖全部合格值；具体可用序数、哈希或filters等策略，响应不能证明计数器数量。cherry 两片都是本地第 3,全局却是第 2。' },
      { svg: step3(), note: '显式写 shard_size=2:启发式不跑,优先队列只留 min(值数, 2) 个。截断发生在 buildAggregations——普通收集先统计全部合格值，构建局部结果才筛候选。cherry 在两片都被挤出队列,记进本片 sum_other。' },
      { svg: step4(), note: '协调节点只加它看见的桶:apple 6+4=10、banana 3、date 4;cherry 没人送，因此没有候选。截 size=2 得 apple:10、date:4——真正的全局第 2 cherry:5 失踪。sum_other=8、聚合 error_bound=7；上界不是精确误差,不补回任何 key。' },
      { svg: step5(), note: '默认 shardSize = size×1.5+10 = 13 ≥ 每片 3 个值,全部上送,cherry 回到候选。这条启发式只在没写 shard_size 且非 key 序时启用;ensureValidity 还兜底 shardSize ≥ size。+10 是小 size 的常数垫。' },
      { svg: step6(), note: 'final reduce 才截客户端要的 size:apple:10、cherry:5,排名修正。hits 用 from+size 严格保住第 k 名(分数可比较),terms 按 count 加总,count 降序本地第3可合计成全局第2，候选不足会近似。range/histogram 按规则分桶，不走 terms 的局部 Top-N 筛选。' }
    ]
  };

  /* ===== 实验：固定ID、显式配置与点名重做 ===== */
  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};
  window.ESEXPERIMENTS["ch19-00-setup-shop"] = {
  "version": 1,
  "id": "ch19-00-setup-shop",
  "title": "A1 · 建 tut-l19-shop:category/price/date",
  "method": "PUT",
  "path": "/tut-l19-shop",
  "body": {
    "settings": {
      "number_of_shards": 1,
      "number_of_replicas": 0,
      "auto_expand_replicas": "false",
      "refresh_interval": "-1",
      "requests.cache.enable": false,
      "default_pipeline": "_none",
      "final_pipeline": "_none",
      "mapping.source.mode": "stored"
    },
    "mappings": {
      "properties": {
        "category": {
          "type": "keyword"
        },
        "price": {
          "type": "float"
        },
        "date": {
          "type": "date"
        }
      },
      "dynamic": "strict",
      "date_detection": false,
      "numeric_detection": false
    }
  },
  "predict": "terms 聚合跑在哪种字段上?text 还是 keyword?",
  "expect": "首次 200、acknowledged=true；重复创建 400 resource_already_exists_exception，原资源不重置。按本组健康等待再写入；数据不符时点名清理四索引，从 A1 重做。"
};
  window.ESEXPERIMENTS["ch19-17-wait-shop"] = {
  "version": 1,
  "id": "ch19-17-wait-shop",
  "title": "A2 · 等待本组主分片 green",
  "method": "GET",
  "path": "/_cluster/health/tut-l19-shop?wait_for_status=green&wait_for_no_initializing_shards=true&timeout=30s",
  "body": null,
  "predict": "请求返回后能开始写入吗?",
  "expect": "status=green、timed_out=false、active_primary_shards=1。只等本组资源；超时先检查节点/分片，再重跑本卡，不继续后面的对照。"
};
  window.ESEXPERIMENTS["ch19-01-bulk-shop"] = {
  "version": 1,
  "id": "ch19-01-bulk-shop",
  "title": "A3 · 小店 8 篇:electronics/books/clothing",
  "method": "POST",
  "path": "/_bulk?refresh=true",
  "body": "{\"index\":{\"_index\":\"tut-l19-shop\",\"_id\":\"1\"}}\n{\"category\":\"electronics\",\"price\":299.99,\"date\":\"2024-01-15\"}\n{\"index\":{\"_index\":\"tut-l19-shop\",\"_id\":\"2\"}}\n{\"category\":\"books\",\"price\":19.99,\"date\":\"2024-01-20\"}\n{\"index\":{\"_index\":\"tut-l19-shop\",\"_id\":\"3\"}}\n{\"category\":\"electronics\",\"price\":149.99,\"date\":\"2024-02-10\"}\n{\"index\":{\"_index\":\"tut-l19-shop\",\"_id\":\"4\"}}\n{\"category\":\"clothing\",\"price\":49.99,\"date\":\"2024-02-15\"}\n{\"index\":{\"_index\":\"tut-l19-shop\",\"_id\":\"5\"}}\n{\"category\":\"books\",\"price\":29.99,\"date\":\"2024-03-01\"}\n{\"index\":{\"_index\":\"tut-l19-shop\",\"_id\":\"6\"}}\n{\"category\":\"electronics\",\"price\":599.99,\"date\":\"2024-03-10\"}\n{\"index\":{\"_index\":\"tut-l19-shop\",\"_id\":\"7\"}}\n{\"category\":\"books\",\"price\":24.99,\"date\":\"2024-03-15\"}\n{\"index\":{\"_index\":\"tut-l19-shop\",\"_id\":\"8\"}}\n{\"category\":\"clothing\",\"price\":79.99,\"date\":\"2024-04-01\"}\n",
  "predict": "electronics / books / clothing 各几篇?terms 会回几个桶?",
  "expect": "errors: false,8 项。electronics 3、books 3、clothing 2——默认 size=10 足够放下 3 个桶。 固定 ID 首次 created/201，重复写 updated/200，篇数不增加；确认 errors=false 后再搜索。refresh=true 只刷新本次触及分片，不改周期设置。"
};
  window.ESEXPERIMENTS["ch19-02-terms-avg"] = {
  "version": 1,
  "id": "ch19-02-terms-avg",
  "title": "A4 · Bucket 套 Metric:by_category + avg_price",
  "method": "POST",
  "path": "/tut-l19-shop/_search?filter_path=aggregations",
  "body": {
    "size": 0,
    "aggs": {
      "by_category": {
        "terms": {
          "field": "category"
        },
        "aggs": {
          "avg_price": {
            "avg": {
              "field": "price"
            }
          }
        }
      }
    }
  },
  "predict": "avg_price 会对全部 8 篇算,还是只在各自桶内算?hits 一条没有,size 哪去了?",
  "expect": "books3、electronics3、clothing2；默认同 count 按 key 升序。均价约24.99、349.99、64.99；float 表示会有尾数。顶层 size=0 只限制 hits，terms 默认 size=10。"
};
  window.ESEXPERIMENTS["ch19-03-fixed-keys"] = {
  "version": 1,
  "id": "ch19-03-fixed-keys",
  "title": "A5 · date_histogram + range:桶 key 事先定",
  "method": "POST",
  "path": "/tut-l19-shop/_search?filter_path=aggregations",
  "body": {
    "size": 0,
    "aggs": {
      "by_month": {
        "date_histogram": {
          "field": "date",
          "calendar_interval": "month"
        }
      },
      "price_ranges": {
        "range": {
          "field": "price",
          "ranges": [
            {
              "to": 50
            },
            {
              "from": 50,
              "to": 200
            },
            {
              "from": 200
            }
          ]
        }
      }
    }
  },
  "predict": "这两个聚合需要 shard_size 过采样吗?",
  "expect": "月份2024-01/02/03/04计数2/2/3/1；价格区间*-50.0、50.0-200.0、200.0-*计数4/2/2。range下界含、上界不含；日历月按值与UTC边界算key，并非枚举全部月份。两者无terms候选截断。"
};
  window.ESEXPERIMENTS["ch19-18-hits-one"] = {
  "version": 1,
  "id": "ch19-18-hits-one",
  "title": "A6 · 只取1个 hit，聚合仍看8篇",
  "method": "POST",
  "path": "/tut-l19-shop/_search",
  "body": {
    "size": 1,
    "sort": [
      {
        "price": "asc"
      }
    ],
    "aggs": {
      "by_category": {
        "terms": {
          "field": "category"
        }
      }
    }
  },
  "predict": "聚合会只统计这一条hit吗?",
  "expect": "hits.total=8、hits只1项（id2），聚合仍books3/electronics3/clothing2。无global、采样、terminate_after/min_score等特殊范围。"
};
  window.ESEXPERIMENTS["ch19-19-query-scope"] = {
  "version": 1,
  "id": "ch19-19-query-scope",
  "title": "A7 · query先缩小聚合范围",
  "method": "POST",
  "path": "/tut-l19-shop/_search",
  "body": {
    "size": 0,
    "query": {
      "term": {
        "category": "books"
      }
    },
    "aggs": {
      "by_category": {
        "terms": {
          "field": "category"
        }
      }
    }
  },
  "predict": "size0或query会改变哪些范围?",
  "expect": "hits.total=3、hits为空，聚合仅books3。size控制hits窗口，query改变普通顶层聚合输入；与A6对照。"
};
  window.ESEXPERIMENTS["ch19-04-setup-s0"] = {
  "version": 1,
  "id": "ch19-04-setup-s0",
  "title": "B1 · 建 tut-l19-s0(单分片)",
  "method": "PUT",
  "path": "/tut-l19-s0",
  "body": {
    "settings": {
      "number_of_shards": 1,
      "number_of_replicas": 0,
      "auto_expand_replicas": "false",
      "refresh_interval": "-1",
      "requests.cache.enable": false,
      "default_pipeline": "_none",
      "final_pipeline": "_none",
      "mapping.source.mode": "stored"
    },
    "mappings": {
      "properties": {
        "fruit": {
          "type": "keyword"
        },
        "price": {
          "type": "double"
        }
      },
      "dynamic": "strict",
      "date_detection": false,
      "numeric_detection": false
    }
  },
  "predict": "为什么用两个单分片索引,而不是一个两分片索引?",
  "expect": "首次 200、acknowledged=true；重复创建 400 resource_already_exists_exception，原资源不重置。按本组健康等待再写入；数据不符时点名清理四索引，从 A1 重做。"
};
  window.ESEXPERIMENTS["ch19-05-setup-s1"] = {
  "version": 1,
  "id": "ch19-05-setup-s1",
  "title": "B2 · 建 tut-l19-s1(单分片)",
  "method": "PUT",
  "path": "/tut-l19-s1",
  "body": {
    "settings": {
      "number_of_shards": 1,
      "number_of_replicas": 0,
      "auto_expand_replicas": "false",
      "refresh_interval": "-1",
      "requests.cache.enable": false,
      "default_pipeline": "_none",
      "final_pipeline": "_none",
      "mapping.source.mode": "stored"
    },
    "mappings": {
      "properties": {
        "fruit": {
          "type": "keyword"
        },
        "price": {
          "type": "double"
        }
      },
      "dynamic": "strict",
      "date_detection": false,
      "numeric_detection": false
    }
  },
  "predict": "两个索引的 mapping 必须一致吗?",
  "expect": "首次 200、acknowledged=true；重复创建 400 resource_already_exists_exception，原资源不重置。按本组健康等待再写入；数据不符时点名清理四索引，从 A1 重做。"
};
  window.ESEXPERIMENTS["ch19-20-wait-fruits"] = {
  "version": 1,
  "id": "ch19-20-wait-fruits",
  "title": "B3 · 等待本组主分片 green",
  "method": "GET",
  "path": "/_cluster/health/tut-l19-s0,tut-l19-s1?wait_for_status=green&wait_for_no_initializing_shards=true&timeout=30s",
  "body": null,
  "predict": "请求返回后能开始写入吗?",
  "expect": "status=green、timed_out=false、active_primary_shards=2。只等本组资源；超时先检查节点/分片，再重跑本卡，不继续后面的对照。"
};
  window.ESEXPERIMENTS["ch19-06-bulk-s0"] = {
  "version": 1,
  "id": "ch19-06-bulk-s0",
  "title": "B4 · s0:apple×6 banana×3 cherry×2",
  "method": "POST",
  "path": "/_bulk?refresh=true",
  "body": "{\"index\":{\"_index\":\"tut-l19-s0\",\"_id\":\"1\"}}\n{\"fruit\":\"apple\",\"price\":1}\n{\"index\":{\"_index\":\"tut-l19-s0\",\"_id\":\"2\"}}\n{\"fruit\":\"apple\",\"price\":1}\n{\"index\":{\"_index\":\"tut-l19-s0\",\"_id\":\"3\"}}\n{\"fruit\":\"apple\",\"price\":1}\n{\"index\":{\"_index\":\"tut-l19-s0\",\"_id\":\"4\"}}\n{\"fruit\":\"apple\",\"price\":1}\n{\"index\":{\"_index\":\"tut-l19-s0\",\"_id\":\"5\"}}\n{\"fruit\":\"apple\",\"price\":1}\n{\"index\":{\"_index\":\"tut-l19-s0\",\"_id\":\"6\"}}\n{\"fruit\":\"apple\",\"price\":1}\n{\"index\":{\"_index\":\"tut-l19-s0\",\"_id\":\"7\"}}\n{\"fruit\":\"banana\",\"price\":1}\n{\"index\":{\"_index\":\"tut-l19-s0\",\"_id\":\"8\"}}\n{\"fruit\":\"banana\",\"price\":1}\n{\"index\":{\"_index\":\"tut-l19-s0\",\"_id\":\"9\"}}\n{\"fruit\":\"banana\",\"price\":1}\n{\"index\":{\"_index\":\"tut-l19-s0\",\"_id\":\"10\"}}\n{\"fruit\":\"cherry\",\"price\":1}\n{\"index\":{\"_index\":\"tut-l19-s0\",\"_id\":\"11\"}}\n{\"fruit\":\"cherry\",\"price\":1}\n",
  "predict": "shard 0 的本地词频表写好了吗?cherry 排第几?",
  "expect": "errors: false,11 项。apple:6、banana:3、cherry:2——cherry 本地第 3,这就是后面被挤掉的伏笔。 固定 ID 首次 created/201，重复写 updated/200，篇数不增加；确认 errors=false 后再搜索。refresh=true 只刷新本次触及分片，不改周期设置。"
};
  window.ESEXPERIMENTS["ch19-07-bulk-s1"] = {
  "version": 1,
  "id": "ch19-07-bulk-s1",
  "title": "B5 · s1:date×4 apple×4 cherry×3",
  "method": "POST",
  "path": "/_bulk?refresh=true",
  "body": "{\"index\":{\"_index\":\"tut-l19-s1\",\"_id\":\"1\"}}\n{\"fruit\":\"date\",\"price\":9}\n{\"index\":{\"_index\":\"tut-l19-s1\",\"_id\":\"2\"}}\n{\"fruit\":\"date\",\"price\":9}\n{\"index\":{\"_index\":\"tut-l19-s1\",\"_id\":\"3\"}}\n{\"fruit\":\"date\",\"price\":9}\n{\"index\":{\"_index\":\"tut-l19-s1\",\"_id\":\"4\"}}\n{\"fruit\":\"date\",\"price\":9}\n{\"index\":{\"_index\":\"tut-l19-s1\",\"_id\":\"5\"}}\n{\"fruit\":\"apple\",\"price\":9}\n{\"index\":{\"_index\":\"tut-l19-s1\",\"_id\":\"6\"}}\n{\"fruit\":\"apple\",\"price\":9}\n{\"index\":{\"_index\":\"tut-l19-s1\",\"_id\":\"7\"}}\n{\"fruit\":\"apple\",\"price\":9}\n{\"index\":{\"_index\":\"tut-l19-s1\",\"_id\":\"8\"}}\n{\"fruit\":\"apple\",\"price\":9}\n{\"index\":{\"_index\":\"tut-l19-s1\",\"_id\":\"9\"}}\n{\"fruit\":\"cherry\",\"price\":9}\n{\"index\":{\"_index\":\"tut-l19-s1\",\"_id\":\"10\"}}\n{\"fruit\":\"cherry\",\"price\":9}\n{\"index\":{\"_index\":\"tut-l19-s1\",\"_id\":\"11\"}}\n{\"fruit\":\"cherry\",\"price\":9}\n",
  "predict": "shard 1 的本地词频里 cherry 又排第几?",
  "expect": "errors: false,11 项。date:4、apple:4、cherry:3——cherry 又是本地第 3。两片都第 3,全局合计 5 却是第 2 名:动画步骤 2 的数字。 固定 ID 首次 created/201，重复写 updated/200，篇数不增加；确认 errors=false 后再搜索。refresh=true 只刷新本次触及分片，不改周期设置。"
};
  window.ESEXPERIMENTS["ch19-21-local-s0"] = {
  "version": 1,
  "id": "ch19-21-local-s0",
  "title": "B6 · 局部词频 · s0",
  "method": "POST",
  "path": "/tut-l19-s0/_search",
  "body": {
    "size": 0,
    "aggs": {
      "top": {
        "terms": {
          "field": "fruit",
          "size": 10
        }
      }
    }
  },
  "predict": "只搜一片时cherry是第几?",
  "expect": "桶为apple6/banana3/cherry2，共11篇，sum_other与误差均0；每个索引仅一个主分片。"
};
  window.ESEXPERIMENTS["ch19-22-local-s1"] = {
  "version": 1,
  "id": "ch19-22-local-s1",
  "title": "B7 · 局部词频 · s1",
  "method": "POST",
  "path": "/tut-l19-s1/_search",
  "body": {
    "size": 0,
    "aggs": {
      "top": {
        "terms": {
          "field": "fruit",
          "size": 10
        }
      }
    }
  },
  "predict": "只搜一片时cherry是第几?",
  "expect": "桶为apple4/date4/cherry3，共11篇，sum_other与误差均0；每个索引仅一个主分片。"
};
  window.ESEXPERIMENTS["ch19-08-true-global"] = {
  "version": 1,
  "id": "ch19-08-true-global",
  "title": "B8 · 先看真实全局(size 开大)",
  "method": "POST",
  "path": "/tut-l19-s0,tut-l19-s1/_search?filter_path=aggregations",
  "body": {
    "size": 0,
    "aggs": {
      "top": {
        "terms": {
          "field": "fruit",
          "size": 10
        }
      }
    }
  },
  "predict": "四个词的全局名次?cherry 应在第几?",
  "expect": "apple:10、cherry:5、date:4、banana:3。这是标准答案——接下来两个实验分别演示「送少了」和「默认过采样」。"
};
  window.ESEXPERIMENTS["ch19-09-shard-size-2"] = {
  "version": 1,
  "id": "ch19-09-shard-size-2",
  "title": "B9 · shard_size=2:cherry 被挤掉",
  "method": "POST",
  "path": "/tut-l19-s0,tut-l19-s1/_search?filter_path=aggregations",
  "body": {
    "size": 0,
    "aggs": {
      "top": {
        "terms": {
          "field": "fruit",
          "size": 2,
          "shard_size": 2,
          "show_term_doc_count_error": true
        }
      }
    }
  },
  "predict": "第二名是 cherry 还是 date?cherry 的计数 5 会出现在响应里吗?",
  "expect": "apple10、date4；sum_other=8（局部丢cherry共5，最终丢banana3）。聚合error_bound=7，桶内apple=0、date=3。本例date真实也是4，上界3不等于实际误差；cherry未成为候选。"
};
  window.ESEXPERIMENTS["ch19-10-default"] = {
  "version": 1,
  "id": "ch19-10-default",
  "title": "B10 · 默认启发式:shardSize=2×1.5+10=13",
  "method": "POST",
  "path": "/tut-l19-s0,tut-l19-s1/_search?filter_path=aggregations",
  "body": {
    "size": 0,
    "aggs": {
      "top": {
        "terms": {
          "field": "fruit",
          "size": 2,
          "show_term_doc_count_error": true
        }
      }
    }
  },
  "predict": "去掉 shard_size,第二名会换人吗?error_bound 呢?",
  "expect": "apple10、cherry5；本例默认容量13覆盖每片3值，聚合及桶误差上界0，sum_other=7（date4+banana3）。其他数据不保证默认容量足够。"
};
  window.ESEXPERIMENTS["ch19-11-size3-shard2"] = {
  "version": 1,
  "id": "ch19-11-size3-shard2",
  "title": "B11 · size=3 + shard_size=2:被抬回去",
  "method": "POST",
  "path": "/tut-l19-s0,tut-l19-s1/_search?filter_path=aggregations",
  "body": {
    "size": 0,
    "aggs": {
      "top": {
        "terms": {
          "field": "fruit",
          "size": 3,
          "shard_size": 2
        }
      }
    }
  },
  "predict": "shard_size=2 小于 size=3,ES 会照单全收地送 2 个吗?",
  "expect": "容量抬到3，返回apple10、cherry5、date4，sum_other=3。本例计数准确，聚合上界仍可为5（两片队列刚好满）；上界保守不等于已知实际误差，也不保证实际返回桶数至少size。"
};
  window.ESEXPERIMENTS["ch19-23-key-order"] = {
  "version": 1,
  "id": "ch19-23-key-order",
  "title": "B12 · _key排序，无count候选误差",
  "method": "POST",
  "path": "/tut-l19-s0,tut-l19-s1/_search",
  "body": {
    "size": 0,
    "aggs": {
      "top": {
        "terms": {
          "field": "fruit",
          "size": 2,
          "order": {
            "_key": "asc"
          },
          "show_term_doc_count_error": true
        }
      }
    }
  },
  "predict": "这次第二个key是cherry还是banana?",
  "expect": "apple10、banana3，误差上界0、sum_other9。按key不是按count；默认不套1.5+10，只把容量抬到size。仅论本课min_doc_count默认1的普通terms。"
};
  window.ESEXPERIMENTS["ch19-24-pipeline-small"] = {
  "version": 1,
  "id": "ch19-24-pipeline-small",
  "title": "B13 · terms size=2 后再 bucket_sort",
  "method": "POST",
  "path": "/tut-l19-s0,tut-l19-s1/_search",
  "body": {
    "size": 0,
    "aggs": {
      "top": {
        "terms": {
          "field": "fruit",
          "size": 2
        },
        "aggs": {
          "last_key": {
            "bucket_sort": {
              "sort": [
                {
                  "_key": {
                    "order": "desc"
                  }
                }
              ],
              "size": 1
            }
          }
        }
      }
    }
  },
  "predict": "bucket_sort会重新向分片要桶吗?",
  "expect": "只剩cherry5，sum_other仍为terms阶段的7；bucket_sort只重排普通terms保留下来的桶。与另一容量卡对照：请求局部参数不改字段/索引设置，pipeline不补丢失key。"
};
  window.ESEXPERIMENTS["ch19-25-pipeline-full"] = {
  "version": 1,
  "id": "ch19-25-pipeline-full",
  "title": "B14 · terms size=4 后再 bucket_sort",
  "method": "POST",
  "path": "/tut-l19-s0,tut-l19-s1/_search",
  "body": {
    "size": 0,
    "aggs": {
      "top": {
        "terms": {
          "field": "fruit",
          "size": 4
        },
        "aggs": {
          "last_key": {
            "bucket_sort": {
              "sort": [
                {
                  "_key": {
                    "order": "desc"
                  }
                }
              ],
              "size": 1
            }
          }
        }
      }
    }
  },
  "predict": "bucket_sort会重新向分片要桶吗?",
  "expect": "只剩date4，sum_other仍为terms阶段的0；bucket_sort只重排普通terms保留下来的桶。与另一容量卡对照：请求局部参数不改字段/索引设置，pipeline不补丢失key。"
};
  window.ESEXPERIMENTS["ch19-29-avg-merge"] = {
  "version": 1,
  "id": "ch19-29-avg-merge",
  "title": "B15 · avg合并sum/count，不平均局部均值",
  "method": "POST",
  "path": "/tut-l19-s0,tut-l19-s1/_search",
  "body": {
    "size": 0,
    "query": {
      "term": {
        "fruit": "apple"
      }
    },
    "aggs": {
      "price_avg": {
        "avg": {
          "field": "price"
        }
      },
      "price_sum": {
        "sum": {
          "field": "price"
        }
      },
      "price_count": {
        "value_count": {
          "field": "price"
        }
      }
    }
  },
  "predict": "s0六个price1，s1四个price9，全局均值是5还是4.2?",
  "expect": "price_sum=42、price_count=10、price_avg=4.2。InternalAvg携带sum/count，归并再除；(1+9)/2=5给分片等权，错误。这里每文档恰一数值，没有missing或多值。"
};
  window.ESEXPERIMENTS["ch19-12-setup-card"] = {
  "version": 1,
  "id": "ch19-12-setup-card",
  "title": "C1 · 建 tut-l19-card(user_id keyword)",
  "method": "PUT",
  "path": "/tut-l19-card",
  "body": {
    "settings": {
      "number_of_shards": 1,
      "number_of_replicas": 0,
      "auto_expand_replicas": "false",
      "refresh_interval": "-1",
      "requests.cache.enable": false,
      "default_pipeline": "_none",
      "final_pipeline": "_none",
      "mapping.source.mode": "stored"
    },
    "mappings": {
      "properties": {
        "user_id": {
          "type": "keyword"
        }
      },
      "dynamic": "strict",
      "date_detection": false,
      "numeric_detection": false
    }
  },
  "predict": "每篇文档一个不同 user_id,这叫什么?",
  "expect": "首次 200、acknowledged=true；重复创建 400 resource_already_exists_exception，原资源不重置。按本组健康等待再写入；数据不符时点名清理四索引，从 A1 重做。"
};
  window.ESEXPERIMENTS["ch19-26-wait-card"] = {
  "version": 1,
  "id": "ch19-26-wait-card",
  "title": "C2 · 等待本组主分片 green",
  "method": "GET",
  "path": "/_cluster/health/tut-l19-card?wait_for_status=green&wait_for_no_initializing_shards=true&timeout=30s",
  "body": null,
  "predict": "请求返回后能开始写入吗?",
  "expect": "status=green、timed_out=false、active_primary_shards=1。只等本组资源；超时先检查节点/分片，再重跑本卡，不继续后面的对照。"
};
  window.ESEXPERIMENTS["ch19-13-bulk-card"] = {
  "version": 1,
  "id": "ch19-13-bulk-card",
  "title": "C3 · 20 个唯一 user_id",
  "method": "POST",
  "path": "/_bulk?refresh=true",
  "body": "{\"index\":{\"_index\":\"tut-l19-card\",\"_id\":\"1\"}}\n{\"user_id\":\"u-1\"}\n{\"index\":{\"_index\":\"tut-l19-card\",\"_id\":\"2\"}}\n{\"user_id\":\"u-2\"}\n{\"index\":{\"_index\":\"tut-l19-card\",\"_id\":\"3\"}}\n{\"user_id\":\"u-3\"}\n{\"index\":{\"_index\":\"tut-l19-card\",\"_id\":\"4\"}}\n{\"user_id\":\"u-4\"}\n{\"index\":{\"_index\":\"tut-l19-card\",\"_id\":\"5\"}}\n{\"user_id\":\"u-5\"}\n{\"index\":{\"_index\":\"tut-l19-card\",\"_id\":\"6\"}}\n{\"user_id\":\"u-6\"}\n{\"index\":{\"_index\":\"tut-l19-card\",\"_id\":\"7\"}}\n{\"user_id\":\"u-7\"}\n{\"index\":{\"_index\":\"tut-l19-card\",\"_id\":\"8\"}}\n{\"user_id\":\"u-8\"}\n{\"index\":{\"_index\":\"tut-l19-card\",\"_id\":\"9\"}}\n{\"user_id\":\"u-9\"}\n{\"index\":{\"_index\":\"tut-l19-card\",\"_id\":\"10\"}}\n{\"user_id\":\"u-10\"}\n{\"index\":{\"_index\":\"tut-l19-card\",\"_id\":\"11\"}}\n{\"user_id\":\"u-11\"}\n{\"index\":{\"_index\":\"tut-l19-card\",\"_id\":\"12\"}}\n{\"user_id\":\"u-12\"}\n{\"index\":{\"_index\":\"tut-l19-card\",\"_id\":\"13\"}}\n{\"user_id\":\"u-13\"}\n{\"index\":{\"_index\":\"tut-l19-card\",\"_id\":\"14\"}}\n{\"user_id\":\"u-14\"}\n{\"index\":{\"_index\":\"tut-l19-card\",\"_id\":\"15\"}}\n{\"user_id\":\"u-15\"}\n{\"index\":{\"_index\":\"tut-l19-card\",\"_id\":\"16\"}}\n{\"user_id\":\"u-16\"}\n{\"index\":{\"_index\":\"tut-l19-card\",\"_id\":\"17\"}}\n{\"user_id\":\"u-17\"}\n{\"index\":{\"_index\":\"tut-l19-card\",\"_id\":\"18\"}}\n{\"user_id\":\"u-18\"}\n{\"index\":{\"_index\":\"tut-l19-card\",\"_id\":\"19\"}}\n{\"user_id\":\"u-19\"}\n{\"index\":{\"_index\":\"tut-l19-card\",\"_id\":\"20\"}}\n{\"user_id\":\"u-20\"}\n",
  "predict": "20篇、20个唯一值；terms size=2能证明只分配两个计数器吗?",
  "expect": "errors=false、20项。首次created/201，重复updated/200不增加篇数。逻辑基数20不是生产级内存压力测试；计数器布局需查执行策略，响应不直接暴露分配量。"
};
  window.ESEXPERIMENTS["ch19-14-card-terms"] = {
  "version": 1,
  "id": "ch19-14-card-terms",
  "title": "C4 · size=2 只回 2 桶,sum_other=18",
  "method": "POST",
  "path": "/tut-l19-card/_search?filter_path=aggregations",
  "body": {
    "size": 0,
    "aggs": {
      "users": {
        "terms": {
          "field": "user_id",
          "size": 2
        }
      }
    }
  },
  "predict": "只回两个桶，sum_other=18说明什么?这能测出字节分配量吗?",
  "expect": "u-1、u-10各1（同count按字典序），sum_other=18、误差上界0。18是未返回桶的计数总和，包含局部与最终截断；不是18个实际计数器或18篇内存对象的证明。"
};
  window.ESEXPERIMENTS["ch19-27-card-full"] = {
  "version": 1,
  "id": "ch19-27-card-full",
  "title": "C5 · 返回完整20个值作基数对照",
  "method": "POST",
  "path": "/tut-l19-card/_search",
  "body": {
    "size": 0,
    "aggs": {
      "users": {
        "terms": {
          "field": "user_id",
          "size": 20
        }
      }
    }
  },
  "predict": "sum_other会变成多少?",
  "expect": "20个桶各1、sum_other=0，逻辑基数20；与C4的2桶+18对照。此小样本不证明一百万值的内存消耗。"
};
  window.ESEXPERIMENTS["ch19-28-card-profile"] = {
  "version": 1,
  "id": "ch19-28-card-profile",
  "title": "C6 · profile观察实际选择的执行器",
  "method": "POST",
  "path": "/tut-l19-card/_search",
  "body": {
    "size": 0,
    "profile": true,
    "aggs": {
      "users": {
        "terms": {
          "field": "user_id",
          "size": 2
        }
      }
    }
  },
  "predict": "keyword一定使用同一个GlobalOrdinals执行器吗?",
  "expect": "聚合结果同C4；profile.shards[].aggregations可含StringTermsAggregatorFromFilters/FilterByFilter等适配路径，也可见序数实现。实际类型随条件选择；profile耗时不等于完整请求耗时，不能直接数计数器。"
};
  window.ESEXPERIMENTS["ch19-15-breakers"] = {
  "version": 1,
  "id": "ch19-15-breakers",
  "title": "C7 · 只看一眼 breaker 的名字和限额",
  "method": "GET",
  "path": "/_nodes/_local/stats/breaker?filter_path=nodes.*.name,nodes.*.breakers.request,nodes.*.breakers.parent,nodes.*.breakers.fielddata",
  "predict": "聚合的字节账记在哪个 breaker 上?现在 tripped 是几?",
  "expect": "本地节点的request/parent/fielddata限额、估计与累计tripped；历史或其他请求可使tripped非0，瞬时统计不能还原本次峰值。AggregatorBase固定初始估计5120B，不是最终内存；本课不调限额、不制造熔断。"
};
  window.ESEXPERIMENTS["ch19-16-cleanup"] = {
  "version": 1,
  "id": "ch19-16-cleanup",
  "title": "清理 · 点名删除本课四索引",
  "method": "DELETE",
  "path": "/tut-l19-shop,tut-l19-s0,tut-l19-s1,tut-l19-card",
  "predict": "一句话总结本课?",
  "expect": "首次200 acknowledged=true；全部不存在时重复DELETE为404 index_not_found_exception。会删除本课四索引全部文档；之后按A→B→C完整重做，每组先健康等待再bulk与查询。"
};
})();
