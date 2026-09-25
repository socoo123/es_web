/* experiments/ch25.js — 第 25 课:熔断器与背压实验 + 熔断水位旗舰动画 */
(function () {
  'use strict';

  /* ===== 动画:一笔 500MB 聚合的记账与熔断 ===== */
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

  /* 步骤 1:1GB 堆的家底 */
  function step1() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('c1');
    s += rect(15, 15, 730, 46, 'fig-box-hot');
    s += txt(380, 34, 'JVM 堆 1GB', 'fig-name');
    s += txt(380, 52, '真实已用 900MB(含 segment/倒排/线程——很多没挂账本)', 'fig-sub');
    s += rect(15, 70, 222, 60, 'fig-box');
    s += txt(126, 92, 'request · 600MB', 'fig-name');
    s += txt(126, 112, '已用 50MB', 'fig-sub');
    s += txt(126, 128, '聚合/请求内存', 'fig-sub');
    s += rect(269, 70, 222, 60, 'fig-box');
    s += txt(380, 92, 'fielddata · 400MB', 'fig-name');
    s += txt(380, 112, '已用 ≈ 0', 'fig-sub');
    s += txt(380, 128, '堆上缓存', 'fig-sub');
    s += rect(523, 70, 222, 60, 'fig-box');
    s += txt(634, 92, 'Parent · 950MB', 'fig-name');
    s += txt(634, 112, '95% 堆,看真实堆', 'fig-sub');
    s += txt(634, 128, '不是第四本账', 'fig-sub');
    s += rect(15, 145, 730, 74, 'fig-box');
    s += txt(380, 170, 'use_real_memory=true(默认)', 'fig-key');
    s += txt(380, 194, 'checkParentLimit 拿 currentMemoryUsage()(HeapMemoryUsage.getUsed())', 'fig-sub');
    s += txt(380, 214, '+ 这一笔预留,和 95% 比——不是三本子账相加', 'fig-sub');
    s += bottom('家底:子账分类限,Parent 真实堆总闸', '孩子限额之和 60%+40%+100% 可以超过 95%:同一时刻不会都顶满');
    return s + '</svg>';
  }

  /* 步骤 2:一笔 +500MB 到达 */
  function step2() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('c2');
    s += rect(15, 15, 730, 46, 'fig-box');
    s += txt(380, 34, '高基数 terms(第 19 课那种)预估 +500MB', 'fig-name', false, 'fp-pop');
    s += txt(380, 52, 'addEstimateBytesAndMaybeBreak(500MB, label)', 'fig-sub');
    s += rect(15, 75, 730, 90, 'fig-box');
    s += txt(380, 100, '这笔账怎么构成的?', 'fig-key');
    s += txt(380, 124, 'preallocate[aggregations] 6kb → agg 5kb → BigArrays 随基数扩', 'fig-sub');
    s += txt(380, 144, 'size=2 只管返回窗口,收集期照样按基数记账', 'fig-sub');
    s += txt(380, 164, '这里画成一笔 500MB,是把后面 N 次扩页合成一跳', 'fig-sub');
    s += rect(15, 178, 730, 44, 'fig-box');
    s += txt(380, 197, '顺序:先过子账(request),再问 Parent', 'fig-sub');
    s += txt(380, 214, 'label 会进异常文案——拒绝时你能认出是哪类分配', 'fig-sub');
    s += bottom('先估计,后记账,再决定', '调用方从不先 new 一块堆再回头问「能不能用」');
    return s + '</svg>';
  }

  /* 步骤 3:子账检查 + CAS */
  function step3() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('c3');
    s += rect(15, 15, 730, 64, 'fig-box');
    s += txt(380, 37, '子账:request 50 + 500 = 550MB(×overhead 1.0)', 'fig-key');
    s += txt(380, 60, '550 ≤ 600:过,compareAndSet(50 → 550) 成功', 'fig-sub');
    s += rect(15, 95, 730, 60, 'fig-box-hot', 'fp-pop');
    s += txt(380, 118, '此刻账已加上:used = 550MB', 'fig-name');
    s += txt(380, 140, '若子账自己超限,circuitBreak 发生在 CAS 之前——账面根本不动', 'fig-sub');
    s += rect(15, 170, 730, 54, 'fig-box');
    s += txt(380, 191, '对照:限额调到 1kb 时(实验 6)', 'fig-key');
    s += txt(380, 211, '6kb 的 preallocate[aggregations] 直接撞 1024,CAS 前拒绝', 'fig-sub');
    s += txt(380, 227, 'bytes_wanted=6kb+、bytes_limit=1024、durability=TRANSIENT', 'fig-sub');
    s += bottom('子账这一关:550 过了,但还没完', 'CAS 之后才轮到 Parent——总闸还没看这笔');
    return s + '</svg>';
  }

  /* 步骤 4:Parent 检查 */
  function step4() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('c4');
    s += rect(15, 15, 730, 64, 'fig-box');
    s += txt(380, 37, 'checkParentLimit(500MB, label)', 'fig-key');
    s += txt(380, 60, 'trackRealMemoryUsage=true:真实堆 900 + 预留 500 = 1400MB', 'fig-sub');
    s += rect(15, 95, 340, 76, 'fig-box');
    s += txt(185, 118, '总用量 1400MB', 'fig-name');
    s += txt(185, 142, '≈ 堆的 137%', 'fig-sub');
    s += txt(185, 162, '若放行:一步之遥 OOM', 'fig-sub', true);
    s += rect(405, 95, 340, 76, 'fig-box');
    s += txt(575, 118, 'Parent 限额 950MB', 'fig-name');
    s += txt(575, 142, '= 95% × 1GB', 'fig-sub');
    s += txt(575, 162, '1400 > 950:破', 'fig-sub', true);
    s += rect(15, 186, 730, 40, 'fig-box');
    s += txt(380, 204, 'durability 按瞬时/永久占比挑:这笔在 request(TRANSIENT)→ 报 TRANSIENT', 'fig-sub');
    s += txt(380, 220, 'parentTripCount +1(下次 stats 里 parent.tripped 会多一)', 'fig-sub');
    s += bottom('Parent 看的是真实堆 + 这一笔预留', 'use_real_memory=false 才改看「子账之和」,限额默认也变 70%');
    return s + '</svg>';
  }

  /* 步骤 5:回滚 */
  function step5() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('c5');
    s += rect(15, 15, 730, 64, 'fig-box-hot', 'fp-pop');
    s += txt(380, 37, 'addWithoutBreaking(-500MB):把刚加的扣回去', 'fig-name', true);
    s += txt(380, 60, '不乘 overhead、不问 Parent、不熔断——专门用于释放与回滚', 'fig-sub');
    s += rect(15, 95, 730, 70, 'fig-box');
    s += txt(380, 120, 'request.used:550 → 50MB', 'fig-key');
    s += txt(380, 144, '不变量:used = 此刻仍被允许占着的估算', 'fig-sub');
    s += txt(380, 164, '漏掉回滚,后面的合法请求会替这 500MB 背锅(思考题 2)', 'fig-sub', true);
    s += rect(15, 180, 730, 44, 'fig-box');
    s += txt(380, 200, '然后 throw CircuitBreakingException', 'fig-key');
    s += txt(380, 218, 'bytes_wanted=1400MB、bytes_limit=950MB、durability=TRANSIENT', 'fig-sub');
    s += bottom('拒绝发生在加账之后——所以必须回滚', '分配从未发生:那 500MB 没有真的占上堆');
    return s + '</svg>';
  }

  /* 步骤 6:429,节点活着 */
  function step6() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('c6');
    s += rect(15, 15, 355, 96, 'fig-box');
    s += txt(192, 39, '客户端视角', 'fig-name');
    s += txt(192, 63, 'HTTP 429(TOO_MANY_REQUESTS)', 'fig-sub', true);
    s += txt(192, 83, 'type: circuit_breaking_exception', 'fig-sub');
    s += txt(192, 103, 'reason 含 [request] Data too large', 'fig-sub');
    s += rect(390, 15, 355, 96, 'fig-box-hot');
    s += txt(567, 39, '节点视角', 'fig-name');
    s += txt(567, 63, '真实堆还是 ≈900MB', 'fig-sub');
    s += txt(567, 83, '下一个请求照常处理', 'fig-sub');
    s += txt(567, 103, '集群健康色仍是 Green', 'fig-sub');
    s += rect(15, 128, 730, 90, 'fig-box');
    s += txt(380, 152, '对照另一本账:IndexingPressure', 'fig-key');
    s += txt(380, 176, '写入字节超 10%/15% 抛 EsRejectedExecutionException(第 8 课那种)', 'fig-sub');
    s += txt(380, 196, '不实现 CircuitBreaker;同样是「先 addAndGet 再减回去再抛」的不变量', 'fig-sub');
    s += txt(380, 214, 'Green/Yellow/Red 是分片是否 STARTED,和熔断无关', 'fig-sub');
    s += bottom('429 杀的是请求,不是节点', '熔断器换来的正是「节点活着,才有资格拒绝下一个」');
    return s + '</svg>';
  }

  /* 步骤 7:恢复与收束 */
  function step7() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('c7');
    s += rect(15, 15, 730, 60, 'fig-box');
    s += txt(380, 38, 'transient 设回 null:限额回到 60% 堆', 'fig-key');
    s += txt(380, 60, '同一条 terms 重新 200;不带 aggs 的 match_all 更没问题', 'fig-sub');
    s += rect(15, 90, 355, 96, 'fig-box');
    s += txt(192, 114, 'tripped 是计数器', 'fig-name');
    s += txt(192, 138, '恢复限额不清零、不锁死', 'fig-sub');
    s += txt(192, 158, '它只回答「历史上跳过几次」', 'fig-sub');
    s += txt(192, 178, '别设 0b:那会让加 0 也拒绝', 'fig-sub', true);
    s += rect(390, 90, 355, 96, 'fig-box');
    s += txt(567, 114, '真正的解法在查询', 'fig-name');
    s += txt(567, 138, '高基数 terms → cardinality', 'fig-sub');
    s += txt(567, 158, '或 include / min_doc_count 收窄', 'fig-sub');
    s += txt(567, 178, 'breaker 是安全网不是配额', 'fig-sub');
    s += rect(15, 200, 730, 30, 'fig-box');
    s += txt(380, 219, '第五篇至此收官:快照状态 → quorum 发布 → 过滤链落位 → 两阶段补数据 → 内存这道闸', 'fig-sub');
    s += bottom('先记账再拒绝:这就是背压的全部秘密', '子账 CAS 前自己跳,Parent CAS 后强制回滚——账面永远等于真实意图');
    return s + '</svg>';
  }

  window.ESFLOWS = window.ESFLOWS || {};
  window.ESFLOWS['ch25-breaker'] = {
    version: 1,
    id: 'ch25-breaker',
    title: '一笔 500MB 聚合的记账与熔断',
    speed: 2600,
    steps: [
      { svg: step1(), note: '1GB 堆的家底:真实已用 900MB(很多没挂账本);request 账 50MB/限 600MB,fielddata 空/限 400MB,Parent 950MB=95% 且默认看真实堆。孩子限额之和可以超过 95%——同一时刻不会都顶满。' },
      { svg: step2(), note: '高基数 terms 预估 +500MB:preallocate 6kb + agg 5kb + BigArrays 随基数扩,这里合成一跳。size=2 只管返回窗口,救不了收集期记账。入口是 addEstimateBytesAndMaybeBreak(bytes, label),label 会进异常文案。' },
      { svg: step3(), note: '先过子账:50+500=550(×overhead 1.0)≤ 600,CAS 把 used 换成 550——账已加上。对照实验 6:限额 1kb 时 6kb 的 preallocate[aggregations] 在 CAS 前就被拒,账面不动,bytes_limit=1024。' },
      { svg: step4(), note: 'CAS 之后问 Parent:use_real_memory=true 拿真实堆 900 + 预留 500 = 1400,对 950 比——破。durability 按瞬时/永久占比挑,这笔在 request → TRANSIENT;parent.tripped 计数 +1。' },
      { svg: step5(), note: '关键一步:回滚。addWithoutBreaking(-500) 把 request 拉回 50MB——不乘 overhead、不问 Parent、不熔断。不变量是 used = 仍被允许占着的估算;漏掉回滚,后续合法请求会替这 500MB 背锅。然后才抛异常。' },
      { svg: step6(), note: '客户端看到 HTTP 429、circuit_breaking_exception、bytes_wanted=1400/bytes_limit=950;节点真实堆仍是 ~900MB,下一个请求照常处理,健康色仍 Green。写入侧另一本账 IndexingPressure 抛的是 EsRejectedExecutionException,别混。' },
      { svg: step7(), note: 'transient 设回 null:同一条 terms 重新 200;tripped 是计数器,不清零也不锁死。真正的解法在查询层:cardinality / include / min_doc_count——breaker 是安全网不是配额系统。第五篇至此收官。' }
    ]
  };

  /* ===== 实验 ===== */
  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};

  window.ESEXPERIMENTS['ch25-00-stats'] = {
    version: 1, id: 'ch25-00-stats',
    title: '实验 0 · 四本账的字段名',
    method: 'GET',
    path: '/_nodes/stats/breaker?filter_path=nodes.*.breakers',
    body: null,
    predict: 'breakers 下有哪些 key?字节字段叫 limit_in_bytes 还是 limit_size_in_bytes?跳闸叫 tripped 还是 tripped_count?',
    expect: 'key 至少含 parent / request / fielddata / inflight_requests(可能还有插件的)。字段名以 CircuitBreakerStats.Fields 为准:limit_size_in_bytes、limit_size、estimated_size_in_bytes、estimated_size、overhead、tripped——没有 tripped_count。本地 1GB 堆:parent 限 ≈95%、request ≈60%、fielddata ≈40%。'
  };

  window.ESEXPERIMENTS['ch25-01-cat'] = {
    version: 1, id: 'ch25-01-cat',
    title: '实验 1 · _cat 视图 + 一个预测:parent.estimated vs 三子之和',
    method: 'GET',
    path: '/_cat/circuit_breaker?v&h=breaker,limit,estimated,tripped,overhead&bytes=b',
    body: null,
    predict: 'parent 的 estimated 是约等于三本子账 estimated 之和,还是明显更大?',
    expect: '通常明显更大:默认 use_real_memory=true 下 parent 的 estimated 填的是 memoryUsed(0).totalUsage ≈ 此刻真实堆——堆上还有 segment/倒排/线程这些没挂账本的东西。若你答「等于之和」,是把 use_real_memory=false 的测试路径当成了默认。'
  };

  window.ESEXPERIMENTS['ch25-02-setup'] = {
    version: 1, id: 'ch25-02-setup',
    title: '实验 2 · 建 tut-l25-card(20 个唯一 user_id 打底)',
    method: 'PUT', path: '/tut-l25-card',
    body: {
      settings: { number_of_shards: 1, number_of_replicas: 0 },
      mappings: { properties: { user_id: { type: 'keyword' } } }
    },
    predict: '为什么用 keyword?',
    expect: 'acknowledged: true。keyword 才有全局序数、才能复现第 19 课「收集期按基数记账」的内存曲线(与 tut-l19-card 同构,但不复用那课索引——每课自包含)。'
  };

  window.ESEXPERIMENTS['ch25-03-bulk'] = {
    version: 1, id: 'ch25-03-bulk',
    title: '实验 3 · 灌 20 个不同 user_id',
    method: 'POST', path: '/tut-l25-card/_bulk?refresh=true',
    body: '{"index":{}}\n{"user_id":"u-1"}\n{"index":{}}\n{"user_id":"u-2"}\n{"index":{}}\n{"user_id":"u-3"}\n{"index":{}}\n{"user_id":"u-4"}\n{"index":{}}\n{"user_id":"u-5"}\n{"index":{}}\n{"user_id":"u-6"}\n{"index":{}}\n{"user_id":"u-7"}\n{"index":{}}\n{"user_id":"u-8"}\n{"index":{}}\n{"user_id":"u-9"}\n{"index":{}}\n{"user_id":"u-10"}\n{"index":{}}\n{"user_id":"u-11"}\n{"index":{}}\n{"user_id":"u-12"}\n{"index":{}}\n{"user_id":"u-13"}\n{"index":{}}\n{"user_id":"u-14"}\n{"index":{}}\n{"user_id":"u-15"}\n{"index":{}}\n{"user_id":"u-16"}\n{"index":{}}\n{"user_id":"u-17"}\n{"index":{}}\n{"user_id":"u-18"}\n{"index":{}}\n{"user_id":"u-19"}\n{"index":{}}\n{"user_id":"u-20"}\n',
    predict: 'errors 会是 false 吗?',
    expect: 'errors: false,20 items。基数 20——第 19 课验证过这条 terms 会回 2 桶 + sum_other_doc_count=18。本课要它做的只是「默认限额下能过、1kb 下必炸」。'
  };

  window.ESEXPERIMENTS['ch25-04-terms-ok'] = {
    version: 1, id: 'ch25-04-terms-ok',
    title: '实验 4 · 默认限额:terms size=2 正常返回',
    method: 'POST',
    path: '/tut-l25-card/_search?filter_path=aggregations.users.buckets,aggregations.users.sum_other_doc_count',
    body: { size: 0, aggs: { users: { terms: { field: 'user_id', size: 2 } } } },
    predict: '回几个桶?sum_other 是多少?',
    expect: '2 个桶、sum_other_doc_count=18(与第 19 课一致)。此时 request 账只是 6kb+5kb+小数组的量级,离 600MB 远得很——待会儿把限额压到 1kb,同一条查询的命运就变了。'
  };

  window.ESEXPERIMENTS['ch25-05-limit-1kb'] = {
    version: 1, id: 'ch25-05-limit-1kb',
    title: '实验 5 · transient 把 request 限额压到 1kb(破坏实验)',
    method: 'PUT', path: '/_cluster/settings',
    body: { transient: { 'indices.breaker.request.limit': '1kb' } },
    predict: '这会让整台节点熔断锁死吗?重启后还在吗?',
    expect: 'acknowledged: true。都不会:transient 重启即丢,但课内仍要显式 null 恢复;tripped 是计数器不是开关,限额恢复后新请求照常。选 1kb 而不是 0b:0 会让任何一次记账(包括加 0 探 Parent)立刻拒绝。只在本地教程集群做。'
  };

  window.ESEXPERIMENTS['ch25-06-terms-break'] = {
    version: 1, id: 'ch25-06-terms-break',
    title: '实验 6 · 同一条 terms:429,circuit_breaking_exception',
    method: 'POST',
    path: '/tut-l25-card/_search?filter_path=status,error.type,error.reason,error.bytes_wanted,error.bytes_limit,error.durability,error.root_cause',
    body: { size: 0, aggs: { users: { terms: { field: 'user_id', size: 2 } } } },
    predict: '429 还是 500?label 是 preallocate[aggregations] 还是 user_id?durability 呢?',
    expect: 'status=429、type=circuit_breaking_exception;reason 含 [request] Data too large 与 preallocate[aggregations]——6kb 预留 > 1024,CAS 前就拒了,还没走到收集。bytes_limit=1024、durability=TRANSIENT。单节点偶尔包成 search_phase_execution_exception:往 root_cause 里找同样三件事。绝不该是 es_rejected_execution_exception——那是 IndexingPressure/线程池。'
  };

  window.ESEXPERIMENTS['ch25-07-tripped'] = {
    version: 1, id: 'ch25-07-tripped',
    title: '实验 7 · request.tripped ≥ 1 且限额=1024',
    method: 'GET',
    path: '/_nodes/stats/breaker?filter_path=nodes.*.breakers.request.tripped,nodes.*.breakers.request.limit_size_in_bytes',
    body: null,
    predict: 'tripped 是几?limit_size_in_bytes 呢?',
    expect: 'tripped ≥ 1(每次跳闸 +1),limit_size_in_bytes=1024。对照实验 0:动态设置实时生效在账本上——这正是「运行中的账」的含义,不用重启。'
  };

  window.ESEXPERIMENTS['ch25-08-restore'] = {
    version: 1, id: 'ch25-08-restore',
    title: '实验 8 · null 恢复(必做)',
    method: 'PUT', path: '/_cluster/settings',
    body: { transient: { 'indices.breaker.request.limit': null } },
    predict: 'null 是设成一个叫 null 的值吗?',
    expect: 'acknowledged: true。null 表示删掉这条覆盖,回到默认 60% 堆——第 5 课的语义:动态设置的重置也是一次状态更新。破坏实验的收尾不是可选项:留着 1kb,本机集群的聚合会一直 429。'
  };

  window.ESEXPERIMENTS['ch25-09-stats-restored'] = {
    version: 1, id: 'ch25-09-stats-restored',
    title: '实验 9 · 恢复后的账本:限额回来了,tripped 不清零',
    method: 'GET',
    path: '/_nodes/stats/breaker?filter_path=nodes.*.breakers.request.tripped,nodes.*.breakers.request.limit_size_in_bytes',
    body: null,
    predict: 'tripped 归零了吗?限额回到 60% 量级了吗?',
    expect: 'limit_size_in_bytes 回到堆 60% 的量级(1GB 堆约 600MB+),tripped 保持刚才的值——它是历史计数器,恢复限额不清零、也不锁死任何请求。'
  };

  window.ESEXPERIMENTS['ch25-10-terms-ok2'] = {
    version: 1, id: 'ch25-10-terms-ok2',
    title: '实验 10 · 同一条 terms:又是 200',
    method: 'POST',
    path: '/tut-l25-card/_search?filter_path=aggregations.users.buckets,aggregations.users.sum_other_doc_count',
    body: { size: 0, aggs: { users: { terms: { field: 'user_id', size: 2 } } } },
    predict: '查询一个字没改,这次结果如何?',
    expect: '又是 2 桶 + sum_other=18。同一条查询,账本限额一升一降就是 200 ⇄ 429——熔断的输入从来不是查询本身,而是「这笔估计值 vs 当时的限额」。'
  };

  window.ESEXPERIMENTS['ch25-11-matchall'] = {
    version: 1, id: 'ch25-11-matchall',
    title: '实验 11 · 不带 aggs 的 match_all:tripped>0 不锁死',
    method: 'POST',
    path: '/tut-l25-card/_search?filter_path=hits.total',
    body: { size: 0, query: { match_all: {} } },
    predict: 'tripped 还是 ≥1,这条查询会被拒吗?',
    expect: '正常 200:match_all 不加聚合账,几乎不进 request。tripped 只是计数,不是熔断锁——证明「跳过闸」和「现在能不能过」是两个问题。'
  };

  window.ESEXPERIMENTS['ch25-12-restore-again'] = {
    version: 1, id: 'ch25-12-restore-again',
    title: '清理 · 再 null 一次(保险)',
    method: 'PUT', path: '/_cluster/settings',
    body: { transient: { 'indices.breaker.request.limit': null } },
    predict: '已经恢复过了,为什么还要再来一次?',
    expect: 'acknowledged: true(对已删除的覆盖再删一次是无害幂等)。防御性收尾:即使实验 5-8 中途失败,这条也保证本机集群不被 1kb 限额困住——破坏实验的清理要假设最坏路径。'
  };

  window.ESEXPERIMENTS['ch25-13-cleanup'] = {
    version: 1, id: 'ch25-13-cleanup',
    title: '清理 · 删 tut-l25-card',
    method: 'DELETE', path: '/tut-l25-card',
    predict: '一句话总结本课?',
    expect: 'acknowledged: true。先记账再拒绝:addEstimateBytesAndMaybeBreak 先估后加,子账 CAS 前自己跳,Parent(CAS 后)强制 addWithoutBreaking 回滚;CircuitBreakingException → 429,节点活着;高基数 terms 的解法在查询,breaker 是安全网不是配额。'
  };
})();
