/* experiments/ch18.js — 第 18 课:查询语法实验 + match→SHOULD 翻译动画(注册表) */
(function () {
  'use strict';

  /* ===== 动画:一句 match 的翻译之旅 ===== */
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

  /* 步骤 1:JSON → MatchQueryBuilder */
  function step1() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('ah18s1');
    s += rect(15, 25, 730, 56, 'fig-box');
    s += txt(380, 48, '{"match":{"title":"quick brown"}}', 'fig-key');
    s += txt(380, 70, '客户端 JSON', 'fig-sub');
    s += line(380, 81, 380, 105, 'ah18s1');
    s += rect(230, 109, 300, 52, 'fig-box', 'fp-pop');
    s += txt(380, 131, 'MatchQueryBuilder', 'fig-name');
    s += txt(380, 153, 'fromXContent 解析出 Builder', 'fig-sub');
    s += txt(380, 196, 'REST 解析发生在协调节点,真正翻译在数据节点', 'fig-sub');
    s += txt(380, 218, 'SearchExecutionContext.toQuery 就是这一跳', 'fig-sub');
    s += txt(380, 252, '翻译完的 Lucene Query 写进 originalQuery(第 17 课)', 'fig-sub');
    return s + '</svg>';
  }

  /* 步骤 2:doToQuery 与 keyword 短路 */
  function step2() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('ah18s2');
    s += rect(15, 20, 730, 60, 'fig-box');
    s += txt(380, 44, 'doToQuery → MatchQueryParser.parse', 'fig-name');
    s += txt(380, 66, 'Type.BOOLEAN · occur = SHOULD(默认 OR)', 'fig-key');
    s += rect(15, 105, 230, 56, 'fig-box');
    s += txt(130, 127, 'operator', 'fig-key');
    s += txt(130, 149, 'OR → SHOULD', 'fig-sub');
    s += rect(265, 105, 230, 56, 'fig-box');
    s += txt(380, 127, 'analyzer', 'fig-key');
    s += txt(380, 149, '字段 search analyzer', 'fig-sub');
    s += rect(515, 105, 230, 56, 'fig-box');
    s += txt(630, 127, 'zero_terms_query', 'fig-key');
    s += txt(630, 149, 'none → 不匹配', 'fig-sub');
    s += rect(15, 185, 730, 56, 'fig-box-hot', 'fp-pop');
    s += txt(380, 209, '默认 keyword 保留整串', 'fig-name');
    s += txt(380, 231, '默认 keyword 可提前 Builder rewrite;否则 parser 短路', 'fig-sub');
    s += txt(380, 272, '本例 text + standard → createBooleanQuery', 'fig-sub');
    return s + '</svg>';
  }

  /* 步骤 3:tokenStream 切词 */
  function step3() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('ah18s3');
    s += rect(15, 20, 730, 52, 'fig-box');
    s += txt(380, 42, 'analyzer.tokenStream("title", "quick brown")', 'fig-key');
    s += txt(380, 62, 'standard:词边界切分 + lowercase', 'fig-sub');
    s += rect(105, 100, 220, 56, 'fig-box', 'fp-pop');
    s += txt(215, 124, 'token[0]', 'fig-name');
    s += txt(215, 148, 'quick', 'fig-key');
    s += rect(435, 100, 220, 56, 'fig-box', 'fp-pop');
    s += txt(545, 124, 'token[1] · position+1', 'fig-name');
    s += txt(545, 148, 'brown', 'fig-key');
    s += rect(15, 180, 730, 78, 'fig-box');
    s += txt(380, 204, 'createFieldQuery 先数 token', 'fig-name');
    s += txt(380, 226, '0 个 → zero_terms_query;1 个 → 单 TermQuery', 'fig-sub');
    s += txt(380, 248, '多个且跨 position → analyzeMultiBoolean', 'fig-sub');
    return s + '</svg>';
  }

  /* 步骤 4:analyzeMultiBoolean 组布尔 */
  function step4() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('ah18s4');
    s += rect(105, 20, 550, 52, 'fig-box');
    s += txt(380, 42, 'analyzeMultiBoolean:每个 position 一个子句', 'fig-name');
    s += txt(380, 64, 'occur = SHOULD', 'fig-sub');
    s += line(300, 72, 260, 100, 'ah18s4');
    s += line(460, 72, 500, 100, 'ah18s4');
    s += rect(140, 104, 240, 52, 'fig-box');
    s += txt(260, 128, 'TermQuery', 'fig-key');
    s += txt(260, 150, '("title","quick")', 'fig-sub');
    s += rect(380, 104, 240, 52, 'fig-box');
    s += txt(500, 128, 'TermQuery', 'fig-key');
    s += txt(500, 150, '("title","brown")', 'fig-sub');
    s += line(260, 156, 340, 185, 'ah18s4');
    s += line(500, 156, 420, 185, 'ah18s4');
    s += rect(230, 189, 300, 78, 'fig-box-hot', 'fp-pop');
    s += txt(380, 213, 'BooleanQuery', 'fig-name');
    s += txt(380, 235, 'SHOULD + SHOULD', 'fig-sub');
    s += txt(380, 257, '同文档多命中可累加贡献', 'fig-sub');
    s += txt(380, 288, 'operator:and 只改 occur 为 MUST;短语相邻是 match_phrase 的事', 'fig-sub');
    return s + '</svg>';
  }

  /* 步骤 5:term 对照:整串当 key */
  function step5() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('ah18s5');
    s += rect(15, 20, 355, 140, 'fig-box');
    s += txt(192, 44, 'term: "quick brown"', 'fig-name');
    s += txt(192, 72, '不跑 tokenStream', 'fig-sub');
    s += txt(192, 96, 'BytesRef 整串当 key', 'fig-key');
    s += txt(192, 120, 'TermBasedFieldType.termQuery', 'fig-sub');
    s += txt(192, 146, 'indexedValueForSearch 原样', 'fig-sub');
    s += rect(390, 20, 355, 140, 'fig-box');
    s += txt(567, 44, 'text 字段的词典', 'fig-name');
    s += txt(567, 72, 'the / quick / brown / fox', 'fig-sub');
    s += txt(567, 96, '没有 "quick brown" 这个 key', 'fig-sub');
    s += txt(567, 128, '→ 0 hits', 'fig-key', true);
    s += rect(15, 180, 730, 78, 'fig-box');
    s += txt(380, 204, 'term 在 text 上仍然跳过分析', 'fig-name');
    s += txt(380, 226, 'term: "Quick" 也 0 hits——词典里只有小写', 'fig-sub');
    s += txt(380, 248, 'keyword 上的 term 对整串;normalizer 只归一化成单 token', 'fig-sub');
    return s + '</svg>';
  }

  /* 步骤 6:接第 17 课三层字段 */
  function step6() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('ah18s6');
    s += rect(205, 15, 350, 48, 'fig-box');
    s += txt(380, 37, '写入 originalQuery', 'fig-name');
    s += txt(380, 57, 'parsedQuery 保存 originalQuery 与 query', 'fig-sub');
    s += line(380, 63, 380, 76, 'ah18s6');
    s += rect(205, 80, 350, 48, 'fig-box');
    s += txt(380, 102, 'preProcess 改 query', 'fig-name');
    s += txt(380, 122, 'alias/nested/slice 加成 FILTER', 'fig-sub');
    s += line(380, 128, 380, 141, 'ah18s6');
    s += rect(205, 145, 350, 48, 'fig-box-hot', 'fp-pop');
    s += txt(380, 167, 'rewrittenQuery()', 'fig-name');
    s += txt(380, 187, 'searcher.rewrite 之后才 search', 'fig-sub');
    s += rect(15, 215, 730, 60, 'fig-box');
    s += txt(380, 238, 'SHOULD 两个 term 出现在第 1 层', 'fig-key');
    s += txt(380, 260, '第 16 课每个 shard 回的 _score,就是这份查询跑出来的', 'fig-sub');
    return s + '</svg>';
  }

  window.ESFLOWS = window.ESFLOWS || {};
  window.ESFLOWS['ch18-match-to-should'] = {
    version: 1,
    id: 'ch18-match-to-should',
    title: '一句 match 的翻译之旅',
    speed: 2200,
    steps: [
      { svg: step1(), note: "JSON 解析成 MatchQueryBuilder；SearchExecutionContext.toQuery 先 rewrite Builder，再调用 doToQuery 构造 Lucene Query。分片可以承担该转换，本图省略协调侧提前 rewrite 等分支。" },
      { svg: step2(), note: "本例 title 显式 standard、默认 OR→SHOULD。默认 keyword 的 match 可在 Builder rewrite 阶段转为 TermQueryBuilder；仍进入 parser 时另有关键词短路，不能说一定在此才短路。" },
      { svg: step3(), note: "StandardTokenizer 按词边界切分，LowerCaseFilter 小写化；本例 quick/brown 是两个位置。零词项按 zero_terms_query，单词项生成字段查询；同义词图、模糊查询等会改变构造。" },
      { svg: step4(), note: "本例多个位置各建 TermQuery，默认 SHOULD 至少匹配一个。同一文档可累加两个匹配贡献，但跨文档不能仅据匹配词数保证排序。AND 要求都在；短语另检查位置与顺序。" },
      { svg: step5(), note: "默认 text 的 term 不运行全文分析，quick brown 整串不在本例词典中。keyword 配 normalizer 时 term 可以归一化单词项，不能把不分词等同所有字段都原样比较。" },
      { svg: step6(), note: "parsedQuery 写 originalQuery 与 query；preProcess 按条件加入过滤，rewrittenQuery 懒加载 searcher.rewrite。Explain 解释执行查询，也会受到别名过滤约束；原查询主要保留给默认高亮等用途。" }
    ]
  };

  /* ===== 实验：A13 / B9 / C11 / 清理1；保留原19稳定ID ===== */
  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};
  window.ESEXPERIMENTS["ch18-00-setup"] = {
  "version": 1,
  "id": "ch18-00-setup",
  "title": "A1 · 创建本课索引与 published 过滤别名",
  "method": "PUT",
  "path": "/tut-l18-dsl",
  "body": {
    "settings": {
      "number_of_shards": 1,
      "number_of_replicas": 0,
      "auto_expand_replicas": false,
      "refresh_interval": "-1",
      "requests.cache.enable": false,
      "default_pipeline": "_none",
      "final_pipeline": "_none",
      "mapping.source.mode": "stored",
      "analysis": {
        "normalizer": {
          "fold_status": {
            "type": "custom",
            "filter": [
              "lowercase"
            ]
          }
        }
      }
    },
    "mappings": {
      "dynamic": "strict",
      "properties": {
        "title": {
          "type": "text",
          "analyzer": "standard",
          "search_analyzer": "standard",
          "term_vector": "with_positions_offsets"
        },
        "status": {
          "type": "keyword"
        },
        "status_fold": {
          "type": "keyword",
          "normalizer": "fold_status"
        },
        "price": {
          "type": "float"
        },
        "date": {
          "type": "date",
          "format": "strict_date_optional_time"
        }
      }
    },
    "aliases": {
      "tut-l18-published": {
        "filter": {
          "term": {
            "status": "published"
          }
        }
      }
    }
  },
  "predict": "title 是 text、status 是 keyword——这两个字段进倒排的 key 分别长什么样?",
  "expect": "200，acknowledged=true；一主零副、周期刷新关闭、request cache 关闭。title 显式 standard 并保存词向量；status 不归一化，status_fold 只 lowercase。别名只允许 published。已存在时 400 resource_already_exists_exception：先执行末尾点名清理，再从 A1 重做。"
};
  window.ESEXPERIMENTS["ch18-19-health"] = {
  "version": 1,
  "id": "ch18-19-health",
  "title": "A2 · 等待本课索引 green",
  "method": "GET",
  "path": "/_cluster/health/tut-l18-dsl?wait_for_status=green&wait_for_no_initializing_shards=true&timeout=10s",
  "body": null,
  "predict": "为何只看本课索引，而不要求整个集群 green？",
  "expect": "200、status=green、timed_out=false、active_primary_shards=1。仅本课一主零副的健康等待；超时应先恢复分片，再写入，不能把超时当就绪。"
};
  window.ESEXPERIMENTS["ch18-01-bulk"] = {
  "version": 1,
  "id": "ch18-01-bulk",
  "title": "A3 · 固定 ID 写入四篇文档并显式刷新",
  "method": "POST",
  "path": "/tut-l18-dsl/_bulk?refresh=true",
  "body": "{\"index\":{\"_index\":\"tut-l18-dsl\",\"_id\":\"1\"}}\n{\"title\":\"The quick brown fox\",\"status\":\"published\",\"price\":39.99,\"date\":\"2024-01-15\",\"status_fold\":\"PUBLISHED\"}\n{\"index\":{\"_index\":\"tut-l18-dsl\",\"_id\":\"2\"}}\n{\"title\":\"quick brown\",\"status\":\"draft\",\"price\":29.99,\"date\":\"2024-06-20\",\"status_fold\":\"DRAFT\"}\n{\"index\":{\"_index\":\"tut-l18-dsl\",\"_id\":\"3\"}}\n{\"title\":\"lazy dog\",\"status\":\"published\",\"price\":49.99,\"date\":\"2023-11-01\",\"status_fold\":\"PUBLISHED\"}\n{\"index\":{\"_index\":\"tut-l18-dsl\",\"_id\":\"4\"}}\n{\"title\":\"Elasticsearch in Action\",\"status\":\"published\",\"price\":39.99,\"date\":\"2024-01-15\",\"status_fold\":\"PUBLISHED\"}\n",
  "predict": "\"The quick brown fox\" 索引后,title 词典里会躺哪几个 key?",
  "expect": "errors=false、四项首次 status=201/result=created；未清理重复写为 200/updated。固定 ID 不增加篇数，refresh=true 确保后续搜索可见。四篇 title/status/price/date 与表格一致；status_fold 输入大写、索引为小写整串。"
};
  window.ESEXPERIMENTS["ch18-02-analyze"] = {
  "version": 1,
  "id": "ch18-02-analyze",
  "title": "A4 · _analyze:词典里到底躺着什么",
  "method": "POST",
  "path": "/tut-l18-dsl/_analyze?filter_path=tokens.token",
  "body": {
    "field": "title",
    "text": "The quick brown fox"
  },
  "predict": "会留下哪些 token?大小写呢?整串 \"quick brown\" 会在吗?",
  "expect": "the、quick、brown、fox；standard 默认保留 the。_analyze 展示指定字段的分析输出，不是直接枚举倒排词典；A5 读取本例保存的词向量，核对文档 1 的实际词项和位置。"
};
  window.ESEXPERIMENTS["ch18-20-termvectors"] = {
  "version": 1,
  "id": "ch18-20-termvectors",
  "title": "A5 · 读取文档 1 保存的词项与位置",
  "method": "POST",
  "path": "/tut-l18-dsl/_termvectors/1",
  "body": {
    "fields": [
      "title"
    ],
    "positions": true,
    "offsets": true,
    "term_statistics": false,
    "field_statistics": false
  },
  "predict": "本课显式存了词向量，能看到整串 quick brown 吗？",
  "expect": "found=true；terms 为 the/quick/brown/fox，position 分别 0/1/2/3。不存在 quick brown 整串。offsets 是本课显式 term_vector 的产物，不推广为默认 text 总保存 offsets。"
};
  window.ESEXPERIMENTS["ch18-21-query-analyze"] = {
  "version": 1,
  "id": "ch18-21-query-analyze",
  "title": "A6 · standard 处理 Quick, BROWN!",
  "method": "POST",
  "path": "/tut-l18-dsl/_analyze",
  "body": {
    "field": "title",
    "text": "Quick, BROWN!"
  },
  "predict": "逗号和叹号两侧没有全是空白，standard 如何处理？",
  "expect": "tokens 为 quick/brown，position=0/1。StandardTokenizer 按词边界切分，LowerCaseFilter 小写化；不是简单的空白切分。这个请求不改变字段 mapping。"
};
  window.ESEXPERIMENTS["ch18-03-match"] = {
  "version": 1,
  "id": "ch18-03-match",
  "title": "A7 · match \"quick brown\":SHOULD 命中",
  "method": "POST",
  "path": "/tut-l18-dsl/_search?filter_path=hits.total,hits.hits._id,hits.hits._score",
  "body": {
    "query": {
      "match": {
        "title": "quick brown"
      }
    }
  },
  "predict": "默认 OR 的两个词都在文档 1、2 中。能仅用这次结果证明 SHOULD 吗？B1 会换成 quick fox。",
  "expect": "_id 1、2(SHOULD:quick 或 brown 中任一即进候选;3 是 lazy dog,4 是 Elasticsearch in Action)。分数与排序以 BM25 为准(第 20 课展开)——match 不是「把整句拿去倒排里找」。"
};
  window.ESEXPERIMENTS["ch18-04-term-whole"] = {
  "version": 1,
  "id": "ch18-04-term-whole",
  "title": "A8 · term \"quick brown\":整串落空",
  "method": "POST",
  "path": "/tut-l18-dsl/_search?filter_path=hits.total",
  "body": {
    "query": {
      "term": {
        "title": "quick brown"
      }
    }
  },
  "predict": "文档 1、2 的 _source 里明明写着 quick brown——整串 term 能命中吗?",
  "expect": "total: 0。term 不跑分析器,拿 \"quick brown\" 当一个 key 去词典找,而词典里只有切开的小写 token。_source 里「看得见」和倒排里「找得到」是两回事。"
};
  window.ESEXPERIMENTS["ch18-05-term-quick"] = {
  "version": 1,
  "id": "ch18-05-term-quick",
  "title": "A9 · term \"quick\":碰巧是 token",
  "method": "POST",
  "path": "/tut-l18-dsl/_search?filter_path=hits.total,hits.hits._id",
  "body": {
    "query": {
      "term": {
        "title": "quick"
      }
    }
  },
  "predict": "单个词、全小写的 term 呢?",
  "expect": "命中 ID 1、2。小写 quick 与本例已有索引 term 精确一致；term 不运行全文分析器。能命中取决于查询值与 mapping 产物相同，不是必须依赖运气。"
};
  window.ESEXPERIMENTS["ch18-06-term-Quick"] = {
  "version": 1,
  "id": "ch18-06-term-Quick",
  "title": "A10 · term \"Quick\":大写 miss",
  "method": "POST",
  "path": "/tut-l18-dsl/_search?filter_path=hits.total",
  "body": {
    "query": {
      "term": {
        "title": "Quick"
      }
    }
  },
  "predict": "只把 Q 大写,其它不动?",
  "expect": "total: 0。term 不小写化,词典里只有 quick。text 字段上用 term,连大小写都能让你悄悄 miss——0 hits 不是 bug,是查询 key 和索引 key 不是同一种东西。"
};
  window.ESEXPERIMENTS["ch18-07-term-status"] = {
  "version": 1,
  "id": "ch18-07-term-status",
  "title": "A11 · keyword 上的 term：精确值相等",
  "method": "POST",
  "path": "/tut-l18-dsl/_search?filter_path=hits.total,hits.hits._id",
  "body": {
    "query": {
      "term": {
        "status": "published"
      }
    }
  },
  "predict": "换成 keyword 字段呢?",
  "expect": "_id 1、3、4。status 是 keyword,存的就是整串 \"published\",term 拿整串找整串。term 的正确用法在 keyword / 数字 / 日期 / bool 这些结构化字段上。"
};
  window.ESEXPERIMENTS["ch18-15-match-keyword"] = {
  "version": 1,
  "id": "ch18-15-match-keyword",
  "title": "A12 · match 打在 keyword 上:短路整串",
  "method": "POST",
  "path": "/tut-l18-dsl/_search?filter_path=hits.total",
  "body": {
    "query": {
      "match": {
        "status": "published draft"
      }
    }
  },
  "predict": "match 会把 \"published draft\" 切成两个 token 吗?注意这是 keyword 字段。",
  "expect": "total=0：默认 keyword 分析器保留 published draft 整串。Builder 阶段通常先改写为 TermQueryBuilder；若仍进入 MatchQueryParser，也有 keyword analyzer 短路。带 normalizer 或显式 analyzer 时需另判断，不能一概称 keyword 永不分析。"
};
  window.ESEXPERIMENTS["ch18-25-normalized-term"] = {
  "version": 1,
  "id": "ch18-25-normalized-term",
  "title": "A13 · keyword normalizer 只归一化单词项",
  "method": "POST",
  "path": "/tut-l18-dsl/_search?filter_path=hits.total,hits.hits._id,hits.hits._score",
  "body": {
    "query": {
      "term": {
        "status_fold": "PUBLISHED"
      }
    }
  },
  "predict": "term 没有全文分词，为何大写值仍能命中？",
  "expect": "命中 1、3、4。字段 normalizer 把 PUBLISHED 归一化为单个 published，term 使用该字段的 indexedValueForSearch；不把“term 不分词”等同“所有字段都原样比较”。"
};
  window.ESEXPERIMENTS["ch18-22-match-or"] = {
  "version": 1,
  "id": "ch18-22-match-or",
  "title": "B1 · quick fox：默认 OR 的对照",
  "method": "POST",
  "path": "/tut-l18-dsl/_search?filter_path=hits.total,hits.hits._id,hits.hits._score",
  "body": {
    "query": {
      "match": {
        "title": "quick fox"
      }
    }
  },
  "predict": "文档 2 没有 fox，会被排除吗？",
  "expect": "命中 1、2；默认 SHOULD 至少一项，文档 2 只有 quick 也命中。与 B2 同一串显式 AND 的结果对照，不能仅靠 quick brown 的双词均中证明 OR。"
};
  window.ESEXPERIMENTS["ch18-08-match-and"] = {
  "version": 1,
  "id": "ch18-08-match-and",
  "title": "B2 · operator:and 只改 occur",
  "method": "POST",
  "path": "/tut-l18-dsl/_search?filter_path=hits.total,hits.hits._id",
  "body": {
    "query": {
      "match": {
        "title": {
          "query": "quick fox",
          "operator": "and"
        }
      }
    }
  },
  "predict": "默认 OR 时 \"quick fox\" 命中谁?and 之后呢?and 是变成短语了吗?",
  "expect": "OR 会命中 1、2(quick 两篇都有);AND 只剩 _id 1(\"The quick brown fox\" 两个词都有,doc2 没有 fox)。operator 改的是 occur(SHOULD→MUST),只要求「都在」,不要求「相邻」——相邻是 B4 的 match_phrase。"
};
  window.ESEXPERIMENTS["ch18-23-and-reversed"] = {
  "version": 1,
  "id": "ch18-23-and-reversed",
  "title": "B3 · AND brown quick：不要求词序",
  "method": "POST",
  "path": "/tut-l18-dsl/_search?filter_path=hits.total,hits.hits._id,hits.hits._score",
  "body": {
    "query": {
      "match": {
        "title": {
          "query": "brown quick",
          "operator": "and"
        }
      }
    }
  },
  "predict": "将两词顺序反转，AND 会像短语那样失败吗？",
  "expect": "仍命中 1、2；MUST 要求两个 term 都在，不要求位置或词序。B5 反向 match_phrase 在同一数据上是零命中。"
};
  window.ESEXPERIMENTS["ch18-16-phrase-right"] = {
  "version": 1,
  "id": "ch18-16-phrase-right",
  "title": "B4 · match_phrase \"quick brown\":要相邻",
  "method": "POST",
  "path": "/tut-l18-dsl/_search?filter_path=hits.total,hits.hits._id",
  "body": {
    "query": {
      "match_phrase": {
        "title": "quick brown"
      }
    }
  },
  "predict": "quick 和 brown 在两篇里都相邻吗?",
  "expect": "_id 1、2:两篇里 quick、brown 都位置相邻。match_phrase 同样先分析(token 相同),但建的是 PhraseQuery——除了「都在」,还要求位置挨着(slop 默认 0)。"
};
  window.ESEXPERIMENTS["ch18-17-phrase-wrong"] = {
  "version": 1,
  "id": "ch18-17-phrase-wrong",
  "title": "B5 · match_phrase \"brown quick\":顺序反了",
  "method": "POST",
  "path": "/tut-l18-dsl/_search?filter_path=hits.total",
  "body": {
    "query": {
      "match_phrase": {
        "title": "brown quick"
      }
    }
  },
  "predict": "同样的两个词、顺序反过来?",
  "expect": "total=0：brown quick 顺序反向，默认 slop=0 不匹配。两词在原文中相邻，但顺序不同；B3 的 AND brown quick 仍命中 1、2，B6 quick fox 则展示正向但有间隔的短语也不匹配。"
};
  window.ESEXPERIMENTS["ch18-24-phrase-gap"] = {
  "version": 1,
  "id": "ch18-24-phrase-gap",
  "title": "B6 · quick fox：两个词中间有 brown",
  "method": "POST",
  "path": "/tut-l18-dsl/_search?filter_path=hits.total,hits.hits._id,hits.hits._score",
  "body": {
    "query": {
      "match_phrase": {
        "title": "quick fox"
      }
    }
  },
  "predict": "AND quick fox 命中文档 1，slop=0 的短语呢？",
  "expect": "total=0；文档 1 quick 和 fox 的位置为 1 与 3，中间有 brown。仅有相同词项不足以满足默认相邻短语；显式 slop 可放宽，未改变索引配置。"
};
  window.ESEXPERIMENTS["ch18-26-zero-none"] = {
  "version": 1,
  "id": "ch18-26-zero-none",
  "title": "B7 · 显式 stop 分析器：零词项 none",
  "method": "POST",
  "path": "/tut-l18-dsl/_search?filter_path=hits.total,hits.hits._id,hits.hits._score",
  "body": {
    "query": {
      "match": {
        "title": {
          "query": "the",
          "analyzer": "stop",
          "zero_terms_query": "none"
        }
      }
    }
  },
  "predict": "默认 standard 保留 the；本次请求覆盖为 stop 后会怎样？",
  "expect": "total=0。stop 把 the 移除，零词项按 none 不匹配。请求 analyzer 只覆盖本次查询；字段索引与 search_analyzer 仍为 standard。"
};
  window.ESEXPERIMENTS["ch18-27-zero-all"] = {
  "version": 1,
  "id": "ch18-27-zero-all",
  "title": "B8 · 同一零词项查询改为 all",
  "method": "POST",
  "path": "/tut-l18-dsl/_search?filter_path=hits.total,hits.hits._id,hits.hits._score",
  "body": {
    "query": {
      "match": {
        "title": {
          "query": "the",
          "analyzer": "stop",
          "zero_terms_query": "all"
        }
      }
    }
  },
  "predict": "零词项仍然存在，改变的是哪一层行为？",
  "expect": "命中全部 1、2、3、4；zero_terms_query=all 选择 match_all，不是把 the 加回词流。本例没有额外过滤；实际外层 bool/alias 约束仍可缩小集合。"
};
  window.ESEXPERIMENTS["ch18-32-validate-should"] = {
  "version": 1,
  "id": "ch18-32-validate-should",
  "title": "B9 · validate 展示 Lucene OR 表示",
  "method": "POST",
  "path": "/tut-l18-dsl/_validate/query?explain=true&rewrite=true",
  "body": {
    "query": {
      "match": {
        "title": "quick brown"
      }
    }
  },
  "predict": "解释中的两个 term 是否带 MUST 的 + 号？",
  "expect": "valid=true；explanation 含 title:quick title:brown，默认 OR 没有两个 +。validate 展示改写后的查询表示；结合源代码的 Occur.SHOULD 与命中对照，不保证任意分析器都产出这棵简单树。"
};
  window.ESEXPERIMENTS["ch18-09-explain-1"] = {
  "version": 1,
  "id": "ch18-09-explain-1",
  "title": "C1 · POST _explain：观察执行查询的两个词项",
  "method": "POST",
  "path": "/tut-l18-dsl/_explain/1",
  "body": {
    "query": {
      "match": {
        "title": "quick brown"
      }
    }
  },
  "predict": "explanation 的 description 里会出现 \"match\" 这个词吗?能看到什么?",
  "expect": "200、matched=true，explanation 包含 title:quick 与 title:brown 的贡献。结合 B9 validate 的两项 OR 表示理解 SHOULD；Explain 描述不保证出现 SHOULD 字样。它先 preProcess，再解释 rewrittenQuery；用过滤别名时也包含别名约束。"
};
  window.ESEXPERIMENTS["ch18-10-explain-3"] = {
  "version": 1,
  "id": "ch18-10-explain-3",
  "title": "C2 · 不命中的 _explain",
  "method": "POST",
  "path": "/tut-l18-dsl/_explain/3?filter_path=matched,explanation.description",
  "body": {
    "query": {
      "match": {
        "title": "quick brown"
      }
    }
  },
  "predict": "lazy dog 那篇的 matched 是什么?会报错吗?",
  "expect": "200、matched=false；文档 3 存在但不满足查询。不要把不匹配与文档不存在混为一谈。网页用 POST 发送查询体；GET body 不会被浏览器客户端发送。"
};
  window.ESEXPERIMENTS["ch18-11-explain-in-search"] = {
  "version": 1,
  "id": "ch18-11-explain-in-search",
  "title": "C3 · explain:true:另一个入口",
  "method": "POST",
  "path": "/tut-l18-dsl/_search?filter_path=hits.hits._id,hits.hits._score,hits.hits._explanation.description",
  "body": {
    "explain": true,
    "query": {
      "match": {
        "title": "quick brown"
      }
    }
  },
  "predict": "\"explain\": true 和 _explain API 是一回事吗?",
  "expect": "ID 1、2 各带 _explanation，解释主执行查询 rewrittenQuery（可能再有 rescore 等加工）。与单篇 _explain 是不同入口。本例没有额外过滤时，文档 1 的主评分解释应一致。"
};
  window.ESEXPERIMENTS["ch18-33-explain-alias"] = {
  "version": 1,
  "id": "ch18-33-explain-alias",
  "title": "C4 · 过滤别名解释文档 2",
  "method": "POST",
  "path": "/tut-l18-published/_explain/2",
  "body": {
    "query": {
      "match": {
        "title": "quick brown"
      }
    }
  },
  "predict": "文档 2 满足两个词，但 status=draft；Explain 会只看用户原查询吗？",
  "expect": "200、matched=false，explanation 含 status:published 的失败约束。_explain 同样 preProcess + rewrittenQuery，别名过滤参与判断。文档 2 存在，false 不是资源缺失。"
};
  window.ESEXPERIMENTS["ch18-12-bool-filter"] = {
  "version": 1,
  "id": "ch18-12-bool-filter",
  "title": "C5 · must 管全文,filter 管条件",
  "method": "POST",
  "path": "/tut-l18-dsl/_search?filter_path=hits.total,hits.hits._id,hits.hits._score",
  "body": {
    "query": {
      "bool": {
        "must": [
          {
            "match": {
              "title": "elasticsearch"
            }
          }
        ],
        "filter": [
          {
            "term": {
              "status": "published"
            }
          },
          {
            "range": {
              "price": {
                "lte": 50
              }
            }
          }
        ]
      }
    }
  },
  "predict": "谁被滤掉?_score 里有 status / price 的贡献吗?",
  "expect": "_id 4(Elasticsearch in Action,published,39.99)。filter 只问「在不在」,不算分——_score 只来自 must 里的 match。状态、价格这类「只要是不是」的条件就该放这里。"
};
  window.ESEXPERIMENTS["ch18-13-bool-must"] = {
  "version": 1,
  "id": "ch18-13-bool-must",
  "title": "C6 · 同一条件搬进 must:分数变了",
  "method": "POST",
  "path": "/tut-l18-dsl/_search?filter_path=hits.total,hits.hits._id,hits.hits._score",
  "body": {
    "query": {
      "bool": {
        "must": [
          {
            "match": {
              "title": "elasticsearch"
            }
          },
          {
            "term": {
              "status": "published"
            }
          }
        ]
      }
    }
  },
  "predict": "hits 变吗?_score 变吗?",
  "expect": "仍只命中 ID 4，但相较 C5 的 _score 增加：status 的 term 在 must 下也贡献分数。本例 keyword 的 TermQuery 使用相似度评分，并非固定常数分；价格过滤与否在这四篇数据上不改变命中集合。"
};
  window.ESEXPERIMENTS["ch18-28-filter-only"] = {
  "version": 1,
  "id": "ch18-28-filter-only",
  "title": "C7 · 纯 filter：分数为零",
  "method": "POST",
  "path": "/tut-l18-dsl/_search?filter_path=hits.total,hits.hits._id,hits.hits._score",
  "body": {
    "query": {
      "bool": {
        "filter": {
          "term": {
            "status": "published"
          }
        }
      }
    }
  },
  "predict": "仅有过滤条件，没有 must/should，_score 是多少？",
  "expect": "命中 1、3、4，_score 全为 0。若再加 match_all 到 must，分数可为 1；不能把所有过滤搜索都说成固定 0。不以两次请求承诺缓存命中。"
};
  window.ESEXPERIMENTS["ch18-29-should-optional"] = {
  "version": 1,
  "id": "ch18-29-should-optional",
  "title": "C8 · 有 filter 时 should 默认可选",
  "method": "POST",
  "path": "/tut-l18-dsl/_search?filter_path=hits.total,hits.hits._id,hits.hits._score",
  "body": {
    "query": {
      "bool": {
        "filter": {
          "term": {
            "status": "published"
          }
        },
        "should": [
          {
            "match": {
              "title": "quick"
            }
          }
        ]
      }
    }
  },
  "predict": "published 文档 3、4 都没有 quick，会留下吗？",
  "expect": "命中 1、3、4；同层已有 filter，minimum_should_match 默认 0，should 仅给文档 1 加分。3、4 保留且分数为 0。"
};
  window.ESEXPERIMENTS["ch18-30-should-required"] = {
  "version": 1,
  "id": "ch18-30-should-required",
  "title": "C9 · 显式 minimum_should_match=1",
  "method": "POST",
  "path": "/tut-l18-dsl/_search?filter_path=hits.total,hits.hits._id,hits.hits._score",
  "body": {
    "query": {
      "bool": {
        "filter": {
          "term": {
            "status": "published"
          }
        },
        "should": [
          {
            "match": {
              "title": "quick"
            }
          }
        ],
        "minimum_should_match": 1
      }
    }
  },
  "predict": "仅改门槛，命中集合会怎样？",
  "expect": "只命中 1；published AND 至少一个 should。显式 1 将可选 quick 变成必要条件；这不是 operator 参数，也不作用于其他层 bool。"
};
  window.ESEXPERIMENTS["ch18-14-post-filter"] = {
  "version": 1,
  "id": "ch18-14-post-filter",
  "title": "C10 · post_filter:hits 瘦身,聚合不看",
  "method": "POST",
  "path": "/tut-l18-dsl/_search?filter_path=hits.total,hits.hits._id,aggregations",
  "body": {
    "query": {
      "match_all": {}
    },
    "aggs": {
      "by_status": {
        "terms": {
          "field": "status"
        }
      }
    },
    "post_filter": {
      "term": {
        "status": "published"
      }
    }
  },
  "predict": "hits 是谁?聚合桶里还有 draft 吗?",
  "expect": "hits 为 ID 1、3、4；聚合 published=3、draft=1。post_filter 在 Query 阶段的 hits 收集路径检查，聚合路径不检查它；不是对已取出的 Top-N 再过滤。C11 将条件移进 bool.filter 后，draft 桶消失。"
};
  window.ESEXPERIMENTS["ch18-31-aggregation-filter"] = {
  "version": 1,
  "id": "ch18-31-aggregation-filter",
  "title": "C11 · 条件移进 query，聚合也缩小",
  "method": "POST",
  "path": "/tut-l18-dsl/_search?filter_path=hits.total,hits.hits._id,aggregations",
  "body": {
    "query": {
      "bool": {
        "filter": {
          "term": {
            "status": "published"
          }
        }
      }
    },
    "aggs": {
      "by_status": {
        "terms": {
          "field": "status"
        }
      }
    }
  },
  "predict": "与 C10 的 post_filter 相比，draft 桶还会出现吗？",
  "expect": "hits 仍为 1、3、4；聚合只有 published=3，draft 消失。bool.filter 限制主 query 文档集，普通顶层聚合和 hits 共享这个集合；未使用 global 聚合。"
};
  window.ESEXPERIMENTS["ch18-18-cleanup"] = {
  "version": 1,
  "id": "ch18-18-cleanup",
  "title": "清理 · 删除 tut-l18-dsl",
  "method": "DELETE",
  "path": "/tut-l18-dsl",
  "predict": "本课资源用完，删除父索引会怎样处理它的过滤别名？",
  "expect": "200、acknowledged=true，删除 tut-l18-dsl 及其别名 tut-l18-published。再次清理在资源已不存在时返回 404 index_not_found_exception；重做按 A1→A2→A3→其余卡片→清理。不删除其他章节资源。"
};
})();
