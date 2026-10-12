# 第十九章重构验收

2026-10-12（Asia/Shanghai）。已按 AGENTS → STATUS → PLAN → CHAPTER_STANDARD → CLAUDE 读取协作要求；从本章旧 HTML、17 张注册卡和六步动画出发，只改 ch19、其图源/产物/验收与 STATUS。未通读 tutorial，未使用子代理；共享 CSS/JS、其他章节和原有 .gitignore 修改未纳入。

## 内容与版本依据

固定 **ES 9.4.0 / Lucene 10.4.0**，运行节点 build_hash 与源码提交 `2e8528e92361c3399724226deaf2b46f933e925b` 一致。[源码审计](review/ch19-source-review.json)为 **17 文件 / 36 精确区间 PASS**，已读取本课目标源码，范围有效、本地 bytes 与干净固定 checkout 的 git 对象相同；图 sources 首次即传真实 --repo-root 核验。

按七段阅读结构重排：聚合输入与 hits 窗口、四层职责、局部候选、计数误差、指标归并/Pipeline、执行策略与资源。3 目标、折叠目录、图解/机制/实验跳转、5 折叠思考题、4 陷阱和速记保持一致。

主要校正：

- 普通桶/数值聚合不依赖主 hits Fetch 补统计；top_hits 在构建自身结果时另有 Fetch。聚合随 Query 回的是局部树，之后仍须全局归并。
- Builder.innerBuild 创建 Factory；工厂的字段供应商创建 Aggregator。keyword 不是一个固定执行器：有 filters 适配、低基数、dense/remap 等路径。
- shardSize ≥ size 是容量下限，不是实际返回桶数下限；默认公式含取整与 MAX 上限，未指定且非 _key 才套启发式。
- sum_other 是 terms 候选/窗口截断桶的计数总和，不是 key 数/计数器数；局部和 final 都可贡献。bucket_sort 二次裁剪不回记到 terms.sum_other。
- count 降序的 error_bound 是保守上界，聚合级与桶级不同；本例显式容量3计数全部准确，但聚合上界仍5。不能推断非零一定有错，也不能套到所有 order。
- 默认 count 降序 partial 合并候选，final 选窗口；_key/计数门槛有提前限量特例，不能笼统写所有 partial 都不截。
- avg 携带并合并 sum/count；不平均分片均值。Pipeline 只访问普通归并后结果，不补桶。
- breadth_first 可延迟非排序子聚合；depth_first 主收集已维护子结果。强制 depth_first 的 nested 与 needsScores 是合取条件，另有时序执行条件。
- 高基数状态依赖执行策略；20篇 sum_other18 不证明20个计数器，size/shard_size 也会影响队列/结果/部分子聚合内存。DEFAULT_WEIGHT=5120B 仅初始估计，breaker tripped 是节点累计值。
- range 给区间，histogram/date_histogram 按值与间隔/日历算 key，不是请求预列全部 key；无 terms Top-N 截断不代表无其他边界/资源成本。

## 真实 ES 与重复运行

保留原 **17 稳定 ID**，新增13，共 **3组 / 30卡**（A7、B15、C7、清理1），六步机制 ID 保留。显式1主0副、auto-expand=false、strict mapping/stored source、周期refresh=-1、request cache关闭、无default/final管道；四本课索引分别健康等待后写入，所有bulk固定ID并refresh=true。首次/重复创建、写入、清理与完整重做流程写入正文/预期。

[真实API报告](review/ch19-es-review.json)、[复现脚本](review/ch19-es-review.py)：**两轮每轮30实际注册请求 PASS**，method/path/body 逐项一致。第二轮由第一轮点名清理后的空资源重新建立。另 **29 条重复性观察 PASS**：四索引实际mapping/settings、重复创建400、固定ID首次created201/重复updated200、重写后三个主要计数响应不变、删除200与重复删除404。最终四索引HEAD均404。

实测关键结果：

- 小店8篇，books/electronics/clothing=3/3/2，均价约24.99/349.99/64.99（float尾数按容差）。月份1–4计数2/2/3/1，价格区间4/2/2。hits size1只回id2，聚合仍全8篇；query books则只剩books3。
- 两单分片索引各11篇，局部与全局词频符合账本；容量2返回apple10/date4，sum_other8、聚合error7，桶error0/3；默认13返回apple10/cherry5，other7/error0；size3/shard2抬底返回apple10/cherry5/date4，other3/error5。
- _key asc返回apple10/banana3、other9/error0。terms size2后bucket_sort key desc仅cherry5，other仍7；size4后仅date4，other仍0。
- apple六个price1、四个price9，全局sum42/count10/avg4.2。20唯一user_id：size2→u-1/u-10、other18，size20→20桶/other0。
- 两轮profile均实际 **StringTermsAggregatorFromFilters**，delegate **FilterByFilterAggregator**，可见20个filters与constant-time segment计数；不能当作普遍策略或内存测量。只读本地node breaker，不修改限额、不制造熔断。

[原卡响应](review/ch19-original-responses.json)单列旧17请求，已点名清理，不当作当前30卡验收。没有模拟ES响应、修改集群设置或操作其他章节资源。多节点网络、并发slice、百万基数压力、分片故障、实际熔断与性能收益未实测，相关条件仅据固定源码说明。

## 官方 Archify 门禁

使用[官方 Archify 3.0.1 技能](https://github.com/tt-a1i/archify/blob/v3.0.1/archify/SKILL.md)，已读 authoring defaults、repository authoring、Workflow v2/common schema、指定 example、viewer、delivery 与布局/viewport修复契约。两幅 Workflow v2 均中文/showcase/有限trace；图源修改后完整 finalize，未手改生成HTML。复用 ARCHIFY-LICENSE.txt，保留HTML内字体许可。

| 图 | candidate SHA-256 | HTML SHA-256 | 当前收据 |
|---|---|---|---|
| aggregation-journey | `40828c8aa3281a39308f1064c6619e4a299d34d4dd3c0b395384403ed3c558e7` | `0d4f9cb075b57047b7b61f7b6446ecb83244673d24161423d7ba3f0d770c0bcc` | review-2 |
| terms-candidates | `9e0afe3873162fbbb1ffcb9b968fc519074109155c0cd8123bdde27e74e383d1` | `3f2099a31f47a880ef6479317ddffcbbdee3d7ee2613ce0f7e74d806580947e2` | review-2 |

两图 validate/deliver/strict check 均 **showcase9/9、0 errors/warnings、provenance current**；原生 **browser-check与finalize整体 PASS**，update.noticeRequired=false。首次分别引用了越界行号57与37，官方gate拒绝；修正实际范围后review-2通过，初始候选/失败收据保留。原生visualReview=not-requested不代表人工审图，实际审阅单列。

## HTTP、交互与截图审阅

[最终HTTP](review/ch19-http-review.json)、[局部滚动](review/ch19-scroll-review.json)、[六步捕获](review/ch19-mechanism-review.json)均PASS。使用本地临时HTTP + Python Playwright + 本机Chrome；控制台深链会自动执行，浏览器验收显式abort本机ES请求，没有伪造响应，真实API另行完成。

- 独立两图1440/1600/1920/2048 ×浅深；说明卡完整、无横向溢出。最小SVG/普通节点投影：journey7.0455/8.052px，terms7.3372/8.3854px。
- 章节1920/1440/1024/768/390/320 ×浅深；阅读列≤880px，标题/正文/图框/图注/表格/实验/章节尾左右边界差≤1px；页面与iframe无横溢/垂直裁切，全部节点完整。测量图框桌面790px、≤800px540px。
- 源码探索/关闭、展开、同步主题、暂停→外层重播/Enter、目录/已读、六步前后/播放/重置/键盘、30条真实控制台导航与method/path/body、endpoint/auth/raw、/es_web/前缀路径通过；JS未处理错误与静态HTTP失败为空。
- reduced motion优先，外层重播不覆盖系统偏好；机制不自动播、可手动步进，页面无平滑滚动。390/320表格与旧SVG在自身容器横滑，页面无溢出。
- **实际查看7张审阅拼图，覆盖24张最终浅深独立/嵌入/桌面/390px/实验/表格截图与全部6步完整快照**，另单独查看旅程浅色独立图与候选图深色手机截图。图的完整主路径、两次独立请求边界、说明卡/图注均正确；无箭头交叉/遮挡。手机图为概览，细字需探索或展开缩放，必要结论在正文与图注；旧SVG局部滑动，手机机制标题省略而解说完整。

实际审阅绑定见 [visual-review](review/ch19-visual-review.json)，[contact sheet映射](review/ch19-visual-sheets.json)。截图生成本身不算审阅。

## 站点检查与复现

全站 **30正式页 / 617操作卡 / 22机制播放器**，Archify trace另计。node tools/check.mjs、修改JS语法、figwidth、git diff --check、17稳定ID/30唯一有序槽位、GET/HEAD无body、.nojekyll与静态路径PASS。最终产物/证据哈希见 [artifacts](review/ch19-artifacts.json)。

```bash
node tools/check.mjs
node --check experiments/ch19.js
node tools/figwidth.mjs chapters/ch19.html experiments/ch19.js
ES_SOURCE_ROOT=/path/to/clean-es-v9.4.0 python3 .archify/review/ch19-source-audit.py
python3 .archify/review/ch19-es-review.py                 # 空本课资源开始；两轮30请求+29重复性观察+清理
python3 .archify/review/ch19-es-review.py --validate-only # 复核已有证据，另检查资源HEAD
/path/to/playwright-python .archify/review/ch19-http-review.py
/path/to/playwright-python .archify/review/ch19-scroll-review.py
/path/to/playwright-python .archify/review/ch19-mechanism-review.py
python3 .archify/review/ch19-visual-sheets.py              # 需要Pillow；只捕获拼图，不能替代实际查看
python3 .archify/review/ch19-bind-artifacts.py             # 实际查看新图后才能更新审阅绑定
# 官方图重现：finalize workflow candidate.json output.html --repo-root ... --quality showcase --json
# JSON修改后完整finalize，已有browser证据时使用新的--out-dir
```

按持续授权提交并推送origin/main；GitHub与Pages发布状态在交付时另核对，不将本地验收等同线上更新。
