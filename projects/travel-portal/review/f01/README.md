# 旧门户草稿的验收记录

本目录与 `projects/travel-portal` 一起保存，属于历史草稿，不作为现行 F01 或 F07 的通过证据。当前 Java 搜索工程与验收在 [travel-search](../../../travel-search/README.md)。

`api-browser.json` 的原始时间为 2026-10-13，记录两轮路由、请求契约与 Java 健康 API 的通过结果；18 张截图、Java/Vite 原始日志一并保留。JSON 的 `visualReview` 仍是 `pending actual image inspection`，不能据其 `result: pass` 声称视觉验收完成。本次未修改原始 JSON、截图或日志。

本次核对 JSON 所列文件哈希：除 `framework/f01.html` 已被现行导学替代外，其余列出的工程、依赖锁文件、图源和 SVG 均一致。旧验收脚本依赖当时的教程 DOM，不可用来验证当前 F01。

2026-10-20 保存前实际执行的检查：

- `npm run build`：TypeScript 检查与 Vite 生产构建通过。
- 独立临时目录的 lesson 模式构建：3 个生成文件与保留的 `framework/labs/travel-portal` 产物逐字节一致。
- `./mvnw -B -ntp clean package`：JDK 21 编译与 Boot 3 打包通过；工程没有单元测试。
- 历史实验 JavaScript 语法、Python AST、JSON/XML/SVG 解析及仓库 `node tools/check.mjs`、片段同步检查通过。

本次没有重新运行 Java 健康接口或浏览器案例，没有重新做图解生成与截图视觉审阅，也没有 ES、数据库、搜索、报价或预订验收。
