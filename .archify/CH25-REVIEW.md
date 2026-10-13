# ch25 重构验收（ES 9.4.0 / Lucene 10.4.0）

本章围绕“拒绝发生在哪一步，以及怎样恢复到原基线”重构。保留原 14 个稳定操作 ID 和 `ch25-breaker` 七步机制，实验重排为 29 张操作卡（前提 5 / A 6 / B 10 / C 4 / 清理 4），新增两幅 Archify workflow v2 交互图和两条有限 trace。只改 ch25、首页本章卡片及本章进度/证据，共用 CSS/JS 直接复用。

## 内容与源码

固定官方 ES revision `2e8528e92361c3399724226deaf2b46f933e925b`（v9.4.0），Lucene 10.4.0。手工沿实际方法、调用和分支阅读，`review/ch25-source-review.json` 另验证 **22 个文件 / 58 处行段**与干净 checkout、固定提交的字节相同。字节审计不替代语义审阅。

- 正限额先比较 `(used+bytes)×overhead` 再 CAS；CAS 冲突重新读取/比较。Parent 失败后回滚原始 `-bytes` 再抛。`-1` 只跳过子限额，仍检查 Parent；0 立即拒绝检查入口。
- Parent 默认用真实堆加本笔预留；false 模式汇总所有注册子账 `used×overhead`，不重复再加已入账增量。默认总限额随模式为 95% / 70%，实际值需看配置。
- 首次 Parent 超限还调用 overLimitStrategy，策略结果仍超限才抛；G1 分支可尝试 GC 和复采样，不能保证回收/通过。Parent durability 按全部子账 transient/permanent 估算占比；这只是类别提示。
- 子账统计 estimated 是 raw used，overhead 单列；Parent estimated 来自 memoryUsed(0)，不能强制与三本裸账之和建立大小关系。tripped 是实例内累计计数，不作锁定开关。
- 6KB 预留覆盖包装器内的 5KB，超过缓冲只补差，缓冲满后直通。关闭聚合器/包装器释放相应账额，实际堆回收由 GC 决定。BigArrays 有分配前与分配后核算路径，不能说“从不先分配”。
- size/shard_size 可影响候选窗口及相关内存，却不能限制全部收集状态；min_doc_count 不是普遍的收集内存上限，cardinality 只适用于近似计数语义。
- IndexingPressure 是另一套阶段字节账；coordinating/primary 对 combined+replica 比较，replica 看自己的字节，普通检查受 forceExecution 条件影响。增量 Bulk maybeSplit 使用用量与当前块大小两项 `>=`，高水位分支先判断，不是所有 HTTP Bulk 体积必拆。
- 429 需要读完整 error/type/reason；Parent 示例名称是 `[parent]`，低限额实验预期 `[request]`。健康色、节点存活、下次请求成功都不能由一次熔断保证。
- null 删除指定层覆盖，回到 persistent/节点/默认，不自动还原已覆盖的 transient 原值。示例改为 H=1000MiB 的明确算术，不把 1GiB 的 95% 当成 950MiB。
- 三次 terms 均设 `request_cache=false`，只控制本次请求，不修改索引缓存设置，排除重复查询缓存路径干扰。

具体旧说法、修正与固定链接见 STATUS「第二十五章重构校对」。

## 实验顺序与恢复

单个专用本地 9.4.0 节点，默认 memory 型 request、overhead=1，无其他客户端并发，堆有余量；默认端点 localhost:9200，匿名；启用安全先选择正确认证。前提读取版本、节点数/堆/节点配置、两层集群覆盖、实际限额/tripped 与 CAT 节点标识。

仅 request.limit 原先无 transient/persistent 覆盖且节点默认时继续 B；原有覆盖时跳过 B 与相应设置清理，不把未知值清空。本组仅修改 `transient.indices.breaker.request.limit`，无 persistent/Parent/线程池设置修改。

A：HEAD404 → 显式 1P0R、auto_expand=false、strict keyword → 等本章 Green → 固定 ID 1–20 Bulk + refresh → count20 → 关闭本次请求缓存的 terms。B：设置1kb → 来源确认 → 实际1024与拒绝前计数 → 同一 terms → 比较计数增量 → 立即 null → 来源删除确认 → 实际限额回基线 → 同一 terms / match_all。完整错误保留；不写死一次 REST 只增加一次计数，或 bytes_wanted 必精确6144。

C 只读 current/total/线程池基线，正常固定 ID Bulk 重写后对照正常累计。**未以小 Bulk 验证背压拒绝或拆分水位**。首次 Bulk 是 created、重复是 updated，count 不翻倍。清理先删除本轮 transient（只有执行过 B1 时），对照设置并重读实际账本，再点名删 tut-l25-card、HEAD404，完整重做从前提开始。累计计数不因删索引归零。

## 真实 ES 实验：未运行

本轮真实执行官方 Compose 启动命令，容器 `es-study` 于 `2026-10-13T06:48:11.809329828Z` 启动，`06:48:16.921506773Z` 退出，exit1。异常为 `Could not set coredump filter`，原因 `NoSuchFileException: /proc/self/coredump_filter`；9200探测退出7。只记录本次启动后的错误，见 `review/ch25-es-runtime.json`。

全部 API、低限额拒绝、设置清理与首次/重复运行均未实测，没有合成 ES 响应。网页已经明确标注这是固定源码核对后的待实测预期。浏览器控制台测试显式 abort localhost:9200 流量；它只能验证卡片/深链，不证明服务端行为。

## Archify 原生门禁与独立 HTTP

两个候选均设置 zh-CN/showcase/trace，保留真实 ES 仓库身份、具体节点源码及 `--repo-root`。仅改 JSON，正式 finalize 生成，无手改 HTML。复用 `.archify/ARCHIFY-LICENSE.txt`，生成 HTML 保留字体许可。

聚合预留图初稿 `construct-buffer` 与 `overflow-direct` 共用44px外侧通道；按实际 diagnostic 修复 `construct-buffer` bottom→top 接口，保留其他语义与布局，完整 finalize 重跑。初稿 JSON 和 `review/ch25-aggregation-layout-failure.json` 保存；**1 次布局修复**。拒绝路径图无布局修复。

| 图 / type | 当前候选 / 产物 / 收据 | 原生结果 |
| --- | --- | --- |
| 拒绝路径 / workflow v2 | `workflow-ch25-breaker-paths-20261013-145213/{candidate.json,breaker-paths.html,breaker-paths.finalize.json}` | validate / deliver / strict check：9/9、0错误0警告；browser-check失败 |
| 聚合预留 / workflow v2 | `workflow-ch25-aggregation-buffer-20261013-145213/{candidate.json,aggregation-buffer.html,aggregation-buffer.finalize.json}` | validate / deliver / strict check：9/9、0错误0警告；browser-check失败 |

原生 Chrome 的 file快照导航返回 `net::ERR_BLOCKED_BY_ADMINISTRATOR`，因此两个 finalize 整体均为 fail；没有修改浏览器策略或把 HTTP 通过改记成原生通过。更新检查 noticeRequired=false，无需升级提示。

独立 `review/ch25-http-review.json` **pass**：两图分别检查1440×900 / 1600×1000 / 1920×1080 / 2048×1320浅深主题；章节1920 / 1440 / 1024 / 768 / 390 / 320浅深主题。桌面列≤880px，各区左右边界差≤1px；整页及 iframe 无横向溢出，节点完整位于面板内，说明卡无截断。桌面独立最小投影 SVG字约7.041px、普通节点字约8.047px。

测得嵌入高度：拒绝路径1080px / ≤800px640px；聚合预留980px / ≤800px620px，工具栏、探索、图内主题、外层重播/展开正常。已检查暂停→外层重播、键盘Enter/Escape焦点与关闭、reduced motion 强制静止、机制不自动播放但可步进、页面不平滑滚动、目录跳转/进度、29个真实卡片的控制台请求内容、endpoint/auth别名/raw标记、Pages前缀相对资产与无present展开。没有未处理 JS 错误或失败的 HTTP 资产。

`review/ch25-scroll-review.json` **pass**：390/320 双主题，源码表与原机制 SVG 只在自身容器横向滚动，整页保持包含。`review/ch25-mechanism-review.json` **pass**：七张完整快照、唯一 marker 与文字边界、前后/重置/播放及键盘均核对；快照生成与实际视觉审阅另记。

## 实际视觉审阅

实际通过 image reader 查看 **7张联系表，覆盖24张最终章节/图解截图和全部7步机制截图**，`review/ch25-visual-review.json` 绑定当前HTML/JS及截图 SHA。检查了浅深主题标题、目标、桌面独立和880px嵌入、手机图/实验/源码表、机制双主题与各步。

两图分支、条件与箭头可辨，没有文字越框、节点遮挡或说明卡截断；目录不遮内容。窄屏的 Archify 是路径总览，精细源码/标签通过点节点、正文或“展开图解”读取，不声称桌面完整说明直接在小屏同样易读；旧机制标题会省略、SVG可在自身容器滚动，完整步进解说保留。源码表可局部横滚。联系表的灰色空白是拼版布局，不是网页空白。

## 站点检查与复现

- `node tools/check.mjs`：30正式页 / **730实验卡 / 22机制动画**，通过。
- `node --check experiments/ch25.js`、`node tools/figwidth.mjs chapters/ch25.html experiments/ch25.js`、`git diff --check`：通过。
- 22文件/58行段固定源码与14稳定ID/29操作顺序审计、独立HTTP、局部滚动、7步捕获、实际视觉审阅：通过/完成；最终哈希见 `review/ch25-artifacts.json`。

从仓库根目录按顺序运行 source-audit、http-review、scroll-review、mechanism-review Python脚本；visual-sheets仅生成截图联系表，必须实际查看后才填写 visual-review。需要 Python Playwright/Pillow 和 `/usr/bin/chromium`。源码默认 `/workspace/scratch/es-v9.4.0`（可用 ES_SOURCE_ROOT），只检查固定提交与本章目标片段。Archify 用上表候选运行标准 finalize；当前环境仍会真实返回原生浏览器失败。
