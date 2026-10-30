# F42 · 延迟、对账与补偿

先读[F42正文](../../../../framework/f42.html)。DB事实、事件到达、Java投影、ES条级写入和搜索可见分别观察；同一来源边界对账，按当前事实产生新修订号补偿。复用F07观察窗，不新增Controller或前端。

Docker、Python3、curl、完整JDK25；先配置JAVA_HOME/PATH。从仓库根目录开始，每个out必须是新目录：

```bash
cd projects/travel-search
python3 labs/f42/lab.py init --out /tmp/f42-init
python3 labs/f42/lab.py start --out /tmp/f42-start
cd backend
./mvnw -B -ntp clean package dependency:build-classpath -Dmdep.outputFile=target/f42-classpath.txt
cd ..
backend/mvnw -B -ntp -f labs/f42/pom.xml dependency:build-classpath -Dmdep.outputFile=target/projection-classpath.txt
python3 labs/f42/lab.py run --out /tmp/f42-round1
python3 labs/f42/lab.py cleanup --out /tmp/f42-cleanup1
python3 labs/f42/lab.py run --out /tmp/f42-round2
python3 labs/f42/lab.py cleanup --out /tmp/f42-cleanup2
python3 labs/f42/lab.py down --out /tmp/f42-down
```

init只创建首次秘密，已有.local或卷拒绝覆盖；重启原卷只用start。秘密目录0700/文件0600，Connect用FileConfigProvider，不打印密码、不进URL/浏览器/提交文件。独立es-framework-f42：PG15442、Kafka29342、Connect18342、ES20642、Java18092；回环绑定。本机合成ES无认证、Kafka/Connect明文，部署安全回看F35。down不带-v。

版本：PG17.5、Kafka broker4.0.1、Debezium3.3.1.Final（Connect4.1.0），前三镜像digest沿用前课；ES9.4.0/Lucene10.4.0。应用Boot4.0.8/JDK25.0.4.1+1/官方ES Java与Rest5 Client9.4.8/Kafka客户端4.0.1；ES内置JVM另实读。索引1主0副/strict/价格long且coerce=false/refresh=-1；单topic单分区/单消费者组f42-v1、delete保留7天。

run自动启停观察窗，18092须空闲。作者可加`--observer ../../docs/framework-review/20261030-f42-reconcile/observe-shell.py`做真实浏览器验收，读者不需要Playwright。

1. c01：初始p01/6000、p02/0、p03/3000分。暂停connector后DB改p01/6500/revision2，end=next3仍lag0。恢复捕获后end4/next3，消费者未运行；drain4后GET6500、search6000；refresh后search6500。原始时间及探测请求独立留档，不当性能测试。
2. c02：p01改7000/revision3、删p02/revision2、新增p04/4500/revision1，来源fence H8并消费。故意只破坏本课目标：p01同revision/hash旧价6500、p02旧开放资料、p04物理缺失。开放数都3，实际ID不同。audit找到field_mismatch/deletion_residual/missing。同版p01重放noop仍错；repair按当前SQL在同一锁内emit三份更高revision，fence H12/完整复验恢复。
3. c03：再次只破坏p01价格，stale H13对账保存计划；正常业务改p01/7200/revision5。旧计划SQL原子拒绝，不emit、不直接写ES。消费后final H15再次全字段/删除/搜索复验；初始快照3项全noop，next15不动。

最终物理4份、开放3份、HZ观察窗2份；p01/v5/7200、p02/v3删除标记、p03/v1/3000、p04/v2/4500。15来源事件=3初始r＋8 document c＋4 fence c。7个稳定点initial、before-refresh、visible、before-corruption、corrupted、repaired、final；按ID顺序的金额分别60/0、60/0、65/0、70/45、65/0、70/45、72/45元。REST重放与完整字段分别检查。

手工执行与run二选一，完整SQL、REST、关键Java和每一步命令见正文。CLI：prepare初始化；pause/resume捕获；step price/changes/newer执行固定业务事务；inspect只读原始事件及位置；drain HIGH消费offset<HIGH并手动提交；fence audit/repaired/stale/final只允许首次保存；audit KEY在恰好相同next下refresh后比较；repair KEY从保存的审阅计划生成补偿；corrupt/corrupt-stale只制造本课故障；refresh主动刷新。预期拒绝命令非零，不能当成功步骤串入set -e。自动run内部实际验证预期失败。没有持续后台服务。

手工观察窗在第二终端：

```bash
ES_URL=http://127.0.0.1:20642 ES_INDEX=tut-f42-attractions-read ES_CA_FILE= ES_API_KEY_FILE= APP_PORT=18092 java -Xms64m -Xmx192m -jar backend/target/travel-search-0.7.0.jar
```

打开http://127.0.0.1:18092/。所有样本用合作事务锁42042、同事务改业务/clock/完整outbox；城市/标签变化需emit所有受影响ID。clock在物理删除后保留。source_recorded_at是事务内采集，客户端前后给提交区间；Debezium、Kafka时间与Java Instant各有定义。单VM受控暂停/主动refresh，不测自然刷新延迟或生产吞吐。

audit保留代次/Topic ID/Kafka集群ID/索引UUID、精确边界H、SQL规范快照和完整差异。最多100份，超界/分片失败/超时拒绝；物理索引含删除标记，read alias只用于游客结果。未知ID/目标版本超前拒绝自动补偿，来源变化则先新建边界。补偿检查和emit处于同一个共同事务锁内；任意旁路写入者不受该约定自动约束。worker与协调器共用本机文件锁；不支持多主分布式协调。

cleanup核对身份/资源白名单/无活跃组，停止connector、清来源offset/connector、删f42 schema/clock/outbox/publication/slot/CDC角色及DB授权、唯一业务topic/组、点名索引/alias及本地job/replay文件。保留具名卷、Connect内部topic及infra.local秘密；不接触前课/9200/9201。先停手工服务与worker，保存证据。

未验证任意断电、HA、跨分区一致快照、保留耗尽、大规模扫描、自动修复未知/超前目标、自然可见性SLO和容量。来源投影本身错了需要修算法/新版本或重建；不能用同一份错误算法“独立证明”正确。已固定字段对照人工核对。真实执行见[review/f42](../../review/f42/README.md)，[图解/HTTP/视觉](../../../../docs/framework-review/20261030-f42-reconcile/README.md)分列。
