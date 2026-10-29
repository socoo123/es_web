# F36 · SQL 来源、搜索投影与快照增量

先读[正文](../../../../framework/f36.html)。这一课首次引入业务数据库，用三张小表说明搜索投影、稳定 ID、关联变化和快照缺口。实际运行 PostgreSQL、ES、有限文件导入器和既有搜索观察窗；**没有 WAL/binlog、Kafka、Debezium、事件消费者或 checkpoint**。增量是本课受控事务人工列明的三个键，写入暂停后重读当前投影；不声称已经打通 CDC。

## 隔离与首次启动

在仓库根目录进入项目。需要 Docker、Python3、curl、完整 JDK25。应用基线 Boot4.0.8 / Temurin25.0.4.1+1 / 官方 Java与Rest5 Client9.4.8 / Maven3.9.11；先自行设置 JDK25 的 JAVA_HOME/PATH。PG固定17.5-bookworm与清单digest，属于可复现实验制品，不表示最新补丁推荐。ES9.4.0的 bundled JVM26.0.1与应用 JDK分列记录。

```bash
cd projects/travel-search
python3 labs/f36/lab.py init --out /tmp/f36-reader-init
python3 labs/f36/lab.py start --out /tmp/f36-reader-setup
cd backend
./mvnw -B -ntp clean package dependency:build-classpath -Dmdep.outputFile=target/f36-classpath.txt
cd ..
```

独立Compose项目es-framework-f36。PG数据库travel_f36、用户travel，不映射宿主机端口；通过容器本地socket执行psql。随机PG初始化口令仅在被忽略的infra/f36/.local，目录0700、文件0600；不提交或截图。学习账户是本库初始化管理员，不是F37的最小CDC账户。ES单节点travel-f36-lab / travel-f36-es，回环20036、256MiB堆/768MiB限额；PG256MiB限额。索引tut-f36-attractions-v001，1主0副、strict、refresh=-1；固定读写alias。仅操作本课资源，不触及9200/9201与F35。

本课独立环境显式关闭ES认证，入口只绑定回环，不沿用F35凭据；Docker网络内服务仍可访问，回环不是权限控制。仅用于本机合成数据实验。部署所需TLS、读写权限继续按F35设计，本课不宣称进行了安全部署验证。

init只用于没有本课.local和卷的全新环境，拒绝覆盖；start用原卷重启。不要将新密码文件混用到旧PG卷。每个--out必须是尚不存在的目录。实验中保持没有其他写入者。

## 手工路径：原生SQL、REST、Java

与下一节自动路径二选一。每步都检查响应和业务字段，不符时先停下恢复前提。`requests.sh`只是展开常用SQL/curl，`to-bulk.py`把SQL输出的op/id/document转换为ES Bulk NDJSON；它们不读取事件或自动补齐。

```bash
bash labs/f36/requests.sh prepare /tmp/f36-manual
bash labs/f36/requests.sh inspect
# 重复导入同一文件：index p01/p02均200 updated；文档仍为两份
bash labs/f36/java.sh /tmp/f36-manual/initial.ndjson
bash labs/f36/requests.sh refresh
bash labs/f36/requests.sh related /tmp/f36-manual
bash labs/f36/requests.sh inspect
# SQL已改城市名、删p01的游船标签，ES仍旧；再完整覆盖
bash labs/f36/java.sh /tmp/f36-manual/related.ndjson
bash labs/f36/requests.sh refresh
bash labs/f36/requests.sh inspect
```

prepare应返回两条index/201、errors=false；不要只看HTTP200。重复Java导入应两条200/updated，固定_id避免新增两份文档。related后所有HZ景点的城市展示名应改为“杭州（旅游展示名）”，p01标签应只剩亲子；attraction自身未修改也需重投影。以完整_source核对，观察窗不显示城市展示名或标签。

然后启动两个SQL会话。终端A保持打开：

```bash
docker compose -f infra/f36/compose.yaml exec postgres psql -X -qAt -v ON_ERROR_STOP=1 -U travel -d travel_f36
```

在psql里输入：

```text
\i /lesson/snapshot-begin.sql
```

显示repeatable read与2；第一条SELECT固定读视图，并将两行投影输出到容器/tmp/f36-snapshot.ndjson。不要退出、提交或另开会话代替A。终端B：

```bash
bash labs/f36/requests.sh change
```

这是单个事务，改p01=6500分、p02=closed、新增p03=3000分。回A输入：

```text
\i /lesson/snapshot-end.sql
\q
```

仍在同一读视图的再次导出应相同，最后才COMMIT。在终端B继续：

```bash
docker compose -f infra/f36/compose.yaml cp postgres:/tmp/f36-snapshot.ndjson /tmp/f36-manual/snapshot.ndjson
docker compose -f infra/f36/compose.yaml cp postgres:/tmp/f36-snapshot-again.ndjson /tmp/f36-manual/snapshot-again.ndjson
cmp /tmp/f36-manual/snapshot.ndjson /tmp/f36-manual/snapshot-again.ndjson
python3 labs/f36/to-bulk.py /tmp/f36-manual/snapshot.ndjson > /tmp/f36-manual/snapshot.bulk.ndjson
curl --fail-with-body -sS -X POST 'http://127.0.0.1:20036/tut-f36-attractions-write/_bulk?require_alias=true' -H 'Content-Type: application/x-ndjson' --data-binary @/tmp/f36-manual/snapshot.bulk.ndjson
bash labs/f36/requests.sh refresh
bash labs/f36/requests.sh inspect
bash labs/f36/requests.sh delta /tmp/f36-manual
bash labs/f36/java.sh /tmp/f36-manual/delta.ndjson
curl --fail-with-body -sS http://127.0.0.1:20036/tut-f36-attractions-read/_doc/p01
bash labs/f36/requests.sh inspect
bash labs/f36/requests.sh refresh
bash labs/f36/requests.sh inspect
```

cmp成功无输出。旧快照导入后搜索还是p01/6000、p02/0，没有p03。delta只用本课事务已知键p01/p02/p03，不是自动发现的全站变更；Java输出index p01 200 updated / delete p02 200 deleted / index p03 201 created。refresh前GET p01已6500，SEARCH仍是旧集合；refresh后p01/6500、p03/3000。全字段要与当前SQL投影对齐，不能只看“两份”这个相同计数。若发生物理删除，普通当前行查询无法给出已消失键，本课不验证其自动捕获。

## 既有观察窗

手工路径另开JDK25终端，在projects/travel-search运行：

```bash
ES_URL=http://127.0.0.1:20036 ES_INDEX=tut-f36-attractions-read ES_CA_FILE= ES_API_KEY_FILE= APP_PORT=18086 java -Xms64m -Xmx192m -jar backend/target/travel-search-0.7.0.jar
```

打开http://127.0.0.1:18086/，使用默认西湖/HZ/200元/30.25,120.15/3km。prepare后两张卡p01=60.00元/p02=0元；快照缺口和delta未refresh时仍如此；refresh后p01=65.00元/p03=30.00元。Browser→Java→ES，复用F07，无新增Controller/前端。接口原始整数分与esRequest可独立REST重放。相同输入见search/f36/search.json；新增tags/city_name用完整REST_source核对，不冒称观察窗已显示这些字段。停止此Java用原终端Ctrl+C。

## 自动验收与重做

自动run会启动/停止自己创建的Java，18086必须空闲；不与手工Java并行。首次和点名清理后分别执行，输出目录不能复用：

```bash
python3 labs/f36/lab.py run --out /tmp/f36-reader-round1
python3 labs/f36/lab.py cleanup --out /tmp/f36-reader-cleanup1
python3 labs/f36/lab.py run --out /tmp/f36-reader-round2
python3 labs/f36/lab.py cleanup --out /tmp/f36-reader-cleanup2
python3 labs/f36/lab.py down --out /tmp/f36-reader-down
```

3案例：c01三表→两份文档/重复导入；c02关联变动/字段残留/完整覆盖；c03两个真实SQL会话的快照缺口、受控补齐与GET/SEARCH分层。每轮教学REST22＋Java搜索4＋Java Bulk3，身份/guard/清理和可选浏览器附加另计，准确计数以summary.json为准。作者--observer附加Playwright，不是读者依赖。

cleanup先核对集群/库/版本、拒绝外来业务索引，只删除tut-f36-attractions-v001及其alias、DROP SCHEMA f36 CASCADE并核对不存在；保留其他schema、系统索引、数据卷和密码文件。down只移除本课容器/网络并保留卷，未停止读者自行启动的Java。中断后先关闭仍打开的快照会话，再用新--out执行cleanup重来。彻底重置需要另行明确处理本课两卷与.local，不能混用身份；无需删除卷就能完成本课两轮。

手工物理删除、事务中多个表事件的路由、可靠日志位置、故障重放/乱序保护、持续写入追平、生产吞吐未验证，分别留给F37–F42/后续课。真实记录见[review/f36](../../review/f36/README.md)。
