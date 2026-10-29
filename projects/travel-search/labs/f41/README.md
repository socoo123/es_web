# F41 · 持续更新重建与追平

先读[F41正文](../../../../framework/f41.html)。本课与F33受控冻结复制不同：全量快照打开期间业务仍改价/删除/新增，独立v2从已保存L接续增量，随后按明确来源fence核对并切换。v1/v2分别保留消费位置和固定写入alias，查询alias切换后继续维护两版，回滚才不会退回旧价。没有新增Controller或前端。

Docker、Python3、curl、完整JDK25；从仓库根目录开始，先配置JAVA_HOME/PATH。每个out必须是尚不存在的新目录：

```bash
cd projects/travel-search
python3 labs/f41/lab.py init --out /tmp/f41-init
python3 labs/f41/lab.py start --out /tmp/f41-start
cd backend
./mvnw -B -ntp clean package dependency:build-classpath -Dmdep.outputFile=target/f41-classpath.txt
cd ..
backend/mvnw -B -ntp -f labs/f41/pom.xml dependency:build-classpath -Dmdep.outputFile=target/projection-classpath.txt
```

等start返回成功，再执行run或手工流程。init仅首次生成infra/f41/.local（0700/随机密码文件0600）；已有.local或本课卷时拒绝覆盖，原卷重启只用start。PG管理员/CDC秘密不打印，不进URL，连接器用FileConfigProvider。CDC只读追加outbox及复制日志。独立项目es-framework-f41，回环端口PG15441、Kafka29341、Connect18341、ES20541、观察窗18091。ES无认证、Kafka/Connect明文，仅本机合成教学；部署安全沿用F35。

版本锁定PG17.5、broker4.0.1、Debezium3.3.1.Final（内含Connect4.1.0），前三镜像固定digest；ES9.4.0/Lucene10.4.0。应用Boot4.0.8/JDK25.0.4.1+1，官方ES Java/Rest5 Client9.4.8、Kafka客户端4.0.1；ES bundled JVM另行实读。两版1主0副/strict/价格long禁止coerce/refresh=-1，搜索前主动refresh。一个业务topic单分区/单副本，delete保留7天，单worker逐段消费；未提供生产常驻服务。

## 三案例自动运行与点名清理后重做

```bash
python3 labs/f41/lab.py run --out /tmp/f41-round1
python3 labs/f41/lab.py cleanup --out /tmp/f41-cleanup1
python3 labs/f41/lab.py run --out /tmp/f41-round2
python3 labs/f41/lab.py cleanup --out /tmp/f41-cleanup2
python3 labs/f41/lab.py down --out /tmp/f41-down
```

run自行启停观察窗，18091须空闲。作者`--observer`才需要Playwright，读者无需安装。三个案例：

1. c01：旧索引一次reindex初始三条作为反例；保存L=3再打开Repeatable Read并实际执行pg_current_snapshot固定视图。另一个SQL会话改p01/65元、删除p02、新增p04/45元、更新HZ城市并发完整关联投影。快照仍为p01/60、p02/0、p03/30元。v2先消费增量至backfill H=9，再载入旧全量，p01/p02 noop、p03创建；未完成快照时gate拒绝。一次复制目标仍旧价、含已删p02、缺p04。
2. c02：再改p01/70、下架p03、为p04加夜景标签。来源fence到Kafka offset12/H=13。v1=13、v2=9先拒绝；真实index.blocks.write阻断v2，403且next不动；解除block恢复到13。业务再提交p01/72和p04删除，末端15；两消费者仍停13，gate比较保存的fence投影并明确积压2，然后切查询alias至v2，暂时仍70+45元。不是最新业务瞬时强一致。
3. c03：rollback fence offset15/H=16；仅v2消费先显示72元/无p04，v1仍13则拒绝回滚。v1追到16并全字段核对后回滚，仍72元。同一Java进程贯穿。再改p01/76、同ID重开p04/48元空标签，两版到final H=19，最初快照重放全noop，再drain0。

最终四ID修订号p01=6、p02=2（删除）、p03=2（下架）、p04=5（重新开放）；原始4份、搜索2份。19个来源事件=3初始r+12文档c+4fence c，两组next都19。v2新字段price_band为free/under_50/from_50，单位CNY分；恰好5000分归from_50。最后旧版仍查询76+48元，新版保留新布局。

## 手工执行与恢复

与自动run二选一，完整顺序见[F41正文](../../../../framework/f41.html)。prepare初始化三行、两个索引/ingest alias、查询alias和连接器；snapshot特意在第二会话执行during-snapshot.sql，导出完成后再fence/消费/load：

```bash
python3 labs/f41/lab.py prepare --out /tmp/f41-prepare
python3 labs/f41/lab.py snapshot --out /tmp/f41-snapshot
python3 labs/f41/lab.py fence backfill --out /tmp/f41-fence-backfill
python3 labs/f41/lab.py drain backfill:v1 --out /tmp/f41-backfill-v1
python3 labs/f41/lab.py drain backfill:v2 --out /tmp/f41-backfill-v2
python3 labs/f41/lab.py load --out /tmp/f41-load
python3 labs/f41/lab.py gate backfill --out /tmp/f41-gate
bash labs/f41/java.sh inspect
```

step允许backlog、after-fence、after-rollback。fence保存backfill/cutover/rollback/final检查点；drain用`检查点:版本`限定offset<H；gate仅验收不切；switch cutover/rollback重新验收后才发aliases API。预期失败命令非零，不用`set -e`一口气跑过故障。先解除写block，再重复同一个drain到原H；已成功项通过版本守卫noop。初始seed只允许不存在的组，不重置已有进度。inspect/events只读；snapshot-load/drain/seed与alias协调器用同一个本机互斥文件锁。

持久job保存在被忽略的labs/f41/.local/job.json，包含代次、Kafka集群/Topic ID、L、索引UUID、snapshot路径/哈希/完成标记、各fence投影及active。快照应用不改变Kafka提交；增量ES成功后才提交各组next。job保存采用临时文件/flush/fsync/replace，但未验证任意断电。快照文件和投影版本在同一代次内固定；不要编辑旧载荷或把新事实重新标成旧版本。

业务写入者先取共同事务锁41041，再在同事务改业务、emit全部受影响实体。clock与标记保留；outbox不更新/删除。来源fence也遵守相同协议，只短暂串行化该来源事务，不锁住全量/消费/alias切换。Kafka末端本身不能证明DB到达；必须捕获真实fence。gate严格检查两组恰好H、全量完成、身份/保留范围、显式refresh后完整资料、过滤alias和固定写入目标；没有DLQ豁免或“green就通过”。小样本全查size100，超界拒绝，非生产全量扫描工具。

手工观察窗在另一个终端启动：

```bash
ES_URL=http://127.0.0.1:20541 ES_INDEX=tut-f41-attractions-read ES_CA_FILE= ES_API_KEY_FILE= APP_PORT=18091 java -Xms64m -Xmx192m -jar backend/target/travel-search-0.7.0.jar
```

打开http://127.0.0.1:18091/，默认西湖/HZ/200元/3km。六稳定点initial60+0、backfill65+45、cutover70+45、new-live72、rollback72、final76+48元。修订号/删除/城市名/标签/price_band与真实物理_index用原始响应核对；查询alias切换不改变两个ingest alias。浏览器只调用Java，不直连ES，Pages无需连本机。

cleanup核对本课身份/白名单与无活动组，停connector、清Connect来源offset并删除connector，删f41 schema/clock/outbox/publication/slot/CDC角色及数据库权限，一个业务topic、两组、三个点名索引及alias、本地job/snapshot。保留具名卷、Connect内部topic与infra.local秘密；down不带-v。先保存证据；不要只删新索引却沿用旧offset重做。

边界：单VM/broker、单topic分区、合作串行业务写入者/稳定ID/不可变完整快照/本机串行worker。未测任意断电、Kafka故障、跨分区事务屏障、HA/分布式协调、保留耗尽、生产吞吐和自动回滚。alias已改而本地job未写的崩溃窗口需要先核对真实alias再人工恢复；本课会拒绝不一致状态，未实现自动恢复。完整[真实执行](../../review/f41/README.md)与[HTTP/视觉](../../../../docs/framework-review/20261029-f41-rebuild/README.md)分列。
