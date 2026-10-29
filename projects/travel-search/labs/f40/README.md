# F40 · 重放、乱序、删除保护与失败位置

先读[F40正文](../../../../framework/f40.html)。四案例沿用景点/城市/标签业务数据，新增同事务的实体clock与完整快照outbox；Debezium捕获两张追加表，经两个topic送给Java版本守卫。不是把F39三表原始事件直接换个消费者；所有示例写入者在改业务数据之前取得共同事务锁40040，再在同一事务中emit所有受影响景点。绕过协议的任意写入、并行写入和漏发关联ID不在保证范围。没有新增Controller或前端。

需Docker、Python3、curl、完整JDK25；先配置JAVA_HOME与PATH。从仓库根目录开始，每个out用一个尚不存在的新目录：

```bash
cd projects/travel-search
python3 labs/f40/lab.py init --out /tmp/f40-init
python3 labs/f40/lab.py start --out /tmp/f40-start
cd backend
./mvnw -B -ntp clean package dependency:build-classpath -Dmdep.outputFile=target/f40-classpath.txt
cd ..
backend/mvnw -B -ntp -f labs/f40/pom.xml dependency:build-classpath -Dmdep.outputFile=target/projection-classpath.txt
```

等start成功返回再prepare/run。init仅首次生成`infra/f40/.local`（0700/密码文件0600），已有目录或本课卷时拒绝覆盖，原卷重启只用start。PG管理员/CDC随机秘密不输出、不进URL；连接器通过FileConfigProvider读secret。CDC仅复制/读取两张outbox。独立项目es-framework-f40，回环端口PG15440/Kafka29340/Connect18340/ES20440，观察窗18090，自动故障代理20441。ES无认证、Kafka/Connect明文，仅本机合成教学环境，部署安全沿用F35。

锁定PG17.5/Kafka broker4.0.1/Debezium3.3.1.Final（内含Connect4.1.0）镜像digest；ES9.4.0/Lucene10.4.0、ES内置JVM26.0.1。应用Boot4.0.8/JDK25.0.4.1+1，官方ES Java/Rest5 Client9.4.8，Kafka客户端4.0.1。单主0副/strict/long禁止coerce/refresh=-1；两个业务topic与DLQ各单分区/单副本/delete保留7天。版本为固定复现制品。

## 手工三个机制案例

与自动run二选一。每段停止其他业务写入，inspect看到事件到齐再drain；只有一个F40消费者，replay/repair与drain互斥。inspect只读，drain有限处理启动时末端；未提供生产常驻服务。

```bash
python3 labs/f40/lab.py prepare --out /tmp/f40-manual
bash labs/f40/java.sh inspect
bash labs/f40/java.sh drain root
python3 labs/f40/lab.py refresh --out /tmp/f40-initial-refresh
python3 labs/f40/lab.py step crash --out /tmp/f40-change
bash labs/f40/java.sh inspect
bash labs/f40/java.sh drain root crash
```

末条故意退出40。c01初始3条r为p01/6000、p02/0、p03/3000，各revision 1。crash SQL改p01为6500并同事务发布revision 2；Java在ES成功后、Kafka commit前`Runtime.halt(40)`。GET已新，但root committed_next仍3。

```bash
curl --fail-with-body -sS http://127.0.0.1:20440/tut-f40-attractions-v001/_doc/p01
bash labs/f40/java.sh inspect
bash labs/f40/java.sh drain root
bash labs/f40/java.sh replay root
python3 labs/f40/lab.py refresh --out /tmp/f40-duplicate-refresh
python3 labs/f40/lab.py inspect --out /tmp/f40-duplicate-inspect
```

恢复重读offset 3，noop再提交next 4；replay从头但不修改应用组offset。固定ID不等于版本保护。ES以[guard.painless](../../search/f40/guard.painless)原子比较sync_revision/载荷指纹，再clear+putAll完整替换。低版本noop，同版相同指纹noop，同版异载荷失败；指纹是原始不可变JSONB字符串的SHA-256，重放保留原始字符串。ES内部retry_on_conflict与业务版本判旧分开。

```bash
python3 labs/f40/lab.py step reorder --out /tmp/f40-reorder
bash labs/f40/java.sh inspect
bash labs/f40/java.sh drain related
bash labs/f40/java.sh drain root
python3 labs/f40/lab.py refresh --out /tmp/f40-reorder-refresh
python3 labs/f40/lab.py inspect --out /tmp/f40-reorder-inspect
python3 labs/f40/lab.py step delete --out /tmp/f40-delete
bash labs/f40/java.sh inspect
bash labs/f40/java.sh drain root
bash labs/f40/java.sh replay related
python3 labs/f40/lab.py refresh --out /tmp/f40-delete-refresh
python3 labs/f40/lab.py inspect --out /tmp/f40-delete-inspect
python3 labs/f40/lab.py step reopen --out /tmp/f40-reopen
bash labs/f40/java.sh inspect
bash labs/f40/java.sh drain root
python3 labs/f40/lab.py refresh --out /tmp/f40-reopen-refresh
```

c02：root p01 revision 3改7000分；related p01 revision 4包含新城市名杭州城区/标签夜景，p02 revision 2也传播城市名。先消费related offset 0，再消费root offset 4，p01 v3 noop，保留v4完整字段；跨topic offset不能比较。物理删p01后emit v5，ES保留最小sync_deleted=true文档与revision；旧related v4不能复活。读alias DSL过滤删除标记，按ID GET会绕过filter仍读到标记；不是权限边界。重开同ID为v6/7200/空标签，clock不重置。自动run另在独立naive索引重现无守卫的旧价覆盖与删除后复活。

```bash
python3 labs/f40/lab.py step partial --out /tmp/f40-partial
bash labs/f40/java.sh inspect
bash labs/f40/java.sh drain root
bash labs/f40/java.sh inspect
bash labs/f40/java.sh drain root park
bash labs/f40/java.sh dlq
python3 labs/f40/lab.py refresh --out /tmp/f40-park-refresh
python3 labs/f40/lab.py repair-file --out /tmp/f40-repair
bash labs/f40/java.sh repair /tmp/f40-repair/reviewed-repair.json
bash labs/f40/java.sh repair /tmp/f40-repair/reviewed-repair.json
python3 labs/f40/lab.py refresh --out /tmp/f40-repair-refresh
python3 labs/f40/lab.py inspect --out /tmp/f40-repair-inspect
```

c03第一次drain预期退出1。真实Bulk p01/7500 v7成功、p02 v3的投影价格字符串broken返回400、p03/3200 v2成功；root offset7/8/9部分生效但next仍7。park重放成功项noop，p02原消息/错误/来源先写DLQ并等acks=all确认，才commit next10。DLQ key=travel_f40.f40.root_event:0:8，初次DLQ offset0；p02搜索仍旧0元，隔离不是业务修复。

repair-file只支持本课这条p02/v3故障，核对source clock仍3后从权威SQL修复价格；若有更高来源版本则拒绝把当前资料冒充旧版本。repair通过同一守卫应用为1000分/v3；重复noop，不修改源组offset。原DLQ保留pending原文，修复文件、应用结果和完整字段另存为审计，未实现生产DLQ工单/自动修复服务。DLQ与源提交之间仍有重复隔离窗口，稳定来源键用于识别重复；不宣称恰好一次。

## 第四案例、两轮与观察窗

自动run覆盖上述三案例，以及条级429仅重试失败子集、请求429预算耗尽及恢复、真实停止本课ES/原卷恢复、真实写入后丢响应确认再noop。HTTP/item 429和丢确认由回环代理明确注入，不能当真实负载拒绝或任意网络故障证明。至多4次应用层尝试，200/400/800毫秒基数加0–150毫秒抖动；409/429/502/503/504暂时重试，IO可能结果未知，重试未确认请求；仅document_parsing_exception/mapper_parsing_exception的条级400可明确park，脚本/未知/认证/配置错误停止。耗尽不提交、不自动DLQ。

```bash
python3 labs/f40/lab.py run --out /tmp/f40-round1
python3 labs/f40/lab.py cleanup --out /tmp/f40-cleanup1
python3 labs/f40/lab.py run --out /tmp/f40-round2
python3 labs/f40/lab.py cleanup --out /tmp/f40-cleanup2
python3 labs/f40/lab.py down --out /tmp/f40-down
```

run临时启动/停止18090观察窗与20441代理，端口须空闲。作者`--observer`另需Playwright，读者不用安装。手工另起观察窗：

```bash
ES_URL=http://127.0.0.1:20440 ES_INDEX=tut-f40-attractions-read ES_CA_FILE= ES_API_KEY_FILE= APP_PORT=18090 java -Xms64m -Xmx192m -jar backend/target/travel-search-0.7.0.jar
```

打开http://127.0.0.1:18090/，默认西湖/HZ/200元/3km。八稳定点：initial=60+0元，duplicate=65+0，reordered=70+0，deleted仅p02/0，reopened=72+0，parked=75+0，repaired=75+10，final=81+12。p03在SZ不入选，完整字段另查。最终root 15/related 2条，committed_next各15/2，再drain0；p01 v11/8100、p02 v4/1200、p03 v2/3200。

同一REST守卫可在c01后重放，完整请求体随课交付：

```bash
curl --fail-with-body -sS -X POST 'http://127.0.0.1:20440/tut-f40-attractions-write/_update/p01?require_alias=true&retry_on_conflict=3' -H 'Content-Type: application/json' --data-binary @search/f40/guard-example.json
```

cleanup核对本课身份/白名单及无活动应用组，停connector、清Connect来源offset/connector，删f40 schema/clock/outbox/publication/slot/CDC账户及数据库权限、两业务topic/DLQ/应用组、两份点名ES索引与alias。会删除教学DLQ审计，只在保存证据后重做。不要只删ES却留消费位置。保留具名卷、Connect内部topic和.local；down不带-v；其他项目不动。

单VM/单broker/每topic单分区/单消费者、稳定主键、合作串行写入者/不可变完整快照；未验证任意崩溃/断电、Kafka或DLQ故障、HA、并行rebalance、生产吞吐和在线重建。clock/标记保留期间守卫有效，清标记/恢复旧快照/新建索引另需重放边界。完整[执行证据](../../review/f40/README.md)与[阅读验收](../../../../docs/framework-review/20261029-f40-replay/README.md)分列。
