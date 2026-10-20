# F07 · 本机旅游搜索服务

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
