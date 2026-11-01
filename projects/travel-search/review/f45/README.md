# F45 真实运行记录

本课[独立任务](../../labs/f45/TASK.md)与[参考实现](../../labs/f45/README.md)使用完全隔离的F45资源，不依赖前课索引/来源数据/消费位置。[构建](build.log)、[Kafka依赖](dependencies.log)、[Java编译](java-compile.log)单列；应用Boot4.0.8/JDK25.0.4.1+1/官方Java与Rest5 Client9.4.8，Kafka客户端4.0.1。ES bundled JVM通过节点身份实读，不能与应用JDK混为一项。

实验锁定ES9.4.0/Lucene10.4.0、PG17.5、Kafka4.0.1、Debezium3.3.1.Final。两个ES master/data/ingest节点、两个业务索引均1主1副/strict/refresh=-1。端口PG15445、Kafka29345、Connect18345、ES20945/20946、观察窗18095，只绑定回环。本机合成资料，ES/Kafka/Connect无认证、明文；秘密由init生成、FileConfigProvider读取，不进入URL或提交。不是生产安全/HA方案。

正式两轮为[run-03](run-03/summary.json)与点名清理后的[run-04](run-04/summary.json)，同一最终实现均通过。[cleanup03](cleanup03/cleanup.json)、[cleanup04](cleanup04/cleanup.json)及[down](down/compose.log)已完成；未完成轮不计通过。每轮35条lab.req显式留档REST（从原始gzip逐条复核），12次留档Java命令；Java内部ES/Bulk、inspect就绪轮询、4次真实观察窗提交及4次独立REST重放另列，不声称覆盖全部网络请求。每个run保留identity/layout、初始8条与变更后10条真实事件、Java输入/结果、完整字段对账、酒店逐晚来源/投影/错误条件与命中、c01/c02/c03、HTTP无损gzip；观察窗另存实际浏览器→Java→ES与逐次独立REST重放。

初始景点n02/4000分、n01/6000分；酒店h03/o31/52000分、h02/o21/60000分。错误拆分nested多命中h01；h04无第二晚库存、h05第二晚缺价，投影排除对应offer。酒店是2027-03-01记录的固定两晚快照，不代表真实实时可订。

同步来源是PG单表业务行+同事务完整outbox。Debezium初始快照8条r；唯一写入者随后追加两条c，固定来源边界暂停新写入，实际核对event_id=1..10。ES写block触发真实两项403、next维持8/end10；解除后原位置重读成功到10。GET先见45元，refresh前搜索仍60元/含n02；显式refresh后新增查询只剩n01/4500分。物理8份包含n02逻辑删除标记，逐字段与同边界SQL相等；原始快照8项noop，next不变、无退价/复活。

旧F07观察窗仍按自身基础契约，输入“江岸”/HZ/200元/3km：初始5条，恢复4条且n01为45元。没有新增无障碍/时长/酒店前端；新增需求严格由本课独立REST/Java核对，不能把旧壳5→4与新DSL2→1混为一项。

预验收限制：首次Connect配置192MiB堆在插件扫描时发生Java heap OOM，恢复前课256MiB/容器640MiB后重启。首次start就绪阶段遇到Connect非JSON启动响应，按启动轮询处理。attempt-01在start未完成时提前run，首个连接失败，无业务初始化；attempt-02完成初始真实CDC后，DSL字面比较发现Java会将term/sort简写规范成长写；改DSL为显式等价长写，点名cleanup后重新完整运行。run-01的作者Python环境缺Playwright；run-02的观察窗Java搜索已正确，但独立REST重放地址遗留旧课索引而404；修正后单独通过观察窗与酒店对照，点名清理，再完成run-03/run-04。页面初验补齐F45目录card类后已读标记正常。样本n03时长在正式两轮前统一为45分钟，与题表相同。这些记录保留，不能当正式通过轮。

未验证：任意崩溃、跨机器HA/网络、长停机与WAL/日志保留耗尽、跨分区事务或分布式协调、全站中文/相关性、在线重建、安全或生产吞吐。ES与Kafka未组成原子事务；通过旧快照重放验证幂等/旧版本保护，不虚称已注入写后崩溃。双节点green不代表两票能失去任意一票；集群数据核对与投票可用性分开。

图解生成、HTTP阅读、实际查看截图、内容自审、最终检查和发布记录见[本课交付验收](../../../../docs/framework-review/20261101-f45-capstone/README.md)。

两轮ES9.4.0/Lucene10.4.0、两个实际节点均使用bundled JVM26.0.1；cluster UUID相同，每索引p/r分别STARTED于不同节点。身份与布局见[轮1identity](run-03/identity.json)/[layout](run-03/layout.json)、[轮2identity](run-04/identity.json)/[layout](run-04/layout.json)。完整[数量与结果核对](../../../../docs/framework-review/20261101-f45-capstone/results.json)由原始文件生成。
