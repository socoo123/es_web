# F29 · 内容、图解、HTTP与视觉验收

仅实施F29，必要当前摘要/目录与F28下一课链接同步；F30未实施。正文约5039汉字（不含代码）、七段式、3案例/62教学HTTP、13次独立Java SDK调用另计；2静态D2、8折叠练习、4陷阱、0机制播放器。

- [作者自审](content-review.json)：概念、因果、版本分支、错值反例、复制/读取、请求/Java与清理一致；无独立代理。[运行入口](reasoning.json)不能设置或读回用户最新gpt-6.1-sol/max，不以提示词冒充实际配置。
- [源码](sources.json)：四份v9.4.0官方原文件与本地字节相等；IndexRouting创建版本与Unpartitioned、OperationRouting目标组/偏好、TransportGetAction.shards、ReplicationOperation.execute/handlePrimaryResult/performOnReplicas按目标方法核对。
- [D2生成](../../../framework/diagrams/f29/generation.json)：官方v0.9.0/dagre/主题4与201，2源4SVG的fmt/validate/导出与SHA通过，改源后重生成。搜索图把两条独立请求放在同一对照卡片，避免误读为先全后缩小。
- [HTTP阅读](http-review.json)：1920/1440/1024/768/390/320×浅深12组，阅读列最大880px、边界差≤1px；29锚点、13折叠、24真实剪贴板、主题/图同步/重载/已读隔离、file双主题/reduced-motion/键盘通过，零整页横溢。独立图4桌面宽度×双主题×2图共16组，必要目录/F28共12组；无JS、HTTP或请求失败，Pages业务调用=0。
- [视觉](visual-review.json)：54张阅读/图截图经5组总览实际查看，部分最终原图单开；[额外Java代码截图](code-screens.json)8张，长行局部滚动；代码/观察窗/最终正文另20张经2组总览查看，其中最终实际结果正文增加4组针对性HTTP复验，见[收据](final-smoke.json)。实际观测与范围写明，未声称逐像素或全部代码逐字视觉审阅。
- [真实观察窗](shell-review.json)：独立8次Java调用+8次作者REST重放，截图与source/packaged/HTTP资源字节一致性分别验证。展示壳只连接默认索引，无前端/Controller改动。
- [真实两轮ES与Java](../../../projects/travel-search/review/f29/README.md)：每轮62教学HTTP+13 SDK调用+5附加验证HTTP；启动、等待、清理与浏览器独立计数。ID/source/routing/错误与恢复、当前主副实际读取分别核对。
- [最终清理](workspace-state.json)与[检查](checks.json)记录本课资源边界与必要站点/片段/JSON/Python/Bash/Compose检查；提交后远端SHA/Pages验证在工作树外收据及交付中，不提前冒充发布成功。

单Docker VM、固定小资料；跨主机容灾、故障恢复、性能、热点、权限与后续课程均未测。未修改历史章节内容，只将必要前课导航接到F29。
