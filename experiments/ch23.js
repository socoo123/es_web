/* experiments/ch23.js — 第 23 课:分片分配实验 + 均衡迁移动画(旗舰) */
(function () {
  'use strict';

  /* ===== 动画:从单节点 Yellow 到三节点均衡 ===== */
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
  /* 节点盒子:x 传列左缘,w=222,y=15,h=96 */
  function nodeBox(x, name, chips, hot, anim) {
    var s = rect(x, 15, 222, 96, hot ? 'fig-box-hot' : 'fig-box', anim);
    s += txt(x + 111, 40, name, 'fig-name');
    s += txt(x + 111, 66, chips, 'fig-key');
    return s;
  }
  function ghost(x, label) {
    return txt(x + 111, 60, label, 'fig-sub');
  }
  function bottom(title, sub) {
    var s = rect(15, 242, 730, 46, 'fig-box-hot', 'fp-pop');
    s += txt(380, 263, title, 'fig-name');
    s += txt(380, 282, sub, 'fig-sub');
    return s;
  }
  var A = 126, B = 380, C = 634;

  /* 步骤 1:单节点 Yellow */
  function step1() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('b1');
    s += nodeBox(269, 'Node-A', 'idx1 P0 STARTED', true);
    s += ghost(15, '(还没有别的节点)');
    s += rect(15, 130, 730, 46, 'fig-box');
    s += txt(380, 149, 'R0 问 Node-A:same_shard 投 NO', 'fig-key', true);
    s += txt(380, 169, 'a copy of this shard is already allocated to this node', 'fig-sub');
    s += rect(15, 190, 730, 40, 'fig-box');
    s += txt(380, 208, '过滤链遇 NO 即 break,balancer 根本没上场', 'fig-sub');
    s += txt(380, 224, 'R0 停在 UNASSIGNED,RoutingTable 这行没有 node', 'fig-sub');
    s += bottom('集群 Yellow:能读写,但没有第二台可切', '这就是第 1 课看见的现象——本课终于能说出投出那一票的名字');
    return s + '</svg>';
  }

  /* 步骤 2:Node-B 加入 */
  function step2() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('b2');
    s += nodeBox(15, 'Node-A', 'idx1 P0 STARTED', true);
    s += nodeBox(269, 'Node-B', '(空)', false, 'fp-pop');
    s += txt(380, 100, '节点加入 → 触发 reroute,R0 重新走过滤链', 'fig-sub');
    s += rect(15, 130, 340, 52, 'fig-box');
    s += txt(185, 150, 'R0 问 A:same_shard → NO', 'fig-sub', true);
    s += txt(185, 172, '同号副本已在这台,剔除', 'fig-sub', true);
    s += rect(405, 130, 340, 52, 'fig-box');
    s += txt(575, 150, 'R0 问 B:全链 YES', 'fig-sub');
    s += txt(575, 172, '磁盘/过滤/限流全放行', 'fig-sub');
    s += bottom('过滤链的产出是候选集:{Node-B}', '磁盘没过水位、没有 filter、并发 recovery 没超限——每张票都是 YES');
    return s + '</svg>';
  }

  /* 步骤 3:balancer 打分,R0 落 B */
  function step3() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('b3');
    s += nodeBox(15, 'Node-A', 'idx1 P0 STARTED', true);
    s += nodeBox(269, 'Node-B', 'idx1 R0 INITIALIZING', true, 'fp-pop');
    s += arrow('b3', 237, 63, 263, 63);
    s += txt(250, 120, 'peer recovery:从 P0 拷数据(第 24 课)', 'fig-sub');
    s += rect(15, 130, 730, 46, 'fig-box');
    s += txt(380, 149, '候选集只有一个,权重最低也只能是它', 'fig-key');
    s += txt(380, 169, 'THROTTLE 会说「这轮先别动」:并发 recovery 默认每节点 2', 'fig-sub');
    s += rect(15, 190, 730, 40, 'fig-box');
    s += txt(380, 208, 'Master 把这步写进新的 ClusterState(第 21 课)', 'fig-sub');
    s += txt(380, 224, 'RoutingTable:idx1 R0 → node B,state=INITIALIZING', 'fig-sub');
    s += bottom('balancer 只在候选集里挑人,不推翻 NO', '它根本看不到 Node-A——被剔除的节点不进打分');
    return s + '</svg>';
  }

  /* 步骤 4:Green */
  function step4() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('b4');
    s += nodeBox(15, 'Node-A', 'idx1 P0 STARTED', true);
    s += nodeBox(269, 'Node-B', 'idx1 R0 STARTED', true);
    s += ghost(523, '(两台各持一份)');
    s += rect(15, 130, 730, 46, 'fig-box');
    s += txt(380, 149, '恢复完成:R0 STARTED,集群 Green', 'fig-key');
    s += txt(380, 169, '一份数据、两个故障域:任一台挂掉,另一份还在', 'fig-sub');
    s += rect(15, 190, 730, 40, 'fig-box');
    s += txt(380, 208, 'explain 再问 R0 已没有 unassigned 可解释', 'fig-sub');
    s += txt(380, 224, '想再看到那一票,就再建一个带副本的索引', 'fig-sub');
    s += bottom('Yellow → Green 的全部原因:多了一个合法候选', '不是「副本终于创建了」,是过滤链第一次有了放行的节点');
    return s + '</svg>';
  }

  /* 步骤 5:新索引,P/R 交错落位 */
  function step5() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('b5');
    s += nodeBox(15, 'Node-A', 'idx1 P0 + idx2 P0', true);
    s += nodeBox(269, 'Node-B', 'idx1 R0 + idx2 R0', true);
    s += rect(15, 130, 340, 52, 'fig-box');
    s += txt(185, 150, 'idx2 P0:A/B 都 YES', 'fig-sub');
    s += txt(185, 172, '权重相同,选一台(示意 A)', 'fig-sub');
    s += rect(405, 130, 340, 52, 'fig-box');
    s += txt(575, 150, 'idx2 R0:A 已有 idx2 P0', 'fig-sub', true);
    s += txt(575, 172, 'same_shard NO → 落 B', 'fig-sub', true);
    s += rect(15, 196, 730, 36, 'fig-box');
    s += txt(380, 218, 'balance.index=0.55:同一索引的分片尽量不堆一台——P/R 天然交错', 'fig-sub');
    s += bottom('两节点各 2 片:总分片均衡,同索引也打散', '每一步落位都是「过滤链先答行不行,权重再挑谁最好」');
    return s + '</svg>';
  }

  /* 步骤 6:Node-C 加入,relocation */
  function step6() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('b6');
    s += nodeBox(15, 'Node-A', 'idx1 P0 + idx2 P0', true);
    s += nodeBox(269, 'Node-B', 'idx1 R0* + idx2 R0', false);
    s += nodeBox(523, 'Node-C', 'idx1 R0 INITIALIZING', true, 'fp-pop');
    s += arrow('b6', 491, 63, 517, 63);
    s += txt(504, 120, 'relocation(搬迁)', 'fig-sub');
    s += rect(15, 130, 730, 46, 'fig-box');
    s += txt(380, 149, 'DesiredBalance 重算:A=2,B=2,C=0 偏差超 threshold', 'fig-key');
    s += txt(380, 169, 'balance() 挑「搬哪个最划算」:idx1 R0 从 B 搬 C', 'fig-sub');
    s += rect(15, 190, 730, 40, 'fig-box');
    s += txt(380, 208, '搬迁期间源分片仍 STARTED(可读写),目标同步完成后才切换', 'fig-sub');
    s += txt(380, 224, 'R0*:搬迁中的源副本;threshold=1.0 之下的小不平衡不搬,防抖动', 'fig-sub');
    s += bottom('节点加入不只是「新分片有地方放」', 'balancer 会把存量也往理想位置挪——每次挪仍要过过滤链');
    return s + '</svg>';
  }

  /* 步骤 7:终态与收束 */
  function step7() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('b7');
    s += nodeBox(15, 'Node-A', 'idx1 P0 + idx2 P0', true);
    s += nodeBox(269, 'Node-B', 'idx2 R0', false);
    s += nodeBox(523, 'Node-C', 'idx1 R0 STARTED', true);
    s += rect(15, 130, 730, 46, 'fig-box');
    s += txt(380, 149, '终态 2/1/1:主副分离、总分片摊开、同索引打散', 'fig-key');
    s += txt(380, 169, '磁盘 86% 的话:C 进不来了(disk_threshold NO);91% 才动存量', 'fig-sub');
    s += rect(15, 190, 730, 40, 'fig-box');
    s += txt(380, 208, '搬错的每一步都能被 explain 读出那一票', 'fig-sub');
    s += txt(380, 224, '搬过去的每个分片都要走 peer recovery(第 24 课)', 'fig-sub');
    s += bottom('过滤链管「行不行」,balancer 管「谁最好」', '一个 NO 就出局;能放的节点里,永远选偏差最小的那个');
    return s + '</svg>';
  }

  window.ESFLOWS = window.ESFLOWS || {};
  window.ESFLOWS['ch23-balance'] = {
    version: 1,
    id: 'ch23-balance',
    title: '从单节点 Yellow 到三节点均衡',
    speed: 2600,
    steps: [
      { svg: step1(), note: '起点是第 1 课的老朋友:单节点 Node-A 持有 idx1 的 P0,replica R0 想进同一台被 same_shard 拒绝——a copy of this shard is already allocated to this node。过滤链遇 NO 即 break,balancer 没上场,集群 Yellow。' },
      { svg: step2(), note: 'Node-B 加入,触发 reroute,R0 重新走过滤链:A 仍被 same_shard 剔除;B 磁盘没过水位、没有 filter、并发 recovery 没超限,全链 YES。过滤链的产出只是候选集 {B}。' },
      { svg: step3(), note: 'balancer 只在候选集里选权重最低者——这里只有一个候选。R0 落到 B,状态 INITIALIZING,数据从 A 的 P0 拷(peer recovery,第 24 课)。THROTTLE 若出现会说「这轮先别动」:并发 recovery 默认每节点 2。' },
      { svg: step4(), note: 'R0 STARTED,集群 Green。Yellow→Green 的全部原因不是「副本终于创建了」,是过滤链第一次有了放行的节点——一份数据、两个故障域,任一台挂掉另一份还在。' },
      { svg: step5(), note: '再建一个 1P1R 的索引 idx2:P0 对 A、B 都 YES(权重相同,示意落 A);R0 对 A 被 same_shard 拒(idx2 P0 已在那)→ 落 B。balance.index=0.55 让同一索引的分片天然交错,两台各 2 片。' },
      { svg: step6(), note: 'Node-C 加入,DesiredBalance 重算:A=2、B=2、C=0,偏差超过 threshold=1.0,balance() 决定把 idx1 的 R0 从 B 搬到 C:搬迁期间源分片仍 STARTED 可读写,目标 INITIALIZING,同步完成才切换。每次挪都要再过过滤链。' },
      { svg: step7(), note: '终态 2/1/1:主副分离、总分片摊开、同索引打散。若某台磁盘 86%,新分片进不来(disk_threshold 对新 replica 投 NO),91% 才迁存量,95% 是只读块。搬过去的每个分片都要走 peer recovery——第 24 课接着拆。' }
    ]
  };

  /* ===== 实验 ===== */
  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};

  window.ESEXPERIMENTS['ch23-00-setup'] = {
    version: 1, id: 'ch23-00-setup',
    title: '实验 0 · 建 tut-l23-yellow(1 主 1 副,单节点)',
    method: 'PUT', path: '/tut-l23-yellow',
    body: { settings: { number_of_shards: 1, number_of_replicas: 1 } },
    predict: '单节点放 1 主 1 副,集群会是什么颜色?',
    expect: 'acknowledged: true。P0 会 STARTED;R0 想进同一台被 same_shard 拒——第 1 课的 Yellow 重现。这次我们不只知道黄,还要读出投出那一票的 Decider 名字。'
  };

  window.ESEXPERIMENTS['ch23-01-cat-shards'] = {
    version: 1, id: 'ch23-01-cat-shards',
    title: '实验 1 · _cat/shards:两行,一行 UNASSIGNED',
    method: 'GET',
    path: '/_cat/shards/tut-l23-yellow?v&h=index,shard,prirep,state,unassigned.reason,node',
    body: null,
    predict: '几行?哪行 UNASSIGNED?unassigned.reason 是什么?',
    expect: '两行:p = STARTED(node 有名有姓)、r = UNASSIGNED(node 空)。unassigned.reason = INDEX_CREATED:分片从建索引起就没分出去过。第 1 课是 2P+2R 的四行版,现象同源。'
  };

  window.ESEXPERIMENTS['ch23-02-health'] = {
    version: 1, id: 'ch23-02-health',
    title: '实验 2 · Yellow 又来了',
    method: 'GET', path: '/_cat/health?v',
    body: null,
    predict: 'status 列是什么颜色对应的词?',
    expect: 'yellow。主分片全在、能读写;缺的是副本这一层冗余。Green 的定义是「所有副本也就位」——单节点永远给不了第二台。'
  };

  window.ESEXPERIMENTS['ch23-03-explain'] = {
    version: 1, id: 'ch23-03-explain',
    title: '实验 3 · explain:读出 same_shard 那一票',
    method: 'POST', path: '/_cluster/allocation/explain',
    body: { index: 'tut-l23-yellow', shard: 0, primary: false },
    predict: 'can_allocate 是 yes 还是 no?deciders[].decider 叫什么?explanation 以什么开头?',
    expect: 'current_state=unassigned、can_allocate=no;node_allocation_decisions[0].node_decision=no;deciders 里 decider=same_shard、decision=NO、explanation 以 a copy of this shard is already allocated to this node 开头。这一票就是 Yellow 的全部原因。默认 include_yes_decisions=false:不是链上只有一个 Decider,是 YES 被滤掉了。'
  };

  window.ESEXPERIMENTS['ch23-04-explain-yes'] = {
    version: 1, id: 'ch23-04-explain-yes',
    title: '实验 4 · include_yes_decisions=true:看整条链',
    method: 'POST', path: '/_cluster/allocation/explain?include_yes_decisions=true',
    body: { index: 'tut-l23-yellow', shard: 0, primary: false },
    predict: 'deciders 数组会变长还是变短?same_shard 那条 NO 会不会变 YES?',
    expect: '明显变长:replica_after_primary_active、disk_threshold、throttling、enable、filter 等都以 YES 出现(DebugMode.ON 收齐所有非 ALWAYS 票);same_shard 仍是 NO——看见整条链 ≠ 改写投票。对比实验 3:默认模式下你只看到 1 条,是过滤不是缺席。'
  };

  window.ESEXPERIMENTS['ch23-05-defaults'] = {
    version: 1, id: 'ch23-05-defaults',
    title: '实验 5 · 默认值核对:水位 + 平衡因子',
    method: 'GET',
    path: '/_cluster/settings?include_defaults=true&filter_path=defaults.cluster.routing.allocation.disk.watermark,defaults.cluster.routing.allocation.disk.threshold_enabled,defaults.cluster.routing.allocation.balance',
    body: null,
    predict: '三档水位默认各是多少?balance 五个因子呢?',
    expect: 'watermark: low=85%、high=90%、flood_stage=95%,threshold_enabled=true——与 DiskThresholdSettings 源码字符串逐字一致。balance: shard=0.45、index=0.55、write_load=10.0、disk_usage=2e-11(没看错,就是 2×10⁻¹¹,磁盘大头由水位硬阈值管)、threshold=1.0。'
  };

  window.ESEXPERIMENTS['ch23-06-cat-allocation'] = {
    version: 1, id: 'ch23-06-cat-allocation',
    title: '实验 6 · _cat/allocation:本机磁盘离水位远吗',
    method: 'GET', path: '/_cat/allocation?v&h=shards,disk.indices,disk.used,disk.avail,disk.percent,node',
    body: null,
    predict: '本机 disk.percent 过 85% 了吗?这跟实验 3 的 NO 什么关系?',
    expect: '远低于 85%。所以实验 3 里投 NO 的不是 disk_threshold,是 same_shard——单节点 Yellow 的锅不在磁盘。这张表正是 DiskThresholdDecider 的输入(ClusterInfo 的磁盘快照);真正灌磁盘验证水位是被禁止的,读 canAllocate 分支就够了。'
  };

  window.ESEXPERIMENTS['ch23-07-replicas-0'] = {
    version: 1, id: 'ch23-07-replicas-0',
    title: '实验 7 · 副本数归零:Yellow 的开关(上)',
    method: 'PUT', path: '/tut-l23-yellow/_settings',
    body: { number_of_replicas: 0 },
    predict: '不需要第二份了,集群会变什么颜色?',
    expect: 'acknowledged: true。改副本数是一次 ClusterState 更新(第 21 课:version +1);R0 被移出 RoutingTable。顺带一提:这也是动态索引设置,和第 5 课同一套机制。'
  };

  window.ESEXPERIMENTS['ch23-08-green'] = {
    version: 1, id: 'ch23-08-green',
    title: '实验 8 · Yellow 的开关(下):Green',
    method: 'GET', path: '/_cat/health?v&h=status',
    body: null,
    predict: '现在 status 是什么?',
    expect: 'green。Yellow 说的是「副本没处放」而不是「集群坏了」:需求消失,黄也消失。生产上这是权衡——单节点要 Green 只能 0 副本,等于放弃冗余(思考题 2 的另一面)。'
  };

  window.ESEXPERIMENTS['ch23-09-replicas-back'] = {
    version: 1, id: 'ch23-09-replicas-back',
    title: '实验 9 · 副本数改回 1:Yellow 回来了',
    method: 'PUT', path: '/tut-l23-yellow/_settings',
    body: { number_of_replicas: 1 },
    predict: 'explain 指定 primary:false 还能解释到分片吗?空 body 会怎样?',
    expect: 'acknowledged: true,R0 重新 UNASSIGNED(又能用实验 3 读出 same_shard 那一票)。空 body 的 GET /_cluster/allocation/explain 会挑「第一条 unassigned」并带一段 note——集群里有别的黄分片时容易解释错对象,所以实验 3 用 body 指定。'
  };

  window.ESEXPERIMENTS['ch23-10-cleanup'] = {
    version: 1, id: 'ch23-10-cleanup',
    title: '清理 · 删 tut-l23-yellow',
    method: 'DELETE', path: '/tut-l23-yellow',
    predict: '一句话总结本课?',
    expect: 'acknowledged: true。过滤链管「行不行」(一个 NO 就出局:同号副本不同节点、磁盘水位、filter、总开关),balancer 管「谁最好」(候选集里选权重最低);Yellow 是那张 NO 的合法产物,explain 能把票箱读出来。'
  };
})();
