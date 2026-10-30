# 旅游搜索 Elasticsearch 实验工程

用景点/酒店/房型搜索学习 ES，实验在本机运行。教程从 [F01 导学](../../framework/f01.html)开始，F02 概念推演、F03 首次启动、F07 引入 Spring Boot 4 / JDK 25 与本机搜索展示壳。F01–F03 已完成；F04 字段建模、F05 关键词查询与 F06 组合筛选正文/脚本已交付，真实 ES 待验收；F07 Java接口与本机展示壳、F08多字段与高亮、F09聚合与筛选计数、F10显式排序、F11稳定分页与PIT、F12更新与基础结业、F13分析链与中文召回、F14中文分词方案比较、F15专有词与词典、F16别名/同义词与繁简及F17提示/拼音与容错已交付，F18已交付BM25与解释评分，F19已交付名称/短语与多字段权重，F20已交付点评/热度与数值评分，F21已交付距离/时效与显式排序，F22已交付查询集/标注与质量评估，F23已交付酒店/房型/offer文档边界，F24已交付同房型条件/inner_hits与nested排序，F25多晚库存/逐晚总价与Java固定价表核对已交付，F26酒店去重/匹配报价/最低价范围已交付，F27酒店与房型分层排序已交付，F28三节点拓扑/角色/发现与持久重启已交付，F29主副分片/routing与读写路径已交付，F30选主/投票多数与数据节点失效恢复已交付，F31分配/扩缩容与resize条件已交付，F32–F35已交付模板/alias、受控迁移、快照恢复与安全连接，F36已交付SQL来源/搜索投影/快照缺口与人工补齐，F37已交付PostgreSQL WAL/Kafka/单表Java消费与ES及受控恢复，F38已交付MySQL binlog/ROW-FULL/内部history与独立恢复，F39已交付Java多表关联路由/旧新归属重算与残留移除，F40已交付重放/乱序/删除保护与失败位置，F41已交付持续更新重建/双版本追平与切换回滚，F42已交付延迟/对账与来源补偿，F43已交付负载/容量与受控拒绝恢复，F44–F45待实施，验收见 [STATUS.md](../../STATUS.md)。

本轮新增 [F43正文](../../framework/f43.html)、[负载/容量与拒绝恢复本机步骤](labs/f43/README.md)及[执行记录](review/f43/README.md)；前课原记录保留，F44及后续课未实施。

初学入口是 [F03 首搜](../../framework/f03.html)、[F03 手工实验](labs/f03/README.md)与[两轮真实 ES 记录](review/f03/README.md)，无需前端、Java、数据库或 Kibana。[F04 字段设计与 Bulk](../../framework/f04.html)及其[本机步骤](labs/f04/README.md)已提供；[执行状态](review/f04/README.md)明确记录本环境启动阻塞，尚未两轮实测。F04 从新资源独立开始，不依赖 F03 索引。历史文件、资源与案例 ID 保留：

- [历史启动实验正文](../../framework/f01-startup-legacy.html)
- [手工步骤、案例与重做](labs/f01/README.md)
- [两轮真实 ES 验收](review/f01/README.md)
- [45 课路线](../../FRAMEWORK_PLAN.md)

下面命令对应当前资源 `tut-f03-attractions` 与 `labs/f03`，配置和脚本保持原实验约定。

需要 Docker Engine/Desktop、Compose v2+、Bash 与 curl（7.76+，支持 `--fail-with-body`）。Docker Desktop 至少分配 4GB 内存；本课一个容器上限 1GB、堆 512MB。这是几条文档的教学配置；更多语料和多节点另做容量测量。Windows 可在 WSL2 中运行；F03 实际 ES 验收为 macOS arm64 + Docker，F04/F05/F06 云环境启动受阻，未声称 Windows/Linux 全平台验收。

在仓库根目录执行：

```bash
cd projects/travel-search
bash labs/f03/run.sh
```

它按顺序启动隔离 ES、观察、建索引、写文档、刷新、搜索和核对。第二次先按本课清理步骤删除 `tut-f03-attractions`；脚本不会暗中删除已有索引。脚本默认只访问 `http://127.0.0.1:19200`，Compose project 为 `es-framework-single`；不复用源码篇 9200/9201 服务，不发布 transport 9300。

本课显式关闭安全，仅绑定本机。正式安全连接在 F35 学习；Docker 官方默认安全启动流程不同。本课不需要 CORS，因为 curl 直接访问 ES，Pages 只用于阅读。

```bash
# 保留容器和数据，暂时停止本工程 ES。
docker compose -f infra/single-node/compose.yaml stop es
# 再次启动仍保留数据。
docker compose -f infra/single-node/compose.yaml up -d
bash infra/single-node/wait.sh
```

数据保存在 Compose 卷 `es-framework-single_es-data`；停止/重启容器不会删除该卷。不要为了重做一课运行 `down -v`，按课次点名清理索引即可。

## F05 · 名称关键词与精确条件

[F05 正文](../../framework/f05.html)沿用五份固定景点，比较 term/match 的 OR、AND、keyword 完整值与 slop=0 短语。新增独立索引 `tut-f05-attractions`，3案例、22条教学请求；与F04正确数据/mapping一致，可独立准备。

- [固定资料](data/f05/attractions.json)、[完整查询与预测](search/f05/expected.json)
- [本机入口、ID对照与点名重做](labs/f05/README.md)
- [真实执行状态与两轮验收脚本](review/f05/README.md)

正文、图解与阅读记录已交付；本轮云环境 ES9.4.0 在HTTP前因缺少 `/proc/self/coredump_filter` 退出，真实API/两轮未通过。预测不是响应，未交付本机展示壳或Java功能；F06将组合城市/预算/状态/距离条件。


## F06 · bool 与组合筛选

[F06 正文](../../framework/f06.html)将名称、城市、CNY预算、开放和3km组合起来；独立索引 `tut-f06-attractions`，保留原五份资料，新增七份边界，3案例、22条教学请求。

- [固定12份资料](data/f06/attractions.json)、[16组查询与预测](search/f06/expected.json)
- [本机步骤、完整请求与点名重做](labs/f06/README.md)
- [真实执行状态与两轮脚本](review/f06/README.md)

包含20000/20001分、免费/缺价/null、未知状态/无坐标、半径外，以及should默认门槛和过滤评分对照。正文与阅读可交付；云环境原Compose本轮仍在HTTP前启动失败，真实ES待验收。F07才引入Java与配套本机展示壳。

## F07 · Java接口与本机展示壳

[F07正文](../../framework/f07.html)将F06已理解的条件接入Boot4.0.8 / JDK25 / 官方Java与Rest5 Client9.4.8。使用独立tut-f07-attractions，沿用十二份固定资料；浏览器只调用本机Java，Pages只承载教程。

- [应用构建、版本与契约](backend/README.md)，同源展示壳随应用提供，默认127.0.0.1:18080
- [三案例/17条教学请求与点名重做](labs/f07/README.md)，[完整输入与DSL](search/f07/near.json)
- [ES/Java两轮、依赖树与制品](review/f07/README.md)，[本机展示壳与阅读验收](../../docs/framework-review/20261020-f07-java/README.md)

REST/Java逐项核对ID、价格、total/relation与实际序列化DSL；200元→80元、空结果、非法输入、索引缺失、ES停机/同进程恢复分别验证。本课不提供多字段/高亮/聚合/分页；F04–F06历史云环境受阻状态不回填。


## F08 · 多字段与高亮

[F08正文](../../framework/f08.html)在同一F07工程增加普通业务aliases字段、multi_match/best_fields AND、copy_to对照与安全文本段DTO。独立tut-f08-attractions，保留十二份原资料并补别名，新增三份边界，共十五份。

- [三案例/15条教学请求、启动与重做](labs/f08/README.md)，[固定资料](data/f08/attractions.json)、[主DSL](search/f08/multi.json)
- 新接口`POST /api/attractions/multi-search`，展示壳`http://127.0.0.1:18080/f08.html`；原F07接口与根路径保留
- [ES/Java两轮](review/f08/README.md)、[真实浏览器/阅读/图解验收](../../docs/framework-review/20261020-f08-multifield/README.md)

西湖多字段5条、钱塘湖别名1条、copy_to额外split、片段缺失回退、原文HTML纯文本显示分别核对；不把显示高亮当成评分解释或实体识别。F09再学习聚合计数。


## F09 · 聚合与筛选计数

[F09正文](../../framework/f09.html)使用独立tut-f09-attractions：继承F08十五份资料、补主题、加上海对照，共16份；全国候选浏览，显式移除附近半径。共同候选9份，选择HZ+lake或culture时命中4、城市范围6、主题范围7。query/post_filter/filter分支、同维OR/跨维AND、多值重叠/缺主题与range边界分别解释。

- [手工实验与重做](labs/f09/README.md)：3案例、28条教学HTTP请求，清理2与探活/作者附加检查另计
- `POST /api/attractions/facet-search`；本机观察页`http://127.0.0.1:18080/f09.html`，保留范围/桶/误差的DTO
- 第二索引tut-f09-candidates只演示同节点双分片候选误差：小候选A5，完整C8/A6/B6
- [真实两轮ES/Java记录](review/f09/README.md)、[HTTP与展示壳证据](../../docs/framework-review/20261020-f09-facets/README.md)

F10再学习排序切换；不把本课ID次序当推荐排序，不把桶计数当库存或任意业务实体总数。

## F10 · 显式排序

[F10正文](../../framework/f10.html)比较相关性、价格、距离的完整次序、第二键与缺值；独立tut-f10-attractions继承F09十六份资料，3案例/23条教学HTTP请求。

- [本机手工入口](labs/f10/README.md)、[完整请求](search/f10/relevance.json)、[两轮实连](review/f10/README.md)。
- Boot4/JDK25工程新增POST /api/attractions/sort-search与http://127.0.0.1:18080/f10.html；浏览器→Java→ES，F09计数页保留。
- 只完成排序，不实现F11分页/PIT；实际验收与限制见[记录](../../docs/framework-review/20261021-f10-sort/README.md)。

## F11 · 稳定分页与PIT

新增[本课手工入口](labs/f11/README.md)：from/size、受控改价、PIT/search_after与三模式Java分页。启动同一个Boot4/JDK25应用后打开 http://127.0.0.1:18080/f11.html ，顺序翻页、末页与关闭/换条件重新开始；教程无需前端开发。旧接口保留，独立tut-f11-attractions，原始实连与重做分别记录。


## F12 · 更新、可见性与基础结业

新增[手工入口](labs/f12/README.md)，独立tut-f12-attractions/结业tut-f12-graduation，显式关闭自动refresh。新增/api/attractions/changes：实时GET、只准新建、带版本的完整替换/局部更新/删除、显式refresh和独立PIT分页；旧课接口保留。本机观察页http://127.0.0.1:18080/f12.html；结业用同jar的APP_PORT=18081/TRAVEL_F12_INDEX=tut-f12-graduation，浏览器不能指定任意索引。Pages只承载教程，不要求开发前端。先独立做新样本任务，再看参考解；脚本通过不等于独立结业。


## F13 · 分析链与中文召回

[F13正文](../../framework/f13.html)从故意失配的查询恢复召回，再检查单字AND/短语与标点的误匹配。独立tut-f13-attractions、八份固定资料，分析链与field/显式analyzer、token/position/offset、大小写/HTML/UTF-16分开解释；未安装插件，方案比较留到F14。

- [三案例、58条教学HTTP、本机启动与点名重做](labs/f13/README.md)；[固定语料](data/f13/attractions.json)、[完整分析配置](search/f13/index.json)
- 新接口`POST /api/attractions/analysis-search`，本机页`http://127.0.0.1:18080/f13.html`，四模式白名单；两列均分析输入q，不读取存量文档词项
- [真实ES/Java两轮](review/f13/README.md)、[构建与依赖](review/f13/build/runtime.json)、[HTTP/真实观察窗/独立xhigh审阅与视觉](../../docs/framework-review/20261023-f13-analysis/README.md)

失配0/对齐AND4/短语3/英文2/不转小写0、城市/预算/空流、400/502/真实ES停机503与同Java进程恢复分别核对。Pages仍仅承载教程，浏览器通过Java访问ES。

## F14 · 中文分词方案的受控比较

[F14正文](../../framework/f14.html)在独立19214节点，先用内置standard，再比较SmartCN/ICU/IK两模式。同12份资料、4查询、固定人工意图/过滤/AND/ID排序，保留token与漏/误召回矩阵，不预定最佳插件。

- [三案例108条教学HTTP与点名重做](labs/f14/README.md)、[固定语料/判断](data/f14/judgments.json)、[完整字段配置](search/f14/index-plugins.json)、[插件锁](infra/f14/plugins.lock.json)
- 新接口`POST /api/attractions/analyzer-search`、本机页`http://127.0.0.1:18080/f14.html`；固定候选与样本，Java启动时ES_URL指向19214
- [真实插件/ES/Java两轮与错版本拒绝](review/f14/README.md)、[内容/图解/阅读/观察窗](../../docs/framework-review/20261024-f14-analyzers/README.md)；未测词典/同义词/拼音、整体质量与性能

## F15 · 本地词典与历史词项

[F15正文](../../framework/f15.html)用虚构品牌/地名观察本地IK词典：只改文件、重启加载、旧/新文档与_source受控重建。独立19215与tut-f15-v1/v2，显式存储term vector，既解释漏召回修复，也核对新增误匹配。

- [三案例84教学HTTP与点名重做](labs/f15/README.md)、[固定样本/判断](data/f15/judgments.json)、[字段配置](search/f15/index.json)、[插件锁](infra/f15/plugins.lock.json)
- 接口`POST /api/attractions/dictionary-search`、本机页`http://127.0.0.1:18080/f15.html`；启动Java时ES_URL指向19215，索引选择不切词典
- [ES/Java两轮](review/f15/README.md)、[内容/图解/阅读/观察窗](../../docs/framework-review/20261024-f15-dictionary/README.md)；不认证远程词典、多节点发布、在线迁移、全站质量或性能

## F16 · 别名、同义词与繁简

[F16正文](../../framework/f16.html)用显式实体别名、查询synonym_graph、ICU繁简与城市对照，解释多词图/AND/phrase、分析链顺序、别名可见性与查询集重载。独立19216/tut-f16-attractions/tut-f16-names，不改变F15词典。

- [本机三案例/87请求与重做](labs/f16/README.md)、[固定资料与意图](data/f16/judgments.json)、[完整配置](search/f16/index.json)、[ICU锁](infra/f16/plugins.lock.json)
- 接口POST /api/attractions/synonym-search，本机http://127.0.0.1:18080/f16.html；Java启动ES_URL指向19216，浏览器不直连ES
- [真实两轮](review/f16/README.md)、[内容/图解/阅读/观察窗](../../docs/framework-review/20261025-f16-synonyms/README.md)；全站质量、性能、多节点与在线发布未测

## F17 · 提示、拼音与容错

[F17正文](../../framework/f17.html)比较completion/search_as_you_type、显式全拼/首字母、整名fuzzy与收窄代价；固定14份资料核对文字/实体去重、城市/下架、同音与短词误匹配。独立19217/tut-f17-attractions，无额外插件。

- [本机三案例/64请求与重做](labs/f17/README.md)、[固定资料与意图](data/f17/judgments.json)、[完整配置](search/f17/index.json)
- 接口POST /api/attractions/suggestions，本机http://127.0.0.1:18080/f17.html；Java的ES_URL指向19217，浏览器不直连ES
- [真实两轮](review/f17/README.md)、[内容/图解/阅读/观察窗](../../docs/framework-review/20261025-f17-suggestions/README.md)；全站质量/性能/多节点/自动转写未测

## F18 · BM25与解释评分

[F18正文](../../framework/f18.html)用等长词频、同频长度、稀有词项、must/filter和不命中追加资料，解释相对次序与真实_explain；固定10+6份虚构资料，独立19218/tut-f18-attractions，无插件。

- [本机三案例/58请求与重做](labs/f18/README.md)、[资料清单](data/f18/manifest.json)、[完整配置](search/f18/index.json)
- POST /api/attractions/score-search，观察窗http://127.0.0.1:18080/f18.html；Java的ES_URL指向19218，浏览器不直连ES
- [真实两轮](review/f18/README.md)、[内容/图解/阅读/观察窗](../../docs/framework-review/20261025-f18-bm25/README.md)；未测全站质量/性能、多主分片/DFS

## F19 · 名称、短语与多字段权重

[F19正文](../../framework/f19.html)区分整名相等/名称短语/散词，比较加和、dis_max、轻补、奖励与should门槛；保留夜游摄影展被误抬的反例。独立19219/tut-f19-attractions，12份虚构资料，无插件。

- [本机三案例/92教学请求与重做](labs/f19/README.md)、[固定资料与意图](data/f19/judgments.json)、[完整配置](search/f19/index.json)
- POST /api/attractions/weight-search，观察窗http://127.0.0.1:18080/f19.html；启动Java时ES_URL指向19219
- [真实两轮](review/f19/README.md)、[内容/图解/阅读/观察窗](../../docs/framework-review/20261025-f19-weights/README.md)；全站质量/性能/多分片/生产安全未测

## F20 点评质量与热度

[本机实验](labs/f20/README.md) · [完整查询](search/f20) · [两轮记录](review/f20/README.md)

## F21 距离、时效与显式排序

[正文](../../framework/f21.html) · [本机实验](labs/f21/README.md) · [完整查询](search/f21) · [两轮证据](review/f21/README.md)。独立19221/tut-f21-attractions，14份虚构资料；本机18081/f21.html与decay-search接口。gauss/exp、两层合成与三种排序意图，固定核验时间、缺值零奖励和软/硬半径分别核对；质量评估见F22，本节保留F21实验范围。

## F22 · 查询集、标注与质量评估

[正文](../../framework/f22.html) · [本机实验](labs/f22/README.md) · [独立结业](labs/f22/assessment.md) · [固定请求](search/f22) · [两轮证据](review/f22/README.md)。独立19222/tut-f22-attractions、24份资料/8查询完整标注；本机18081/f22.html与quality/evaluate接口。调整/留出分开，Recall@10/nDCG@10、坏例/短结果/未标注/HTTP200内失败均核对；小固定语料不宣称全站改善，酒店阶段见F23。

## F23 · 酒店、房型与offer文档边界

[正文](../../framework/f23.html) · [本机实验](labs/f23/README.md) · [固定样本](data/f23/catalog.json) · [完整请求](search/f23) · [两轮证据](review/f23/README.md)。独立19223，3酒店/5房型/8报价；四投影比较查询单位、Lucene文档数与真实改价/更名更新范围。本机18081/f23.html与model/inspect接口；rates为object只作明细，报价条件在独立offer执行。后续同房型组合条件与排序见F24。

## F24 · 同房型条件与nested排序

[正文](../../framework/f24.html) · [本机步骤](labs/f24/README.md) · [完整DSL](search/f24) · [固定资料](data/f24/hotels.json) · [两轮](review/f24/README.md)。独立19224，9酒店/16房型报价条目；object/多个nested错误对照、一个完整nested与inner_hits、嵌套排序过滤一致性；本机18081/f24.html和nested/inspect接口。F25多晚核对见[labs/f25/README.md](labs/f25/README.md)。

## F25 · 多晚库存与精确价表核对

[正文](../../framework/f25.html) · [本机入口](labs/f25/README.md) · [固定逐晚表](data/f25/stay-table.json) · [完整DSL](search/f25) · [实际收据](review/f25/README.md)。独立19225/tut-f25-offers，Java本机18081/f25.html与/api/stay/inspect；ES摘要筛候选，同offer逐晚检查缺晚/库存/价格/入住最短晚数，按全部房间与住宿晚核对总预算。非实时可订，不做酒店去重或总价排名。F26见[labs/f26/README.md](labs/f26/README.md)。

## F26 · collapse、酒店去重与最低价范围

[正文](../../framework/f26.html) · [本机入口](labs/f26/README.md) · [固定表](data/f26/stay-table.json) · [DSL](search/f26) · [验收](review/f26/README.md)。独立19226/tut-f26-offers，Java18081/f26.html与/api/collapse/inspect；10候选报价/6候选酒店，完整逐晚核对7报价/4酒店。区分起价/入住总价、报价数/酒店数、cardinality估计和完整集合、Top K酒店内/酒店间遗漏。仅固定快照，无实时预订。

## F27 · 酒店与房型的分层排序

[正文](../../framework/f27.html) · [本机入口](labs/f27/README.md) · [固定表](data/f27/stay-table.json) · [DSL](search/f27) · [验收](review/f27/README.md)。独立19227/tut-f27-hotels，Java18081/f27.html与/api/hotel-ranking/inspect；8根酒店/19nested摘要，酒店相关性/品质/距离与酒店内总价/偏好分开，先逐晚资格再排序，区分硬条件、所选/最低价、完整/前2家。不实现实时可订或订单。

## F28 · 三节点拓扑、角色与持久首启

[正文](../../framework/f28.html) · [本机入口](labs/f28/README.md) · [稳定配置](infra/f28/compose.yaml) · [数据](data/f28/attractions.json) · [验收](review/f28/README.md)。独立19228–19230/三个256MiB堆进程，3个master候选、2个data、1个ingest；首启后移除引导名单，2P+2R与6份固定景点核对，保留卷重启、错误独立UUID/不能靠seed合并/原卷恢复。复用F07 Java接口和观察窗，ES_URL指19229、ES_INDEX=tut-f28-attractions，无新增Controller。单Docker VM，不证明跨机器容灾。

F29 独立三节点与路由实验入口：[labs/f29/README.md](labs/f29/README.md)；复用F07观察窗，新增独立官方Java客户端路由实验，未增加前端或Web接口。

F30独立四进程故障与恢复入口：[labs/f30/README.md](labs/f30/README.md)；复用F07单入口观察窗，分别核对投票多数、业务分片与入口错误；真实两轮、资源试案OOM及恢复见[review/f30](review/f30/README.md)。

F31独立分配与扩缩容入口：[labs/f31/README.md](labs/f31/README.md)；复用F07观察窗，实际核对same_shard/filter/disk_threshold拒绝、加入第三数据节点、排空后停机与split/shrink/reindex条件。两轮81教学REST＋7 Java调用及快照边界见[review/f31](review/f31/README.md)。

F32独立模板与读写alias入口：[labs/f32/README.md](labs/f32/README.md)；复用F07搜索与观察窗，ES_INDEX固定read alias，写入用独立官方客户端。两轮85教学REST＋6 Java搜索＋6客户端写入，优先级/模拟/实际继承、唯一写索引与错误恢复见[review/f32](review/f32/README.md)。
