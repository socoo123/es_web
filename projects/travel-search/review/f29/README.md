# F29 · 主副分片、routing与读写路径两轮实测

[正文](../../../../framework/f29.html) / [本机入口](../../labs/f29/README.md) / [构建与运行](runtime.json)。仅本课三节点、两个索引；ES9.4.0/Lucene10.4.0，同Docker VM，2主每主1副，strict/whitespace/refresh=-1。

- [首次身份](setup/identity.json)：首启后移除引导名单、UUID与三个node ID保持；配置与JVM分列。[启动收据](setup/summary.json)的等待不混入教学HTTP。
- [第一轮](round-1/default/summary.json)和[第二轮](round-2/default/summary.json)均先点名清理索引，再执行default/routing/reads。每轮62教学HTTP=21+28+13，其中1次到既有Java接口；Java内部ES请求另计。各阶段events.jsonl逐条保存URL/body/status/response，轮次输出不覆盖。
- 默认_id真实分布：组0=['p04', 'p05']，组1=['p01', 'p02', 'p03', 'p06']。按分片搜索逐份_source比对，再用_search_shards交叉核对；主片docs合计6，含副本12，三个入口与Java均p01/p02。
- HZ→0、FZ→0、SH→1；r01/HZ正确200、跨SH 404、缺值400 routing_missing_exception、同片错FZ仍200且存储_routing=HZ。跨片错误update404/delete404，正确update7000分后可读；故意跨片同_id创建导致两份r01，再点名删SH拷贝、恢复HZ价格6000分。
- 全索引match_all6份/_shards.total2；HZ范围r01/r02/r04/r05/total1，不能替代城市filter。完整query无routing与HZ均r01/r02、SH则0命中；HZ,SH范围合并为2组/6份。
- 两轮分别通过真实_only_nodes/profile把执行节点/shard关联到当时primary=true/false，主副读取均r01/r02、_shards.total1/failed0；不声称正常默认请求必须轮流到主副。[第一轮拷贝证据](round-1/reads/reads-proof.json)、[第二轮拷贝证据](round-2/reads/reads-proof.json)。
- 独立RoutingLab.java每轮13次SDK调用：专用probe完整CRUD、3搜索、跨片/同片/缺值GET；[第一轮](round-1/java/java-proof.json)与[第二轮](round-2/java/java-proof.json)。verify-java每轮5附加HTTP=3搜索独立重放+refresh+全6份_source/routing核对；无probe或重复残留。不抓包底层客户端重试，所以不把SDK调用数称网络报文数。
- Java构建clean package/classpath/依赖树实跑；Maven日志的行尾空白仅在展示文本中清除，原始字节以.raw.gz无损保留，[哈希与处理记录](log-normalization.json)单列；无测试源，不将No tests to run当测试通过。原临时JDK缺jvm.cfg的失败和同版本官方归档SHA校验恢复分别保留，未更改仓库应用依赖或共享前端。
- [真实观察窗](../../../../docs/framework-review/20261028-f29-routing/shell-review.json)：8次Java请求+8次作者REST重放，双主题/1440与390/200与50元；默认索引p01/p02与p02，卡片/原文/DSL一致，浏览器直连ES=0。观察窗没有routing输入，自定义routing由独立Java/REST检验。
- [保护](guards/summary.json)：reset缺显式删除标记，变更前拒绝。[清理](../../../../docs/framework-review/20261028-f29-routing/workspace-state.json)核对全部最终资料与原身份后点名删两个索引、正常停止自启Java、移除本课容器/网络、保留三卷；原安全节点自本课启动后采样至清理的ID/Pid/StartedAt/healthy均相同。

探索与正式轮次分开：attempts保留选路由、routing/reads探查和旧JDK首次失败。没有运行选举/主分片提升/副本全丢失、跨机器、性能/热点基准、扩缩容或权限实验；这些不是本课已验收成果。
