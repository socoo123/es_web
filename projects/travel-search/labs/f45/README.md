# F45 · 从空资源独立复现

先做[TASK.md](TASK.md)，用[SUBMISSION.md](SUBMISSION.md)提交预测、实现、结果与解释，再看[F45正文](../../../../framework/f45.html)的参考实现。run是作者参考实现的复现入口；跑通脚本不能替代你独立设计DSL、投影和恢复方案。

独立项目es-framework-f45，PG15445、Kafka29345、Connect18345、ES20945/20946、F07观察窗18095，全部只绑定回环。只放合成教学资料；ES/Kafka/Connect无认证且明文，不是部署安全方案。两ES节点均为master/data/ingest，两个业务索引均1主1副，不能推导容忍任意一节点失效：两投票节点的多数仍为2。容器同一Docker VM，建议Docker至少4GiB可用内存且不要同时运行其他大实验；本轮与已有9201并行的实际限制见review。

版本ES9.4.0/Lucene10.4.0、PG17.5、Kafka4.0.1、Debezium3.3.1.Final（内含Connect4.1.0）；镜像固定digest。Boot4.0.8/JDK25.0.4.1+1/官方Java与Rest5 Client9.4.8、Kafka客户端4.0.1。ES bundled JVM另读，应用必须完整JDK25。需要Docker Compose、Python3.9+、curl，设置JAVA_HOME/PATH后，从仓库根开始：

```bash
cd projects/travel-search
python3 labs/f45/lab.py init --out /tmp/f45-init
python3 labs/f45/lab.py start --out /tmp/f45-start
cd backend
./mvnw -B -ntp clean package dependency:build-classpath -Dmdep.outputFile=target/f45-classpath.txt
cd ..
backend/mvnw -B -ntp -f labs/f45/pom.xml dependency:build-classpath -Dmdep.outputFile=target/projection-classpath.txt
bash labs/f45/java.sh compile
```

必须等start成功退出再执行后续实验。init只生成本课.local秘密（目录0700，文件0600），已有.local或具名卷时拒绝覆盖；秘密不进入URL/证据/提交。start首次仅es1使用bootstrap.yaml，记下UUID后移除首启配置并等待两节点；原卷重启只用基础compose。PG管理员与受限CDC口令分别生成，连接器使用FileConfigProvider。

## 参考实现，两轮与清理

所有out必须是不存在的新目录；一次只运行一个F45任务/来源写入者。run要求schema、业务topic、组与两个业务索引为空，先通过快照投影8条，再做三个案例。只删本课索引或只重置组都不算重做：

```bash
python3 labs/f45/lab.py run --out /tmp/f45-round1
python3 labs/f45/lab.py cleanup --out /tmp/f45-cleanup1
python3 labs/f45/lab.py run --out /tmp/f45-round2
python3 labs/f45/lab.py cleanup --out /tmp/f45-cleanup2
python3 labs/f45/lab.py down --out /tmp/f45-down
```

cleanup停本课连接器、清其来源offset后删除连接器，删除本课topic/消费组、slot/publication/schema/CDC角色、两个索引与附属alias，确认资源消失；保留本课秘密、具名卷与Connect内部topic。down不带-v，不清理其他项目。中断后先保存证据、解除写block，再cleanup；已有业务状态不能直接run覆盖。作者`--observer`还需要Playwright与Chromium；普通读者不需安装测试工具。

## 手工对照

独立挑战可仅启动基础设施，然后按自己的模型导入。`prepare`是完整参考搭建，会直接采用随课mapping/alias/连接器并导入初始8条；查看自己的答案后再使用。之后可以发送search/f45中的完整DSL并调用Java：

```bash
python3 labs/f45/lab.py prepare --out /tmp/f45-prepare
curl -sS -H 'Content-Type: application/json' 'http://127.0.0.1:20945/tut-f45-attractions-read/_search?allow_partial_search_results=false' -d @search/f45/attractions.json
bash labs/f45/java.sh search attractions
bash labs/f45/java.sh inspect
```

酒店固定逐晚表→候选投影与同报价条件的完整逻辑在lab.py的hotels方法中，自动run实际执行；query与nested sort使用同一完整filter，inner_hits返回合格报价。本课最多2个offer/酒店，inner_hits size10完整覆盖，超出这个小样本范围需重新设计完整性检查。正文给出逐晚人工核对。

同步手工故障（在prepare之后；预期失败单独执行，不放进set -e的整段命令）：

```bash
docker compose -f infra/f45/compose.yaml exec -T postgres psql -X -v ON_ERROR_STOP=1 -U travel -d travel_f45 < data/f45/changes.sql
bash labs/f45/java.sh inspect
bash labs/f45/java.sh events 10
curl -sS -X PUT -H 'Content-Type: application/json' http://127.0.0.1:20945/tut-f45-attractions-v001/_settings -d '{"index.blocks.write":true}'
bash labs/f45/java.sh drain 10
```

先等inspect.end=10，并在events核对真实event_id=1..10/实体/修订号及来源；这时唯一业务写入者已经暂停。next应仍8；drain失败非零，条级403，不能略过此检查。恢复：

```bash
curl -sS -X PUT -H 'Content-Type: application/json' http://127.0.0.1:20945/tut-f45-attractions-v001/_settings -d '{"index.blocks.write":null}'
bash labs/f45/java.sh drain 10
curl -sS http://127.0.0.1:20945/tut-f45-attractions-v001/_doc/n01
bash labs/f45/java.sh search attractions
curl -sS -X POST http://127.0.0.1:20945/tut-f45-attractions-v001/_refresh
bash labs/f45/java.sh search attractions
bash labs/f45/java.sh replay /tmp/f45-prepare/initial-documents.json
```

refresh=-1便于确定性观察：恢复后GET先见45元，显式refresh前搜索仍60元；随后capstone只剩n01/45元。replay使用原快照文本的同一修订号/哈希，不重新标版本。8条旧快照均noop，n02逻辑删除标记仍在。消费者手动assign单分区、禁自动commit、ES全部条级成功后才提交next；本机文件锁防止同目录两个worker。没有把ES和Kafka改成分布式原子事务；写后提交前崩溃仍可能重复，本课通过原始快照重放验证幂等/旧版本保护，没有注入任意进程崩溃。

## 现有展示壳

另一个终端启动，打开http://127.0.0.1:18095/，保持HZ/200元/3km，名称输入“江岸”：

```bash
ES_URL=http://127.0.0.1:20945 ES_INDEX=tut-f45-attractions-read ES_CA_FILE= ES_API_KEY_FILE= APP_PORT=18095 java -Xms32m -Xmx160m -jar backend/target/travel-search-0.7.0.jar
```

路径为浏览器→原F07 Java接口→ES。初始5条n01/n02/n03/n06/n08，恢复后4条且n01为45元。旧壳没有无障碍/时长控件，也仍采用match OR/ID排序；新增完整需求由REST和独立官方Java入口严格核对，不把旧壳的5→4条称为新DSL的2→1条。酒店用REST/Java观察，不新增前端或Controller。停止观察窗用Ctrl-C；Pages只承载教程。

边界：这是一条景点PG单表完整outbox链、一个业务topic/单分区、单本机消费者、合作写入者、冻结来源验收；酒店是静态两晚合成快照，非实时可订。未重新验证所有中文/评分/安全/多表/在线重建/性能能力，也未测试跨机器HA、任意崩溃、长停机/WAL耗尽或跨分区事务。实际[两轮证据](../../review/f45/README.md)与[阅读记录](../../../../docs/framework-review/20261101-f45-capstone/README.md)分别保存。
