# F06 组合筛选的阅读与内容验收

只覆盖 F06 与必要的 F05 下一课/目录导航。固定 A–E 完整保留，再加 F–L 七份单一边界对照，3案例、22条教学HTTP请求（清理另1条）、2静态D2、6道练习。

- [内容自审与固定版本依据](content-review.json)
- [实际 HTTP 阅读脚本](review.py)、[测量与交互收据](http-review.json)
- [图解生成记录](../../../framework/diagrams/f06/generation.json)
- [真实 ES 状态](../../../projects/travel-search/review/f06/README.md)：原Compose启动失败；两轮未完成

正文预测与真实响应分别标记。截图只证明阅读与交互；生成不等于实际查看，实际审阅范围另记。file://若被浏览器管理策略阻止，单列限制，不修改策略。

根会话无法设置或确认实际xhigh，本轮作者自审，未启动独立代理。实际结果如下；推理强度限制不以提示词记录替代。


## 实际结果

最终 [HTTP收据](http-review.json)通过：Chromium151.0.7922.173，1920/1440/1024/768/390/320 × 浅深12组；阅读列880/880/880/724/362/292px，边界差≤1px、无整页横溢，必要代码/表格局部滚动。每组17锚点、13折叠区；13段代码实际剪贴板与源码逐字一致。

主题切换/重载、双图和展开链接、实际Tab焦点、标已读/重载/目录徽标/取消、F01–F05旧键隔离、F05↔F06/目录导航均通过。F07保留待编写；F05/目录24组必要回归，独立两图1440/1600/1920/2048×浅深16组，双图真实弹窗打开。reduced motion下无平滑滚动，图为静态；JS错误、HTTP失败、请求失败与ES/Java业务请求均0。

最终26张PNG已全部用view_image实际查看并核对哈希，逐张状态在HTTP收据，[截图目录](screenshots/)。覆盖桌面/手机双主题开篇、双图、完整主查询与should请求、320px图、展开练习、独立浅深图。320px图字较小但完整，可展开；请求体截图不能当作ES结果。

第一次视觉审阅发现should图末节点标签被排在框外；缩短D2图源后用官方CLI重新生成，完整重跑HTTP并查看最终截图，已修正。[修复记录与两张原始问题图](visual-fix/record.json)保留；未手改SVG，未把几何测量通过当作视觉通过。

file://被浏览器管理策略以ERR_BLOCKED_BY_ADMINISTRATOR拒绝，离线未验证。HTTP与离线状态分别记录，没有修改策略。

[静态与手工模型核对](repository-checks.json)通过：原A–E保留、mapping逐字继承、12对NDJSON/末尾换行、16组预测独立核对、全部请求覆盖、22+1请求统计、Bash/Python/JS语法与JSON/SVG解析、D2源/产物哈希和差异检查。球面公式及当前简单汉字模型只帮助核对预测，不是Lucene/ES运行。最终 [交付检查](delivery-checks.json)核对实际文件与浏览器收据一致。

[真实ES](../../../projects/travel-search/review/f06/README.md)为blocked_before_http，0成功F06 API、0完成轮次，不能以以上通过项补记。
