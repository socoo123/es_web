# 第二十章重构验收

2026-10-12（Asia/Shanghai）。按 AGENTS → STATUS → PLAN → CHAPTER_STANDARD → CLAUDE 执行，只处理 ch20、其图源/产物/验收和 STATUS；未重读 tutorial、未使用子代理。复用共享880px布局/主题/重播控制，没有改共享 CSS/JS 或其他章节；已有 .gitignore 修改不纳入本次提交。

## 内容与依据

版本 **ES 9.4.0 / Lucene 10.4.0**，单节点真实 build_hash 与固定源码提交 `2e8528e92361c3399724226deaf2b46f933e925b` 一致。[源码审计](review/ch20-source-review.json)：**17文件 / 25精确区间 PASS**，本课目标源码已读，链接区间有效、本地bytes与干净固定checkout的git对象一致。[Lucene固定源码](review/ch20-lucene-source-review.json)另记10.4.0原文件哈希/公式/参数/长度解码依据。

保留七段结构，正文围绕窗口职责、源码、手算、Legacy与字段统计、两个Explain、业务分/排序、每片rescore重排；3个目标、折叠目录与跳转、5道折叠问答、4条陷阱和速记相互一致。保留原12稳定实验ID和七步旗舰机制，扩为3组30卡（A12/B12/C5/清理1），2交互图/2有限trace。

主要校正：

- 分片 Query 的局部候选仍要协调全局归并；Fetch可计算Explain并补rescore说明、加载所选hit，不据解释重选窗口。
- 浏览器不会发送GET body；原Explain卡真实400缺query，稳定ID改POST后200。指定文档存在而不匹配200，缺失404；非realtime读者。
- 默认内置BM25仍Legacy，boost2.2对应k1+1；统一倍数不改次序仅限同参数纯BM25。Deprecated不等于已改默认；饱和仍增长且堆词可能改变长度。
- N为字段docCount、avgdl为字段总频/docCount，缺title文档未进入本例统计。c长2使N3/n2/avgdl2涨分，缺title的d增加索引篇数但不改变本例分数。旧更新/删除版本可能暂留段统计；精确重做应点名删索引再建。
- 单_score desc可被buildSort优化成默认TopScore，本例不返回sort数组；views字段sort用字段键，track_scores补分不改键，其他特殊sort不可一概归为业务字段Doc Values。
- function_score乘views可翻盘、乘零可失去高名次；replace仍以query限制匹配集合，同常量分并列；multiply/replace均受max_boost约束。
- rescore每片窗口，允许无sort或_score desc，普通views或_score asc拒绝；源码另有升序_shard_doc tie-break条件，本章未实测PIT。窗口外仍乘query_weight，设1才保持初分。
- 同读者/查询/统计的单片普通search和独立Explain可对齐；DFS、多片、search rescore、过滤或读者差异不能笼统说同一数值树。

## 真实 ES 与重复性

[真实API](review/ch20-es-review.json)、[复现脚本](review/ch20-es-review.py)：**两轮每轮30实际注册请求 PASS**，method/path/body逐项一致；第二轮从第一轮点名清理后的空索引开始。**13条补充真实观察 PASS**。最终HEAD本课索引404；只操作tut-l20-bm25，不修改集群配置，没有模拟响应。

创建显式1主0副/auto-expand=false、stored source、strict、title standard/BM25/norms/词向量、views integer/Doc Values；关闭周期refresh/request cache、无default/final管道。局部健康green，固定ID bulk refresh=true。mapping响应省略默认true的norms与Doc Values，Explain dl及实际字段排序另作行为证据；词向量API总频键为sum_ttf。预测/请求/参考实际响应分开，点名清理、重复创建400/重复bulk updated200/重复清理404与完整重做写入正文。

关键实测：

- 初始词向量a:es/tutorial频次1/1，b:es2，字段docCount2/sum_ttf4，DF2/1。单词b/a=0.25069216/0.18232156，双词a/b=0.8754687/0.25069216。Explain boost2.2/n2/N2/k1=1.2/b=.75/dl=avgdl2，树值与_score相符。
- size1命中2只返回a及一棵树；POST指定a同分，tutorial指定b为200 matched=false，missing为404无explanation。
- weight2分数翻倍；views乘积b≈25.069216/a≈8.754687；仅b零权重a先/b0后；replace两篇同分2。views排序b/a、sort100/10、_score=null；track_scores补相关性分却仍b/a。单_score desc按相关性a/b、无sort数组。
- rescore window1未覆盖a，仍b/a；window2让a≈4.559665翻盘，Explain含二次贡献。显式_score desc成功且无sort数组，views排序400；普通请求恢复初始分数，无持久配置变化。
- c含title且长2：n2/N3/avgdl2，单词b≈0.646255、a≈0.4700036；d缺title仍N3、a分数不变。
- 补充query_weight2/window1：窗口外a也变≈0.36464313，b≈0.5013843；_score asc+rescore400。未刷新写入成功201、realtime GET found=true、Explain404；显式refresh后Explain200 matched=true。创建/写入/删除重复语义确认。

[原12卡响应](review/ch20-original-responses.json)仅作原卡审计，已经清理；GET卡400不当作当前实验通过。采集后验证器最初假定mapping会回显默认true、词向量键为sum_total_term_freq、单_score desc会带sort数组；按真实响应与源码修正这些断言及页面预期，复用已采集的60条真实请求完成验证，补充请求另实际执行。没有将验证器失败隐藏为API失败或成功。

多节点DFS/PIT tie-break、其他rescorer、复杂评分模型、长文档norm量化对照、压力与性能未实测，仅据固定源码说明适用条件。

## 官方 Archify 门禁

使用[官方Archify3.0.1技能](https://github.com/tt-a1i/archify/blob/v3.0.1/archify/SKILL.md)，已读authoring defaults、repository authoring、Workflow v2/common完整schema、指定example、viewer和delivery修复契约。首次附固定源码并传真实checkout --repo-root；只改JSON，通过完整finalize生成，不手改HTML。复用ARCHIFY-LICENSE.txt，HTML字体许可保留。

| 图 | candidate SHA-256 | HTML SHA-256 | 当前收据 |
|---|---|---|---|
| ranking-window | `4ac9d8436085c12df2a8fa0dd30a963f621b0168a84cb23dbb202aebfa66e987` | `2a4262a04c2ea5058e3ba739133ad1c1739ad96ba36e4f5126024a75e48efee3` | review-3 |
| explain-entries | `031cb8ec6d1c2b15421ae3bb6461761d975d8c5301dd5a9b77130b5d29f8a250` | `31b82f6c9c3be7499290757e7dc3c0c4f37c6211bbf713c06ef2e9b0afe65690` | 根目录 |

两图validate/deliver/strict check均 **showcase9/9、0 errors/warnings、provenance current**；原生 **browser-check与finalize整体PASS**，update.noticeRequired=false。ranking的review-2补评分条件/单分数优化，review-3补Fetch实际加载源码；旧candidate/原生收据/HTTP记录与截图保留。原生visualReview=not-requested是自动门禁状态；实际审图单列如下。

## HTTP、交互与实际截图审阅

[最终HTTP](review/ch20-http-review.json)、[局部滚动](review/ch20-scroll-review.json)、[七步捕获](review/ch20-mechanism-review.json)均PASS；临时本地HTTP + Python Playwright + 本机Chrome。控制台深链会自动执行，浏览器验收显式abort ES端点请求；真实API独立执行，没有伪造响应。

- 两图独立1440/1600/1920/2048 ×浅深，无横溢、说明卡完整。最小SVG/普通节点文字投影：ranking7.0455/8.052px，explain6.58984/7.53125px。
- 章节1920/1440/1024/768/390/320 ×浅深，桌面阅读列≤880px，标题/正文/图框/图注/表格/实验/尾左右边界差≤1px。整页/iframe横溢为零，节点完整且iframe无垂直裁切。图高桌面790/900px，≤800px540/620px。
- 探索固定源码/关闭、展开、主题同步、暂停→外层重播/Enter、目录/已读、七步前后/播放/重置/键盘、30控制台导航及method/path/body、endpoint/auth/raw、/es_web/前缀路径全部通过；未处理JS错误与HTTP失败为空。
- reduced motion优先且重播不覆盖系统偏好；机制无自动播、可手动步进，页面无平滑滚动。390/320源码表与旧SVG仅在自身容器横滑。
- **实际查看7张拼图，覆盖24张最终独立/嵌入/桌面/390px/实验/表格/双主题截图与全部7步完整快照**，另看ranking浅色独立图和Explain深色手机图。无路径交叉/遮挡；两条Explain请求互不连接，必需解释在图注。手机图是概览，细字需要探索/展开缩放；机制标题手机省略，步骤、控制和解说可读。截图生成没有替代实际审阅。

[实际审阅绑定](review/ch20-visual-review.json)及[最终文件哈希](review/ch20-artifacts.json)记录当前证据；图源/HTML与原生收据可复现。

## 结构、复现与交付

node tools/check.mjs：30正式页 / 635实验卡 / 22机制播放器 PASS；修改JS的node --check、figwidth、git diff --check、原12ID/30有序唯一槽位、GET/HEAD无body及.nojekyll PASS。Archify trace单列，不计入ESFLOWS播放器数量。

```bash
node tools/check.mjs
node --check experiments/ch20.js
node tools/figwidth.mjs chapters/ch20.html experiments/ch20.js
ES_SOURCE_ROOT=/path/to/clean-es-v9.4.0 python3 .archify/review/ch20-source-audit.py
python3 .archify/review/ch20-es-review.py                 # 空本课索引开始，执行两轮与补充，再清理
python3 .archify/review/ch20-es-review.py --validate-only # 复核现有请求证据与资源HEAD
/path/to/playwright-python .archify/review/ch20-http-review.py
/path/to/playwright-python .archify/review/ch20-scroll-review.py
/path/to/playwright-python .archify/review/ch20-mechanism-review.py
/path/to/pillow-python .archify/review/ch20-visual-sheets.py # 只生成拼图
python3 .archify/review/ch20-bind-artifacts.py             # 实际查看后才可更新绑定
# finalize workflow candidate.json output.html --repo-root ... --quality showcase --out-dir 新收据目录 --json
```

按持续授权将本轮章节、图源/产物/记录与STATUS提交并推送origin/main。GitHub远端与Pages状态在交付时单独核对；本地HTTP通过不代表Pages已完成部署。
