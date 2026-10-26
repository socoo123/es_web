# F21 · 真实ES与Java验收

正文与读者入口：[F21](../../../../framework/f21.html)、[实验说明](../../labs/f21/README.md)。作者正式两轮由[run.py](run.py)执行，原始每条HTTP记录在`round-1/`与`round-2/`；汇总见[es-java-review.json](es-java-review.json)、[排序](ranking-summary.json)、[公式](explain-summary.json)、[版本与制品](runtime.json)。

本课独立19221/tut-f21-attractions，14份固定虚构资料，一主零副本/strict/refresh=-1，无插件。Java最终jar/Boot4.0.8/JDK25/官方Client9.4.8；应用JDK与ES bundled JVM分列。最终验收运行次数以JSON为准。

每轮88教学HTTP：16准备/单项、13合成、20排序边界、39 Java↔REST；点名清理前后各2、附加契约/日期毫秒边界/错误与恢复另计。原始JSONL保存请求、状态、完整响应；比较相同样本的ID、分数、sort、每卡字段/解释与完整query解释，排除仅内部doc ordinal的不同。REST↔Java数值采用微小容忍，不宣称字节相同。

六模式、三意图、软/硬半径、原点改变、裸缺值/仅weight0回退/常量0修正、未来日期对称性、零分仍匹配与min_score分别对照。低相关展厅被抬高仍保留为坏案例；未测全站质量/留出指标、性能、多节点、生产安全、持续核验更新。超时/部分分片失败仅代码防护。

[观察窗、图源生成、HTTP与截图自审](../../../../docs/framework-review/20261026-f21-decay/README.md)分列；不以静态检查替代真实执行。初探与修正保留在[attempts](../../../../docs/framework-review/20261026-f21-decay/attempts)。F22未实施。
