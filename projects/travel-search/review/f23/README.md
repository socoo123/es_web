# F23 · 酒店、房型与offer真实两轮

[正文](../../../../framework/f23.html) · [读者入口](../../labs/f23/README.md) · [内容/图解/HTTP与实际截图](../../../../docs/framework-review/20261026-f23-model/README.md)。只实施F23；F24未开始。

ES9.4.0/Lucene10.4.0，独立19223，四索引tut-f23-hotels/object/nested/offers，一主零副本/strict/refresh=-1、无插件。固定3酒店/5房型/8报价；同一catalog生成四投影，CNY分/USD美分，单晚2026-11-01、快照2026-10-26。rooms为nested的投影中rates仍为object，只作完整明细取回；组合报价条件在独立offer根文档执行。

| 最终jar验收 | round1 | round2 |
| --- | --- | --- |
| prepare：版本、插件、四索引创建/green/Bulk/刷新/count/mapping/settings/docs统计/全部_source | [38 HTTP](round1/prepare.json) | [38 HTTP](round2/prepare.json) |
| boundaries：查询单位/作用域/房型GET404/币种与两层状态反例/恢复 | [14 HTTP](round1/lookup.json) | [14 HTTP](round2/lookup.json) |
| updates：nested与offer改价、旧版本409、错根404、更名四副本及精确恢复 | [28 HTTP](round1/updates.json) | [28 HTTP](round2/updates.json) |
| Java与实际DSL重放：5 mode，ID/完整_source/排序/total一致 | [10 HTTP](round1/java.json) | [10 HTTP](round2/java.json) |
| 附加：重复创建400、Bulk17项409、类型/strict400、5非法Java输入400、计数未增 | [19 HTTP](round1/errors.json) | [19 HTTP](round2/errors.json) |
| 每轮前点名DELETE/GET404 | [8 HTTP](round1-cleanup/cleanup.json) | [8 HTTP](round2-cleanup/cleanup.json) |

每轮90教学HTTP＋19附加；Java内部5次ES搜索另计，清理/探活/浏览器另计。[轮间缺索引502](between-rounds.jsonl)后同Java进程恢复。原始请求/响应在各round目录同名.jsonl，不用截图替代ID与数值核对。

实际root数3/3/3/8，Lucene live3/3/8/8。nested单字段直接根查询0，加path查询命中酒店h01，完整_source仍有r101/r102。GET nested/_doc/r101是404，offer/_doc/o101是200。完整双床/两人/含早/可退/CNY/active/open/服务日/700元条件命中[o101,o201]；删currency多o103 USD、删offer_status多o202 closed、删hotel_status多o301 paused，恢复重回2条。任意房型550元返回[o102,o104,o203]、酒店[h01,h01,h02]，明确3报价不等于3酒店。

nested改o101 60000→63000：只h01根版本增加，h02/h03版本与_source不变；两轮实际_segments均观察旧段live5/deleted3、新段live3/deleted0，live总数8。固定源码支持整个h01根＋2房型块重索引；deleted受merge影响不是持久写放大计数。独立offer仅o101版本变化，其余7根完全不变。酒店主文档更名不传播，明确update_by_query实际updated4/failures空/零冲突；随后恢复原价和原名，所有_source逐份等于固定文件。

[探索与修正](../../../../docs/framework-review/20261026-f23-model/attempts/README.md)保留_stats层级、GET mapping省略type=object、未refresh造成按查询恢复3成功/1冲突409，以及typed客户端省略null评分字段的原始失败。最终只归一化明确省略的max_score/_score，源文档（包括null）仍严格对比；最终两个完整干净轮次均重新执行。

[最终构建/依赖与运行](runtime.json)：Boot4.0.8/Temurin25.0.4.1+1/Java与Rest5 Client9.4.8/Wrapper3.3.4/Maven3.9.11；[Maven实际版本](maven-version.txt)。[clean package](build.log)及[dependency tree](dependency-tree.txt)通过，原始字节另有gzip；jar SHA在runtime，ES bundled JVM单列。工程没有测试源，不把“No tests to run”称测试通过；本课验证来自真实ES/Java与浏览器断言。

[真实观察窗](../../../../docs/framework-review/20261026-f23-model/shell-review.json)：1440/768/390/320×浅深×5输入=40组，另10次非法400/报价字段与房型明细不完整502/缺索引502/真实停机503及恢复，共50次真实Java调用；同一PID恢复，浏览器直连ES=0。逐卡核对根ID、原文、完整明细、币种/金额/单晚单位、计划/日期/状态/快照、完整实际DSL与typed响应；失败/改条件清空旧卡片与旧DSL。[全部场景恢复后_Source](../../../../docs/framework-review/20261026-f23-model/post-shell-canonical.json)再次逐份相同，open_contexts0。

[结束清理](../../../../docs/framework-review/20261026-f23-model/workspace-state.json)：四索引各DELETE/GET404，Java正常SIGTERM/18081关闭，F23容器和网络移除、19223关闭；F23数据卷和官方镜像保留，所有既有卷/镜像保留。既有es-study-secure节点ID、StartedAt、PID及运行状态不变，结束时healthy。

范围仅本机单节点合成小快照；不测性能/容量、多节点、生产安全、实时供价同步、逐晚库存、税费或订单事务。真实超时/部分分片失败未注入，只有代码防护。F24多条件nested/inner_hits/nested sort、F25多晚核对与F26酒店去重仍待实施。
