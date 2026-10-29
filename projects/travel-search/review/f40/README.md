# F40 · 真实执行记录

本轮只实施F40。正文[framework/f40](../../../../framework/f40.html)，实验入口[labs/f40](../../labs/f40/README.md)，HTTP/图解/视觉记录在[本轮审阅目录](../../../../docs/framework-review/20261029-f40-replay/README.md)。

最终严格错误分类实现的两轮为[run-05](run-05/summary.json)及点名清理后的[run-06](run-06/summary.json)。此前[run-03](run-03/summary.json)/[run-04](run-04/summary.json)另完成同样四案例及真实浏览器两轮。每轮4案例、17个真实来源事件（root15/related2）、21次留档Java处理/复核执行（另有只读轮询）；各53项已记录HTTP（ES41、Connect4、Java搜索8，含身份/观察），26次应用层Bulk尝试/29条item结果及代理请求分列，见[计数审计](execution-audit.json)。run-03/04各8稳定点×1440/390×双主题=32次浏览器提交及32独立REST重放；卡片ID/价格、Java/DSL请求及完整字段逐项核对。

- c01：初始三条r，p01改价6500/v2；Runtime.halt(40)发生在ES成功后、消费提交前，GET已新而root next仍3；重启noop后next4，从头重放不改组位置或字段。
- c02：related offset0的p01/v4先到，root offset4的v3后到noop；完整城市/标签/价格核对。独立naive索引真实重现旧价覆盖与DELETE后旧快照复活；受保护索引保留v5删除标记，旧v4不复活，v6可合法重开；读alias的按ID GET绕过filter已实测，搜索过滤另测。
- c03：真实ES Bulk为200/400/200，next保持7；再次park为noop/400/noop，等待DLQ offset0确认才next10。失败来源为root:0:8，原key/value/error保留；p02在DLQ期间搜索仍0元，审核修复至1000/v3后与三表投影一致，再修复noop。源组位置不改变，原DLQ保留pending原文，修复证据另存。
- c04：条级429由代理暂扣p02、真实转发p01，失败子集第二次仅p02；请求级注入429四次预算耗尽不提交、原位恢复；真实停止ES与原卷恢复；先写真实ES再丢一次响应确认，后续尝试noop。代理记录见每轮fault-proxy.jsonl；注入429不代表真实饱和负载。

最终完整_source为p01/v11/8100分、p02/v4/1200、p03/v2/3200；root/related next各15/2，与各自末端相等；再次drain处理0条。p03在苏州，观察窗不命中，用完整ES/SQL投影另核。[边界补验](boundary/summary.json)以显式合成载荷验证同版本异内容在park策略下仍阻断、不写DLQ，映射数据失败可持久隔离；p04合成失败不创建文档。旧v3修复在现有v4上noop、repair-file拒绝给新来源状态贴旧版本，REST样本指纹与真实v2载荷一致且重放noop；source组位置不变。补验在原DLQ后另加1条明确标注的合成隔离记录，不混入正式17条来源或两轮计数。构建、身份及最终停止记录分别保存，不把浏览器图片当作链路完整性证明。

保留的预验收：run-01在start尚未返回时误提前调用，Connect启动期关闭连接，未建立业务资源；run-02前三机制通过，但旧版故障代理未读取Java的chunked请求，c04未完成，不能算整轮通过。cleanup-02漏撤数据库CONNECT权限导致角色删除被拒绝；修复后cleanup-02-retry与后续清理通过。失败日志与更正保留，不覆盖历史证据。

边界：单VM、broker、topic单分区、单消费者，串行业务写入者共同锁协议/稳定ID/完整不可变outbox；clock与ES删除标记保留期间才有本课保护。未验证任意时刻断电、Kafka/DLQ故障、HA/并行rebalance、吞吐、在线重建、长时保留耗尽及跨集群回放；不宣称跨ES/Kafka恰好一次。本机明文配置不是F35的部署安全配置。

[最终清理](cleanup-final/summary.json)和[停止/端口/保留资源](shutdown.json)通过；F40服务与网络已移除，具名卷/.local保留，既有安全节点ID/启动时间/healthy不变。应用Java与ES镜像内JDK分别实际读取，见[runtime](runtime.json)。
