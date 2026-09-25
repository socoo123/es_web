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
    s += txt(380, 276, '单 shard 让本地统计就是全局统计,手算才能对上 explain', 'fig-sub');
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
    s += txt(380, 276, '两个 SHOULD:中一个进候选,两个都中分更高(第 18 课)', 'fig-sub');
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
    s += txt(380, 176, '稀有词一个 ≈ 常见词四个', 'fig-name');
    s += txt(380, 198, '0.693 vs 0.182', 'fig-key');
    s += txt(380, 240, 'IDF 依赖本 shard 的 N/n——写入新文档会改老文档的分数', 'fig-sub');
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
    s += txt(380, 274, '1→2 增 37.5%;20→21 只增 0.3%——堆砌买不到排名', 'fig-sub');
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
    s += txt(380, 254, '重复堆常见词,赢不了多命中一个稀有词', 'fig-sub');
    return s + '</svg>';
  }

  /* 步骤 7:Legacy 层与「名次已定」 */
  function step7() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">';
    s += rect(15, 20, 355, 110, 'fig-box');
    s += txt(192, 44, 'Lucene BM25Similarity', 'fig-name');
    s += txt(192, 72, 'tf = freq/(freq+k1×norm)', 'fig-key');
    s += txt(192, 98, '分子里没有 (k1+1)', 'fig-sub');
    s += txt(192, 122, '常数不改变排序,被拿掉了', 'fig-sub');
    s += rect(390, 20, 355, 110, 'fig-box');
    s += txt(567, 44, 'LegacyBM25Similarity', 'fig-name');
    s += txt(567, 72, 'scorer: boost × (1+k1)', 'fig-key');
    s += txt(567, 98, '查询 boost=1 → Lucene 看到 2.2', 'fig-sub');
    s += txt(567, 122, '倍数折进 boost,公式不变', 'fig-sub');
    s += rect(15, 152, 730, 60, 'fig-box-hot', 'fp-pop');
    s += txt(380, 176, '名次在 Query 阶段就定了', 'fig-name');
    s += txt(380, 200, '(docId, score) 回协调节点截窗口;Fetch 不算分,只搬赢家', 'fig-sub');
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
      { svg: step1(), note: '语料只有两篇:a = "elasticsearch tutorial",b = "elasticsearch elasticsearch",dl 都是 2。单 shard、N=2、avgdl=2,DF(es)=2、DF(tut)=1。长度归一化项恰好为 1,先不干扰 TF——玩具就是这么设计的。' },
      { svg: step2(), note: '一篇对一个查询的分 = 各匹配 term 的 IDF×tf_sat 相加(不再乘 coord)。tf_sat = freq×(k1+1)/(freq+k1),k1=1.2。ES 默认是 Legacy 包装:scorer 把 boost 乘上 (1+k1),explain 里 boost 显示 2.2。' },
      { svg: step3(), note: 'IDF = ln(1+(N-n+0.5)/(n+0.5)):es 两篇都有,ln(1.2)≈0.182;tut 只有 a 有,ln(2)≈0.693——稀有词一个顶常见词四个。注意 IDF 依赖本 shard 的 N/n,写入新文档会改老文档的分数。' },
      { svg: step4(), note: '饱和:TF=1 → 1.000,TF=2 → 1.375,TF=20 → 2.075,TF=21 → 2.081。1→2 增 37.5%,20→21 只剩 0.3%:出现过远大于再堆一次。若按线性加,堆 21 次比 1 次高 21 倍,关键词堆砌直接买到排名。' },
      { svg: step5(), note: '只搜 elasticsearch:唯一变量是 TF。a ≈ 0.182,b ≈ 0.251——b 赢,但两倍 TF 只换来 1.375 倍贡献,饱和在拖后腿。' },
      { svg: step6(), note: '搜两个词:a = 0.182(es) + 0.693(tut) ≈ 0.875,b = 0.251 + 0 ≈ 0.251。a 翻盘:tutorial 的稀有度把只堆常见词的 b 远远甩开。同一语料,查询从一个 term 换成两个 SHOULD,胜负就换了。' },
      { svg: step7(), note: 'Lucene 的 tf 分子没有 (k1+1)(常数不改变排序);ES 的 LegacyBM25Similarity 把它折进 boost(1×2.2),所以手算用经典形式正好对上 _score。名次在 Query 阶段就定:Fetch 不再算分,只搬运已经赢了的正文。' }
    ]
  };

  /* ===== 实验 ===== */
  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};

  window.ESEXPERIMENTS['ch20-00-setup'] = {
    version: 1, id: 'ch20-00-setup',
    title: '实验 0 · 建 tut-l20-bm25(1 shard)',
    method: 'PUT', path: '/tut-l20-bm25',
    body: {
      settings: { number_of_shards: 1, number_of_replicas: 0 },
      mappings: { properties: { title: { type: 'text' }, views: { type: 'integer' } } }
    },
    predict: '为什么坚持 1 个 shard?',
    expect: 'acknowledged: true。默认 query_then_fetch 用各 shard 本地 IDF——单 shard 时本地就是全局,手算才能和 explain 对上(第 16 课的伏笔)。'
  };
  window.ESEXPERIMENTS['ch20-01-bulk'] = {
    version: 1, id: 'ch20-01-bulk',
    title: '实验 1 · 两篇对照文档 a / b',
    method: 'POST', path: '/tut-l20-bm25/_bulk?refresh=true',
    body: '{"index":{"_id":"a"}}\n{"title":"elasticsearch tutorial","views":10}\n{"index":{"_id":"b"}}\n{"title":"elasticsearch elasticsearch","views":100}\n',
    predict: 'a、b 的 title 各切出什么 token?TF 各是多少?',
    expect: 'errors: false。a:es×1 + tut×1(dl=2);b:es×2(dl=2)。refresh=true 让 SEARCH 立刻可见(第 16 课:SEARCH 只看已 refresh 的 searcher)。'
  };
  window.ESEXPERIMENTS['ch20-02-match-one'] = {
    version: 1, id: 'ch20-02-match-one',
    title: '实验 2 · 单词查询:b 赢(TF 唯一变量)',
    method: 'POST', path: '/tut-l20-bm25/_search?filter_path=hits.hits._id,hits.hits._score',
    body: { query: { match: { title: 'elasticsearch' } } },
    predict: 'b 的 TF 是 a 的两倍——分数也是两倍吗?谁在前?',
    expect: 'b ≈ 0.2507 在前,a ≈ 0.1823 在后。两倍 TF 只换来 1.375 倍贡献:饱和项 tf_sat(1)=1.000、tf_sat(2)=1.375,k1=1.2 在拖后腿。IDF 两篇相同(ln(1.2)≈0.1823,DF=2)。'
  };
  window.ESEXPERIMENTS['ch20-03-match-two'] = {
    version: 1, id: 'ch20-03-match-two',
    title: '实验 3 · 双词查询:a 翻盘(稀有词压重复词)',
    method: 'POST', path: '/tut-l20-bm25/_search?filter_path=hits.hits._id,hits.hits._score',
    body: { query: { match: { title: 'elasticsearch tutorial' } } },
    predict: '同一批文档,加上 tutorial 之后谁在前?',
    expect: 'a ≈ 0.8755(0.1823 + 0.6931,两个 SHOULD 相加)、b ≈ 0.2507(tut 未命中贡献 0)。tutorial DF=1、IDF=ln(2)≈0.693,一个稀有词顶四个常见词——重复堆 elasticsearch 赢不了。对照实验 2:查询从一个 term 换成两个 SHOULD,胜负就换了。'
  };
  window.ESEXPERIMENTS['ch20-04-explain-search'] = {
    version: 1, id: 'ch20-04-explain-search',
    title: '实验 4 · explain:true:对上公式',
    method: 'POST', path: '/tut-l20-bm25/_search?filter_path=hits.hits._id,hits.hits._score,hits.hits._explanation',
    body: { explain: true, query: { match: { title: 'elasticsearch' } } },
    predict: '解释树里的 boost 是 1.0 还是 2.2?idf 子节点的 n、N 是几?tf 描述里有 (k1+1) 吗?',
    expect: 'boost = 2.2(= 1 × (1+k1),LegacyBM25Similarity 折进去的,查询没写 boost);idf 节点 n=2、N=2,value ≈ 0.1823;tf 描述形如 freq/(freq + k1×(1-b+b×dl/avgdl)),没有 (k1+1)——倍数在 boost 里。_explanation.value 等于该 hit 的 _score。它是 Fetch 子阶段:只解释进了窗口的 hit。'
  };
  window.ESEXPERIMENTS['ch20-05-explain-api'] = {
    version: 1, id: 'ch20-05-explain-api',
    title: '实验 5 · _explain/a:另一个入口',
    method: 'GET', path: '/tut-l20-bm25/_explain/a?filter_path=matched,explanation.value,explanation.description',
    body: { query: { match: { title: 'elasticsearch' } } },
    predict: '响应里有 hits[] 吗?顶层 value 和实验 4 里 a 的分数什么关系?',
    expect: 'matched: true,顶层 explanation.value 与实验 4 中 a 的那份一致——同一棵 Lucene explain 树。但响应没有 hits[]:它按 _id 路由到单个 shard(像 GET,不像 SEARCH),根本不做 Query Then Fetch,哪怕这篇排在第 10000 名也能解释。'
  };
  window.ESEXPERIMENTS['ch20-06-func-score'] = {
    version: 1, id: 'ch20-06-func-score',
    title: '实验 6 · function_score weight=2:分数翻倍',
    method: 'POST', path: '/tut-l20-bm25/_search?filter_path=hits.hits._id,hits.hits._score',
    body: {
      query: {
        function_score: {
          query: { match: { title: 'elasticsearch' } },
          functions: [{ weight: 2 }],
          boost_mode: 'multiply'
        }
      }
    },
    predict: 'b 的分数会变吗?名次会变吗?',
    expect: 'b ≈ 0.501、a ≈ 0.365——都是实验 2 的 2 倍,顺序仍是 b、a。boost_mode 默认就是 multiply:乘的是已算完的 BM25,不动 IDF/TF;两篇同乘,名次不变,只是绝对值翻倍。业务上「同样相关,浏览量高的往前」要靠 field_value_factor,不只是常数 weight。'
  };
  window.ESEXPERIMENTS['ch20-07-sort-views'] = {
    version: 1, id: 'ch20-07-sort-views',
    title: '实验 7 · sort views desc:换掉截窗口的尺子',
    method: 'POST', path: '/tut-l20-bm25/_search?filter_path=hits.hits._id,hits.hits._score,hits.hits.sort',
    body: { query: { match: { title: 'elasticsearch tutorial' } }, sort: [{ views: 'desc' }] },
    predict: '双词查询 BM25 冠军是 a——加了 sort 之后谁在前?_score 还在吗?',
    expect: 'b 在前(sort: [100])、a 在后([10]);_score 是 null。写字段 sort 后收集器换成 TopFieldCollectorManager,读 Doc Values,BM25 冠军 a 若窗口小就根本不被 Fetch——sort 改的是 Query 阶段截 Top-N 的键,不是 Fetch 的装饰。'
  };
  window.ESEXPERIMENTS['ch20-08-track-scores'] = {
    version: 1, id: 'ch20-08-track-scores',
    title: '实验 8 · track_scores:true:旁路看 BM25',
    method: 'POST', path: '/tut-l20-bm25/_search?filter_path=hits.hits._id,hits.hits._score,hits.hits.sort',
    body: { track_scores: true, query: { match: { title: 'elasticsearch tutorial' } }, sort: [{ views: 'desc' }] },
    predict: '_score 回来了,顺序会跟着分数走吗?',
    expect: '_score 回到实验 3 的那对数字(b ≈ 0.251、a ≈ 0.875),但顺序仍按 views(b 在前)。track_scores 让分数「旁路可见」,不改变名次键——分数算给谁看,和分数决定谁在前面,是两件事。'
  };
  window.ESEXPERIMENTS['ch20-09-add-doc'] = {
    version: 1, id: 'ch20-09-add-doc',
    title: '实验 9 · 加一篇不含查询词的文档',
    method: 'PUT', path: '/tut-l20-bm25/_doc/c?refresh=true',
    body: { title: 'unrelated document', views: 1 },
    predict: 'c 不含 elasticsearch——它会影响 a、b 的分数吗?',
    expect: 'created。N 从 2 变 3,elasticsearch 的 n 仍是 2:词相对集合更稀有了。下一跑看老文档的分数怎么动——IDF 不是查询常量,是本 shard 的集合统计。'
  };
  window.ESEXPERIMENTS['ch20-10-score-changed'] = {
    version: 1, id: 'ch20-10-score-changed',
    title: '实验 10 · 老文档的分数变大了',
    method: 'POST', path: '/tut-l20-bm25/_search?filter_path=hits.hits._id,hits.hits._score',
    body: { query: { match: { title: 'elasticsearch' } } },
    predict: '同样的查询,a、b 的分数变大、变小还是不变?',
    expect: '变大:a ≈ 0.470、b ≈ 0.646(IDF 从 ln(1.2)≈0.182 升到 ln(1.6)≈0.470;TF 饱和项没变)。写入一篇不相干的文档,把老文档的查询分数抬高了——「同查询同分数」在 BM25 里不成立,统计变了分就变(默认 QTF 用 shard 本地统计,第 16 课)。'
  };
  window.ESEXPERIMENTS['ch20-11-cleanup'] = {
    version: 1, id: 'ch20-11-cleanup',
    title: '清理 · 删除 tut-l20-bm25',
    method: 'DELETE', path: '/tut-l20-bm25',
    predict: '一句话总结本课?',
    expect: 'acknowledged: true。名次在 Query 阶段就定:BM25(带 (k1+1) 的 Legacy 形式)算分,function_score 改分,sort 换尺子——Fetch 只搬赢家。'
  };
})();
