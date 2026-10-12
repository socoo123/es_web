# 第十六章重构验收

本轮日期：2026-10-12；记录时间：2026-10-12T08:08:20.058585+08:00（Asia/Shanghai）。范围为 ch16、两幅本章图、实验与验收记录、STATUS。已读 AGENTS→STATUS→PLAN→CHAPTER_STANDARD→CLAUDE；未重读 tutorial、未启用代理。共享样式/控制脚本与其他章节未改；预先存在的 .gitignore 改动不纳入本轮提交。

## 内容与源码

锚定 ES **9.4.0 / Lucene 10.4.0**。真实匿名单节点 localhost:9200 的 build_hash 与固定提交 `2e8528e92361c3399724226deaf2b46f933e925b` 一致。[源码审计](review/ch16-source-review.json)通过 **13 文件 / 30 精确区间**：clean checkout `/tmp/es-ch15/es-v9.4.0`，引用字节与提交对象、行区间一致。只查看本课目标文件。官方[分页说明](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/paginate-search-results)与[profile 观测范围](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/search-profile)补充通用 API 条件，不替代固定源码。

七段结构，约 3800 中文字符，3 个可验证目标、折叠目录、3 个图/机制跳转、5 道折叠题、4 条陷阱与同口径速记。保留原 14 稳定 ID 和 ch16-qtf 七步播放器。正文、图源、动画解说、实验预期与问答同步修正：

- 普通候选 from+size 是窗口/上限，限定 size>0、无 scroll/rescore/rank/collapse/suggest。实际受 reader 与匹配数量限制；维护 Top-k 不表示只扫描 k 文档。本课实际分布 12/9/9，size=10 上限合计 28，最终 hits=10；动画 30→10 和 3/5/2 明确是假设足量的虚构示例。
- SEARCH 默认选择目标分片组，每组选一份拷贝，可受 routing/can-match 影响；单节点不等于单分片。各片 EXTERNAL 读者不是全索引同一事务时刻。doc 是当前分片读者空间的 Lucene 文档号，非 segment 内编号或 _id。
- 受每节点并发限制的扇出不等待全部响应，但可以排队/同步回调，不保证立即释放线程。先 consumeResult 完成再倒数；FetchSearchPhase.run 经 context.execute 调度 reduce，不固定最后网络回调线程。
- Query 排序值、聚合、统计等不能压成固定小元组；_source:false 是请求选项，Fetch 仍可能执行。size=0 本例不取 hits，聚合 sum=465 仍执行。
- 超窗实际 HTTP 400，顶层 search_phase_execution_exception/all shards failed，内层 illegal_argument_exception；分组后的 failed_shards 数组长度不是失败片数。等于窗口可成功返回空页；filter_path 改为保留 hits.hits，避免空数组被子字段过滤掉。
- 普通无 rank/kNN 的单分片 QTF 可合并 Query/Fetch；hasKnnSearch 分支改 DFS，非所有向量查询的总括。批量 Query、can-match 有条件；DFS 收跨片统计，其收益不能作绝对性能判断。
- from/size 与无 PIT search_after 也有临时上下文；跨请求保留读者另用 PIT/scroll。search_after 传完整末项 sort，保持 from=0；本例唯一 n、冻结数据不模拟并发变化。
- refresh=-1 只关周期刷新；NRT 组先删除旧 nrt 并 refresh→基线0→未刷新写→GET→count0→refresh→count1。排除其他刷新/恢复等操作；同次重复写入与干净清理后的重做分开解释。

## 实验与真实 ES

**4 组 /29 张操作卡**：A6 准备、B10 排名与翻页、C7 可见性、D3 单分片、清理3。显式 standard / strict / stored source / standard analyzer /整数 n、3 主片0副本、auto_expand=false、无默认/最终管道、refresh=-1、max_result_window=10000；限定本索引健康等待。完整顺序、预期错误、首次/重复、C 组基线与两资源点名清理写明。

[两轮实际响应与验证](review/ch16-es-review.json) /[可复现脚本](review/ch16-es-review.py)：**每轮29请求通过，清理后重建重做通过**。核对版本/构建、单节点、设置、健康、12/9/9、全局10 hits、3个 searches、size1一个 fetch、source-off 仍 fetch、size0聚合、超窗层次、合法空页、21..30最后一页、search_after 1..5→6..10、GET可见/count0→1、单片第二篇/profile两段。各 fetch.load_stored_fields_count 本例合计10，next_reader_count不是文档数。两索引最终 HEAD 均404。

初步实测与 filter_path 修复前响应保留在 [initial](review/ch16-initial-responses.json) /[before-filter-fix](review/ch16-es-before-filter-fix.json)。最终 requestIdentityVerified=true，记录执行时 experimentSha256 与当前 reviewedExperimentSha256；后续只改解说/快照，不改变已实测请求。未声称实测多节点传输/副本切换、部分失败、DFS/kNN/rank、PIT并发一致性或同次重复建索引/写入；这些范围按源码和公开 API 条件讲解。

## 官方 Archify 原生门禁

使用[官方 Archify 3.0.1 技能](https://github.com/tt-a1i/archify/blob/v3.0.1/archify/SKILL.md)。已读 defaults/repository、Workflow v2/common schema、指定 example、viewer/delivery、布局/viewport 契约。两幅 Workflow v2 首次即附固定源码证据及真实 checkout / --repo-root，只改 JSON 并完整 finalize；HTML 未手改，复用 MIT 许可，保留生成字体许可。

| 图 | candidate SHA-256 | HTML SHA-256 | 当前原生收据 |
|---|---|---|---|
| qtf-journey | `3e5a7e7fc2913be64e93e59233ea2422b30180ae93f1294175968e4b8b6adcce` | `2ed2f83193ea9e038b36d1908780a636fe756a5bebed68b3b2e9101abfd163fd` | review-2 |
| page-window | `fa2e67c7c47eaeeab3a7dd01ef61dc7fb54da2652740b6aedea2d90d93efaff4` | `329ddd923a2010d8731ed7bf969847acdd635b0d1c577194eb67193317bfb46d` | review-2 |

两图 validate /deliver /strict check 均 **showcase9/9、0 errors/warnings、provenance current**；原生 browser-check 与 finalize整体均 **PASS**，update.noticeRequired=false。初版图源/收据保留，修正普通 Fetch 精确引用及窗口默认依据后使用 review-2。page-window 的 gate→local 两折绕行收到可选审阅提示：浅深桌面/嵌入已实际查看，绕行在空白走廊，无交叉或含糊分支，不需要布局修复。原生 visualReview=not-requested 不当作人工审阅；人工审阅独立记录。

## HTTP、视觉与交互

[独立 HTTP](review/ch16-http-review.json) PASS，绑定当前页面/注册表/JSON/HTML。[局部滚动](review/ch16-scroll-review.json) PASS；[视觉范围](review/ch16-visual-review.json)与[七步快照](review/ch16-mechanism-review.json)独立记录。使用临时本地 HTTP、Python Playwright、已安装 Google Chrome；控制台深链默认会自动执行，浏览器验收对 localhost:9200 显式 abort，不发送也不伪造 ES 响应。真实 API 单独执行。

- 独立两图×1440/1600/1920/2048×浅深：页面无横向溢出、说明卡无截断，最小 SVG/普通节点投影分别 qtf 6.189/7.073px、window 7.265/8.303px。
- 章节×1920/1440/1024/768/390/320×两主题：阅读列≤880px，各区左右差≤1px，页面/iframe无横向溢出，主 SVG所有节点完整。实测 iframe 高度 qtf820/700、window800/700（桌面/≤800），并检查内容不垂直溢出。
- 节点探索/固定源码/关闭、展开独立图、主题同步、暂停→外层重播/Enter、目录锚点、已读、七步前后/重置/播放/键盘、29条实际控制台导航请求的 method/path/body、endpoint/auth alias/raw 与 /es_web/前缀均通过；未处理 JS 错误和静态 HTTP 失败为空。
- reduced motion 优先，重播不覆盖系统偏好，旧播放器不自动播、手动步进保留；页面无平滑滚动。390/320源码表和旧 SVG 可在自身容器滚动。
- **实际查看24张图/章节截图与七步7张快照**。发现第2/5步底部说明贴边，调整快照方框高度，复看修复后的2/5步及机制桌面/手机浅深，重跑浏览器验证。手机图为完整概览，细字需探索/展开缩放；旧SVG局部滚动，长播放器标题窄屏省略但解说完整，不声称全部细字原比例清晰。

## 检查与复现

站点 **30正式页/575卡/22机制播放器**；Archify trace单列。node tools/check.mjs、node --check、figwidth、git diff --check与稳定ID/槽位一致性通过；.nojekyll 与静态路径保留。当前文件、收据和截图哈希绑定见 [ch16-artifacts](review/ch16-artifacts.json)。

```bash
node tools/check.mjs
node --check experiments/ch16.js
node tools/figwidth.mjs chapters/ch16.html experiments/ch16.js
ES_SOURCE_ROOT=/path/to/clean-es-v9.4.0 python3 .archify/review/ch16-source-audit.py
python3 .archify/review/ch16-es-review.py          # 两轮实际修改/清理本章资源
python3 .archify/review/ch16-es-review.py --validate-only
/path/to/playwright-python .archify/review/ch16-http-review.py
/path/to/playwright-python .archify/review/ch16-scroll-review.py
/path/to/playwright-python .archify/review/ch16-mechanism-review.py
# 图源重现用官方 finalize workflow candidate.json output.html --repo-root ... --quality showcase --json
# 已有浏览器证据后使用新的 --out-dir 保留历史收据。
```

按用户持续授权提交并推送 origin/main；交付时独立核对远端提交。Pages 部署完成另行核验，不把本地检查等同线上已更新。
