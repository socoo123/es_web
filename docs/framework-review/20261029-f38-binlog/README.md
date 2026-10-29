# F38 · MySQL binlog独立对照验收

本轮只实施F38及必要目录/前课下一页链接/进度同步，未实施F39。正文[framework/f38.html](../../../framework/f38.html)，读者入口[labs/f38](../../../projects/travel-search/labs/f38/README.md)，真实执行[review/f38](../../../projects/travel-search/review/f38/README.md)。

- [内容自审](content-review.json)：4918汉字（不含代码）、3案例、23代码块、19折叠、8能力检查、4陷阱；业务问题/因果/输入/关键Java/实际结果/反例/清理重做一致。F37仅变更下一课链接。
- [图生成](../../../framework/diagrams/f38/generation.json)：官方D2 v0.9.0/dagre/theme4与201，两源四SVG，fmt/check/validate/导出及SHA-256通过，没有手改产物；无Archify门禁、无动画承诺。
- [HTTP阅读](http-review.json)：1920/1440/1024/768/390/320×双主题12组合、880px列/左右差≤1/局部滚动；23真实Clipboard复制、19折叠、锚点/主题持久化/独立已读、16独立SVG视图、file双主题/reduced-motion/键盘通过；JS/HTTP/请求失败与业务请求均0。[补充点击](supplement-review.json)：1440/390/320×双主题，全折叠打开无整页溢出、实际目录/前后课/课程目录点击、12次真实图解展开通过。
- [视觉审阅](visual-review.json)：实际查看10张联系表，覆盖116原截图，另单独查看5张原图；浅深/窄屏正文、完整图和真实卡片无明显缺陷。联系表覆盖不等于逐字原分辨率核验，范围在收据中单列。
- [运行证据](../../../projects/travel-search/review/f38/README.md)：Boot4/JDK25实际clean package/classpath；MySQL8.4.5/Kafka4.0.1/Debezium3.3.1.Final/ES9.4.0两正式轮run-02与清理后的run-03；ROW/FULL/权限、r/c/u/d/tombstone、GET/SEARCH、停机DDL与增删改恢复、空history失败/还原、完整字段与删除均通过。每轮41教学HTTP（26 ES＋10 Connect＋5 Java搜索）和9消费者写入，身份/轮询/清理/浏览器另计；两轮40真实浏览器搜索/40独立REST重放。
- [follow附加](../../../projects/travel-search/review/f38/follow/summary.json)：持续消费者处理1800→1900→1800分，offset11/12提交至13、完整最终投影一致，停止后等待组无活动成员；与两轮11事件分列。
- [预验收](../../../projects/travel-search/review/f38/attempts/README.md)：run-01在快照后因辅助history多行JSON解析停止，已修正并点名清理重做，不列完整通过。
- [停止核对](../../../projects/travel-search/review/f38/shutdown.json)：最终清理本课connector来源offset/connector、SQL库/账户、业务/history topic/group和ES索引，down移除本课服务/网络，三个具名卷与.local保留；既有es-study-secure身份/启动时间不变且healthy。
- [最终检查](checks.json)：站点、片段、Shell/Python语法、git diff、图/源码哈希、两轮计数与实际秘密排除/忽略/模式检查通过；[交付哈希](delivery-artifacts.json)列本轮文本/源码/记录摘要。图生成/HTTP/截图不替代真实链路。

写作与内容自审由根会话完成，没有启动子代理；入口不能设置或读回提示词保存的gpt-6.1-sol/max与仓库xhigh偏好，不声称已切换，见[reasoning.json](reasoning.json)。

范围为单MySQL主节点、单业务分区/单消费者、稳定主键、短时正常worker停启与原日志仍在。没有验证任意崩溃/HA/GTID切换、长停机/binlog清除或过期/满盘、性能、主键变更/TRUNCATE、多表投影、任意乱序、重试/DLQ和在线重建，不宣称跨系统恰好一次。本机学习环境明文/无ES认证，不替代F35部署安全设计。
