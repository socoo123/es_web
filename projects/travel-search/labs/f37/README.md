# F37 · PostgreSQL WAL → Kafka → Java → ES

先读[正文](../../../../framework/f37.html)。本课只做单表、单分区、单消费者、主键不变的最小闭环。已实现Debezium真实快照/streaming、Java官方客户端index/delete、成功后提交消费位置与正常停启恢复。多表投影、任意乱序、DLQ和持续重建留到F39–F42。

## 初次启动与构建

需要Docker、Python3、curl、完整JDK25，先自行设置JAVA_HOME/PATH。以下在仓库根目录开始；每个--out都必须为尚不存在的目录。

```bash
cd projects/travel-search
python3 labs/f37/lab.py init --out /tmp/f37-init
python3 labs/f37/lab.py start --out /tmp/f37-setup
cd backend
./mvnw -B -ntp clean package dependency:build-classpath -Dmdep.outputFile=target/f37-classpath.txt
cd ..
backend/mvnw -B -ntp -f labs/f37/pom.xml dependency:build-classpath -Dmdep.outputFile=target/kafka-classpath.txt
```

基线：Boot4.0.8 / JDK25.0.4.1+1 / Maven3.9.11 / Java与Rest5 Client9.4.8；PG17.5-bookworm、Kafka broker4.0.1、Debezium Connect3.3.1.Final（内含Kafka4.1.0），Kafka Java客户端4.0.1。前三个新增镜像固定digest，不表示最新补丁推荐。ES9.4.0 / Lucene10.4.0 / bundled JVM26.0.1另列；实际构建与身份见[review/f37](../../review/f37/README.md)。

独立Compose项目es-framework-f37：数据库travel_f37、schema f37、publication f37_publication、slot f37_slot、topic travel_f37.f37.attraction、group f37-es-v1，ES索引tut-f37-attractions-v001与read/write alias。PG不发布宿主端口；ES20137、Kafka29137、Connect18137、Java18087均只发布回环。默认不操作9200/9201或其他课。ES显式无认证，Kafka/Connect明文无认证，是本机合成数据环境；部署权限/TLS按F35设计，不能把回环当成完整安全隔离。

init生成随机PG管理员口令与CDC口令，仅在被忽略的infra/f37/.local，目录0700、文件0600。已有.local或本课卷时拒绝覆盖。start使用原卷；不要将新口令文件混到旧数据库。连接器JSON用服务端FileConfigProvider引用，不将实际密码放在JSON、URL、浏览器、Pages或提交中。PG学习管理员travel只用于建表/授权/执行实验；连接器实际用非superuser的f37_cdc。

PG显式wal_level=logical、4 slots/4 senders、max_slot_wal_keep_size=128MB；ES1主0副、strict、refresh=-1；topic1分区1副本、cleanup.policy=delete、retention.ms=604800000。Kafka256MiB堆/16MiB清理缓冲、512MiB容器，Connect256MiB堆/640MiB容器，ES256MiB堆/768MiB容器，PG256MiB容器。不是HA/吞吐/磁盘容量配置建议。

## 手工路径：三个可解释的观察过程

与下一节自动run二选一。在独占本课数据、没有其他写入者时执行。prepare会创建两行初始资料、受限账户/publication、topic、ES索引/alias、注册连接器，等待首批Kafka快照事件，但不会消费到ES：

```bash
python3 labs/f37/lab.py prepare --out /tmp/f37-manual
bash labs/f37/java.sh inspect
bash labs/f37/requests.sh inspect
bash labs/f37/java.sh drain
curl --fail-with-body -sS http://127.0.0.1:20137/tut-f37-attractions-read/_doc/p01
bash labs/f37/requests.sh inspect
bash labs/f37/requests.sh refresh
bash labs/f37/requests.sh inspect
```

c01：inspect应有两条r，key为p01/p02；inspect是无提交的独立查看，不改变应用组。drain将两份open投影按业务键index，提交下一位置2。GET p01=6000分，refresh前SEARCH仍为空，显式refresh后p01/6000、p02/0。prepare还验证CDC SELECT成功、UPDATE因42501拒绝，以及临时REPLICA IDENTITY NOTHING导致DELETE拒绝，事务退出后默认标识与p01均恢复。表、权限与固定输入见[data/f37/setup.sql](../../data/f37/setup.sql)。

```bash
bash labs/f37/requests.sh changes
bash labs/f37/java.sh inspect
bash labs/f37/requests.sh inspect
bash labs/f37/java.sh drain
curl --fail-with-body -sS http://127.0.0.1:20137/tut-f37-attractions-read/_doc/p01
bash labs/f37/requests.sh refresh
bash labs/f37/requests.sh inspect
bash labs/f37/requests.sh delete
bash labs/f37/java.sh inspect
bash labs/f37/java.sh drain
bash labs/f37/requests.sh refresh
bash labs/f37/requests.sh inspect
```

c02：changes.sql按独立事务新增p03/3000、改p01/6500、下架p02。应出现c/u/u，Kafka已新但未消费时ES仍旧；drain之后GET p01已6500、p02为404，refresh后搜索p01/6500与p03/3000。delete.sql物理删除p03，应出现d及同key的value=null tombstone。当前默认replica identity下，d.before的非主键字段实际为零/空串占位，不能当成真实旧价格。消费者按key删除；tombstone只确认处理。累计next/end=7，refresh后只剩p01/6500。

```bash
bash labs/f37/requests.sh stop-connect
docker compose -f infra/f37/compose.yaml exec -T postgres psql -X -qAt -v ON_ERROR_STOP=1 -U travel -d travel_f37 < data/f37/positions.sql
bash labs/f37/requests.sh offline
docker compose -f infra/f37/compose.yaml exec -T postgres psql -X -qAt -v ON_ERROR_STOP=1 -U travel -d travel_f37 < data/f37/positions.sql
bash labs/f37/java.sh inspect
bash labs/f37/java.sh drain
bash labs/f37/requests.sh start-connect
curl --fail-with-body -sS http://127.0.0.1:18137/connectors/f37-pg/status
bash labs/f37/java.sh inspect
bash labs/f37/requests.sh inspect
bash labs/f37/java.sh drain
bash labs/f37/requests.sh refresh
bash labs/f37/requests.sh inspect
bash labs/f37/java.sh drain
```

c03：stop后先确认slot.active=false，再提交offline.sql；改p01/7000、新增p04/1800、删除SQL中closed的p02。比较两次positions：restart_lsn不动、current_lsn距离增长，Kafka仍7条、ES仍p01/6500。不要在Connect停机时运行requests.sh inspect，它含Connect REST，会报连接失败；用上面独立SQL观察。

start恢复原worker后，等待REST可达、connector与唯一task均RUNNING，再反复inspect，直到收到u p01/c p04/d p02/tombstone四条，不能用固定睡眠代替判断。本轮没有新增r。先看Kafka已新但ES仍旧，再drain：p02 delete:not_found可接受，它早因下架从ES移除；最终next/end=11，refresh后p01/7000、p04/1800，p02/p03 GET404。再drain处理0条，表明同组从保存的位置恢复；不证明崩溃场景没有重复。

保留的三种位置各有职责：PG slot维护所需WAL、Connect来源offset在f37-connect-offsets、Java组提交业务topic分区的下一offset。LSN不是Kafka offset，也不能跨分区比较offset作为全局业务版本。128MB仅为本课PG参数，未灌满/触发slot失效；位置差不是实际WAL文件大小。

## 持续消费与既有观察窗

drain用于暂停写入的稳定观察点。需要看到数据库更新持续进入ES时，另开终端运行：

```bash
bash labs/f37/java.sh follow
```

它使用相同组，只启动一个消费者。不要与drain并行，也不要在运行中删除topic、重置组或重建索引；用原终端Ctrl+C停止，等消费组没有活动成员后清理。apply成功后逐条commit offset+1；apply/commit抛错会退出，不会替该条继续提交。没有自动重试/DLQ/外部版本，异常后先定位原因，不冒称F40已经实现。

观察窗另开JDK25终端，在projects/travel-search执行：

```bash
ES_URL=http://127.0.0.1:20137 ES_INDEX=tut-f37-attractions-read ES_CA_FILE= ES_API_KEY_FILE= APP_PORT=18087 java -Xms64m -Xmx192m -jar backend/target/travel-search-0.7.0.jar
```

打开http://127.0.0.1:18087/，默认西湖/HZ/200元/3km，每个已refresh阶段点击搜索：初始p01/60元+p02/0元→改动后p01/65元+p03/30元→删除后p01/65元→停机仍旧→恢复p01/70元+p04/18元。浏览器→Java→ES，接口给出ID、整数分与esRequest，可REST重放；事件/位置在本课CLI核对，无新增Controller/前端。读者不开发门户。

## 自动验收、清理与重做

自动run会创建/停止自己的18087 Java进程，此端口需空闲，不与手工路径/消费者并行。作者--observer附加Playwright，不是读者依赖。

```bash
python3 labs/f37/lab.py run --out /tmp/f37-round1
python3 labs/f37/lab.py cleanup --out /tmp/f37-cleanup1
python3 labs/f37/lab.py run --out /tmp/f37-round2
python3 labs/f37/lab.py cleanup --out /tmp/f37-cleanup2
python3 labs/f37/lab.py down --out /tmp/f37-down
```

每轮3案例，38教学HTTP入口：26 ES REST＋7 Connect REST＋5 Java搜索；消费者9次官方index/delete写入另计。身份/guard五条、状态轮询、清理与浏览器附加另计。summary.json列出实际计数。assert包括原始事件、来源、key、位置、完整字段/下架/物理删除、GET与SEARCH，以及Java搜索契约的独立REST重放。

cleanup先检查本课身份、拒绝外来业务索引/topic/connector，再stop连接器、删除其source offsets（需STOPPED）及connector、非活动slot、publication/schema/CDC角色及已授予的DB CONNECT权限，删除本课topic/group与ES索引。保留三个具名卷、Connect内部topic和.local，不用down -v。若中断在Connect停机时，先start connect并等HTTP恢复；若消费者仍运行，先停止并等组不活动。清理后可重新prepare/run；初始化口令无需重建。

down只移除本课容器和网络，保留具名卷，不操作其他课程和读者手工Java。连接器镜像自身声明的匿名目录卷不是恢复检查点；checkpoint在具名Kafka卷与PG卷。本课不清理其他人的卷。

真实证据见[review/f37](../../review/f37/README.md)。正常停启不等于PG/Kafka崩溃、HA、长期保留或恰好一次；不支持主键变更、TRUNCATE、TOAST大字段、多分区/多消费者、多表投影、任意乱序与在线重建。本课没有实施MySQL链路。
