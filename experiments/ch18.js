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
    s += txt(380, 209, 'keyword 字段在这里短路', 'fig-name');
    s += txt(380, 231, 'KEYWORD_ANALYZER → 直接 TermQuery 整串,不切', 'fig-sub');
    s += txt(380, 272, 'text 字段没有这条短路,继续 createBooleanQuery', 'fig-sub');
    return s + '</svg>';
  }

  /* 步骤 3:tokenStream 切词 */
  function step3() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('ah18s3');
    s += rect(15, 20, 730, 52, 'fig-box');
    s += txt(380, 42, 'analyzer.tokenStream("title", "quick brown")', 'fig-key');
    s += txt(380, 62, 'standard:小写、按空白切', 'fig-sub');
    s += rect(105, 100, 220, 56, 'fig-box', 'fp-pop');
    s += txt(215, 124, 'token[0]', 'fig-name');
    s += txt(215, 148, 'quick', 'fig-key');
    s += rect(435, 100, 220, 56, 'fig-box', 'fp-pop');
    s += txt(545, 124, 'token[1] · position+1', 'fig-name');
    s += txt(545, 148, 'brown', 'fig-key');
    s += rect(15, 180, 730, 60, 'fig-box');
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
    s += rect(230, 189, 300, 64, 'fig-box-hot', 'fp-pop');
    s += txt(380, 213, 'BooleanQuery', 'fig-name');
    s += txt(380, 235, 'SHOULD + SHOULD', 'fig-sub');
    s += txt(380, 257, '命中任一进候选,越多分越高', 'fig-sub');
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
    s += rect(15, 180, 730, 64, 'fig-box');
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
    s += txt(380, 57, 'parsedQuery 一次写两个字段', 'fig-sub');
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
      { svg: step1(), note: 'REST 把 JSON 解析成 MatchQueryBuilder,但它只是「怎么造查询」的描述。真正翻译发生在数据节点的 SearchExecutionContext.toQuery——本课就是这一跳,造完写进第 17 课的 originalQuery。' },
      { svg: step2(), note: 'doToQuery 造 MatchQueryParser:默认 operator 是 OR,映射只有两行——OR→SHOULD、AND→MUST。keyword 字段有短路:分析器就是 KEYWORD_ANALYZER 时直接 TermQuery 整串,根本不切;text 字段继续走切词链。' },
      { svg: step3(), note: 'tokenStream 把查询串当文档切:standard 小写、按空白分,quick 和 brown 落在两个 position。createFieldQuery 数 token:0 个交给 zero_terms_query,1 个收成单 TermQuery,多个跨 position 才进 analyzeMultiBoolean。' },
      { svg: step4(), note: 'analyzeMultiBoolean 每个 position 出一个子句,occur 用传入的 SHOULD:命中任一词即进候选,两词都中分数更高。operator:and 只是改 MUST,不是变 phrase——位置相邻是 match_phrase → PhraseQuery 的事。' },
      { svg: step5(), note: 'term 把值原样 BytesRef 当词典 key,从不切词:text 词典里没有整串 quick brown,也没有大写 Quick——0 hits 不是 bug,是查询 key 和索引 key 不是同一种东西。keyword 上 term 对整串;normalizer 只归一化出恰好一个 token。' },
      { svg: step6(), note: '翻译出的 BooleanQuery 写进 originalQuery;preProcess 把 alias/nested/slice 包成 FILTER,改的是 query;searcher.rewrite 之后才是执行计划。第 16 课每个 shard 回的 _score,就是这份查询(经两层加工)跑出来的。' }
    ]
  };

  /* ===== 实验 ===== */
  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};

  window.ESEXPERIMENTS['ch18-00-setup'] = {
    version: 1, id: 'ch18-00-setup',
    title: '实验 0 · 建 tut-l18-dsl:title text + status keyword',
    method: 'PUT', path: '/tut-l18-dsl',
    body: {
      settings: { number_of_shards: 1, number_of_replicas: 0 },
      mappings: { properties: {
        title: { type: 'text' },
        status: { type: 'keyword' },
        price: { type: 'float' },
        date: { type: 'date' }
      } }
    },
    predict: 'title 是 text、status 是 keyword——这两个字段进倒排的 key 分别长什么样?',
    expect: 'acknowledged: true。title 存 token(standard 小写切词),status 存整串。后面所有 match/term 的胜负都由这一行 mapping 决定(第 11 课的伏笔)。'
  };
  window.ESEXPERIMENTS['ch18-01-bulk'] = {
    version: 1, id: 'ch18-01-bulk',
    title: '实验 1 · 四篇对照文档(?refresh=true)',
    method: 'POST', path: '/_bulk?refresh=true',
    body: '{"index":{"_index":"tut-l18-dsl","_id":"1"}}\n{"title":"The quick brown fox","status":"published","price":39.99,"date":"2024-01-15"}\n{"index":{"_index":"tut-l18-dsl","_id":"2"}}\n{"title":"quick brown","status":"draft","price":29.99,"date":"2024-06-20"}\n{"index":{"_index":"tut-l18-dsl","_id":"3"}}\n{"title":"lazy dog","status":"published","price":49.99,"date":"2023-11-01"}\n{"index":{"_index":"tut-l18-dsl","_id":"4"}}\n{"title":"Elasticsearch in Action","status":"published","price":39.99,"date":"2024-01-15"}\n',
    predict: '"The quick brown fox" 索引后,title 词典里会躺哪几个 key?',
    expect: 'errors: false,4 项 201。下一个实验用 _analyze 直接看切词结果——词典 key 就是那些 token,整串从来不进词典。'
  };
  window.ESEXPERIMENTS['ch18-02-analyze'] = {
    version: 1, id: 'ch18-02-analyze',
    title: '实验 2 · _analyze:词典里到底躺着什么',
    method: 'POST', path: '/tut-l18-dsl/_analyze?filter_path=tokens.token',
    body: { field: 'title', text: 'The quick brown fox' },
    predict: '会留下哪些 token?大小写呢?整串 "quick brown" 会在吗?',
    expect: 'tokens:the、quick、brown、fox,全小写(standard 默认不停用 the)。索引时的词典 key 就是这四个——"quick brown" 这样的整串从不在里面,这是实验 4 整串 term 落空的根据。'
  };
  window.ESEXPERIMENTS['ch18-03-match'] = {
    version: 1, id: 'ch18-03-match',
    title: '实验 3 · match "quick brown":SHOULD 命中',
    method: 'POST', path: '/tut-l18-dsl/_search?filter_path=hits.total,hits.hits._id,hits.hits._score',
    body: { query: { match: { title: 'quick brown' } } },
    predict: 'match 命中谁?一篇都没全中 "quick brown" 这个词组的文档 2 呢?',
    expect: '_id 1、2(SHOULD:quick 或 brown 中任一即进候选;3 是 lazy dog,4 是 Elasticsearch in Action)。分数与排序以 BM25 为准(第 20 课展开)——match 不是「把整句拿去倒排里找」。'
  };
  window.ESEXPERIMENTS['ch18-04-term-whole'] = {
    version: 1, id: 'ch18-04-term-whole',
    title: '实验 4 · term "quick brown":整串落空',
    method: 'POST', path: '/tut-l18-dsl/_search?filter_path=hits.total',
    body: { query: { term: { title: 'quick brown' } } },
    predict: '文档 1、2 的 _source 里明明写着 quick brown——整串 term 能命中吗?',
    expect: 'total: 0。term 不跑分析器,拿 "quick brown" 当一个 key 去词典找,而词典里只有切开的小写 token。_source 里「看得见」和倒排里「找得到」是两回事。'
  };
  window.ESEXPERIMENTS['ch18-05-term-quick'] = {
    version: 1, id: 'ch18-05-term-quick',
    title: '实验 5 · term "quick":碰巧是 token',
    method: 'POST', path: '/tut-l18-dsl/_search?filter_path=hits.total,hits.hits._id',
    body: { query: { term: { title: 'quick' } } },
    predict: '单个词、全小写的 term 呢?',
    expect: '_id 1、2。查询串碰巧就是索引 token(小写、单个),所以命中——但这是运气,不是 term 走了分析器。下一个实验换个大小写立刻见分晓。'
  };
  window.ESEXPERIMENTS['ch18-06-term-Quick'] = {
    version: 1, id: 'ch18-06-term-Quick',
    title: '实验 6 · term "Quick":大写 miss',
    method: 'POST', path: '/tut-l18-dsl/_search?filter_path=hits.total',
    body: { query: { term: { title: 'Quick' } } },
    predict: '只把 Q 大写,其它不动?',
    expect: 'total: 0。term 不小写化,词典里只有 quick。text 字段上用 term,连大小写都能让你悄悄 miss——0 hits 不是 bug,是查询 key 和索引 key 不是同一种东西。'
  };
  window.ESEXPERIMENTS['ch18-07-term-status'] = {
    version: 1, id: 'ch18-07-term-status',
    title: '实验 7 · keyword 上的 term:天作之合',
    method: 'POST', path: '/tut-l18-dsl/_search?filter_path=hits.total,hits.hits._id',
    body: { query: { term: { status: 'published' } } },
    predict: '换成 keyword 字段呢?',
    expect: '_id 1、3、4。status 是 keyword,存的就是整串 "published",term 拿整串找整串。term 的正确用法在 keyword / 数字 / 日期 / bool 这些结构化字段上。'
  };
  window.ESEXPERIMENTS['ch18-08-match-and'] = {
    version: 1, id: 'ch18-08-match-and',
    title: '实验 8 · operator:and 只改 occur',
    method: 'POST', path: '/tut-l18-dsl/_search?filter_path=hits.total,hits.hits._id',
    body: { query: { match: { title: { query: 'quick fox', operator: 'and' } } } },
    predict: '默认 OR 时 "quick fox" 命中谁?and 之后呢?and 是变成短语了吗?',
    expect: 'OR 会命中 1、2(quick 两篇都有);AND 只剩 _id 1("The quick brown fox" 两个词都有,doc2 没有 fox)。operator 改的是 occur(SHOULD→MUST),只要求「都在」,不要求「相邻」——相邻是实验 16 的 match_phrase。'
  };
  window.ESEXPERIMENTS['ch18-09-explain-1'] = {
    version: 1, id: 'ch18-09-explain-1',
    title: '实验 9 · _explain:看见两个 SHOULD',
    method: 'GET', path: '/tut-l18-dsl/_explain/1',
    body: { query: { match: { title: 'quick brown' } } },
    predict: 'explanation 的 description 里会出现 "match" 这个词吗?能看到什么?',
    expect: 'matched: true。details 里能指认 title:quick 与 title:brown 两条——图 2 的两个 SHOULD 就在这里(BM25 数值细节第 20 课拆)。_explain 对着 originalQuery 说话(第 17 课),里面已经是分析后的 Lucene Query,不是 JSON。'
  };
  window.ESEXPERIMENTS['ch18-10-explain-3'] = {
    version: 1, id: 'ch18-10-explain-3',
    title: '实验 10 · 不命中的 _explain',
    method: 'GET', path: '/tut-l18-dsl/_explain/3?filter_path=matched,explanation.description',
    body: { query: { match: { title: 'quick brown' } } },
    predict: 'lazy dog 那篇的 matched 是什么?会报错吗?',
    expect: 'matched: false,不报错——_explain 按 _id 单篇求值,不命中也返回,explanation 说明没有匹配的子句。'
  };
  window.ESEXPERIMENTS['ch18-11-explain-in-search'] = {
    version: 1, id: 'ch18-11-explain-in-search',
    title: '实验 11 · explain:true:另一个入口',
    method: 'POST', path: '/tut-l18-dsl/_search?filter_path=hits.hits._id,hits.hits._score,hits.hits._explanation.description',
    body: { explain: true, query: { match: { title: 'quick brown' } } },
    predict: '"explain": true 和 _explain API 是一回事吗?',
    expect: '不是同一个入口:它是 _search body 上的开关,让每个 hit 多带一个 _explanation,内容与 _explain 同源思想。对照实验 9:_id 1 的描述应当对得上。两个入口都没被删。'
  };
  window.ESEXPERIMENTS['ch18-12-bool-filter'] = {
    version: 1, id: 'ch18-12-bool-filter',
    title: '实验 12 · must 管全文,filter 管条件',
    method: 'POST', path: '/tut-l18-dsl/_search?filter_path=hits.total,hits.hits._id,hits.hits._score',
    body: {
      query: {
        bool: {
          must: [{ match: { title: 'elasticsearch' } }],
          filter: [
            { term: { status: 'published' } },
            { range: { price: { lte: 50 } } }
          ]
        }
      }
    },
    predict: '谁被滤掉?_score 里有 status / price 的贡献吗?',
    expect: '_id 4(Elasticsearch in Action,published,39.99)。filter 只问「在不在」,不算分——_score 只来自 must 里的 match。状态、价格这类「只要是不是」的条件就该放这里。'
  };
  window.ESEXPERIMENTS['ch18-13-bool-must'] = {
    version: 1, id: 'ch18-13-bool-must',
    title: '实验 13 · 同一条件搬进 must:分数变了',
    method: 'POST', path: '/tut-l18-dsl/_search?filter_path=hits.total,hits.hits._id,hits.hits._score',
    body: {
      query: {
        bool: {
          must: [
            { match: { title: 'elasticsearch' } },
            { term: { status: 'published' } }
          ]
        }
      }
    },
    predict: 'hits 变吗?_score 变吗?',
    expect: 'hits 还是 _id 4,但 _score 与实验 12 不同:term status 也参与打分(常数的 term 分)。「必须命中」的集合一样,代价差在打分——这就是 filter 存在的理由,也是它有资格被缓存的前提。'
  };
  window.ESEXPERIMENTS['ch18-14-post-filter'] = {
    version: 1, id: 'ch18-14-post-filter',
    title: '实验 14 · post_filter:hits 瘦身,聚合不看',
    method: 'POST', path: '/tut-l18-dsl/_search?filter_path=hits.total,hits.hits._id,aggregations',
    body: {
      query: { match_all: {} },
      aggs: { by_status: { terms: { field: 'status' } } },
      post_filter: { term: { status: 'published' } }
    },
    predict: 'hits 是谁?聚合桶里还有 draft 吗?',
    expect: 'hits:1、3、4(只显示 published);by_status 桶里 draft: 1 仍在——聚合按 query 的文档集算,hits 排完序再滤一层。电商侧边栏「颜色聚合显示全部、列表只显示勾选」走这条;post_filter 不是第四种 Occur,也不是更快的 filter。'
  };
  window.ESEXPERIMENTS['ch18-15-match-keyword'] = {
    version: 1, id: 'ch18-15-match-keyword',
    title: '实验 15 · match 打在 keyword 上:短路整串',
    method: 'POST', path: '/tut-l18-dsl/_search?filter_path=hits.total',
    body: { query: { match: { status: 'published draft' } } },
    predict: 'match 会把 "published draft" 切成两个 token 吗?注意这是 keyword 字段。',
    expect: 'total: 0。keyword 的 search analyzer 就是 keyword analyzer,MatchQueryParser 走短路:直接 TermQuery 整串——词典里没有 "published draft"。match 不是「永远切词」,是「用字段的 search analyzer」;字段一换,match/term 的胜负对调(思考题 1)。'
  };
  window.ESEXPERIMENTS['ch18-16-phrase-right'] = {
    version: 1, id: 'ch18-16-phrase-right',
    title: '实验 16 · match_phrase "quick brown":要相邻',
    method: 'POST', path: '/tut-l18-dsl/_search?filter_path=hits.total,hits.hits._id',
    body: { query: { match_phrase: { title: 'quick brown' } } },
    predict: 'quick 和 brown 在两篇里都相邻吗?',
    expect: '_id 1、2:两篇里 quick、brown 都位置相邻。match_phrase 同样先分析(token 相同),但建的是 PhraseQuery——除了「都在」,还要求位置挨着(slop 默认 0)。'
  };
  window.ESEXPERIMENTS['ch18-17-phrase-wrong'] = {
    version: 1, id: 'ch18-17-phrase-wrong',
    title: '实验 17 · match_phrase "brown quick":顺序反了',
    method: 'POST', path: '/tut-l18-dsl/_search?filter_path=hits.total',
    body: { query: { match_phrase: { title: 'brown quick' } } },
    predict: '同样的两个词、顺序反过来?',
    expect: 'total: 0。词都在,但位置不相邻(顺序也反)——PhraseQuery 的 slop=0 不让步。对照实验 8:AND 只要都在,phrase 还要挨着;三档严格度:SHOULD < MUST < PHRASE。'
  };
  window.ESEXPERIMENTS['ch18-18-cleanup'] = {
    version: 1, id: 'ch18-18-cleanup',
    title: '清理 · 删除 tut-l18-dsl',
    method: 'DELETE', path: '/tut-l18-dsl',
    predict: '一个词总结本课?',
    expect: 'acknowledged: true。「进倒排之前变没变」——match 变(token),term 不变(整串);must 算分,filter 不算。'
  };
})();
