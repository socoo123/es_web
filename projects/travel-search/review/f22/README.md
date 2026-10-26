# F22 真实ES / Java验收

两轮均使用最终工程与固定24份资料；实际范围以round1/round2输出和jsonl为准。每轮70教学HTTP，Java内部16搜索另计；作者附加、浏览器、清理分列。初次与点名清理后重做不依赖动作时机，refresh=-1后显式刷新。

- [运行版本、构建与制品](runtime.json)
- [第一轮](round1/summary.json)、[第二轮](round2/summary.json)：准备/调整/留出/边界/Java/独立结业分文件记录
- [附加失败与恢复](extra.json)、[资源清理](../../../../docs/framework-review/20261026-f22-evaluation/workspace-state.json)
- [内容、图解与HTTP/实际截图](../../../../docs/framework-review/20261026-f22-evaluation/README.md)

调整集nDCG0.768275→0.829090、Recall同0.916667；留出nDCG同0.731603、Recall同0.937500。候选仅通过固定教学语料门槛，不声称全站改善。没有观察到新增指标退步，原有0级/1级首位仍保留。独立结业参考：c-bridge Recall2/3、nDCG0.766116；c-indoor Recall1、nDCG0.928495；两个固定策略相同，不提供新策略逐步答案。读者应先独立作答再看此处。

标准IDCG从全部等级取前10；ES9.4.0内置短结果理想长度不同，探针1与0.765361明确分开。主8查询每条返回10，因此REST、Python、Java一致。标签由作者单人编写，未测标注一致性、代表性、显著性、性能、多节点、生产安全与持续更新。超时/部分分片失败仅代码防护，未实际构造。
