# F28 · 三节点拓扑、发现与持久首启验收

[正文](../../../framework/f28.html) · [本机入口](../../../projects/travel-search/labs/f28/README.md) · [真实集群执行](../../../projects/travel-search/review/f28/README.md)

仅实施F28，必要前课链接/目录和当前摘要同步；F29没有实现。所有完成状态来自实际收据，作者自审不称独立审阅。

| 验收类别 | 实际范围与收据 |
| --- | --- |
| 内容 | [作者完整审阅](content-review.json)，约5299汉字/七段式/8练习/4陷阱，样本、图、源码、结果与答案一致；[推理入口限制](reasoning.json)：偏好gpt-6.1-sol/max不可设置或读回，无独立代理 |
| 来源 | [sources.json](sources.json)：3份v9.4.0源码与官方字节相等，结合本课实际日志；在线官方文档只作概念依据 |
| 真实集群 | [两轮](../../../projects/travel-search/review/f28/README.md)，各72教学HTTP=26+22+24，等待60/62另计，轮间点名索引/卷清理；真实三进程、UUID/角色/2P+2R/全部字段/重启/错误集群恢复 |
| Java构建 | [runtime.json](../../../projects/travel-search/review/f28/runtime.json)，Boot4/JDK25实际构建/依赖树/实连；复用F07代码与资源，源/包内/HTTP字节相等；No tests to run不是测试通过 |
| 观察窗 | [shell-review.json](shell-review.json)，1440/390浅深×两预算=8次Java调用、8次作者REST重放；浏览器直连ES=0，卡片/原文/输入/DSL一致；没有本课浏览器故障注入声明 |
| 图生成 | [generation.json](../../../framework/diagrams/f28/generation.json)，D2v0.9.0/dagre/浅4深201、2源4SVG，fmt/validate/CLI/哈希；不手改产物 |
| HTTP/file阅读 | [http-review.json](http-review.json)，正文12组、独立图16组、必要前课/目录12组，最大880px/边界≤1px、无整页横溢；29锚点/14折叠/18真实复制、主题/图同步、重载/进度隔离、键盘/reduced motion；最终JS/HTTP/请求错误与Pages业务调用均0 |
| 实际视觉 | [visual-review.json](visual-review.json)，70PNG由6张总览实际查看、另9最终原图单开；320px眉题/表格修正复验，图/表/代码局部右滚动有截图，不称全文逐字或逐像素审阅 |
| 清理 | [workspace-state.json](workspace-state.json)，先复核原身份/完整数据，点名索引清理、Java SIGTERM/18081关闭、F28容器/网络移除、三正常卷/镜像保留；原安全节点Pid/StartedAt/运行/healthy不变，初始容器ID未采集 |
| 仓库 | [checks.json](checks.json)，站点/片段/语法/Compose/数据/图与收据检查；发布在提交后核对，最终SHA/Pages结果放交付与工作树外收据 |

正文与本机操作入口可直接阅读。代表截图：[200元两张卡片](screenshots/shell-1440-light-200.png)、[50元仅p02](screenshots/shell-390-dark-50.png)、[浅色拓扑](screenshots/independent-topology-light.png)、[深色持久流程](screenshots/independent-lifecycle-dark.png)。

[探索与恢复](../../../projects/travel-search/review/f28/attempts/README.md)保留失败与修正；本目录attempts另外保留阅读脚本早期错误/阶段收据，不混入最终通过。作者稿把“只改seed后必产生加入拒绝”改为实际两类诊断：一轮明确拒绝，另一轮独立集群不再发现其他节点。源码、日志和HTTP成员/UUID一起解释原因。

复现：安装Python Playwright与Chromium后运行`reading-review.py`、`shell-review.py`；可用F28_BROWSER_EXECUTABLE指定浏览器。[图生成脚本](generate-diagrams.py)可用D2_BIN指定同版本CLI。[内容审阅](content-review.py)读取正式两轮收据，不重新启动ES；`record-runtime.py`与`cleanup-workspace.py`是本机作者验收脚本，含本次路径/PID与前置安全节点基线，不作为读者实验入口。读者使用labs/f28/README.md。

限制：同Docker VM三进程不证明跨机器容灾；ingest只角色核对；未测routing/随机故障/多数选举/分片失效、扩缩容、性能容量、TLS/权限或CDC；既有Java客户端只配置单地址，没有自动端点发现/切换。浏览器阅读与图生成不能替代ES/Java实测。最终推送状态不在提交前虚填通过。
