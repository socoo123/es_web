# F43 · 负载与容量

先读[F43正文](../../../../framework/f43.html)。固定语料和资源，分别比较导入、搜索加改价、实际分片/节点布局，再观察受控429与恢复。复用F07观察窗；无新Controller、无前端开发、无SQL/CDC服务。

Docker、Python3（仅标准库）、完整JDK25；配置JAVA_HOME/PATH。从仓库根目录开始，每个out必须为新目录：

```bash
cd projects/travel-search
python3 labs/f43/lab.py start --out /tmp/f43-start
cd backend
./mvnw -B -ntp clean package dependency:build-classpath -Dmdep.outputFile=target/f43-classpath.txt
cd ..
bash labs/f43/java.sh compile
python3 labs/f43/lab.py run --out /tmp/f43-round1 --warmup 3 --seconds 15
python3 labs/f43/lab.py cleanup --out /tmp/f43-cleanup1
python3 labs/f43/lab.py run --out /tmp/f43-round2 --warmup 3 --seconds 15
python3 labs/f43/lab.py cleanup --out /tmp/f43-cleanup2
python3 labs/f43/lab.py down --out /tmp/f43-down
```

独立es-framework-f43，n1:20743/n2:20744/观察窗18093，全部回环绑定；本机ES无认证。每节点1 CPU、768MiB容器内存、256MiB堆、node.processors=1。n1为master/data/ingest，n2仅data/ingest，只有一个master候选，非HA。版本ES9.4.0/Lucene10.4.0、Boot4.0.8/JDK25.0.4.1+1、官方Java与Rest5 Client9.4.8；ES bundled JVM另读。镜像digest锁在Compose。

start仅在卷均不存在时使用bootstrap覆盖，保存本课cluster UUID后移除首次名单并重启原卷；已有卷无身份文件拒绝自动首启。原卷重启仍用start。所有CLI命令共用本机非阻塞文件锁，不支持多主协调。run要求单节点和干净的本课用户索引；运行中不接受其他手工写入。18093必须空闲。监控、全字段核对和浏览器都与正式负载窗口分列。

1. c01：确定性f43-v1语料，2000/100/1→10000/100/1→10000/500/1→10000/500/4（份数/批次/并发），每项重建tut-f43-import。1主0副、strict、price long/coerce=false、refresh=-1。Java读取语料和最多500份warmup不计时，计时包括线程启动/调度、组装、序列化、网络、ES确认和显式重试；refresh/Java搜索/逐份核对在计时后。源字节不是完整wire字节，JIT未保证稳态。
2. c02：同10000份，每项重新导入，显式refresh=1s。依次1节点1主0副/4搜索0更新、相同布局4搜索1更新、8搜索1更新、1节点2主0副/4+1、2节点2主0副/4+1、2节点2主1副/4+1。实际布局必须STARTED且分布节点数正确。更新唯一线程每批20份完整index覆盖，只改价格为7000+(批序号%100)*10分。搜索契约不变：西湖/HZ/20000分/3km，2500命中，首页p000001/5/9/.../37。价格以最后确认记录为准。
3. c03：停n2，原卷重启n1并临时indexing_pressure.memory.limit=1kb；批500、并发1写2000份。真实HTTP429，4批各初次+3重试，有限全抖动50/100/200ms；失败不计成功。移除覆盖、核对正常限额与同cluster UUID，批100/并发1重放，2000份全部_source与500命中验证。受控限额不是自然过载阈值。

正式闭环窗口默认预热3秒/发出15秒，最长可设预热30秒/窗口120秒。每个worker一次仅1条请求在途，固定HTTP连接；延迟从构造前到解析后，含成功/失败原始样本。按起始时间分预热与正式，正式起点后发出、截止前开始的请求全部等待结束；分母含尾部排空。p50/p95/p99用nearest-rank。慢响应会降低发出速率，不能测独立到达流量的完整排队等待或发布该模型的SLO。监控每秒采样，before/after计数器区间含预热、监控与边界观测，不能当作精确15秒账本。

run保存确定性JSONL与哈希、环境/节点JVM、实际容器配额、每批逐尝试错误、客户端样本、节点资源与线程池/写入压力/GC/CPU计数器、每配置索引统计、实际布局、最终完整核对。两个稳定点自动启停F07观察窗，在负载窗口外实连核对REST↔Java；作者可加`--observer ../../docs/framework-review/20261030-f43-capacity/observe-shell.py`做真实浏览器观察，读者不需要Playwright。

cleanup先核对cluster UUID和用户索引白名单，只删tut-f43-import/load/pressure/warmup并确认404，停n2，恢复正常n1，保留具名卷/身份文件。down不带-v。中断在pressure阶段也可用cleanup恢复。未知用户索引、未知集群、已有卷缺身份、并发CLI会拒绝，不用广泛删除绕过。

不代表生产容量：重复合成文本、均匀分布、单热查询、固定顺序、短窗口、小工作集、唯一更新者、同Docker VM；不测冷缓存、长期merge/GC稳态、热点、端到端网站吞吐、CDC积压、开放到达率、HA或故障后余量。400/传输异常分支有保守处理但本课不注入；429为真实ES受控拒绝。功能、构建、图解、HTTP阅读、实际视觉和性能限制分别见[运行记录](../../review/f43/README.md)与[阅读记录](../../../../docs/framework-review/20261030-f43-capacity/README.md)。

完整文件：[Java Bulk/查询](java/F43Bulk.java)、[协调与混合负载](lab.py)、[节点配置](../../infra/f43/compose.yaml)、[mapping](../../search/f43/create.json)、[查询DSL](../../search/f43/query.json)、[观察窗输入](../../search/f43/shell-request.json)。
