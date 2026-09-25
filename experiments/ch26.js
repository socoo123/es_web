/* experiments/ch26.js — 第 26 课:脚本引擎实验 + 一段脚本的编译旅程动画 */
(function () {
  'use strict';

  /* ===== 动画:一段脚本从字符串到 execute() ===== */
  function rect(x, y, w, h, cls, anim) {
    return '<rect x="' + x + '" y="' + y + '" width="' + w + '" height="' + h + '" rx="9" class="' + cls + (anim ? ' ' + anim : '') + '"/>';
  }
  function txt(x, y, s, cls, warn, anim) {
    var st = warn ? ' style="fill: rgb(var(--warn))"' : '';
    return '<text x="' + x + '" y="' + y + '" text-anchor="middle" class="' + cls + (anim ? ' ' + anim : '') + '"' + st + '>' + s + '</text>';
  }
  function arrow(id, x1, y1, x2, y2) {
    return '<line x1="' + x1 + '" y1="' + y1 + '" x2="' + x2 + '" y2="' + y2 + '" class="fig-arrow" marker-end="url(#' + id + ')"/>';
  }
  function defs(id) {
    return '<defs><marker id="' + id + '" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
      + '<path d="M 0 0 L 10 5 L 0 10 z" class="fig-arrowhead"/></marker></defs>';
  }
  function bottom(title, sub) {
    var s = rect(15, 240, 730, 48, 'fig-box-hot', 'fp-pop');
    s += txt(380, 261, title, 'fig-name');
    s += txt(380, 281, sub, 'fig-sub');
    return s;
  }

  /* 步骤 1:请求到达,还只是字符串 */
  function step1() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('k1');
    s += rect(15, 15, 730, 60, 'fig-box');
    s += txt(380, 38, 'POST /tut-l26-score/_search(script_score)', 'fig-name');
    s += txt(380, 60, 'query: match_all + script.source: doc[\'price\'].value * 0.9', 'fig-sub');
    s += rect(15, 90, 730, 60, 'fig-box');
    s += txt(380, 113, '此刻 source 只是一段 JSON 字符串', 'fig-key');
    s += txt(380, 135, '没有解析、没有查表、没有字节码——什么都不曾发生', 'fig-sub');
    s += rect(15, 165, 730, 54, 'fig-box');
    s += txt(380, 186, 'ScriptScoreQueryBuilder.doToQuery', 'fig-key');
    s += txt(380, 208, 'context.compile(script, ScoreScript.CONTEXT) —— 编译从这里开始', 'fig-sub');
    s += bottom('入口:评分脚本在内层 query 变成 Lucene Query 之前编译', 'query 为 null 连构造都过不了:REST 缺 query 实测 400 Required [query]');
    return s + '</svg>';
  }

  /* 步骤 2:ANTLR 解析成用户树 */
  function step2() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('k2');
    s += rect(15, 15, 730, 56, 'fig-box');
    s += txt(380, 38, 'Walker.buildPainlessTree → ANTLR PainlessParser', 'fig-name');
    s += txt(380, 60, '源码字符串 → 用户树 SClass(每个节点带 Location,供报错画 ^---- HERE)', 'fig-sub');
    s += rect(15, 88, 355, 76, 'fig-box');
    s += txt(192, 112, '这一步只认语法', 'fig-name');
    s += txt(192, 136, '括号配对、类型名长得像不像类', 'fig-sub');
    s += txt(192, 156, 'java.io.File 在这里还是普通字符', 'fig-sub');
    s += rect(390, 88, 355, 76, 'fig-box');
    s += txt(567, 112, '还不认识任何类型', 'fig-name');
    s += txt(567, 136, 'value 是不是字段?乘法有没有定义?', 'fig-sub');
    s += txt(567, 156, '全部留给下一跳:语义分析', 'fig-sub');
    s += rect(15, 180, 730, 44, 'fig-box');
    s += txt(380, 200, '「不是 eval」证据一:先有树,再谈名字', 'fig-sub');
    s += txt(380, 217, 'eval 会在运行时才拿字符串去找类;这里树先建好,等表来审', 'fig-sub');
    s += bottom('解析:语法层完成,类型问题原封未动', 'AST 只是中间态——离字节码还有两道检查');
    return s + '</svg>';
  }

  /* 步骤 3:语义分析对照 Lookup */
  function step3() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('k3');
    s += rect(15, 15, 730, 56, 'fig-box-hot');
    s += txt(380, 38, 'PainlessSemanticAnalysisPhase:逐个名字对照 PainlessLookup', 'fig-name');
    s += txt(380, 60, '这张表由 PainlessPlugin.baseWhiteList() 的 txt + context 叠加 txt 装出,构造时冻住', 'fig-sub');
    s += rect(15, 88, 355, 92, 'fig-box');
    s += txt(192, 110, '基础白名单(共享)', 'fig-name');
    s += txt(192, 132, 'java.lang / java.util / java.time*', 'fig-sub');
    s += txt(192, 152, 'java.math / java.text / java.util.regex', 'fig-sub');
    s += txt(192, 172, 'java.nio(Buffer 家族,无 Path)', 'fig-sub');
    s += rect(390, 88, 355, 92, 'fig-box');
    s += txt(567, 110, 'score context 叠加', 'fig-name');
    s += txt(567, 132, 'org.elasticsearch.script.score.txt', 'fig-sub');
    s += txt(567, 152, '加 saturation / decayGeoGauss 绑定', 'fig-sub');
    s += txt(567, 172, '只加不减:File 不会回来', 'fig-sub');
    s += rect(15, 196, 730, 30, 'fig-box');
    s += txt(380, 215, 'doc[...] 取值、value、乘法:都在表上 → 通过', 'fig-key');
    s += bottom('语义分析:脚本能叫出名字的类,必须先写在 txt 里', 'canonicalTypeNameToType 查不到返回 null——没有 Class.forName 的后路');
    return s + '</svg>';
  }

  /* 步骤 4:IR + ASM 写出 byte[] */
  function step4() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('k4');
    s += rect(15, 15, 730, 56, 'fig-box');
    s += txt(380, 38, '用户树 → IR(ClassNode):PainlessUserTreeToIRTreePhase', 'fig-name');
    s += txt(380, 60, '顺手做常量折叠、字符串拼接优化——编译器该有的都有', 'fig-sub');
    s += rect(15, 88, 355, 76, 'fig-box');
    s += txt(192, 112, 'DefaultIRTreeToASMBytesPhase', 'fig-name');
    s += txt(192, 136, 'IR → byte[](真的 JVM 字节码)', 'fig-sub');
    s += txt(192, 156, '类名固定 PainlessScript$Script', 'fig-sub');
    s += rect(390, 88, 355, 76, 'fig-box-hot', 'fp-pop');
    s += txt(567, 112, '产物是一个 class', 'fig-name');
    s += txt(567, 136, '不是解释器里的语法树', 'fig-sub');
    s += txt(567, 156, 'execute() 是真方法,JIT 可优化', 'fig-sub');
    s += rect(15, 180, 730, 44, 'fig-box');
    s += txt(380, 200, '对照 eval:eval 每次执行都重新理解字符串', 'fig-sub');
    s += txt(380, 217, '这里理解一次,之后只剩方法调用', 'fig-sub');
    s += bottom('字节码生成:通过检查的树,落成可加载的 class', '常量池里只可能出现在 txt 表上的类型——这就是安全宇宙');
    return s + '</svg>';
  }

  /* 步骤 5:加载与缓存 */
  function step5() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('k5');
    s += rect(15, 15, 355, 96, 'fig-box');
    s += txt(192, 39, 'Loader.defineScript', 'fig-name');
    s += txt(192, 63, '继承 SecureClassLoader', 'fig-sub');
    s += txt(192, 83, 'CodeSource 指向 UNTRUSTED_CODEBASE', 'fig-sub');
    s += txt(192, 103, 'findClass 只认 Lookup 里那几个类', 'fig-sub');
    s += rect(390, 15, 355, 96, 'fig-box-hot', 'fp-pop');
    s += txt(567, 39, 'ScriptCache.computeIfAbsent', 'fig-name');
    s += txt(567, 63, 'key = context + 源码 + params', 'fig-sub');
    s += txt(567, 83, '千篇文档只编译这一次', 'fig-sub');
    s += txt(567, 103, '「不是逐文档 eval」证据二', 'fig-sub');
    s += rect(15, 128, 730, 92, 'fig-box');
    s += txt(380, 152, 'factory.newFactory(params, lookup)', 'fig-key');
    s += txt(380, 176, '每个 shard 拿 factory 造 LeafFactory,逐段读 doc values', 'fig-sub');
    s += txt(380, 196, 'ScoreScript.get_score() 就是脚本里的 _score 变量', 'fig-sub');
    s += txt(380, 216, '编译一次,实例随请求生灭', 'fig-sub');
    s += bottom('加载 + 缓存:同一句脚本在整个集群生命周期里通常只编一次', 'context 不同则另算:score 与 ingest 各有各的缓存条目');
    return s + '</svg>';
  }

  /* 步骤 6:每篇文档调 execute() */
  function step6() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('k6');
    s += rect(15, 15, 730, 50, 'fig-box');
    s += txt(380, 36, '内层 match_all 的 _score = 1.0', 'fig-name');
    s += txt(380, 56, '对每篇命中文档调 execute():_score * doc[\'popularity\'].value / 100', 'fig-sub');
    s += rect(15, 80, 355, 76, 'fig-box');
    s += txt(192, 103, 'cheap: popularity=10', 'fig-name');
    s += txt(192, 127, '1.0 * 10 / 100 = 0.1', 'fig-key');
    s += txt(192, 147, '读的是 doc values,不是 _source', 'fig-sub');
    s += rect(390, 80, 355, 76, 'fig-box');
    s += txt(567, 103, 'popular: popularity=100', 'fig-name');
    s += txt(567, 127, '1.0 * 100 / 100 = 1.0', 'fig-key');
    s += txt(567, 147, '排在前,和 BM25 无关', 'fig-sub');
    s += rect(15, 172, 730, 54, 'fig-box');
    s += txt(380, 193, '换成 doc[\'price\'].value * 0.9:cheap 90 / popular 72', 'fig-key');
    s += txt(380, 215, 'script_score 完全替换内层分数——和 function_score 的乘一层不同(第 20 课)', 'fig-sub');
    s += bottom('执行期:只剩方法调用,没有解析、没有查表', 'CPU 花在算术与 doc values 读取上——expensive 开关管的就是这笔');
    return s + '</svg>';
  }

  /* 步骤 7:对照支线——File 在第 3 步就死了 */
  function step7() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('k7');
    s += rect(15, 15, 730, 50, 'fig-box');
    s += txt(380, 36, '对照:source = new java.io.File("/tmp/x")', 'fig-name');
    s += txt(380, 56, '同样走到语义分析(visitNewObj),接下来发生什么?', 'fig-sub');
    s += rect(15, 80, 355, 60, 'fig-box');
    s += txt(192, 103, 'canonicalTypeNameToType 查表', 'fig-name');
    s += txt(192, 127, 'java.io 不在任何 txt 里 → null', 'fig-sub');
    s += rect(390, 80, 355, 60, 'fig-box-hot', 'fp-pop');
    s += txt(567, 103, 'Not a type [java.io.File].', 'fig-name', true);
    s += txt(567, 127, 'IllegalArgumentException,位置信息画 ^---- HERE', 'fig-sub');
    s += rect(15, 156, 730, 70, 'fig-box');
    s += txt(380, 179, 'IR / ASM / defineClass 一行都没跑', 'fig-key');
    s += txt(380, 201, '包装成 ScriptException("compile error") → HTTP 400', 'fig-sub');
    s += txt(380, 221, '"/tmp/x" 从未被当成文件系统参数——磁盘无事发生', 'fig-sub');
    s += bottom('拒绝发生在编译期:产物是异常,不是一个会打开文件的 class', '声明写法走 visitDeclaration:cannot resolve type——同一张表,同一死法');
    return s + '</svg>';
  }

  window.ESFLOWS = window.ESFLOWS || {};
  window.ESFLOWS['ch26-script-compile'] = {
    version: 1,
    id: 'ch26-script-compile',
    title: '一段脚本从字符串到 execute()',
    speed: 2400,
    steps: [
      { svg: step1(), note: 'script_score 请求到达:source 此刻只是一段 JSON 字符串。ScriptScoreQueryBuilder.doToQuery 调 context.compile(script, ScoreScript.CONTEXT),编译从这里开始;query 缺失连构造都过不了。' },
      { svg: step2(), note: 'ANTLR 把源码解析成用户树 SClass——纯语法层,java.io.File 在这里只是普通字符,类型问题原封未动。「不是 eval」证据一:先有树,再谈名字。' },
      { svg: step3(), note: '语义分析逐个名字对照 PainlessLookup:基础白名单 txt(java.lang/util/time/nio 的 Buffer 家族)+ context 叠加 txt(只加不减)。查不到返回 null,没有 Class.forName 后路。' },
      { svg: step4(), note: '通过检查的树降成 IR,常量折叠后由 ASM 写出真的 byte[]——类名 PainlessScript$Script。产物是一个 class,不是解释器里的语法树;常量池里只可能出现表上的类型。' },
      { svg: step5(), note: 'Loader(SecureClassLoader,UNTRUSTED_CODEBASE)defineClass;ScriptCache 按 context+源码缓存——千篇文档只编译一次,这是「不是逐文档 eval」的第二条证据。' },
      { svg: step6(), note: '执行期只剩方法调用:match_all 内层 1.0,cheap 算出 0.1、popular 1.0;换 price*0.9 则是 90/72——script_score 完全替换内层分数,与 function_score 的乘一层不同。' },
      { svg: step7(), note: '对照支线:new java.io.File 在语义分析就死——canonicalTypeNameToType 返回 null,Not a type,HTTP 400;IR/ASM/defineClass 一行没跑,磁盘从未被碰。拒绝发生在编译期。' }
    ]
  };

  /* ===== 实验 ===== */
  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};

  window.ESEXPERIMENTS['ch26-01-setup'] = {
    version: 1, id: 'ch26-01-setup',
    title: '实验 1 · 建 tut-l26-score(price/popularity打底)',
    method: 'PUT', path: '/tut-l26-score',
    body: { mappings: { properties: { title: { type: 'keyword' }, popularity: { type: 'long' }, price: { type: 'double' } } } },
    predict: '脚本读 doc[\'popularity\'] 需要什么字段类型?text 行吗?',
    expect: 'acknowledged: true。数值型(doc values)即可;text 默认不分 doc values,脚本读 .value 会取分析后的词而非数值——这也是脚本读的是 doc values 不是 _source 的伏笔。'
  };

  window.ESEXPERIMENTS['ch26-02-bulk'] = {
    version: 1, id: 'ch26-02-bulk',
    title: '实验 2 · 两篇文档:cheap(10/100)与 popular(100/80)',
    method: 'POST', path: '/tut-l26-score/_bulk?refresh=true',
    body: '{"index":{"_id":"cheap"}}\n{"title":"obscure","popularity":10,"price":100.0}\n{"index":{"_id":"popular"}}\n{"title":"hit","popularity":100,"price":80.0}\n',
    predict: 'match_all 的 _score 会是多少?',
    expect: 'errors: false。match_all 每篇都是常数 1.0(不是 BM25)——下一个实验的脚本分数就建立在它之上;若你猜了 BM25,是把第 20 课的相关性评分和过滤型查询混了。'
  };

  window.ESEXPERIMENTS['ch26-03-score-pop'] = {
    version: 1, id: 'ch26-03-score-pop',
    title: '实验 3 · 最小 script_score:分数乘 popularity',
    method: 'POST',
    path: '/tut-l26-score/_search?filter_path=hits.hits._id,hits.hits._score',
    body: { query: { script_score: { query: { match_all: {} }, script: { source: "_score * doc['popularity'].value / 100" } } } },
    predict: '先猜:cheap(10)和 popular(100)的 _score 各是多少?谁在前?',
    expect: 'popular 1.0 在前,cheap 0.1。源码此刻已编成 ScoreScript.CONTEXT 的 class(ScriptScoreQueryBuilder.doToQuery 里 context.compile),对每篇命中文档调 execute()——不是每篇重新 parse 字符串。猜错多半是把 _score 当成了 BM25。'
  };

  window.ESEXPERIMENTS['ch26-04-score-price'] = {
    version: 1, id: 'ch26-04-score-price',
    title: '实验 4 · 换一句:doc[\'price\'].value * 0.9',
    method: 'POST',
    path: '/tut-l26-score/_search?filter_path=hits.hits._id,hits.hits._score',
    body: { query: { script_score: { query: { match_all: {} }, script: { source: "doc['price'].value * 0.9" } } } },
    predict: '这次的 _score 跟 popularity 还有关系吗?和第 20 课 function_score 的乘一层一样吗?',
    expect: 'cheap 90、popular 72——popularity 完全出局。script_score 是整体替换内层分数;function_score(第 20 课)是在原分上再乘一层。新源码是新缓存条目:与实验 3 各编各的 class。'
  };

  window.ESEXPERIMENTS['ch26-05-script-fields'] = {
    version: 1, id: 'ch26-05-script-fields',
    title: '实验 5 · script_fields:不改分,只多一个返回字段',
    method: 'POST',
    path: '/tut-l26-score/_search?filter_path=hits.hits._id,hits.hits._score,hits.hits.fields',
    body: { script_fields: { discounted_price: { script: { source: "doc['price'].value * params.discount", params: { discount: 0.8 } } } } },
    predict: '_score 会变吗?折扣价出现在哪一节?',
    expect: '_score 仍是 1.0(不改分);hits.fields.discounted_price = [80.0] / [64.0]。script_fields 编进第四个 context "field"(FieldScript.CONTEXT)——算返回值,不碰磁盘上的 _source。'
  };

  window.ESEXPERIMENTS['ch26-06-update'] = {
    version: 1, id: 'ch26-06-update',
    title: '实验 6 · update 脚本:ctx._source.views = 1',
    method: 'POST', path: '/tut-l26-score/_update/cheap?refresh=true',
    body: { script: { source: 'ctx._source.views = params.count', params: { count: 1 } } },
    predict: 'views 字段原来不存在,直接赋值会报错吗?',
    expect: 'result: updated、_version: 2。ctx._source 是 Map,新键直接放入——和 += 不同(对 null 做 += 才会 NPE,那和白名单无关,是数据问题)。这句编进 UpdateScript.CONTEXT("update")。'
  };

  window.ESEXPERIMENTS['ch26-07-get-cheap'] = {
    version: 1, id: 'ch26-07-get-cheap',
    title: '实验 7 · GET 回看:views 进了 _source',
    method: 'GET', path: '/tut-l26-score/_doc/cheap?filter_path=_source',
    body: null,
    predict: '_source 里会多出什么?popularity 还在吗?',
    expect: '_source 多了 views: 1,popularity: 10 原样。update 脚本改的是文档 _source 本体(重索引);对比实验 5 的 script_fields 只在响应里现算——一个落盘一个不落,context 决定脚本能摸到什么。'
  };

  window.ESEXPERIMENTS['ch26-08-pipeline-put'] = {
    version: 1, id: 'ch26-08-pipeline-put',
    title: '实验 8 · PUT 摄取管道:fullname 拼接脚本',
    method: 'PUT', path: '/_ingest/pipeline/tut-l26-script',
    body: { processors: [{ script: { source: "ctx.fullname = ctx.first_name + ' ' + ctx.last_name" } }] },
    predict: 'PUT 这一刻脚本编译了吗,还是等第一条文档?',
    expect: 'acknowledged: true。ScriptProcessor 在 PUT pipeline 时就 compile 成 IngestScript.CONTEXT 的 factory(第 12 课的链提前到建管道)——所以下一个破坏实验里,坏脚本活不到第一条文档。'
  };

  window.ESEXPERIMENTS['ch26-09-simulate'] = {
    version: 1, id: 'ch26-09-simulate',
    title: '实验 9 · _simulate:ingest 上下文的 ctx',
    method: 'POST', path: '/_ingest/pipeline/tut-l26-script/_simulate',
    body: { docs: [{ _source: { first_name: 'Grace', last_name: 'Hopper' } }] },
    predict: 'fullname 出现在哪里?这条命令选 shard 吗?',
    expect: 'docs[0]._source 多了 fullname: "Grace Hopper"。_simulate 跑的是同一条 Pipeline.execute,不选 shard(第 12 课);ctx 是 ingest context 独有的绑定——score context 里没有它。'
  };

  window.ESEXPERIMENTS['ch26-10-file-execute'] = {
    version: 1, id: 'ch26-10-file-execute',
    title: '实验 10 · 破坏:new java.io.File(_execute 直测)',
    method: 'POST',
    path: '/_scripts/painless/_execute?filter_path=error.type,error.reason,error.caused_by.reason,error.script_stack,error.status',
    body: { script: { source: 'return new java.io.File("/tmp/painless-should-not-exist");' } },
    predict: '会在磁盘建文件吗?HTTP 200 还是 400?error.reason 与 caused_by.reason 各是什么?',
    expect: 'HTTP 400:reason=compile error,caused_by.reason=Not a type [java.io.File].,script_stack 画着 ^---- HERE。类型不在 txt 宇宙里,visitNewObj 直接抛——IR/ASM 一行没跑,路径字符串从未被当成文件系统参数(实测 /tmp 无此文件)。猜 SecurityException/文件被建,是把 Painless 当 eval。'
  };

  window.ESEXPERIMENTS['ch26-11-file-search'] = {
    version: 1, id: 'ch26-11-file-search',
    title: '实验 11 · 破坏:同一句塞进 script_score',
    method: 'POST',
    path: '/tut-l26-score/_search?filter_path=error.type,error.reason,error.root_cause.caused_by.reason,error.failed_shards.reason.caused_by.reason',
    body: { query: { script_score: { query: { match_all: {} }, script: { source: 'return new java.io.File("/tmp/x");' } } } },
    predict: '还是 400 吗?caused_by 还能找到那句话吗?',
    expect: '400,但外层包成 search_phase_execution_exception(all shards failed)。往 root_cause / failed_shards 里挖,caused_by.reason 仍是同一个 Not a type [java.io.File].——编译错误发生在 shard 侧建查询时,包装层换皮不换骨。'
  };

  window.ESEXPERIMENTS['ch26-12-file-pipeline'] = {
    version: 1, id: 'ch26-12-file-pipeline',
    title: '实验 12 · 破坏:File 写进 pipeline,PUT 当场失败',
    method: 'PUT', path: '/_ingest/pipeline/tut-l26-file',
    body: { processors: [{ script: { source: 'ctx.f = new java.io.File("/tmp/x")' } }] },
    predict: '这条 PUT 能成功吗?若能,坏脚本什么时候爆?',
    expect: 'HTTP 400,PUT 直接失败——ingest 的 script processor 在建管道时就 compile(实验 8 说过),第一条文档还没到来。对照:若编译被推迟到写入期,每条文档都会撞一次同一个错误,还可能写脏数据。'
  };

  window.ESEXPERIMENTS['ch26-13-decl'] = {
    version: 1, id: 'ch26-13-decl',
    title: '实验 13 · 声明写法:cannot resolve type',
    method: 'POST',
    path: '/_scripts/painless/_execute?filter_path=error.reason,error.caused_by.reason,error.position.offset',
    body: { script: { source: 'java.io.File f = null; return 1;' } },
    predict: '还是 Not a type 吗?报错位置指向哪个字符?',
    expect: 'caused_by.reason=invalid declaration: cannot resolve type [java.io.File]——声明走 visitDeclaration,new 走 visitNewObj,同一张 Lookup 两条入口。offset=13 指着类型名:Location 只管画箭头,不改文案。'
  };

  window.ESEXPERIMENTS['ch26-14-getclass'] = {
    version: 1, id: 'ch26-14-getclass',
    title: '实验 14 · 反射入口:String s.getClass()',
    method: 'POST',
    path: '/_scripts/painless/_execute?filter_path=error.reason,error.caused_by.reason',
    body: { script: { source: 'String s = "x"; return s.getClass();' } },
    predict: 'getClass 在白名单里吗?错误发生在编译期还是运行期?',
    expect: 'compile error + member method [java.lang.String, getClass/0] not found——静态类型让编译器当场查表。把 source 改成 def x = 1; return x.getClass(); 再跑:变 runtime error + dynamic method [java.lang.Integer, getClass/0] not found——def 推迟到运行期查,但同一张表,反射入口不存在。'
  };

  window.ESEXPERIMENTS['ch26-15-context-classes'] = {
    version: 1, id: 'ch26-15-context-classes',
    title: '实验 15 · score context 的类型宇宙(404 个类)',
    method: 'GET', path: '/_scripts/painless/_context?context=score&filter_path=classes.name',
    body: null,
    predict: 'classes 里能找到 java.io.File / java.lang.Runtime / java.lang.String 中的哪几个?',
    expect: '用 Ctrl+F 搜:java.lang.String 在;java.io.File、java.lang.Runtime 都不在。PainlessContextAction 把当前 context 的 PainlessLookup 序列化成 classes——就是语义分析查的那张表的运行时投影。score 叠加的 txt 只加评分函数,不会放开 JDK。'
  };

  window.ESEXPERIMENTS['ch26-16-expensive-off'] = {
    version: 1, id: 'ch26-16-expensive-off',
    title: '实验 16 · 破坏:allow_expensive_queries=false',
    method: 'PUT', path: '/_cluster/settings',
    body: { transient: { 'search.allow_expensive_queries': false } },
    predict: '脚本只是 return 1.0(已白名单化、编译过),还会被拒吗?',
    expect: 'acknowledged: true。会——doToQuery 第一件事就是查 allowExpensiveQueries,在 compile 之前。这是第二层开关:白名单管「能不能编译」(安全宇宙),expensive 管「集群愿不愿意按文档跑脚本」(容量)。课末必须 null 恢复。'
  };

  window.ESEXPERIMENTS['ch26-17-expensive-reject'] = {
    version: 1, id: 'ch26-17-expensive-reject',
    title: '实验 17 · 无害脚本也被拒:query_shard_exception',
    method: 'POST',
    path: '/tut-l26-score/_search?filter_path=error.root_cause.reason,error.caused_by.reason',
    body: { query: { script_score: { query: { match_all: {} }, script: { source: 'return 1.0;' } } } },
    predict: '拒绝发生在建查询阶段还是执行阶段?文案会提哪个设置?',
    expect: 'root_cause 是 query_shard_exception:failed to create query + [script score] queries cannot be executed when \'search.allow_expensive_queries\' is set to false.——脚本再干净也拦,因为成本在按文档 execute,不在编译(思考题 3)。'
  };

  window.ESEXPERIMENTS['ch26-18-restore'] = {
    version: 1, id: 'ch26-18-restore',
    title: '清理 · null 恢复 expensive 开关(必做)',
    method: 'PUT', path: '/_cluster/settings',
    body: { transient: { 'search.allow_expensive_queries': null } },
    predict: 'null 是设成字符串 "null" 吗?',
    expect: 'acknowledged: true。null = 删掉覆盖回到默认 true(第 5 课语义)。留着 false,本机所有 script_score / scripting 查询会一直被拒——破坏实验收尾不是可选项。'
  };

  window.ESEXPERIMENTS['ch26-19-cleanup'] = {
    version: 1, id: 'ch26-19-cleanup',
    title: '清理 · 删 tut-l26-score',
    method: 'DELETE', path: '/tut-l26-score',
    predict: '一句话总结本课?',
    expect: 'acknowledged: true。Painless 是「源码 → 白名单检查 → 字节码 → SecureClassLoader 加载缓存」:类型宇宙里没有的名字在编译期就死(Not a type / cannot resolve type / member|dynamic method not found 三连),产物是 class 不是解释执行;千篇文档共用一个 execute()。'
  };

  window.ESEXPERIMENTS['ch26-20-cleanup-pipeline'] = {
    version: 1, id: 'ch26-20-cleanup-pipeline',
    title: '清理 · 删管道 tut-l26-script',
    method: 'DELETE', path: '/_ingest/pipeline/tut-l26-script',
    predict: 'tut-l26-file 需要删吗?',
    expect: 'acknowledged: true。不需要——实验 12 那条 PUT 从未成功,管道不存在。顺手验证:GET /_ingest/pipeline/tut-l26-file 会 404(资源不存在),和未知路由的 400 是两回事(第 7 课口径)。'
  };
})();
