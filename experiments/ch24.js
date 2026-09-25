/* experiments/ch24.js — 第 24 课:分片恢复与快照实验 + peer recovery 旗舰动画 */
(function () {
  'use strict';

  /* ===== 动画:一次 peer recovery 的两阶段 ===== */
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
  function side(x, name, lines, hot, anim) {
    var s = rect(x, 15, 222, 118, hot ? 'fig-box-hot' : 'fig-box', anim);
    s += txt(x + 111, 38, name, 'fig-name');
    for (var i = 0; i < lines.length; i++) {
      s += txt(x + 111, 64 + i * 22, lines[i], 'fig-sub');
    }
    return s;
  }
  function mid(x, w, title, sub, hot, anim, warn) {
    var s = rect(x, 150, w, 72, hot ? 'fig-box-hot' : 'fig-box', anim);
    s += txt(x + w / 2, 174, title, 'fig-name', warn);
    s += txt(x + w / 2, 200, sub, 'fig-sub', false);
    return s;
  }
  function bottom(title, sub) {
    var s = rect(15, 240, 730, 48, 'fig-box-hot', 'fp-pop');
    s += txt(380, 261, title, 'fig-name');
    s += txt(380, 281, sub, 'fig-sub');
    return s;
  }

  /* 步骤 1:primary 的家底 */
  function step1() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('p1');
    s += side(15, 'Node-A · primary', ['磁盘 commit:seqNo 0-9', 'segment 文件 + checksum', 'local_checkpoint = 9', 'translog:10、11、12', '(refresh 已可见,未 flush)'], true);
    s += side(523, 'Node-B · replica 目标', ['Lucene 目录还是空的', '第 15 课:CREATED 时', 'currentEngine == null', '等待数据'], false);
    s += txt(380, 140, '第 23 课的下一跳:分片已分到 B,数据从哪来?', 'fig-sub');
    s += mid(190, 380, '家底 = 第 14 课那条缝', '磁盘 commit 一半 + translog 一半:恢复也要分两半搬运', true);
    s += bottom('起点:primary 有 commit 0-9 + 未 flush 的 10-12', '目标目录是空的——它要长出同样的 commit,再补上那三条');
    return s + '</svg>';
  }

  /* 步骤 2:接棒,目标进 RECOVERING */
  function step2() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('p2');
    s += side(15, 'Node-A · primary', ['STARTED,继续服务'], true);
    s += side(523, 'Node-B · 目标', ['第 23 课:过滤链放行 B', 'Master 改 RoutingTable', 'shard = INITIALIZING', 'IndexShard = RECOVERING', 'currentEngine == null'], false, 'fp-pop');
    s += txt(380, 140, '恢复开始前,Engine 还没建——顺序不能倒', 'fig-sub');
    s += mid(190, 380, 'RECOVERING:收文件的姿势已就位', 'innerOpenEngineAndTranslog 要求 RECOVERING 且无 Engine(第 15 课)', false);
    s += bottom('第 23 课给节点,这一课给数据', '两步:先把 commit 文件拷齐,再补 commit 之后的 ops');
    return s + '</svg>';
  }

  /* 步骤 3:phase1 准备 */
  function step3() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('p3');
    s += side(15, '源端:acquireSafeCommit', ['拿到 safe commit', '读 user data:', 'local_checkpoint = 9', '→ startingSeqNo = 10', '只看 commit,不看 NRT'], true);
    s += side(523, '目标端:报文件清单', ['目标已有的文件:', '同 size + 同 checksum', '→ reuse,不再传', '缺的才进传输计划'], false);
    s += txt(380, 140, 'FILES_INFO:先对账,后传文件', 'fig-sub');
    s += mid(190, 380, 'phase1 计划 = commit 文件 - 可 reuse 的', '节点离开又回来、目录没清干净时,这里能省一大截', false);
    s += bottom('phase1 的输入是 IndexCommit,不是 IndexWriter 缓冲', 'refresh 过但没 flush 的 10-12:文件里没有它们');
    return s + '</svg>';
  }

  /* 步骤 4:phase1 拷文件 */
  function step4() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('p4');
    s += side(15, '源端:FILE_CHUNK', ['按文件分块传输', '走限速:', 'indices.recovery', '.max_bytes_per_sec', 'CLEAN_FILES 收尾'], true);
    s += side(523, '目标端:写进 Store', ['目录里长出同样的', 'segment 文件(seqNo 0-9)', '能打开同样的 last commit', 'stage = INDEX', 'index.files 计数在这里'], false, 'fp-pop');
    s += arrow('p4', 237, 74, 517, 74);
    s += txt(380, 140, '拷完之后目标有一份「合法的 Lucene 目录」', 'fig-sub');
    s += mid(190, 380, '_recovery 的 index.files 块', 'total / reused / recovered 对应这一阶段(实验 6 会读到 reused)', false);
    s += bottom('phase1 完成:文件那半到位', '但 10-12 还没到——它们不在任何 commit 里');
    return s + '</svg>';
  }

  /* 步骤 5:PREPARE_TRANSLOG 开 Engine */
  function step5() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('p5');
    s += side(15, '源端:prepareTargetForTranslog', ['通知目标:准备收 ops', '不是拷 .tlog 文件', 'ops 即将按 seqNo 发'], true);
    s += side(523, '目标端:开 Engine', ['PREPARE_TRANSLOG 到达', 'openEngineAndSkip', 'TranslogRecovery()', '断言:Type == PEER', '本地 .tlog 不 replay'], false, 'fp-pop');
    s += txt(380, 140, 'Engine 开在文件之后:Directory 上此刻才允许挂 IndexWriter', 'fig-sub');
    s += mid(190, 380, '为什么 skip?', '缺失 ops 会从网络以 PEER_RECOVERY origin 写进这个 Engine', false);
    s += bottom('先文件后 Engine——顺序就是正确性', '第 15 课 currentEngine==null 的那扇窗,这一步才关上');
    return s + '</svg>';
  }

  /* 步骤 6:phase2 发 ops */
  function step6() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('p6');
    s += side(15, '源端:phase2', ['对 [10, maxSeqNo]', '建 changes snapshot', 'OperationBatchSender', '分批发 TRANSLOG_OPS', '不走限速'], true);
    s += side(523, '目标端:放 ops', ['applyTranslogOperation', 'origin = PEER_RECOVERY', 'seqNo 沿用 primary 的', '不重新分配', 'translog 计数在这里'], false, 'fp-pop');
    s += arrow('p6', 237, 74, 517, 74);
    s += txt(380, 140, '传的是解码后的 Operation 列表,不是 .tlog 文件', 'fig-sub');
    s += mid(190, 380, '_recovery 的 translog 块', 'recovered / total / percent:实验 14-18 的 uncommitted 就是这截', false);
    s += bottom('phase2 完成:目标追平 primary', 'ops 必须尽快追上——所以不和大文件抢限速阀门');
    return s + '</svg>';
  }

  /* 步骤 7:finalize 与对照 */
  function step7() {
    var s = '<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">' + defs('p7');
    s += side(15, '源端:finalizeRecovery', ['同步 global checkpoint', '必要时 force flush'], true);
    s += side(523, '目标端:DONE → STARTED', ['shard 转为 STARTED', ' replica 上线', '集群回到 Green'], false, 'fp-pop');
    s += txt(380, 140, '对照:若那 3 条先 _flush 过呢?', 'fig-sub');
    s += mid(190, 380, 'flush 之后,10-12 进了新 commit', 'phase1 会把它们当文件拷走;phase2 从新的 local_checkpoint+1 起', false);
    s += bottom('可见 ≠ 已 commit', 'refresh 换 searcher 不推进 commit——phase1 拷的是 commit,phase2 补的是缝');
    return s + '</svg>';
  }

  window.ESFLOWS = window.ESFLOWS || {};
  window.ESFLOWS['ch24-peer-recovery'] = {
    version: 1,
    id: 'ch24-peer-recovery',
    title: '一次 peer recovery 的两阶段',
    speed: 2600,
    steps: [
      { svg: step1(), note: 'primary 的家底:磁盘 commit 覆盖 seqNo 0-9(local_checkpoint=9),translog 里躺着 10、11、12——refresh 已让它们可搜,但还没 flush。replica 目标的 Lucene 目录是空的。恢复 = 把这两半分别搬过去。' },
      { svg: step2(), note: '第 23 课接棒:过滤链放行 Node-B,Master 写 RoutingTable(shard=INITIALIZING),目标 IndexShard 进 RECOVERING、currentEngine==null。顺序从这就定死了:先收文件,Engine 最后才开。' },
      { svg: step3(), note: '源端 acquireSafeCommit:只信 commit 里的 user data,local_checkpoint=9 → startingSeqNo=10。FILES_INFO 先对账:目标已有的文件只要 size+checksum 全同就 reuse,缺的才进传输计划——节点短暂离开又回来时这里省一大截。' },
      { svg: step4(), note: 'phase1 按 FILE_CHUNK 传文件,走 indices.recovery.max_bytes_per_sec 限速,CLEAN_FILES 收尾。目标长出同样的 last commit(stage=INDEX);_recovery 的 index.files.total/reused/recovered 记的就是这一阶段。10-12 不在其中。' },
      { svg: step5(), note: 'PREPARE_TRANSLOG:目标调 openEngineAndSkipTranslogRecovery(断言 recoverySource 是 PEER)。skip 本地 translog,因为缺失 ops 将以 PEER_RECOVERY origin 从网络写进这个 Engine。Engine 开在文件之后——第 15 课那扇窗此刻才关上。' },
      { svg: step6(), note: 'phase2:源端对 [10, maxSeqNo] 建 changes snapshot,OperationBatchSender 分批发 TRANSLOG_OPS——传的是解码后的 Operation 列表,不是 .tlog 文件,而且不走限速。目标 applyTranslogOperation,seqNo 沿用 primary 分配的,不再生成一份。' },
      { svg: step7(), note: 'finalizeRecovery 同步 global checkpoint、必要时 force flush,shard 转 STARTED。对照:若那 3 条先 _flush 过,phase1 会把它们当文件拷走、phase2 从新的 local_checkpoint+1 起。refresh 救不了它们——可见 ≠ 已 commit,第 14 课的缝贯穿到底。' }
    ]
  };

  /* ===== 实验 ===== */
  window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};

  window.ESEXPERIMENTS['ch24-00-setup'] = {
    version: 1, id: 'ch24-00-setup',
    title: '实验 0 · 建 tut-l24-rec(1 主 0 副)',
    method: 'PUT', path: '/tut-l24-rec',
    body: { settings: { number_of_shards: 1, number_of_replicas: 0 } },
    predict: '新 primary 的恢复 type 会是哪个?',
    expect: 'acknowledged: true。新索引的 primary 没有对端可拷、本地也没有旧数据——RecoverySource 是 EMPTY_STORE。对照六种来源表:只有 replica/relocation 目标才走 PEER。'
  };

  window.ESEXPERIMENTS['ch24-01-recovery-empty'] = {
    version: 1, id: 'ch24-01-recovery-empty',
    title: '实验 1 · _recovery:EMPTY_STORE / DONE',
    method: 'GET', path: '/tut-l24-rec/_recovery?human=true',
    body: null,
    predict: 'type、stage 各是什么?JSON 挂在顶层 recoveries 数组还是索引名下面?',
    expect: 'tut-l24-rec.shards[0]:type=EMPTY_STORE、stage=DONE、primary=true。JSON 挂在索引名下的 shards 数组(RecoveryResponse.toXContentChunked),没有顶层 recoveries 键。stage 抓不住 INDEX/TRANSLOG:空索引恢复只有几十毫秒——和第 15 课 _cat 抓不住 CREATED 同一原因。index.files 与 translog 两块字段都在,对应两阶段。'
  };

  window.ESEXPERIMENTS['ch24-02-doc'] = {
    version: 1, id: 'ch24-02-doc',
    title: '实验 2 · 写一篇(给 reused 准备弹药)',
    method: 'PUT', path: '/tut-l24-rec/_doc/1?refresh=true',
    body: { title: 'recovery-files' },
    predict: '这篇现在在 Lucene commit 里吗?',
    expect: 'created。refresh 只让它可搜;磁盘上还没有覆盖它的 commit(第 14 课)。下一步 flush 把它变成磁盘文件,close/open 后才能被登记为 reused。'
  };

  window.ESEXPERIMENTS['ch24-03-flush'] = {
    version: 1, id: 'ch24-03-flush',
    title: '实验 3 · _flush:落成磁盘 commit',
    method: 'POST', path: '/tut-l24-rec/_flush?filter_path=_shards',
    body: null,
    predict: 'flush 之后,这篇进入 IndexCommit 了吗?translog 呢?',
    expect: '_shards.total=1。flush 把内存里的 segment fsync 成新 commit 并清掉对应 translog(第 14 课);现在磁盘上有了一份含这篇的合法 Lucene 目录——close/open 后它就是 reused 的来源。'
  };

  window.ESEXPERIMENTS['ch24-04-close'] = {
    version: 1, id: 'ch24-04-close',
    title: '实验 4 · _close:关掉索引(数据仍在磁盘)',
    method: 'POST', path: '/tut-l24-rec/_close?filter_path=acknowledged,indices',
    body: null,
    predict: 'close 会删数据吗?shard 去哪了?',
    expect: 'acknowledged: true。close 只是卸掉 shard 的内存结构(Engine、searcher),磁盘上的 Store 原样保留,RoutingTable 里分片标记为关闭。下次 open 就是一次 EXISTING_STORE 恢复——本地磁盘还在的场景。'
  };

  window.ESEXPERIMENTS['ch24-05-open'] = {
    version: 1, id: 'ch24-05-open',
    title: '实验 5 · _open:重新打开',
    method: 'POST', path: '/tut-l24-rec/_open?filter_path=acknowledged',
    body: null,
    predict: '这次的 RecoverySource 会变成哪个?',
    expect: 'acknowledged: true。本地 Store 里已有 commit → EXISTING_STORE:StoreRecovery.recoverFromStore 把已有 Lucene 文件登记为 reused,再 openEngineAndRecoverFromTranslog。下一跑读字段。'
  };

  window.ESEXPERIMENTS['ch24-06-recovery-existing'] = {
    version: 1, id: 'ch24-06-recovery-existing',
    title: '实验 6 · _recovery?detailed:EXISTING_STORE + reused',
    method: 'GET', path: '/tut-l24-rec/_recovery?detailed=true&human=true',
    body: null,
    predict: 'type 变了吗?index.files.reused 和 recovered 谁大?',
    expect: 'type=EXISTING_STORE、stage 仍 DONE。index.files 里 reused>0(本机已有的 commit 文件直接登记,recovered≈0)——文件没从别人那拷。detailed=true 时 index.files.details 列出每个文件(RecoveryFilesDetails.toXContent 看 params.detailed)。这与 yaml 测试 indices.recovery/10_basic.yml 的两条断言一一对应。'
  };

  window.ESEXPERIMENTS['ch24-07-replicas-1'] = {
    version: 1, id: 'ch24-07-replicas-1',
    title: '实验 7 · 副本改 1:想看 PEER,但单节点给不出',
    method: 'PUT', path: '/tut-l24-rec/_settings',
    body: { index: { number_of_replicas: 1 } },
    predict: 'replica 会被分到哪?恢复会开始吗?',
    expect: 'acknowledged: true。第 23 课的答案:same_shard 把唯一节点剔除,replica 停在 UNASSIGNED——「需要 peer recovery」不等于「正在 peer recovery」。下一跑验证 _recovery 里不会多出 PEER 行。'
  };

  window.ESEXPERIMENTS['ch24-08-no-peer-row'] = {
    version: 1, id: 'ch24-08-no-peer-row',
    title: '实验 8 · _recovery 里没有 PEER 行',
    method: 'GET', path: '/tut-l24-rec/_recovery?filter_path=**.type,**.stage,**.primary',
    body: null,
    predict: '会多出一条 type: PEER 的记录吗?',
    expect: '不会:shards 里仍只有那条 primary 的 EXISTING_STORE/DONE。_recovery 只列「已开始」的恢复;UNASSIGNED 的 replica 没开始,自然没有行。想真看 PEER,要第二台节点接副本(两节点的思考题 1 就是那个场景)。'
  };

  window.ESEXPERIMENTS['ch24-09-fs-repo-put'] = {
    version: 1, id: 'ch24-09-fs-repo-put',
    title: '实验 9 · 注册 fs 仓库:如实失败',
    method: 'PUT', path: '/_snapshot/tut-l24-repo',
    body: { type: 'fs', settings: { location: '/tmp/es-backup' } },
    predict: '会 200 吗?错误文案会提哪个 setting?',
    expect: '非 200:RepositoryException,文案含 location [...] doesn\'t match any of the locations specified by path.repo because this setting is empty。FsRepository 构造时 resolveRepoDir 对不上就拒绝——fs 仓库要求 location 落在节点配置的 path.repo 白名单里,不是操作系统权限问题(/tmp 谁都能写也没用)。这是预期行为,不是实验失败。'
  };

  window.ESEXPERIMENTS['ch24-10-fs-repo-list'] = {
    version: 1, id: 'ch24-10-fs-repo-list',
    title: '实验 10 · 仓库列表:空的',
    method: 'GET', path: '/_snapshot/_all',
    body: null,
    predict: '注册失败的仓库会出现在列表里吗?',
    expect: '空对象 {}——注册失败即不存在,不要接着 PUT _snapshot/tut-l24-repo/snap-1(那只是另一条 404/500)。增量语义不靠本地 Demo:BlobStoreRepository 按「物理名+size+checksum」reuse 已有 blob,只上传新文件(indexIncrementalFileCount)。'
  };

  window.ESEXPERIMENTS['ch24-11-gap-setup'] = {
    version: 1, id: 'ch24-11-gap-setup',
    title: '实验 11 · 建 tut-l24-gap(冻结自动 refresh)',
    method: 'PUT', path: '/tut-l24-gap',
    body: { settings: { number_of_shards: 1, number_of_replicas: 0, refresh_interval: -1 } },
    predict: '为什么要 refresh_interval=-1?',
    expect: 'acknowledged: true。和第 16 课同一手法:冻住自动 refresh,让「SEARCH 可见与否」完全由我们手动控制,实验结果无竞态、可复现。'
  };

  window.ESEXPERIMENTS['ch24-12-gap-flush'] = {
    version: 1, id: 'ch24-12-gap-flush',
    title: '实验 12 · _flush 打底:一个干净的 commit',
    method: 'POST', path: '/tut-l24-gap/_flush?filter_path=_shards',
    body: null,
    predict: '这一步保证什么?',
    expect: '磁盘上有了一个确定的 commit 点(local_checkpoint=某值)。接下来写入的那篇,相对这个 commit 就是「commit 之后」——正好是动画里 ops 10-12 的角色。'
  };

  window.ESEXPERIMENTS['ch24-13-gap-doc'] = {
    version: 1, id: 'ch24-13-gap-doc',
    title: '实验 13 · 写一篇,不 flush',
    method: 'PUT', path: '/tut-l24-gap/_doc/1',
    body: { title: 'only-in-translog' },
    predict: '这篇现在活在内存 + translog 里。如果此刻发生 peer recovery,phase1 拷走的文件里有它吗?',
    expect: 'created。它不在任何 Lucene commit 里:peer 的 phase1 拷不到它,只能靠 phase2 按 seqNo 发 ops 补——或者在节点重启场景由 recoverFromTranslogInternal 从 localCheckpoint+1 重放。下一跑读它的账本。'
  };

  window.ESEXPERIMENTS['ch24-14-gap-stats'] = {
    version: 1, id: 'ch24-14-gap-stats',
    title: '实验 14 · uncommitted_operations=1:那条缝有多宽',
    method: 'GET',
    path: '/tut-l24-gap/_stats/translog?filter_path=indices.tut-l24-gap.primaries.translog',
    body: null,
    predict: 'uncommitted_operations 是 0 还是 1?这个数字对应两阶段的哪一段?',
    expect: 'uncommitted_operations=1(还有 earliest_last_modified_age 等)。它就是 flush 没盖住的那截——动画 phase2 要发的 ops 数量、本地重启时 recoverFromTranslogInternal 要重放的数量。phase1 的文件计数里永远没有它。'
  };

  window.ESEXPERIMENTS['ch24-15-gap-search0'] = {
    version: 1, id: 'ch24-15-gap-search0',
    title: '实验 15 · SEARCH:0 hits(refresh 冻着)',
    method: 'GET', path: '/tut-l24-gap/_search?q=title:only-in-translog&filter_path=hits.total',
    body: null,
    predict: '能搜到吗?',
    expect: 'hits.total.relation=eq、value=0。refresh_interval=-1 且没手动 refresh:searcher 还是旧的。第 14 课写入全路径的另一半:可见性由 refresh 决定,与 commit/translog 无关。'
  };

  window.ESEXPERIMENTS['ch24-16-gap-refresh'] = {
    version: 1, id: 'ch24-16-gap-refresh',
    title: '实验 16 · 手动 _refresh:换 searcher',
    method: 'POST', path: '/tut-l24-gap/_refresh?filter_path=_shards.total',
    body: null,
    predict: 'refresh 会把这篇写进磁盘 commit 吗?',
    expect: '_shards.total=1。refresh 只是把内存里未提交的 NRT segment 换成 EXTERNAL searcher——它不 fsync、不换 commit 点。这篇「可见」了,但 local_checkpoint 没变:phase1 拷的 safe commit 里仍然没有它。'
  };

  window.ESEXPERIMENTS['ch24-17-gap-search1'] = {
    version: 1, id: 'ch24-17-gap-search1',
    title: '实验 17 · SEARCH:1 hit(可见 ≠ 已 commit)',
    method: 'GET', path: '/tut-l24-gap/_search?q=title:only-in-translog&filter_path=hits.total',
    body: null,
    predict: '现在能搜到了。它能被 phase1 拷走吗?',
    expect: 'value=1。能搜到,但仍不在 commit 里:可见性(refresh)与持久化(flush)是两件事。若以为「能搜到就可以只拷文件、不必重放 translog」,就是把 EXTERNAL searcher 当成了 acquireSafeCommit 拿到的那份 commit。'
  };

  window.ESEXPERIMENTS['ch24-18-gap-stats2'] = {
    version: 1, id: 'ch24-18-gap-stats2',
    title: '实验 18 · uncommitted 仍是 1:refresh 救不了那条缝',
    method: 'GET',
    path: '/tut-l24-gap/_stats/translog?filter_path=indices.tut-l24-gap.primaries.translog.uncommitted_operations',
    body: null,
    predict: 'refresh 之后这个数字变了吗?',
    expect: '仍是 1。refresh 不推进 Lucene commit:那篇依然只活在 translog 里,恢复时依然要走 phase2 重放。只有 _flush 才会把这截收进文件(那时 phase1 就能拷走它——动画第 7 帧的对照)。'
  };

  window.ESEXPERIMENTS['ch24-19-cleanup'] = {
    version: 1, id: 'ch24-19-cleanup',
    title: '清理 · 删两个 tut-l24 索引',
    method: 'DELETE', path: '/tut-l24-rec',
    body: null,
    predict: '一句话总结本课?',
    expect: 'acknowledged: true。再手动 DELETE /tut-l24-gap(若实验 9 的仓库碰巧注册成功,补 DELETE /_snapshot/tut-l24-repo;没站住时那条同样 404,可忽略)。恢复沿第 14 课那条缝:commit 之前拷文件(phase1),commit 之后重放 ops(phase2);快照只是把对端从 primary 换成仓库,增量单位永远是文件。'
  };
})();
