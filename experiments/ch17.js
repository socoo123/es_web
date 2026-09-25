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
    s += txt(380, 162, 'handler 在 DIRECT 上,立即转交', 'fig-sub');
    s += txt(380, 205, 'public executeQueryPhase 返回 void + listener', 'fig-sub');
    s += txt(380, 227, '真正跑 Lucene 的是 private 重载,丢进 search 池', 'fig-sub');
    s += txt(380, 262, '第 8 课不变量:handler 线程不卡在 Lucene 上', 'fig-sub');
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
    s += txt(567, 108, 'alias / nested / slice 进 FILTER', 'fig-sub');
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
    s += txt(380, 127, 'preProcess 加上 FILTER 之后的执行查询', 'fig-sub');
    s += line(380, 136, 380, 149, 'ah17s3');
    s += rect(180, 153, 400, 52, 'fig-box-hot', 'fp-pop');
    s += txt(380, 176, 'rewrittenQuery()', 'fig-name');
    s += txt(380, 196, 'searcher.rewrite:词项展开、常量折叠', 'fig-sub');
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
    s += txt(380, 66, '聚合 / rescore / suggest 接在主查询之后,读同一份 context', 'fig-sub');
    s += rect(205, 100, 350, 64, 'fig-box-hot', 'fp-pop');
    s += txt(380, 124, 'searcher.search(query, collector)', 'fig-name');
    s += txt(380, 146, 'query 就是 rewrittenQuery()', 'fig-sub');
    s += rect(15, 178, 355, 70, 'fig-box');
    s += txt(192, 202, 'loadOrExecuteQueryPhase', 'fig-name');
    s += txt(192, 224, 'canCache 命中 → 请求缓存', 'fig-sub');
    s += txt(192, 244, '不跑 Lucene 直接填结果', 'fig-sub');
    s += rect(390, 178, 355, 70, 'fig-box');
    s += txt(567, 202, '超时检查点', 'fig-name');
    s += txt(567, 224, 'getTimeoutCheck 挂 cancellation', 'fig-sub');
    s += txt(567, 244, '收集过程中看相对时钟', 'fig-sub');
    s += txt(380, 274, '返回 (docId,score),不含 _source;占 search 池的是这里', 'fig-sub');
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
    s += txt(567, 112, '不再发第二次跨节点往返', 'fig-sub');
    s += rect(15, 148, 730, 70, 'fig-box');
    s += txt(380, 172, 'numberOfShards() == 1 && rankBuilder() == null', 'fig-key');
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
    s += txt(567, 192, 'DELETE /_pit 或到期才释放', 'fig-sub');
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
      { svg: step1(), note: '数据节点收到 phase/query。Transport handler 那条 executeQueryPhase 签名是 void + ActionListener:它只做 rewrite 与提交,立刻返回——Lucene 在 private 重载、search 池里跑完才 onResponse。' },
      { svg: step2(), note: 'createContext 三步:从 ReaderContext 拿 Searcher、parseSource 写 from/size/timeout 与 originalQuery、preProcess 校验窗口并改写 query 字段。整个生命周期套在 try-with-resources 上,任一步抛错都先 close 再往外抛。' },
      { svg: step3(), note: '三个查询字段:originalQuery 是用户的 ParsedQuery(留给 highlight/explain/profile 说话);query 在 preProcess 里加上 alias/nested/slice FILTER,但尚未 Lucene rewrite;rewrittenQuery() 才是 searcher.rewrite 之后真正执行的那份。' },
      { svg: step4(), note: 'QueryPhase.execute 是 static:searcher.search(rewrittenQuery(), collector)。能缓存(canCache)就不跑 Lucene;超时检查点挂成 cancellation,在收集过程中看相对时钟——不是墙上时钟一到就杀线程。' },
      { svg: step5(), note: '多分片:回 QuerySearchResult,只有 (docId,score) 与聚合,_source 留给第 16 课的 Fetch 阶段。单分片且无 rankBuilder:同一份 SearchContext 里顺手 executeFetchPhase——这是优化路径,不是一种 SearchType。' },
      { svg: step6(), note: 'close 只关这一趟的 SearchContext(释放 searcher 视图)。跨请求保活的是 ReaderContext:PIT/Scroll 活在 activeReaders 里靠 keep-alive 续命,DELETE /_pit 或到期才释放;普通搜索 singleSession,Query 相位就可能 freeReaderContext。' }
    ]
  };

  /* ===== 实验 ===== */
  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};

  window.ESEXPERIMENTS['ch17-00-setup'] = {
    version: 1, id: 'ch17-00-setup',
    title: '实验 0 · 建 tut-l17-timeout(1 主分片)',
    method: 'PUT', path: '/tut-l17-timeout',
    body: { settings: { number_of_shards: 1, number_of_replicas: 0 } },
    predict: '1 个主分片对超时实验意味着什么?',
    expect: 'acknowledged: true。单分片让「收集多少文档、检查点跑几次」完全可控——超时观察的变量只有工作量,没有多分片并行的噪声。'
  };
  window.ESEXPERIMENTS['ch17-01-bulk3'] = {
    version: 1, id: 'ch17-01-bulk3',
    title: '实验 1 · 三篇文档(?refresh=true)',
    method: 'POST', path: '/_bulk?refresh=true',
    body: '{"index":{"_index":"tut-l17-timeout","_id":"1"}}\n{"title":"quick brown fox","n":1}\n{"index":{"_index":"tut-l17-timeout","_id":"2"}}\n{"title":"lazy dog","n":2}\n{"index":{"_index":"tut-l17-timeout","_id":"3"}}\n{"title":"quick brown","n":3}\n',
    predict: '3 篇、match_all、timeout=1ms:下一个实验里 timed_out 更可能是 true 还是 false?',
    expect: 'errors: false、3 项 201。数据就绪。先记住你的预测——超时是收集检查点,不是「方法一开始就看表」,3 篇大概率在第一次检查之前就收集完了。'
  };
  window.ESEXPERIMENTS['ch17-02-timeout-fast'] = {
    version: 1, id: 'ch17-02-timeout-fast',
    title: '实验 2 · timeout=1ms 但快到看不见',
    method: 'POST', path: '/tut-l17-timeout/_search?filter_path=timed_out,hits.total,hits.hits._id',
    body: { timeout: '1ms', query: { match_all: {} } },
    predict: '设了 1ms 超时,timed_out 是 true 吗?',
    expect: '大概率 timed_out: false、3 hits。getTimeoutCheck 挂的是收集过程中的 cancellation 检查点:3 篇文档在第一次检查之前就收集完了。这不是 bug,是检查粒度——「设了 1ms 就一定超时」不成立。'
  };
  window.ESEXPERIMENTS['ch17-03-bulk30'] = {
    version: 1, id: 'ch17-03-bulk30',
    title: '实验 3 · 再灌 30 篇,给忙循环铺量',
    method: 'POST', path: '/_bulk?refresh=true',
    body: '{"index":{"_index":"tut-l17-timeout","_id":"10"}}\n{"title":"doc 10","n":10}\n{"index":{"_index":"tut-l17-timeout","_id":"11"}}\n{"title":"doc 11","n":11}\n{"index":{"_index":"tut-l17-timeout","_id":"12"}}\n{"title":"doc 12","n":12}\n{"index":{"_index":"tut-l17-timeout","_id":"13"}}\n{"title":"doc 13","n":13}\n{"index":{"_index":"tut-l17-timeout","_id":"14"}}\n{"title":"doc 14","n":14}\n{"index":{"_index":"tut-l17-timeout","_id":"15"}}\n{"title":"doc 15","n":15}\n{"index":{"_index":"tut-l17-timeout","_id":"16"}}\n{"title":"doc 16","n":16}\n{"index":{"_index":"tut-l17-timeout","_id":"17"}}\n{"title":"doc 17","n":17}\n{"index":{"_index":"tut-l17-timeout","_id":"18"}}\n{"title":"doc 18","n":18}\n{"index":{"_index":"tut-l17-timeout","_id":"19"}}\n{"title":"doc 19","n":19}\n{"index":{"_index":"tut-l17-timeout","_id":"20"}}\n{"title":"doc 20","n":20}\n{"index":{"_index":"tut-l17-timeout","_id":"21"}}\n{"title":"doc 21","n":21}\n{"index":{"_index":"tut-l17-timeout","_id":"22"}}\n{"title":"doc 22","n":22}\n{"index":{"_index":"tut-l17-timeout","_id":"23"}}\n{"title":"doc 23","n":23}\n{"index":{"_index":"tut-l17-timeout","_id":"24"}}\n{"title":"doc 24","n":24}\n{"index":{"_index":"tut-l17-timeout","_id":"25"}}\n{"title":"doc 25","n":25}\n{"index":{"_index":"tut-l17-timeout","_id":"26"}}\n{"title":"doc 26","n":26}\n{"index":{"_index":"tut-l17-timeout","_id":"27"}}\n{"title":"doc 27","n":27}\n{"index":{"_index":"tut-l17-timeout","_id":"28"}}\n{"title":"doc 28","n":28}\n{"index":{"_index":"tut-l17-timeout","_id":"29"}}\n{"title":"doc 29","n":29}\n{"index":{"_index":"tut-l17-timeout","_id":"30"}}\n{"title":"doc 30","n":30}\n{"index":{"_index":"tut-l17-timeout","_id":"31"}}\n{"title":"doc 31","n":31}\n{"index":{"_index":"tut-l17-timeout","_id":"32"}}\n{"title":"doc 32","n":32}\n{"index":{"_index":"tut-l17-timeout","_id":"33"}}\n{"title":"doc 33","n":33}\n{"index":{"_index":"tut-l17-timeout","_id":"34"}}\n{"title":"doc 34","n":34}\n{"index":{"_index":"tut-l17-timeout","_id":"35"}}\n{"title":"doc 35","n":35}\n{"index":{"_index":"tut-l17-timeout","_id":"36"}}\n{"title":"doc 36","n":36}\n{"index":{"_index":"tut-l17-timeout","_id":"37"}}\n{"title":"doc 37","n":37}\n{"index":{"_index":"tut-l17-timeout","_id":"38"}}\n{"title":"doc 38","n":38}\n{"index":{"_index":"tut-l17-timeout","_id":"39"}}\n{"title":"doc 39","n":39}\n',
    predict: '这次写入和上一个实验的 3 篇在同一个索引里,总共有几篇?给下一个实验的忙循环备了多少个命中?',
    expect: 'errors: false。索引共 33 篇,下一个实验的 script_score 会对每个命中都跑一遍忙循环——把收集过程拉长到跨过超时检查点。'
  };
  window.ESEXPERIMENTS['ch17-04-timeout-slow'] = {
    version: 1, id: 'ch17-04-timeout-slow',
    title: '实验 4 · script_score 忙循环:timed_out 变 true',
    method: 'POST', path: '/tut-l17-timeout/_search?filter_path=timed_out,hits.total,hits.hits._id,_shards',
    body: {
      timeout: '1ms', size: 10,
      query: {
        script_score: {
          query: { match_all: {} },
          script: { source: 'long acc = 0L; for (int i = 0; i < 5000000; i++) { acc += i; } return 1.0;' }
        }
      }
    },
    predict: '每个命中跑五百万次加法:timed_out 现在是什么?hits 还全吗?',
    expect: 'timed_out: true;hits 可能不足全集甚至为空——部分结果合法(ContextIndexSearcher 尽量带着已收集的部分返回)。对照源码链:getTimeoutCheck → throwTimeExceededException → SearchTimeoutException.handleTimeout → searchTimedOut(true) → 响应顶层 timed_out。若你机器太快仍是 false,把循环次数再加一个零。'
  };
  window.ESEXPERIMENTS['ch17-05-timeout-strict'] = {
    version: 1, id: 'ch17-05-timeout-strict',
    title: '实验 5 · 禁止部分结果:同一个超时变 429',
    method: 'POST', path: '/tut-l17-timeout/_search?allow_partial_search_results=false&filter_path=error,timed_out',
    body: {
      timeout: '1ms', size: 10,
      query: {
        script_score: {
          query: { match_all: {} },
          script: { source: 'long acc = 0L; for (int i = 0; i < 5000000; i++) { acc += i; } return 1.0;' }
        }
      }
    },
    predict: '同一个超时,allow_partial_search_results=false:还是「200 + timed_out: true」吗?',
    expect: '不是。HTTP 429,SearchTimeoutException(handleTimeout 里 allowPartialSearchResults == false 的分支直接抛)。同一个 TimeExceededException,出口由「允不允许部分结果」决定——这就是两分支的唯一差别。'
  };
  window.ESEXPERIMENTS['ch17-06-setup-pit'] = {
    version: 1, id: 'ch17-06-setup-pit',
    title: '实验 6 · 建 tut-l17-pit(1 主分片)',
    method: 'PUT', path: '/tut-l17-pit',
    body: { settings: { number_of_shards: 1, number_of_replicas: 0 } },
    predict: 'PIT 钉住的是哪个对象的视图?',
    expect: 'acknowledged: true。PIT 钉的是 Engine.SearcherSupplier 背后那份 IndexReader 视图——不是「缓存了搜索结果」。ts 字段留给 sort/search_after 用。'
  };
  window.ESEXPERIMENTS['ch17-07-bulk5'] = {
    version: 1, id: 'ch17-07-bulk5',
    title: '实验 7 · 五篇带 ts 的文档',
    method: 'POST', path: '/_bulk?refresh=true',
    body: '{"index":{"_index":"tut-l17-pit","_id":"1"}}\n{"title":"quick brown fox","ts":1}\n{"index":{"_index":"tut-l17-pit","_id":"2"}}\n{"title":"quick brown","ts":2}\n{"index":{"_index":"tut-l17-pit","_id":"3"}}\n{"title":"lazy dog","ts":3}\n{"index":{"_index":"tut-l17-pit","_id":"4"}}\n{"title":"quick fox","ts":4}\n{"index":{"_index":"tut-l17-pit","_id":"5"}}\n{"title":"brown fox","ts":5}\n',
    predict: 'title 里含 quick 的有几篇?',
    expect: 'errors: false。_id 1、2、4 三篇含 quick(ts 1、2、4)——后面 PIT 搜索的预期集合以这批为准。'
  };
  window.ESEXPERIMENTS['ch17-08-pit-open'] = {
    version: 1, id: 'ch17-08-pit-open',
    title: '实验 8 · 打开 PIT(抄下返回的 id)',
    method: 'POST', path: '/tut-l17-pit/_pit?keep_alive=2m&filter_path=id',
    predict: 'openReaderContext 之后,这个 id 代表什么?它自己会过期吗?',
    expect: '返回一长串 id(含 searcher id 与分片版本),把它抄下来粘进实验 10、12、14 的 pit.id 字段再运行。keep_alive=2m:两分钟内不用会自动过期——手慢就重开一个。对应源码 openReaderContext → activeReaders。'
  };
  window.ESEXPERIMENTS['ch17-09-contexts-open'] = {
    version: 1, id: 'ch17-09-contexts-open',
    title: '实验 9 · open_contexts:PIT 在节点上记了账',
    method: 'GET', path: '/_nodes/stats/indices/search?filter_path=nodes.*.name,nodes.*.indices.search.open_contexts',
    predict: '刚开了一个 PIT,open_contexts 是多少?',
    expect: '本节点 open_contexts ≥ 1(实验前是 0)。activeReaders 里的 ReaderContext 在节点统计上就是这一格——PIT 不是免费的,每个都占着一份 IndexReader 直到关闭或过期。'
  };
  window.ESEXPERIMENTS['ch17-10-pit-page1'] = {
    version: 1, id: 'ch17-10-pit-page1',
    title: '实验 10 · PIT 第一页:size=2 + sort',
    method: 'POST', path: '/_search?filter_path=hits.hits._id,hits.hits.sort',
    body: { size: 2, sort: [{ ts: 'asc' }], query: { match: { title: 'quick' } }, pit: { id: '把实验 8 返回的 id 粘进来', keep_alive: '2m' } },
    predict: 'hits 是哪两篇?sort 值是多少,拿去干什么用?',
    expect: '_id 1 和 2(sort 值 [1]、[2])。把最后一条的 sort 值放进下一次请求的 search_after,就是现代翻页——进度在客户端,不在服务端;这份 sort 值就是下一页的接力棒。'
  };
  window.ESEXPERIMENTS['ch17-11-write-new'] = {
    version: 1, id: 'ch17-11-write-new',
    title: '实验 11 · PIT 开着,写入并 refresh 一篇',
    method: 'PUT', path: '/tut-l17-pit/_doc/new?refresh=true',
    body: { title: 'quick newcomer', ts: 99 },
    predict: 'refresh=true 已经把新文档编进 segment:同一个 PIT 还能看见它吗?普通搜索呢?',
    expect: 'result: created。refresh 生效的是「当前的」EXTERNAL searcher;PIT 钉住的是开 PIT 那一刻的 SearcherSupplier,新 segment 不在它的视图里。下面两个实验分别验证。'
  };
  window.ESEXPERIMENTS['ch17-12-pit-again'] = {
    version: 1, id: 'ch17-12-pit-again',
    title: '实验 12 · 同一个 PIT 再搜:看不见 new',
    method: 'POST', path: '/_search?filter_path=hits.total,hits.hits._id',
    body: { size: 20, sort: [{ ts: 'asc' }], query: { match: { title: 'quick' } }, pit: { id: '同一个 id 粘进来', keep_alive: '2m' } },
    predict: 'PIT 搜索的 hits 里有没有 new?total 是多少?',
    expect: '没有 new;只有 _id 1、2、4(在实验 8 的快照里,当时 new 还不存在)。注意 PIT 不是「缓存搜索结果」——query 现场跑,只是 Reader 视图冻结;total 也是基于旧视图统计的。'
  };
  window.ESEXPERIMENTS['ch17-13-no-pit'] = {
    version: 1, id: 'ch17-13-no-pit',
    title: '实验 13 · 不用 PIT:立刻看见 new',
    method: 'POST', path: '/tut-l17-pit/_search?filter_path=hits.total,hits.hits._id',
    body: { size: 20, query: { match: { title: 'quick' } } },
    predict: '普通搜索能看到 new 吗?total 比实验 12 多几?',
    expect: '能看到 new;total 多 1(4 篇)。普通 _search 每次都 acquire 当时的 EXTERNAL searcher——refresh 进来的新 segment 立刻可见。PIT 与普通搜索的差别不在 query,在 Reader。'
  };
  window.ESEXPERIMENTS['ch17-14-pit-close'] = {
    version: 1, id: 'ch17-14-pit-close',
    title: '实验 14 · 关掉 PIT',
    method: 'DELETE', path: '/_pit',
    body: { id: '同一个 id 粘进来' },
    predict: 'DELETE /_pit 成功后,那份 IndexReader 什么时候真正释放?',
    expect: 'succeeded: true(可能是 true/false 布尔字段,以返回为准)。freeReaderContext 把 activeReaders 里这份 ReaderContext 关掉,SearcherSupplier 引用归零后 IndexReader 才真正释放——PIT 的 keep_alive 要设短、用完要显式关,原因就在这。'
  };
  window.ESEXPERIMENTS['ch17-15-contexts-closed'] = {
    version: 1, id: 'ch17-15-contexts-closed',
    title: '实验 15 · open_contexts 回到 0',
    method: 'GET', path: '/_nodes/stats/indices/search?filter_path=nodes.*.name,nodes.*.indices.search.open_contexts',
    predict: '现在是多少?如果忘了关,靠什么兜底?',
    expect: '回到 0。兜底是 keep-alive 到期(markAsUsed 的续命用完自动 free)——但「等过期」意味着这段时间里 reader 一直占着,养成 DELETE /_pit 的习惯。'
  };
  window.ESEXPERIMENTS['ch17-16-cleanup-timeout'] = {
    version: 1, id: 'ch17-16-cleanup-timeout',
    title: '清理 1 · 删除 tut-l17-timeout',
    method: 'DELETE', path: '/tut-l17-timeout',
    predict: '这个索引里有实验 4 制造的部分结果残留吗?',
    expect: 'acknowledged: true。部分结果只存在于当时的响应里,从未写盘——索引删掉即全清。'
  };
  window.ESEXPERIMENTS['ch17-17-cleanup-pit'] = {
    version: 1, id: 'ch17-17-cleanup-pit',
    title: '清理 2 · 删除 tut-l17-pit',
    method: 'DELETE', path: '/tut-l17-pit',
    predict: '实验 14 已经关了 PIT,直接删索引还有障碍吗?',
    expect: 'acknowledged: true。PIT 已关、open_contexts 归零,删除无障碍——若 PIT 还开着,索引也不至于删不掉,但那份 reader 会随索引一起被清理;顺序上先关 PIT 再删索引更干净。'
  };
})();
