# F42 · 真实链路与补偿验收

[实验入口](../../labs/f42/README.md)和[F42正文](../../../../framework/f42.html)。仅F42隔离资源，真实PG17.5→Debezium3.3.1.Final→Kafka4.0.1→Java→ES9.4.0；Boot4.0.8/JDK25.0.4.1+1/官方客户端9.4.8实际构建实连，ES内置JVM26.0.1另列，[runtime.json](runtime.json)。

正式两轮为[run-03](run-03/summary.json)及点名清理后[run-04](run-04/summary.json)，同一最终逻辑。每轮3案例、15来源事件（3初始r＋8 document c＋4 fence c）、10次留档Java命令、65项协调/观察HTTP（52 ES＋6 Connect＋7 Java）。7个含Bulk命令、15条item（created5/updated6/noop4）另列；只读inspect/events就绪轮询及浏览器请求分别统计，不冒称已逐请求抓取Java客户端内部HTTP。[计数03](run-03/execution-counts.json)、[计数04](run-04/execution-counts.json)。

c01：连接器PAUSED后，DB6500而end=next3，topic lag0不能证明来源到达；恢复后end4/next3。Java条级成功并next4后GET6500/search6000，refresh后search6500。暂停连接器不证明WAL尚未读取；实际Debezium处理时间与Kafka CreateTime不同，只定位Kafka之前的来源读取/内部队列/发布段。[时间03](run-03/timing.json)、[时间04](run-04/timing.json)保留提交客户端区间、事务内source_recorded_at、source.ts_ms/ts_ms、Kafka timestamp/type、received/projected/item/commit、旧新搜索探针。受控暂停、javac启动和浏览器开销包含在时间中，非性能或自然refresh延迟基准。

c02：来源fence H8、next8。故意破坏目标，使开放集合都3但ID不同；audit按完整业务键发现p01旧价字段、p02删除残留、p04缺失。p01同revision/hash的载荷重放noop仍6500，证明存储hash不能代替实际字段核对。来源锁内重新核对当前事实、emit三份更高revision，新fence H12后完整字段/删除/查询无差异。未重置offset或直接补写ES。

c03：stale H13计划之后正常业务改p01/7200/revision5；旧计划SQL失败整体回滚，无新补偿事件、无直接ES写入。正常事件消费后final H15再次无差异；最初快照3项全noop，next15不动。最终p01/v5/7200、p02/v3删除、p03/v1/3000、p04/v2/4500；物理4、开放3、HZ结果2。全部原始事件、四ID及错误/恢复JSON保留每轮目录。

每轮七个稳定点initial、before-refresh、visible、before-corruption、corrupted、repaired、final；同一Java PID贯穿。每点1440/390×浅深=4次真实浏览器提交及4次独立REST重放；两轮共56次浏览器→Java与56次REST，卡片ID/金额与完整观察JSON一致，浏览器无直连ES。每点*-browser.json与screenshots/保留，完整字段另查物理索引，不以卡片替代删除/版本核对。

[额外拒绝](extra-rejections/summary.json)：正式两轮后在真实目标注入p01/revision999及未知p99两个明确合成fixture，ahead_revision/unexpected均拒绝自动补偿；随后只恢复这些fixture并完整对账干净，来源end及next仍15。0新增来源事件，不混入正式65项/15事件。

预验收run-01的排序断言写成价格顺序，F07实际按ID；run-02已完成机制对照但末尾Path对象未转字符串导致汇总失败。修正、点名清理后run-03/04完整通过，部分运行不算正式通过。启动时Connect尚未就绪返回非JSON，等待器新增JSONDecodeError重试；失败日志在[attempts](attempts/README.md)。

最终[cleanup-final](cleanup-final/summary.json)点名清理connector/source offsets、schema/clock/outbox、角色授权、slot/publication、业务topic/group、点名ES索引/alias与本地状态；[down](down/summary.json)只停F42容器/网络，保留具名卷/Connect内部topic/.local秘密。原es-study-secure启动时间与身份未变，端口关闭单列shutdown.json。

前提：单VM/broker、单topic分区、单消费者/本机协调、稳定ID、所有合作写入者同事务锁/clock/完整快照协议。对账最多100份，来源算法和固定期望值人工核对；同算法出错不能自证正确。未测任意断电、HA、跨分区一致边界、保留耗尽、生产扫描/吞吐或自然可见性SLO；未知/超前目标只拒绝，未提供自动修复。[图解、HTTP与实际视觉](../../../../docs/framework-review/20261030-f42-reconcile/README.md)分列。
