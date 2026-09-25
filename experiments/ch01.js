/* experiments/ch01.js — 第 1 课:实验 + 近实时动画(注册表) */
(function () {
  'use strict';

  /* ===== 动画:近实时(GET vs SEARCH)===== */
  var LABELS = ['① 写入', '② GET', '③ SEARCH', '④ refresh', '⑤ 再 SEARCH'];
  var SUBS = ['PUT _doc/1', 'GET _doc/1', 'match: brown', 'POST _refresh', 'match: brown'];
  var RESULTS = ['201 Created', 'found: true', 'hits.total: 0', '新 segment', 'hits.total: 1'];
  var NOTES = [
    '文档写入成功:进了 translog 和内存 buffer,但还没编进倒排表。',
    'GET 是 realtime:按 _id 直接定位这一篇,写完立刻拿得到。',
    'SEARCH 走倒排表:新文档还没被编进去,brown 查不到——写入成功 ≠ 可搜索。',
    'refresh 把内存 buffer 变成一个新的可搜索 segment(注意:不是落盘,落盘是 flush)。',
    '倒排表里现在有 brown → Doc1 了。未改 refresh_interval 且分片仍被搜索时约每 1 秒 refresh;进入 search idle 后这只钟会停。'
  ];

  function stepSvg(hotIx) {
    var s = '<svg viewBox="0 0 760 175" xmlns="http://www.w3.org/2000/svg">';
    s += '<defs><marker id="ah-nrt" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
      + '<path d="M 0 0 L 10 5 L 0 10 z" class="fig-arrowhead"/></marker></defs>';
    for (var i = 0; i < 5; i++) {
      var x = 10 + i * 152;
      var w = 132;
      if (i < 4) {
        var lit = i < hotIx;
        s += '<line x1="' + (x + w) + '" y1="103" x2="' + (x + w + 20) + '" y2="103" class="fig-arrow" marker-end="url(#ah-nrt)"'
          + (lit ? '' : ' opacity="0.35"') + '/>';
      }
      var isHot = i === hotIx;
      var op = i <= hotIx ? 1 : 0.4;
      s += '<g opacity="' + op + '">';
      s += '<rect x="' + x + '" y="70" width="' + w + '" height="70" rx="9" class="'
        + (isHot ? 'fig-box-hot fp-pop' : 'fig-box') + '"/>';
      s += '<text x="' + (x + w / 2) + '" y="92" text-anchor="middle" class="fig-sub">' + LABELS[i] + '</text>';
      s += '<text x="' + (x + w / 2) + '" y="110" text-anchor="middle" class="fig-name">' + SUBS[i] + '</text>';
      if (isHot) {
        var miss = i === 2;
        s += '<text x="' + (x + w / 2) + '" y="128" text-anchor="middle" class="fig-key'
          + (miss ? ' fp-pulse' : '') + '"'
          + (miss ? ' style="fill: rgb(var(--warn))"' : '')
          + '>' + RESULTS[i] + '</text>';
      } else {
        s += '<text x="' + (x + w / 2) + '" y="128" text-anchor="middle" class="fig-sub">' + RESULTS[i] + '</text>';
      }
      s += '</g>';
    }
    s += '</svg>';
    return s;
  }

  window.ESFLOWS = window.ESFLOWS || {};
  window.ESFLOWS['ch01-nrt'] = {
    version: 1,
    id: 'ch01-nrt',
    title: '近实时:写入后 GET 与 SEARCH 的可见性差',
    speed: 2200,
    steps: NOTES.map(function (note, i) { return { svg: stepSvg(i), note: note }; })
  };

  /* ===== 实验 ===== */
  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};
  window.ESEXPERIMENTS['ch01-00-setup'] = {
    version: 1, id: 'ch01-00-setup',
    title: '实验 0 · 建索引(2 主分片、1 副本、关自动 refresh)',
    method: 'PUT', path: '/tut-l01-docs',
    body: {
      settings: {
        number_of_shards: 2,
        number_of_replicas: 1,
        refresh_interval: -1
      }
    },
    predict: '为什么 refresh_interval 要设 -1?不关的话,实验 3 的「搜不到」窗口只有 1 秒,会变成手慢就搜到了。',
    expect: 'acknowledged: true。这一步只是建壳:分片就位,还没有任何文档。'
  };
  window.ESEXPERIMENTS['ch01-01-analyze-chain'] = {
    version: 1, id: 'ch01-01-analyze-chain',
    title: '实验 1a · 显式拼分析链(standard + lowercase + stop)',
    method: 'POST', path: '/tut-l01-docs/_analyze',
    body: {
      tokenizer: 'standard',
      filter: ['lowercase', 'stop'],
      text: 'The Quick Brown FOX'
    },
    predict: '先猜:"The Quick Brown FOX" 走完这条链,留下哪些 token?the 还在吗?',
    expect: '留下 quick、brown、fox 三个 token——和图 2 一致。'
  };
  window.ESEXPERIMENTS['ch01-02-analyze-standard'] = {
    version: 1, id: 'ch01-02-analyze-standard',
    title: '实验 1b · 内置 standard 分析器(默认不停用词)',
    method: 'POST', path: '/tut-l01-docs/_analyze',
    body: {
      analyzer: 'standard',
      text: 'The Quick Brown FOX'
    },
    predict: '同样一句话,只写 analyzer: standard,the 会被去掉吗?',
    expect: 'the 还在!ES 内置 standard 的默认停用词表是空的(StandardAnalyzerProvider 里是 EMPTY_SET)。谁说一定会去 the,谁就是把 Lucene 的 StandardAnalyzer 和 ES 的 standard 弄混了。'
  };
  window.ESEXPERIMENTS['ch01-03-shards'] = {
    version: 1, id: 'ch01-03-shards',
    title: '实验 2a · 看分片放置',
    method: 'GET', path: '/_cat/shards/tut-l01-docs?v',
    predict: '2 主分片 × 1 副本、只有一个节点:应有几行?p 和 r 各自的 state 是什么?',
    expect: '4 行(P0、P1、R0、R1)。两行 prirep=p 是 STARTED,两行 prirep=r 是 UNASSIGNED——不是副本没建,是没第二台机器可放。'
  };
  window.ESEXPERIMENTS['ch01-04-health'] = {
    version: 1, id: 'ch01-04-health',
    title: '实验 2b · 集群健康(Yellow 的由来)',
    method: 'GET', path: '/_cluster/health?v',
    predict: '主分片全在、副本没处放:status 是 green 还是 yellow?',
    expect: 'yellow。green=主副本全就位;red=有主分片都丢了。单节点带副本,只能是 yellow——这是结构问题,不是故障。'
  };
  window.ESEXPERIMENTS['ch01-05-nrt-put'] = {
    version: 1, id: 'ch01-05-nrt-put',
    title: '实验 3 · 第 1 步:写入文档(不带 refresh)',
    method: 'PUT', path: '/tut-l01-docs/_doc/1',
    body: { body: 'The Quick Brown FOX' },
    predict: '写入会成功吗?result 字段是 created 还是 updated?',
    expect: 'result: created。文档进了 translog 和内存 buffer,但索引 refresh_interval=-1,倒排表不会自动更新。'
  };
  window.ESEXPERIMENTS['ch01-06-nrt-get'] = {
    version: 1, id: 'ch01-06-nrt-get',
    title: '实验 3 · 第 2 步:立刻 GET',
    method: 'GET', path: '/tut-l01-docs/_doc/1',
    predict: '刚写完、还没 refresh:GET 能拿到吗?',
    expect: 'found: true。GET 是 realtime 读,按 _id 直查,不等 refresh(机制在第 10 课拆)。'
  };
  window.ESEXPERIMENTS['ch01-07-nrt-search-miss'] = {
    version: 1, id: 'ch01-07-nrt-search-miss',
    title: '实验 3 · 第 3 步:立刻 SEARCH(应扑空)',
    method: 'POST', path: '/tut-l01-docs/_search',
    body: { query: { match: { body: 'brown' } } },
    predict: 'GET 都拿到了,SEARCH brown 能搜到吗?',
    expect: 'hits.total.value = 0。SEARCH 走倒排表,而倒排表还停在旧视图——写入成功 ≠ 可搜索。'
  };
  window.ESEXPERIMENTS['ch01-08-refresh'] = {
    version: 1, id: 'ch01-08-refresh',
    title: '实验 3 · 第 4 步:手动 refresh',
    method: 'POST', path: '/tut-l01-docs/_refresh',
    predict: '_refresh 会把什么变成什么?',
    expect: '把内存 buffer 里的文档生成新的可搜索 segment。_shards 里每个分片各成功一次。'
  };
  window.ESEXPERIMENTS['ch01-09-nrt-search-hit'] = {
    version: 1, id: 'ch01-09-nrt-search-hit',
    title: '实验 3 · 第 5 步:再 SEARCH(命中)',
    method: 'POST', path: '/tut-l01-docs/_search',
    body: { query: { match: { body: 'brown' } } },
    predict: 'refresh 之后,搜 brown 命中几条?',
    expect: 'hits.total.value = 1,_id=1。注意:PUT 时加 ?refresh=true 也能立刻命中,但那是把 refresh 成本算进这一次写入。'
  };
  window.ESEXPERIMENTS['ch01-10-cleanup'] = {
    version: 1, id: 'ch01-10-cleanup',
    title: '清理 · 删除实验索引',
    method: 'DELETE', path: '/tut-l01-docs',
    predict: '删索引会连带删掉什么?',
    expect: 'acknowledged: true。索引及其所有分片数据(包括 translog 与 segment)一并删除,不可恢复。'
  };
})();
