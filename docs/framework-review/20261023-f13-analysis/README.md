# F13 · 分析链与中文召回验收

只实施F13及必要目录/前课下一课/工程与当前摘要，提示词转向下一课F14；未实施F14。[正文](../../../framework/f13.html) · [本机实验](../../../projects/travel-search/labs/f13/README.md)。

- [内容](content-review.json)：约4751正文汉字（不含代码），七段式、3案例、58教学HTTP、7折叠练习、3陷阱。索引/查询链的故意失配、恢复与误召回分开；emoji与HTML offset由实测校正。
- [xhigh运行收据](reasoning.json)：根入口无法核验或设置；独立作者与独立审阅均实际配置xhigh并有运行元数据。[初稿](author-draft.md)明确原为预测；[独立内容审阅](independent-content-review.md)无阻断问题，两建议已采纳。[四份固定源码](sources.json)与官方v9.4.0逐字节一致。
- [真实ES/Java两轮](../../../projects/travel-search/review/f13/README.md)：两轮各81客户端请求=教学58+附加23；58不重复计算Java内部两次分析和一次搜索。10输入分析/11REST查询/7Java输入，两份分析与搜索DSL按实际请求重放，完整token/位置/偏移、ID/次序/价格/score/sort/total/relation一致，400/502及重建恢复通过。[最终构建与依赖](../../../projects/travel-search/review/f13/build/runtime.json)单列。
- [图生成](../../../framework/diagrams/f13/generation.json)：官方D2v0.9.0/dagre/主题4与201，2源4SVG，fmt/validate/生成/CLI及源产物哈希通过；无Archify/机制播放器，相应门禁不适用。
- [HTTP阅读](http-review.json)：1920/1440/1024/768/390/320双主题12组，F12/目录24组必要回归，独立图16组；16锚点/组、11折叠/组、22段真实剪贴板，图同步/展开弹窗、已读及旧键隔离、主题重载、实际Tab、file双主题/reduced-motion通过。最大880px、边界差≤1px，无整页横溢，长代码表格局部滚动。[审阅后段落补验](final-text-review.json)另4组，核对白名单来源与UTF16/整数分边界。
- [真实观察窗](shell-review.json)：12尺寸/主题组、47真实Java API，0→4→3、英文2→0、SY、预算50元反例、纯标点空流，tokens/卡片/价格/DSL/DTO与响应逐项核对。400、删索引502、真实停机503及同Java进程恢复通过；浏览器直接请求ES为0，改变条件/错误清空旧结果。
- [视觉](visual-review.json)：48原始PNG，44张看8张标注总览，16张另逐张打开（含4最终段落）；32张仅总览不冒充逐字核对。Java截图仅初始横向位置；完整片段由同步/局部滚动/实际剪贴板补足。卡片与token数字另以DOM/API逐项比较。
- [失败尝试](attempts/README.md)、[资源恢复](workspace-state.json)、[最终仓库检查](repository-checks.json)分别保存。目标索引open_contexts=0，点名删除/GET404；Java正常关闭，框架ES恢复开始前exited状态，卷/源码篇节点保留。

未比较插件/词典/同义词/拼音、未做查询集质量结业或评分调优、性能、多节点、TLS/权限、DB/CDC。搜索执行超时/部分分片失败仅保留代码防护，未注入。F04–F06旧阻塞状态不回填。Pages只承载教程与资产，本机应用由读者启动。
