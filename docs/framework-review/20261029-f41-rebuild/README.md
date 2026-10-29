# F41 · 持续更新重建、追平与切换回滚验收

本轮仅实施[F41](../../../framework/f41.html)和必要的目录、前课下一页及当前进度摘要。正文与[本机工程](../../../projects/travel-search/labs/f41/README.md)先解释业务/来源契约、全量与增量交叠、来源检查点，再实现双版本投影、拒绝/恢复和回滚。运行记录在[review/f41](../../../projects/travel-search/review/f41/README.md)。

三案例两轮真实PG→Debezium→Kafka→Java→ES与展示壳通过，见[run-03](../../../projects/travel-search/review/f41/run-03/summary.json)、[清理后run-04](../../../projects/travel-search/review/f41/run-04/summary.json)。每轮19来源事件、4来源fence、16次Java命令、92项协调/观察HTTP，36项Java Bulk结果另列，客户端HTTP未逐请求抓取。最终两组next19、p01/76元、p04/48元；不以图解或截图替代这些断言。构建Boot4.0.8/JDK25与ES内置JDK分别记录。

正文约5353汉字（不含代码）、20代码块、13折叠（含8能力检查）、4陷阱，七段式/880px/双主题；关键SQL、完整Java投影/守卫/Bulk与提交、Python切换门槛均与工程片段一致。首次交付，无旧已发布F41勘误；作者自审和预发布更正见[content-review.json](content-review.json)，不是独立代理审阅。

[HTTP阅读](http-review.json)：Playwright1.64.1/Chromium156.0.8078.4，1920/1440/1024/768/390/320×浅深12组合，桌面列880、768列724、390列362、320列292，区块边界差≤1px，零整页横溢。表格/代码/D2仅局部滚动。20次真实Clipboard复制、13折叠开合、主题切换/重载/图源同步、F41进度与F40隔离/目录反映、15本地链接200、file双主题/reduced-motion/键盘焦点通过。独立2图×4桌面视口×双主题=16组合；目录和F40下一页相关12组合。最终记录无JS/HTTP/请求失败或Pages业务调用。

[补充交互](supplement-review.json)：1440/390/320双主题全折叠打开布局、真实目录锚点/前后页/目录课程链接/每图展开点击通过；窄屏展开入口可发现。两图静态，无播放器或动画控制验收。

[实际视觉](visual-review.json)：正式教程80张、两轮展示壳48张，共128张通过16张contact实际查看；另按原尺寸查看7个具体截图，范围和文件列在记录中。桌面浅深/320与390窄屏、两幅完整图、局部滚动、代码/段落、六稳定点卡片前后对照已审阅。非全页逐像素审阅；截图生成与人工查看分列。最终头部实数更新后重新跑HTTP并查看桌面浅色/320深色原图。

源码记录见[source-evidence.json](source-evidence.json)：3份官方固定版本源码HTTP200，ES两份与本地字节相同，首次误用旧ReindexRequest路径的404保留后更正。两幅静态D2 v0.9.0/dagre/themes4与201、2源4SVG的fmt/validate/实际命令/哈希见[generation.json](../../../framework/diagrams/f41/generation.json)，未用Archify。图生成、阅读与真实执行分开。

未验证任意断电/HA、Kafka故障、跨分区来源屏障、分布式协调、生产吞吐、保留耗尽或自动恢复alias/job崩溃窗口；本课只证明固定检查点及持续维护的回滚窗口。源业务可继续在H之后提交，积压明确展示，不宣称零延迟强一致。

推理配置：逐课提示词最新请求gpt-6.1-sol/max，旧xhigh要求仍有历史记录。根会话自行写作和内容自审，未启动子代理；当前入口不能设置或独立读回运行模型/强度，不声称已经选择，见[reasoning.json](reasoning.json)。最终站点/片段/语法/范围与实际秘密排除见checks.json；推送与Pages在提交后核对，未提前标为已发布。
