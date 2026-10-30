# F43 · 图解、阅读与内容验收

正文：[F43](../../../framework/f43.html)。真实ES/Java、负载测量、观察窗和清理在[运行目录](../../../projects/travel-search/review/f43/README.md)独立记录。图解和截图不替代真实执行；本课不声称测得生产容量。

| 验收 | 实际范围与记录 |
| --- | --- |
| 内容 | [作者自审](content-review.json)、[课内清单](lesson-inventory.json)：6758汉字（不含代码）、12代码块/12折叠（8能力检查）/4陷阱、3案例、2静态D2/0播放器；定义、因果、单位、窗口、反例与恢复先讲清 |
| 依据 | [source-evidence.json](source-evidence.json)：官方文档原则、9.4.0 IndexingPressure固定文件与本地逐字节哈希、实际API响应；闭环/到达模型区别有一手来源 |
| 图解 | [图源与生成](../../../framework/diagrams/f43/README.md)：官方D2 v0.9.0/dagre/theme4+201/pad24，fmt/validate/render均退出0，2源/4SVG与哈希；首版过宽改源后重新生成，未手改SVG，未用Archify |
| HTTP/file阅读 | [http-review.json](http-review.json)：/es_web/前缀下1920/1440/1024/768/390/320×浅深12视图，最大880px、左右列对齐、无整页溢出；12块真实Clipboard复制、12折叠、锚点/展开/主题切换与重载、F43已读与F42隔离、file双主题/reduced motion/键盘焦点；无未处理JS/HTTP错误或业务服务请求 |
| 图与相关入口 | 独立SVG1440/1600/1920/2048×浅深×2图共16访问，完整SVG截图另存；目录与F42下一页1440/390/320×浅深12视图；复制和阅读进度逐项验证 |
| 结果表补充 | [detail-review.json](detail-review.json)：1440/390/320×浅深，实测结果/资源表左右滚动、表格留在阅读列内，完整双主题SVG与练习截图；桌面能放下的表格不要求人为滚动 |
| 实际视觉 | [visual-review.json](visual-review.json)、[缩略图与来源](contacts.json)：实际查看首屏、数值表、资源/折叠练习、完整双主题图，以及本机展示壳前后价格；访问/生成和实际审阅范围分开描述 |
| 原始结果复算 | [recomputed.json](recomputed.json)验证原始计时/正式样本边界/nearest-rank分位数/含排空吞吐/线程串行性、Bulk逻辑失败与重试、两轮相同语料与全部压缩前后哈希；[archive-run.py](archive-run.py)无损gzip保留大响应 |
| 保护与清理 | [guards.json](guards.json)记录并发CLI、已有out拒绝且无HTTP；[workspace-state.json](workspace-state.json)记录四索引404、恢复正常配置、卷保留、端口关闭及旧9201 PID/启动/健康不变 |
| 仓库 | [checks.json](checks.json)：node tools/check.mjs、片段一致性、Bash/Python/JSON/Compose/D2/哈希/路径检查；F42正文只有下一课链接改变；未提交target、pycache或.local身份 |

测量边界：负载REST与独立Java共享size10 DSL，F07观察窗保留自己的字段组合与size20，每次按实际esRequest重放。功能相同样本的2500命中不代表DSL、成本或延迟完全相同。浏览器截图不混进性能窗口。已有安全节点和宿主活动未隔离，短窗口/顺序/JIT/热缓存/重复合成文本/闭环自动降速都限制结论；自然阈值、生产SLO、开放到达排队、长稳态/真实热点/故障后余量未测。

[推理入口](reasoning.json)：当前会话无法切换或自行读回用户最新gpt-6.1-sol/max或历史xhigh。作者自行写作与内容审阅，未启动子代理，不声称已实际启用。预验收与复核脚本的桌面滚动假设修正存于[attempts](attempts/)，未冒充正式测量失败或成功；正式运行分别留档。
