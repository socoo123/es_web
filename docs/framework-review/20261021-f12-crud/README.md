# F12 · 更新、可见性与基础结业验收

本轮只实施F12及必要前课导航、目录和当前摘要。[正文](../../../framework/f12.html) · [本机实验](../../../projects/travel-search/labs/f12/README.md)。当前入口无法设置或核验xhigh，作者自审、无独立代理；提示词没有改变实际运行配置。

- [内容自审](content-review.json)：约5177正文汉字（不含代码），七段式、3案例、114条主流程HTTP、6练习；CRUD/可见性/条件写与独立新样本结业。任务先于折叠参考解，作者脚本通过不替读者结业。[六份固定源码收据](sources.json)均与官方v9.4.0逐字节一致。
- [真实ES/Java](../../../projects/travel-search/review/f12/README.md)：两轮各160请求（主流程114+附加断言/清理46）。GET/search受控旧新值、完整替换/局部合并/删除、409与重读、noop、true/wait_for、输入错误及独立结业资料通过。构建与依赖树单列，无单元测试。
- [图生成](../../../framework/diagrams/f12/generation.json)：官方D2v0.9.0/dagre，浅4深201，2源/4SVG；fmt/validate/生成及CLI/源/产物哈希通过。不使用Archify或机制播放器，对应门禁不适用。
- [HTTP阅读](http-review.json)：1920/1440/1024/768/390/320双主题12组；F11/目录24组回归、独立图16组；17锚点/组、12折叠/组、15段真实剪贴板逐字对照，图同步/弹窗、导航、独立已读、旧键隔离、实际Tab、file双主题与reduced motion通过。桌面880px、各区边界差≤1px、无整页横溢；长代码/表格局部可滚。26截图。
- [真实观察窗](shell-review.json)：12尺寸/主题组、86次真实API操作，浏览器→Java→ES，未模拟响应。2/1分页与GET/卡片分元/sort/DSL/DTO逐项比较；改价GET新/搜索旧、refresh/旧PIT、双窗口409及重读、条件改变、空集、404、502删索引重建、ES真实停机503/同Java进程恢复通过，直接ES浏览器请求0。14截图。
- [补充区域截图](visual-detail.json)：额外13次真实API、9PNG，完整409提示、GET9000与旧PIT4500、重新读取closed和新结果，以及观察窗双主题开头。
- [视觉范围](visual-review.json)：49原始PNG中40张看标注总览，19张另逐张打开（包括所有9张补充）；仅作总览的30张不冒充逐字全文核对。长Java截图为初始横向位置，右侧需局部滚动，片段同步/真实剪贴板补足；卡片数字以DOM/API逐项比较。七张总览另存在[overview](overview/01.png)。
- [失败尝试](attempts/README.md)、[资源恢复](workspace-state.json)、[最终仓库检查](repository-checks.json)分别记录。两索引结束前open_contexts=0、点名删除确认404；两个Java正常关闭，框架ES恢复原停止状态，持久卷/源码篇节点保留。

未测试随机并发/负载/性能、主分片切换、多节点故障、refresh监听槽耗尽、TLS/权限、插件/数据库/CDC或跨系统事务；搜索超时/部分分片失败仅沿用防护。F04–F06历史受阻状态不回填。Pages只承载教程，观察窗由读者本机启动。
