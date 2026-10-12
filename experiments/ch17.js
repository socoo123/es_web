/* experiments/ch17.js — 第 17 课:SearchService 与 SearchContext 实验 + 上下文生命周期动画(注册表) */
(function () {
  'use strict';

  /* ===== 动画:一个分片上的 SearchContext 一生 ===== */
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

  /* 步骤 1:ShardSearchRequest 到达数据节点 */
  function step1() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('ah17s1');
    s += rect(15, 25, 730, 60, 'fig-box');
    s += txt(380, 50, 'indices:data/read/search[phase/query]', 'fig-key');
    s += txt(380, 72, 'ShardSearchRequest:已经是「某一个 shard」的请求', 'fig-sub');
    s += line(380, 85, 380, 112, 'ah17s1');
    s += rect(230, 116, 300, 56, 'fig-box-hot', 'fp-pop');
    s += txt(380, 140, '数据节点 SearchService', 'fig-name');
    s += txt(380, 162, '普通索引调度到 search executor', 'fig-sub');
    s += txt(380, 205, 'public executeQueryPhase 返回 void + listener', 'fig-sub');
    s += txt(380, 227, '真正跑 Lucene 的是 private 重载,丢进 search 池', 'fig-sub');
    s += txt(380, 262, '可有改写 / can-match 捷径,不保证立即返回', 'fig-sub');
    return s + '</svg>';
  }

  /* 步骤 2:create 三步 */
  function step2() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('ah17s2');
    s += rect(15, 15, 355, 120, 'fig-box');
    s += txt(192, 40, 'createContext:先拿 Reader', 'fig-name');
    s += txt(192, 64, '1. ReaderContext 里取 Searcher', 'fig-sub');
    s += txt(192, 86, '2. parseSource:from/size/timeout', 'fig-sub');
    s += txt(192, 108, '3. 写入 originalQuery', 'fig-sub');
    s += line(371, 75, 389, 75, 'ah17s2');
    s += rect(390, 15, 355, 120, 'fig-box');
    s += txt(567, 40, 'preProcess:改 query', 'fig-name');
    s += txt(567, 64, '校验 from+size ≤ max_result_window', 'fig-sub');
    s += txt(567, 86, 'query = buildFilteredQuery(query)', 'fig-key');
    s += txt(567, 108, '按需:alias / nested / slice 进 FILTER', 'fig-sub');
    s += rect(15, 150, 730, 60, 'fig-box-hot', 'fp-pop');
    s += txt(380, 174, 'SearchContext 装好这一趟搜索的全部状态', 'fig-name');
    s += txt(380, 196, '查询、from/size、timeout、这一趟的 TopDocs', 'fig-sub');
    s += txt(380, 244, '套在 try-with-resources 里:进出即 close', 'fig-sub');
    s += txt(380, 266, '任一步抛错都先 close 再往外抛,不漏 searcher', 'fig-sub');
    return s + '</svg>';
  }

  /* 步骤 3:三个查询字段 */
  function step3() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('ah17s3');
    s += rect(180, 15, 400, 52, 'fig-box');
    s += txt(380, 38, 'originalQuery · ParsedQuery', 'fig-name');
    s += txt(380, 58, '用户查询,不含 alias 过滤(highlight 要用)', 'fig-sub');
    s += line(380, 67, 380, 80, 'ah17s3');
    s += rect(180, 84, 400, 52, 'fig-box');
    s += txt(380, 107, 'query(未 rewrite)', 'fig-name');
    s += txt(380, 127, 'preProcess 按需补 FILTER 的执行查询', 'fig-sub');
    s += line(380, 136, 380, 149, 'ah17s3');
    s += rect(180, 153, 400, 52, 'fig-box-hot', 'fp-pop');
    s += txt(380, 176, 'rewrittenQuery()', 'fig-name');
    s += txt(380, 196, 'searcher.rewrite:按查询实现继续改写', 'fig-sub');
    s += rect(15, 225, 730, 56, 'fig-box');
    s += txt(380, 248, 'match "quick brown" → SHOULD quick + SHOULD brown', 'fig-key');
    s += txt(380, 270, '分词发生在 toQuery;Lucene rewrite 是另一步,别并成一个', 'fig-sub');
    return s + '</svg>';
  }

  /* 步骤 4:QueryPhase 执行 */
  function step4() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('ah17s4');
    s += rect(15, 20, 730, 56, 'fig-box');
    s += txt(380, 44, 'QueryPhase.execute(context) — static', 'fig-key');
    s += txt(380, 66, '聚合在收集阶段参与;随后 rescore / suggest', 'fig-sub');
    s += rect(205, 100, 350, 64, 'fig-box-hot', 'fp-pop');
    s += txt(380, 124, 'searcher.search(query, collector)', 'fig-name');
    s += txt(380, 146, 'query 取自 rewrittenQuery()', 'fig-sub');
    s += rect(15, 178, 355, 70, 'fig-box');
    s += txt(192, 202, 'loadOrExecuteQueryPhase', 'fig-name');
    s += txt(192, 224, 'canCache 且缓存命中 → 填结果', 'fig-sub');
    s += txt(192, 244, '命中跳过 QueryPhase;未命中仍查询', 'fig-sub');
    s += rect(390, 178, 355, 70, 'fig-box');
    s += txt(567, 202, '超时检查点', 'fig-name');
    s += txt(567, 224, 'getTimeoutCheck 挂 cancellation', 'fig-sub');
    s += txt(567, 244, '收集过程中看相对时钟', 'fig-sub');
    s += txt(380, 274, '返回候选 / sort / 聚合等;不含完整 _source', 'fig-sub');
    return s + '</svg>';
  }

  /* 步骤 5:两种返回 + 单分片捷径 */
  function step5() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('ah17s5');
    s += rect(15, 20, 355, 110, 'fig-box');
    s += txt(192, 44, '多分片(默认)', 'fig-name');
    s += txt(192, 68, 'QuerySearchResult', 'fig-key');
    s += txt(192, 90, 'docId + score + 聚合', 'fig-sub');
    s += txt(192, 112, '_source 留给 Fetch 阶段', 'fig-sub');
    s += rect(390, 20, 355, 110, 'fig-box-hot', 'fp-pop');
    s += txt(567, 44, '单分片(优化)', 'fig-name');
    s += txt(567, 68, 'QueryFetchSearchResult', 'fig-key');
    s += txt(567, 90, '同一份 SearchContext 顺手 Fetch', 'fig-sub');
    s += txt(567, 112, '可合并 Query 与 Fetch 调用', 'fig-sub');
    s += rect(15, 148, 730, 70, 'fig-box');
    s += txt(380, 172, '单目标分片且无 rankBuilder · 普通 QTF', 'fig-key');
    s += txt(380, 194, '这是 SearchService 的优化路径,不是一种 SearchType', 'fig-sub');
    s += txt(380, 214, 'SearchType.QUERY_AND_FETCH 枚举已删,别去 search_type 找它', 'fig-sub');
    s += txt(380, 254, 'listener 在 private 调用 return 之后才收到值', 'fig-sub');
    return s + '</svg>';
  }

  /* 步骤 6:close 与 ReaderContext */
  function step6() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('ah17s6');
    s += rect(15, 20, 730, 56, 'fig-box');
    s += txt(380, 44, 'try-with-resources 出口:SearchContext.close()', 'fig-name');
    s += txt(380, 66, 'closeFuture.onResponse → 释放这一趟的 searcher 视图', 'fig-sub');
    s += rect(15, 100, 355, 110, 'fig-box');
    s += txt(192, 124, '普通搜索', 'fig-name');
    s += txt(192, 148, 'ReaderContext singleSession=true', 'fig-sub');
    s += txt(192, 170, '没有 hits 要 Fetch 时', 'fig-sub');
    s += txt(192, 192, 'Query 相位里就 freeReaderContext', 'fig-sub');
    s += rect(390, 100, 355, 110, 'fig-box');
    s += txt(567, 124, 'PIT / Scroll', 'fig-name');
    s += txt(567, 148, 'ReaderContext 活在 activeReaders', 'fig-sub');
    s += txt(567, 170, 'markAsUsed(keepAlive) 续命', 'fig-sub');
    s += txt(567, 192, '显式关闭 / 过期清理;索引删除也会清理', 'fig-sub');
    s += rect(15, 228, 730, 54, 'fig-box-hot', 'fp-pop');
    s += txt(380, 250, 'close 的是 SearchContext,不是 PIT Reader', 'fig-name');
    s += txt(380, 272, '两个 Context 别当一个:一个活一趟,一个跨请求', 'fig-sub');
    return s + '</svg>';
  }

  window.ESFLOWS = window.ESFLOWS || {};
  window.ESFLOWS['ch17-context-lifecycle'] = {
    version: 1,
    id: 'ch17-context-lifecycle',
    title: '一个分片上的 SearchContext 一生',
    speed: 2200,
    steps: [
      { svg: step1(), note: '数据节点收到 phase/query。Transport handler 那条 executeQueryPhase 签名是 void + ActionListener:通常改写后提交到 executor;can-match 可提前回空结果。执行分支在 private 重载完成并关闭 context 后回调。' },
      { svg: step2(), note: 'createContext 三步:从 ReaderContext 拿 Searcher、parseSource 写 from/size/timeout 与 originalQuery、preProcess 校验窗口并改写 query 字段。整个生命周期套在 try-with-resources 上,任一步抛错都先 close 再往外抛。' },
      { svg: step3(), note: '三个查询字段:originalQuery 是用户的 ParsedQuery(默认高亮使用);query 在 preProcess 里按需补 alias/nested/slice FILTER,但尚未 Lucene rewrite;rewrittenQuery() 才是 searcher.rewrite 之后真正执行的那份。' },
      { svg: step4(), note: 'QueryPhase.execute 是 static:searcher.search(rewrittenQuery(), collector)。可缓存且命中才跳过 QueryPhase;缓存未命中仍执行;超时检查点挂成 cancellation,在收集过程中看相对时钟——不是墙上时钟一到就杀线程。' },
      { svg: step5(), note: '多分片:回 QuerySearchResult,可含候选、sort 值、聚合等,_source 留给第 16 课的 Fetch 阶段。普通 QTF 单目标分片且无 rankBuilder:同一份 SearchContext 里顺手 executeFetchPhase——这是优化路径,不是一种 SearchType。' },
      { svg: step6(), note: 'close 释放本次 context 持有的资源(释放 searcher 视图)。跨请求保活的是 ReaderContext:PIT/Scroll 活在 activeReaders 里靠 keep-alive 续命,显式关闭 / 过期清理;索引删除也会清理;普通搜索 singleSession,Query 相位就可能 freeReaderContext。' }
    ]
  };

  function timeoutBulk() {
    var rows = [];
    for (var n = 10; n < 3010; n++) {
      rows.push(JSON.stringify({ index: { _index: "tut-l17-timeout", _id: String(n) } }));
      rows.push(JSON.stringify({ title: "doc " + n, n: n }));
    }
    return rows.join("\n") + "\n";
  }

  /* ===== 实验：A 查询证据 / B 超时 / C PIT / 点名清理 ===== */
  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};
  window.ESEXPERIMENTS["ch17-00-setup"] = {
  "version": 1,
  "id": "ch17-00-setup",
  "title": "A1 · 建超时与查询索引",
  "method": "PUT",
  "path": "/tut-l17-timeout",
  "body": {
    "settings": {
      "number_of_shards": 1,
      "number_of_replicas": 0,
      "auto_expand_replicas": "false",
      "refresh_interval": "-1",
      "default_pipeline": "_none",
      "final_pipeline": "_none",
      "requests.cache.enable": false
    },
    "mappings": {
      "dynamic": "strict",
      "_source": {
        "enabled": true
      },
      "properties": {
        "title": {
          "type": "text",
          "analyzer": "standard"
        },
        "n": {
          "type": "integer"
        }
      }
    }
  },
  "predict": "固定一主零副、显式 mapping，能否排除所有耗时变量？",
  "expect": "acknowledged=true。固定分片与字段，仍受 JIT、负载、段与检查粒度影响。重复建同名索引返回400；重做先执行末尾两条清理。"
};
  window.ESEXPERIMENTS["ch17-18-health-timeout"] = {
  "version": 1,
  "id": "ch17-18-health-timeout",
  "title": "A2 · 等本章索引可用",
  "method": "GET",
  "path": "/_cluster/health/tut-l17-timeout?wait_for_status=green&wait_for_active_shards=1&timeout=10s",
  "body": null,
  "predict": "单节点一主零副应达到什么状态？",
  "expect": "status=green、timed_out=false、active_primary_shards=1。超时则先解决分片就绪问题。"
};
  window.ESEXPERIMENTS["ch17-19-settings"] = {
  "version": 1,
  "id": "ch17-19-settings",
  "title": "A3 · 读回显式设置",
  "method": "GET",
  "path": "/tut-l17-timeout/_settings?flat_settings=true",
  "body": null,
  "predict": "refresh=-1 与 request cache 关闭能保证相同耗时吗？",
  "expect": "index.refresh_interval=-1、index.requests.cache.enable=false、1主0副。-1只关闭周期刷新；本章写入显式 refresh。设置不消除机器负载差异。"
};
  window.ESEXPERIMENTS["ch17-01-bulk3"] = {
  "version": 1,
  "id": "ch17-01-bulk3",
  "title": "A4 · 写三篇并显式刷新",
  "method": "POST",
  "path": "/tut-l17-timeout/_bulk?refresh=true",
  "body": "{\"index\":{\"_index\":\"tut-l17-timeout\",\"_id\":\"1\"}}\n{\"title\":\"quick brown fox\",\"n\":1}\n{\"index\":{\"_index\":\"tut-l17-timeout\",\"_id\":\"2\"}}\n{\"title\":\"lazy dog\",\"n\":2}\n{\"index\":{\"_index\":\"tut-l17-timeout\",\"_id\":\"3\"}}\n{\"title\":\"quick brown\",\"n\":3}\n",
  "predict": "3 篇、match_all、timeout=1ms:下一个实验里 timed_out 更可能是 true 还是 false?",
  "expect": "errors=false、3项created/201；同组重复写是updated/200，仍为3篇。此处显式刷新，后续立即可搜；不要依赖周期刷新或手速。"
};
  window.ESEXPERIMENTS["ch17-20-analyze"] = {
  "version": 1,
  "id": "ch17-20-analyze",
  "title": "A5 · 用字段分析链观察分词",
  "method": "POST",
  "path": "/tut-l17-timeout/_analyze",
  "body": {
    "field": "title",
    "text": "quick brown"
  },
  "predict": "standard 对这两个词产生几个 token？",
  "expect": "两个 token：quick、brown。此请求证明分析结果；不直接暴露 SearchContext 私有字段。"
};
  window.ESEXPERIMENTS["ch17-21-validate"] = {
  "version": 1,
  "id": "ch17-21-validate",
  "title": "A6 · 看 match 的 Lucene 查询表示",
  "method": "POST",
  "path": "/tut-l17-timeout/_validate/query?rewrite=true&explain=true",
  "body": {
    "query": {
      "match": {
        "title": "quick brown"
      }
    }
  },
  "predict": "SHOULD 两个词是否要等 Lucene rewrite 才产生？",
  "expect": "valid=true，explanation含title:quick、title:brown。标准分析器、默认OR在 QueryBuilder.toQuery 阶段形成词查询；此接口显示改写后的表示，不能单凭响应重建全部中间态。"
};
  window.ESEXPERIMENTS["ch17-22-alias"] = {
  "version": 1,
  "id": "ch17-22-alias",
  "title": "A7 · 建只含 n=1 的过滤别名",
  "method": "POST",
  "path": "/_aliases",
  "body": {
    "actions": [
      {
        "add": {
          "index": "tut-l17-timeout",
          "alias": "tut-l17-filtered",
          "filter": {
            "term": {
              "n": 1
            }
          }
        }
      }
    ]
  },
  "predict": "原索引 quick 的两篇，别名会保留几篇？",
  "expect": "acknowledged=true。别名过滤按搜索路径生效；不当作直接按ID访问的权限边界。别名随本索引点名删除。"
};
  window.ESEXPERIMENTS["ch17-23-alias-profile"] = {
  "version": 1,
  "id": "ch17-23-alias-profile",
  "title": "A8 · 过滤、Profile、Explain 与高亮",
  "method": "POST",
  "path": "/tut-l17-filtered/_search?request_cache=false",
  "body": {
    "query": {
      "match": {
        "title": "quick brown"
      }
    },
    "profile": true,
    "explain": true,
    "highlight": {
      "fields": {
        "title": {}
      }
    },
    "size": 10
  },
  "predict": "Profile/Explain 是否都只看 originalQuery？",
  "expect": "hits仅_id=1；高亮quick/brown。profile查询树含过滤查询，_explanation来自rewrittenQuery，不能把二者都归originalQuery。默认高亮从parsedQuery取查询，但不保证反映完整布尔匹配逻辑。"
};
  window.ESEXPERIMENTS["ch17-02-timeout-fast"] = {
  "version": 1,
  "id": "ch17-02-timeout-fast",
  "title": "B1 · 快查询的1ms观察",
  "method": "POST",
  "path": "/tut-l17-timeout/_search?request_cache=false&allow_partial_search_results=true",
  "body": {
    "timeout": "1ms",
    "track_total_hits": true,
    "query": {
      "match_all": {}
    }
  },
  "predict": "相同1ms每次都超时吗？",
  "expect": "常见200、timed_out=false、total=3，本轮两次均如此；负载变化也可能超时。检查可在叶子开始等位置执行，并非“小数据一定一次检查都没有”。不是全请求1ms截止线。"
};
  window.ESEXPERIMENTS["ch17-03-bulk30"] = {
  "version": 1,
  "id": "ch17-03-bulk30",
  "title": "B2 · 固定ID增加3000篇",
  "method": "POST",
  "path": "/tut-l17-timeout/_bulk?refresh=true",
  "body": timeoutBulk(),
  "predict": "这次写入和上一个实验的 3 篇在同一个索引里,总共有几篇?给下一个实验的忙循环备了多少个命中?",
  "expect": "errors=false，首次3000项created/201；重复3000项updated/200。与A组3篇合计3003篇。不要把增量写入次数当作文档数。"
};
  window.ESEXPERIMENTS["ch17-28-count"] = {
  "version": 1,
  "id": "ch17-28-count",
  "title": "B3 · 读回3003篇基线",
  "method": "GET",
  "path": "/tut-l17-timeout/_count",
  "body": null,
  "predict": "这些固定ID重复写会让总数变6006吗？",
  "expect": "count=3003；重复写相同ID是覆盖。若不是3003，先点名清理，再从A1完整重做。"
};
  window.ESEXPERIMENTS["ch17-30-loop-guard"] = {
  "version": 1,
  "id": "ch17-30-loop-guard",
  "title": "B4 · 原忙循环先撞脚本限制",
  "method": "POST",
  "path": "/tut-l17-timeout/_search?request_cache=false",
  "body": {
    "query": {
      "script_score": {
        "query": {
          "match_all": {}
        },
        "script": {
          "source": "long acc = 0L; for (int i = 0; i < 5000000; i++) { acc += i; } return 1.0;"
        }
      }
    }
  },
  "predict": "500万次循环是查询超时，还是脚本保护错误？",
  "expect": "预期400：顶层search_phase_execution_exception，内层script_exception/painless_error，reason含maximum number of statements。这是脚本限制，不是timed_out或429；下一步换有界脚本，无需改集群设置。"
};
  window.ESEXPERIMENTS["ch17-29-work-baseline"] = {
  "version": 1,
  "id": "ch17-29-work-baseline",
  "title": "B5 · 无短超时验证有界工作负载",
  "method": "POST",
  "path": "/tut-l17-timeout/_search?request_cache=false",
  "body": {
    "timeout": "30s",
    "size": 10,
    "track_total_hits": true,
    "query": {
      "script_score": {
        "query": {
          "match_all": {}
        },
        "script": {
          "source": "double acc = 0.0; double n = doc[\"n\"].value; for (int i = 0; i < params.loops; i++) { acc += Math.log(1.0 + n + i); } return acc / params.loops;",
          "params": {
            "loops": 20000
          }
        }
      }
    }
  },
  "predict": "两万次有界计算能否先完整返回？",
  "expect": "200、timed_out=false、total=3003；脚本结果使用acc，循环远小于旧负载。先证明脚本合法，再比较短超时；不把失败脚本当慢查询证据。"
};
  window.ESEXPERIMENTS["ch17-04-timeout-slow"] = {
  "version": 1,
  "id": "ch17-04-timeout-slow",
  "title": "B6 · 有界负载允许部分结果",
  "method": "POST",
  "path": "/tut-l17-timeout/_search?request_cache=false&allow_partial_search_results=true",
  "body": {
    "timeout": "1ms",
    "size": 10,
    "track_total_hits": true,
    "query": {
      "script_score": {
        "query": {
          "match_all": {}
        },
        "script": {
          "source": "double acc = 0.0; double n = doc[\"n\"].value; for (int i = 0; i < params.loops; i++) { acc += Math.log(1.0 + n + i); } return acc / params.loops;",
          "params": {
            "loops": 20000
          }
        }
      }
    }
  },
  "predict": "相同合法脚本加1ms，会怎样收束？",
  "expect": "本轮200、timed_out=true；hits/total可为部分结果，不能当全集。此观察受负载与检查粒度影响；若false，记录实际值、对比B5，不无限扩大单次循环，不保证每台机器触发。"
};
  window.ESEXPERIMENTS["ch17-05-timeout-strict"] = {
  "version": 1,
  "id": "ch17-05-timeout-strict",
  "title": "B7 · 同一负载禁止部分结果",
  "method": "POST",
  "path": "/tut-l17-timeout/_search?request_cache=false&allow_partial_search_results=false",
  "body": {
    "timeout": "1ms",
    "size": 10,
    "track_total_hits": true,
    "query": {
      "script_score": {
        "query": {
          "match_all": {}
        },
        "script": {
          "source": "double acc = 0.0; double n = doc[\"n\"].value; for (int i = 0; i < params.loops; i++) { acc += Math.log(1.0 + n + i); } return acc / params.loops;",
          "params": {
            "loops": 20000
          }
        }
      }
    }
  },
  "predict": "若查询超时，HTTP和错误类型是什么？",
  "expect": "本轮429：顶层search_phase_execution_exception/all shards failed，内层search_timeout_exception/Time exceeded。若负载未跨过检查点可正常200；400脚本错误不能冒充超时。两卡仅部分结果开关不同。"
};
  window.ESEXPERIMENTS["ch17-06-setup-pit"] = {
  "version": 1,
  "id": "ch17-06-setup-pit",
  "title": "C1 · 建PIT索引",
  "method": "PUT",
  "path": "/tut-l17-pit",
  "body": {
    "settings": {
      "number_of_shards": 1,
      "number_of_replicas": 0,
      "auto_expand_replicas": "false",
      "refresh_interval": "-1",
      "default_pipeline": "_none",
      "final_pipeline": "_none",
      "requests.cache.enable": false
    },
    "mappings": {
      "dynamic": "strict",
      "_source": {
        "enabled": true
      },
      "properties": {
        "title": {
          "type": "text",
          "analyzer": "standard"
        },
        "ts": {
          "type": "integer"
        }
      }
    }
  },
  "predict": "PIT 钉住的是哪个对象的视图?",
  "expect": "acknowledged=true。显式standard文本与整数ts，1主0副。重复建索引400；先清理重建，避免new已进入即将打开的PIT。"
};
  window.ESEXPERIMENTS["ch17-24-health-pit"] = {
  "version": 1,
  "id": "ch17-24-health-pit",
  "title": "C2 · 等PIT索引就绪",
  "method": "GET",
  "path": "/_cluster/health/tut-l17-pit?wait_for_status=green&wait_for_active_shards=1&timeout=10s",
  "body": null,
  "predict": "这个实验需要几份分片视图？",
  "expect": "green、timed_out=false、active_primary_shards=1。本课单分片PIT，不能据此推断多分片全局事务快照。"
};
  window.ESEXPERIMENTS["ch17-07-bulk5"] = {
  "version": 1,
  "id": "ch17-07-bulk5",
  "title": "C3 · 固定五篇并刷新",
  "method": "POST",
  "path": "/tut-l17-pit/_bulk?refresh=true",
  "body": "{\"index\":{\"_index\":\"tut-l17-pit\",\"_id\":\"1\"}}\n{\"title\":\"quick brown fox\",\"ts\":1}\n{\"index\":{\"_index\":\"tut-l17-pit\",\"_id\":\"2\"}}\n{\"title\":\"quick brown\",\"ts\":2}\n{\"index\":{\"_index\":\"tut-l17-pit\",\"_id\":\"3\"}}\n{\"title\":\"lazy dog\",\"ts\":3}\n{\"index\":{\"_index\":\"tut-l17-pit\",\"_id\":\"4\"}}\n{\"title\":\"quick fox\",\"ts\":4}\n{\"index\":{\"_index\":\"tut-l17-pit\",\"_id\":\"5\"}}\n{\"title\":\"brown fox\",\"ts\":5}\n",
  "predict": "title 里含 quick 的有几篇?",
  "expect": "errors=false；首次5项201，重复200。quick在1/2/4，ts为1/2/4。重做先删索引，以免旧new使初始快照变4篇。"
};
  window.ESEXPERIMENTS["ch17-25-context-baseline"] = {
  "version": 1,
  "id": "ch17-25-context-baseline",
  "title": "C4 · 记录本索引上下文基线N",
  "method": "GET",
  "path": "/tut-l17-pit/_stats/search?filter_path=indices.*.primaries.search.open_contexts",
  "body": null,
  "predict": "其他索引开的PIT会影响这个统计吗？",
  "expect": "记录本索引primaries.search.open_contexts=N，干净重建通常0。统计限定本章索引；同索引其他并发读者仍会影响，后续比较N+1→N。"
};
  window.ESEXPERIMENTS["ch17-08-pit-open"] = {
  "version": 1,
  "id": "ch17-08-pit-open",
  "title": "C5 · 打开PIT并复制id",
  "method": "POST",
  "path": "/tut-l17-pit/_pit?keep_alive=5m",
  "predict": "openReaderContext 之后,这个 id 代表什么?它自己会过期吗?",
  "expect": "返回id及_shards，本例1片成功。复制id到C7请求的pit.id；后续每次搜索都取最新pit_id。keep_alive只需覆盖下次操作，不必覆盖整个分页；过期后从C1重建前提，不能直接重开并沿用旧sort。"
};
  window.ESEXPERIMENTS["ch17-09-contexts-open"] = {
  "version": 1,
  "id": "ch17-09-contexts-open",
  "title": "C6 · 本索引上下文N+1",
  "method": "GET",
  "path": "/tut-l17-pit/_stats/search?filter_path=indices.*.primaries.search.open_contexts",
  "predict": "刚开了一个 PIT,open_contexts 是多少?",
  "expect": "本索引open_contexts=N+1，本轮0→1。ReaderContext保留读者引用；不是缓存命中数，也不等于独占一整份物理IndexReader。"
};
  window.ESEXPERIMENTS["ch17-10-pit-page1"] = {
  "version": 1,
  "id": "ch17-10-pit-page1",
  "title": "C7 · 第一页与完整sort",
  "method": "POST",
  "path": "/_search",
  "body": {
    "size": 2,
    "track_total_hits": true,
    "sort": [
      {
        "ts": "asc"
      }
    ],
    "query": {
      "match": {
        "title": "quick"
      }
    },
    "pit": {
      "id": "粘贴C5的id，之后使用最新pit_id",
      "keep_alive": "5m"
    }
  },
  "predict": "hits 是哪两篇?sort 值是多少,拿去干什么用?",
  "expect": "_id=1、2、total=3。响应pit_id必须保留；末项sort含ts和隐式_shard_doc，本轮[2,1]。将整个数组作为C9的search_after，不手造文档号。PIT请求不在路径写索引。"
};
  window.ESEXPERIMENTS["ch17-11-write-new"] = {
  "version": 1,
  "id": "ch17-11-write-new",
  "title": "C8 · 旧PIT打开时写new并刷新",
  "method": "PUT",
  "path": "/tut-l17-pit/_doc/new?refresh=true",
  "body": {
    "title": "quick newcomer",
    "ts": 99
  },
  "predict": "refresh=true 已经把新文档编进 segment:同一个 PIT 还能看见它吗?普通搜索呢?",
  "expect": "首次created/201，同组重复updated/200。refresh=true使普通搜索当前视图看到new；旧PIT引用仍不包含new。刷新不是把新数据追加进已开的PIT。"
};
  window.ESEXPERIMENTS["ch17-26-pit-page2"] = {
  "version": 1,
  "id": "ch17-26-pit-page2",
  "title": "C9 · 传完整sort取第二页",
  "method": "POST",
  "path": "/_search",
  "body": {
    "size": 2,
    "track_total_hits": true,
    "sort": [
      {
        "ts": "asc"
      }
    ],
    "query": {
      "match": {
        "title": "quick"
      }
    },
    "pit": {
      "id": "粘贴C5的id，之后使用最新pit_id",
      "keep_alive": "5m"
    },
    "search_after": [
      "粘贴C7末项sort[0]",
      "粘贴C7末项sort[1]"
    ]
  },
  "predict": "刷新后旧PIT第二页能否出现new？",
  "expect": "改pit.id为C7最新pit_id，search_after替换为完整数字数组。本轮用[2,1]返回仅_id=4、total=3；返回pit_id继续传给后续卡。保持query/sort，from默认0；不包含new。"
};
  window.ESEXPERIMENTS["ch17-12-pit-again"] = {
  "version": 1,
  "id": "ch17-12-pit-again",
  "title": "C10 · 旧PIT重搜仍是3篇",
  "method": "POST",
  "path": "/_search",
  "body": {
    "size": 20,
    "track_total_hits": true,
    "sort": [
      {
        "ts": "asc"
      }
    ],
    "query": {
      "match": {
        "title": "quick"
      }
    },
    "pit": {
      "id": "粘贴C5的id，之后使用最新pit_id",
      "keep_alive": "5m"
    }
  },
  "predict": "PIT 搜索的 hits 里有没有 new?total 是多少?",
  "expect": "使用C9最新pit_id，无search_after；_id=1/2/4、total=3，无new。响应pit_id继续保存。查询重新执行，PIT保留的是视图而非结果缓存。"
};
  window.ESEXPERIMENTS["ch17-31-pit-other-query"] = {
  "version": 1,
  "id": "ch17-31-pit-other-query",
  "title": "C11 · 同一视图换查询",
  "method": "POST",
  "path": "/_search",
  "body": {
    "size": 20,
    "track_total_hits": true,
    "sort": [
      {
        "ts": "asc"
      }
    ],
    "query": {
      "match": {
        "title": "lazy"
      }
    },
    "pit": {
      "id": "粘贴C5的id，之后使用最新pit_id",
      "keep_alive": "5m"
    }
  },
  "predict": "PIT若只是缓存quick结果，换lazy会怎样？",
  "expect": "使用最新pit_id，返回仅_id=3、total=1。查询可变但仍读旧视图，证明PIT不是结果缓存；这张卡是新查询，不是沿用quick的分页游标。保存最新pit_id用于关闭。"
};
  window.ESEXPERIMENTS["ch17-13-no-pit"] = {
  "version": 1,
  "id": "ch17-13-no-pit",
  "title": "C12 · 普通搜索当前4篇",
  "method": "POST",
  "path": "/tut-l17-pit/_search",
  "body": {
    "size": 20,
    "track_total_hits": true,
    "sort": [
      {
        "ts": "asc"
      }
    ],
    "query": {
      "match": {
        "title": "quick"
      }
    }
  },
  "predict": "普通搜索能看到 new 吗?total 比实验 12 多几?",
  "expect": "_id=1/2/4/new、total=4；旧PIT仍3。普通搜索也有临时ReaderContext/SearchContext，只是没有这个跨请求保留的PIT。"
};
  window.ESEXPERIMENTS["ch17-14-pit-close"] = {
  "version": 1,
  "id": "ch17-14-pit-close",
  "title": "C13 · 用最新pit_id关闭",
  "method": "DELETE",
  "path": "/_pit",
  "body": {
    "id": "粘贴C11最新返回的pit_id"
  },
  "predict": "DELETE /_pit 成功后,那份 IndexReader 什么时候真正释放?",
  "expect": "本轮succeeded=true、num_freed=1。保存这个ID供C15验证。解除PIT引用；若其他请求/reader仍持引用，底层资源不保证此刻全部释放。重复关闭可能num_freed=0，不等于释放了两次。"
};
  window.ESEXPERIMENTS["ch17-15-contexts-closed"] = {
  "version": 1,
  "id": "ch17-15-contexts-closed",
  "title": "C14 · 上下文回基线N",
  "method": "GET",
  "path": "/tut-l17-pit/_stats/search?filter_path=indices.*.primaries.search.open_contexts",
  "predict": "现在是多少?如果忘了关,靠什么兜底?",
  "expect": "open_contexts回N，本轮1→0。keep_alive过期由后台reaper检查清理，不是墙上时钟一到立即销毁；本例显式关闭且无并发操作。"
};
  window.ESEXPERIMENTS["ch17-27-closed-pit"] = {
  "version": 1,
  "id": "ch17-27-closed-pit",
  "title": "C15 · 关闭后的ID不能继续分页",
  "method": "POST",
  "path": "/_search",
  "body": {
    "size": 2,
    "track_total_hits": true,
    "sort": [
      {
        "ts": "asc"
      }
    ],
    "query": {
      "match": {
        "title": "quick"
      }
    },
    "pit": {
      "id": "粘贴C13关闭的pit_id",
      "keep_alive": "5m"
    }
  },
  "predict": "显式关闭后仍能搜同一快照吗？",
  "expect": "本轮404：顶层search_phase_execution_exception，root_cause是search_context_missing_exception。恢复须重建/重新开PIT并从第一页开始；新PIT可能包含new，不能假装接上旧快照。"
};
  window.ESEXPERIMENTS["ch17-16-cleanup-timeout"] = {
  "version": 1,
  "id": "ch17-16-cleanup-timeout",
  "title": "清理1 · 点名删除超时索引",
  "method": "DELETE",
  "path": "/tut-l17-timeout",
  "predict": "这个索引里有实验 4 制造的部分结果残留吗?",
  "expect": "acknowledged=true；同时删除附属tut-l17-filtered别名。仅删本章资源，重复DELETE已不存在索引404；搜索部分结果不会写回索引。"
};
  window.ESEXPERIMENTS["ch17-17-cleanup-pit"] = {
  "version": 1,
  "id": "ch17-17-cleanup-pit",
  "title": "清理2 · 点名删除PIT索引",
  "method": "DELETE",
  "path": "/tut-l17-pit",
  "predict": "实验 14 已经关了 PIT,直接删索引还有障碍吗?",
  "expect": "acknowledged=true。先用最新ID关闭PIT再点名删索引。完整重做从A1开始；不要只覆写五篇便重开PIT，new会污染初始条件。重复DELETE返回404。"
};
})();
