# F39 · Java多表关联投影验收

本轮只实施F39与必要目录、前课下一页链接和进度。正文[framework/f39](../../../framework/f39.html)，读者[labs/f39](../../../projects/travel-search/labs/f39/README.md)，真实执行[review/f39](../../../projects/travel-search/review/f39/README.md)。F38仅替换下一课链接，F40及后续课未实施。

- [内容自审](content-review.json)：4668汉字（不含代码）、3案例、26代码块、17折叠/8能力检查、4陷阱；业务问题/投影边界、FULL/旧新归属、当前状态回查、完整Bulk、实际结果/反例/清理边界一致。源码片段由sync-framework-code逐字核对，F38仅换下一课链接。
- [图生成](../../../framework/diagrams/f39/generation.json)：官方D2 v0.9.0/dagre/theme4与201，两源四SVG，fmt/check/validate/导出及SHA-256通过，无手改产物；没有Archify门禁或动画承诺。
- [HTTP阅读](http-review.json)：1920/1440/1024/768/390/320×双主题12组合，880px/左右差≤1/无整页横向溢出；26次真实Clipboard复制、17折叠、锚点/主题持久化/独立已读，16独立SVG视图、file双主题/reduced-motion/键盘通过。JS/HTTP/请求失败和Pages业务请求均0。[附加点击](supplement-review.json)：1440/390/320×双主题，全折叠打开、目录/前后课/课程目录真实点击、12图解展开均通过。
- [视觉审阅](visual-review.json)：实际查看11张联系表覆盖132截图，另查看7原图；浅深/窄屏正文、完整图与真实卡片未发现明显缺陷。窄屏图/代码/表格局部滚动，展开入口可见；联系表覆盖不等于逐字原分辨率核验。
- [两轮执行](../../../projects/travel-search/review/f39/README.md)：Boot4/JDK25构建、独立PG17.5/Kafka4.0.1/Debezium3.3.1.Final/ES9.4.0、pgJDBC42.7.8实连；run-02及清理后的run-03各20事件、17消费者Bulk/20条目、45教学HTTP（35 ES＋3 Connect＋7 Java搜索），其余观察/身份/清理分列。城市共享改名/改价/子新增、before旧p01与after新p02、after-only反例与残留移除、[]/下架/级联删除/重开、完整字段及分区3/8/9均通过。两轮56真实浏览器搜索/56独立REST重放通过。
- [follow附加](../../../projects/travel-search/review/f39/follow/summary.json)：t02往返转移，两条事件各重算[p01,p02]、2 Bulk/4条目，分区offset9/10提交next10/11；最终完整投影恢复，SIGINT后等组无人活动。与两轮分列。[实际REST Bulk](../../../projects/travel-search/review/f39/rest-bulk-replay.json)复用最终p02 NDJSON，条目及完整字段一致。
- [启动期预验收](../../../projects/travel-search/review/f39/run-01/README.md)：作者在start尚未返回时提前调用run，Connect短暂关闭HTTP连接；未建业务资源，不计完整通过。等待start成功后两正式轮通过。
- [停止核对](../../../projects/travel-search/review/f39/shutdown.json)：清理来源offset/connector、SQL/slot/publication/两读取角色、三业务topic/group/本课ES，down移除本课服务网络；三具名卷和.local保留，既有es-study-secure身份/启动时间/healthy不变。
- [最终检查](checks.json)与[交付哈希](delivery-artifacts.json)：站点/片段/语法/图源与产物/两轮计数和实际秘密排除分别记录。图、阅读和截图不能替代真实链路。

内容与实现由根会话写作、自审，没有启动子代理。当前入口无法设置或自行读回逐课提示词保存的gpt-6.1-sol/max及仓库xhigh偏好，不声称已切换；配置限制单列到reasoning.json。

范围为单主库、三topic各单分区、单消费者、稳定表主键，教学阶段暂停其他写入。REPEATABLE READ是每事件的回查视图，不是原事件时间或跨topic事务快照。没有验证任意崩溃/乱序/延迟副本/失败重放/自动重试与DLQ、HA、主键变更/TRUNCATE、在线重建或高扇出性能，不宣称数据库/ES/Kafka原子性或恰好一次；本机明文环境不能替代F35部署安全设计。
