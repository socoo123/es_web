/* experiments/ch11.js — 第 11 课:动态映射推断动画 + 实验(注册表) */
(function () {
  'use strict';

  /* ===== 动画:动态映射推断(快照式,每步一张完整 SVG)===== */
  var FIELDS = [
    { f: 'title', v: '"Elasticsearch Guide"', t: 'text+keyword', d: 1 },
    { f: 'price', v: '29.99', t: 'float', d: 2 },
    { f: 'in_stock', v: 'true', t: 'boolean', d: 2 },
    { f: 'publish_date', v: '"2024-01-15"', t: 'date', d: 3 },
    { f: 'tags', v: '["search","database"]', t: 'text', d: 3 },
    { f: 'author', v: '{"name":…}', t: 'object', d: 4 },
    { f: 'author.name', v: '"John Doe"', t: 'text+keyword', d: 4 },
    { f: 'author.age', v: '35', t: 'long', d: 4 }
  ];

  var NOTES = [
    '一份没见过 mapping 的 JSON 文档写进新索引:此刻 mapping 里只有根对象 _doc。DocumentParser.parseValue 对每个字段先找叶子 mapper——一个都找不到。',
    'title 是 VALUE_STRING:能 parse 成数字吗?numeric_detection 默认关;像日期吗?不像。落到 newDynamicStringField:主字段 text,再挂子字段 keyword,ignore_above 写死 256。',
    'price 是 JSON 数字(DOUBLE token):走 VALUE_NUMBER 另一支,建成 float 而不是 double——源码注释写的是 much more space-efficient。in_stock 是 true/false,直接 boolean。',
    'publish_date 的值 "2024-01-15" 被 date_detection(默认开)认成日期,建成 date。tags 是数组:数组没有自己的类型,每个元素复用同一个 mapper,切出的词全挂在 tags 下。',
    'author 是 START_OBJECT:建成 object mapper 再展开,字段路径变成 author.name、author.age,扁平挂进同一篇 Lucene 文档。name 是字符串 → text+keyword,age 是整数 → long。',
    '解析收尾:createDynamicUpdate 把这批动态 builder 收成一份 mapping 源,经 MapperService.merge(MAPPING_AUTO_UPDATE) 合并进 cluster state——第一篇文档把 schema 写死了。',
    '第二篇把 price 写成字符串 "29.99":与已有 float 对不上,这篇文档解析失败(400);但自动更新保住旧 mapper,不会为一篇类型不符的文档改掉全索引的类型。'
  ];

  function rbox(x, y, w, h, cls, op) {
    return '<rect x="' + x + '" y="' + y + '" width="' + w + '" height="' + h + '" rx="9" class="' + cls + '"'
      + (op < 1 ? ' opacity="' + op + '"' : '') + '/>';
  }
  function txt(x, y, cls, t, extra) {
    return '<text x="' + x + '" y="' + y + '" text-anchor="middle" class="' + cls + '"' + (extra || '') + '>' + t + '</text>';
  }
  function arrow(x1, y1, x2, y2, lit) {
    return '<line x1="' + x1 + '" y1="' + y1 + '" x2="' + x2 + '" y2="' + y2 + '" class="fig-arrow" marker-end="url(#ah-dyn)"'
      + (lit ? '' : ' opacity="0.35"') + '/>';
  }

  function stepSvg(step) {
    var s = '<svg viewBox="0 0 760 316" xmlns="http://www.w3.org/2000/svg">';
    s += '<defs><marker id="ah-dyn" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
      + '<path d="M 0 0 L 10 5 L 0 10 z" class="fig-arrowhead"/></marker></defs>';

    /* 顶部管线 */
    var t1hot = step === 0 || step === 6;
    var t2hot = step >= 1 && step <= 4;
    var t3hot = step === 5;
    s += rbox(10, 12, 228, 54, t1hot ? 'fig-box-hot fp-pop' : 'fig-box', 1);
    s += txt(124, 34, 'fig-name', step === 6 ? '① 第二篇:类型冲突' : '① PUT 未知 JSON');
    s += txt(124, 54, 'fig-sub', step === 6 ? 'price: "29.99"(字符串)' : 'tut-l11/_doc/1(6 个字段)');
    s += arrow(242, 39, 290, 39, step >= 1);
    s += rbox(296, 12, 228, 54, t2hot ? 'fig-box-hot fp-pop' : 'fig-box', step >= 1 ? 1 : 0.4);
    s += txt(410, 34, 'fig-name', '② 逐字段找 mapper');
    s += txt(410, 54, 'fig-sub', 'DocumentParser.parseValue');
    s += arrow(528, 39, 576, 39, step >= 5);
    s += rbox(582, 12, 168, 54, t3hot ? 'fig-box-hot fp-pop' : 'fig-box', step >= 5 ? 1 : 0.4);
    s += txt(666, 34, 'fig-name', '③ 推断并写回');
    s += txt(666, 54, 'fig-sub', 'DynamicFieldsBuilder');

    /* 字段网格:逐个点亮决策 */
    for (var i = 0; i < FIELDS.length; i++) {
      var f = FIELDS[i];
      var col = i % 4;
      var row = i < 4 ? 0 : 1;
      var x = 10 + col * 180;
      var y = row === 0 ? 80 : 152;
      var w = 170, h = 62;
      var decided = step >= f.d;
      var justNow = step === f.d;
      var conflict = step === 6 && f.f === 'price';
      s += '<g opacity="' + (decided ? 1 : 0.38) + '">';
      s += rbox(x, y, w, h, (justNow || conflict) ? 'fig-box-hot fp-pop' : 'fig-box', 1);
      s += txt(x + w / 2, y + 18, 'fig-sub', f.f);
      s += txt(x + w / 2, y + 34, 'fig-sub', f.v);
      if (conflict) {
        s += txt(x + w / 2, y + 52, 'fig-key fp-pulse', 'float ✗ "29.99"', ' style="fill: rgb(var(--warn))"');
      } else {
        s += txt(x + w / 2, y + 52, 'fig-name', decided ? f.t : '?');
      }
      s += '</g>';
    }

    /* 汇入 cluster state 的 mapping */
    s += arrow(380, 218, 380, 228, step >= 5);
    var pHot = step >= 5;
    s += rbox(10, 232, 740, 72, pHot ? (step === 5 ? 'fig-box-hot fp-pop' : 'fig-box-hot') : 'fig-box', pHot ? 1 : 0.5);
    s += txt(380, 254, 'fig-name', 'cluster state · mappings(tut-l11)');
    if (step <= 4) {
      s += txt(380, 282, 'fig-sub', '还是空的:mapping 只有根对象 _doc,等这篇文档解析完');
    } else if (step === 5) {
      s += txt(380, 282, 'fig-sub', 'merge(MAPPING_AUTO_UPDATE):title: text+kw · price: float · … 8 个字段定稿');
    } else {
      s += txt(380, 278, 'fig-key fp-pulse', 'PUT /_doc/2 → 400 failed to parse field [price] of type [float]', ' style="fill: rgb(var(--warn))"');
      s += txt(380, 296, 'fig-sub', '这篇文档被拒;mapping 里 price 仍是 float——类型一经首写即定死');
    }
    s += '</svg>';
    return s;
  }

  window.ESFLOWS = window.ESFLOWS || {};
  window.ESFLOWS['ch11-dynamic-mapping'] = {
    version: 1,
    id: 'ch11-dynamic-mapping',
    title: '动态映射推断:一份未知 JSON 如何写死 schema',
    speed: 2200,
    steps: NOTES.map(function (note, i) { return { svg: stepSvg(i), note: note }; })
  };

  /* ===== 实验 ===== */
  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};
  window.ESEXPERIMENTS['ch11-00-setup'] = {
    version: 1, id: 'ch11-00-setup',
    title: '实验 0 · 建一张白纸索引(不写 mappings)',
    method: 'PUT', path: '/tut-l11-inferred',
    body: {},
    predict: '一行 mapping 都没写,这个索引有 schema 吗?GET _mapping 会返回什么?',
    expect: 'acknowledged: true。mappings 里只有空的 properties——不是「没有 schema」,是一张白纸:下一实验的第一篇文档将替你把它写死。'
  };
  window.ESEXPERIMENTS['ch11-01-infer-put'] = {
    version: 1, id: 'ch11-01-infer-put',
    title: '实验 1a · 写入一篇没人声明过类型的文档',
    method: 'PUT', path: '/tut-l11-inferred/_doc/1?refresh=true',
    body: {
      title: 'Elasticsearch Guide',
      price: 29.99,
      in_stock: true,
      publish_date: '2024-01-15',
      tags: ['search', 'database'],
      author: { name: 'John Doe', age: 35 }
    },
    predict: '先猜:title 会是纯 text 还是 text+keyword?price 是 float 还是 double?publish_date 是 text 还是 date?author 呢?',
    expect: 'result: created,6 个字段全部当场推断成功(refresh=true 是为了后面几个搜索实验立刻可见)。类型答案在下一步 GET _mapping 对。'
  };
  window.ESEXPERIMENTS['ch11-02-infer-mapping'] = {
    version: 1, id: 'ch11-02-infer-mapping',
    title: '实验 1b · 对答案:推断出的 mapping',
    method: 'GET', path: '/tut-l11-inferred/_mapping',
    body: null,
    predict: '最可能猜错的是哪一个?小数、日期串、对象,各是什么类型?',
    expect: 'title/tags/author.name 都是 text + fields.keyword(ignore_above: 256)——DynamicFieldsBuilder.newDynamicStringField 的手笔;price 是 float 不是 double;publish_date 是 date(date_detection 默认开);author 是 object(properties 嵌套);author.age 是 long;in_stock 是 boolean。'
  };
  window.ESEXPERIMENTS['ch11-03-detection-put'] = {
    version: 1, id: 'ch11-03-detection-put',
    title: '实验 1c · 再写一篇:字符串 "42" vs 数字 42',
    method: 'PUT', path: '/tut-l11-inferred/_doc/2',
    body: { sku: '42', qty: 42 },
    predict: 'sku 带引号、qty 不带引号,两个字段的类型会一样吗?',
    expect: 'created。两个字段走不同 JSON token:sku 是 VALUE_STRING、qty 是 VALUE_NUMBER。答案下一实验对——回忆 numeric_detection 的默认值。'
  };
  window.ESEXPERIMENTS['ch11-04-detection-mapping'] = {
    version: 1, id: 'ch11-04-detection-mapping',
    title: '实验 1d · 对答案:detection 两开关的默认值',
    method: 'GET', path: '/tut-l11-inferred/_mapping?filter_path=**.sku,**.qty',
    body: null,
    predict: 'sku 会被认成 long 吗?像日期的字符串又归谁管?',
    expect: 'sku 是 text + keyword 子字段:numeric_detection 默认关(RootObjectMapper Defaults 里是 IMPLICIT_FALSE),字符串就算能 Long.parseLong 也不当数字;qty 是 long:JSON 数字与 detection 开关无关。date_detection 则默认开,所以上一篇的 "2024-01-15" 成了 date。'
  };
  window.ESEXPERIMENTS['ch11-05-analyze-text'] = {
    version: 1, id: 'ch11-05-analyze-text',
    title: '实验 2a · _analyze 看 text 切词',
    method: 'POST', path: '/tut-l11-inferred/_analyze',
    body: { field: 'title', text: 'Elasticsearch Guide' },
    predict: '同一段文字走 title 的分析链,留下几个 token?大小写呢?',
    expect: '两个 token:elasticsearch、guide——standard 小写 + 切词。倒排表的 key 是 token,不是原始 JSON 字符串;这就是 text 侧词典里躺着的东西。'
  };
  window.ESEXPERIMENTS['ch11-06-analyze-keyword'] = {
    version: 1, id: 'ch11-06-analyze-keyword',
    title: '实验 2b · _analyze 看 keyword 整串',
    method: 'POST', path: '/tut-l11-inferred/_analyze',
    body: { field: 'title.keyword', text: 'Elasticsearch Guide' },
    predict: '同样的文字走 title.keyword,会留下什么?',
    expect: '一个 token:Elasticsearch Guide,原样(大小写、空格都保留)。KeywordFieldMapper 的 javadoc 第一句就是 indexes them as-is——tokenized=false,整串即一个 term。'
  };
  window.ESEXPERIMENTS['ch11-07-term-miss'] = {
    version: 1, id: 'ch11-07-term-miss',
    title: '实验 2c · term 打在 text 上(扑空)',
    method: 'POST', path: '/tut-l11-inferred/_search',
    body: { query: { term: { title: 'Elasticsearch' } } },
    predict: '文档 1 的 title 就是 Elasticsearch Guide,term 精确查 Elasticsearch 能命中吗?',
    expect: 'hits.total.value = 0。term 查询不再跑分析器,查询串原样进词典;而词典里的 key 是 elasticsearch(小写)——大小写对不上就是 0 hits,不报错。'
  };
  window.ESEXPERIMENTS['ch11-08-match-hit'] = {
    version: 1, id: 'ch11-08-match-hit',
    title: '实验 2d · match 打在同一字段(命中)',
    method: 'POST', path: '/tut-l11-inferred/_search',
    body: { query: { match: { title: 'Elasticsearch' } } },
    predict: '只把 term 换成 match,同一个词,这次呢?',
    expect: '命中文档 1。match 会用字段同一个分析器处理查询串:Elasticsearch → elasticsearch,与写入侧落进词典的 key 对上。写入、查询走同一套分析,才谈得上全文检索。'
  };
  window.ESEXPERIMENTS['ch11-09-term-keyword'] = {
    version: 1, id: 'ch11-09-term-keyword',
    title: '实验 2e · term 打在 keyword 子字段(整串命中)',
    method: 'POST', path: '/tut-l11-inferred/_search',
    body: { query: { term: { 'title.keyword': 'Elasticsearch Guide' } } },
    predict: 'term 的正确打法:换到 keyword 子字段,查询串要写成什么才命中?',
    expect: '命中文档 1——但查询串必须与存储值一字不差(大小写、空格)。term、terms 聚合、sort 都住在这边:doc_values 列存,天然可聚合。'
  };
  window.ESEXPERIMENTS['ch11-10-strict-create'] = {
    version: 1, id: 'ch11-10-strict-create',
    title: '实验 3a · 建一个 dynamic: strict 的索引',
    method: 'PUT', path: '/tut-l11-strict',
    body: { mappings: { dynamic: 'strict', properties: { title: { type: 'text' } } } },
    predict: 'strict 模式下,写一个 mapping 里没有的字段会发生什么?',
    expect: 'acknowledged: true。schema 钉死:只认 title。下一实验往里塞未知字段,看是写入被拒还是字段被吞。'
  };
  window.ESEXPERIMENTS['ch11-11-strict-reject'] = {
    version: 1, id: 'ch11-11-strict-reject',
    title: '实验 3b · strict:未知字段直接 400',
    method: 'PUT', path: '/tut-l11-strict/_doc/1',
    body: { title: 'ok', unknown_field: 'boom' },
    predict: '状态码是 400、404 还是 201?报错文案里会出现哪几个词?',
    expect: '400,文档整体被拒(注意是请求 body 坏导致的 400,不是路由问题)。reason 含 mapping set to strict, dynamic introduction of [unknown_field] within [_doc] is not allowed——根对象的 path 就是 _doc(MapperService.SINGLE_MAPPING_NAME);异常类型名以你的返回为准。'
  };
  window.ESEXPERIMENTS['ch11-12-false-create'] = {
    version: 1, id: 'ch11-12-false-create',
    title: '实验 3c · 建一个 dynamic: false 的索引',
    method: 'PUT', path: '/tut-l11-false',
    body: { mappings: { dynamic: 'false', properties: { title: { type: 'text' } } } },
    predict: 'false 既不建字段也不报错,那个字段的值去哪了?',
    expect: 'acknowledged: true。dynamic:false 不改 mapping、不写倒排,未知字段的值只随 _source 存储。下一实验写入验证。'
  };
  window.ESEXPERIMENTS['ch11-13-false-swallow'] = {
    version: 1, id: 'ch11-13-false-swallow',
    title: '实验 3d · false:字段被吞,写入却成功',
    method: 'PUT', path: '/tut-l11-false/_doc/1',
    body: { title: 'visible', note: 'swallowed' },
    predict: 'note 不在 mapping 里,这篇文档能写进去吗?',
    expect: 'result: created——没有报错。note 原样进 _source,但不进任何倒排结构:搜不到、聚合不到。对比 strict 的 400,false 是安静的丢失。'
  };
  window.ESEXPERIMENTS['ch11-14-false-mapping'] = {
    version: 1, id: 'ch11-14-false-mapping',
    title: '实验 3e · 对答案:mapping 里没有 note',
    method: 'GET', path: '/tut-l11-false/_mapping',
    body: null,
    predict: 'properties 里会有几个字段?note 在不在?',
    expect: '只有 title。写入成功 ≠ 可查询——排障第一步永远是 GET _mapping。想确认字段是否真的无处安身,可用 _field_caps?fields=note&include_unmapped=true,它会以 unmapped 身份显形。'
  };
  window.ESEXPERIMENTS['ch11-15-merge-conflict'] = {
    version: 1, id: 'ch11-15-merge-conflict',
    title: '实验 4a · 踩 merge 的墙:把 text 改成 keyword',
    method: 'PUT', path: '/tut-l11-inferred/_mapping',
    body: { properties: { title: { type: 'keyword' } } },
    predict: '状态码 400 还是 200?error.reason 的原文是哪一句?同一请求若只新增 status 字段会不会成功?',
    expect: '400。reason 链里能找到 mapper [title] cannot be changed from type [text] to [keyword](可能包在 Merge failed / caused_by 里,以你的返回为准)——FieldMapper.checkIncomingMergeType 先比 mapper Class 再比 contentType(),拼的就是这句。merge 看的是类型承诺,不是文档条数:零篇也改不了。'
  };
  window.ESEXPERIMENTS['ch11-16-merge-add'] = {
    version: 1, id: 'ch11-16-merge-add',
    title: '实验 4b · 对照:加新字段可以',
    method: 'PUT', path: '/tut-l11-inferred/_mapping',
    body: { properties: { status: { type: 'keyword' } } },
    predict: '同一个端点,只加一个 mapping 里没有的字段,结果?',
    expect: 'acknowledged: true。mapping 更新是 merge 不是 replace:新字段、新 multi-field、dynamic 参数(如 ignore_above)都能加能改;唯独已有字段的 type 不行。要换类型:新索引 + _reindex。'
  };
  window.ESEXPERIMENTS['ch11-17-field-caps'] = {
    version: 1, id: 'ch11-17-field-caps',
    title: '实验 5 · _field_caps 看字段能力',
    method: 'GET', path: '/tut-l11-inferred/_field_caps?fields=title,title.keyword,price,sku,qty,status',
    body: null,
    predict: 'title 相关会返回几行?text 与 keyword 的 aggregatable 各是 true 还是 false?',
    expect: 'title → text、title.keyword → keyword,同一份值两种能力并列;price → float、qty → long;status → keyword。每行带 searchable / aggregatable:text 行 aggregatable 是 false(无 doc_values),keyword/float 是 true——查询侧选 Query 前先看这份能力表(MappingLookup.getFieldType)。'
  };
  window.ESEXPERIMENTS['ch11-18-cleanup'] = {
    version: 1, id: 'ch11-18-cleanup',
    title: '清理 · 删除本课三个索引',
    method: 'DELETE', path: '/tut-l11-inferred,tut-l11-strict,tut-l11-false',
    body: null,
    predict: '一次 DELETE 多个索引,参数怎么写?',
    expect: 'acknowledged: true。索引连同推断出的 mapping 一起消失——下次重建同名片,又是一张白纸。'
  };
})();
