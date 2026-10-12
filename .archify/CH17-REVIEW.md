# 第十七章重构验收

日期：2026-10-12；记录：2026-10-12T19:18:16.580343+08:00（Asia/Shanghai）。指定范围为 ch17、两幅本章图、实验、验收与 STATUS。已依次读 AGENTS→STATUS→PLAN→CHAPTER_STANDARD→CLAUDE；从本章既有 HTML/注册表出发，未重读 tutorial、未启用代理。共享 CSS/JS、其他章节与原有 .gitignore 改动不纳入本轮。

## 内容与依据

锚定 **ES9.4.0 / Lucene10.4.0**。本机匿名单节点9200版本/build_hash与固定提交 `2e8528e92361c3399724226deaf2b46f933e925b` 一致。[源码审计](review/ch17-source-review.json)为 **15文件 /43精确区间 PASS**：临时 clean sparse checkout固定revision；实际查看的本地 es-src目标字节与 git提交对象一致，行范围均有效。稀疏checkout未含Painless文件，审计直接验证本地已查看文件对提交对象；未把未检出的文件冒充已读取的clean工作树文件。图的所有sources通过官方 --repo-root门禁。

按七段结构重排上下文所有权、入口调度、三个查询字段、超时边界、PIT分页与源码导航。3目标、折叠目录/3图与机制跳转、5折叠题、4陷阱和一致速记。保留原18稳定ID及 ch17-context-lifecycle 六步机制；新增14卡，共3组32操作（A8/B7/C15/清理2）。

- 正常执行分支有 SearchContext；can-match可提前空返回，不保证每次创建或handler立即返回。9.4.0 private重载有reader参数，markAsUsed由异步包装持有；普通索引search executor、系统索引另选。
- 普通Query→Fetch可暂存ReaderContext；PIT/scroll跨请求保存reader引用。SearchContext.close释放注册资源，reader所有者引用移除不保证物理reader/句柄立即归零。
- originalQuery默认供高亮；Explain用rewrittenQuery，Profile观察执行查询树。标准/OR的quick brown在toQuery分析构造SHOULD，非Lucene rewrite才分词；无过滤可保持原query。
- timeout依赖检查点与默认200ms缓存相对时钟，不是全请求deadline。小数据不是“完全没有检查”；Query合并Fetch时清除查询超时检查。请求显式设置部分结果开关，避免配置层覆盖默认值。
- 旧500万循环真实400脚本保护，非200超时/429。新合法2万计算×3003文档先验证完整基线，后做1ms对照；仍不承诺各机器工作量阈值。
- PIT用最新pit_id和完整末项sort（含隐式_shard_doc）；新增真正第二页，换查询证明非结果缓存。不要写死_shard_doc，不把重开后含new的新PIT当旧视图。keep_alive后台清理、失败恢复/重建皆有条件。

## 真实ES与重做

[两轮响应/逐项验证](review/ch17-es-review.json)、[复现脚本](review/ch17-es-review.py) **每轮32请求 PASS**。匿名单节点，两个显式1主0副、auto-expand=false、strict/stored source/standard/integer mapping、无默认/最终pipeline、refresh=-1、request cache关闭的索引。索引限定健康与上下文统计，固定ID、显式refresh、别名随父索引点名清理。第二轮在第一轮清理后重建；最终两个索引及别名HEAD404。

两轮均确认：token quick/brown、validate查询表示、过滤别名只命中1，profile和explain含n过滤/高亮；count3003、脚本基线无超时；旧循环400含maximum statements，合法短查询200+timed_out=true，严格查询429/顶层search_phase_execution_exception、内层search_timeout_exception。基线 took为519/517ms；短查询为513/514ms，且total仍3003（检查在批次末触发，超时标记不保证每次一定丢文档）。不能把这一例的完整total推广为超时总数可靠。

PIT：本索引上下文0→1→0；第一页1/2，完整sort末项[2,1]，写new+refresh后旧第二页4、旧重搜1/2/4；同PIT查lazy得3，新普通搜索1/2/4/new。按每次最新pit_id传递，关闭succeeded=true/num_freed=1，关闭ID再搜404/search_context_missing_exception。

[原18卡初次响应](review/ch17-original-responses.json)与[33篇合法负载未触发的诊断](review/ch17-short-load-responses.json)保留，不当最终通过记录。最终requestIdentityVerified=true：实测请求与注册表一致，只按流程替换PIT ID与完整sort；代码中后续压缩为等价NDJSON生成函数/修正说明，经 --validate-only验证请求字节一致。本轮没有实测多节点、scroll翻页、取消、重试重建、并发故障或自动过期；这些是固定源码/官方API条件说明。未改集群设置、未制造响应。

## 官方Archify门禁

使用[官方3.0.1技能](https://github.com/tt-a1i/archify/blob/v3.0.1/archify/SKILL.md)；已读defaults/repository、Workflow v2/common schema、指定example、viewer/delivery与布局契约。两图首次附真实ES源码与 --repo-root，只改JSON，HTML未手改。复用 .archify/ARCHIFY-LICENSE.txt，保留HTML字体许可。

| 图 | candidate SHA-256 | HTML SHA-256 | 当前收据 |
|---|---|---|---|
| context-lease | `6727cd9618fa0e6e46d8920c10edc962639dd27f1fbde36a61b9a6c4012cd9a6` | `5666bad611aab9217bacaddc58d3c3bd2d6bf5bad316c650861e9ac778b8824c` | 根目录 |
| query-plan | `91edc020ce4b84256d28f16c073fdd626718bc5679f44376f883bf4aaa8d78e6` | `468bbda13d20c15e68687b0d38c77cef342030fbd6fd03b9f259e07ab89e47b2` | review-2 |

两图 validate/deliver/strict check均 **showcase9/9、0errors/warnings、provenance current**，原生browser-check与finalize整体均 **PASS**。update.noticeRequired=false。query初稿源码区间收紧并补operator构造依据后review-2；candidate.initial与原生旧收据保留。visualReview=not-requested属于原生流程；实际截图审阅单独记录。

## HTTP、视觉、交互

[HTTP](review/ch17-http-review.json) PASS；[局部滚动](review/ch17-scroll-review.json) PASS；[实际视觉审阅](review/ch17-visual-review.json)、[六步快照](review/ch17-mechanism-review.json)独立记录。临时本地HTTP、Python Playwright与已安装Chrome。控制台深链会自动运行，浏览器验证对localhost:9200显式abort，没有发送或伪造ES响应；真实API另行执行。

- 独立两图×1440/1600/1920/2048×浅深，说明卡无截断、页面无横向溢出。最小SVG/普通节点投影：context6.982/7.979px，query7.191/8.219px。
- 章节×1920/1440/1024/768/390/320×浅深，阅读列≤880px、左右边界差≤1px、全页/iframe无横溢、所有图节点完整。图高context820/query800，≤800宽均540；图内无垂直溢出。
- 探索/固定源码/关闭、展开、主题同步、暂停→外层重播/Enter、目录/已读、六步手动前后/播放/重置/键盘、32条真实控制台导航method/path/body、endpoint/auth alias/raw、/es_web/静态前缀都通过。JS未处理错误和静态HTTP失败为空。
- reduced motion优先，重播不覆盖系统偏好，机制不自动播/手动步进保留，页面无平滑滚动。390/320源码表与旧SVG局部横向滚动；3000篇NDJSON在卡片内340px垂直滚动，通过实测scrollTop。
- **实际查看26张独立/嵌入/桌面/390px/批量卡浅深截图，及六步完整快照**；部分用仅供审阅的拼图辅助。按审阅把手机图框700→540收紧、源码表右列最小宽260避免细长折行，复看修复图/表/批量卡。手机图是完整概览，细字需探索或展开缩放；旧SVG可局部滑动，手机播放器标题省略但解说完整。
- 初期控制台导航自动化等待不足，补齐页面落定/卡片就绪后通过；另一次Chrome启动超时，30s bounded重试及最终检查通过。未更改浏览器管理政策，不把早期失败记为成功。

## 检查与复现

站点30正式页 /589操作卡 /22机制播放器；Archify trace另计。站点check、修改JS语法、figwidth、git diff --check、18稳定ID与32唯一有序槽位、.nojekyll、路径全部PASS。图与当前文件/收据/截图SHA绑定在 [artifacts](review/ch17-artifacts.json)。

```bash
node tools/check.mjs
node --check experiments/ch17.js
node tools/figwidth.mjs chapters/ch17.html experiments/ch17.js
ES_SOURCE_ROOT=/path/to/clean-es-v9.4.0 python3 .archify/review/ch17-source-audit.py
python3 .archify/review/ch17-es-review.py              # 两轮实际操作并清理本章资源
python3 .archify/review/ch17-es-review.py --validate-only
/path/to/playwright-python .archify/review/ch17-http-review.py
/path/to/playwright-python .archify/review/ch17-scroll-review.py
/path/to/playwright-python .archify/review/ch17-mechanism-review.py
# 两图重现：官方 finalize workflow candidate.json output.html --repo-root ... --quality showcase --json
# 图源编辑后完整重新finalize；已有browser证据需新的--out-dir。
```

按持续授权提交并推送origin/main；远端提交与Pages完成状态交付时独立核对，不把本地验收等同线上更新。
