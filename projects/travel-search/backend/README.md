# F07–F11 · 本机旅游搜索服务

本工程实现 F07 的输入校验、官方 Java Client、最小搜索接口与课程提供的展示壳。只学习已在 F06 解释的名称、城市、预算、开放、半径条件；无需开发前端。Pages 不运行这个应用。

## 固定版本

- 应用：Spring Boot **4.0.8**、JDK **25**（本轮实际 Temurin 25.0.4.1+1，macOS arm64）。
- 官方 Elasticsearch Java API Client / Rest5 Client **9.4.8**，`elasticsearch-client.version` 同时覆盖 Boot 管理的这两个依赖；显式使用 Jackson3JsonpMapper。
- Maven Wrapper **3.3.4** / Maven **3.9.11**，官方 only-script 产物，distributionSha256Sum 固定下载包。
- 服务端：ES **9.4.0** / Lucene **10.4.0**，容器 bundled JVM 与应用 JDK 分开。
- [依赖树](../review/f07/dependency-tree.txt)、[制品哈希](../review/f07/artifacts.json)、[真实运行](../review/f07/README.md)分别记录。不是性能或生产部署基准。

先安装并选择 JDK25，使 JAVA_HOME / PATH 指向该 JDK。只在 pom 中设置 java.version 不会安装 JDK。`./mvnw -version` 应显示 Java25。Windows 的 Wrapper 为 `mvnw.cmd`，本轮未验收 Windows。

## 准备与启动

仓库根目录，终端一：

```bash
cd projects/travel-search
docker compose -f infra/single-node/compose.yaml up -d
bash infra/single-node/wait.sh
bash labs/f07/01-prepare.sh
```

终端二：

```bash
cd projects/travel-search/backend
./mvnw -version
./mvnw -B -ntp clean package
java -jar target/travel-search-0.7.0.jar
```

打开 `http://127.0.0.1:18080/` 使用课程提供的展示壳。默认只绑定本机；浏览器仅调用同源 Java 接口，不调用 ES，不保存 ES 凭据。ES_URL 默认 `http://127.0.0.1:19200`，ES_INDEX 默认 `tut-f07-attractions`，APP_PORT 默认 `18080`；均为服务端启动环境变量，变更后需重启应用。不要把无认证学习配置照搬到公网；TLS/权限的实现放在 F35。

## 接口契约

`POST /api/attractions/search` / `Content-Type: application/json`：

```json
{"q":"西湖","cityCode":"HZ","maxPriceFen":20000,"latitude":30.25,"longitude":120.15,"radiusKm":3}
```

全部必填；q 非空、最长60；cityCode 两位大写；预算整数分0–100000000；经纬度合法；半径大于0且不超过100km。应用禁用浮点转整型的截断。服务端固定 CNY / status=open / gte0 / match OR / ID升序 / 最多20条，不提供任意DSL代理。

- 成功：total、totalRelation、esTookMs、conditions、esRequest、items；Card 为 id/name/cityCode/ticketPriceFen/currency/status/score。
- 正常零命中：200，total=0，items=[]。
- 非法输入：400 / INVALID_SEARCH_INPUT。
- 连接或Transport错误：503 / SEARCH_UNAVAILABLE。
- ES拒绝请求（例如索引缺失）：502 / SEARCH_BACKEND_REJECTED。
- 超时、分片失败、缺关键字段：502 / SEARCH_INCOMPLETE。该分支存在，但本轮未构造真实分片失败或执行超时故障。
- `GET /api/health` 只报告Java进程，不探测ES/索引。

请求级别构造SearchRequest；Spring管理单例ElasticsearchClient，正常关闭时close释放Transport。源名称与JSON用textContent展示。前端10秒等待截止只控制本次页面等待，不等于ES执行时限或取消服务端任务。

本机 [实验与点名重做](../labs/f07/README.md)，课程 [F07正文](../../../framework/f07.html)。


## F08 增量

沿用本工程/版本/构建命令。按[本机F08步骤](../labs/f08/README.md)准备独立索引，启动同一个jar，打开`http://127.0.0.1:18080/f08.html`。根路径和`/api/attractions/search`保留F07契约；新`/api/attractions/multi-search`使用相同SearchInput，服务端索引默认为`tut-f08-attractions`（Spring环境变量TRAVEL_F08_INDEX覆盖）。两个课次分别配置索引，不能用F07数据冒充F08验收。

F08固定multi_match/name^3,aliases^2,description/best_fields/AND/tie_breaker0；完整硬条件与ID升序保留。MultiFieldResult每卡增加snippets：field/highlighted/segments[{text,matched}]。高亮先encoder=html，Java先拆固定mark边界再按段解码；缺片段回退_source，缺别名/描述显示明确占位。展示壳只用textContent放入mark/span，不解析任意HTML。Java与REST精确DSL/DTO、原文标签与回退见[两轮真实记录](../review/f08/README.md)。


## F09 增量

沿用版本与构建命令。[F09本机实验](../labs/f09/README.md)准备tut-f09-attractions与独立双分片候选索引；新接口`POST /api/attractions/facet-search`，观察页`http://127.0.0.1:18080/f09.html`。服务端默认tut-f09-attractions，TRAVEL_F09_INDEX可在启动前覆盖。F07/F08接口、索引配置与观察页保留。

FacetInput：q非空最长60；cityCodes与themes数组必填，空数组不限；城市允许HZ/FZ/SH，最多3项；主题允许lake/walk/garden/culture，最多4项；maxPriceFen整数分0–100000000，不截断小数。各维度内OR，跨维AND。全国浏览移除F08圆心/半径；query保留multi_match/best_fields/AND/CNY/open/非负价格/预算，post_filter应用全部选择。城市filter聚合只加主题，主题filter聚合只加城市，价格filter聚合保留两维，range含from不含to。仍按ID升序核对，最多20卡；不请求高亮。

DTO保存scope/scopeTotal、整体/逐桶docCountErrorUpperBound、sumOtherDocCount、missingThemeCount及价格分布/priceScopeTotal；不把未返回的桶自动当0。缺必要聚合/源字段或搜索不完整502；输入400、后端拒绝502、连接不可用503沿用错误代码。本课Controller提供适配数组输入的400说明。无CORS代理或任意DSL入口。范围/桶/误差与REST精确比较、非法输入和删除索引恢复见[真实验收](../review/f09/README.md)。

## F11 · 稳定分页与PIT

新增[本课手工入口](../labs/f11/README.md)：from/size、受控改价、PIT/search_after与三模式Java分页。启动同一个Boot4/JDK25应用后打开 http://127.0.0.1:18080/f11.html ，顺序翻页、末页与关闭/换条件重新开始；教程无需前端开发。旧接口保留，独立tut-f11-attractions，原始实连与重做分别记录。


## F12 · 更新、可见性与基础结业

新增[手工入口](../labs/f12/README.md)，独立tut-f12-attractions/结业tut-f12-graduation，显式关闭自动refresh。新增/api/attractions/changes：实时GET、只准新建、带版本的完整替换/局部更新/删除、显式refresh和独立PIT分页；旧课接口保留。本机观察页http://127.0.0.1:18080/f12.html；结业用同jar的APP_PORT=18081/TRAVEL_F12_INDEX=tut-f12-graduation，浏览器不能指定任意索引。Pages只承载教程，不要求开发前端。先独立做新样本任务，再看参考解；脚本通过不等于独立结业。


## F13 分析链观察

`POST /api/attractions/analysis-search`接受q、cityCode(BJ/SY)、maxPriceFen(0–100000000整数分)、mode(mismatch/aligned/phrase/case-sensitive)。q非空，长度不超过60个UTF-16单位。索引默认tut-f13-attractions，启动前可用TRAVEL_F13_INDEX配置；浏览器不能指定任意索引、字段或analyzer。服务端模式分派与[完整配置](../search/f13/index.json)保持一致。

本机`/f13.html`返回同一查询文本分别经过字段索引链与查询链的真实token/position/offset、两份实际分析请求、SearchRequest DSL与卡片。分析结果不代表读取存量词项；每次两次额外分析用于本课诊断，普通业务接口不用这样重复分析。[准备/运行/清理](../labs/f13/README.md) · [两轮及构建](../review/f13/README.md)。

## F14 中文分析方案观察窗

本课另用独立ES端口19214，与前课19200分开。在启动Java前运行[F14基线与插件准备](../labs/f14/README.md)，然后从backend目录：

```bash
./mvnw -B clean package
ES_URL=http://127.0.0.1:19214 java -jar target/travel-search-0.7.0.jar
```

打开`http://127.0.0.1:18080/f14.html`，API`POST /api/attractions/analyzer-search`接受q/cityCode/maxPriceFen/candidate。五种候选由服务端映射到固定字段/analyzer，默认索引tut-f14-attractions（启动前TRAVEL_F14_INDEX可配置）；两列分析当前查询与固定样本，不读取存量词项。输入/插件不可用/缺索引/连接故障分别400/502/502/503，错误清空旧卡片。标准基线无需插件，其他模式需完整准备。构建/两轮实连见[review/f14](../review/f14/README.md)，浏览器不直连ES。

## F16 · 别名与同义词观察窗

按[本机入口](../labs/f16/README.md)准备独立19216节点、ICU9.4.0、初始规则与11份资料。沿用Boot4.0.8/JDK25/官方客户端9.4.8，启动前设置ES_URL=http://127.0.0.1:19216；打开http://127.0.0.1:18080/f16.html。

POST /api/attractions/synonym-search接受q/cityCode(BJ|SY)/maxPriceFen整数分0–100000000/mode(plain|aliases|graph|phrase|loose|late)。服务端固定本课索引、字段和分析器，双分析都处理当前输入，返回position/positionLength/offset与完整链，不冒充历史词项。完整查询与DTO逐份REST重放；条件/错误清空旧结果，400/502/503与正常0结果分开。[两轮与构建](../review/f16/README.md)。

## F18 评分观察

[本机实验](../labs/f18/README.md)使用ES_URL=http://127.0.0.1:19218。新增POST /api/attractions/score-search与/f18.html，三模式共用完整query执行搜索与_explain；详情见[正文](../../../framework/f18.html)。继承Boot4.0.8/JDK25/官方客户端9.4.8，原接口保留。观察窗只读，不写入追加资料；固定ID/字段/索引，解释数值来自ES。

## F19 增量

[手工入口](../labs/f19/README.md)准备独立19219/tut-f19-attractions，Java启动时ES_URL指向该节点。新增POST /api/attractions/weight-search与/f19.html，六模式sum/best/tie/tuned/optional/required；每字段AND，名称match权重1–50整数，tuned额外短语boost4与整名constant_score8。q保留原值，未自动去空格。固定索引/字段/解释ID，不提供任意DSL代理。

结果携带实际搜索/解释请求、客户端序列化响应、完整卡片和解释树；两个ES请求非并发原子视图。400/502/503沿用错误映射，字段不完整502；真实超时/分片部分失败仅代码防护。整名目标提升与夜游摄影展退步同列，未认证全站质量。[两轮实连](../review/f19/README.md)。

## F20 点评质量与热度

[实验说明](../labs/f20/README.md)：独立19220/tut-f20-attractions，`POST /api/attractions/signal-search` 与本机 `/f20.html`。固定虚构点评、质量、热度，八模式与完整解释；浏览器→Java→ES。版本基线不变，未测整体质量/性能。

## F21 距离与核验时效

[实验说明](../labs/f21/README.md)：独立19221/tut-f21-attractions、Java18081，`POST /api/attractions/decay-search`与本机`/f21.html`。六评分模式/三种sort，固定核验原点、可空硬半径与完整解释；版本基线不变，未测整体质量/性能。
