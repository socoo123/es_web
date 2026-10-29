# F38 · MySQL binlog独立对照

先读[F38正文](../../../../framework/f38.html)。本课复现F37同组增删改，沿用其单表Java投影、index/delete、成功后commit和既有搜索观察窗；独立MySQL profile，不需同时启动PG。新增验证ROW/FULL、权限、文件位置、内部schema history、停机DDL及空history失败/恢复。多表、任意乱序和在线重建不在本课。

## 初始化与构建

需要Docker、Python3、curl、完整JDK25，先配置JAVA_HOME/PATH。以下从仓库根目录开始，每个--out使用新目录：

```bash
cd projects/travel-search
python3 labs/f38/lab.py init --out /tmp/f38-init
python3 labs/f38/lab.py start --out /tmp/f38-setup
cd backend
./mvnw -B -ntp clean package dependency:build-classpath -Dmdep.outputFile=target/f38-classpath.txt
cd ..
backend/mvnw -B -ntp -f labs/f38/pom.xml dependency:build-classpath -Dmdep.outputFile=target/kafka-classpath.txt
```

独立Compose项目es-framework-f38，所有服务profile=mysql，SQL库travel_f38；ES20238/Kafka29238/Connect18238/Java18088仅回环，MySQL不发布宿主端口。基础服务MySQL8.4.5、Kafka broker4.0.1、Debezium Connect3.3.1.Final（内含Connect4.1.0）；前三者锁定digest。应用Boot4.0.8/JDK25.0.4.1+1/Java与Rest5 Client9.4.8/Kafka客户端4.0.1；ES9.4.0/Lucene10.4.0/bundled JVM26.0.1另列。固定制品不是当前补丁推荐。

init在被忽略的infra/f38/.local创建随机管理员、CDC口令与客户端配置，目录0700/文件0600，已有.local或本课卷时拒绝覆盖。start复用原卷，不能混入新口令。mysql客户端经defaults-extra-file读取凭据，连接器经FileConfigProvider引用，秘密不进入浏览器/Pages/URL/提交。该本机合成环境显式无ES认证、Kafka/Connect明文、MySQL连接关闭TLS，不是生产安全部署；按F35另行设计权限与TLS。

MySQL显式log-bin=mysql-bin/server-id=1838/ROW/FULL/binlog-row-value-options空、保留604800秒、GTID关闭，连接器复制客户端server.id=54038。MySQL512MiB/64MiB buffer pool、Kafka512MiB/256MiB堆/16MiB清理缓冲、Connect640MiB/256MiB堆、ES768MiB/256MiB堆，非性能或HA建议。ES1主0副/strict/refresh=-1。

## 手工路径：三个案例

与自动run二选一；独占本课数据，暂停其他写入，无follow进程。prepare创建[单表/初始行/读取账户](../../data/f38/setup.sql)、业务topic（1分区/1副本/7天保留）、history（1分区/cleanup.policy=delete/retention.ms与bytes=-1）、[ES mapping](../../search/f38/create.json)与alias、[连接器](../../cdc/f38/connector.json)，等快照入Kafka但不写ES。SQL模板的@CDC_PASSWORD@由prepare私下经stdin绑定，不要原样执行或写入实际密码。

```bash
python3 labs/f38/lab.py prepare --out /tmp/f38-manual
bash labs/f38/java.sh inspect
bash labs/f38/requests.sh inspect
bash labs/f38/java.sh drain
curl --fail-with-body -sS http://127.0.0.1:20238/tut-f38-attractions-read/_doc/p01
bash labs/f38/requests.sh inspect
bash labs/f38/requests.sh refresh
bash labs/f38/requests.sh inspect
```

c01：CDC实连SELECT成功、UPDATE1142拒绝，随后真实快照和复制成功。两个r的key为p01/p02，初始6000/0分；inspect不提交应用组。drain按业务键index，成功后提交next=2；GET已新、SEARCH仍空，refresh后p01/6000与p02/0。topic=travel_f38.travel_f38.attraction，前段为prefix、后段为数据库。

```bash
bash labs/f38/requests.sh changes
bash labs/f38/java.sh inspect
bash labs/f38/requests.sh inspect
bash labs/f38/java.sh drain
curl --fail-with-body -sS http://127.0.0.1:20238/tut-f38-attractions-read/_doc/p01
bash labs/f38/requests.sh refresh
bash labs/f38/requests.sh inspect
bash labs/f38/requests.sh delete
bash labs/f38/java.sh inspect
bash labs/f38/java.sh drain
bash labs/f38/requests.sh refresh
bash labs/f38/requests.sh inspect
```

c02：[changes.sql](../../data/f38/changes.sql)新增p03/3000、改p01/6500、p02=closed，事件c/u/u。Kafka已新/Java未消费时ES仍旧；消费后GET p01已6500、p02=404，refresh才搜索p01/p03。物理删p03得到d+同key null tombstone，ROW/FULL下before含真实旧名与3000分；Java按key删除，tombstone不另写ES。next/end=7，refresh后只剩p01/6500。

```bash
bash labs/f38/requests.sh stop-connect
docker compose --profile mysql -f infra/f38/compose.yaml exec -T mysql mysql --defaults-extra-file=/run/secrets/admin-cnf --batch --raw --skip-column-names < data/f38/positions.sql
bash labs/f38/requests.sh offline
docker compose --profile mysql -f infra/f38/compose.yaml exec -T mysql mysql --defaults-extra-file=/run/secrets/admin-cnf --batch --raw --skip-column-names < data/f38/positions.sql
bash labs/f38/java.sh inspect
bash labs/f38/requests.sh start-connect
curl --fail-with-body -sS http://127.0.0.1:18238/connectors/f38-mysql/status
bash labs/f38/java.sh inspect
bash labs/f38/requests.sh inspect
bash labs/f38/java.sh drain
bash labs/f38/requests.sh refresh
bash labs/f38/requests.sh inspect
bash labs/f38/java.sh drain
```

c03：停止整个worker、保留原卷；[offline.sql](../../data/f38/offline.sql)加入source_note列、改p01/7000、新增p04/1800、删除SQL中的closed p02。停机前后同一binlog文件位置增长，Kafka仍7条、ES仍旧。停机时不要用requests.sh inspect，它含Connect REST；用独立SQL读取位置。

启动原worker后等REST和唯一task均RUNNING，再反复inspect直到u p01/c p04/d p02/tombstone到齐，不用固定睡眠猜完成。本轮无新增r，u.after.source_note=binlog-after-restart，history含ADD COLUMN；Java显式选择原搜索字段。消费后next=11，refresh后完整投影等于SQL开放行p01/7000+p04/1800，p02/p03 GET404，再drain为0。p02早因下架从ES消失，因此delete:not_found可接受。

在以上稳定状态，还可独立复现history错误与恢复：

```bash
python3 labs/f38/lab.py probe-history --out /tmp/f38-history-probe
```

保留source offsets，临时指向新建空topic f38-schema-history-empty，task FAILED并指出history缺失。原history未动；恢复原config后RUNNING，仍11事件、drain0，删除临时topic。若反例意外中断，可恢复已发布配置后清理：

```bash
python3 -c 'import json; print(json.dumps(json.load(open("cdc/f38/connector.json"))["config"]))' > /tmp/f38-connector-config.json
curl --fail-with-body -sS -X PUT http://127.0.0.1:18238/connectors/f38-mysql/config -H 'Content-Type: application/json' --data-binary @/tmp/f38-connector-config.json
```

MySQL来源file/pos/row、Connect来源offset、内部schema history、Java分区下一offset不是同一对象。Java lag=0不证明来源已捕获；所需binlog和history必须仍在。保留7天不是离线复制客户端的slot，也不是磁盘容量保证；未验证过期/PURGE/长停机/崩溃/GTID切换。

## 持续消费与观察窗

```bash
bash labs/f38/java.sh follow
```

与drain同一组，只启动一个。apply/commit异常退出不越过该条；没有自动重试、DLQ或旧写保护。原终端Ctrl+C停止，等消费组无活动成员再清理。另开JDK25终端：

```bash
ES_URL=http://127.0.0.1:20238 ES_INDEX=tut-f38-attractions-read ES_CA_FILE= ES_API_KEY_FILE= APP_PORT=18088 java -Xms64m -Xmx192m -jar backend/target/travel-search-0.7.0.jar
```

打开http://127.0.0.1:18088/，默认西湖/HZ/200元/3km。五稳定点为初始p01/60元+p02/0元→改动p01/65元+p03/30元→删除p01/65元→停机仍旧→恢复p01/70元+p04/18元。浏览器→Java→ES；响应esRequest可REST重放。事件/位置/history由CLI/REST核对，不新建管理页面或前端。

## 两轮、清理与重做

```bash
python3 labs/f38/lab.py run --out /tmp/f38-round1
python3 labs/f38/lab.py cleanup --out /tmp/f38-cleanup1
python3 labs/f38/lab.py run --out /tmp/f38-round2
python3 labs/f38/lab.py cleanup --out /tmp/f38-cleanup2
python3 labs/f38/lab.py down --out /tmp/f38-down
```

run包括三案例与history反例，并启动/停止自己的18088搜索进程，该端口需空闲。作者--observer额外使用Playwright，读者不需要安装浏览器验收工具。每轮HTTP与9次消费者index/delete写入分列统计，见summary；身份/轮询/清理/浏览器附加另计。

cleanup校验本课身份，拒绝外来业务索引/topic/connector，stop连接器后清其source offsets及connector，删travel_f38数据库/f38_cdc账户、业务/history topic/Java group/ES索引及alias。保留三个具名卷、Connect内部topic和.local；down不带-v，仅移除本课容器/网络。停着的Connect需先start再清理，自己的follow/观察窗先Ctrl+C停止，确保组无活动成员。不要只删除索引却保留消费位置，或只删除history却保留来源offset。

真实验收见[review/f38](../../review/f38/README.md)。单表、单分区/单消费者、稳定主键、正常worker停启；没有任意乱序/失败重放/HA/GTID切换/多表投影/在线重建/性能验收，不宣称恰好一次。
