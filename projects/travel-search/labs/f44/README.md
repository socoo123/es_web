# F44 · 请求成本与故障诊断

先读[F44正文](../../../../framework/f44.html)。本课仅启动独立 ES，复用已有 Boot 4/JDK 25 工程与 F07 观察窗；没有新增 Controller、前端或 CDC 服务。

前提：Docker、Python 3.9+、完整 JDK 25，设置 JAVA_HOME/PATH。以下从仓库根目录开始；每个 out 使用新目录：

```bash
cd projects/travel-search
python3 labs/f44/lab.py start --out /tmp/f44-start
cd backend
./mvnw -B -ntp clean package dependency:build-classpath -Dmdep.outputFile=target/f44-classpath.txt
cd ..
bash labs/f44/java.sh compile
python3 labs/f44/lab.py run --out /tmp/f44-round1
python3 labs/f44/lab.py cleanup --out /tmp/f44-cleanup1
python3 labs/f44/lab.py run --out /tmp/f44-round2
python3 labs/f44/lab.py cleanup --out /tmp/f44-cleanup2
python3 labs/f44/lab.py down --out /tmp/f44-down
```

项目 es-framework-f44，节点 f44-es/20844 仅回环；无认证，仅使用合成学习资料。固定 ES 9.4.0/Lucene 10.4.0/digest；每容器 1 CPU/768MiB、堆256MiB、node.processors=1。应用 Boot4.0.8/JDK25.0.4.1+1/官方Java和Rest5 Client9.4.8；ES bundled JVM从节点另读。单节点/同VM不代表HA或生产性能。

- c01：独立 f44-v1 的6000份固定资料，tut-f44-attractions 为1主0副、tut-f44-fanout为2主0副；strict、whitespace、价格long/coerce=false、自动refresh关闭，显式refresh后再查。逐份核对两索引完整_source。HZ/西湖3000命中，首页p000001/3/5…19，深页p004001/3…19。每种成本条件连续3次正常请求与1次profile：doc values、完整source、source过滤、高亮、2桶、1000桶、from2000。profile不参与正常耗时比较；顺序/JIT/首次加载没有隔离，不给稳定分位数。另测真实1/2分片、400窗口拒绝、PIT打开/深锚点/下一页/关闭和size0请求缓存。深锚点本身仍有from成本，不能当作免费跳页。
- c02：原卷临时重启为search.size=1/queue_size=1，仅本课节点；开本课索引query/fetch慢日志0ms。4条有限的CPU脚本查询同时发出，采集同窗口tasks/hot threads/统计和真实429。Docker镜像的慢日志写Console，用docker logs采集。tasks只关联有限类别X-Opaque-Id=f44-diagnose；hot threads是活动快照，不能直接证明某个task在某个线程。结束后关闭慢日志，移除override重启，同UUID核对，单请求正常恢复。重启前后不相减累计计数器。
- c03：临时request breaker=1kb，真实聚合429/circuit_breaking_exception；REST与Java分别确认。撤销后1000桶/其他2000项恢复。再用search.allow_expensive_queries=false得到脚本查询400，普通查询仍200，最后撤销。不是自然过载、堆耗尽或生产阈值。

运行时不要向本课集群手工写入或并行执行另一轮。run要求两个本课索引尚不存在；重复运行先cleanup。cleanup只点名删除上述两个索引，撤销本课两个transient设置并恢复正常Compose；保留具名卷。down不带-v。异常中断后也用cleanup恢复。勿把命令指向其他集群。

正文里的正常查询可直接执行：

```bash
curl -sS -H 'Content-Type: application/json' \
  'http://127.0.0.1:20844/tut-f44-attractions/_search?request_cache=false&allow_partial_search_results=false' \
  -d @search/f44/base.json
bash labs/f44/java.sh search/f44/base.json profile
```

观察窗另开终端，在本课run完成、cleanup之前：

```bash
cd projects/travel-search
ES_URL=http://127.0.0.1:20844 ES_INDEX=tut-f44-attractions APP_PORT=18094 \
  java -jar backend/target/travel-search-0.7.0.jar
```

浏览器打开 http://127.0.0.1:18094 ，使用默认“西湖/HZ/200元/3km”输入，3000命中、20张卡，p000001=61元。展示壳走浏览器→Java→ES；以返回的esRequest独立REST重放，不能把其size20/source字段与成本实验size10/docvalue_fields当成完全相同的请求。完成后Ctrl-C关闭Java。

完整文件：[实验协调](lab.py)、[Java](java/F44Search.java)、[节点](../../infra/f44/compose.yaml)、[小队列覆盖](../../infra/f44/limited.yaml)、[mapping](../../search/f44/create.json)、[基础DSL](../../search/f44/base.json)、[受控CPU查询](../../search/f44/slow.json)、[聚合](../../search/f44/aggregate.json)。

真实执行、构建与限制见[运行记录](../../review/f44/README.md)；图解和HTTP阅读另见[阅读记录](../../../../docs/framework-review/20261101-f44-diagnosis/README.md)。本课只证明请求语义、诊断与恢复，不测生产容量/长稳态/真实热点/跨节点网络/自然熔断/自动取消/索引压力429。F43的写入压力和本课搜索队列、request breaker是不同机制。
