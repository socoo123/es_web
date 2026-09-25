/* experiments/ch22.js — 第 22 课:主节点选举与共识实验 + 选举时序旗舰动画 */
(function () {
  'use strict';

  /* ===== 动画:旧 Master 被隔离,一场选举的完整时序 ===== */
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
  /* 三个节点盒子:x=15(n1) 269(n2) 523(n3),y=15,h=84 */
  function nodeBox(x, name, role, sub, hot, warn) {
    var s = rect(x, 15, 222, 84, hot ? 'fig-box-hot' : 'fig-box');
    s += txt(x + 111, 40, name, 'fig-name', false);
    s += txt(x + 111, 64, role, 'fig-key', warn);
    s += txt(x + 111, 86, sub, 'fig-sub');
    return s;
  }
  function bottom(title, sub) {
    var s = rect(15, 242, 730, 46, 'fig-box-hot', 'fp-pop');
    s += txt(380, 263, title, 'fig-name');
    s += txt(380, 282, sub, 'fig-sub');
    return s;
  }
  var N1 = 126, N2 = 380, N3 = 634; /* 节点盒子中心 x */

  /* 步骤 1:健康集群 */
  function step1() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('a1');
    s += nodeBox(15, 'n1', 'LEADER · term=5', '正常 publish', true, false);
    s += nodeBox(269, 'n2', 'FOLLOWER', '接受 PublishRequest', false, false);
    s += nodeBox(523, 'n3', 'FOLLOWER', '接受 PublishRequest', false, false);
    s += arrow('a1', 237, 57, 263, 57);
    s += arrow('a1', 491, 57, 517, 57);
    s += txt(380, 122, 'LeaderChecker / FollowersChecker 心跳正常', 'fig-sub');
    s += rect(15, 140, 730, 74, 'fig-box');
    s += txt(380, 165, 'voting configuration = {n1, n2, n3},quorum = 2', 'fig-key');
    s += txt(380, 192, '2 * 2 > 3 成立,2 票即多数;3 节点集群同一时刻只有 n1 一个 LEADER', 'fig-sub');
    s += bottom('健康集群:n1 当 LEADER,term=5', 'version 每次成功 publish 加一,term 只在换届加一');
    return s + '</svg>';
  }

  /* 步骤 2:网线拔掉 */
  function step2() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('a2');
    s += nodeBox(15, 'n1', '仍自称 LEADER', '听得见自己', true, true);
    s += nodeBox(269, 'n2', 'FOLLOWER', '与 n3 互通', false, false);
    s += nodeBox(523, 'n3', 'FOLLOWER', '与 n2 互通', false, false);
    s += '<line x1="252" y1="15" x2="252" y2="260" class="fig-arrow" style="stroke-dasharray: 6 5"/>';
    s += txt(126, 122, '分区 A:1/3', 'fig-sub');
    s += txt(567, 122, '分区 B:2/3', 'fig-sub');
    s += arrow('a2', 491, 57, 517, 57);
    s += rect(15, 140, 730, 74, 'fig-box');
    s += txt(380, 165, '两侧互不通信:没有「谁把票传给谁」', 'fig-key');
    s += txt(380, 192, '同一时刻最多一个分区拥有 quorum=2——这里只能是分区 B', 'fig-sub');
    s += bottom('网线拔掉:分区 A(n1)与分区 B(n2,n3)', '两侧各走各的心跳检测,谁先反应过来?下一帧');
    return s + '</svg>';
  }

  /* 步骤 3:两侧各自发现失联 */
  function step3() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('a3');
    s += nodeBox(15, 'n1', '仍自称 LEADER', '等不到 follower ACK', true, true);
    s += nodeBox(269, 'n2', 'CANDIDATE', 'becomeCandidate', false, false);
    s += nodeBox(523, 'n3', 'CANDIDATE', 'becomeCandidate', false, false);
    s += txt(126, 122, 'FollowersChecker 把 n2/n3 标 faulty', 'fig-sub', true);
    s += txt(567, 122, 'LeaderChecker 失败 → becomeCandidate', 'fig-sub');
    s += rect(15, 140, 730, 74, 'fig-box');
    s += txt(380, 165, 'onLeaderFailure → becomeCandidate("onLeaderFailure")', 'fig-key');
    s += txt(380, 192, 'n2/n3 站下来变成 CANDIDATE——但先别急着抬 term,还要 pre-vote', 'fig-sub');
    s += bottom('两侧都发现了失联,状态机各退回 CANDIDATE', '注意:谁都没有马上广播「我要选举」');
    return s + '</svg>';
  }

  /* 步骤 4:pre-vote 假投票 */
  function step4() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('a4');
    s += nodeBox(15, 'n1', 'CANDIDATE', 'pre-vote 没人理', true, true);
    s += nodeBox(269, 'n2', 'CANDIDATE', '发起 pre-vote', false, false);
    s += nodeBox(523, 'n3', 'CANDIDATE', '无 leader,给票', false, false);
    s += txt(507, 120, 'PreVoteRequest / Response(term 仍=5)', 'fig-key');
    s += arrow('a4', N2, 132, 622, 132);
    s += arrow('a4', 642, 160, 400, 160);
    s += txt(126, 140, 'n1 也在试探,但 n2/n3 听不见它', 'fig-sub', true);
    s += txt(126, 166, '若对方已有 leader:直接拒绝', 'fig-sub');
    s += rect(15, 182, 730, 44, 'fig-box');
    s += txt(380, 203, 'StatefulPreVoteCollector:假 Join 凑 VoteCollection', 'fig-key');
    s += txt(380, 221, '2/2 假投票达多数 → 才 startElection;凑不齐就停手,term 一个不加', 'fig-sub');
    s += bottom('pre-vote:不动 term,先证明「联系得到多数」', '拒绝的理由写得很直:already a leader');
    return s + '</svg>';
  }

  /* 步骤 5:正式选举,term+1 */
  function step5() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('a5');
    s += nodeBox(15, 'n1', 'CANDIDATE', 'term 还停在 5', true, true);
    s += nodeBox(269, 'n2', 'CANDIDATE', 'term 5→6 开选', false, false);
    s += nodeBox(523, 'n3', 'CANDIDATE', 'handleStartJoin', false, false);
    s += txt(507, 120, 'StartJoinRequest(term=6) / 回一张 Join', 'fig-key');
    s += arrow('a5', N2, 132, 622, 132);
    s += arrow('a5', 642, 160, 400, 160);
    s += rect(15, 182, 730, 44, 'fig-box');
    s += txt(380, 203, 'joinVotes=2 → electionWon 翻 true → becomeLeader', 'fig-key');
    s += txt(380, 221, '断言:必须已经是 CANDIDATE;n1 那侧 term 没人抬,停在原地', 'fig-sub');
    s += bottom('n2 赢得 term=6 的选举,成为新 LEADER', 'handleStartJoin 拒绝 term 不严格变大的请求');
    return s + '</svg>';
  }

  /* 步骤 6:publish / commit 两阶段 */
  function step6() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('a6');
    s += nodeBox(15, 'n1', 'LEADER(旧)', 'publish 凑不齐', true, true);
    s += nodeBox(269, 'n2', 'LEADER · term=6', '两阶段发布', true, false);
    s += nodeBox(523, 'n3', 'FOLLOWER', 'accept → committed', false, false);
    s += txt(507, 120, 'PublishRequest(v=N+1) → accept,回 Response', 'fig-key');
    s += arrow('a6', N2, 132, 622, 132);
    s += arrow('a6', 642, 160, 400, 160);
    s += txt(507, 184, '2 份 Response → ApplyCommitRequest → markCommitted', 'fig-key');
    s += arrow('a6', 358, 174, 624, 174);
    s += rect(15, 196, 222, 40, 'fig-box');
    s += txt(126, 214, 'n1 侧:1*2>3 不成立', 'fig-sub', true);
    s += txt(126, 230, 'FailedToCommit → 站下来', 'fig-sub', true);
    s += bottom('分区 B 正常更新集群状态;分区 A 一道门都过不去', 'accept ≠ committed:多数 accept 之后才广播第二枪');
    return s + '</svg>';
  }

  /* 步骤 7:愈合 */
  function step7() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('a7');
    s += nodeBox(15, 'n1', 'FOLLOWER', '接受 term=6 状态', false, false);
    s += nodeBox(269, 'n2', 'LEADER · term=6', '正常 publish', true, false);
    s += nodeBox(523, 'n3', 'FOLLOWER', '正常接受发布', false, false);
    s += arrow('a7', 237, 57, 263, 57);
    s += arrow('a7', 491, 57, 517, 57);
    s += txt(380, 122, '网络恢复:n1 看到更高的 term=6', 'fig-key');
    s += txt(126, 150, '变 FOLLOWER', 'fig-sub');
    s += txt(126, 172, '丢弃自造状态', 'fig-sub');
    s += txt(567, 150, '接受多数派已 committed 的状态', 'fig-sub');
    s += rect(15, 188, 730, 40, 'fig-box');
    s += txt(380, 207, 'n1 若曾抬 term:健康侧会看到 maxTermSeen>currentTerm 自行重选', 'fig-sub');
    s += txt(380, 224, 'pre-vote 拒绝「已有 leader」的试探,正是让这种打断不发生', 'fig-sub');
    s += bottom('愈合:term 高者胜,集群回归一个真理', '从头到尾任何时刻最多一个 Master——hasQuorum 那行算术保证的');
    return s + '</svg>';
  }

  window.ESFLOWS = window.ESFLOWS || {};
  window.ESFLOWS['ch22-election'] = {
    version: 1,
    id: 'ch22-election',
    title: '旧 Master 被隔离:一场选举的完整时序',
    speed: 2800,
    steps: [
      { svg: step1(), note: '起点:3 个 master-eligible 节点,n1 是 term=5 的 LEADER,n2/n3 跟随。voting configuration={n1,n2,n3},quorum=2:2*2>3。version 每次 publish 加一,term 只在换届加一。' },
      { svg: step2(), note: '把 n1 的网线拔掉:分区 A 只有 n1(1/3),分区 B 是 n2+n3(2/3)。两侧互不通信——多数派任何时刻只能属于一个分区,这是脑裂防护的地基。' },
      { svg: step3(), note: '两侧各走各的检测:n1 的 FollowersChecker 把 n2/n3 标成 faulty;n2/n3 的 LeaderChecker 等不到心跳,onLeaderFailure → becomeCandidate。注意:没人立刻开选。' },
      { svg: step4(), note: 'n2 先跑 pre-vote:PreVoteRequest 不抬 term(term 仍=5)。n3 没有 leader,给票;若 n3 已认某个 leader 会直接拒绝(already a leader)。2/2 假投票凑齐多数,才允许 startElection——n1 在自己那边怎么试探都凑不齐,term 一个不加。' },
      { svg: step5(), note: '正式选举:getTermForNewElection 把 term 抬到 6,广播 StartJoinRequest。n3 handleStartJoin 拒绝 term 不严格变大的请求、持久化 term=6、回一张 Join。2 张 Join → electionWon 翻 true → becomeLeader(断言:必须已经是 CANDIDATE)。' },
      { svg: step6(), note: '分区 B 恢复写能力:n2 发 PublishRequest(v=N+1),n3 写入 last-accepted(accept≠committed)并回 Response;凑齐 2 份才发 ApplyCommitRequest,n3 markCommitted。同一时刻 n1 那侧 1*2>3 不成立,FailedToCommitClusterStateException,站下来。' },
      { svg: step7(), note: '网络恢复:n1 看到更高的 term=6,变 FOLLOWER,接受多数派已 committed 的状态。回头看:pre-vote 的拒绝保护了多数派不被少数派试探打扰;从头到尾任何时刻最多一个 Master。' }
    ]
  };

  /* ===== 实验 ===== */
  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};

  window.ESEXPERIMENTS['ch22-00-cat-master'] = {
    version: 1, id: 'ch22-00-cat-master',
    title: '实验 0 · _cat/master:当前 Master 一行流',
    method: 'GET', path: '/_cat/master?v',
    body: null,
    predict: '会返回几行?列名是什么?',
    expect: '一行:id / host / ip / node。RestMasterAction 的实现是发一个 ClusterStateRequest、取 nodes.getMasterNodeId() 填表——没有另一套「选举 API」。单节点集群上这一行就是你正在打的那台。'
  };

  window.ESEXPERIMENTS['ch22-01-master-node'] = {
    version: 1, id: 'ch22-01-master-node',
    title: '实验 1 · master_node:同一个 id,同一份真理',
    method: 'GET', path: '/_cluster/state?filter_path=master_node',
    body: null,
    predict: '这个 master_node 和实验 0 的 id 什么关系?',
    expect: '完全相等——_cat/master 和 _cluster/state 读的是同一个 DiscoveryNodes.getMasterNodeId()(第 21 课 Nodes 块)。注意这是 9.4.0 的路径,早已没有 Zen1 时代的 _zen 接口。'
  };

  window.ESEXPERIMENTS['ch22-02-nodes-roles'] = {
    version: 1, id: 'ch22-02-nodes-roles',
    title: '实验 2 · 谁有资格当选:node.role 里的 m',
    method: 'GET', path: '/_cat/nodes?v&h=name,id,node.role,master',
    body: null,
    predict: 'master 列的 * 落在哪一行?node.role 里的字母都是什么意思?',
    expect: 'master 列为 * 的就是当前 Master(与实验 0/1 同一个 id);node.role 含 m 表示 master-eligible——只有这类节点进投票配置、有选举票(实验 3 可证)。单节点是 * 又含 m:自己选自己。'
  };

  window.ESEXPERIMENTS['ch22-03-voting-config'] = {
    version: 1, id: 'ch22-03-voting-config',
    title: '实验 3 · 读投票配置,算出 quorum',
    method: 'GET', path: '/_cluster/state?filter_path=metadata.cluster_coordination',
    body: null,
    predict: 'last_committed_config 里有几个 node id?算式 votedNodesCount * 2 > nodeIds.size() 里,N=几、几票算多数?',
    expect: 'term=1(从没换过届),last_committed_config 与 last_accepted_config 各含 1 个 id(同一个)。1 * 2 > 1 为真:quorum=1,自己投自己就算数。若是 3 节点集群,这里会是 3 个 id → quorum=2。稳定运行时两份 config 相同——它们只在换配置的中途才可能不同。'
  };

  window.ESEXPERIMENTS['ch22-04-discovery-type'] = {
    version: 1, id: 'ch22-04-discovery-type',
    title: '实验 4 · discovery.type=single-node 的承诺',
    method: 'GET', path: '/_nodes/settings?filter_path=nodes.*.settings.discovery.type',
    body: null,
    predict: '本机 docker 的 discovery.type 是什么?Coordinator.doStart 对它有什么额外要求?',
    expect: 'single-node(docker-compose.yml 里写死的)。doStart 要求:开了它,本地节点必须对 committed configuration 自己就构成 quorum——否则拒绝启动。反例:3 节点名单 + single-node,hasQuorum({自己})=false,启动即 IllegalStateException:一个声称单机的进程带着 3 节点配置,既发现不了同伴、又永远选不出主。'
  };

  window.ESEXPERIMENTS['ch22-05-before'] = {
    version: 1, id: 'ch22-05-before',
    title: '实验 5 · 记下 version 与 term(下面要用)',
    method: 'GET',
    path: '/_cluster/state/version,metadata?filter_path=version,state_uuid,metadata.cluster_coordination.term',
    body: null,
    predict: 'version 和 term 哪个数字大?下一次状态更新,两个各会怎么动?',
    expect: 'version 通常远大于 term:version 每次 publish 加一,term 只在换届加一。把这两个数抄下来——实验 7 对照用。预测:PUT 索引后 version+1、term 不动(还是同一任 LEADER)。'
  };

  window.ESEXPERIMENTS['ch22-06-put-index'] = {
    version: 1, id: 'ch22-06-put-index',
    title: '实验 6 · 一次货真价实的状态更新',
    method: 'PUT', path: '/tut-l22-vote',
    body: { settings: { number_of_shards: 1, number_of_replicas: 0 } },
    predict: 'quorum=1 的单节点,publish/commit 这两道门开不开?',
    expect: 'acknowledged: true。单节点的 1 票满足 1*2>1,publish 多数就是自己——门是开的。这证明「更新 ClusterState 走 publish/commit」在单节点同样成立,只是多数恰好是一票。'
  };

  window.ESEXPERIMENTS['ch22-07-after'] = {
    version: 1, id: 'ch22-07-after',
    title: '实验 7 · version +1,term 不动',
    method: 'GET',
    path: '/_cluster/state/version,metadata?filter_path=version,state_uuid,metadata.cluster_coordination.term',
    body: null,
    predict: '对照实验 5 抄下的数字:version、term、state_uuid 各怎么动?',
    expect: 'version +1,state_uuid 换新串,term 不变——同一任 LEADER 在 publish,没有换届。term 变大的唯一途径是重新选举(handleStartJoin);对照动画第 5 帧:n2/n3 那侧 term 5→6 是因为换了 Master,不是例行公事。'
  };

  window.ESEXPERIMENTS['ch22-08-health'] = {
    version: 1, id: 'ch22-08-health',
    title: '实验 8 · quorum=1 的集群自洽吗',
    method: 'GET', path: '/_cluster/health?filter_path=status,number_of_nodes,timed_out',
    body: null,
    predict: '单节点、刚建的索引 0 副本,状态是 green 还是 yellow?',
    expect: 'green,number_of_nodes=1。主分片有处放、副本数为 0 无处安放也无所谓。若你留着前面课程带副本的索引,这里会是 yellow——不是选举出了问题,是副本分片没地方放:第 23 课分片分配的入场券。'
  };

  window.ESEXPERIMENTS['ch22-09-cleanup'] = {
    version: 1, id: 'ch22-09-cleanup',
    title: '清理 · 删 tut-l22-vote',
    method: 'DELETE', path: '/tut-l22-vote',
    predict: '一句话总结本课?',
    expect: 'acknowledged: true——而且这又是一次 publish(quorum=1,version 再 +1)。四道门同一条多数派不变量:pre-vote 试探、选举拿资格、publish 收 ACK、commit 落地;3 节点 quorum=2,任何时刻最多一个分区能写集群真理。'
  };
})();
