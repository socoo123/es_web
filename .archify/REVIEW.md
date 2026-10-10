# 第一章交付与验证记录

使用官方 Archify 3.0.1，从三个 candidate.json 生成 HTML；未手改生成的查看器。最后一次内容修订后，原生 validate、deliver、strict check 均通过，showcase 9/9、零错误/警告。原生 browser-check 失败：管理策略禁止 file:// 导航，报 ERR_BLOCKED_BY_ADMINISTRATOR。因此不把 finalize 的整体结果标成成功。

独立 HTTP 检查与最终 HTML 哈希绑定，覆盖三图四种桌面尺寸、主题同步、暂停后重播、节点探索、原近实时动画操作、390px 页宽和 reduced motion，未出现 JavaScript 错误。额外验证了 11 张实验卡、章节到控制台的真实跳转和 /es_web/ Pages 前缀。它不替代原生检查。记录见 [content-http-review.json](review/content-http-review.json)；当前原生收据在 review/content-* 目录。首次试稿与中间修订的收据保留原始哈希。

实际查看了最终三幅浅色嵌入图、深色倒排图、章节首屏和窄屏截图，未发现文字被截断或横向页面溢出。视觉审阅范围是第一章，未审阅其他章节。关键技术结论通过 v9.4.0 / Lucene 10.4.0 官方源码核对，链接已在正文和 STATUS.md 留存。

沿用 main 分支根目录的 GitHub Pages 自动部署。阅读与图解无需 ES；当前云运行时无法启动 ES 9.4.0，真实实验请求尚未执行，浏览器检查不代表 ES 请求通过。

### inverted-index

- 类型：`architecture`
- 已检查 HTML：`/workspace/es_web/.archify/architecture-ch01-index-20261010-113428/inverted-index.html`
- 图源：`/workspace/es_web/.archify/architecture-ch01-index-20261010-113428/candidate.json`
- 图源 SHA-256：`ef759c1c8d27b3ae491d62841ca1aae0533b3002ef4382c6974354966ea76643`
- HTML SHA-256：`e18480098f26de185a5866c3c710c126ec524871d15153afdb6a523788fa16ec`
- 生成收据：`/workspace/es_web/.archify/architecture-ch01-index-20261010-113428/inverted-index.delivery.json`
- 当前原生检查：`/workspace/es_web/.archify/review/content-inverted-index/inverted-index.finalize-summary.json`

### shard-placement

- 类型：`architecture`
- 已检查 HTML：`/workspace/es_web/.archify/architecture-ch01-shards-20261010-113428/shard-placement.html`
- 图源：`/workspace/es_web/.archify/architecture-ch01-shards-20261010-113428/candidate.json`
- 图源 SHA-256：`a57fae6fe187a30f0a3209576b550f934be1fd15a3b87abd776c1082abe6e06d`
- HTML SHA-256：`53111ffa554a584a295a6566c50609be9f91d57ae0ba62f3fecf2478f38739f7`
- 生成收据：`/workspace/es_web/.archify/architecture-ch01-shards-20261010-113428/shard-placement.delivery.json`
- 当前原生检查：`/workspace/es_web/.archify/review/content-shard-placement/shard-placement.finalize-summary.json`

### analysis-chain

- 类型：`workflow`
- 已检查 HTML：`/workspace/es_web/.archify/workflow-ch01-analysis-20261010-113428/analysis-chain.html`
- 图源：`/workspace/es_web/.archify/workflow-ch01-analysis-20261010-113428/candidate.json`
- 图源 SHA-256：`2061d1cbf39db1084d9f2d0c49c0fb33f72d829646984c09656236d0016afd85`
- HTML SHA-256：`b46772741cbc6b0ec3a82d2ecfb15c0429ecba13d4f0e6435eee547a1d84ce91`
- 生成收据：`/workspace/es_web/.archify/workflow-ch01-analysis-20261010-113428/analysis-chain.delivery.json`
- 当前原生检查：`/workspace/es_web/.archify/review/content-analysis-chain/analysis-chain.finalize-summary.json`
