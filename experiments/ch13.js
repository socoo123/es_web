/* experiments/ch13.js — 第 13 课:bulk 协议实验 + 按 shard 拆组分发动画(注册表) */
(function () {
  'use strict';

  /* ===== 动画:一次 _bulk,切条目、算路由、按 shard 分组 ===== */
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

  /* 步骤 1:NDJSON 请求到达 */
  function step1() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('ah13s1');
    s += rect(15, 25, 390, 240, 'fig-box-hot', 'fp-pop');
    s += txt(210, 50, 'POST /_bulk', 'fig-key');
    var lines = [
      '{"index":{"_index":"t","_id":"1"}}',
      '{"title":"A"}',
      '{"create":{"_index":"t","_id":"2"}}',
      '{"title":"B"}',
      '{"delete":{"_index":"t","_id":"3"}}'
    ];
    for (var i = 0; i < lines.length; i++) s += txt(210, 82 + i * 24, lines[i], 'fig-sub');
    s += txt(210, 208, '(delete 没有 source 行)', 'fig-sub');
    s += txt(210, 238, '每行(含最后一行)以 \\n 结尾', 'fig-sub');
    s += rect(425, 25, 320, 110, 'fig-box');
    s += txt(585, 50, '两行一组', 'fig-name');
    s += txt(585, 72, 'action 行:做什么、写到哪', 'fig-sub');
    s += txt(585, 94, 'source 行:文档 JSON(delete 除外)', 'fig-sub');
    s += rect(425, 155, 320, 110, 'fig-box');
    s += txt(585, 180, '六行 = 三个条目', 'fig-name');
    s += txt(585, 202, 'index / create / delete 混批', 'fig-sub');
    s += txt(585, 224, '条目之间互不担保', 'fig-sub');
    return s + '</svg>';
  }

  /* 步骤 2:切成条目 */
  function step2() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('ah13s2');
    s += rect(230, 15, 300, 52, 'fig-box');
    s += txt(380, 37, 'BulkRequestParser 按行切', 'fig-name');
    s += txt(380, 57, 'action 行此刻解析,非法即 400', 'fig-sub');
    s += line(340, 67, 137, 91, 'ah13s2');
    s += line(380, 67, 377, 91, 'ah13s2');
    s += line(420, 67, 617, 91, 'ah13s2');
    var cards = [
      { x: 15, op: '条目[0] index', key: '_id = "1"', sub1: 'source 原样收下', sub2: '此刻不解析 JSON' },
      { x: 265, op: '条目[1] create', key: '_id = "2"', sub1: '已存在则 409', sub2: 'source 原样收下' },
      { x: 515, op: '条目[2] delete', key: '_id = "3"', sub1: '无 source 行', sub2: '单行成项' }
    ];
    for (var i = 0; i < 3; i++) {
      var c = cards[i], cx = c.x + 112;
      s += rect(c.x, 95, 225, 110, i === 0 ? 'fig-box-hot' : 'fig-box', i === 0 ? 'fp-pop' : null);
      s += txt(cx, 120, c.op, 'fig-name');
      s += txt(cx, 147, c.key, 'fig-key');
      s += txt(cx, 172, c.sub1, 'fig-sub');
      s += txt(cx, 192, c.sub2, 'fig-sub');
    }
    s += rect(15, 235, 730, 55, 'fig-box');
    s += txt(380, 258, 'source 行此刻不解析 JSON——失败推迟到 primary 上才爆', 'fig-sub');
    s += txt(380, 280, '条目顺序 = 数组下标,响应按它对齐', 'fig-sub');
    return s + '</svg>';
  }

  /* 步骤 3:逐条路由 */
  function step3() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('ah13s3');
    var cols = [
      { op: 'index · _id="1"', h: 'Murmur3("1")', hv: '-126235597', m: '= 1 → shard 1', hot: false },
      { op: 'create · _id="2"', h: 'Murmur3("2")', hv: '-303927213', m: '= 1 → shard 1', hot: false },
      { op: 'delete · _id="3"', h: 'Murmur3("3")', hv: '-1151172406', m: '= 0 → shard 0', hot: true }
    ];
    for (var i = 0; i < 3; i++) {
      var c = cols[i], x = 15 + i * 250, cx = x + 112;
      s += rect(x, 15, 225, 64, 'fig-box');
      s += txt(cx, 38, c.op, 'fig-name');
      s += txt(cx, 58, '无 routing,键 = _id', 'fig-sub');
      s += line(cx, 79, cx, 103, 'ah13s3');
      s += rect(x, 107, 225, 58, 'fig-box');
      s += txt(cx, 130, c.h, 'fig-key');
      s += txt(cx, 150, c.hv, 'fig-sub');
      s += line(cx, 165, cx, 191, 'ah13s3');
      s += rect(x, 195, 225, 56, c.hot ? 'fig-box-hot' : 'fig-box', c.hot ? 'fp-pop' : null);
      s += txt(cx, 218, 'floorMod(…,2)', 'fig-key');
      s += txt(cx, 238, c.m, 'fig-sub');
    }
    s += txt(380, 282, '有效键 = routing ?? _id;不是 round-robin,不是把 _id 当整数取模', 'fig-sub');
    return s + '</svg>';
  }

  /* 步骤 4:按 ShardId 分组、并行发往 primary */
  function step4() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('ah13s4');
    var chips = ['条目[0] _id="1"', '条目[1] _id="2"', '条目[2] _id="3"'];
    for (var i = 0; i < 3; i++) {
      s += rect(15 + i * 250, 15, 225, 44, 'fig-box');
      s += txt(127 + i * 250, 42, chips[i], 'fig-sub');
    }
    s += line(150, 59, 235, 103, 'ah13s4');
    s += line(377, 59, 320, 103, 'ah13s4');
    s += line(604, 59, 560, 103, 'ah13s4');
    s += rect(15, 107, 360, 92, 'fig-box-hot', 'fp-pop');
    s += txt(195, 132, 'ShardId(t, 1)', 'fig-name');
    s += txt(195, 157, 'BulkShardRequest', 'fig-key');
    s += txt(195, 180, '条目[0] + 条目[1]', 'fig-sub');
    s += rect(385, 107, 360, 92, 'fig-box-hot', 'fp-pop');
    s += txt(565, 132, 'ShardId(t, 0)', 'fig-name');
    s += txt(565, 157, 'BulkShardRequest', 'fig-key');
    s += txt(565, 180, '条目[2]', 'fig-sub');
    s += line(195, 199, 195, 223, 'ah13s4');
    s += line(565, 199, 565, 223, 'ah13s4');
    s += rect(15, 227, 360, 52, 'fig-box');
    s += txt(195, 250, 'shard 1 primary', 'fig-name');
    s += txt(195, 270, '并行发出', 'fig-sub');
    s += rect(385, 227, 360, 52, 'fig-box');
    s += txt(565, 250, 'shard 0 primary', 'fig-name');
    s += txt(565, 270, '并行发出', 'fig-sub');
    s += txt(380, 294, 'executeLocally 在本节点启动;ReroutePhase 转发到 primary 所在节点', 'fig-sub');
    return s + '</svg>';
  }

  /* 步骤 5:primary 逐项执行 */
  function step5() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('ah13s5');
    s += rect(15, 20, 440, 170, 'fig-box');
    s += '<text x="35" y="45" class="fig-name">shard 1 primary 逐项执行</text>';
    s += '<text x="35" y="75" class="fig-sub">条目[0] index _id="1"</text>';
    s += '<text x="35" y="95" class="fig-key">→ 201 created,领 seq_no=0</text>';
    s += '<text x="35" y="120" class="fig-sub">条目[1] create _id="2"(已存在)</text>';
    s += '<text x="35" y="140" class="fig-key" style="fill: rgb(var(--warn))">→ 409 版本冲突,未领 seq_no</text>';
    s += '<text x="35" y="165" class="fig-sub">失败也 advance(),继续下一项</text>';
    s += rect(475, 20, 270, 170, 'fig-box');
    s += '<text x="495" y="45" class="fig-name">shard 0 primary</text>';
    s += '<text x="495" y="75" class="fig-sub">条目[2] delete _id="3"</text>';
    s += '<text x="495" y="95" class="fig-key" style="fill: rgb(var(--warn))">→ 404 not_found</text>';
    s += '<text x="495" y="120" class="fig-sub">delete 一个不存在的 _id</text>';
    s += '<text x="495" y="140" class="fig-sub">不是 failure(无 error 字段)</text>';
    s += rect(15, 215, 730, 70, 'fig-box-hot');
    s += txt(380, 238, '一项失败 ≠ 整批失败', 'fig-name');
    s += txt(380, 260, 'BulkPrimaryExecutionContext:FAILURE 也 advance() 进下一项', 'fig-sub');
    s += txt(380, 278, '成功项之后带 seq_no 复制给 replica(细节下一课)', 'fig-sub');
    return s + '</svg>';
  }

  /* 步骤 6:汇总响应 */
  function step6() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('ah13s6');
    s += rect(15, 20, 730, 56, 'fig-box-hot', 'fp-pop');
    s += txt(380, 43, 'HTTP 200 · errors: true', 'fig-name');
    s += txt(380, 65, 'errors 来自 BulkResponse.hasFailures() 扫 items', 'fig-sub');
    s += line(127, 76, 127, 104, 'ah13s6');
    s += line(377, 76, 377, 104, 'ah13s6');
    s += line(627, 76, 627, 104, 'ah13s6');
    var cards = [
      { x: 15, n: 'items[0] · 201', k: 'index _id="1"', s1: 'created', s2: 'seq_no 复制给 replica', warn: false },
      { x: 265, n: 'items[1] · 409', k: 'create 撞已有 _id', s1: 'error: version_conflict', s2: '失败只记这一项', warn: true },
      { x: 515, n: 'items[2] · 404', k: 'delete _id="3"', s1: 'result: not_found', s2: '无 error 字段,不算失败', warn: false }
    ];
    for (var i = 0; i < 3; i++) {
      var c = cards[i], cx = c.x + 112;
      s += rect(c.x, 108, 225, 110, 'fig-box');
      s += txt(cx, 133, c.n, 'fig-name', c.warn);
      s += txt(cx, 158, c.k, 'fig-key');
      s += txt(cx, 180, c.s1, 'fig-sub');
      s += txt(cx, 200, c.s2, 'fig-sub');
    }
    s += rect(15, 238, 730, 48, 'fig-box');
    s += txt(380, 268, 'items[] 与 NDJSON 行序一一对应,不按 shard 排序——客户端必须逐项扫 status', 'fig-sub');
    return s + '</svg>';
  }

  window.ESFLOWS = window.ESFLOWS || {};
  window.ESFLOWS['ch13-bulk-group'] = {
    version: 1,
    id: 'ch13-bulk-group',
    title: '一次 _bulk:切条目、算路由、按 shard 分组',
    speed: 2200,
    steps: [
      { svg: step1(), note: '一次 _bulk 的 body 是 NDJSON:一行 JSON 一个换行。奇数行是 action(index/create/update/delete),偶数行是 source;delete 没有 source 行。所有行(含最后一行)必须以 \\n 结尾——这是后面 400 的来源。' },
      { svg: step2(), note: 'REST 层按行切成有序条目。action 行此刻就被解析(不是合法 JSON 对象则整请求 400);source 行只按字节切片交给 IndexRequest.source(),不解析 JSON——失败推迟到 primary 才爆,这是条级失败的伏笔。' },
      { svg: step3(), note: '每条独立路由:有效键 = routing ?? _id,Murmur3HashFunction.hash 之后 Math.floorMod(hash, 2)。Java 的 % 对负数向零截断,源码用的是 floorMod。"1"、"2" 都余 1,"3" 余 0——落点跟字符串哈希走,不跟数字大小走。' },
      { svg: step4(), note: 'BulkOperation 按 ShardId 归堆(computeIfAbsent),每堆一份 BulkShardRequest(带 refresh / waitForActiveShards),多个 shard 并行发出。executeLocally 只是在本节点启动 shard 级 action,真正转发到 primary 所在节点的是 ReroutePhase。' },
      { svg: step5(), note: 'performOnPrimary 里一个 while 循环逐项执行:create 撞已有 _id 记 409,delete 不存在的 _id 记 not_found,都只记在那一项上,循环继续。成功项在 primary 领 seq_no 之后才复制给 replica;失败且未领号的项,replica 直接跳过。' },
      { svg: step6(), note: '所有 shard 的应答汇成 BulkResponse:HTTP 200 只说明整批被受理并执行完,有没有失败看顶层 errors(hasFailures() 扫 items)。items[] 按原始行序回填,不按 shard 排序——只盯状态码的客户端会把失败项悄悄丢掉。' }
    ]
  };

  /* ===== 实验 ===== */
  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};

  window.ESEXPERIMENTS['ch13-00-setup'] = {
    version: 1, id: 'ch13-00-setup',
    title: '实验 0 · 建索引 tut-l13-items(2 主分片 0 副本)',
    method: 'PUT', path: '/tut-l13-items',
    body: { settings: { number_of_shards: 2, number_of_replicas: 0 } },
    predict: '单节点为什么敢写 0 副本?这一课要观察的是什么粒度?',
    expect: 'acknowledged: true。0 副本让单节点立刻 green,把「复制」变量先拿掉——本课聚焦 bulk 协议本身;primary 先成功再复制的不变量,看正文第 7 节和思考题,引擎细节在下一课。'
  };
  window.ESEXPERIMENTS['ch13-01-mixed'] = {
    version: 1, id: 'ch13-01-mixed',
    title: '实验 1 · 混合操作同批:六项各自报各自的 status',
    method: 'POST', path: '/_bulk',
    body: '{"index":{"_index":"tut-l13-items","_id":"ok-a"}}\n{"title":"good A"}\n{"create":{"_index":"tut-l13-items","_id":"dup"}}\n{"title":"first"}\n{"create":{"_index":"tut-l13-items","_id":"dup"}}\n{"title":"again"}\n{"update":{"_index":"tut-l13-items","_id":"ok-a"}}\n{"doc":{"tag":"t1"}}\n{"delete":{"_index":"tut-l13-items","_id":"bye"}}\n{"index":{"_index":"tut-l13-items","_id":"ok-b"}}\n{"title":"good B"}\n',
    predict: '六项同批:两次 create 写同一个 _id、update 依赖同批先写的 ok-a、delete 一个不存在的 _id。HTTP 状态码是多少?哪几项失败?',
    expect: 'HTTP 200、errors: true。第一项 index/create 201;第二个 create 撞已有 _id 是 409(version_conflict)——版本冲突在条级报,不烧整批;update 200(同批前一项已写进同一个 primary,取得到);delete 得 result: not_found、status 404。items[] 顺序与你的 NDJSON 行序一一对应。机制:primary 上逐项执行,BulkPrimaryExecutionContext 里 FAILURE 也 advance() 进下一项。'
  };
  window.ESEXPERIMENTS['ch13-02-bad-source'] = {
    version: 1, id: 'ch13-02-bad-source', allowInvalidBody: true,
    title: '实验 2 · 坏 source 行夹在好文档中间',
    method: 'POST', path: '/_bulk',
    body: '{"index":{"_index":"tut-l13-items","_id":"ok-c"}}\n{"title":"good C"}\n{"index":{"_index":"tut-l13-items","_id":"bad"}}\n{this is not json}\n{"index":{"_index":"tut-l13-items","_id":"ok-d"}}\n{"title":"good D"}\n',
    predict: '坏 source 夹在中间:整个请求 400,还是 200 + 部分失败?ok-d 还能写进去吗?',
    expect: 'HTTP 200、errors: true。bad 一项 4xx(解析类异常,具体类型以你的返回为准);ok-c、ok-d 照常 201。source 行在 REST 层只是按行切片交给 IndexRequest.source(),不解析 JSON——解析推迟到 primary 上,所以是条级失败;对照实验 4 的整请求 400,两层别混。'
  };
  window.ESEXPERIMENTS['ch13-03-unknown-index'] = {
    version: 1, id: 'ch13-03-unknown-index',
    title: '实验 3 · 向不存在的索引 delete:条级 404',
    method: 'POST', path: '/_bulk',
    body: '{"delete":{"_index":"tut-l13-nope","_id":"x"}}\n{"index":{"_index":"tut-l13-items","_id":"ok-e"}}\n{"title":"good E"}\n',
    predict: '一个条目指向根本不存在的索引 tut-l13-nope:整个 bulk 404?还是别的形态?tut-l13-nope 会被自动建出来吗?',
    expect: 'HTTP 200、errors: true。nope 的 delete 一项 404(index_not_found_exception);ok-e 201。TransportBulkAction.populateMissingTargets 只为写操作自动建索引,普通 delete 不会为删一篇不存在的文档建索引。错误码阶梯在条级同样成立:路由命中、索引不在 = 404;对照实验 4:请求体坏 = 400。'
  };
  window.ESEXPERIMENTS['ch13-04-malformed'] = {
    version: 1, id: 'ch13-04-malformed', allowInvalidBody: true,
    title: '实验 4 · 缺末尾换行:整请求 400',
    method: 'POST', path: '/_bulk',
    body: '{"index":{"_index":"tut-l13-items","_id":"no-nl"}}\n{"title":"missing terminator"}',
    predict: '只差结尾一个换行符:HTTP 是多少?响应里还有 items 吗?',
    expect: 'HTTP 400,报错 The bulk request must be terminated by a newline(BulkRequestParser 切行阶段)。这类失败发生在请求被切成条目之前——没有「其它项」,也没有 items,和实验 2 的条级失败是两层。action 行不是合法 JSON 对象,同样在这层 400。'
  };
  window.ESEXPERIMENTS['ch13-05-setup-routed'] = {
    version: 1, id: 'ch13-05-setup-routed',
    title: '实验 5 · 建路由实验索引 tut-l13-routed',
    method: 'PUT', path: '/tut-l13-routed',
    body: { settings: { number_of_shards: 2, number_of_replicas: 0 } },
    predict: '2 个主分片,对下面三个 _id 意味着什么?先查正文第 4 节的表再猜分布。',
    expect: 'acknowledged: true。下一个实验写入 _id=1、2、3:按表,"1"、"2" 的 Murmur3 都余 1(进 shard 1),"3" 余 0(进 shard 0)——不是均匀轮转,是字符串哈希的余数。'
  };
  window.ESEXPERIMENTS['ch13-06-bulk-write'] = {
    version: 1, id: 'ch13-06-bulk-write',
    title: '实验 6 · _id=1/2/3 三篇写入(?refresh=true)',
    method: 'POST', path: '/_bulk?refresh=true',
    body: '{"index":{"_index":"tut-l13-routed","_id":"1"}}\n{"title":"id-1"}\n{"index":{"_index":"tut-l13-routed","_id":"2"}}\n{"title":"id-2"}\n{"index":{"_index":"tut-l13-routed","_id":"3"}}\n{"title":"id-3"}\n',
    predict: '三项各落哪个 shard?分布是 2:1 还是 1:2?refresh=true 对谁生效?',
    expect: '三项都 201、errors: false。refresh 是每请求一份的策略:这一整批写完立即 refresh,返回即可搜。路由:两项进 shard 1(_id "1"、"2"),一项进 shard 0(_id "3")——与表里 Murmur3 的余数一致。'
  };
  window.ESEXPERIMENTS['ch13-07-search-shards'] = {
    version: 1, id: 'ch13-07-search-shards',
    title: '实验 7 · _search_shards 核对路由落点',
    method: 'GET', path: '/tut-l13-routed/_search_shards?routing=1,3&filter_path=shards.shard',
    predict: 'routing=1,3 逗号分隔:返回哪两个 shard 号?_id=1 在 shard 1 是因为「数字 1」吗?',
    expect: 'shards 数组含 1 与 0:有效键 "1" 的 Murmur3 是 -126235597,floorMod(…,2)=1 → shard 1;"3" 是 -1151172406,余 0 → shard 0(与实验 6 的写入对上)。注意:不带 routing 的 _search_shards 返回全部 shard,别拿它推断写路由。'
  };
  window.ESEXPERIMENTS['ch13-08-cat-shards'] = {
    version: 1, id: 'ch13-08-cat-shards',
    title: '实验 8 · _cat/shards 看 docs 分布(2:1)',
    method: 'GET', path: '/_cat/shards/tut-l13-routed?v&h=shard,prirep,state,docs',
    predict: '两个 primary 的 docs 列是多少比多少?会自动均衡吗?',
    expect: 'shard 1 的 docs=2、shard 0 的 docs=1(统计口径以你的返回为准)。bulk 不是 round-robin 轮流放,是逐条独立哈希——3 篇 2:1 完全正常,连续多篇挤进同一个 shard 也正常。'
  };
  window.ESEXPERIMENTS['ch13-09-waitfor'] = {
    version: 1, id: 'ch13-09-waitfor',
    title: '实验 9 · ?refresh=wait_for 写入',
    method: 'POST', path: '/_bulk?refresh=wait_for',
    body: '{"index":{"_index":"tut-l13-items","_id":"w1"}}\n{"title":"waited"}\n',
    predict: '不带 refresh 的 bulk 返回时文档可搜吗?wait_for 的返回时机和 refresh=true 有什么不同?',
    expect: 'wait_for 让这次写入等下一次自动 refresh 把它编进 segment 才返回(搭班车,通常比自己强制 refresh 便宜;具体 took 以你的返回为准),返回即可搜。默认(不带参数)返回时文档只在 translog/buffer,约 1 秒的 refresh 间隔内搜不到——第 1 课的近实时。下一个实验立刻数数验证。'
  };
  window.ESEXPERIMENTS['ch13-10-count'] = {
    version: 1, id: 'ch13-10-count',
    title: '实验 10 · 立刻计数:wait_for 返回即可搜',
    method: 'GET', path: '/tut-l13-items/_count?q=_id:w1&filter_path=count',
    predict: 'wait_for 返回后立刻数:count 是 0 还是 1?如果实验 9 不带任何 refresh 参数,这里可能是多少?',
    expect: 'count: 1——wait_for 返回时文档已编进 segment。若刚才不带参数,这里就取决于自动 refresh 是否已跑过,可能是 0:默认 bulk 的「返回」和「可搜」之间隔着一次 refresh。'
  };
  window.ESEXPERIMENTS['ch13-11-cleanup-items'] = {
    version: 1, id: 'ch13-11-cleanup-items',
    title: '清理 1 · 删除 tut-l13-items',
    method: 'DELETE', path: '/tut-l13-items',
    predict: '删除会连带清掉什么?',
    expect: 'acknowledged: true。索引及所有分片数据(含 translog 与 segment)一并删除。'
  };
  window.ESEXPERIMENTS['ch13-12-cleanup-routed'] = {
    version: 1, id: 'ch13-12-cleanup-routed',
    title: '清理 2 · 删除 tut-l13-routed',
    method: 'DELETE', path: '/tut-l13-routed',
    predict: 'tut-l13-nope 需要清理吗?',
    expect: 'acknowledged: true。实验 3 的 tut-l13-nope 从未被创建(delete 不触发自动建索引),无东西可删——本课清理完毕。'
  };
})();
