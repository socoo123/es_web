# F30 真实实验：两轮通过

[正文](../../../../framework/f30.html) · [运行入口](../../labs/f30/README.md) · [作者内容交叉核对](../../../../docs/framework-review/20261028-f30-failover/content-review.json)。

ES9.4.0/Lucene10.4.0，四进程在同Docker VM。m1/m2仅master，m3 master/data/ingest，d1仅data；三票、两data、1主1副。原卷持久化，HTTP仅回环19430–19433，无认证。`setup/identity.json`保存首启形成后移除引导名单、UUID与node ID核对。

| 收据 | 每轮教学HTTP | 准备 / 轮询 | 最终资料 |
| --- | --- | --- | --- |
| [round1](round1/summary.json) | 75 REST＋7 Java接口 | 准备11次HTTP；轮询51次（含准备中的6次） | 6份完整_source；p01=7000分；两拷贝一致 |
| [round2](round2/summary.json) | 75 REST＋7 Java接口 | 准备4次HTTP；轮询38次 | 同上，先点名清理并从6000分重做 |

75 REST=初态12＋c01的16＋c02的15＋c03的32，包含配套字段核对和Java返回DSL重放。`events.jsonl`每行保存原请求、响应、状态码与阶段；Java接口内层ES请求、客户端重试没有抓包计数。guard/identity/cleanup/command另分标签，准备与轮询有交集，不能直接相加为教学数量。

- c01：两轮实际停专用master m1/m2，分别选出m3/m1，选举term增长；当时分片主副位置及primary term不变。6500分确认2拷贝，元数据创建与删除成功，原节点回归。
- c02：停m1+m2，活m3/d1没有master且block2、原三票配置保留；默认write策略下d1仍能读6500，改9900返回503 cluster_block_exception，建索引返回503 master_not_discovered_exception。回归后仍6500、6份资料，失败创建的索引404。
- c03：实验前保证专用master；两轮实际主片均在d1，停后原同步副本m3提升，primary term 1→2 / 2→3，master保持原身份。wait=1写7000确认1份；wait=all写9900拒绝。d1带原卷回归、PEER/DONE且两拷贝全字段一致。再停m3+d1，m1+m2保留两票和master，red/主副UNASSIGNED，业务搜索/写入503；wait=0创建元数据ack/shards_ack为true，但分片仍UNASSIGNED。点名删临时索引，再带原卷恢复并查回全部资料。

每轮UUID `Nhg5IH1VTh2DzrnUNUg5wA`及四个node ID前后相同。索引每轮重建，创建版本/settings/mapping分别记录，不能用green或总数代替字段核对。投票列表以集合比较，源顺序不构成语义。

[构建与运行](runtime.json)：Boot4.0.8 / Temurin25.0.4.1+1 / Java与Rest5 Client9.4.8 / Maven3.9.11；ES内置JVM26.0.1。clean package、依赖树、类路径通过；无测试源，不声称单元测试通过。共享Java/前端未改，三个静态资源源码/包内/实际HTTP字节一致。

首轮7稳定点×1440/390×浅深=28浏览器→Java真实HTTP，20成功与8错误，成功另做20 REST重放；[汇总](../../../../docs/framework-review/20261028-f30-failover/shell-review-summary.json)。浏览器直连ES=0。单入口m1停机与全部data离线都触发503 SEARCH_UNAVAILABLE，原因由原始REST区分。[一次独立Java诊断](java-failure-probe.log)在全data离线窗口证实客户端顶层ResponseException属于IOException；它不是额外的Web接口，SDK调用单计。

`attempts/`保留未算通过的执行：五进程资源试案、投票列表顺序比较问题、Java错误码预期修正及恢复。首次五进程的master限额384MiB不足；调整后VM压力意外OOM了原es-study-secure。停止本课资源后原容器/原UUID恢复healthy，正式改四进程；[影响与恢复说明](../../../../docs/framework-review/20261028-f30-failover/README.md)。没有原业务字段基线，不声称逐项对账。

[最终清理](../../../../docs/framework-review/20261028-f30-failover/workspace-state.json)：只删本课两个索引，Java SIGTERM且18081关闭；四容器及网络移除、四卷保留；原安全节点在恢复后采样至清理保持同PID/StartedAt/healthy。无网络分区、卷丢失、随机并发、跨机器、客户端多入口、性能或恢复时限验证。
