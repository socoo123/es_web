/* experiments/ch28.js — 第 28 课:索引生命周期管理实验 + 一分钟 rollover 动画 */
(function () {
  'use strict';

  /* ===== 动画:一分钟 rollover 的完整旅程 ===== */
  function rect(x, y, w, h, cls, anim) {
    return '<rect x="' + x + '" y="' + y + '" width="' + w + '" height="' + h + '" rx="9" class="' + cls + (anim ? ' ' + anim : '') + '"/>';
  }
  function txt(x, y, s, cls, warn, anim) {
    var st = warn ? ' style="fill: rgb(var(--warn))"' : '';
    return '<text x="' + x + '" y="' + y + '" text-anchor="middle" class="' + cls + (anim ? ' ' + anim : '') + '"' + st + '>' + s + '</text>';
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

  /* 步骤 1:家底 */
  function step1() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('m1');
    s += rect(15, 15, 730, 50, 'fig-box-hot');
    s += txt(380, 36, '策略 tut-l28-policy:hot=rollover 1m,warm 2h readonly,delete 24h', 'fig-name');
    s += txt(380, 56, '阶段 = Phase(名字 + min_age + actions):五个名字一个类,不是五个执行类', 'fig-sub');
    s += rect(15, 80, 355, 76, 'fig-box');
    s += txt(192, 103, '接力三件套', 'fig-name');
    s += txt(192, 127, '模板只带 lifecycle settings', 'fig-sub');
    s += txt(192, 147, '首索引手动带 write alias', 'fig-sub');
    s += txt(192, 167, '(alias 不进模板,见步骤 6)', 'fig-sub');
    s += rect(390, 80, 355, 76, 'fig-box');
    s += txt(567, 103, 'poll 调到 15s', 'fig-name');
    s += txt(567, 127, '默认 10 分钟(下限 1s)', 'fig-sub');
    s += txt(567, 147, '不调短,1 分钟的实验看不见', 'fig-sub', true);
    s += rect(15, 172, 730, 54, 'fig-box');
    s += txt(380, 193, '执行引擎只在 master:状态变化触发一遍 + 调度器按 poll 再跑一遍', 'fig-sub');
    s += txt(380, 215, '每个托管索引读出 StepKey(phase, action, step) 三元组交给 runner', 'fig-sub');
    s += bottom('箭头上写的是条件,不是类名', 'rollover 看 max_*;进下一阶段看下一阶段的 min_age——两种时钟');
    return s + '</svg>';
  }

  /* 步骤 2:初始化 */
  function step2() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('m2');
    s += rect(15, 15, 730, 50, 'fig-box');
    s += txt(380, 36, 'PUT tut-l28-logs-000001:lifecycleDate = 索引创建时刻', 'fig-name');
    s += txt(380, 56, '此刻 explain 显示 phase=new / step=complete——ILM 还没碰过它(实测)', 'fig-sub');
    s += rect(15, 80, 355, 96, 'fig-box');
    s += txt(192, 104, '第一轮 poll 到来', 'fig-name');
    s += txt(192, 128, 'InitializePolicyContextStep', 'fig-sub');
    s += txt(192, 148, '进入 hot 相:从活策略', 'fig-sub');
    s += txt(192, 168, '整份加载这一相的 JSON', 'fig-sub');
    s += rect(390, 80, 355, 96, 'fig-box-hot', 'fp-pop');
    s += txt(567, 104, 'phaseDefinition 缓存', 'fig-name');
    s += txt(567, 128, '写在索引 metadata 的 "ilm" 键', 'fig-sub');
    s += txt(567, 148, 'version=1, actions=[rollover]', 'fig-sub');
    s += txt(567, 168, 'explain 的 phase_execution 就是它', 'fig-sub');
    s += rect(15, 192, 730, 34, 'fig-box');
    s += txt(380, 212, '当前 step 从这份缓存 JSON 解析(PolicyStepsRegistry.getStep),不是每次读活策略', 'fig-sub');
    s += bottom('索引自己带着「正在执行的那一相」', '这是后面改策略分叉的伏笔');
    return s + '</svg>';
  }

  /* 步骤 3:check-rollover-ready 与暗门 */
  function step3() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('m3');
    s += rect(15, 15, 730, 50, 'fig-box');
    s += txt(380, 36, 'hot / rollover / check-rollover-ready(WaitForRolloverReadyStep)', 'fig-name');
    s += txt(380, 56, 'AsyncWaitStep:只走周期 poll 这条路,每 15s 醒一次评估条件', 'fig-sub');
    s += rect(15, 80, 355, 76, 'fig-box');
    s += txt(192, 103, '对 Rollover API dry_run', 'fig-name');
    s += txt(192, 127, 'max_age=1m 到了吗?', 'fig-sub');
    s += txt(192, 147, 'max_primary_shard_size / max_docs 同理', 'fig-sub');
    s += rect(390, 80, 355, 76, 'fig-box-hot', 'fp-pop');
    s += txt(567, 103, '暗门:min_docs: 1', 'fig-name', true);
    s += txt(567, 127, 'only_if_has_documents 默认 true', 'fig-sub');
    s += txt(567, 147, '空索引到点也不滚——必须先写一篇', 'fig-sub');
    s += rect(15, 172, 730, 54, 'fig-box');
    s += txt(380, 193, '一次 rollover 其实是一串 step(RolloverAction.toSteps 排好):', 'fig-key');
    s += txt(380, 215, 'check-rollover-ready → attempt-rollover → wait-for-active-shards → update-date → set-indexing-complete', 'fig-sub');
    s += bottom('rollover 的触发和阶段切换的触发,不是同一次判断', 'dry_run 看 Rollover 条件;min_age 要等 PhaseCompleteStep');
    return s + '</svg>';
  }

  /* 步骤 4:T≈75s,滚了 */
  function step4() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('m4');
    s += rect(15, 15, 730, 50, 'fig-box');
    s += txt(380, 36, 'T≈75s 的一轮 poll:dry_run 判 max_age 满足(文档已写)', 'fig-name');
    s += txt(380, 56, '迈到 attempt-rollover:真的调 Rollover API,新索引按模板创建', 'fig-sub');
    s += rect(15, 80, 355, 96, 'fig-box');
    s += txt(192, 104, 'tut-l28-logs-000002 诞生', 'fig-name');
    s += txt(192, 128, '模板注入 lifecycle settings', 'fig-sub');
    s += txt(192, 148, '(rollover 不复制它们,实测)', 'fig-sub', true);
    s += txt(192, 168, 'managed=true,自己再走一遍', 'fig-sub');
    s += rect(390, 80, 355, 96, 'fig-box');
    s += txt(567, 104, '000001 不是「改名」', 'fig-name');
    s += txt(567, 128, '还是同一条索引', 'fig-sub');
    s += txt(567, 148, 'indexing_complete=true', 'fig-sub');
    s += txt(567, 168, 'lifecycleDate 改成 rollover 时刻', 'fig-sub');
    s += rect(15, 192, 730, 34, 'fig-box');
    s += txt(380, 212, 'wait-for-active-shards → update-rollover-lifecycle-date → set-indexing-complete 依次收尾', 'fig-sub');
    s += bottom('rollover 换的是写索引,不是把旧索引变成 Warm 对象', '000001 只是在执行状态里改 phase 名');
    return s + '</svg>';
  }

  /* 步骤 5:min_age 从停止写入起算 */
  function step5() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('m5');
    s += rect(15, 15, 730, 50, 'fig-box');
    s += txt(380, 36, 'hot 到头:PhaseCompleteStep 上等 warm 的 min_age=2h', 'fig-name');
    s += txt(380, 56, 'isReadyToTransitionToThisPhase:now >= lifecycleDate + min_age(实测 000001 停在 hot/complete)', 'fig-sub');
    s += rect(15, 80, 355, 76, 'fig-box');
    s += txt(192, 104, '零点不是创建时刻', 'fig-name');
    s += txt(192, 128, 'update-rollover-lifecycle-date', 'fig-sub');
    s += txt(192, 148, '把零点写成停止写入的', 'fig-sub');
    s += txt(192, 168, 'rollover 时刻', 'fig-sub');
    s += rect(390, 80, 355, 76, 'fig-box');
    s += txt(567, 104, 'min_age 读活策略', 'fig-name');
    s += txt(567, 128, 'getIndexAgeForPhase →', 'fig-sub');
    s += txt(567, 148, 'lifecyclePolicyMap(集群上', 'fig-sub');
    s += txt(567, 168, '那份最新策略)', 'fig-sub');
    s += rect(15, 172, 730, 54, 'fig-box');
    s += txt(380, 193, 'explain 的 age 字段看同一个零点:从 rollover 起算的年龄', 'fig-sub');
    s += txt(380, 215, '到点进 warm:执行 readonly;再满 24h 进 delete:删索引——都是 Phase 上的 action', 'fig-sub');
    s += bottom('「滚走后再满 2h」的再字,来自 lifecycleDate 被改写', '热数据按写入年龄退休,不按出生年龄');
    return s + '</svg>';
  }

  /* 步骤 6:改策略的分叉 */
  function step6() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('m6');
    s += rect(15, 15, 355, 96, 'fig-box');
    s += txt(192, 39, '活策略:v2', 'fig-name');
    s += txt(192, 63, 'PUT 加了 forcemerge', 'fig-sub');
    s += txt(192, 83, 'hot actions=[rollover,forcemerge]', 'fig-sub');
    s += txt(192, 103, 'GET _ilm/policy 立刻可见', 'fig-sub');
    s += rect(390, 15, 355, 96, 'fig-box-hot');
    s += txt(567, 39, '000001 缓存:仍 v1', 'fig-name', true);
    s += txt(567, 63, 'phase_execution.version=1', 'fig-sub');
    s += txt(567, 83, 'actions 仍只有 rollover', 'fig-sub');
    s += txt(567, 103, '把旧 Hot 跑完,跳过 forcemerge', 'fig-sub');
    s += rect(15, 128, 730, 92, 'fig-box');
    s += txt(380, 152, '门闩:isIndexPhaseDefinitionUpdatable', 'fig-key');
    s += txt(380, 176, '当前 StepKey 还在,但当前相的 StepKey 集合变了(多出 forcemerge 的 steps)→ 不刷新', 'fig-sub');
    s += txt(380, 196, '只改 max_age / 改未来相:集合不变或换相时从活策略重读 → 生效', 'fig-sub');
    s += txt(380, 216, '000002 靠模板托管,进 Hot 时从活策略加载 → 拿到 v2(带 forcemerge)', 'fig-sub');
    s += bottom('当前相按缓存,下一相/新索引按活策略', '缓存兜底:正在跑的这一相不能被并发 PUT 抽掉当前 step');
    return s + '</svg>';
  }

  /* 步骤 7:收束 */
  function step7() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('m7');
    s += rect(15, 15, 730, 50, 'fig-box');
    s += txt(380, 36, '清理有顺序:先删索引(去引用)→ 模板/策略 → 恢复 poll', 'fig-name');
    s += txt(380, 56, '实测两个 400:策略被引用时删不掉;wildcard DELETE 默认被拒', 'fig-sub');
    s += rect(15, 80, 355, 96, 'fig-box');
    s += txt(192, 104, 'Cannot delete policy', 'fig-name', true);
    s += txt(192, 128, '"in use by one or more', 'fig-sub');
    s += txt(192, 148, 'indices" —— 顺序错了', 'fig-sub');
    s += txt(192, 168, '先 DELETE 两个索引', 'fig-sub');
    s += rect(390, 80, 355, 96, 'fig-box');
    s += txt(567, 104, 'Wildcard not allowed', 'fig-name', true);
    s += txt(567, 128, 'action.destructive_requires_name', 'fig-sub');
    s += txt(567, 148, '默认 true:删索引要显式点名', 'fig-sub');
    s += txt(567, 168, '安全默认,第 29 课见', 'fig-sub');
    s += rect(15, 192, 730, 34, 'fig-box');
    s += txt(380, 212, '别忘了 poll:null 回默认 10 分钟——教程集群不留快档轮询在 master 上', 'fig-sub');
    s += bottom('触发器 + 模板接力 + 缓存相 + 顺序敏感的清理', '这就是 ILM 的全部日常');
    return s + '</svg>';
  }

  window.ESFLOWS = window.ESFLOWS || {};
  window.ESFLOWS['ch28-ilm-rollover'] = {
    version: 1,
    id: 'ch28-ilm-rollover',
    title: '一分钟 rollover 的完整旅程',
    speed: 2400,
    steps: [
      { svg: step1(), note: '家底:策略 1m/2h/24h 三相 + 接力三件套(模板只带 lifecycle settings、首索引手动带 write alias)+ poll 调 15s(默认 10 分钟)。阶段是 Phase(名字+min_age+actions),五个名字一个类;执行引擎只在 master。' },
      { svg: step2(), note: 'PUT 索引后 lifecycleDate=创建时刻,explain 还是 new/complete;第一轮 poll 才进 hot,并从活策略整份加载这一相,写进索引 metadata 的 phaseDefinition(v1, actions=[rollover])——explain 的 phase_execution 就是它。' },
      { svg: step3(), note: 'check-rollover-ready 是 AsyncWaitStep:每轮 poll 对 Rollover API dry_run 看 max_age;暗门是 only_if_has_documents 默认 true 注入 min_docs:1——空索引到点不滚。一次 rollover 其实是一串 step。' },
      { svg: step4(), note: 'T≈75s 判满足 → attempt-rollover:000002 按模板创建、write alias 翻转;rollover 不复制 lifecycle settings,托管身份靠模板接力(实测无模板时 000002 managed=false)。000001 还是同一条索引,indexing_complete=true。' },
      { svg: step5(), note: 'hot 到头停在 PhaseCompleteStep 等 warm 的 min_age=2h:零点被 update-rollover-lifecycle-date 改写过,「再满 2h」从停止写入起算;min_age 本身读活策略。到点进 warm readonly,再满 24h 进 delete。' },
      { svg: step6(), note: '改策略的分叉:PUT v2 加 forcemerge 后活策略 version=2,但 000001 的缓存仍 v1/只有 rollover——StepKey 集合变了,isIndexPhaseDefinitionUpdatable 拒绝刷新。当前相按缓存;000002 靠模板托管,进 Hot 时从活策略拿到 v2。' },
      { svg: step7(), note: '清理有顺序:先显式删两个索引(去引用),再删模板/策略,最后 poll=null。实测两个 400:策略 in use 删不掉;wildcard DELETE 被 destructive_requires_name 默认拒——安全默认,第 29 课接着讲。' }
    ]
  };

  /* ===== 实验 ===== */
  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};

  window.ESEXPERIMENTS['ch28-01-poll'] = {
    version: 1, id: 'ch28-01-poll',
    title: '实验 1 · 把 poll 从默认 10 分钟调到 15s',
    method: 'PUT', path: '/_cluster/settings',
    body: { transient: { 'indices.lifecycle.poll_interval': '15s' } },
    predict: '默认轮询间隔是多久?不调短会怎样?',
    expect: 'acknowledged: true。默认 10 分钟(LifecycleSettings,下限 1s)——旧课写「每 10 秒」是错的。不调短,1 分钟的 max_age 你最多要干等到下一个 10 分钟槽才被看见。课末必须 null 恢复。'
  };

  window.ESEXPERIMENTS['ch28-02-policy'] = {
    version: 1, id: 'ch28-02-policy',
    title: '实验 2 · 建策略:hot rollover 1m / warm 2h / delete 24h',
    method: 'PUT', path: '/_ilm/policy/tut-l28-policy',
    body: { policy: { phases: {
      hot: { min_age: '0ms', actions: { rollover: { max_age: '1m' } } },
      warm: { min_age: '2h', actions: { readonly: {} } },
      delete: { min_age: '24h', actions: { delete: {} } }
    } } },
    predict: '三个阶段是三个类吗?rollover 的 max_age 和 warm 的 min_age 是同一种条件吗?',
    expect: 'acknowledged: true,version=1。不是:都是 Phase(名字+min_age+actions)。rollover.max_age 管「写索引要不要滚」(dry_run);warm/delete 的 min_age 管「滚走后要不要进下一阶段」——两种时钟,两次判断。'
  };

  window.ESEXPERIMENTS['ch28-03-template'] = {
    version: 1, id: 'ch28-03-template',
    title: '实验 3 · 接力模板:只带 lifecycle settings,不带 alias',
    method: 'PUT', path: '/_index_template/tut-l28-tpl',
    body: { index_patterns: ['tut-l28-logs-*'], template: { settings: { 'index.lifecycle.name': 'tut-l28-policy', 'index.lifecycle.rollover_alias': 'tut-l28-logs' } } },
    predict: '把 write alias 也写进模板,rollover 会不会更省事?',
    expect: 'acknowledged: true。千万别:实测 rollover 直接进 ERROR step——illegal_argument:Rollover alias can point to multiple indices, found duplicated alias in index template。alias 由 rollover 自己管理,模板只负责把 lifecycle settings 注入每一个新索引(这是 9.4.0 的接力正解,原文没写)。'
  };

  window.ESEXPERIMENTS['ch28-04-index'] = {
    version: 1, id: 'ch28-04-index',
    title: '实验 4 · 建 000001:命中模板,手动带 write alias',
    method: 'PUT', path: '/tut-l28-logs-000001',
    body: { aliases: { 'tut-l28-logs': { is_write_index: true } } },
    predict: 'settings 一个字没写,index.lifecycle.name 从哪来?缺 alias 会怎样?',
    expect: 'acknowledged: true。模板按 index_patterns 命中注入 lifecycle settings(可 GET 本索引 _settings 核对)。缺 alias 或 is_write_index 不为 true,rollover 卡 error:alias 写错时 WaitForRolloverReadyStep 直接 onFailure。data stream 免手写,本课用 alias 就为了看清这两条 setting。'
  };

  window.ESEXPERIMENTS['ch28-05-doc'] = {
    version: 1, id: 'ch28-05-doc',
    title: '实验 5 · 写一篇文档(暗门需要它)',
    method: 'POST', path: '/tut-l28-logs/_doc?refresh=true',
    body: { msg: 'l28-keep' },
    predict: '空索引到了 1 分钟会滚吗?',
    expect: 'result: created。不会:indices.lifecycle.rollover.only_if_has_documents 默认 true,给 dry_run 注入 min_docs:1(include_defaults 里可见)。这是 rollover 的暗门——教程实验必须先写一篇。'
  };

  window.ESEXPERIMENTS['ch28-06-explain-new'] = {
    version: 1, id: 'ch28-06-explain-new',
    title: '实验 6 · 立刻 explain:ILM 还没碰过它',
    method: 'GET',
    path: '/tut-l28-logs-000001/_ilm/explain?filter_path=indices.tut-l28-logs-000001.managed,indices.tut-l28-logs-000001.phase,indices.tut-l28-logs-000001.action,indices.tut-l28-logs-000001.step,indices.tut-l28-logs-000001.age',
    body: null,
    predict: '刚建好的索引,phase 已经是 hot 了吗?',
    expect: 'phase=new / action=complete / step=complete(实测)——初始化也要等第一轮 poll。managed=true、age 从毫秒起跳。这个 new 态是 InitializePolicyContextStep 的地盘,下一轮 poll 才进 hot。'
  };

  window.ESEXPERIMENTS['ch28-07-explain-hot'] = {
    version: 1, id: 'ch28-07-explain-hot',
    title: '实验 7 · 等 15-20s 再 explain:进 Hot,读的是缓存相',
    method: 'GET',
    path: '/tut-l28-logs-000001/_ilm/explain',
    body: null,
    predict: 'phase_execution.phase_definition 里会出现 delete 的 24h 吗?actions 有几个?',
    expect: 'phase=hot / action=rollover / step=check-rollover-ready;phase_execution.version=1,phase_definition.actions 只有 rollover——没有 warm 没有 delete。explain 展示的是这条索引正在执行的缓存相(PolicyStepsRegistry.getStep 读同一份 JSON),不是 GET _ilm/policy 那份全文。'
  };

  window.ESEXPERIMENTS['ch28-08-policy-v2'] = {
    version: 1, id: 'ch28-08-policy-v2',
    title: '实验 8 · 破坏:PUT v2,给 Hot 加 forcemerge(须在 1 分钟内)',
    method: 'PUT', path: '/_ilm/policy/tut-l28-policy',
    body: { policy: { phases: {
      hot: { min_age: '0ms', actions: { rollover: { max_age: '1m' }, forcemerge: { max_num_segments: 1 } } },
      warm: { min_age: '2h', actions: { readonly: {} } },
      delete: { min_age: '24h', actions: { delete: {} } }
    } } },
    predict: 'PUT 是集群级的,正在 check-rollover-ready 的 000001 会立刻改道执行 forcemerge 吗?',
    expect: 'acknowledged: true。不会——这正是本课要钉的分叉。若此时已过 1 分钟 rollover 已完成,本实验做不了:那是正常现象,重跑 01-05 即可。forcemerge 属于 HOT_ACTIONS_THAT_REQUIRE_ROLLOVER,真跑也要在 rollover 之后。'
  };

  window.ESEXPERIMENTS['ch28-09-policy-get'] = {
    version: 1, id: 'ch28-09-policy-get',
    title: '实验 9 · 活策略:version 2,Hot 多了 forcemerge',
    method: 'GET',
    path: '/_ilm/policy/tut-l28-policy?filter_path=tut-l28-policy.version,tut-l28-policy.policy.phases.hot.actions,tut-l28-policy.modified_date_in_millis',
    body: null,
    predict: 'version 会 +1 吗?',
    expect: 'version=2(每次 PUT +1),hot.actions=[rollover, forcemerge]。这是集群上那份活策略——和下一条实验里索引的缓存相对照,两份 JSON 即刻分叉。'
  };

  window.ESEXPERIMENTS['ch28-10-explain-after'] = {
    version: 1, id: 'ch28-10-explain-after',
    title: '实验 10 · 同一时刻 000001 的缓存:仍 v1,仍只有 rollover',
    method: 'GET',
    path: '/tut-l28-logs-000001/_ilm/explain?filter_path=indices.tut-l28-logs-000001.step,indices.tut-l28-logs-000001.phase_execution.version,indices.tut-l28-logs-000001.phase_execution.phase_definition.actions',
    body: null,
    predict: 'phase_execution.version 现在是几?actions 里有 forcemerge 吗?',
    expect: '仍 step=check-rollover-ready、version=1、actions=[rollover](实测)。isIndexPhaseDefinitionUpdatable:当前 StepKey 还在新策略里,但当前相的 StepKey 集合变了(多出 forcemerge 的 steps)→ return false,缓存不刷新。000001 会把旧 Hot 跑完,跳过 forcemerge——不是停机,只是不采纳。'
  };

  window.ESEXPERIMENTS['ch28-11-wait-cat'] = {
    version: 1, id: 'ch28-11-wait-cat',
    title: '实验 11 · 等约 80 秒:000002 出现',
    method: 'GET', path: '/_cat/indices/tut-l28-*?v&h=index,docs.count,status',
    body: null,
    predict: '先等 1 分钟 max_age + 至多一个 15s poll 槽再点。会有几行?000002 的 docs.count 是多少?',
    expect: '两行:000001(1 篇)与 000002(0 篇)。000002 由 rollover 按模板创建:托管身份来自模板注入的 lifecycle settings(rollover 本身不复制它们)。若没做实验 3 的模板,000002 会 managed=false,链条到此为止。'
  };

  window.ESEXPERIMENTS['ch28-12-alias-flip'] = {
    version: 1, id: 'ch28-12-alias-flip',
    title: '实验 12 · write alias 翻到了 000002',
    method: 'GET', path: '/_cat/aliases/tut-l28-logs?v',
    body: null,
    predict: 'is_write_index 现在在哪边?',
    expect: '000001 一行 is_write_index=false,000002 一行 true——rollover 翻的是别名的写指针,旧索引没有被改名或删除。它随后被设 index.lifecycle.indexing_complete=true。'
  };

  window.ESEXPERIMENTS['ch28-13-explain-both'] = {
    version: 1, id: 'ch28-13-explain-both',
    title: '实验 13 · 两份 explain:等 2h 的 v1,刚上路 v2',
    method: 'GET',
    path: '/tut-l28-*/_ilm/explain?filter_path=indices.*.managed,indices.*.phase,indices.*.action,indices.*.step,indices.*.phase_execution.version,indices.*.phase_execution.phase_definition.actions',
    body: null,
    predict: '000001 停在哪?000002 的缓存 version 是几、actions 有几个?',
    expect: '000001:phase=hot、step=complete——PhaseCompleteStep 上等 warm 的 2h(零点是 rollover 时刻)。000002:等一轮 poll 后 managed=true、hot/rollover/check-rollover-ready,phase_execution.version=2、actions=[rollover, forcemerge]——靠模板托管,进 Hot 时从活策略加载,和 000001 的 v1 缓存同屏对照。'
  };

  window.ESEXPERIMENTS['ch28-14-delete-inuse'] = {
    version: 1, id: 'ch28-14-delete-inuse',
    title: '实验 14 · 破坏:被引用的策略删不掉(顺序错了)',
    method: 'DELETE', path: '/_ilm/policy/tut-l28-policy',
    predict: '索引还在,这条 DELETE 能成功吗?',
    expect: '400 illegal_argument:Cannot delete policy [tut-l28-policy]. It is in use by one or more indices——清理必须先删索引(去引用)再删策略。若这里 200,说明索引已被清过,直接跳到实验 18。'
  };

  window.ESEXPERIMENTS['ch28-15-wildcard'] = {
    version: 1, id: 'ch28-15-wildcard',
    title: '实验 15 · 破坏:DELETE /tut-l28-* 被 400 拒',
    method: 'DELETE', path: '/tut-l28-*',
    predict: '通配符删索引,默认集群允许吗?',
    expect: '400:Wildcard expressions or all indices are not allowed——action.destructive_requires_name 默认 true,删除必须显式点名(9.4.0 安全默认;教程原文的清理命令在这条默认下会失败,网站按显式名走)。第 29 课安全机制的第一道预告。'
  };

  window.ESEXPERIMENTS['ch28-16-del-1'] = {
    version: 1, id: 'ch28-16-del-1',
    title: '清理 · 显式删 000001',
    method: 'DELETE', path: '/tut-l28-logs-000001',
    predict: '删它之前需要先摘 alias 吗?',
    expect: 'acknowledged: true。不需要:索引删除会连带清理它的 alias 条目。000001 此刻还在 hot/complete 等 2h——删除直接终止生命周期,不需要先手动移出策略。'
  };

  window.ESEXPERIMENTS['ch28-17-del-2'] = {
    version: 1, id: 'ch28-17-del-2',
    title: '清理 · 显式删 000002',
    method: 'DELETE', path: '/tut-l28-logs-000002',
    predict: '它是写索引,删掉后 alias 还指向谁?',
    expect: 'acknowledged: true。谁都不指:两个索引都删了,alias tut-l28-logs 随之消失。引用清零,下一步删策略就能成功——顺序的意义在这里兑现。'
  };

  window.ESEXPERIMENTS['ch28-18-del-tpl-policy'] = {
    version: 1, id: 'ch28-18-del-tpl-policy',
    title: '清理 · 删模板,再删策略',
    method: 'DELETE', path: '/_index_template/tut-l28-tpl',
    predict: '模板能删吗?策略呢?',
    expect: 'acknowledged: true(模板随时可删,它只在索引创建时起作用)。删完模板再 DELETE /_ilm/policy/tut-l28-policy——对照实验 14 的 400:同一条命令,前后的差别只是「还有没有索引引用它」。'
  };

  window.ESEXPERIMENTS['ch28-19-del-policy'] = {
    version: 1, id: 'ch28-19-del-policy',
    title: '清理 · 现在删策略成功了',
    method: 'DELETE', path: '/_ilm/policy/tut-l28-policy',
    predict: '和实验 14 同一条命令,这次结果?',
    expect: 'acknowledged: true(若实验 18 前策略已不存在则 404,同样算过)。in-use 检查看的是集群状态里的引用计数,不是策略本身——「先索引后策略」就是给这个检查让路。'
  };

  window.ESEXPERIMENTS['ch28-20-restore'] = {
    version: 1, id: 'ch28-20-restore',
    title: '清理 · poll 恢复默认(必做)',
    method: 'PUT', path: '/_cluster/settings',
    body: { transient: { 'indices.lifecycle.poll_interval': null } },
    predict: '不恢复会怎样?',
    expect: 'acknowledged: true。master 会一直按 15s 扫全部托管索引并可能提交集群状态任务——教程档位不该留在本机集群上。null 回默认 10 分钟;一句话总结:阶段是触发器(max_*/min_age 两种时钟),rollover 靠模板接力,执行按缓存相——改策略当前相不刷、新索引按活策略。'
  };
})();
