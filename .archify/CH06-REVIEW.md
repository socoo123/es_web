# 第六章交付与验证记录

第六章按 CHAPTER_STANDARD 重构为“路由选择 → 参数消费 → GET / HEAD → 入口保护与统计”，保留七段式、目录、图解跳转、上下课导航、已读进度及原有 10 个稳定实验 ID。新增显式建索引、基线 GET、合法 _source 过滤、两个 HEAD、编码 ID 写入与读取 7 卡；共 2 组实验 / 17 张操作卡（含末尾清理）、2 幅 Workflow v2 交互图，均使用有限 trace，无 ESFLOWS 机制播放器。

源码固定到 Elasticsearch v9.4.0 提交 `2e8528e92361c3399724226deaf2b46f933e925b`，仓库 `https://github.com/elastic/elasticsearch.git`。每个语义节点携带查阅的文件 / 行号，首次 finalize 即传入真实源码 checkout 作为 `--repo-root`。图概括普通自管 REST 路由和正常 GetResponse 适配，省略兼容性解析、安全提前失败、分片读取及线程切换；图注与正文保留这些边界。

## 分项验收

| 项目 | 实际结果 |
| --- | --- |
| 内容依据 | 已核对固定版本源码；参数容器与消费、OPTIONS / CORS、breaker overhead、路由统计、Java 客户端等勘误见 STATUS |
| 结构 / 语法 | `node tools/check.mjs`、`node --check experiments/ch06.js`、`git diff --check` 通过；全站 30 页 / 425 张操作卡 / 22 个机制播放器 |
| Archify validate / deliver / strict check | 两图 showcase 9/9、零错误 / 警告，源码证据核验与当前 delivery 哈希匹配 |
| 原生 browser-check | **失败**：Chrome 私有 file 快照被管理员策略阻止，`ERR_BLOCKED_BY_ADMINISTRATOR`；finalize 整体为 fail，未修改管理策略 |
| 独立 HTTP Chromium | 两图各 1440 / 1600 / 1920 / 2048px、浅深主题；章节 1920 / 1440 / 1024 / 768 / 390 / 320px、浅深主题，页面 / iframe 无横向或垂直内容截断，阅读列最大 880px，各区边界差 ≤1px |
| 交互 | 节点探索 / 源码链接 / 关闭、展开、主题同步、两图暂停后外层重播与键盘重播、目录 / 已读、17 卡真实导航到控制台、方法 / 路径 / 请求体、端点 / 认证别名 / raw 标记、Pages 前缀与两图 reduced motion |
| 静态路径 | 相对资源、课间导航、章节锚点、iframe、控制台深链与 `/es_web/` 前缀有效；保留 `.nojekyll`，无未处理 JS 异常或 HTTP 资源失败 |
| 真实 ES API | **首次运行与清理后重做未执行**：本轮 9200 无连接；云运行时缺 `/proc/self/coredump_filter`，已有 ES 9.4.0 启动记录确认阻塞。源码已核对、API 未实测；页面及 curl 请求中的状态、头与 body 均是对照预期，不算本轮实测 |

独立 HTTP 检查不替代原生 browser-check 或真实 API。绑定当前章节、实验、图源与 HTML SHA-256 的结果见 [review/ch06-http-review.json](review/ch06-http-review.json)，重现脚本为 [review/ch06-http-review.py](review/ch06-http-review.py)，需环境提供 Python、Playwright 与 Chromium。未模拟 ES 响应。

## 视觉审阅与修复

实际查看独立图、章节嵌入的浅深主题，以及桌面 / 390px 手机首屏、窄屏图框、长编码路径实验卡与源码表格截图。窄屏图用作结构总览，正文与图注明确给出必要条件；节点探索与展开查看器用于阅读完整细节。表格仅在自身容器内滚动，长实验路径能够换行。图高按本章内容测量：桌面 1100 / 1320px，601–800px 为 820 / 900px，≤600px 为 540 / 600px，减少手机留白；复用共享 CSS / JS，仅本章设置窄屏高度。

路由图初稿的失败分支共用线段导致歧义，已只改 JSON，依据测量把方法集合与选择步骤放入同一阶段并分开入边 / 出边；重新 finalize 后九项检查通过。根目录及 review-2 / review-3 保存旧失败证据，当前结果为 review-4。没有手改生成 HTML。GET 边界图首次 artifact 检查通过，其原生浏览器收据仍失败。

浏览器测试关闭探索后移动指针，避免查看器的 hover 预览重新出现；这修正了测试交互顺序。截图在主题颜色过渡结束后采集，独立图截图用真实暂停控制呈现完整静态关系。截图生成与人工查看分别记录；代表图位于 `review/ch06-*.png`。

## 再生成

使用上述固定提交的干净 ES Git checkout；稀疏 checkout 需包含所有所引 sources。教程目录不能作为源码仓库。修改图源后完整 finalize，已有浏览器证据时使用新的 `--out-dir` 保存新收据。此云运行时使用技能支持的 `ARCHIFY_CHROME_NO_SANDBOX=1` 启动 Chromium；这不会改变 file URL 政策，原生浏览器检查仍失败。

```bash
node /path/to/archify/bin/archify.mjs finalize workflow \
  .archify/workflow-ch06-route-dispatch-20261010-195617/candidate.json \
  .archify/workflow-ch06-route-dispatch-20261010-195617/route-dispatch.html \
  --repo-root /path/to/elasticsearch --quality showcase --json

node /path/to/archify/bin/archify.mjs finalize workflow \
  .archify/workflow-ch06-get-boundary-20261010-195617/candidate.json \
  .archify/workflow-ch06-get-boundary-20261010-195617/get-boundary.html \
  --repo-root /path/to/elasticsearch --quality showcase --json
```

Archify 许可复用 [ARCHIFY-LICENSE.txt](ARCHIFY-LICENSE.txt)，生成 HTML 保留内嵌字体许可。当前机器可读产物身份与门禁另见 [review/ch06-artifacts.json](review/ch06-artifacts.json)。

## 当前产物与原生收据

### route-dispatch

- 类型：Workflow v2，有限 trace。
- 图源：[workflow-ch06-route-dispatch-20261010-195617/candidate.json](workflow-ch06-route-dispatch-20261010-195617/candidate.json)
- HTML：[workflow-ch06-route-dispatch-20261010-195617/route-dispatch.html](workflow-ch06-route-dispatch-20261010-195617/route-dispatch.html)
- 图源 SHA-256：`be88e551955e2051754de7762df2e9c6a5dfb8a6688fc91cf8aab8dabd35844c`
- HTML SHA-256：`d929bd071e70dd1167702f59ba95f468654d755160af3f403bd4266183ccf696`
- 当前原生摘要：[workflow-ch06-route-dispatch-20261010-195617/review-4/route-dispatch.finalize-summary.json](workflow-ch06-route-dispatch-20261010-195617/review-4/route-dispatch.finalize-summary.json)
- 完整收据：[workflow-ch06-route-dispatch-20261010-195617/review-4/route-dispatch.finalize.json](workflow-ch06-route-dispatch-20261010-195617/review-4/route-dispatch.finalize.json)
- Delivery：[workflow-ch06-route-dispatch-20261010-195617/route-dispatch.delivery.json](workflow-ch06-route-dispatch-20261010-195617/route-dispatch.delivery.json)
- validate / deliver / strict check：pass；原生 browser-check：fail，finalize 整体为 fail。

### get-boundary

- 类型：Workflow v2，有限 trace。
- 图源：[workflow-ch06-get-boundary-20261010-195617/candidate.json](workflow-ch06-get-boundary-20261010-195617/candidate.json)
- HTML：[workflow-ch06-get-boundary-20261010-195617/get-boundary.html](workflow-ch06-get-boundary-20261010-195617/get-boundary.html)
- 图源 SHA-256：`a6861be525fc803bb62a4eb70cece64ad0b01b2421da84605d0ea6d26ad9f4ad`
- HTML SHA-256：`6b7ec0848a2be0ccc3a89c85e2108c82e1fccc62ab63c023742a5d9eb2a757a8`
- 当前原生摘要：[workflow-ch06-get-boundary-20261010-195617/get-boundary.finalize-summary.json](workflow-ch06-get-boundary-20261010-195617/get-boundary.finalize-summary.json)
- 完整收据：[workflow-ch06-get-boundary-20261010-195617/get-boundary.finalize.json](workflow-ch06-get-boundary-20261010-195617/get-boundary.finalize.json)
- Delivery：[workflow-ch06-get-boundary-20261010-195617/get-boundary.delivery.json](workflow-ch06-get-boundary-20261010-195617/get-boundary.delivery.json)
- validate / deliver / strict check：pass；原生 browser-check：fail，finalize 整体为 fail。
