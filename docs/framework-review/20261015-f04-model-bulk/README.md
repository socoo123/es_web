# F04 字段设计与 Bulk 阅读验收

日期：2026-10-15。只实施 F04 及必要的前课导航、目录与当前进度摘要，不推进 F05。作者与内容自审在当前根入口无法设置或确认实际 xhigh，未调用独立代理；不把偏好文本当作运行配置。

正文、固定五份资料、28条教学HTTP请求、三案例脚本、两幅D2与六道练习已提供。案例预测、真实执行、图源生成与浏览器阅读分别记录；本课没有 Java/展示壳、插件、多节点、CDC 或机制动画。无 Archify，其门禁不适用。

- [ES启动阻塞与复现](../../../projects/travel-search/review/f04/README.md)：真实两轮未运行，不能标为通过。
- [图解生成](../../../framework/diagrams/f04/generation.json)：D2 v0.9.0 / dagre，双主题4份SVG，fmt/validate/生成已执行。
- [HTTP阅读](http-review.json)、[内容自审](content-review.json)、[静态检查](repository-checks.json)与[补充交互检查](supplemental-checks.json)分别保存；截图生成与实际审阅分别记载。

作者复现：

```bash
python3 framework/diagrams/f04/generate.py /path/to/d2
python3 docs/framework-review/20261015-f04-model-bulk/review.py
node tools/check.mjs
node tools/sync-framework-code.mjs --check
```

浏览器检查用HTTP `/es_web/`，不连接ES；需要Playwright和Chromium。不借用F03的通过数。

## 实际通过与限制

- HTTP `/es_web/`：1920/1440/1024/768/390/320 × 双主题共12组。正文列最大880px，实际880/880/880/724/362/292px，左右差≤1px，无整页横溢；必要代码/表格只在本容器滚动。
- 每组17个目录/图锚点与10个折叠区真实点击，顶栏无遮挡；16段代码实际剪贴板逐字一致。主题重载、双图/展开同步、Tab可见焦点、已读/取消/目录徽标、F03↔F04和目录导航通过；补测F01/旧F01/F02/F03进度键保留与 reduced motion，图注均在图元素范围内。
- F03与目录各12组必要回归，共24组；独立两图1440/1600/1920/2048 × 双主题共16组，实际展开两图通过。JS错误/HTTP失败/请求失败/业务请求各0。未实施F05，没有空下一课链接。
- 最终26张PNG实际查看22张：桌面/390px浅深开头；两图桌面/390px浅深；手机浅深mapping、桌面浅色与手机深色核对请求；320px图；手机展开练习；四幅独立图。其余4张代码截图仅生成。逐张名单/哈希见JSON。320px字较小，但节点/箭头完整，并保留展开。
- `file://` 被浏览器管理策略以 ERR_BLOCKED_BY_ADMINISTRATOR 拒绝，离线打开未验证；HTTP通过单独成立，未改浏览器策略。[初次尝试记录](attempts.json)也记录D2末标签过宽，改图源生成后完整重跑HTTP，未手改SVG。
- ES原Compose启动失败，真实三案例两轮未执行；正文结果全为预测，未生成实测响应。验收脚本语法/资源/数据已检查，但不能称其业务断言已运行通过。当前根入口不能设置/确认xhigh，只有作者自审。

仓库结构、片段同步、JS/Python/Bash语法、JSON/NDJSON/SVG、固定样本与金额/状态一致性、请求数、生成哈希和差异检查通过。本轮按仓库持续授权提交推送origin/main；最终提交与远端是否一致在交付时核对。
