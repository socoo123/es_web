/* experiments/ch20.js — 第 20 课:评分与排序实验 + BM25 手算演算动画(旗舰) */
(function () {
  'use strict';

  /* ===== 动画:两个词、两篇文档,BM25 现场演算 ===== */
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

  /* 步骤 1:语料与集合统计 */
  function step1() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">';
    s += rect(15, 20, 355, 110, 'fig-box');
    s += txt(192, 44, 'Doc a · dl=2', 'fig-name');
    s += txt(192, 72, '"elasticsearch tutorial"', 'fig-key');
    s += txt(192, 98, 'es TF=1 · tut TF=1 · views 10', 'fig-sub');
    s += rect(390, 20, 355, 110, 'fig-box');
    s += txt(567, 44, 'Doc b · dl=2', 'fig-name');
    s += txt(567, 72, '"elasticsearch elasticsearch"', 'fig-key');
    s += txt(567, 98, 'es TF=2 · tut TF=0 · views 100', 'fig-sub');
    s += rect(15, 152, 730, 64, 'fig-box-hot', 'fp-pop');
    s += txt(380, 176, '集合统计(单 shard)', 'fig-name');
    s += txt(380, 202, 'N=2 · avgdl=2 · DF(es)=2 · DF(tut)=1', 'fig-key');
    s += txt(380, 250, '两篇 dl 都等于 avgdl:长度归一化项=1,先不干扰 TF', 'fig-sub');
    s += txt(380, 276, '本例仅搜一个 shard,含 title 的 N=2,与 explain 对照', 'fig-sub');
    return s + '</svg>';
  }

  /* 步骤 2:公式登场 */
  function step2() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">';
    s += rect(15, 20, 730, 64, 'fig-box');
    s += txt(380, 44, 'Legacy BM25(手算形式)', 'fig-name');
    s += txt(380, 70, 'score = Σ IDF(qi) × tf_sat(TF(qi, D))', 'fig-key');
    s += rect(15, 110, 355, 70, 'fig-box');
    s += txt(192, 136, 'tf_sat = freq×(k1+1)/(freq+k1)', 'fig-key');
    s += txt(192, 162, 'k1=1.2 · b=0.75 · dl=avgdl 时', 'fig-sub');
    s += rect(390, 110, 355, 70, 'fig-box');
    s += txt(567, 136, 'ES 的 Legacy 包装', 'fig-name');
    s += txt(567, 162, 'scorer 把 boost 乘上 (1+k1)', 'fig-sub');
    s += txt(380, 216, 'explain 里的 boost 是 2.2——不是查询 JSON 写了 2.2', 'fig-sub');
    s += txt(380, 244, '现代 Lucene 不再乘 coord:一篇的分 = 各匹配 term 相加', 'fig-sub');
    s += txt(380, 276, '本例默认 OR:匹配贡献相加,分数取决于具体统计', 'fig-sub');
    return s + '</svg>';
  }

  /* 步骤 3:IDF */
  function step3() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">';
    s += rect(15, 20, 355, 110, 'fig-box');
    s += txt(192, 44, 'IDF(elasticsearch)', 'fig-name');
    s += txt(192, 72, 'ln(1+(2-2+0.5)/(2+0.5))', 'fig-key');
    s += txt(192, 98, '= ln(1.2) ≈ 0.1823', 'fig-key');
    s += txt(192, 122, 'DF=2:两篇都有,不值钱', 'fig-sub');
    s += rect(390, 20, 355, 110, 'fig-box');
    s += txt(567, 44, 'IDF(tutorial)', 'fig-name');
    s += txt(567, 72, 'ln(1+(2-1+0.5)/(1+0.5))', 'fig-key');
    s += txt(567, 98, '= ln(2) ≈ 0.6931', 'fig-key');
    s += txt(567, 122, 'DF=1:只有 a 有,稀有词贵', 'fig-sub');
    s += rect(15, 152, 730, 56, 'fig-box-hot', 'fp-pop');
    s += txt(380, 176, '本例 IDF(tut) ≈ 3.8 × IDF(es)', 'fig-name');
    s += txt(380, 198, '0.693 vs 0.182', 'fig-key');
    s += txt(380, 240, 'IDF 依赖本 shard 的 N/n——字段统计变化可能改老文档分数', 'fig-sub');
    s += txt(380, 268, '默认 QTF 用各 shard 本地统计(第 16 课)', 'fig-sub');
    return s + '</svg>';
  }

  /* 步骤 4:TF 饱和 */
  function step4() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">';
    s += rect(15, 16, 355, 88, 'fig-box');
    s += txt(192, 44, 'TF=1', 'fig-name');
    s += txt(192, 74, 'tf_sat = 2.2/2.2 = 1.000', 'fig-key');
    s += rect(390, 16, 355, 88, 'fig-box');
    s += txt(567, 44, 'TF=2', 'fig-name');
    s += txt(567, 74, 'tf_sat = 4.4/3.2 = 1.375', 'fig-key');
    s += rect(15, 122, 355, 88, 'fig-box');
    s += txt(192, 150, 'TF=20', 'fig-name');
    s += txt(192, 180, 'tf_sat ≈ 2.075', 'fig-key');
    s += rect(390, 122, 355, 88, 'fig-box');
    s += txt(567, 150, 'TF=21', 'fig-name');
    s += txt(567, 180, 'tf_sat ≈ 2.081', 'fig-key');
    s += rect(15, 228, 730, 56, 'fig-box-hot', 'fp-pop');
    s += txt(380, 250, '「出现过」远大于「再堆一次」', 'fig-name');
    s += txt(380, 274, '1→2 增 37.5%;20→21 约增 0.3%,收益逐渐变小', 'fig-sub');
    return s + '</svg>';
  }

  /* 步骤 5:单词查询,b 赢 */
  function step5() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">';
    s += rect(15, 20, 730, 56, 'fig-box');
    s += txt(380, 42, '只搜 elasticsearch:单个 term', 'fig-name');
    s += txt(380, 64, 'TF 是唯一变量', 'fig-sub');
    s += rect(15, 96, 355, 90, 'fig-box');
    s += txt(192, 122, 'Doc a', 'fig-name');
    s += txt(192, 152, '0.1823 × 1.000 ≈ 0.182', 'fig-key');
    s += txt(192, 176, '出现一次', 'fig-sub');
    s += rect(390, 96, 355, 90, 'fig-box-hot');
    s += txt(567, 122, 'Doc b', 'fig-name');
    s += txt(567, 152, '0.1823 × 1.375 ≈ 0.251', 'fig-key');
    s += txt(567, 176, '出现两次,饱和只到 1.375', 'fig-sub');
    s += rect(15, 208, 730, 56, 'fig-box-hot', 'fp-pop');
    s += txt(380, 230, 'b 赢:堆两次仍在前', 'fig-name');
    s += txt(380, 254, '两倍 TF 换 1.375 倍贡献——饱和在拖后腿', 'fig-sub');
    return s + '</svg>';
  }

  /* 步骤 6:双词查询,a 翻盘 */
  function step6() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">';
    s += rect(15, 20, 730, 56, 'fig-box');
    s += txt(380, 42, '搜 elasticsearch tutorial:两个 SHOULD 相加', 'fig-name');
    s += txt(380, 64, '现代 Lucene 不乘 coord,直接加', 'fig-sub');
    s += rect(15, 96, 355, 90, 'fig-box-hot');
    s += txt(192, 122, 'Doc a', 'fig-name');
    s += txt(192, 152, '0.182 + 0.693 ≈ 0.875', 'fig-key');
    s += txt(192, 176, 'es、tut 都命中', 'fig-sub');
    s += rect(390, 96, 355, 90, 'fig-box');
    s += txt(567, 122, 'Doc b', 'fig-name');
    s += txt(567, 152, '0.251 + 0 ≈ 0.251', 'fig-key');
    s += txt(567, 176, 'tut 未命中,贡献 0', 'fig-sub');
    s += rect(15, 208, 730, 56, 'fig-box-hot', 'fp-pop');
    s += txt(380, 230, 'a 翻盘:稀有词压过重复词', 'fig-name');
    s += txt(380, 254, '本语料双词查询:a 的额外贡献胜过 b 的重复词', 'fig-sub');
    return s + '</svg>';
  }

  /* 步骤 7:Legacy 层与返回窗口 */
  function step7() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">';
    s += rect(15, 20, 355, 110, 'fig-box');
    s += txt(192, 44, 'Lucene BM25Similarity', 'fig-name');
    s += txt(192, 72, 'tf = freq/(freq+k1×norm)', 'fig-key');
    s += txt(192, 98, '分子里没有 (k1+1)', 'fig-sub');
    s += txt(192, 122, '同参数纯 BM25 的统一倍数不改次序', 'fig-sub');
    s += rect(390, 20, 355, 110, 'fig-box');
    s += txt(567, 44, 'LegacyBM25Similarity', 'fig-name');
    s += txt(567, 72, 'scorer: boost × (1+k1)', 'fig-key');
    s += txt(567, 98, '查询 boost=1 → Lucene 看到 2.2', 'fig-sub');
    s += txt(567, 122, '倍数折进 boost,公式不变', 'fig-sub');
    s += rect(15, 152, 730, 60, 'fig-box-hot', 'fp-pop');
    s += txt(380, 176, 'Query + 协调合并先选窗口', 'fig-name');
    s += txt(380, 200, '先选 Top-N;Fetch 可算 explain,不据此重排名', 'fig-sub');
    s += txt(380, 244, '手算用带 (k1+1) 的经典形式,正好对上 ES 的 _score', 'fig-sub');
    s += txt(380, 272, '对不上时先查:是不是用了裸 Lucene 的分数(差 2.2 倍)', 'fig-sub');
    return s + '</svg>';
  }

  window.ESFLOWS = window.ESFLOWS || {};
  window.ESFLOWS['ch20-bm25'] = {
    version: 1,
    id: 'ch20-bm25',
    title: 'BM25 现场演算:a 与 b 谁分高',
    speed: 2600,
    steps: [
      { svg: step1(), note: '语料只有两篇:a = "elasticsearch tutorial",b = "elasticsearch elasticsearch",dl 都是 2。单 shard、title 字段 N=2、avgdl=2,DF(es)=2、DF(tut)=1。长度归一化项恰好为 1,先不干扰 TF——玩具就是这么设计的。' },
      { svg: step2(), note: '一篇对一个查询的分 = 各匹配 term 的 IDF×tf_sat 相加(不再乘 coord)。tf_sat = freq×(k1+1)/(freq+k1),k1=1.2。ES 默认是 Legacy 包装:scorer 把 boost 乘上 (1+k1),explain 里 boost 显示 2.2。' },
      { svg: step3(), note: 'IDF = ln(1+(N-n+0.5)/(n+0.5)):es 两篇都有,ln(1.2)≈0.182;tut 只有 a 有,ln(2)≈0.693，两 IDF 的比约3.8。注意 IDF 依赖本 shard 的 N/n,字段统计变化可能改老文档分数。' },
      { svg: step4(), note: '饱和:TF=1 → 1.000,TF=2 → 1.375,TF=20 → 2.075,TF=21 → 2.081。1→2 增 37.5%,20→21 只剩 0.3%:出现过远大于再堆一次。这些值固定 dl=avgdl；实际加词也可能增加长度，不能保证排名。' },
      { svg: step5(), note: '只搜 elasticsearch:唯一变量是 TF。a ≈ 0.182,b ≈ 0.251——b 赢,但两倍 TF 只换来 1.375 倍贡献,饱和在拖后腿。' },
      { svg: step6(), note: '搜两个词:a = 0.182(es) + 0.693(tut) ≈ 0.875,b = 0.251 + 0 ≈ 0.251。a 翻盘:tutorial 的稀有度把只堆常见词的 b 远远甩开。同一语料,查询从一个 term 换成两个 SHOULD,胜负就换了。' },
      { svg: step7(), note: 'Lucene 的 tf 分子没有 (k1+1)；同参数纯 BM25 的统一倍数不改次序。ES 的 LegacyBM25Similarity 把它折进 boost(1×2.2),所以手算用经典形式正好对上 _score。Query 的局部 Top-N 还要由协调节点合并；Fetch可再算 explain，但不据此改排名。' }
    ]
  };

  /* ===== 实验：按 A → B → C → 点名清理运行 ===== */
  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};
  window.ESEXPERIMENTS["ch20-00-setup"] = {
  "version": 1,
  "id": "ch20-00-setup",
  "title": "A1 · 建 tut-l20-bm25（1主0副）",
  "method": "PUT",
  "path": "/tut-l20-bm25",
  "body": {
    "settings": {
      "number_of_shards": 1,
      "number_of_replicas": 0,
      "auto_expand_replicas": false,
      "refresh_interval": "-1",
      "requests.cache.enable": false,
      "default_pipeline": "_none",
      "final_pipeline": "_none",
      "mapping.source.mode": "stored"
    },
    "mappings": {
      "dynamic": "strict",
      "properties": {
        "title": {
          "type": "text",
          "analyzer": "standard",
          "similarity": "BM25",
          "norms": true,
          "term_vector": "with_positions_offsets"
        },
        "views": {
          "type": "integer",
          "doc_values": true
        }
      }
    }
  },
  "predict": "为什么坚持 1 个 shard?",
  "expect": "200 acknowledged/shards_acknowledged=true；显式 standard/BM25、norms 与 1 主 0 副。重复创建为 400 resource_already_exists_exception；从末尾点名清理后重建。自动 refresh=-1，后续写入显式 refresh=true。"
};
  window.ESEXPERIMENTS["ch20-12-health"] = {
  "version": 1,
  "id": "ch20-12-health",
  "title": "A2 · 等待本课唯一主分片就绪",
  "method": "GET",
  "path": "/_cluster/health/tut-l20-bm25?wait_for_status=green&wait_for_no_initializing_shards=true&timeout=30s",
  "predict": "为何不检查整个集群的健康？",
  "expect": "200 status=green、timed_out=false、active_primary_shards=1；如等待失败先检查本课索引，不继续依赖未就绪数据。"
};
  window.ESEXPERIMENTS["ch20-13-configuration"] = {
  "version": 1,
  "id": "ch20-13-configuration",
  "title": "A3 · 读回索引配置和 mapping",
  "method": "GET",
  "path": "/tut-l20-bm25?flat_settings=true",
  "predict": "节点版本与索引创建版本是同一个字段吗？",
  "expect": "读回1主0副、refresh_interval=-1、stored source、standard/BM25；mapping序列化省略默认true的norms/Doc Values，Explain和排序另作证据；version.created 是索引版本内部编号，不把它直接当节点语义版本。"
};
  window.ESEXPERIMENTS["ch20-01-bulk"] = {
  "version": 1,
  "id": "ch20-01-bulk",
  "title": "A4 · 两篇对照文档 a / b",
  "method": "POST",
  "path": "/tut-l20-bm25/_bulk?refresh=true",
  "body": "{\"index\":{\"_id\":\"a\"}}\n{\"title\":\"elasticsearch tutorial\",\"views\":10}\n{\"index\":{\"_id\":\"b\"}}\n{\"title\":\"elasticsearch elasticsearch\",\"views\":100}\n",
  "predict": "a、b 的 title 各切出什么 token?TF 各是多少?",
  "expect": "200 errors=false，首次两项 created/201；重复同 ID 是 updated/200，不增加活文档数，但旧删除版本可能暂留段统计。准确重现 N=2 应清理重建，而非重写旧索引。refresh=true 后搜索可见。"
};
  window.ESEXPERIMENTS["ch20-14-termvectors"] = {
  "version": 1,
  "id": "ch20-14-termvectors",
  "title": "A5 · 词向量核对 TF 与字段统计",
  "method": "POST",
  "path": "/tut-l20-bm25/_mtermvectors",
  "predict": "TF、DF和title.doc_count分别数什么？",
  "expect": "a:es/tutorial频次1/1；b:es频次2；title字段doc_count=2、sum_ttf=4，es doc_freq=2、tutorial=1。本字段显式保存词向量；统计是分片局部且不保证剔除已删版本。",
  "body": {
    "ids": [
      "a",
      "b"
    ],
    "parameters": {
      "fields": [
        "title"
      ],
      "term_statistics": true,
      "field_statistics": true,
      "positions": true,
      "offsets": true
    }
  }
};
  window.ESEXPERIMENTS["ch20-02-match-one"] = {
  "version": 1,
  "id": "ch20-02-match-one",
  "title": "A6 · 单词查询：b 赢（TF 唯一变量）",
  "method": "POST",
  "path": "/tut-l20-bm25/_search?filter_path=hits.hits._id,hits.hits._score",
  "body": {
    "query": {
      "match": {
        "title": "elasticsearch"
      }
    }
  },
  "predict": "b 的 TF 是 a 的两倍——分数也是两倍吗?谁在前?",
  "expect": "两篇初始语料：b=0.25069216、a=0.18232156（允许浮点尾差），次序 b/a；同长度、同 IDF，TF 2/1 的贡献比 1.375。运行 C 组或重写后请先清理重建。"
};
  window.ESEXPERIMENTS["ch20-03-match-two"] = {
  "version": 1,
  "id": "ch20-03-match-two",
  "title": "A7 · 双词查询：a 翻盘",
  "method": "POST",
  "path": "/tut-l20-bm25/_search?filter_path=hits.hits._id,hits.hits._score",
  "body": {
    "query": {
      "match": {
        "title": "elasticsearch tutorial"
      }
    }
  },
  "predict": "同一批文档,加上 tutorial 之后谁在前?",
  "expect": "初始语料次序 a/b；a≈0.8754687，b≈0.25069216。默认 OR 对应两个 SHOULD 的贡献相加；本例 tutorial 的稀有贡献使 a 翻盘，不是任意稀有词都保证获胜。"
};
  window.ESEXPERIMENTS["ch20-04-explain-search"] = {
  "version": 1,
  "id": "ch20-04-explain-search",
  "title": "A8 · explain:true 对上公式",
  "method": "POST",
  "path": "/tut-l20-bm25/_search?filter_path=hits.hits._id,hits.hits._score,hits.hits._explanation",
  "body": {
    "explain": true,
    "query": {
      "match": {
        "title": "elasticsearch"
      }
    }
  },
  "predict": "解释树里的 boost 是 1.0 还是 2.2?idf 子节点的 n、N 是几?tf 描述里有 (k1+1) 吗?",
  "expect": "每个返回 hit 的 _explanation.value≈_score。boost=2.2、n=N=2，k1=1.2、b=0.75、dl=avgdl=2；解释树 tf 不含 (k1+1)，倍数在 boost。搜索解释在 Fetch 按返回 hit 计算，不重新决定窗口。"
};
  window.ESEXPERIMENTS["ch20-05-explain-api"] = {
  "version": 1,
  "id": "ch20-05-explain-api",
  "title": "A9 · POST _explain/a：指定文档",
  "method": "POST",
  "path": "/tut-l20-bm25/_explain/a",
  "body": {
    "query": {
      "match": {
        "title": "elasticsearch"
      }
    }
  },
  "predict": "响应里有 hits[] 吗?顶层 value 和 A8 里 a 的分数什么关系?",
  "expect": "200 matched=true，explanation.value≈0.18232156；树与同语料普通 search 中 a 一致。浏览器不发送 GET body，改用 POST。存在但不匹配见 A11；不存在见 A12；只看已刷新读者。"
};
  window.ESEXPERIMENTS["ch20-15-explain-window"] = {
  "version": 1,
  "id": "ch20-15-explain-window",
  "title": "A10 · size=1 只解释返回的一篇",
  "method": "POST",
  "path": "/tut-l20-bm25/_search",
  "predict": "命中2篇，为什么只看到一棵解释树？",
  "expect": "hits.total=2但hits.hits只有a，带_explanation≈0.8754687；b没进窗口。Fetch解释返回hit；独立_explain仍可指定b。",
  "body": {
    "size": 1,
    "explain": true,
    "query": {
      "match": {
        "title": "elasticsearch tutorial"
      }
    }
  }
};
  window.ESEXPERIMENTS["ch20-16-explain-nonmatch"] = {
  "version": 1,
  "id": "ch20-16-explain-nonmatch",
  "title": "A11 · 文档存在但查询不匹配",
  "method": "POST",
  "path": "/tut-l20-bm25/_explain/b",
  "predict": "不匹配会回404吗？",
  "expect": "200 matched=false、explanation.value=0；文档存在而查询不匹配，和A12资源缺失不同。",
  "body": {
    "query": {
      "match": {
        "title": "tutorial"
      }
    }
  }
};
  window.ESEXPERIMENTS["ch20-17-explain-missing"] = {
  "version": 1,
  "id": "ch20-17-explain-missing",
  "title": "A12 · 缺失文档的 explain",
  "method": "POST",
  "path": "/tut-l20-bm25/_explain/missing",
  "predict": "缺失ID与matched=false如何区分？",
  "expect": "404，_id=missing、matched=false，通常不带explanation；索引仍在且可继续B组，无需修复文档。",
  "body": {
    "query": {
      "match": {
        "title": "elasticsearch"
      }
    }
  }
};
  window.ESEXPERIMENTS["ch20-06-func-score"] = {
  "version": 1,
  "id": "ch20-06-func-score",
  "title": "B1 · function_score weight2：分数翻倍",
  "method": "POST",
  "path": "/tut-l20-bm25/_search?filter_path=hits.hits._id,hits.hits._score",
  "body": {
    "query": {
      "function_score": {
        "query": {
          "match": {
            "title": "elasticsearch"
          }
        },
        "functions": [
          {
            "weight": 2
          }
        ],
        "boost_mode": "multiply"
      }
    }
  },
  "predict": "b 的分数会变吗?名次会变吗?",
  "expect": "初始语料 b≈0.5013843、a≈0.36464313，约为 A6 两倍、顺序仍 b/a。同一正数倍数不改次序；multiply 还受 max_boost 裁剪，此处默认上限未触发。"
};
  window.ESEXPERIMENTS["ch20-18-function-views"] = {
  "version": 1,
  "id": "ch20-18-function-views",
  "title": "B2 · 把 views 乘入相关性分",
  "method": "POST",
  "path": "/tut-l20-bm25/_search",
  "predict": "乘积中还有BM25，a一定保持第一吗？",
  "expect": "b≈25.069216、a≈8.754687，b翻到第一。乘积混合两项，不保证相关性为主；此例views都正、无缺值且不触发max_boost。",
  "body": {
    "query": {
      "function_score": {
        "query": {
          "match": {
            "title": "elasticsearch tutorial"
          }
        },
        "field_value_factor": {
          "field": "views",
          "factor": 1,
          "modifier": "none",
          "missing": 1
        },
        "boost_mode": "multiply"
      }
    }
  }
};
  window.ESEXPERIMENTS["ch20-19-function-zero"] = {
  "version": 1,
  "id": "ch20-19-function-zero",
  "title": "B3 · 命中 b 的函数权重为零",
  "method": "POST",
  "path": "/tut-l20-bm25/_search",
  "predict": "查询仍命中b，零权重还能保住高排名吗？",
  "expect": "a≈0.18232156在前，b=0在后（未设min_score，仍返回）。函数乘零可让相关文档失去高排名；未匹配函数的a使用因子1。",
  "body": {
    "query": {
      "function_score": {
        "query": {
          "match": {
            "title": "elasticsearch"
          }
        },
        "functions": [
          {
            "filter": {
              "ids": {
                "values": [
                  "b"
                ]
              }
            },
            "weight": 0
          }
        ],
        "boost_mode": "multiply"
      }
    }
  }
};
  window.ESEXPERIMENTS["ch20-20-function-replace"] = {
  "version": 1,
  "id": "ch20-20-function-replace",
  "title": "B4 · replace 只保留函数结果",
  "method": "POST",
  "path": "/tut-l20-bm25/_search",
  "predict": "所有函数分都为2，BM25还能打破并列吗？",
  "expect": "两篇_score都为2，仍由query决定匹配集合；不要断言并列顺序。replace在分数域工作，未自动变成Doc Values字段排序。",
  "body": {
    "query": {
      "function_score": {
        "query": {
          "match": {
            "title": "elasticsearch tutorial"
          }
        },
        "functions": [
          {
            "weight": 2
          }
        ],
        "boost_mode": "replace"
      }
    }
  }
};
  window.ESEXPERIMENTS["ch20-07-sort-views"] = {
  "version": 1,
  "id": "ch20-07-sort-views",
  "title": "B5 · views desc：字段比较键",
  "method": "POST",
  "path": "/tut-l20-bm25/_search?filter_path=hits.hits._id,hits.hits._score,hits.hits.sort",
  "body": {
    "query": {
      "match": {
        "title": "elasticsearch tutorial"
      }
    },
    "sort": [
      {
        "views": "desc"
      }
    ]
  },
  "predict": "双词查询 BM25 冠军是 a——加了 sort 之后谁在前?_score 还在吗?",
  "expect": "次序 b/a，sort=[100]/[10]，_score=null；纯 views 排序不需要分数决定次序。字段 Doc Values 是排序输入；是否还有其他组件需要分数要看请求，不可一概说完全不计算。"
};
  window.ESEXPERIMENTS["ch20-08-track-scores"] = {
  "version": 1,
  "id": "ch20-08-track-scores",
  "title": "B6 · track_scores：旁路看分数",
  "method": "POST",
  "path": "/tut-l20-bm25/_search?filter_path=hits.hits._id,hits.hits._score,hits.hits.sort",
  "body": {
    "track_scores": true,
    "query": {
      "match": {
        "title": "elasticsearch tutorial"
      }
    },
    "sort": [
      {
        "views": "desc"
      }
    ]
  },
  "predict": "_score 回来了,顺序会跟着分数走吗?",
  "expect": "仍 b/a、sort=[100]/[10]；_score≈0.25069216/0.8754687。track_scores=true 补回分数，不把它加入排序键。"
};
  window.ESEXPERIMENTS["ch20-21-sort-score"] = {
  "version": 1,
  "id": "ch20-21-sort-score",
  "title": "B7 · 显式 _score 降序",
  "method": "POST",
  "path": "/tut-l20-bm25/_search",
  "predict": "写了sort就一定不按分数吗？",
  "expect": "a/b、_score≈0.8754687/0.25069216；本请求只有_score desc，buildSort优化为默认路径，响应不带sort数组。特殊分数排序不等于业务字段排序。",
  "body": {
    "query": {
      "match": {
        "title": "elasticsearch tutorial"
      }
    },
    "sort": [
      {
        "_score": "desc"
      }
    ]
  }
};
  window.ESEXPERIMENTS["ch20-22-rescore-window1"] = {
  "version": 1,
  "id": "ch20-22-rescore-window1",
  "title": "B8 · rescore 窗口 1",
  "method": "POST",
  "path": "/tut-l20-bm25/_search",
  "predict": "a包含完整短语，但进入重打窗口了吗？",
  "expect": "window=1只重打首轮b，b不匹配短语，a无二次查询贡献，仍b/a。",
  "body": {
    "size": 2,
    "explain": true,
    "query": {
      "match": {
        "title": "elasticsearch"
      }
    },
    "rescore": {
      "window_size": 1,
      "query": {
        "rescore_query": {
          "match_phrase": {
            "title": "elasticsearch tutorial"
          }
        },
        "query_weight": 1,
        "rescore_query_weight": 5,
        "score_mode": "total"
      }
    }
  }
};
  window.ESEXPERIMENTS["ch20-23-rescore-window2"] = {
  "version": 1,
  "id": "ch20-23-rescore-window2",
  "title": "B9 · rescore 窗口 2",
  "method": "POST",
  "path": "/tut-l20-bm25/_search",
  "predict": "a包含完整短语，但进入重打窗口了吗？",
  "expect": "window=2两篇都重打；a匹配短语后≈4.559665，b≈0.25069216，变a/b。Explain包含重打解释；window是每分片，不是全局窗口。",
  "body": {
    "size": 2,
    "explain": true,
    "query": {
      "match": {
        "title": "elasticsearch"
      }
    },
    "rescore": {
      "window_size": 2,
      "query": {
        "rescore_query": {
          "match_phrase": {
            "title": "elasticsearch tutorial"
          }
        },
        "query_weight": 1,
        "rescore_query_weight": 5,
        "score_mode": "total"
      }
    }
  }
};
  window.ESEXPERIMENTS["ch20-24-rescore-score-sort"] = {
  "version": 1,
  "id": "ch20-24-rescore-score-sort",
  "title": "B10 · rescore 允许 _score desc",
  "method": "POST",
  "path": "/tut-l20-bm25/_search",
  "predict": "rescore是不是禁止一切sort？",
  "expect": "200，a/b、分数与B9一致；单_score desc优化为默认收集，本例无sort数组。9.4.0允许_score降序；源码另允许升序_shard_doc作tie-break，此处只实测单_score。",
  "body": {
    "size": 2,
    "query": {
      "match": {
        "title": "elasticsearch"
      }
    },
    "sort": [
      {
        "_score": "desc"
      }
    ],
    "rescore": {
      "window_size": 2,
      "query": {
        "rescore_query": {
          "match_phrase": {
            "title": "elasticsearch tutorial"
          }
        },
        "query_weight": 1,
        "rescore_query_weight": 5,
        "score_mode": "total"
      }
    }
  }
};
  window.ESEXPERIMENTS["ch20-25-rescore-field-sort"] = {
  "version": 1,
  "id": "ch20-25-rescore-field-sort",
  "title": "B11 · rescore 拒绝 views 排序",
  "method": "POST",
  "path": "/tut-l20-bm25/_search",
  "predict": "哪条限制真正触发？",
  "expect": "400，reason含Cannot use [sort] option in conjunction with [rescore]。因views不是允许的_score降序；错误只影响本次请求，不改索引，继续B12。",
  "body": {
    "query": {
      "match": {
        "title": "elasticsearch"
      }
    },
    "sort": [
      {
        "views": "desc"
      }
    ],
    "rescore": {
      "window_size": 2,
      "query": {
        "rescore_query": {
          "match_phrase": {
            "title": "elasticsearch tutorial"
          }
        },
        "query_weight": 1,
        "rescore_query_weight": 5,
        "score_mode": "total"
      }
    }
  }
};
  window.ESEXPERIMENTS["ch20-26-baseline-again"] = {
  "version": 1,
  "id": "ch20-26-baseline-again",
  "title": "B12 · 回到普通查询核对配置未改",
  "method": "POST",
  "path": "/tut-l20-bm25/_search",
  "predict": "局部function_score、sort与rescore会写回索引吗？",
  "expect": "仍b≈0.25069216、a≈0.18232156；B组只是请求局部选项，无持久字段/Similarity配置变更。",
  "body": {
    "query": {
      "match": {
        "title": "elasticsearch"
      }
    }
  }
};
  window.ESEXPERIMENTS["ch20-09-add-doc"] = {
  "version": 1,
  "id": "ch20-09-add-doc",
  "title": "C1 · 新增含 title 的不匹配文档",
  "method": "PUT",
  "path": "/tut-l20-bm25/_doc/c?refresh=true",
  "body": {
    "title": "unrelated document",
    "views": 1
  },
  "predict": "c 不含 elasticsearch——它会影响 a、b 的分数吗?",
  "expect": "首次 201 created；c 含两个不匹配词，显式刷新后 title.docCount=3、es.docFreq=2、avgdl仍2。重复是 200 updated，精确统计需清理重建；本卡只应在 C1 位置运行一次。"
};
  window.ESEXPERIMENTS["ch20-10-score-changed"] = {
  "version": 1,
  "id": "ch20-10-score-changed",
  "title": "C2 · 同查询：老文档分数变大",
  "method": "POST",
  "path": "/tut-l20-bm25/_search?filter_path=hits.hits._id,hits.hits._score",
  "body": {
    "query": {
      "match": {
        "title": "elasticsearch"
      }
    }
  },
  "predict": "同样的查询,a、b 的分数变大、变小还是不变?",
  "expect": "b≈0.646255、a≈0.4700036；IDF变为ln(1.6)，长度和 TF 因子不变。仅本例新增文档含 title 且长度2，不能推广成任何写入都涨分。"
};
  window.ESEXPERIMENTS["ch20-27-statistics-changed"] = {
  "version": 1,
  "id": "ch20-27-statistics-changed",
  "title": "C3 · explain 读出新 N/n/avgdl",
  "method": "POST",
  "path": "/tut-l20-bm25/_explain/a",
  "predict": "分数升高来自词频还是集合？",
  "expect": "200，boost2.2、n2/N3、dl2/avgdl2、value≈0.4700036；旧文档没改，刷新后的字段集合统计改变。",
  "body": {
    "query": {
      "match": {
        "title": "elasticsearch"
      }
    }
  }
};
  window.ESEXPERIMENTS["ch20-28-missing-title"] = {
  "version": 1,
  "id": "ch20-28-missing-title",
  "title": "C4 · 加一篇没有 title 的文档",
  "method": "PUT",
  "path": "/tut-l20-bm25/_doc/d?refresh=true",
  "predict": "索引总篇数变4，title的N也必变4吗？",
  "expect": "首次201 created，d没有title、不匹配本课词。N是含该字段词项的docCount，不是索引总文档数。重复200 updated；从干净前提只执行一次。",
  "body": {
    "views": 7
  }
};
  window.ESEXPERIMENTS["ch20-29-field-doccount"] = {
  "version": 1,
  "id": "ch20-29-field-doccount",
  "title": "C5 · 缺字段文档不改变本例 N",
  "method": "POST",
  "path": "/tut-l20-bm25/_explain/a",
  "predict": "对照C3，a的分数变了吗？",
  "expect": "仍≈0.4700036、n2/N3、avgdl2；title缺失的d没有进入该字段统计。一般写入影响还取决于刷新、字段内容、长度、分片和删除版本。",
  "body": {
    "query": {
      "match": {
        "title": "elasticsearch"
      }
    }
  }
};
  window.ESEXPERIMENTS["ch20-11-cleanup"] = {
  "version": 1,
  "id": "ch20-11-cleanup",
  "title": "清理 · 删除 tut-l20-bm25",
  "method": "DELETE",
  "path": "/tut-l20-bm25",
  "predict": "一句话总结本课?",
  "expect": "200 acknowledged=true，删除本课唯一索引 tut-l20-bm25。重复删除404 index_not_found_exception。完整重做：清理→A1–A12→B1–B12→C1–C5→清理；本轮两次完整运行另有真实记录。"
};
})();
