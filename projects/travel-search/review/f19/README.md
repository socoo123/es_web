# F19 · 真实ES与Java两轮

[手工入口](../../labs/f19/README.md)、[正文](../../../../framework/f19.html)。本课隔离19219/tut-f19-attractions；12份虚构资料，standard逐字中文；一主零副本/strict/refresh=-1，无插件。使用本地已有官方ES9.4.0镜像，不冒充重新下载。

[两轮汇总](es-java-review.json)和round-1/round-2分别保存完整JSONL请求/原始REST响应与Java客户端结构。每轮92条教学=16+20+8+48；附加39条=12份_source＋重复建索引1＋19非法输入＋字段错误/恢复6＋空词流1。两端点名清理各2另计；第一轮结束缺索引502与第二轮同Java进程恢复各1另计。Java内部ES请求、构建、探活、浏览器单列，不称为92条。

- 01：green、Bulk12全created/errors=false、count12、完整实际mapping/settings、五个字的token/position/offset与存储词项；精确1/短语3/名称AND4/简介AND2。
- 02：sum/best/tie/tuned/1/3/50完整次序；双字段A+B、max、max+.1others的解释算术；三种multi_match同语义对照。整名8分与短语实际贡献、插空格少8分。夜游best/1正确、best/3/50和tuned/1误抬摄影展。
- 03：optional九份、后四0分，required五份、强制名称短语三份；山林matched变化、闭馆/异城/超预算完整条件排除。
- 04：16组实际Java DSL与固定REST文件规范化一致，重放实际搜索和解释，全部卡片/原文/票价/score/sort/total/解释结构核对。浮点容忍2e-6相对/1e-7绝对，不称为原始字节相同。
- 附加：字段description=null使匹配卡片不完整，真实502/SEARCH_INCOMPLETE；完整写回/refresh后同Java进程恢复。无新增单元测试；没有构造执行超时/部分分片失败。

[排序摘要](ranking-summary.json)、[解释摘要](explain-summary.json)是从实际响应提取的教学摘要，完整原始响应保留在两轮JSONL；两轮token/positions/offsets、完整词项、ID/次序/解释算术与Java摘要一致，内部Lucene文档编号不作业务比较。

[版本/制品与构建](runtime.json)、[HTTP与真实观察窗](../../../../docs/framework-review/20261025-f19-weights/README.md)分别记录。run.py为作者证据脚本，学习不依赖它。未认证全站质量/性能、多分片、生产安全/DB/CDC；F04–F06历史受阻不回填。
