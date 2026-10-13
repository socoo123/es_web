# ch24 重构验收记录

2026-10-13。本轮只重构 ch24，并更新对应主页卡片及 STATUS。用户指定 AGENTS / CHAPTER_STANDARD，沿用 880px 阅读列、双主题、七段结构、目录、上下课与已读进度，复用共用图解 CSS/JS；没有修改其他章节或共用控制逻辑。

## 内容与实验

- 锚定 ES v9.4.0，固定提交 `2e8528e92361c3399724226deaf2b46f933e925b`，依赖表 Lucene 10.4.0。已人工读取相关方法；`review/ch24-source-review.json` 另核对 26 文件 / 64 具体范围、源 checkout clean、引用行号和工作区源码与该提交字节一致。字节/行号自动核对本身不代替语义走读。
- 核心修正：safe commit 与 latest commit 区分；操作分支的历史/lease 条件；目标临时本地 Engine 与正式网络入口的 skip 区分；源操作历史来自 Lucene；先 initiateTracking 再采样 endingSeqNo；DONE、POST_RECOVERY、active 路由启动分开；isSame hash/writer UUID 与按段比较；文件计划的快照辅助；文件限速和操作资源约束区分。
- 快照按匹配文件复用引用，每份成功快照有完整清单；新增文件可内联，增量数不等于数据 blob 上传次数；删除按存活引用，注销仓库只移除注册。fs 默认未配置 path.repo 的失败与成功配置环境分开，注册失败阶段可能影响元数据是否已登记，不要求所有仓库为空。
- 保留全部旧 20 个实验 ID 和 `ch24-peer-recovery` 七步机制 ID。3 组 / 57 张卡：3 前提、A17、B13、条件 C14、10 清理。GET/HEAD 无请求体，顺序与章节槽一一一致；写请求只针对本章三个索引、专属仓库/快照，或点名 allocation explain。1P0R、auto-expand=false、strict keyword mapping 明确，B 禁止周期 refresh。
- A：404 干净起点、等待恢复完成、EMPTY/EXISTING 来源、单节点副本路由与 explain、恢复零副本。B：单写入、GET/SEARCH 对比与本地提交账，不能推算未来 peer 操作量。C：仓库检查后按条件继续 s1/s2 SUCCESS、文件统计、删除 s1、独立恢复 s2、等待与数据/来源对照。清理点名快照、三个索引和仓库注册，再用 HEAD/GET 404 确认重做条件。

## 真实 ES：未实测

本轮实际执行仓库正常 `docker compose -f docker/docker-compose.yml up -d`，官方 ES 9.4.0 容器随后 exited / exit 1。初始化 `Elasticsearch.setCoredumpFilter` 因 `/proc/self/coredump_filter` 不存在抛 `NoSuchFileException` / `Could not set coredump filter`，9200 探测无法连接。

`review/ch24-es-runtime.json` 保存本次启动时间、镜像/容器状态、实际错误和 HTTP 探测，`responsesSynthesized=false`。所有真实 API 首次运行、清理后重做、multi-node PEER、文件/操作两分支、快照注册/增量/restore 均未执行；操作卡内容是条件预期，不是响应记录。独立浏览器检查会明确 abort ES 深链自动请求。没有合成响应、修改管理策略或篡改 ES 运行文件来报告成功。

## 官方 Archify：原生门禁与 HTTP 分开

两图使用官方 Archify 3.0.1、workflow v2、zh-CN / showcase / trace。每个语义节点有固定源码引用，生成命令携带真实 ES 源 repo root。只修改 JSON，再完整 finalize；生成 HTML 未手改。许可复用 `.archify/ARCHIFY-LICENSE.txt`，保留 HTML 字体许可。

| 图 | 当前 candidate SHA-256 | 当前 HTML SHA-256 | 当前 finalize 收据 |
| --- | --- | --- | --- |
| peer-paths | `f55c4636b5339973ec618e7ffdf4a71728e44ec28f161194d1c532c5fae87c25` | `e443f999de4bc38da927282a8943d6c377281c976ac650cc0d99487cee0c1b53` | `.archify/workflow-ch24-peer-paths-20261013-133220/review-2/peer-paths.finalize.json` |
| snapshot-files | `9f61d821df46969be1867b5acd21b90a3085d614df8dd7dd0526e318fab780a9` | `3e546c7a0d02bb478ccc279a848da9cac48b7b9d5a517900cc9a07f2b7a1f3ec` | `.archify/workflow-ch24-snapshot-files-20261013-133220/snapshot-files.finalize.json` |

两图当前 validate / deliver / strict check **pass：showcase 9/9，零错误/警告**。原生 browser-check **fail**：其私有 `file://` 快照导航返回 `net::ERR_BLOCKED_BY_ADMINISTRATOR`，因此 finalize **整体 fail**。HTTP 结果和视觉审阅不能覆盖原生状态。update noticeRequired=false。

- 快照图初次共享路由诊断为 ambiguous-corridor；两次局部路径修复后检查稳定 layout receipt，按测得的不足转段间距修正入口方向，完整 finalize 后通过静态门禁。保留初始 JSON 和 `review/ch24-snapshot-layout-failure.json`，后者是第三版生成前的实际诊断；不是最终通过收据。
- 恢复图首版 1440×900 的最小 SVG 文字 5.783px、普通节点 6.609px，未达到标准。`review/ch24-desktop-text-failure.json/png` 留证；仅压缩 JSON 节点高度与纵向间距，同目录重新 finalize 到 review-2，保留旧收据。修复后 HTTP 最小 SVG 6.330px、普通节点 7.234px；快照图分别 6.476px / 7.401px。原生浏览器环境错误不属于图源修复成功。

## 独立 HTTP 与实际视觉

`review/ch24-http-review.json` pass，绑定当前章节、JS、图源/HTML SHA；无未处理 JS 错误或异常静态 HTTP 响应。

- 独立两图：1440×900、1600×1000、1920×1080、2048×1320，浅深主题；SVG 文字与普通节点达到桌面阈值，说明卡完整。
- 章节：1920、1440、1024、768、390、320px，各浅深主题；正文、图框、图注、表格、实验与页尾同列，桌面最大 880px，边界差≤1px，整页/iframe 无横溢、嵌入无需内部纵向滚动，所有节点实际矩形在画布内。测量后图高 peer 1120px / ≤800px 650px，snapshot 980px / ≤800px 620px。
- 真实交互：节点探索及固定源码、关闭、Enter/Escape、暂停后外层目标图重播及键盘重播、展开独立图、主题同步、目录跳转、已读进度；七步上一/下一/左右键/播放暂停/重置，所有快照 marker 唯一、SVG 文字包含。
- 57 个真实操作卡逐项打开控制台，核对 method/path/body；请求自动流量明确拦截，因此此项不声称 API 已运行。endpoint、认证别名、raw marker、`/es_web/` 前缀下资产/iframe/深链及 `.nojekyll` 均核对。
- reduced motion：Archify 静止、动效按钮禁用、外层重播仍静止；机制不自动播放而手动步进可用；页面无 smooth scroll。
- `review/ch24-scroll-review.json` pass：390/320 浅深主题，长表格与旧机制 SVG 仅自身容器滚动，整页保持包含。
- 已通过 view_image 实际查看 **7 张最终联系表，覆盖 24 张最终双主题章节/图解截图与全部 7 个机制步骤**；另查看首版文字失败截图。`review/ch24-visual-review.json` 明确记录实际审阅范围与所有图 SHA。联系表生成器自身只报告 capture-only，机制捕获自身不报告已视觉审阅。
- 手机 Archify 是完整概览，细字需节点探索或展开缩放，必要解释也在正文/图注。源码表与旧 SVG 横向滚动可用；播放器标题在窄屏省略，控制与解说可见。图中节点/分支/文字无重叠或裁切；表格右侧列与旧 SVG 右侧通过局部滚动访问。

## 站点与复现

`node tools/check.mjs` pass：30 正式页 / 715 操作 / 22 机制。`node --check experiments/ch24.js`、`node tools/figwidth.mjs chapters/ch24.html experiments/ch24.js`、Git whitespace check 通过。最终源、产物、原生/HTTP/视觉记录与限制由 `review/ch24-artifacts.json` 绑定。

从仓库根目录运行（官方 CLI 与源码 checkout 路径按环境替换）：

```bash
node /workspace/shared/skills/archify-3.0.1/archify/bin/archify.mjs finalize workflow .archify/workflow-ch24-peer-paths-20261013-133220/candidate.json .archify/workflow-ch24-peer-paths-20261013-133220/peer-paths.html --repo-root /workspace/scratch/es-v9.4.0 --quality showcase --out-dir .archify/workflow-ch24-peer-paths-20261013-133220/review-2 --json
node /workspace/shared/skills/archify-3.0.1/archify/bin/archify.mjs finalize workflow .archify/workflow-ch24-snapshot-files-20261013-133220/candidate.json .archify/workflow-ch24-snapshot-files-20261013-133220/snapshot-files.html --repo-root /workspace/scratch/es-v9.4.0 --quality showcase --json
python .archify/review/ch24-source-audit.py
python .archify/review/ch24-http-review.py
python .archify/review/ch24-scroll-review.py
python .archify/review/ch24-mechanism-review.py
python .archify/review/ch24-visual-sheets.py
node tools/check.mjs
```

浏览器脚本使用本机 Chromium、Playwright 和临时同源 HTTP；后两项只生成截图，重跑后需要实际审阅与更新视觉哈希，不能直接重用旧“已审阅”状态。图源变化后完整 finalize 另选新 revision 收据目录，不覆盖旧图的浏览器证据。finalize 在当前云策略下仍应如实失败。

阅读稿可在明确以上限制后交付；GitHub push 与 Pages 发布另行确认，均不作为真实 ES 实验的替代。
