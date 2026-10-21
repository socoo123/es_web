# F10 真实执行记录

[手工入口](../../labs/f10/README.md)、[正文](../../../../framework/f10.html)。本目录记录实际执行，预测与原始响应区分。

- [ES/Java两轮](es-java-review.json)：ES9.4.0/Lucene10.4.0；每轮独立创建/green/mapping/Bulk16项created/refresh/count16，七组REST↔Java精确DSL/完整ID/总数relation/价格/分数/完整sort/坐标与距离，default不承诺同分次序；m/km、额外3km过滤5份、四份缺价_last/补零、非法输入400，点名清理404和缺索引502。
- [构建](build.json)、[实际依赖](dependency-tree.json)：Boot4.0.8 / Temurin25.0.4.1+1 / 官方Java与Rest5 Client9.4.8 / Wrapper3.3.4 / Maven3.9.11；无单元测试，构建与真实运行分列。
- [真实观察页与停机恢复](../../../../docs/framework-review/20261021-f10-sort/shell-review.json)：真实浏览器→Java→ES；恢复使用同Java进程/Client。
- [作者手工脚本](manual-review.json)记录最终资源准备、模式/边界/Java脚本实际退出码及输出。

可选作者工具：先启动本课ES与Java且确认本课索引不存在，再运行`python3 projects/travel-search/review/f10/verify.py`。它拒绝已有本课索引，只点名删除tut-f10-attractions，不接受任意资源名。教学23条不混入作者附加读取/错误/探活/清理/浏览器重复请求。

另[NaN/Infinity/坐标下界](finite-input-review.json)5种400实测通过。曾观察到ES HTTP刚恢复首请求仍503，随后同一Java进程重试成功；不把探活当业务立即恢复保证。

没有多节点、并发更新、分页/PIT或性能/评分质量验收；ES执行超时与部分分片失败只有代码保护，未造故障。历史F04–F06阻塞不回填。本轮结束资源状态见[恢复收据](../../../../docs/framework-review/20261021-f10-sort/workspace-state.json)。
