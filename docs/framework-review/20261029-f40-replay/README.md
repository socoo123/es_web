# F40 · 重放、乱序、删除保护与失败位置

本轮只交付[F40正文](../../../framework/f40.html)、独立实验增量及必要的目录/前课导航/进度。F39仅替换下一课链接，F41及后续课未实施。

- [两轮真实执行](../../../projects/travel-search/review/f40/README.md)：最终严格分类run-05与清理后的run-06各4案例、17来源事件、21次留档Java执行（只读轮询另列）、53项HTTP实录；前序run-03/04另各32次浏览器提交/32独立REST重放。26次应用层Bulk尝试/29条item结果另有计数审计。版本、完整字段、失败位置、DLQ与恢复证据保留。预验收失败原因单列，不算通过轮。
- [图生成](../../../framework/diagrams/f40/generation.json)：官方D2 v0.9.0，dagre/themes4与201，两源四SVG，保留fmt/check/validate/实际导出与SHA-256。静态图，无Archify门禁或动画承诺。
- [HTTP阅读](http-review.json)：`/es_web/`前缀、1920/1440/1024/768/390/320×双主题12组合，列宽≤880/左右差≤1/无整页横向溢出；23次真实Clipboard复制、13折叠、锚点/主题持久化/独立进度、16独立SVG视图、file双主题/reduced-motion/焦点通过。JS/HTTP/请求失败和Pages业务请求均0。[附加点击](supplement-review.json)在1440/390/320×双主题验证目录/前后课/课程入口/12次图解展开与全折叠打开。
- [视觉审阅](visual-review.json)：实际查看13张联系表覆盖152截图，并查看8张原图；正文、完整图、窄屏局部滚动/展开与真实卡片可读。联系表覆盖不等于逐字或逐像素核验。
- [边界补验](../../../projects/travel-search/review/f40/boundary/summary.json)：已应用同版本异载荷的脚本400在park下仍停止，真实映射400可隔离；显式合成fixture与原来源分列。旧修复noop/新来源版本拒绝/REST原始指纹与真实载荷一致，未改变源组位置。
- [内容自审](content-review.json)：5574汉字（不含代码）、23代码块/8理解题/4陷阱，源片段逐字同步；[固定版本源码](source-evidence.json)3文件HTTP200与本地字节相同。[片段/站点/语法与实际秘密排除](checks.json)、[推理配置限制](reasoning.json)和[交付哈希](delivery-artifacts.json)各自记录。浏览器与图生成不能代替实际ES/Java/Kafka/PG执行。

[最终停止记录](../../../projects/travel-search/review/f40/shutdown.json)：点名清理本课SQL/connector/offset/topic/DLQ/group/两索引及alias，移除F40服务/网络、关闭六个回环端口；三具名卷与.local保留，既有es-study-secure身份/启动时间/healthy不变。

内容与实现由根会话写作、自审，没有启动子代理。当前运行入口无法设置或自行读回逐课提示词保存的gpt-6.1-sol/max，以及仓库的xhigh偏好；不声称已经切换。此限制与实际执行结果分开记录。

已验证方案有明确来源协议：共同串行写锁、业务变化/clock/完整outbox同事务，删除后clock保留，所有ES投影写入经过版本守卫；不是对任意既有业务写入者透明生效。限制与两轮记录一致。
