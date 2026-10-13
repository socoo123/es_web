/* ch23 · ES9.4.0：分配、目标与搬迁；多节点动画为概念示意，API请求仅操作本课索引。 */
(function () {
  'use strict';
  function esc(s) { return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
  function text(x,y,s,c) { return '<text x="'+x+'" y="'+y+'" text-anchor="middle" class="'+c+'">'+esc(s)+'</text>'; }
  function box(x,y,w,h,hot) { return '<rect x="'+x+'" y="'+y+'" width="'+w+'" height="'+h+'" rx="9" class="'+(hot?'fig-box-hot':'fig-box')+'"/>'; }
  function snapshot(n,nodes,lines,title,note) {
    var id='ch23-step-'+n;
    var s='<svg viewBox="0 0 760 360" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="'+esc(title)+'"><defs><marker id="'+id+'" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M 0 0 L 10 5 L 0 10 z" class="fig-arrowhead"/></marker></defs>';
    nodes.forEach(function(a,i) { var x=15+i*255;s+=box(x,15,220,88,a[2])+text(x+110,39,'Node-'+['A','B','C'][i],'fig-name')+text(x+110,64,a[0],'fig-key')+text(x+110,88,a[1],'fig-sub'); });
    if(n===3) s+='<line x1="235" y1="68" x2="268" y2="68" class="fig-arrow" marker-end="url(#'+id+')"/>'+text(380,130,'实线 A → B：本例 replica 向 active primary 恢复','fig-sub');
    if(n===6) {
      s+='<line x1="490" y1="68" x2="521" y2="68" class="fig-arrow" style="stroke-dasharray:5 4" marker-end="url(#'+id+')"/>';
      s+='<path d="M 125 103 V 116 H 635 V 103" fill="none" class="fig-arrow" marker-end="url(#'+id+')"/>';
      s+=text(380,136,'虚线 B → C：搬迁配对；实线 A → C：本例恢复数据','fig-sub');
    }
    s+=box(15,147,730,128,false);lines.forEach(function(l,i) {s+=text(380,168+i*25,l,i===0?'fig-key':'fig-sub');});
    s+=box(15,312,730,43,true)+text(380,331,title,'fig-name')+text(380,348,note,'fig-sub');return s+'</svg>';
  }
  window.ESFLOWS=window.ESFLOWS||{};
  window.ESFLOWS['ch23-balance']={version:1,id:'ch23-balance',title:'七步概念示意：副本分配、目标规划与一次搬迁',speed:2600,steps:[
    {svg:snapshot(1,[['idx1 P0 STARTED','已有主分片',true],['尚未加入','没有第二个候选'],['尚未加入','没有第三个候选']],['idx1 设1主1副；仅一个合格数据节点 A','R0 未分配；same_shard 对已有 P0 的 A 给 NO','这是一个充分阻碍，不证明只有它投 NO','本索引 Yellow 不等于所有请求都能成功'],'起点：副本不能与同号主分片放同一节点','固定前提的概念动画，不是本轮多节点运行录像'),note:'设 idx1 为1主1副，P0在唯一合格数据节点A上active，R0未分配。same_shard的NO足以阻止叠放，但其他decider也可能给NO。本索引Yellow只说明副本冗余未就绪，不承诺写入不受其他块或条件影响。'},
    {svg:snapshot(2,[['idx1 P0 STARTED','已持有同号副本',true],['加入集群','新的可能目标'],['尚未加入','无候选']],['B 加入会带来新分配输入，不等于立刻恢复完','后台 Balanced 规划；Master 可先执行现有目标','假设 B 的磁盘、过滤、角色等条件允许','NO 不能落位；THROTTLE 本轮暂缓，不是立即分配'],'多了可能目标，但仍需实际约束通过','NOT_PREFERRED 在不同动作中的准入条件不同'),note:'B加入使候选条件改变；默认desired_balance后台算目标，同时本轮可先按现有目标reconcile。本例假设B角色、磁盘、过滤等允许且最终解除节流。规划目标不是已完成落位，THROTTLE不会让本轮立即开始。'},
    {svg:snapshot(3,[['idx1 P0 STARTED','active primary',true],['idx1 R0 INITIALIZING','本例向 A 恢复',true],['尚未加入','无分片']],['Master 通过当前检查，初始化 B 上的 R0','路由 INITIALIZING 不等于复制数据已经完成','数据节点进行 peer recovery；primary 须 active','默认 incoming/outgoing 各2；初始本地主分片另有4'],'R0 正在恢复，尚未成为活跃副本','本例 A → B 是数据路径；规划箭头不是数据复制'),note:'获准后先产生INITIALIZING路由，再由数据节点恢复。replica从active primary所在节点A获取数据，不从“目标模型”复制。incoming/outgoing recovery默认各2，初始本地主分片另有4，不能概括为任意节点所有恢复总共只有2。'},
    {svg:snapshot(4,[['idx1 P0 STARTED','主分片活跃',true],['idx1 R0 STARTED','副本恢复完成',true],['尚未加入','无分片']],['恢复完成、启动上报与路由更新后，R0 STARTED','满足本例前提时 idx1 可以转 Green','两个 node 不自动等于两个独立物理故障域','带其他索引或写入块的全群状态需另行判断'],'本索引 Green：所有所需副本 active','不把健康颜色当作可写、性能或零数据丢失保证'),note:'R0恢复并进入STARTED，本例索引全体所需副本active，颜色可转Green。A/B可能同宿主机，因此不能自动叫两个独立物理故障域；master可用、写入块及其他请求条件也不能由Green推出。'},
    {svg:snapshot(5,[['idx1 P0 + idx2 P0','本例均已 STARTED',true],['idx1 R0 + idx2 R0','本例均已 STARTED',true],['尚未加入','无分片']],['再放一个1主1副索引 idx2，图中是可能的布局','same_shard 保证同号两份不叠在同一节点','index 因子看同索引分片数，不强制主角色平均','权重还含总片数、预测写入负载与磁盘字节差'],'A/B 各2片是本例，不是算法唯一答案','不能从0.55推导每个新 primary 必落不同节点'),note:'idx2形成1主1副；图中选择A放主、B放副只是一个可行示意，角色没有强制平均。index因子看同索引分片数，权重还考虑预测写负载和磁盘字节差；相同条件也可能有其他平局结果。'},
    {svg:snapshot(6,[['idx1 P0 STARTED','idx2 P0 STARTED',true],['idx1 R0 RELOCATING','idx2 R0 STARTED'],['idx1 R0 INITIALIZING','新目标仍恢复中',true]],['假设新目标建议 R0 从 B 搬到 C，当前约束允许','源 B：RELOCATING 且 active；目标 C：INITIALIZING','本例 replica 目标向 active primary A 恢复','B → C 表示路由搬迁关系，不表示数据一定来自 B'],'搬迁同时存在源与目标路由','C加入不保证触发这次搬迁，也不保证固定完成时间'),note:'C加入后，假设规划和实际动作检查允许这次R0搬迁。B的源路由是RELOCATING但仍active，C目标是INITIALIZING；本例目标从active primary A恢复。虚线是B/C配对，实线才是A/C数据路径，不承诺一定选这一片。'},
    {svg:snapshot(7,[['idx1 P0 + idx2 P0','2片 · 示意',true],['idx2 R0 STARTED','1片 · 示意'],['idx1 R0 STARTED','1片 · 示意',true]],['目标 C 启动后移除 B 的源路由，得到本例2/1/1','若目标失败且源仍在，可取消源搬迁、删除目标','threshold=1.0 是模型改进门槛，不是片数差公式','水位还受headroom/估计大小影响，不能仅看86/91/95'],'一次可能的终态，不是永久唯一目标','NO可随条件变化；完成搬迁也不证明所有分配已收敛'),note:'目标C进入STARTED后，B的搬迁源路由被移除，本例形成2/1/1。若初始化目标失败且源仍存在，可取消源搬迁并删除目标。布局、门槛与水位都带条件，不承诺片数绝对平均或固定恢复时间。'}
  ]};
  window.ESEXPERIMENTS=window.ESEXPERIMENTS||{};
  function add(id,title,method,path,body,predict,expect) {window.ESEXPERIMENTS[id]={version:1,id:id,title:title,method:method,path:path,body:body,predict:predict,expect:expect};}
  var yellow={index:'tut-l23-yellow',shard:0,primary:false};
  var filtered={index:'tut-l23-filter',shard:0,primary:true};
  var healthFields='&filter_path=status,timed_out,number_of_nodes,number_of_data_nodes,active_primary_shards,active_shards,unassigned_shards';
  var settled='&wait_for_no_initializing_shards=true&wait_for_no_relocating_shards=true&timeout=30s';
  add('ch23-11-version','A1 · 确认固定版本','GET','/?filter_path=version.number,version.build_hash,version.lucene_version',null,'是否为对应的ES9.4.0/Lucene10.4.0？','应为9.4.0、固定build 2e8528e92361c3399724226deaf2b46f933e925b、Lucene10.4.0；版本不同时不能直接套本课源码结论。');
  add('ch23-12-nodes','A2 · 检查单节点实验前提','GET','/_nodes?filter_path=_nodes.total,_nodes.failed,nodes.*.name,nodes.*.roles',null,'是否只有一个合格数据节点？名字是否与C组虚构名不同？','A组颜色和same_shard预期限定一个合格数据节点及active primary；多节点时副本可能就绪，勿硬套Yellow。确认没有节点名__ch23_no_matching_node__，C组才使用它制造明确过滤。');
  add('ch23-13-yellow-empty','A3 · 确认本课索引空前提','HEAD','/tut-l23-yellow',null,'第一次或清理后应是什么状态？','404且无响应体是预期前提；200表示已有资源。需要重做时先执行末尾点名清理，再从A3开始；删除会清掉此索引全部数据。');
  add('ch23-00-setup','A4 · 明确建1主1副的普通索引','PUT','/tut-l23-yellow?wait_for_active_shards=1',{settings:{number_of_shards:1,number_of_replicas:1,auto_expand_replicas:false,refresh_interval:'1s'},mappings:{dynamic:'strict',properties:{marker:{type:'keyword'}}}},'单数据节点能满足主分片等待，却满足不了副本冗余吗？','首次正常创建后，以A6等待为准再观察；request确认不等于副本全active。重复创建通常400 resource_already_exists_exception，不覆盖原索引；清理后再做。不预设version恰好+1。');
  add('ch23-01-cat-shards','A5 · 看本索引两条路由','GET','/_cat/shards/tut-l23-yellow?v&h=index,shard,prirep,state,unassigned.reason,node',null,'p/r各一行，现在已经稳定了吗？','在A6就绪前可短暂见INITIALIZING；稳定单数据节点通常p STARTED、r UNASSIGNED。第一次创建可见INDEX_CREATED；重加副本后的原因可不同，不能把原因枚举当成永久诊断结论。');
  add('ch23-02-health','A6 · 等主分片就绪，限定索引','GET','/_cluster/health/tut-l23-yellow?wait_for_status=yellow'+settled+healthFields,null,'单数据节点且无其他阻碍时，应是哪种本索引颜色？','预期timed_out=false、yellow、active_primary_shards=1、active_shards=1、unassigned_shards=1。若其他条件阻碍主分配、超时或多节点副本已就绪，先核对前提。wait_for_status=yellow也接受更好的green，须读实际status。');
  add('ch23-03-explain','A7 · 指定R0，读same_shard的NO','POST','/_cluster/allocation/explain',yellow,'哪个node已经持有同号主分片？是否还有别的NO？','本例R0 unassigned/can_allocate=no；合格唯一节点的same_shard应NO，说明已有同号副本。可能还出现磁盘、过滤、角色等NO，不写死只有一票；数组路径node_allocation_decisions[].deciders[]，不要固定第0个节点。');
  add('ch23-04-explain-yes','A8 · 对照显示更多决定','POST','/_cluster/allocation/explain?include_yes_decisions=true',yellow,'显示YES是否改变分配许可？','same_shard仍NO；通常显示更多具体YES，但ALWAYS哨兵仍不进数组，不承诺出现每个注册decider。该参数仅改变解释可见性，不修改配置、强制分配或启动搬迁。');
  add('ch23-07-replicas-0','A9 · 本索引副本数改为0','PUT','/tut-l23-yellow/_settings',{index:{number_of_replicas:0}},'取消副本需求后要不要等路由更新？','正常acknowledged=true，副本路由需求移除；下一卡局部等待green。元数据/路由更新可多次，重复设置同值也可能无变化，不保证每次API都使version+1。');
  add('ch23-08-green','A10 · 仅验证本索引Green','GET','/_cluster/health/tut-l23-yellow?wait_for_status=green'+settled+healthFields,null,'取消需求与恢复了第二份数据，是同一件事吗？','本例timed_out=false、green、active_shards=1、unassigned_shards=0。这是不再要求副本，未新增冗余；其他索引不改变本索引颜色，Green也不保证一定可写。');
  add('ch23-09-replicas-back','A11 · 恢复副本需求','PUT','/tut-l23-yellow/_settings',{index:{number_of_replicas:1}},'恢复1副本会立刻有第二份数据吗？','正常acknowledged=true，单合格数据节点仍无第二个落点。先等待下一卡，再解释R0；新副本原因可能REPLICA_ADDED，而不是第一次创建的INDEX_CREATED。');
  add('ch23-14-yellow-again','A12 · 等待恢复需求后的局部状态','GET','/_cluster/health/tut-l23-yellow?wait_for_status=yellow'+settled+healthFields,null,'是否重新看到一个未分配副本？','本例yellow、active_primary_shards=1、active_shards=1、unassigned_shards=1，timed_out=false；若多节点或配置变化须按实际判断。此等待消除“点得快才看见”的竞态。');
  add('ch23-15-explain-again','A13 · 对照恢复需求后的R0','POST','/_cluster/allocation/explain',yellow,'原因枚举改变后，same_shard规则改变了吗？','本例仍有same_shard NO；比较unassigned_info.reason和当前deciders，两者分别描述进入未分配的原因与现在不能落位的条件。不能从INDEX_CREATED或REPLICA_ADDED直接推断唯一NO。');
  add('ch23-05-defaults','B1 · 读取分配器、水位和覆盖值','GET','/_cluster/settings?include_defaults=true&filter_path=defaults.cluster.routing.allocation,persistent.cluster.routing.allocation,transient.cluster.routing.allocation',null,'默认模型与水位是什么？有显式覆盖吗？','源码默认desired_balance；balance为.45/.55/10/2e-11、threshold1；普通水位85/90/95%，未显式改各水位时headroom200/150/100GB。persistent/transient及节点设置可覆盖；小系数乘字节不能理解成磁盘只微调。');
  add('ch23-06-cat-allocation','B2 · 区分显示统计与策略输入','GET','/_cat/allocation?v&bytes=b&h=shards,disk.indices,disk.used,disk.avail,disk.total,disk.percent,node',null,'当前磁盘一定低于85%吗？表格是decider的完整输入吗？','磁盘和总片数由环境及所有索引决定，不写死低于85%。CAT统计、分配使用的ClusterInfo快照、搬迁空间预留和预计分片大小不同；disk.percent也不能单独复现每次disk_threshold结论。');
  add('ch23-16-disk-info','B3 · 指定R0并请求磁盘解释信息','POST','/_cluster/allocation/explain?include_disk_info=true&include_yes_decisions=true',yellow,'是否能看到ClusterInfo与disk_threshold说明？','若已收集磁盘信息可见相关cluster_info；可缺省、滞后或因尚无信息给YES，不能把YES都读成磁盘肯定充足。结合设置、headroom和预计大小解释；不是灌盘/高水位/性能实测。');
  add('ch23-17-filter-empty','C1 · 另一个专属索引空前提','HEAD','/tut-l23-filter',null,'为何不在A组索引上混入过滤和块？','404、无响应体为前提；与A组分离，避免另一个NO污染单副本对照。若已有资源，末尾点名清理再从C1做；不会改集群过滤设置。');
  add('ch23-18-filter-create','C2 · 创建一个明确匹配不到节点的过滤','PUT','/tut-l23-filter?wait_for_active_shards=0',{settings:{number_of_shards:1,number_of_replicas:0,auto_expand_replicas:false,refresh_interval:'1s','index.routing.allocation.require._name':'__ch23_no_matching_node__'},mappings:{dynamic:'strict',properties:{marker:{type:'keyword'}}}},'虚构名无节点匹配，0副本还会Green吗？','前提A2确认无同名节点。wait_for_active_shards=0避免等待故意未分配的primary；request确认不证明primary active。下一卡指定P0应见filter NO；重复创建通常400，先清理重做。');
  add('ch23-19-filter-explain','C3 · 指定未分配的P0','POST','/_cluster/allocation/explain?include_yes_decisions=true',filtered,'本次0副本的主要分配阻碍是什么？','P0应unassigned，候选不匹配require._name时filter给NO；可能有其他阻碍，不能只数一个decider。主分片未active对应本索引Red，说明Red/Yellow要结合具体路由，不都是same_shard。');
  add('ch23-20-filter-settings','C4 · 读回索引过滤配置','GET','/tut-l23-filter/_settings?filter_path=*.settings.index.routing.allocation,*.settings.index.number_of_shards,*.settings.index.number_of_replicas,*.settings.index.auto_expand_replicas',null,'配置是否真的只写在本索引？','require._name应是本课虚构名，1主0副且auto_expand=false。值通常序列化为字符串；此次请求不修改cluster.routing.allocation的全局规则。');
  add('ch23-21-filter-clear','C5 · 移除本索引require条件','PUT','/tut-l23-filter/_settings',{'index.routing.allocation.require._name':null},'NO会永久保持，还是条件变化后重评？','正常acknowledged=true，移除此索引的require._name；其他条件允许时可分配primary。NO不是“只能人工永远修复”的永久票；本次改变条件后仍等下一卡局部就绪。');
  add('ch23-22-filter-ready','C6 · 等过滤移除后的局部Green','GET','/_cluster/health/tut-l23-filter?wait_for_status=green'+settled+healthFields,null,'还在初始化时可继续写入吗？','本例timed_out=false、green、active_primary_shards=1、active_shards=1、unassigned_shards=0。没有满足就绪条件时先停在这里检查剩余NO/磁盘/角色/总开关，不靠操作快慢。');
  add('ch23-23-doc-before','C7 · 先写一个确定存在的文档','PUT','/tut-l23-filter/_doc/1?refresh=wait_for',{marker:'before'},'随后文档删除失败能否排除“本来就不存在”？','首次正常201 created；固定ID重复执行可200 updated。显式refresh等待及原始响应建立文档存在基线。这里不需要bulk或自动ID，重复运行不会累加新文档。');
  add('ch23-24-write-block','C8 · 设置可恢复的普通写入块','PUT','/tut-l23-filter/_settings',{'index.blocks.write':true},'这会改变分片健康颜色，还是阻挡写请求？','正常acknowledged=true。是普通index.blocks.write，不是flood-stage的read_only_allow_delete；没有填满磁盘或触发Monitor。普通写块不会由磁盘恢复自动清除，本组末尾显式还原。');
  add('ch23-25-green-blocked','C9 · Green不等于可写','GET','/_cluster/health/tut-l23-filter?wait_for_status=green'+settled+healthFields,null,'所有分片active时，写块会把颜色改为Yellow吗？','本索引通常仍green且1 active primary，块本身没有制造未分配副本。健康颜色与写请求准入分开，下一卡观察403；这是普通写块对照，不冒充真实磁盘故障。');
  add('ch23-26-write-rejected','C10 · 预期普通写块拒绝写入','PUT','/tut-l23-filter/_doc/1',{marker:'blocked'},'这条预期错误会把marker更新成blocked吗？','在C8写块保持时，单文档请求预期403 cluster_block_exception，理由index write (api)。不要把它写成flood-stage错误；9.4源码的flood块使用429。恢复写块后再重试。');
  add('ch23-27-delete-rejected','C11 · 文档删除也是写请求','DELETE','/tut-l23-filter/_doc/1',null,'删除已有文档是不是也受WRITE级块限制？','普通写块保持时预期403 cluster_block_exception；不是404证明文档不存在。删除整个索引与删除文档是不同操作。本卡不把普通写块伪装成flood块；后卡显式恢复再确认更新。');
  add('ch23-28-write-restore','C12 · 移除本索引普通写块','PUT','/tut-l23-filter/_settings',{'index.blocks.write':null},'何时恢复，才能安全继续本组对照？','正常acknowledged=true，移除刚设置的本索引普通写块。之后才能重试C10；不修改全局磁盘阈值、其他索引或read_only_allow_delete设置。');
  add('ch23-29-doc-after','C13 · 恢复后更新同一个文档','PUT','/tut-l23-filter/_doc/1?refresh=wait_for',{marker:'after'},'基线文档仍存在时应created还是updated？','前序按顺序完成且文档仍在，正常200 updated；403表示还有块，201表示原文档/索引前提已改变。依据实际响应判断，不声称本轮已API验证。');
  add('ch23-10-cleanup','清理1 · 点名删除Yellow实验索引','DELETE','/tut-l23-yellow',null,'删除范围和重复语义是什么？','删除tut-l23-yellow全部文档与映射；正常acknowledged=true，重复删除通常404 index_not_found_exception。完整重做从A3开始；保留稳定清理ID。');
  add('ch23-30-filter-cleanup','清理2 · 点名删除Filter实验索引','DELETE','/tut-l23-filter',null,'是否已执行C12恢复，是否仅删本课资源？','删除tut-l23-filter全部文档与映射；正常acknowledged=true，重复删除通常404。两个索引不使用通配符，不清其他索引或修改cluster配置。');
  add('ch23-31-yellow-missing','清理3 · 确认Yellow索引不存在','HEAD','/tut-l23-yellow',null,'是否回到A3前提？','404、无响应体；再做A3–A13。节点名、时间、状态版本及磁盘统计无需与前轮完全一样，分配条件和路由语义才是重复目标。');
  add('ch23-32-filter-missing','清理4 · 确认Filter索引不存在','HEAD','/tut-l23-filter',null,'是否回到C1前提？','404、无响应体；再做C1–C13后清理。全流程只改两本课索引；多节点搬迁和真实磁盘水位未由这些单节点操作证明。');
})();
