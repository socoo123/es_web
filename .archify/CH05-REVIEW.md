# 第五章交付与验证记录

第五章按 CHAPTER_STANDARD 重构，保留七段式、上下课链接、已读进度与全部 8 个原实验 ID；新增 4 张验证卡，总计 2 组 / 12 张操作卡、2 幅交互图、1 条有限 trace，无 ESFLOWS 机制播放器。配置契约图使用静态 Architecture，动态更新图使用 Workflow v2。

源码固定到 Elasticsearch v9.4.0 提交 `2e8528e92361c3399724226deaf2b46f933e925b`，仓库 `https://github.com/elastic/elasticsearch.git`。所有语义节点携带实际查阅的文件 / 行号；正式 CLI 的首次生成即传入真实源码 checkout 作为 `--repo-root`。图概括配置读值与动态更新，不是完整的协调协议或线程时序；必要条件与执行边界在正文、图注及说明卡重复交代。

## 分项验收

| 项目 | 当前结果 |
| --- | --- |
| 内容依据 | 已核对 v9.4.0 固定版本源码；NodeScope、Final、准备 / 执行边界、覆盖与回退、transient、Filtered 勘误见 STATUS |
| 结构 / 语法 | `node tools/check.mjs`、`node --check experiments/ch05.js`、`git diff --check` 均通过；全站注册表为 418 张操作卡 / 22 个机制播放器 |
| Archify validate / deliver / strict check | 两图 showcase 9/9、零错误 / 警告，源证据 verified，delivery 哈希匹配 |
| Archify 原生 browser-check | **失败**：管理员禁止私有 `file://` 快照，`ERR_BLOCKED_BY_ADMINISTRATOR`；finalize 整体保留 fail，未修改政策 |
| 独立 HTTP Chromium | **通过**：两图各 1440 / 1600 / 1920 / 2048px、浅深主题；章节 1920 / 1440 / 1024 / 768 / 390 / 320px、浅深主题；页面 / iframe 无横向溢出，章节边界差 ≤1px，桌面最大列宽 880px |
| 交互 | 节点源码探索 / 关闭、展开、主题同步、暂停后外层重播、键盘重播、目录 / 已读、12 张真实操作卡到控制台的方法 / 路径 / 请求体、端点 / 认证别名 / raw 标记、Pages 前缀、reduced motion 均通过；没有模拟 ES 响应 |
| 静态路径 | 本章相对资源与锚点、课间导航、iframe、`/es_web/` 前缀与控制台深链有效，`.nojekyll` 保留；无未处理 JS 错误或 HTTP 资源失败 |
| 真实 ES API | **未执行首次运行与清理后重做**：9200 无连接；当前云环境缺 `/proc/self/coredump_filter`，已有 ES 9.4.0 启动日志确认运行时阻塞。源码已核对、API 未实测；400 / 健康 / 清理预期不能据此算作新实测 |

独立 HTTP 记录绑定当前章节、实验、JSON 与 HTML SHA-256，见 [review/ch05-http-review.json](review/ch05-http-review.json)；重现脚本为 [review/ch05-http-review.py](review/ch05-http-review.py)，需要环境提供 Python / Playwright / Chromium。这些检查独立于 Archify 原生 browser-check，不覆盖其失败状态。

## 视觉审阅

实际查看两图独立查看器、最终嵌入的浅深截图，章节桌面 / 390px 手机首屏，手机图框、长请求实验卡与源码表格。动态更新图初稿横向过宽，已在 JSON 中改成纵向步骤，重新 finalize 并保留旧原生收据；当前原生检查的投影文字硬门槛通过。图高依实际内容测量，桌面为 800 / 1020px，≤800px 为 560 / 780px。

手机图用作结构总览，正文保留完整机制说明，细节可以节点探索、放大或展开查看；源码表格在自身容器内横向滚动，实验路径能换行。截图在主题颜色过渡完成后采集；采集成功与人工视觉审阅分别记录。审阅仅覆盖第五章，共用 CSS / JS 未改动。代表截图位于 `review/ch05-*.png`。

## 重现图解生成

使用干净的 ES Git checkout，`git rev-parse HEAD` 须等于上述固定提交；普通或包含全部所引 sources 的 sparse checkout 均可。不要用教程仓库冒充 ES 源码。修改 JSON 后重新完整 finalize；已有浏览器证据时指定新的 `--out-dir` 保留旧收据。生成 HTML 未手改，字体许可保持内嵌，Archify 许可复用 [ARCHIFY-LICENSE.txt](ARCHIFY-LICENSE.txt)。

```bash
node /path/to/archify/bin/archify.mjs finalize architecture \
  .archify/architecture-ch05-setting-contract-20261010-174932/candidate.json \
  .archify/architecture-ch05-setting-contract-20261010-174932/setting-contract.html \
  --repo-root /path/to/elasticsearch --quality showcase --json

node /path/to/archify/bin/archify.mjs finalize workflow \
  .archify/workflow-ch05-dynamic-update-20261010-174932/candidate.json \
  .archify/workflow-ch05-dynamic-update-20261010-174932/dynamic-update.html \
  --repo-root /path/to/elasticsearch --quality showcase --json

```

本云运行时需使用技能支持的 `ARCHIFY_CHROME_NO_SANDBOX=1` 启动容器内 Chromium；这不改变文件 URL 管理政策，原生浏览器门禁仍失败。无需为静态站点安装新的仓库依赖。

## 当前产物、哈希与原生收据

### setting-contract

- 类型：`architecture`
- 图源：[architecture-ch05-setting-contract-20261010-174932/candidate.json](architecture-ch05-setting-contract-20261010-174932/candidate.json)
- HTML：[architecture-ch05-setting-contract-20261010-174932/setting-contract.html](architecture-ch05-setting-contract-20261010-174932/setting-contract.html)
- 图源 SHA-256：`111ac6126438c83068bb38bc66c9712c49f8900f1255b845e27e5ce31150a4f3`
- HTML SHA-256：`19f592993dac0e9ca62a7b2842c5e6e2f4ed2b5100f00114f93ff17c1c63340c`
- 当前原生摘要：[architecture-ch05-setting-contract-20261010-174932/setting-contract.finalize-summary.json](architecture-ch05-setting-contract-20261010-174932/setting-contract.finalize-summary.json)
- 完整收据：[architecture-ch05-setting-contract-20261010-174932/setting-contract.finalize.json](architecture-ch05-setting-contract-20261010-174932/setting-contract.finalize.json)
- Delivery：[architecture-ch05-setting-contract-20261010-174932/setting-contract.delivery.json](architecture-ch05-setting-contract-20261010-174932/setting-contract.delivery.json)
- 原生 browser_evidence：`failed`；独立 HTTP：`passed`；视觉审阅：已实际查看上述范围。

### dynamic-update

- 类型：`workflow`
- 图源：[workflow-ch05-dynamic-update-20261010-174932/candidate.json](workflow-ch05-dynamic-update-20261010-174932/candidate.json)
- HTML：[workflow-ch05-dynamic-update-20261010-174932/dynamic-update.html](workflow-ch05-dynamic-update-20261010-174932/dynamic-update.html)
- 图源 SHA-256：`6f9698d8887c282afcd9a87d1f6c6fdf51c80f253ff91b26421943596c0864b7`
- HTML SHA-256：`f9b48ea2e549bbaff2ff9068a41dd7773106110348ffd3672a5ee30094e65305`
- 当前原生摘要：[workflow-ch05-dynamic-update-20261010-174932/review-2/dynamic-update.finalize-summary.json](workflow-ch05-dynamic-update-20261010-174932/review-2/dynamic-update.finalize-summary.json)
- 完整收据：[workflow-ch05-dynamic-update-20261010-174932/review-2/dynamic-update.finalize.json](workflow-ch05-dynamic-update-20261010-174932/review-2/dynamic-update.finalize.json)
- Delivery：[workflow-ch05-dynamic-update-20261010-174932/dynamic-update.delivery.json](workflow-ch05-dynamic-update-20261010-174932/dynamic-update.delivery.json)
- 原生 browser_evidence：`failed`；独立 HTTP：`passed`；视觉审阅：已实际查看上述范围。

机器可读当前身份与哈希另见 [review/ch05-artifacts.json](review/ch05-artifacts.json)。旧 Workflow 收据保留在图目录根，当前修订收据位于 `review-2/`；不要把旧哈希对应的检查冒充当前产物检查。
