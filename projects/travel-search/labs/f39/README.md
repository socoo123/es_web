# F39 · Java多表关联投影

先读[F39正文](../../../../framework/f39.html)。三个案例以景点、城市、标签三表解释“行事件影响哪些景点文档”；复用F37的PG/Debezium/Kafka技术路径与既有Java搜索观察窗。F39使用独立资源，不要求启动F37或F38。没有新增Controller或前端。

需要Docker、Python3、curl、完整JDK25，先配置JAVA_HOME和PATH。从仓库根目录开始，每个--out都使用新目录：

```bash
cd projects/travel-search
python3 labs/f39/lab.py init --out /tmp/f39-init
python3 labs/f39/lab.py start --out /tmp/f39-start
cd backend
./mvnw -B -ntp clean package dependency:build-classpath -Dmdep.outputFile=target/f39-classpath.txt
cd ..
backend/mvnw -B -ntp -f labs/f39/pom.xml dependency:build-classpath -Dmdep.outputFile=target/projection-classpath.txt
```

Compose项目es-framework-f39；PG17.5、Kafka broker4.0.1、Debezium Connect3.3.1.Final（内含Connect4.1.0）镜像锁定digest；ES9.4.0/Lucene10.4.0，单主0副/strict/refresh=-1。沿用Boot4.0.8、JDK25.0.4.1+1、官方ES Java与Rest5 Client9.4.8；独立Kafka客户端4.0.1、pgJDBC42.7.8。ES bundled JVM26.0.1与应用JDK分开。制品固定用于复现。

回环端口PG15439/Kafka29339/Connect18339/ES20339/观察窗18089。init生成infra/f39/.local，目录0700/三个文件0600；有旧文件或本课卷则拒绝覆盖。管理员密码、CDC密码、JDBC投影密码不输出、不进URL；Debezium由FileConfigProvider读secret，Java从本机Properties读user/password。f39_cdc与f39_projector只有业务表SELECT，前者另有REPLICATION；管理员只用于准备/实验SQL。两账户的SELECT与写入42501拒绝均实测。本地合成数据学习环境无ES认证、Kafka/Connect明文、JDBC sslmode=disable；部署连接按F35另行设计。

## 手工路径：三个案例

与自动run二选一。仅一个消费者；每段先提交SQL，等inspect看到本段预期记录到齐再drain，期间停止其他写入。requests.sh的inspect会打印ES搜索结果、保存HTTP/SQL/完整事件到终端给出的目录；java.sh inspect直接打印所有真实信封，不改变应用组位置。

```bash
python3 labs/f39/lab.py prepare --out /tmp/f39-manual
bash labs/f39/java.sh inspect
bash labs/f39/java.sh drain
curl --fail-with-body -sS http://127.0.0.1:20339/tut-f39-attractions-read/_doc/p01
bash labs/f39/requests.sh inspect
bash labs/f39/requests.sh refresh
bash labs/f39/requests.sh inspect
```

c01：prepare执行[三表/seed/FULL/授权](../../data/f39/setup.sql)，建立publication、三业务topic和read/write alias，然后等8个快照r到齐。三张表都有稳定主键；tag_id与可变attraction_id外键分开。SQL中的密码变量由prepare私下经stdin绑定，不要原样独立执行。

初始城市HZ/杭州、SZ/苏州，景点p01/6000/HZ、p02/0/HZ、p03/3000/SZ，标签t01/p01/亲水、t02/p01/夜游、t03/p02/亲水。三topic各1分区/1副本/7天delete保留，8事件最终3份文档：p01.tags=[亲水,夜游]、p02.tags=[亲水]、p03.tags=[]。drain后GET已新、SEARCH仍空，refresh后再查。不要把跨topic打印顺序当数据库事务次序。

```bash
bash labs/f39/requests.sh shared
bash labs/f39/java.sh inspect
bash labs/f39/java.sh drain
bash labs/f39/requests.sh refresh
bash labs/f39/requests.sh inspect
bash labs/f39/requests.sh transfer
bash labs/f39/java.sh inspect
bash labs/f39/requests.sh naive
bash labs/f39/requests.sh refresh
curl --fail-with-body -sS http://127.0.0.1:20339/tut-f39-attractions-read/_search -H 'Content-Type: application/json' --data-binary @search/f39/night.json
bash labs/f39/java.sh drain
bash labs/f39/requests.sh refresh
curl --fail-with-body -sS http://127.0.0.1:20339/tut-f39-attractions-read/_search -H 'Content-Type: application/json' --data-binary @search/f39/night.json
```

c02：[shared.sql](../../data/f39/shared.sql)改HZ城市名“杭州城区”、p01价格6500、新增p03亲子标签t04，累计11事件。城市路由[p01,p02]、根事件[p01]、子事件[p03]。消费前ES仍旧，消费后完整投影与当前三表一致。转移t02到p02并改夜景，累计12事件；before明确p01、after明确p02。naive故意只更新p02.tags，夜间查询错误命中[p01,p02]；真实消费者重算旧、新两份文档，refresh后只剩[p02]。

```bash
bash labs/f39/requests.sh delete-tag
bash labs/f39/java.sh inspect
bash labs/f39/java.sh drain
bash labs/f39/requests.sh refresh
bash labs/f39/requests.sh inspect
bash labs/f39/requests.sh close
bash labs/f39/java.sh inspect
bash labs/f39/java.sh drain
bash labs/f39/requests.sh refresh
bash labs/f39/requests.sh inspect
bash labs/f39/requests.sh delete-root
bash labs/f39/java.sh inspect
bash labs/f39/java.sh drain
bash labs/f39/requests.sh refresh
bash labs/f39/requests.sh inspect
bash labs/f39/requests.sh reopen
bash labs/f39/java.sh inspect
bash labs/f39/java.sh drain
bash labs/f39/requests.sh refresh
bash labs/f39/requests.sh inspect
bash labs/f39/java.sh drain
```

c03：删t01累计14记录（d+tombstone），由before找到p01，完整index写tags=[]，父文档保留。p02下架累计15、从ES删除，GET404。物理删p03并级联t04，累计19，两表各d+tombstone；两个delete分别为deleted/not_found。p02重开累计20，按当前三表重建城市名、价格与标签，不回填旧文档。最终p01/6500/[]、p02/0/[亲水,夜景]，p03不存在。city/attraction/attraction_tag末端分别3/8/9，各自与committed_next比较，再drain0。

Java关键实现见[F39Consumer](java/F39Consumer.java)：事件先路由，再用只读REPEATABLE READ回查主库，完整index或delete，检查全部Bulk条目后仅提交当前分区下一offset。每次输出affected_ids/完整JSON/bulk_ndjson/items/提交位置；bulk_ndjson可存成末尾有换行的文件，经`POST /_bulk?require_alias=true`、Content-Type application/x-ndjson重放。完整替换会移除省略的旧字段，空集合显式[]。数据库只读事务、Bulk和Kafka提交不是跨系统事务。

## 观察窗与持续模式

另开JDK25终端：

```bash
ES_URL=http://127.0.0.1:20339 ES_INDEX=tut-f39-attractions-read ES_CA_FILE= ES_API_KEY_FILE= APP_PORT=18089 java -Xms64m -Xmx192m -jar backend/target/travel-search-0.7.0.jar
```

打开http://127.0.0.1:18089/，默认西湖/HZ/200元/3km。七稳定点：initial=60元+0元；shared/transferred/empty-tags=65元+0元；closed/root-deleted=65元；reopened=65元+0元。p03在SZ、远离搜索中心，不应入选。城市名和标签不新增界面控件，用完整ES_source和同一标签查询证明；浏览器→Java→ES可REST重放。

```bash
bash labs/f39/java.sh follow
```

持续处理同一规则，与drain互斥，只有一个消费者。手工路径每段应停止其他写入并等事件到齐；follow可用于连续改动观察，单独记录验证，不把有限阶段测试当任意并发保证。Ctrl+C停止，等待组无活动成员后清理。没有自动重试/DLQ、版本与删除保护、主键变更/TRUNCATE、在线重建、HA或大扇出性能验证；不宣称恰好一次。

## 两轮、清理与重做

```bash
python3 labs/f39/lab.py run --out /tmp/f39-round1
python3 labs/f39/lab.py cleanup --out /tmp/f39-cleanup1
python3 labs/f39/lab.py run --out /tmp/f39-round2
python3 labs/f39/lab.py cleanup --out /tmp/f39-cleanup2
python3 labs/f39/lab.py down --out /tmp/f39-down
```

run启动/停止自己的18089观察窗，该端口需空闲。作者`--observer`另需Playwright，读者不需要。每轮45教学HTTP（35 ES+3 Connect+7 Java搜索）与17消费者Bulk/20条目分列；身份、轮询、清理和浏览器附加请求另计。20条业务记录中有3条tombstone，不产生Bulk操作。

cleanup校验本课身份、资源白名单与无活动消费者；停止连接器后删除来源offset与connector，清f39_slot/publication/schema及两个只读角色、三业务topic/应用组/本课ES索引和alias。保留具名卷、Connect内部topic及.local，down不带-v。自己的follow/观察窗先停止；不要只删索引却留下消费位置。完整证据见[review/f39](../../review/f39/README.md)。
