# F25 · 实际ES与Java两轮通过

[读者步骤](../../labs/f25/README.md) · [正文](../../../../framework/f25.html) · [图/HTTP/实际视觉](../../../../docs/framework-review/20261026-f25-stay/README.md)。仅本课隔离19225/tut-f25-offers。12份摘要/34条逐晚记录/11酒店，报价而非酒店作为结果单位。

| 阶段 | 第一次 | 点名清理后第二次 | 每轮实际HTTP |
| --- | --- | --- | --- |
| 清理 | [round1-cleanup](round1-cleanup/cleanup.json) | [round2-cleanup](round2-cleanup/cleanup.json) | 2，主流程外 |
| 准备 | [prepare](round1/prepare.json) | [prepare](round2/prepare.json) | 10 |
| 候选/摘要反例 | [candidates](round1/candidates.json) | [candidates](round2/candidates.json) | 3 |
| 两晚一间 | [stays](round1/stays.json) | [stays](round2/stays.json) | 2 |
| 两间/三晚/一晚 | [variations](round1/variations.json) | [variations](round2/variations.json) | 6 |
| 附加错误/恢复 | [errors](round1/errors.json) | [errors](round2/errors.json) | 29，主流程外 |

每轮21教学HTTP＋29附加HTTP，Java内部主流程4次ES搜索另计。逐请求完整输入/状态/原始响应在同目录同名jsonl；没有将探索收据当正式两轮。准备实测ES9.4.0/Lucene10.4.0，无插件、green，一主零副本/strict/refresh=-1，Bulk12项created、完整mapping/settings与全部_source一致。

默认8候选，o01/o04/o10=70000/65000/90000分合格；o02缺晚、o03售罄、o05入住最少3晚、o06总价130000分超预算、o12缺价。两间合格o01/o10=140000/180000分，o04第二晚库存1不足。三晚合格o04/o05/o06/o10=95000/75000/140000/135000；一晚7条合格。Java完整DSL等于固定REST，请求重放精确比较hits/源/排序/总数，唯独typed省略null评分字段做归一化；每个住宿晚、身份、金额和手工固定拒绝常量逐项核对。o01途经第二日min_stay_arrival5不影响1日入住；离店3日不检查3日晚。

29附加：重复PUT400、重复Bulk12项409、10种非法输入400、快照错配502及恢复、109候选只返回100的502及恢复、strict写入400、12根恢复。失败不返回伪成功空列表。固定上限100只用于小实验，不是大规模候选全集方案。

[运行版本/制品/打包表与HTTP资产](runtime.json)：Boot4.0.8、Temurin25.0.4.1+1、Java/Rest5 Client9.4.8、Wrapper3.3.4/Maven3.9.11；ES bundled JVM26.0.1+8另列。clean package与依赖树实际成功，没有测试源，不将No tests to run写成测试通过。build/Java/dependency/Maven日志可读版去尾空白，原文保留gzip与哈希。

[真实观察窗](../../../../docs/framework-review/20261026-f25-stay/shell-review.json)：4宽度×2主题×4场景=32组，4错误＋4恢复=40次真实Java调用；同一PID，浏览器直连ES=0。另[视觉补证](../../../../docs/framework-review/20261026-f25-stay/visual-followup.json)8次实际Java请求与15次ES操作，专门补拍错误区域；与40次主观察窗计数分列。最后[全部12源复核](final-source.jsonl)、[点名清理](final-cleanup/cleanup.json)、[运行资源清理](../../../../docs/framework-review/20261026-f25-stay/workspace-state.json)完成：索引DELETE/GET404，Java停止/18081关闭，F25容器与网络移除/19225关闭，保留卷/镜像，旧安全节点ID/StartedAt/PID/healthy与所有既有卷不变。

未测负载/性能/容量、多节点/生产安全、实时供价/CDC、税费/取消罚金/儿童/CTA/CTD、订单或扣库存；超时/部分分片失败仅代码防护、无注入。当前核对对象是固定快照，非实时可预订。F26未实施。
