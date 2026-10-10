# 第七章交付与验证记录

第七章按 CHAPTER_STANDARD 重构为“名字与执行体 → 公共执行骨架 → 线程与远程登记 → 登记 / 运行 / 计数”。保留七段式、目录、图解跳转、上下课导航和已读进度。原有 9 个实验 ID 全部保留，新增 6 卡，共 2 组实验 / 15 张操作卡（含清理）；2 幅 Workflow v2 图均启用有限 trace，无 ESFLOWS 机制播放器。

源码固定到 Elasticsearch v9.4.0 提交 `2e8528e92361c3399724226deaf2b46f933e925b`，仓库 `https://github.com/elastic/elasticsearch.git`，Lucene 10.4.0 为本站版本锚点。每个图中语义节点附已查阅的文件和行号；首次及修复后的完整 finalize 都传入真实、干净源码 checkout 作为 `--repo-root`。

## 分项验收

| 项目 | 实际结果 |
| --- | --- |
| 内容依据 | 固定版本源码核对；通配匹配、异步 filter、GET 基类 DIRECT、两张登记表、引用释放与 Task 注销、REST 正数计数等勘误见 STATUS |
| 站点结构 / 语法 | `node tools/check.mjs`、`node --check experiments/ch07.js`、`git diff --check` 通过；全站 30 页 / 431 操作卡 / 22 个机制播放器 |
| Archify validate / deliver / strict check | 两图 showcase 9/9、零错误 / 警告，源码证据校验与当前产物 provenance 匹配 |
| 原生 browser-check | **失败**：Chrome 私有 file 快照被管理员策略拦截，`ERR_BLOCKED_BY_ADMINISTRATOR`；两次当前 finalize 整体为 fail，未修改管理策略 |
| 独立 HTTP Chromium | 两图各 1440 / 1600 / 1920 / 2048px，浅深主题；章节 1920 / 1440 / 1024 / 768 / 390 / 320px，浅深主题；页面与 iframe 无内容溢出，阅读列最大 880px，各区边界差 ≤1px |
| 交互 | 节点探索 / 固定源码链接 / 关闭、展开、主题同步、暂停后外层重播 / 键盘重播、目录锚点、已读进度、15 张卡真实导航到控制台及方法 / 路径 / 请求体、端点 / 认证别名 / raw、Pages 前缀、两图 reduced motion |
| 静态路径 | 相对资源、课间导航、章节锚点、iframe 和控制台深链有效，保留 `.nojekyll`，未发现未处理 JS 异常或 HTTP 资源失败 |
| 真实 ES API | **首次与清理后重做未执行**。允许的网络权限下再次探测 9200 无连接；运行时仍缺 `/proc/self/coredump_filter`，既有 ES 9.4.0 启动记录确认阻塞。未重复启动、修改 ES 或模拟 API 响应 |

独立 HTTP 检查不替代原生 browser-check 或真实 API。页面所有状态、计数增量和字段均注明是源码对照预期；历史勘误表中的本地实测记录保留其原始口径。内部未登记 ActionType 的异常未用错误 URL 冒充实测。

当前 HTTP 结果绑定章节、实验、两幅图源及 HTML SHA-256，见 [review/ch07-recheck-20261010/http-review.json](review/ch07-recheck-20261010/http-review.json)；复现脚本为 [review/ch07-http-review.py](review/ch07-http-review.py)，需要环境提供 Python、Playwright 与 Chromium。所有当前文件、收据和已查看截图的哈希汇总见 [review/ch07-artifacts.json](review/ch07-artifacts.json)。

## 2026-10-10 复核

重新核对名字身份、本地 / 远程登记、查表与 Task 先后、校验与异步 filter、引用释放、DIRECT 与 GET 分片 executor、Task 名称匹配、REST 使用计数及实验清理 / 重做条件。本章引用的 18 个源码文件逐一与固定提交比对，内容一致；记录见 [source-review.json](review/ch07-recheck-20261010/source-review.json)。

发现并修正一处实验预期字段错误：B5 未注册 URL 的 HTTP 400 由 `RestController.handleBadRequest` 直接输出顶层 `error` 字符串，旧卡片写成读取 `reason`。操作卡改为对照 `error`，正文增加该方法的固定版本链接；图中没有这项字段断言，图源和 HTML 哈希均未变，保留有效的 review-4 原生收据。

修改后重新执行完整独立 HTTP 浏览器检查：两图四档桌面尺寸、章节六档宽度、双主题、探索 / 关闭 / 展开、暂停后重播 / 键盘 / reduced motion、目录 / 已读、15 张实际控制台导航及 Pages 前缀通过，无未处理 JS 异常或资源失败。另检查修正卡片和源码说明在 390px 双主题下的显示；实际查看并保留 8 张本次截图。此前 20 张已审阅截图保留各自的历史记录；本次没有把所有新生成截图计为已审阅。

站点检查、JS 语法与 diff 检查通过。9200 再次探测仍连接拒绝，运行时仍缺 `/proc/self/coredump_filter`；真实 API 未执行，原生浏览器门禁的环境限制不变。

## 视觉审阅与修复

实际查看了 20 张截图：两图独立页与章节嵌入的浅深主题、桌面 / 390px 手机首屏、两图手机图框、长任务过滤路径操作卡及源码表。表格在自身容器内滚动，实验路径可换行。窄屏图作为结构总览，正文 / 图注保留机制条件，节点探索与展开查看器提供完整细节。图框高度按截图与浏览器测量调整：桌面 760px，601–800px 为 680px，≤600px 为 440px，两图一致；共享 CSS / JS 未改动。

图源初稿的执行回调与入边共用线段，showcase 校验指出歧义；通过 JSON 明确主路径端口修复。截图审阅后缩短标题、压紧纵向间距，将绑定与 initialize 合为一个有双来源的节点，保留名字查表、未命中、Task 先登记及执行失败 / 短路分支。两图当前原生收据均为 `review-4`，根目录和 earlier review 保存历史收据及 candidate 快照；未手改生成 HTML。

独立查看器在四档桌面宽度均检查完整 SVG 的 6px 投影下限，普通节点上下文另外检查 7px 下限，说明卡必须存在且无自身裁切。实际最小普通节点上下文约 7.5px（第一图）/ 7.6px（第二图），来源徽标等最小文字约 6.56px / 6.66px；没有把建议的 7.5px 当作所有徽标的保证。

HTTP 初始 / second / third 与原 `ch07-http-review.json` 报告保留当时的布局与交互证据，所绑定章节、实验、图源或图框高度与当前版本可能不同；当前验收以 `ch07-recheck-20261010/http-review.json` 为准。截图在主题过渡后采集，独立图使用真实暂停控制查看静态全图；关闭节点探索后移开指针，避免 hover 预览重新出现。截图生成和实际查看分别记录。

## 再生成

使用上述固定 ES 提交的干净 Git checkout；稀疏 checkout 须包含所引 sources。修改图源后完整 finalize，已有浏览器证据时用新的 `--out-dir` 保存收据。此容器用技能支持的 `ARCHIFY_CHROME_NO_SANDBOX=1` 启动 Chromium；它不改变 file URL 策略。当前命令虽通过前三个门禁，仍以原生浏览器失败退出。

```bash
ARCHIFY_CHROME_NO_SANDBOX=1 node /path/to/archify/bin/archify.mjs finalize workflow \
  .archify/workflow-ch07-action-dispatch-20261010-214548/candidate.json \
  .archify/workflow-ch07-action-dispatch-20261010-214548/action-dispatch.html \
  --repo-root /path/to/es-v9.4.0 --quality showcase \
  --out-dir .archify/workflow-ch07-action-dispatch-20261010-214548/review-next --json

ARCHIFY_CHROME_NO_SANDBOX=1 node /path/to/archify/bin/archify.mjs finalize workflow \
  .archify/workflow-ch07-execution-chain-20261010-214548/candidate.json \
  .archify/workflow-ch07-execution-chain-20261010-214548/execution-chain.html \
  --repo-root /path/to/es-v9.4.0 --quality showcase \
  --out-dir .archify/workflow-ch07-execution-chain-20261010-214548/review-next --json

python3 .archify/review/ch07-http-review.py
node tools/check.mjs
node --check experiments/ch07.js
git diff --check
```

## 当前哈希

| 图源 / 产物 | SHA-256 |
| --- | --- |
| [candidate.json](workflow-ch07-action-dispatch-20261010-214548/candidate.json) | `3f86acd2e5cdc87e70de8a9bc58fdc86746a4359167f3eab330f05c22f15a06a` |
| [action-dispatch.html](workflow-ch07-action-dispatch-20261010-214548/action-dispatch.html) | `5495d69ea9efd183cb7b52ff92814d33f1de9d50b6572e4ff2fca0b036c54ade` |
| [candidate.json](workflow-ch07-execution-chain-20261010-214548/candidate.json) | `d070c077153996f56b1a8aef02f16de99bb54208ca7e0a1e1ad4dd1c6a8742ae` |
| [execution-chain.html](workflow-ch07-execution-chain-20261010-214548/execution-chain.html) | `b6231c63576331429b7f3101e9590ea8222b8560745452b97155b1f8d6f064ba` |

许可证保留 [ARCHIFY-LICENSE.txt](ARCHIFY-LICENSE.txt)，生成 HTML 内嵌字体保留其许可。按用户持续授权完成本章验收后提交并推送 `origin/main`；GitHub 提交链接在交付消息中提供。
