# F44 真实运行记录

仅实施[F44](../../../../framework/f44.html)及[本课隔离实验](../../labs/f44/README.md)。run-01与点名清理后的run-02为最终同一实现的完整两轮，均通过；先前预验收失败没有混入正式结果。

| 验证 | 实际证据 |
| --- | --- |
| 构建 | [build.log](build.log)：Boot4.0.8/JDK25.0.4.1+1/官方Java与Rest5 Client9.4.8 clean package；[独立Java编译](java-compile.log)退出0 |
| 版本与输入 | 每轮identity/nodes/corpus：ES9.4.0/Lucene10.4.0、ES bundled JVM另读；f44-v1/6000份语料哈希相同，两个索引完整_source逐份相等 |
| 正式首轮 | [summary](run-01/summary.json)、[c01](run-01/c01.json)、[c02](run-01/c02.json)、[c03](run-01/c03.json)、[完整132条留档HTTP](run-01/http.jsonl.gz) |
| 清理重做 | [cleanup01](cleanup01/cleanup.json)、[第二轮summary](run-02/summary.json)、[c01](run-02/c01.json)、[c02](run-02/c02.json)、[c03](run-02/c03.json)、[完整HTTP](run-02/http.jsonl.gz) |
| 真实观察窗 | [轮1](run-01/observer.json)、[轮2](run-02/observer.json)：每轮1440浅色/390深色真实浏览器→Java→ES；每次独立REST重放实际esRequest |
| 最终退出 | [cleanup02](cleanup02/cleanup.json)、[down](down/compose.log)、[端口/卷与已有安全节点](../../../../docs/framework-review/20261101-f44-diagnosis/workspace-state.json) |

独立单节点20844/观察窗18094，只绑定回环，无认证且只用合成资料；容器1CPU/768MiB/堆256MiB、node.processors=1，同Docker VM。Compose锁定镜像digest。tut-f44-attractions为1主0副，tut-f44-fanout为2主0副；strict/whitespace/价格long且coerce=false/refresh=-1，导入后显式refresh。无SQL/Kafka/CDC、新Controller或前端。

c01每轮7条件×3普通请求与各1次profile：doc values、完整source、过滤source、summary高亮、2标签桶、1000景点桶、from2000。全部3000命中、首页p000001/3…19或深页p004001/3…19，逐项价格核对。两个标签桶各3000；景点桶1000/其他2000。普通响应字节/客户端时间/took与profile分开，原始profile文件逐项保留；[正文摘录](profile-excerpt.json)只删去部分字段，没有合成计时。

PIT先开视图，用深from取p003999锚点，再用完整sort/最新pit_id得到同一目标页并finally关闭；open_contexts增加后回原值。锚点本身仍有深分页成本。from10000+size10真实400，1/2分片实际布局与profile分片数核对。size0相同聚合三次，两次新增request_cache hit；这不是冷缓存性能实验。

c02原卷临时search.size=1/queue_size=1，并发4条有限CPU脚本查询；每轮1次200/3次429，采样active=1/queue=1、search.rejected增加3。拒绝可发生在query或fetch，完整错误树留档。tasks含有限类别f44-diagnose，hot threads实际出现PainlessScript执行栈；本课query/fetch 0ms慢日志从Docker Console采集并保留[轮1](run-01/slowlog.json)/[轮2](run-02/slowlog.json)。统计窗口包含一次1-loop预热和诊断API，不是纯4条请求的性能账本。移除覆盖后等待UUID加载和本课分片green，再核对基础搜索；正常search.size=2/queue_size=2000与运行前一致。重启前后累计计数器不相减。

c03临时request限额1kb，真实聚合429：preallocate[aggregations]需要6144字节，限额1024，内部circuit_breaking_exception；REST后request.tripped增加1，后续独立Java也429。撤销后同请求200/1000桶。search.allow_expensive_queries=false使同一slow.json返回400，普通请求仍200；撤销后transient设置与之前相等。不是自然过载/OOM或生产内存阈值。

每轮132是api函数留档的显式REST调用；另外2次独立Java search、2次观察窗Java搜索及其ES调用、2次观察窗契约的独立REST重放。根端点就绪轮询、Docker、浏览器资产和客户端底层传输没有完整计数，不声称是全部网络请求。两轮完整原始响应以无损gzip保留；[计数核对](accounting.json)从原始记录生成。

观察窗每轮3000命中、20张卡，p000001=6100分；首页20条ID/价格与独立REST相同，没有浏览器直连ES或JS异常。两次观察后Java均退出。它沿用size20/source字段，成本请求是size10/doc values，不能把两条路径当成字节相同的负载。

[预验收修正](attempts.json)记录Docker慢日志Console、重启时分片/UUID未就绪、Node Info参数和默认队列数的修正；孤立保护探针不算完整一轮。最终两轮之后没有改实验实现。最终点名删除两个索引/确认404、撤销实验设置、停止本课容器和网络，保留具名卷；原9201安全节点仍运行且healthy。没有执行全局清理。

限制：固定顺序、重复长文、小热工作集、短样本、同VM/JIT/宿主竞争；不报告稳定分位数、生产容量/SLO、自然过载/熔断、长稳态、跨机器网络或HA。没有注入写入压力429或验证自动取消。工具证据用于解释本课受控窗口，不代表任意生产故障。图解、HTTP阅读、截图实际查看和推理配置另见[阅读记录](../../../../docs/framework-review/20261101-f44-diagnosis/README.md)。
