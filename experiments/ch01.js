/* experiments/ch01.js — 第 1 课:实验 + 近实时动画(注册表) */
(function () {
  'use strict';

  /* ===== 动画:近实时(GET vs SEARCH)===== */
  var LABELS = ['① 写入', '② GET', '③ SEARCH', '④ refresh', '⑤ 再 SEARCH'];
  var SUBS = ['PUT _doc/1', 'GET _doc/1', 'match: brown', 'POST _refresh', 'match: brown'];
  var RESULTS = ['201 Created', 'found: true', 'hits.total: 0', '新 segment', 'hits.total: 1'];
  var NOTES = [
    '文档写入成功:进了 translog 和内存 buffer,但还没进入当前可搜索视图。',
    'GET 是 realtime:按 _id 直接定位这一篇,写完立刻拿得到。',
    'SEARCH 走倒排表:新文档尚未对当前搜索视图可见,brown 查不到——写入成功 ≠ 可搜索。',
    'refresh 让新的 segment 对搜索可见，发布新的可搜索视图。它不等于持久化提交，不能与 flush 混为一谈。',
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
      },
      mappings: {
        properties: { body: { type: 'text', analyzer: 'standard' } }
      }
    },
    predict: '为什么 refresh_interval 要设 -1?不关闭周期性 refresh，下一次刷新可能很快发生，实验 3 会变成「手慢就搜到了」的竞态。',
    expect: 'acknowledged: true 表示索引创建变更已确认；shards_acknowledged 表示所要求的活跃分片条件已达到，默认只需主分片。它不保证副本已分配。这里还没有文档，body 字段显式用 standard。'
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
    expect: '留下 quick、brown、fox 三个 token，和图 2 一致。这是本次请求的分析结果，不会更改 body 字段的 analyzer。'
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
    expect: '得到 the、quick、brown、fox。ES 内置 standard 默认停用词表为空，当前 Lucene 10.4.0 无参 StandardAnalyzer() 也是如此；显式加 stop 才会移除 the。'
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
    title: '实验 2b · 本索引健康(Yellow 的由来)',
    method: 'GET', path: '/_cluster/health/tut-l01-docs',
    predict: '单个数据节点、主分片已启动、副本没处放:本索引 status 是 green 还是 yellow?',
    expect: 'yellow：主分片已分配，仍有副本未分配。green 表示全部分片已分配，red 表示至少一个主分片未分配。这里仅检查本索引，不会被其他索引的健康状态干扰；多节点时可能为 green。'
  };
  window.ESEXPERIMENTS['ch01-05-nrt-put'] = {
    version: 1, id: 'ch01-05-nrt-put',
    title: '实验 3 · 第 1 步:写入文档(不带 refresh)',
    method: 'PUT', path: '/tut-l01-docs/_doc/1',
    body: { body: 'The Quick Brown FOX' },
    predict: '写入会成功吗?result 字段是 created 还是 updated?',
    expect: '新建空索引中首次写入时 result: created；不自动 refresh，所以搜索视图尚不可见。若显示 updated，说明不是第一次写入；请清理并重建索引后重做实验 3。'
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
    expect: '让新的 segment 对搜索可见，发布新的可搜索视图；并非持久化提交。检查 _shards.failed 是否为 0，未分配的副本不会参与这次刷新。'
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
    expect: 'acknowledged: true。本章实验索引及其分片数据被删除，不能靠 refresh 恢复。若索引已不存在则返回 404；重做时可继续实验 0。'
  };
})();
