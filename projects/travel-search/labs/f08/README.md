# F08 · 多字段与高亮（本机手工入口）

继续 F07 的 `projects/travel-search/backend`，不使用历史 `travel-portal`。正文见 [F08](../../../../framework/f08.html)；固定15份[资料](../../data/f08/attractions.json)、[mapping](../../search/f08/index.json)、[真实验收](../../review/f08/README.md)。使用本课交付的 GitHub 提交可固定这一阶段；后续 main 会继续演进。

前置：Docker/Compose、Bash、curl、JDK25。Boot4.0.8 / 官方Java与Rest5 Client9.4.8 / Wrapper3.3.4 / Maven3.9.11沿用F07。先选择本机JDK25，`./mvnw -version`核对；应用JDK与ES容器bundled JVM不同。专用ES只绑定127.0.0.1:19200，Compose project=es-framework-single，不动源码篇9200/9201。合成资料不是现实经营信息。

仓库根目录，终端一：

```bash
cd projects/travel-search
docker compose -f infra/single-node/compose.yaml up -d es
bash infra/single-node/wait.sh
bash labs/f08/01-prepare.sh
bash labs/f08/02-fields.sh
bash labs/f08/03-copy.sh
```

逐项确认ES9.4.0、索引创建成功、green且未超时、Bulk errors=false/15项created、refresh零失败分片、count=15。Bulk的HTTP200不代表条级成功；已有索引不能跳过创建错误，先清理本课索引。主索引为 `tut-f08-attractions`，一主分片零副本，dynamic=strict，standard分析，无插件。固定ID每次写入一致，NDJSON最后有换行。

终端二（先关闭原F07 Java进程，避免端口冲突）：

```bash
cd projects/travel-search/backend
./mvnw -version
./mvnw -B -ntp clean package
java -jar target/travel-search-0.7.0.jar
```

默认F08索引来自服务端 `travel.f08-index`，可用Spring环境变量 `TRAVEL_F08_INDEX` 覆盖，修改需重启；默认ES_URL/APP_PORT仍为127.0.0.1:19200 / 18080。原F07接口索引仍由ES_INDEX配置，两个课次互不复用数据。ES端点与凭据不进入浏览器/Pages/URL。

终端一：

```bash
bash labs/f08/04-java.sh
```

浏览器打开 `http://127.0.0.1:18080/f08.html`，提交“西湖→钱塘湖→火星”，看5→1→0和观察区真实DSL/DTO。根路径保留F07展示壳；不用学习前端代码。浏览器只调用同源Java `/api/attractions/multi-search`；Pages仅教程。

## 三个案例与结果

1. **f08-c01，9条请求**：准备6、name-only/multi/alias查询3。name-only为AND，不能直接拿F07名称OR作“仅扩大字段”的对照。完整前缀 `a-hz-`：名称AND得到boundary→plain→xihu；multi得到boundary→guide→plain→tea→xihu；别名钱塘湖仅xihu。所有查询固定HZ/CNY/0–20000分/open/3km球面距离，按attraction_id升序。
2. **f08-c02，3条请求**：copy→no-highlight→empty。copy额外加入split（西在名称、湖在描述），六条ID升序；原字段无highlight、_source没有search_text。去掉高亮仍是multi五条ID且分数相同；火星正常空集。原文HTML测试在guide描述中，不应解释为页面节点。
3. **f08-c03，3条Java请求**：输入multi/alias/empty，分别与对应REST比对ID、total/relation、整数分、查询DSL与逐字段文本段。卡片显示名称/别名/描述标签；plain缺别名/描述时显示“未提供别名 / 暂无描述”；guide中img和原文mark为文字，只有真正命中段创建mark。

15条教学HTTP请求=6+3+3+3；清理1、启动探活/作者额外检查/页面重复调用另计。[案例注册](cases.json)。HTTP路径/完整请求体在脚本与search/f08里；正文解释因果，作者脚本只作为配套证据。

## 清理重做

应用终端Ctrl+C正常关闭，然后工程目录执行：

```bash
bash labs/f08/cleanup.sh
```

只删除`tut-f08-attractions`，不删其他课索引、容器和持久卷。依原顺序再执行一轮；十五项应重新created，不是updated。无需down -v。结束使用时可`docker compose -f infra/single-node/compose.yaml stop es`暂时停止专用ES，卷保留。
