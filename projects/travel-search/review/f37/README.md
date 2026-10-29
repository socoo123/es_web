# F37 · 真实执行记录

F37只实现PostgreSQL单表→Debezium→Kafka→Java→ES。正式固定制品、构建与源文件hash见[runtime.json](runtime.json)。本机教学步骤见[实验入口](../../labs/f37/README.md)，阅读/图解验收见[独立记录](../../../../docs/framework-review/20261029-f37-wal/README.md)。

正式轮次使用PG bigint→ES long的最终mapping。初次运行与点名清理后的重做分开保留，结论以每份summary.json的passed字段为准：

| 记录 | 作用 |
| --- | --- |
| [init](init/summary.json)、[setup-verified](setup-verified/summary.json) | 初始化随机凭据、启动并核对运行身份 |
| [run-02](run-02/summary.json) | 最终配置第一轮三案例，附既有观察窗的真实浏览器记录 |
| [cleanup-02](cleanup-02/summary.json) | 按名清除来源位置、connector/slot/topic/group/表和ES，保留原卷 |
| [run-03](run-03/summary.json) | 同一最终配置重做三案例，附真实观察窗 |

每轮38教学HTTP入口：26 ES REST＋7 Connect REST＋5 Java搜索；9次消费者官方index/delete另计。另有身份/guard五条和状态轮询；作者浏览器每轮五阶段×四视图，共20次Java搜索＋20次REST重放，单列于*-browser.json，不混入主路径。summary记录主路径，http.jsonl含原始请求/响应，sql.jsonl含SQL与权限/标识反例，c*-events.json含完整Kafka记录，c*-apply.json含每条写入/commit及累计next，c*-positions.json含PG/Connect/group三层位置。实际密码不在记录中。

三个案例分别证明：r快照两条→Java写入→GET新/SEARCH未刷→显式refresh；c/u/u新增/改价/下架与d+tombstone物理删除；保留原slot和Kafka状态停止整个worker、停机继续更新、WAL位置距离增长、恢复后继续u/c/d+tombstone、Kafka已新/ES仍旧、同组消费与refresh后完整投影一致。最终p01=7000分、p04=1800分，p02/p03不存在，next/end=11，再次drain为0。replica identity反例在一次性事务内失败后回滚，不永久改变表配置。

[run-01](run-01/summary.json)是完整链路预验收，当时ES金额仍为integer，后改为与PG bigint对齐的long；不把它作为最终配置的两轮之一。其额外[标识反例](replica-identity-01/replica-identity.json)也单列。初次Kafka192MiB堆发生LogCleaner OOM、plugin.path缩到单个插件目录未发现connector、环境变量前缀/启动HTML错误页解析修正见[attempts](attempts/README.md)。setup与setup-final是未完成启动证据，无通过声明。cleanup-01第一次在DROP ROLE时因残留数据库CONNECT授权失败，修复后[cleanup-01-fixed](cleanup-01-fixed/summary.json)完成；最终cleanup先撤销该授权。

[follow附加实测](follow/summary.json)在持续消费者不重启时完成p04价格1800→1900→1800，两条新u事件offset11/12成功写入并commit到13；SIGINT后等组不活动再清理。与两正式轮分开计数。[最终清理](cleanup-final/summary.json)与[停止](down/summary.json)保留具名卷和本机秘密文件。

本课只证明单PG主节点、单Kafka分区与单消费者的受控正常停启，未做PG/Kafka崩溃、HA、slot失效/满盘、长期保留、随机重复乱序、DLQ、多表投影或持续重建；不宣称恰好一次。delete.before非主键字段出现零/空串占位，消费者仅按业务键处理删除。Pages、图生成、视觉检查不能替代这些实际运行证据。
