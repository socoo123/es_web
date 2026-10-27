# F28 · 三节点拓扑与持久首启真实验收

[正文](../../../../framework/f28.html) · [本机入口](../../labs/f28/README.md) · [脚本](../../labs/f28/lab.py) · [完整作者自审](../../../../docs/framework-review/20261027-f28-cluster/content-review.json)

两轮从全新专属卷开始，均通过首次引导→立即移除bootstrap重建→导入/三入口搜索→保留卷完整重启→错误独立集群/只改seed不合并→原卷恢复。中间[点名删索引](between-rounds/index/summary.json)、[点名删四个专用卷](between-rounds/volumes/summary.json)后重做。正式收据：[round1](round1)、[round2](round2)，每阶段events.jsonl是实际HTTP与Docker命令，summary.json分别计数。

| 轮次 | 原集群UUID | 错误单节点UUID | 稳定首启 → 完整重启 → 错误恢复master | 教学HTTP / 等待HTTP |
| --- | --- | --- | --- | --- |
| 1 | `J73brxk7TIC76PSrq_OdDw` | `M9WhjhTbScGWRFuoot0r9w` | travel-f28-02 → travel-f28-03 → travel-f28-02 | 72 / 60 |
| 2 | `R5g1NciQR3-tPFU7KtduAQ` | `53v6HVq8T2-WbUTW1BV4xg` | travel-f28-03 → travel-f28-03 → travel-f28-02 | 72 / 62 |

每轮3案例/72教学HTTP：c01为first12＋prepare14=26，c02 restart22，c03 mistake24。72条中包含5次Java接口调用（依次502/200/503/200/200）；服务内调用client.search，底层连接重试报文未抓包计数，不能将5次接口调用当成精确网络报文数。手工curl、浏览器与其他验收请求不计入72。等待HTTP另计，启动时连接未就绪属于等待记录，不伪装业务成功。

三端点19228/19229/19230均为ES9.4.0/Lucene10.4.0；3个master候选，es1仅master，es2 master/data/ingest，es3 master/data。稳定配置无initial_master_nodes/single-node，每轮三个原node ID在移除引导、完整重启和错误恢复后均相同。当选master与主副归属允许变化。

固定6份景点、2主每主1副、strict、whitespace、refresh=-1。Bulk6项201/created；mapping/settings、count6、全6份_source精确核对。4行STARTED的每组p/r分别在es2/es3，es1无业务分片，主分片docs总计6。经三个HTTP入口均命中p01/p02；Java完整DSL与固定REST相等并重放，比较ID/total/字段/score。

错误案例另挂新wrong-data，原n3-data保留：同cluster.name却不同UUID、错误集群仅1成员且本课索引404。修复seed并保留错误目录，第一轮实际触发加入验证拒绝，第二轮实际保持独立且记录不会再发现其他节点；[两种诊断和恢复](../../../../docs/framework-review/20261027-f28-cluster/content-review.json)分别记录。仅删除这个没有导入业务文档的专用错误空卷，挂回原n3-data后，核对原UUID/三个node ID/全部数据/REST与Java结果。

[启动/清理保护](guards/summary.json)：已有卷时first拒绝、缺少--delete-f28-data时reset拒绝，均在HTTP/Compose变更前停止。探索失败与恢复保留在[attempts](attempts/README.md)，大型探索events无损gzip并保留原始SHA，不混入正式通过。

[构建/运行版本](runtime.json)：Boot4.0.8/Temurin25.0.4.1+1/Java与Rest5 Client9.4.8/Maven3.9.11；clean package和依赖树实际成功，无测试源，不称No tests to run为测试通过。ES内置JVM26.0.1+8与应用JDK分列。既有F07 index.html/shell.js/shell.css源码、包内与HTTP字节相等；没有新增Controller或前端。复用的本机观察窗仍标F07，配置只切ES_URL到19229、ES_INDEX到本课索引。

实际浏览器观察另见[8次Java调用与8次作者REST重放](../../../../docs/framework-review/20261027-f28-cluster/shell-review.json)，不计教学72条。双主题/1440与390，预算200元为p01/p02、60元/0元；改50元只p02。浏览器直连ES=0，展示原文/DSL/输入与响应一致。本课浏览器未重做故障注入；缺索引502与计划停机503/恢复由两轮脚本实际核对。

三进程位于同一Docker VM（约3.81GiB/2CPU），每节点256MiB堆/768MiB容器限制；不能证明跨机器容灾、负载或容量。ingest只角色核对，未执行管道。未测随机故障/多数选举、routing/扩缩容、TLS/权限、CDC、多地址客户端切换。最终点名清理和原安全节点状态在本课审阅目录另存workspace-state.json；卷和镜像保留。
