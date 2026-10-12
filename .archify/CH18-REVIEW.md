# 第十八章重构验收

2026-10-12（Asia/Shanghai）。已读取 AGENTS、STATUS、PLAN、CHAPTER_STANDARD、CLAUDE；从 ch18 原有 HTML、19 张注册卡与六步快照出发。本轮仅修改 ch18、其图源/生成产物/验收和 STATUS，未通读 tutorial、未使用子代理。共享 CSS/JS 与原有 .gitignore 改动未纳入。

## 内容与依据

锚定 **Elasticsearch 9.4.0 / Lucene 10.4.0**。匿名本机单节点 9200 的 build_hash 与 ES 固定提交 `2e8528e92361c3399724226deaf2b46f933e925b` 一致。按七段阅读结构重排：两层 rewrite 与 toQuery、字段分析/工厂、OR/AND/相对位置、评分/should 门槛、缓存条件、hits/聚合收集边界、Explain 与五个核心入口。3 目标、折叠目录、两图/机制跳转、5 折叠思考题、4 陷阱和速记一致。

[固定源码审计](review/ch18-source-review.json)：**18 文件 / 39 精确区间 PASS**。已实际查看本课目标文件，字节与 clean sparse checkout 的固定 git 对象一致，行范围有效；图内 sources 首次即通过官方 --repo-root 核验。[Lucene 固定 tag 核对](review/ch18-lucene-source-review.json)另保存 StandardAnalyzer、UsageTrackingQueryCachingPolicy 的 URL/行范围/已读取字节 SHA-256。当前官方 prose API 文档只补充语义说明，不替代 9.4.0 执行源码。

主要勘误同时修正文、图、解说、卡片、问答与速记：

- 网页 GET Explain 有 body，但 ESClient 不发送 GET/HEAD body；原两卡真实 400 action_request_validation_exception，保留 ID 改 POST 后真实 200。
- Explain 两入口都解释 rewrittenQuery（可能再经 rescore 等）；过滤别名参与单篇 Explain，不只 originalQuery。原查询保留给默认高亮等观察用途。
- 默认 keyword match 可先在 doIndexMetadataRewrite 收成 TermQueryBuilder；parser 另有短路。normalizer/显式 analyzer 需按条件判断，term 不做全文分词不等于所有字段都原样比较。
- standard 是词边界 tokenizer + lowercase，默认空停用词表；_analyze 不是直接读倒排词典。本例显式保存词向量/offsets，不能推广为默认 text 配置。
- 无同义词/模糊/前缀的本例两位置 match 构造 SHOULD；AND 不约束位置/词序，反向短语失败是词序反而非“两词不相邻”。同文档可累加评分贡献，跨文档不保证命中更多词就排更高。
- must 的评分结论限定普通评分上下文；keyword TermQuery 使用相似度，非固定常数分。should 门槛按同层判断，有 filter 默认 0，显式 1 才要求匹配。
- post_filter 在 Query 阶段只门控 hits 收集，聚合独立收集；不是先截取排序 Top-N 再过滤。query 中 bool.filter 则同时缩小本例两路范围。
- query cache 有可缓存性/策略/segment/容量条件；集合表示按 scorer.cost 的估计条件选择，不按事后精确命中比例。四篇请求不证明缓存收益。

## 真实 ES 与重复运行

保留原 **19 个稳定 ID**，新增 15，共 **3 组 / 34 张操作卡**（A13、B9、C11、清理1）。显式 1 主 0 副、auto-expand=false、strict/stored source、standard、keyword normalizer、price/date mapping、term vector、无默认/最终管道、周期 refresh=-1、request cache 关闭；过滤别名随父索引清理。先局部健康等待，固定 ID bulk refresh=true，再搜索，无抢时间条件。POST 查询体与浏览器客户端相容。

[两轮真实请求与验证](review/ch18-es-review.json)、[复现脚本](review/ch18-es-review.py)：**每轮 34 请求 PASS**；第二轮从第一轮点名清理后的空资源重新建立。请求 method/path/body 与注册表逐项一致，requestIdentityVerified=true。

两轮确认保存词项/位置 the0 quick1 brown2 fox3，Quick, BROWN! 分为 quick/brown；text match/term/大小写、keyword match 整串与 term normalizer；quick fox OR=1/2、AND=1，反向 AND=1/2、反向与有间隔 phrase=0；stop/the 的 none=0、all=4；validate 两项 OR。

Explain 文档 1 matched=true，文档 3 false；过滤别名 Explain 文档 2 false 且含 status:published 约束；search explain 两个 hits。filter/must 文档 4 分数本轮 **1.1608025 → 1.5174774**（只作为本轮值，不写死在预期）；纯 filter 三篇全 0；有 filter 的可选 should 保留 1/3/4，其中 3、4 为 0，显式 minimum=1 只剩 1。post_filter hits=1/3/4，聚合 published3/draft1；query bool.filter hits 相同，聚合只有 published3。

另有 **8 条针对性重复性观察**：真实 mapping/settings，重复创建 400 resource_already_exists_exception，固定 ID 首次四项 created/201、重复四项 updated/200，首次删除 acknowledged、重复删除 404 index_not_found_exception。mapping 序列化会省略等于 analyzer 的冗余 search_analyzer；初始验收守卫误做完整对象相等而失败，修正为对应有效配置后通过，并仅重做这项针对性观察。失败后本课空索引已点名清理。最终索引与别名 HEAD 均 404。

[原卡真实响应](review/ch18-original-responses.json)保留，包括旧 GET 缺 body 的两个真实 400，未当作当前通过结果。没有模拟响应、修改集群设置或操作其他章节资源。本轮未实测多节点、同义词词图、fuzziness、不同相似度、缓存命中率/性能；这些只按固定源码与明确适用条件说明。

## 官方 Archify 门禁

使用[官方 Archify 3.0.1 技能](https://github.com/tt-a1i/archify/blob/v3.0.1/archify/SKILL.md)，已读 defaults、repository authoring、Workflow v2/common schema、指定 example、viewer、delivery 与布局/viewport 契约。两图均中文/showcase/有限 trace；首次附真实固定 ES 源码/checkout。只改 JSON 后运行完整 finalize，未手改 HTML，复用 .archify/ARCHIFY-LICENSE.txt 并保留 HTML 字体许可。

| 图 | candidate SHA-256 | HTML SHA-256 | 当前收据 |
|---|---|---|---|
| query-translation | `b5e72e431145b5411c80fce1407c393657fd524d169936a838583c1ff1be63da` | `2c0751f98d21e2d75959ba06bb7c782e90693a1bc86746b5cc8e79ad3762f556` | review-2 |
| collection-scope | `4bb313b5ea9806e39a4946dc29876a4606588d9208694563dcc72b7aed84b2bd` | `d58dc7a90af84cc131af0bc6beb99c9ae0b145d653dea7e4b224bbf9e9f0b964` | review-3 |

两图 validate/deliver/strict check 均 **showcase 9/9、0 errors/warnings、provenance current**；原生 browser-check 与 finalize 整体均 **PASS**，update.noticeRequired=false。原生 visualReview=not-requested 不表示人工已审图，实际审阅单列。初始候选及原生收据保留；双列初稿桌面原生通过，但 HTTP 手机检测裁切，JSON 纵向重排后修复。collection 主路径按实际截图改为直连；聚合分支需绕过 hits 节点，剩余绕行提示经浅深图实际审阅：箭头完整、无交叉、无 hits 结果转入聚合的错误关系。

## HTTP、交互与实际截图审阅

[独立 HTTP](review/ch18-http-review.json) **PASS**；[局部滚动](review/ch18-scroll-review.json) **PASS**；[实际视觉审阅](review/ch18-visual-review.json)、[六步捕获与审阅](review/ch18-mechanism-review.json)分别绑定。临时本地 HTTP + Python Playwright + 本机 Chrome。控制台深链会自动执行，HTTP 检查显式 abort 本机 ES 请求，没有发送/伪造 ES 响应；真实 API 另行执行。

- 两图独立 1440/1600/1920/2048 × 浅深；说明卡完整、无横向溢出。最小 SVG/普通节点投影：translation 7.328/8.375px，collection 7.718/8.820px。
- 章节 1920/1440/1024/768/390/320 × 浅深；阅读列最大 880px，左右边界差≤1px，页面/iframe 无横溢，所有节点完整。图框桌面均 790px，≤800px 均 540px，iframe 无垂直溢出。
- 探索/固定提交源码/关闭、展开、同步主题、暂停→外层重播/Enter、目录/已读、六步手动前后/播放/重置/键盘、34 条实际控制台导航 method/path/body、endpoint/auth/raw、/es_web/ 前缀静态路径通过，JS 未处理错误和静态 HTTP 失败为空。
- reduced motion 优先且重播不覆盖系统偏好；机制不自动播、手动步进保留，页面无平滑滚动。390/320 源码表/旧 SVG 仅在自身容器滚动。
- **实际查看 24 张最终独立/嵌入/桌面/390px/实验/表格浅深截图，及全部六步完整快照**。手机图是完整概览，细字需探索/展开缩放，必要结论在正文/图注。旧 SVG 局部横滑；手机播放器标题省略，但解说完整。
- [初稿手机失败](review/ch18-containment-failure.json)与对应截图保留；collection review-2 的 HTTP 历史记录/截图保留，明确为旧 HTML 的审阅，不当最终收据。

## 检查与复现

站点 **30 正式页 / 604 操作卡 / 22 机制播放器**，Archify trace 另计。node tools/check.mjs、修改 JS 语法、figwidth、git diff --check、19 稳定 ID/34 唯一有序槽位、GET/HEAD 无 body、.nojekyll 与静态路径通过。[最终产物与证据哈希](review/ch18-artifacts.json)绑定当前图、报告、截图、章节与注册表。

```bash
node tools/check.mjs
node --check experiments/ch18.js
node tools/figwidth.mjs chapters/ch18.html experiments/ch18.js
ES_SOURCE_ROOT=/path/to/clean-es-v9.4.0 python3 .archify/review/ch18-source-audit.py
python3 .archify/review/ch18-es-review.py               # 两轮实际操作 + 8 条针对性观察 + 点名清理
python3 .archify/review/ch18-es-review.py --validate-only
/path/to/playwright-python .archify/review/ch18-http-review.py
/path/to/playwright-python .archify/review/ch18-scroll-review.py
/path/to/playwright-python .archify/review/ch18-mechanism-review.py
python3 .archify/review/ch18-bind-artifacts.py          # 实际看完新截图后才更新审阅绑定
# 图重现：官方 finalize workflow candidate.json output.html --repo-root ... --quality showcase --json
# JSON 修改后完整重新 finalize；已有 browser 证据时用新的 --out-dir。
```

本轮按持续授权提交并推送 origin/main；GitHub 远端与 Pages 完成状态在交付时另行核对，不将本地验收等同线上更新。
