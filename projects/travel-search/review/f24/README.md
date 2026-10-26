# F24 · 真实ES/Java两轮通过

[读者步骤](../../labs/f24/README.md) · [正文](../../../../framework/f24.html) · [全部验收](../../../../docs/framework-review/20261026-f24-nested/README.md) · [实际版本/构建/制品](runtime.json)。独立19224、tut-f24-object/nested；9酒店/16报价条目，根9/9、Lucene live9/25，无插件。

| 最终运行 | prepare | matching | sorting | Java↔REST | 附加errors |
| --- | --- | --- | --- | --- | --- |
| [round1](round1/prepare.json) | 20通过 | 10通过 | 6通过 | 10通过 | 13通过 |
| [round2](round2/prepare.json) | 20通过 | 10通过 | 6通过 | 10通过 | 13通过 |

每轮46教学HTTP＋13附加；Java内部5次ES搜索另计。每轮前点名清理4请求，最终清理4请求。JSONL逐次保留完整真实输入、HTTP状态与响应，JSON为汇总，不替代原始证据。

object/split都命中[h01,h02,h03,h04,h05,h07,h08,h09]，正确nested为[h02,h03,h08]；h03匹配2条、size1取o301、size10取全部，offset精确对应原_source，根源保持完整。无sort.filter使h02使用不合格10000分排首；完整filter顺序[h03,h08,h02]，价格[50000,50000,65000]分。改inner排序与空sort集合探针证明三处作用域独立，恢复后完全回归。全5份Java构造DSL与REST文件精确相等，重放只归一化null的_score/max_score省略，其余字段精确一致。

重复创建400、18个Bulk create条目409、5非法Java输入400、两类写入400且根数不增。真实观察窗另有400/源缺失502/缺索引502/停机503和恢复，同一Java PID。[探索失败](../../../../docs/framework-review/20261026-f24-nested/attempts/README.md)独立保存，不计最终两轮。

clean package/依赖树/Maven实际版本通过；Boot4.0.8/应用JDK25.0.4.1+1/官方Java与Rest5 Client9.4.8/Wrapper3.3.4/Maven3.9.11；ES bundled JVM26.0.1+8另列。工程无测试源，No tests to run不是测试通过。可读日志只去尾部水平空白，gzip保留原始字节及哈希；最终jar与实际HTTP服务资源哈希已固定。

[清理证据](../../../../docs/framework-review/20261026-f24-nested/workspace-state.json)：两索引删除并404、Java/本课容器网络关闭，旧安全节点/卷/镜像保留；单晚快照、非实时可订，性能/多节点/多晚/生产安全未测，超时与部分分片失败未注入。F25未开始。
