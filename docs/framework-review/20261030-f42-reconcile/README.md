# F42 · 延迟、对账与补偿验收

本轮只实施[F42](../../../framework/f42.html)及必要目录/F41下一页/当前进度摘要；逐课提示词转F43，未实施F43及后续课。[实验入口](../../../projects/travel-search/labs/f42/README.md)与[真实链路记录](../../../projects/travel-search/review/f42/README.md)分列。

正文约4680汉字（不含代码），七段式/880px/双主题/独立已读，3目标/3案例、23代码块、10折叠（8能力检查）、4陷阱、2静态D2/0播放器。先讲旧价各层证据与时间定义，再解释同一边界的完整对账、来源补偿与过时计划拒绝。关键SQL、Java完整投影/守卫/Bulk/提交及Python对账/修复错误分支与工程片段一致；通用配置折叠。内容为作者自审，无独立代理，见[content-review.json](content-review.json)。

真实PG→Debezium→Kafka→Java→ES三案例两轮在[run-03](../../../projects/travel-search/review/f42/run-03/summary.json)和[清理后run-04](../../../projects/travel-search/review/f42/run-04/summary.json)完整通过。每轮15来源事件、65项协调/观察HTTP、10次Java命令；15项Bulk结果另列。7稳定点×1440/390×双主题，两轮共56浏览器提交及56独立REST重放。同一PID、完整字段/删除、拒绝与恢复分别核对，不用图或截图替代数据断言。最终游船72元、夜游45元、next15；额外未知ID/超前目标拒绝及恢复单列0来源事件。

[HTTP阅读](http-review.json)：Playwright1.64.1/Chromium156.0.8078.4，1920/1440/1024/768/390/320×双主题12组合，桌面列880px/边界差≤1/无整页横溢；代码、表格与D2局部滚动。23次真实Clipboard复制、10折叠开合、27锚点、主题/图源切换重载、F42进度与F41隔离、11本地链接200、file双主题/reduced-motion/键盘焦点通过。2图×4桌面宽×浅深共16独立图视图；目录/F41导航相关12组合。无JS/资源失败或Pages业务请求。

[补充交互](supplement-review.json)：1440/390/320双主题，全部折叠打开后同列与无整页溢出；真实目录锚点、前后页/目录课程链接、两图展开点击及主题正确。静态图无暂停/步进/重播验收。

[实际视觉](visual-review.json)：84教程＋56正式展示壳截图共140张，通过18张联系表全部实际查看；另看3张最终原图（完整对账图、320深色开头、390浅色最终卡片）。覆盖浅深主题、桌面窄屏、两图文字与箭头、局部滚动、章节段落/代码、七阶段卡片。不是全页逐像素审阅。图初稿横向分支压小文字，改D2源为纵向后重新生成；从未手改SVG。

[D2生成](../../../framework/diagrams/f42/generation.json)：官方v0.9.0/dagre/themes4与201、pad24，2源4SVG；fmt/check/validate、真实导出、源与产物SHA-256通过。未采用Archify，未冒称其门禁。[固定源码](source-evidence.json)四份官方源码HTTP200，三份ES v9.4.0与本地字节相同；Kafka源码固定4.0.1。

首次交付，无旧已发布F42勘误。预验收排序断言/Path汇总/Connect非JSON就绪、lazy图加载与图初稿宽度均有原始失败或前版收据，正式通过只计最终完整轮次。实际时间证据还纠正了“PAUSED意味着WAL尚未读”的过强推断：只能定位Kafka前的捕获/队列/发布段。时间戳跨时钟、主动refresh和受控暂停，不当生产延迟/自然可见性SLO或容量基准。

仅验证单分区、合作写入者、持久clock/删除标记和本机协调；未测任意断电、HA、跨分区边界、保留耗尽或生产全集扫描。未知/超前目标只拒绝，未实现自动修复。cleanup/down/原安全节点未变见[shutdown](../../../projects/travel-search/review/f42/shutdown.json)。

[推理配置](reasoning.json)：最新偏好gpt-6.1-sol/max，历史xhigh保留；当前根入口不能设置或独立读回，作者自审未起子代理，不声称已经切换。最终站点/片段/语法、范围、图产物哈希和秘密排除见checks.json。提交推送与Pages在提交后核对，不提前标为已发布。
