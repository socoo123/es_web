/* experiments/ch24.js — ES 9.4.0 / Lucene 10.4.0；预期不是实测响应。 */
(function () {
  'use strict';
  function rect(x,y,w,h,cls){return '<rect x="'+x+'" y="'+y+'" width="'+w+'" height="'+h+'" rx="9" class="'+cls+'"/>';}
  function txt(x,y,s,cls){return '<text x="'+x+'" y="'+y+'" text-anchor="middle" class="'+cls+'">'+s+'</text>';}
  function box(x,title,lines,hot){var s=rect(x,22,270,146,hot?'fig-box-hot':'fig-box');s+=txt(x+135,47,title,'fig-name');lines.forEach(function(line,i){s+=txt(x+135,73+i*21,line,'fig-sub');});return s;}
  function frame(n,left,right,middle,conclusion,transfer){var id='ch24-peer-step-'+n+'-arrow';var s='<svg viewBox="0 0 760 360" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Peer recovery 第 '+n+' 步">';s+='<defs><marker id="'+id+'" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M 0 0 L 10 5 L 0 10 z" class="fig-arrowhead"/></marker></defs>';s+=box(20,left[0],left.slice(1),true)+box(470,right[0],right.slice(1),false);if(transfer){s+='<line x1="290" y1="91" x2="462" y2="91" class="fig-arrow fp-draw" pathLength="1" marker-end="url(#'+id+')"/>';s+=txt(380,79,transfer,'fig-sub');}s+=rect(20,190,720,68,'fig-box');s+=txt(380,216,middle[0],'fig-name')+txt(380,240,middle[1],'fig-sub');s+=rect(20,282,720,56,'fig-box-hot');s+=txt(380,305,conclusion[0],'fig-name')+txt(380,327,conclusion[1],'fig-sub');return s+'</svg>';}
  var frames=[
    frame(1,['Node A · 活动主分片','选定 safe commit：0–9','local_checkpoint = 9','max_seq_no = 12','示意的安全基线已可用'],['Node B · 新副本目标','空目录，尚无可用历史','路由 INITIALIZING','IndexShard RECOVERING','这是文件恢复的特定示例'],['本示例的起点：safe commit + 后续历史','序号用于教学，不是所有索引固定的恢复计数'],['先确定恢复基线','safe commit 可能旧于最新 commit；不由 uncommitted 直接推算']),
    frame(2,['源端 · 等待恢复请求','从活动主分片恢复普通副本','校验请求中的历史信息','操作路径需完整历史','同时核对 retention lease'],['目标 · 先尝试本地准备','有旧 store 可临时开 Engine','重放到本地 global checkpoint','关闭临时 Engine 再发请求','空目录无法提供有效起点'],['有旧历史时可能走操作恢复','不能说每次 PEER 都先传文件，或完全不使用本地 translog'],['本动画继续演示空目标分支','操作恢复条件不满足，选文件基线']),
    frame(3,['源端 · 选定安全提交','acquireSafeCommit','startingSeqNo = 9 + 1','保护所需历史','计算 recovery file plan'],['目标 · 比较已有文件','按物理名查找元数据','isSame：长度、校验与 hash','writer UUID 也可参与','整段比较可影响复用'],['文件恢复从选定 safe commit 的文件起步','NRT 搜索可见性不是文件基线；最新 flush 也不保证被选中'],['示例 startingSeqNo = 10','实际起点由所选提交决定；操作恢复则由目标请求决定']),
    frame(4,['源端 · FILE_CHUNK','不匹配的文件分块传输','文件路径调用 RateLimiter','CLEAN_FILES 完成目录处理','并发和字节限速是不同约束'],['目标 · 文件就绪','匹配文件直接 reuse','缺失文件写入 Store','记录 index.files / index.size','特定计划可从快照辅助下载'],['文件来源由恢复计划决定','箭头仅表示本例源端文件数据；省略快照辅助及其失败回退'],['空目标示例先取得 0–9 的文件基线','阶段可能重置或重试，计数以这次恢复的实际信息为准'],'文件数据'),
    frame(5,['源端 · 准备发送操作','发送 PREPARE_TRANSLOG','准备后接入正常复制','再采样 endingSeqNo','避免并发写入落在两条路之间'],['目标 · 网络恢复 Engine','openEngineAndSkip…','此入口不再重放本地 tlog','要求 RECOVERING / 无 Engine','早先本地准备的临时实例已关'],['skip 是本次打开入口的行为','不代表 peer 从来没做本地 replay，也不等于删掉整个本地 translog'],['文件路径：文件处理完成后再开此 Engine','Engine 就绪后可一边接收恢复操作，一边接收正常复制']),
    frame(6,['源端 · phase2 历史快照','newChangesSnapshot','普通引擎读取 Lucene 历史','示例发送 seqNo 10–12','分批调用 TRANSLOG_OPS'],['目标 · 应用恢复操作','applyTranslogOperation','origin = PEER_RECOVERY','沿用原 seqNo / primary term','回报已处理 local checkpoint'],['translog 是协议与计数命名，不限定物理来源','此发送链没有 FILE_CHUNK 的同一限速调用；仍有并发与资源约束'],['操作数量不等于 uncommitted_operations','受起止区间、历史、过滤及并发写入影响'],'操作数据'),
    frame(7,['源端 · 收尾与同步','等待目标追平并纳入 in-sync','发送 global checkpoint','主搬迁还有上下文交接','本动画省略故障与重试'],['目标 · 完成并上报','同步 checkpoint / lease','必要时 flush 与旧操作清理','RecoveryState 进入 DONE','IndexShard 先 POST_RECOVERY'],['DONE 与路由 STARTED 是不同步骤','Master 接到报告更新路由，目标应用 active 路由后进入 STARTED'],['一个副本完成不保证整个集群 Green','其他索引、其他副本和约束仍可能让集群 Yellow 或 Red'])
  ];
  var notes=[
    '选定文件恢复的示意输入：safe commit local_checkpoint=9，当前 max_seq_no=12，目标为空。该安全提交可能旧于最新 commit；10–12 只是本例后续历史，不能由本地 uncommitted_operations 推算真实发送量。',
    '目标先尝试 recoverLocallyUpToGlobalCheckpoint：旧 store 可用时临时开 Engine、本地重放并关闭，再发送 startingSeqNo。源端检查同历史、完整历史与 lease 条件；本例为空目标，继续文件路径。',
    '文件路径 acquireSafeCommit，startingSeqNo=其 local_checkpoint+1。文件计划对比目标元数据，isSame 含 hash/writer UUID 条件，整段分组也影响复用。操作路径则跳过传文件，采用目标起点。',
    '本例 FILE_CHUNK 从源端传文件，调用恢复字节限速；匹配文件复用，CLEAN_FILES 收尾。实际 recovery plan 也可能借助快照仓库获取文件；本帧只画源端文件数据，相关来源见正文。',
    'PREPARE_TRANSLOG 在这一入口打开 Engine 并 skip 本地 replay；不能据此抹掉早先的本地恢复。源端先 initiateTracking 接入正常复制，再取 endingSeqNo 和历史快照，防止并发写入遗漏。',
    'newChangesSnapshot 在当前普通引擎中从 Lucene 读取历史，分批发送解码 Operation，目标以 PEER_RECOVERY 应用原序号。此链无 FILE_CHUNK 同一 RateLimiter 调用，仍受并发、CPU、磁盘和网络约束。',
    '收尾等待追平、同步 checkpoint/lease，目标必要时 flush。恢复进度 DONE 与 IndexShard 的 POST_RECOVERY、Master 改路由、应用后 STARTED 分开。单份恢复完成并不保证整个集群 Green。'
  ];
  window.ESFLOWS=window.ESFLOWS||{};
  window.ESFLOWS['ch24-peer-recovery']={version:1,id:'ch24-peer-recovery',title:'Peer recovery：文件路径的七步示意',speed:2600,steps:frames.map(function(svg,i){return {svg:svg,note:notes[i]};})};
  window.ESEXPERIMENTS=window.ESEXPERIMENTS||{};
  var operations=[
  {
    "version": 1,
    "id": "ch24-version",
    "title": "前提 1 · 核对服务端版本",
    "method": "GET",
    "path": "/",
    "body": null,
    "predict": "节点版本和图解源码版本一致吗？",
    "expect": "核对 version.number=9.4.0 与 lucene_version=10.4.0。控制台默认 http://localhost:9200、免认证，仅适用于仓库学习节点；其他环境用自己的 endpoint 和认证别名。未匹配版本时不要套用源码数字。"
  },
  {
    "version": 1,
    "id": "ch24-nodes",
    "title": "前提 2 · 节点数、角色与 path.repo",
    "method": "GET",
    "path": "/_nodes/settings?filter_path=nodes.*.name,nodes.*.roles,nodes.*.version,nodes.*.settings.path.repo",
    "body": null,
    "predict": "有几个可放本课普通索引的数据节点？有没有 path.repo？",
    "expect": "默认实验使用一个可用数据节点。数 nodes 并核对 roles；专用冻结节点等不等于本课可用节点。settings.path.repo 缺失表示未配置该显式 setting；fs 扩展还要求相关 master/data 节点的路径、共享目录和权限一致。"
  },
  {
    "version": 1,
    "id": "ch24-read-recovery-settings",
    "title": "前提 3 · 读取恢复设置及覆盖",
    "method": "GET",
    "path": "/_cluster/settings?include_defaults=true&flat_settings=true&filter_path=defaults.indices.recovery.*,persistent.indices.recovery.*,transient.indices.recovery.*",
    "body": null,
    "predict": "文件限速和操作并发是同一个 setting 吗？",
    "expect": "分别读 max_bytes_per_sec、max_concurrent_file_chunks、max_concurrent_operations 等，以及 persistent/transient 覆盖。值依节点角色、内存或配置变化；本课只读取。操作发送没有 FILE_CHUNK 同一 RateLimiter 调用，不等于没有并发和资源限制。"
  },
  {
    "version": 1,
    "id": "ch24-head-rec",
    "title": "A1 · 检查恢复索引尚不存在",
    "method": "HEAD",
    "path": "/tut-l24-rec",
    "body": null,
    "predict": "干净起点应该是 200 还是 404？",
    "expect": "预期 404。若 200，这个名字仅供本章学习，先检查内容并完成本章清理，再从 A1 重做；不要在旧索引上重复创建来推断 EMPTY_STORE。"
  },
  {
    "version": 1,
    "id": "ch24-00-setup",
    "title": "A2 · 建恢复索引：1 主 0 副",
    "method": "PUT",
    "path": "/tut-l24-rec",
    "body": {
      "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
        "auto_expand_replicas": "false",
        "refresh_interval": "1s"
      },
      "mappings": {
        "dynamic": "strict",
        "properties": {
          "marker": {
            "type": "keyword"
          }
        }
      }
    },
    "predict": "新主分片的来源是什么？",
    "expect": "预期 acknowledged=true；shards_acknowledged 只说明该次创建的等待结果。显式普通索引、1P0R、关闭自动扩副本、marker keyword。首次来源为 EMPTY_STORE，下一卡等待后再读取。"
  },
  {
    "version": 1,
    "id": "ch24-wait-rec-new",
    "title": "等待 · tut-l24-rec 达到 green",
    "method": "GET",
    "path": "/_cluster/health/tut-l24-rec?wait_for_status=green&wait_for_no_initializing_shards=true&wait_for_no_relocating_shards=true&timeout=30s",
    "body": null,
    "predict": "状态变更已确认，分片也已完成了吗？",
    "expect": "继续条件：timed_out=false，status=green，initializing_shards=0、relocating_shards=0。超时或颜色不符先定位分配原因，不把 acknowledged 当恢复完成。"
  },
  {
    "version": 1,
    "id": "ch24-01-recovery-empty",
    "title": "A4 · 读取 EMPTY_STORE 恢复",
    "method": "GET",
    "path": "/tut-l24-rec/_recovery?detailed=true&human=true",
    "body": null,
    "predict": "返回结构在哪里？type 与 stage 各表示什么？",
    "expect": "按 tut-l24-rec.shards 找 id=0、primary=true 的行；满足前卡条件时预期 EMPTY_STORE/DONE。index.files 是文件账、translog 是恢复操作账，适用各恢复来源，不是所有行都经历网络 phase1/phase2。数字不写死。"
  },
  {
    "version": 1,
    "id": "ch24-02-doc",
    "title": "A5 · 写入一条 marker 并刷新",
    "method": "PUT",
    "path": "/tut-l24-rec/_doc/1?refresh=true",
    "body": {
      "marker": "recovery_files"
    },
    "predict": "refresh=true 是否承诺新的 commit？",
    "expect": "干净起点 result=created，重复此卡为 updated。refresh=true 请求可见性，不承诺推进 Lucene commit；后台或其他操作仍可能 flush。下一卡显式提交。"
  },
  {
    "version": 1,
    "id": "ch24-03-flush",
    "title": "A6 · 显式 flush 恢复索引",
    "method": "POST",
    "path": "/tut-l24-rec/_flush?wait_if_ongoing=true",
    "body": null,
    "predict": "flush 会把所有旧 translog 文件立刻删掉吗？",
    "expect": "检查 _shards.failed=0。flush 建立提交边界并滚动 translog，旧代是否删除受引用和保留策略影响。该提交也不能直接当成之后 peer 选中的 safe commit。"
  },
  {
    "version": 1,
    "id": "ch24-04-close",
    "title": "A7 · 关闭恢复索引",
    "method": "POST",
    "path": "/tut-l24-rec/_close",
    "body": null,
    "predict": "close 和 delete 有什么差别？",
    "expect": "检查 acknowledged 与 indices.tut-l24-rec.closed。关闭保留磁盘数据；当前版本的关闭流程也会验证、flush 并恢复关闭的分片，不能把旧记录永久保留当事实。下一卡重新打开。"
  },
  {
    "version": 1,
    "id": "ch24-05-open",
    "title": "A8 · 重新打开恢复索引",
    "method": "POST",
    "path": "/tut-l24-rec/_open?wait_for_active_shards=all&timeout=30s",
    "body": null,
    "predict": "open 已 acknowledged，就可以直接假定 DONE 吗？",
    "expect": "检查 acknowledged、shards_acknowledged，再执行下一等待卡。已有普通本地 store 的主分片采用 EXISTING_STORE；等待失败先定位，不快速连点下一卡。"
  },
  {
    "version": 1,
    "id": "ch24-wait-rec-open",
    "title": "等待 · tut-l24-rec 达到 green",
    "method": "GET",
    "path": "/_cluster/health/tut-l24-rec?wait_for_status=green&wait_for_no_initializing_shards=true&wait_for_no_relocating_shards=true&timeout=30s",
    "body": null,
    "predict": "状态变更已确认，分片也已完成了吗？",
    "expect": "继续条件：timed_out=false，status=green，initializing_shards=0、relocating_shards=0。超时或颜色不符先定位分配原因，不把 acknowledged 当恢复完成。"
  },
  {
    "version": 1,
    "id": "ch24-06-recovery-existing",
    "title": "A10 · 读取 EXISTING_STORE 与复用文件",
    "method": "GET",
    "path": "/tut-l24-rec/_recovery?detailed=true&human=true",
    "body": null,
    "predict": "哪些文件从本机复用，哪些经网络获取？",
    "expect": "预期主分片 EXISTING_STORE/DONE；有已提交数据时通常 reused>0，detailed 文件明细可对照。本地复用不意味着传输；文件数量取决于实际 commit。此 API 是各当前分片保存的恢复信息，非完整历史档案。"
  },
  {
    "version": 1,
    "id": "ch24-07-replicas-1",
    "title": "A11 · 将恢复索引改为 1 副本",
    "method": "PUT",
    "path": "/tut-l24-rec/_settings",
    "body": {
      "index": {
        "number_of_replicas": 1
      }
    },
    "predict": "单数据节点能启动该副本的 peer 恢复吗？",
    "expect": "预期 acknowledged=true。一个可用数据节点且主已在其上时，same_shard 不允许同号副本也落在此处；副本 UNASSIGNED。若有第二个合格数据节点，可能开始 PEER，本段预期须相应改变。"
  },
  {
    "version": 1,
    "id": "ch24-wait-rec-yellow",
    "title": "等待 · tut-l24-rec 达到 yellow",
    "method": "GET",
    "path": "/_cluster/health/tut-l24-rec?wait_for_status=yellow&wait_for_no_initializing_shards=true&wait_for_no_relocating_shards=true&timeout=30s",
    "body": null,
    "predict": "状态变更已确认，分片也已完成了吗？",
    "expect": "继续条件：timed_out=false，status=yellow，initializing_shards=0、relocating_shards=0。超时或颜色不符先定位分配原因，不把 acknowledged 当恢复完成。"
  },
  {
    "version": 1,
    "id": "ch24-08-no-peer-row",
    "title": "A13 · 对照恢复记录：无新 PEER 行",
    "method": "GET",
    "path": "/tut-l24-rec/_recovery?filter_path=**.id,**.type,**.stage,**.primary",
    "body": null,
    "predict": "需要恢复的 UNASSIGNED 副本有一行吗？",
    "expect": "单数据节点前提下仍只看到主分片的 EXISTING_STORE/DONE。未实例化的 UNASSIGNED 副本没有 recovery state；多节点可能看到 PEER，不能用一条旧 DONE 行推断整个索引健康。"
  },
  {
    "version": 1,
    "id": "ch24-cat-rec",
    "title": "A14 · 直接查看该索引路由",
    "method": "GET",
    "path": "/_cat/shards/tut-l24-rec?format=json&h=index,shard,prirep,state,node,unassigned.reason",
    "body": null,
    "predict": "Routing state 与 recovery stage 相同吗？",
    "expect": "单节点预期 p=STARTED、r=UNASSIGNED。这是路由状态，另一个 API 的 DONE 是恢复进度；unassigned.reason 记录触发原因，当前能否分配用 explain。"
  },
  {
    "version": 1,
    "id": "ch24-explain-rec",
    "title": "A15 · 明确解释副本 0 当前不能分配",
    "method": "POST",
    "path": "/_cluster/allocation/explain?include_yes_decisions=true",
    "body": {
      "index": "tut-l24-rec",
      "shard": 0,
      "primary": false
    },
    "predict": "节点决定里 same_shard 是什么？",
    "expect": "单数据节点、主已在该节点时，预期 can_allocate=no，节点 same_shard 的 NO。若前提改变按实际决定读；此请求只解释点名副本，不会创建 PEER 恢复记录。"
  },
  {
    "version": 1,
    "id": "ch24-replicas-zero",
    "title": "A16 · 将恢复索引副本还原为 0",
    "method": "PUT",
    "path": "/tut-l24-rec/_settings",
    "body": {
      "index": {
        "number_of_replicas": 0
      }
    },
    "predict": "为什么扩展快照前要还原？",
    "expect": "预期 acknowledged=true。还原为 1P0R；下一等待卡确认 Green，为单节点快照恢复提供可重复前提。"
  },
  {
    "version": 1,
    "id": "ch24-wait-rec-zero",
    "title": "等待 · tut-l24-rec 达到 green",
    "method": "GET",
    "path": "/_cluster/health/tut-l24-rec?wait_for_status=green&wait_for_no_initializing_shards=true&wait_for_no_relocating_shards=true&timeout=30s",
    "body": null,
    "predict": "状态变更已确认，分片也已完成了吗？",
    "expect": "继续条件：timed_out=false，status=green，initializing_shards=0、relocating_shards=0。超时或颜色不符先定位分配原因，不把 acknowledged 当恢复完成。"
  },
  {
    "version": 1,
    "id": "ch24-head-gap",
    "title": "B1 · 检查可见性索引尚不存在",
    "method": "HEAD",
    "path": "/tut-l24-gap",
    "body": null,
    "predict": "复做前清理完成了吗？",
    "expect": "预期 404。若 200，先清理本章资源再开始；否则旧文档、旧 searcher 和额外操作会破坏计数比较。"
  },
  {
    "version": 1,
    "id": "ch24-11-gap-setup",
    "title": "B2 · 建可见性索引：手动 refresh",
    "method": "PUT",
    "path": "/tut-l24-gap",
    "body": {
      "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
        "auto_expand_replicas": "false",
        "refresh_interval": -1,
        "translog.flush_threshold_size": "1gb"
      },
      "mappings": {
        "dynamic": "strict",
        "properties": {
          "marker": {
            "type": "keyword"
          }
        }
      }
    },
    "predict": "关闭自动 refresh 是否也关闭自动 flush？",
    "expect": "预期创建成功。refresh_interval=-1 禁止周期刷新；1gb threshold 降低本小实验因大小触发 flush 的可能，仍不禁止其他 flush。mapping 是 strict+keyword，避免动态映射与分析器干扰。"
  },
  {
    "version": 1,
    "id": "ch24-wait-gap",
    "title": "等待 · tut-l24-gap 达到 green",
    "method": "GET",
    "path": "/_cluster/health/tut-l24-gap?wait_for_status=green&wait_for_no_initializing_shards=true&wait_for_no_relocating_shards=true&timeout=30s",
    "body": null,
    "predict": "状态变更已确认，分片也已完成了吗？",
    "expect": "继续条件：timed_out=false，status=green，initializing_shards=0、relocating_shards=0。超时或颜色不符先定位分配原因，不把 acknowledged 当恢复完成。"
  },
  {
    "version": 1,
    "id": "ch24-12-gap-flush",
    "title": "B4 · flush 建立比较基线",
    "method": "POST",
    "path": "/tut-l24-gap/_flush?wait_if_ongoing=true",
    "body": null,
    "predict": "接下来比较的是搜索视图还是提交计数？",
    "expect": "检查 _shards.failed=0；干净新索引尚无文档。之后只写一条、不做外部 refresh/flush，分别对比实时 GET、SEARCH、translog 统计。此实验不发起 peer 恢复。"
  },
  {
    "version": 1,
    "id": "ch24-13-gap-doc",
    "title": "B5 · 写入一条，保持默认 refresh=false",
    "method": "PUT",
    "path": "/tut-l24-gap/_doc/1",
    "body": {
      "marker": "only_in_translog"
    },
    "predict": "实时 GET 能见到，SEARCH 也会见到吗？",
    "expect": "首次 created；重复写是 updated 并新增操作，应清理重做整个 B 组。当前写入不请求刷新；不把“不显式 flush”描述为“绝不发生任何 commit”。"
  },
  {
    "version": 1,
    "id": "ch24-gap-get",
    "title": "B6 · 实时 GET 读取这条文档",
    "method": "GET",
    "path": "/tut-l24-gap/_doc/1",
    "body": null,
    "predict": "为何 SEARCH 尚不可见时 GET 可以 found？",
    "expect": "预期 found=true、marker=only_in_translog。默认 realtime GET 的内部视图与外部搜索视图不同，不据此推断 safe commit 或未来 phase2 的发送数量。"
  },
  {
    "version": 1,
    "id": "ch24-14-gap-stats",
    "title": "B7 · 记录提交前 translog 统计",
    "method": "GET",
    "path": "/tut-l24-gap/_stats/translog?filter_path=indices.tut-l24-gap.primaries.translog",
    "body": null,
    "predict": "uncommitted_operations 在本地统计里表示什么？",
    "expect": "在无其他写入/flush 的短实验中通常为 1；记录实际值。如果已变为 0，说明有提交等因素，按基线重做。这是本地 translog 相对本地 commit 的计数，不是 peer 所选 safe commit 的历史区间。"
  },
  {
    "version": 1,
    "id": "ch24-15-gap-search0",
    "title": "B8 · 刷新前 SEARCH 比较",
    "method": "GET",
    "path": "/tut-l24-gap/_search?q=marker:only_in_translog&track_total_hits=true&filter_path=hits.total,_shards.failed",
    "body": null,
    "predict": "外部 searcher 包含刚写入的 marker 吗？",
    "expect": "检查 _shards.failed=0，干净起点、禁止周期刷新且无其他 refresh 时，hits.total.value=0、relation=eq。如果读到 1，检查外部操作或是否重复写，不用速度快慢维持实验。"
  },
  {
    "version": 1,
    "id": "ch24-16-gap-refresh",
    "title": "B9 · 手动 refresh 可见性索引",
    "method": "POST",
    "path": "/tut-l24-gap/_refresh",
    "body": null,
    "predict": "refresh 本身是否提交索引或重置检查点？",
    "expect": "检查 _shards.failed=0。refresh 更新搜索可见性；它不等同 flush，也不意味着 local checkpoint 没变化——检查点可随写入处理推进。后两卡分别读搜索与 translog。"
  },
  {
    "version": 1,
    "id": "ch24-17-gap-search1",
    "title": "B10 · 刷新后 SEARCH 比较",
    "method": "GET",
    "path": "/tut-l24-gap/_search?q=marker:only_in_translog&track_total_hits=true&filter_path=hits.total,_shards.failed",
    "body": null,
    "predict": "现在命中数怎样变化？",
    "expect": "预期 _shards.failed=0、hits.total.value=1、relation=eq。证明文档进入外部搜索视图；不证明它已进 safe commit，也不证明该文档今后一定走文件或操作路径。"
  },
  {
    "version": 1,
    "id": "ch24-18-gap-stats2",
    "title": "B11 · 对照刷新后 translog 统计",
    "method": "GET",
    "path": "/tut-l24-gap/_stats/translog?filter_path=indices.tut-l24-gap.primaries.translog",
    "body": null,
    "predict": "和 B7 比较：刷新动作本身会清零未提交计数吗？",
    "expect": "通常仍为 1；若只有 refresh，预期不因其本身清零。但后台 flush 可改变结果，记录实际条件。peer 源端当前从 Lucene 取操作历史，未来发送量还取决于起点、历史与并发写入。"
  },
  {
    "version": 1,
    "id": "ch24-gap-final-flush",
    "title": "B12 · flush 对照提交边界",
    "method": "POST",
    "path": "/tut-l24-gap/_flush?wait_if_ongoing=true",
    "body": null,
    "predict": "这次哪项统计有理由变化？",
    "expect": "检查 _shards.failed=0。没有新写入时下一卡通常 uncommitted_operations=0；不要求 operations=0，也不宣称所有旧 translog 已物理删除。"
  },
  {
    "version": 1,
    "id": "ch24-gap-final-stats",
    "title": "B13 · 读取提交后的统计",
    "method": "GET",
    "path": "/tut-l24-gap/_stats/translog?filter_path=indices.tut-l24-gap.primaries.translog",
    "body": null,
    "predict": "operations 和 uncommitted_operations 必须都等于 0 吗？",
    "expect": "无新写入前提下预期 uncommitted_operations=0。总 operations 可因保留与引用非零；本组只证明 refresh 与 flush 的职责，不能实证 peer 两阶段的准确操作数。"
  },
  {
    "version": 1,
    "id": "ch24-repo-before",
    "title": "C1 · 检查本章仓库名是否干净",
    "method": "GET",
    "path": "/_snapshot/tut-l24-repo",
    "body": null,
    "predict": "404 表示哪一项不存在？",
    "expect": "干净前提预期 repository_missing_exception/404，可能是 expected error。若已有同名仓库，先确认仅本章使用并完成清理；不要覆盖未知配置。默认 Compose 不配置 path.repo。"
  },
  {
    "version": 1,
    "id": "ch24-09-fs-repo-put",
    "title": "C2 · 尝试注册本章 fs 仓库",
    "method": "PUT",
    "path": "/_snapshot/tut-l24-repo",
    "body": {
      "type": "fs",
      "settings": {
        "location": "tut-l24-repo"
      }
    },
    "predict": "相对 location 会落在哪里？默认学习节点为何拒绝？",
    "expect": "默认 path.repo 为空时创建仓库失败，原因含 path.repo setting is empty。配置时相对 location 解析到首个 path.repo；需独立本章目录、相关节点共享与写权限。不同失败阶段可能留下注册元数据，下一卡点名读取；不固定 HTTP 错误码。"
  },
  {
    "version": 1,
    "id": "ch24-10-fs-repo-list",
    "title": "C3 · 点名读取注册结果",
    "method": "GET",
    "path": "/_snapshot/tut-l24-repo",
    "body": null,
    "predict": "失败后一定不存在吗？",
    "expect": "默认 Master 在创建校验阶段失败，且 C1 为 404 时通常仍 404；后续跨节点验证或超时失败可能已登记，应看实际响应。其他仓库与本课无关，不要求整个 _all 返回 {}。"
  },
  {
    "version": 1,
    "id": "ch24-verify-repo",
    "title": "C4 · 已注册成功时，验证仓库",
    "method": "POST",
    "path": "/_snapshot/tut-l24-repo/_verify",
    "body": null,
    "predict": "在哪些节点验证了目录读写？",
    "expect": "只在 C2/C3 成功、仓库为本章独占时执行。核对 nodes 中相关节点的验证结果；失败先处理配置并停下本扩展。默认未配置环境跳过 C4–C14，不为教学演示修改节点配置。"
  },
  {
    "version": 1,
    "id": "ch24-snapshot-one",
    "title": "C5 · 条件扩展：创建第一份快照",
    "method": "PUT",
    "path": "/_snapshot/tut-l24-repo/s1?wait_for_completion=true",
    "body": {
      "indices": "tut-l24-rec",
      "include_global_state": false,
      "partial": false
    },
    "predict": "这是即时发起响应，还是等快照完成？",
    "expect": "必须满足 C4、A17 且停止本章写入。等待后检查 snapshot.state=SUCCESS 与 shards.failed=0；partial=false、include_global_state=false，只包含 tut-l24-rec。同名快照已存在应走清理重做，不覆盖。"
  },
  {
    "version": 1,
    "id": "ch24-snapshot-one-status",
    "title": "C6 · 读取第一份快照的文件统计",
    "method": "GET",
    "path": "/_snapshot/tut-l24-repo/s1/_status",
    "body": null,
    "predict": "total 与 incremental 的区别是什么？",
    "expect": "定位 indices.tut-l24-rec.shards.0.stats，记录 total/incremental.file_count 与 size_in_bytes。第一次对本章空仓库通常需登记全部文件；小文件可内联，增量文件数不等于数据 blob PUT 次数。"
  },
  {
    "version": 1,
    "id": "ch24-snapshot-two",
    "title": "C7 · 不新增文档，再创建第二份快照",
    "method": "PUT",
    "path": "/_snapshot/tut-l24-repo/s2?wait_for_completion=true",
    "body": {
      "indices": "tut-l24-rec",
      "include_global_state": false,
      "partial": false
    },
    "predict": "第二份是否必须重新上传所有文件？",
    "expect": "等 snapshot.state=SUCCESS、shards.failed=0。不写入且文件没变化通常大量复用；后台段合并或提交仍可产生新文件，不承诺 incremental 固定为 0。每份成功快照仍有完整恢复清单。"
  },
  {
    "version": 1,
    "id": "ch24-snapshot-two-status",
    "title": "C8 · 对照第二份快照统计",
    "method": "GET",
    "path": "/_snapshot/tut-l24-repo/s2/_status",
    "body": null,
    "predict": "逻辑完整是否意味着物理文件也全新？",
    "expect": "和 C6 比较 total 与 incremental。total 是该快照完整文件集合，incremental 是新增文件集合；小文件内联和段变化影响数字。文件实际引用的来源并不决定恢复所需的快照链。"
  },
  {
    "version": 1,
    "id": "ch24-delete-first-snapshot",
    "title": "C9 · 删除本章第一份快照",
    "method": "DELETE",
    "path": "/_snapshot/tut-l24-repo/s1",
    "body": null,
    "predict": "会把第二份仍引用的文件一起删掉吗？",
    "expect": "只在 s1/s2 都 SUCCESS 后执行；预期 acknowledged=true。Repository 删除按存活引用处理，不按“谁最先上传”清理。不得手动 rm 仓库文件。下一步仅从 s2 恢复。"
  },
  {
    "version": 1,
    "id": "ch24-restore-head",
    "title": "C10 · 确认恢复目标名不存在",
    "method": "HEAD",
    "path": "/tut-l24-restored",
    "body": null,
    "predict": "恢复会覆盖现有目标吗？",
    "expect": "预期 404。若 200，检查是否为本章旧资源并按清理卡移除；不把重复恢复到已存在索引视为新的独立成功。"
  },
  {
    "version": 1,
    "id": "ch24-restore-two",
    "title": "C11 · 从第二份快照恢复到新索引",
    "method": "POST",
    "path": "/_snapshot/tut-l24-repo/s2/_restore?wait_for_completion=true",
    "body": {
      "indices": "tut-l24-rec",
      "include_global_state": false,
      "include_aliases": false,
      "rename_pattern": "tut-l24-rec",
      "rename_replacement": "tut-l24-restored",
      "index_settings": {
        "index.number_of_replicas": 0,
        "index.auto_expand_replicas": "false"
      }
    },
    "predict": "s1 已删，s2 能否独立恢复？",
    "expect": "普通索引恢复文件到新目标；检查 snapshot.shards.failed=0，之后仍执行等待卡。恢复请求局部覆盖副本数为 0、禁用自动扩副本；此路径不代表 searchable snapshot 挂载。"
  },
  {
    "version": 1,
    "id": "ch24-wait-restored",
    "title": "等待 · tut-l24-restored 达到 green",
    "method": "GET",
    "path": "/_cluster/health/tut-l24-restored?wait_for_status=green&wait_for_no_initializing_shards=true&wait_for_no_relocating_shards=true&timeout=30s",
    "body": null,
    "predict": "状态变更已确认，分片也已完成了吗？",
    "expect": "继续条件：timed_out=false，status=green，initializing_shards=0、relocating_shards=0。超时或颜色不符先定位分配原因，不把 acknowledged 当恢复完成。"
  },
  {
    "version": 1,
    "id": "ch24-restored-get",
    "title": "C13 · 读取恢复的数据",
    "method": "GET",
    "path": "/tut-l24-restored/_doc/1",
    "body": null,
    "predict": "删除 s1 后，marker 仍能恢复吗？",
    "expect": "按 A5 数据前提预期 found=true、marker=recovery_files。该响应才是数据对照；快照清单完整不等于本轮已真实验证，本云端不能运行 ES，API 状态另记。"
  },
  {
    "version": 1,
    "id": "ch24-restored-recovery",
    "title": "C14 · 查看恢复来源",
    "method": "GET",
    "path": "/tut-l24-restored/_recovery?detailed=true&human=true",
    "body": null,
    "predict": "恢复主分片的 type 与 stage 是什么？",
    "expect": "成功等待后普通主分片预期 SNAPSHOT/DONE，source 含 repository/snapshot。若显式增加副本且有合格节点，其副本通常走 PEER；本扩展保持 1P0R。文件数按实际记录。"
  },
  {
    "version": 1,
    "id": "ch24-cleanup-s1",
    "title": "清理 1 · 点名删除 s1",
    "method": "DELETE",
    "path": "/_snapshot/tut-l24-repo/s1",
    "body": null,
    "predict": "中途停下时是否也可能留下 s1？",
    "expect": "仅进入成功仓库扩展时执行；本轮已在 C9 删过可返回 snapshot_missing_exception/404。否则检查 acknowledged。不使用快照通配符，不改其他课资源。"
  },
  {
    "version": 1,
    "id": "ch24-cleanup-s2",
    "title": "清理 2 · 点名删除 s2",
    "method": "DELETE",
    "path": "/_snapshot/tut-l24-repo/s2",
    "body": null,
    "predict": "删除本章快照是否删除已恢复的索引？",
    "expect": "仅进入成功仓库扩展时执行；预期 acknowledged 或未创建时的 404。快照与恢复后的索引是不同资源，下一卡点名删除恢复索引。"
  },
  {
    "version": 1,
    "id": "ch24-cleanup-restored",
    "title": "清理 3 · 删除本章恢复目标",
    "method": "DELETE",
    "path": "/tut-l24-restored",
    "body": null,
    "predict": "默认未运行扩展时该索引存在吗？",
    "expect": "存在则 acknowledged=true，未创建则 index_not_found_exception/404。只删 tut-l24-restored；不会删别的索引。"
  },
  {
    "version": 1,
    "id": "ch24-19-cleanup",
    "title": "清理 4 · 删除恢复索引",
    "method": "DELETE",
    "path": "/tut-l24-rec",
    "body": null,
    "predict": "close 状态和副本数影响显式删除吗？",
    "expect": "存在则 acknowledged=true，已清理则 404。保留旧稳定 ID，但此卡只删除点名的 tut-l24-rec；下一卡补全 gap 索引清理。"
  },
  {
    "version": 1,
    "id": "ch24-cleanup-gap",
    "title": "清理 5 · 删除可见性索引",
    "method": "DELETE",
    "path": "/tut-l24-gap",
    "body": null,
    "predict": "两条主实验线的资源都清理了吗？",
    "expect": "存在则 acknowledged=true，未创建/已删除则 404。删除后 B 组才可恢复确定的新索引、旧搜索视图和单写入前提。"
  },
  {
    "version": 1,
    "id": "ch24-cleanup-repo",
    "title": "清理 6 · 注销本章仓库",
    "method": "DELETE",
    "path": "/_snapshot/tut-l24-repo",
    "body": null,
    "predict": "注销仓库会清空仓库目录吗？",
    "expect": "已注册则 acknowledged=true，不存在则 404。注销删除配置，不删除仓库中的快照文件；成功扩展应先点名删除 s1/s2。不要在节点上 rm 共享仓库目录。"
  },
  {
    "version": 1,
    "id": "ch24-clean-head-rec",
    "title": "清理核对 · 恢复索引",
    "method": "HEAD",
    "path": "/tut-l24-rec",
    "body": null,
    "predict": "重做前应返回什么？",
    "expect": "预期 404。三项都为空，点名仓库也为空后，从前提卡和 A1/B1/C1 重做。存在则检查清理响应，不通过覆盖未知资源继续。"
  },
  {
    "version": 1,
    "id": "ch24-clean-head-gap",
    "title": "清理核对 · 可见性索引",
    "method": "HEAD",
    "path": "/tut-l24-gap",
    "body": null,
    "predict": "重做前应返回什么？",
    "expect": "预期 404。三项都为空，点名仓库也为空后，从前提卡和 A1/B1/C1 重做。存在则检查清理响应，不通过覆盖未知资源继续。"
  },
  {
    "version": 1,
    "id": "ch24-clean-head-restored",
    "title": "清理核对 · 恢复目标",
    "method": "HEAD",
    "path": "/tut-l24-restored",
    "body": null,
    "predict": "重做前应返回什么？",
    "expect": "预期 404。三项都为空，点名仓库也为空后，从前提卡和 A1/B1/C1 重做。存在则检查清理响应，不通过覆盖未知资源继续。"
  },
  {
    "version": 1,
    "id": "ch24-clean-repo-check",
    "title": "清理核对 · 本章仓库",
    "method": "GET",
    "path": "/_snapshot/tut-l24-repo",
    "body": null,
    "predict": "注销完成了吗？",
    "expect": "预期 repository_missing_exception/404；这是资源清理核对。真实 API 首次及清理后重做均需在可运行 ES 环境执行，浏览器深链检查不替代这些结果。"
  }
];
  operations.forEach(function(e){window.ESEXPERIMENTS[e.id]=e;});
})();
