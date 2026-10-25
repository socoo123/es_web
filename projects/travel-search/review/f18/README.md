# F18 · 真实ES与Java两轮

运行[教学入口](../../labs/f18/README.md)；作者用[run.py](run.py)执行点名清理前后两轮。[execution.json](execution.json)记录请求数量、完整token/词向量/相对分数/解释项、七组REST↔Java和两轮一致性；round-*.jsonl保留所有原始请求与响应，未用mock。Java内部ES请求不重复计作客户端教学HTTP。

每轮58教学=21+6+10+21。额外验收与前后清理分别计数；额外包括12非法输入400、逐份_source、重复建索引400、缺索引502及同Java进程恢复。解释结构与描述逐项核对，数值容忍客户端float/double再序列化的微小差别，不要求跨环境固定小数。附加重建只为错误恢复，未改检查器或跳过字段。

[初始hz-short完整_explain](explain-short.json)、[正文使用的扁平教学摘要](explain-short-summary.json)。[runtime.json](runtime.json)记录实际版本、JVM、镜像来源、最终jar/构建/依赖树哈希；[build.log](build.log)、[dependency-tree.txt](dependency-tree.txt)、[java.log](java.log)。Boot4.0.8/JDK25.0.4.1+1、官方Java/Rest5 Client9.4.8、Wrapper3.3.4/Maven3.9.11沿用已验证基线；ES bundled JVM单列。

[内容/图解/HTTP/观察窗/资源恢复](../../../../docs/framework-review/20261025-f18-bm25/README.md)独立记录；浏览器实停机503与恢复在观察窗记录中。只证明单主分片、小型固定语料的评分机制，不代表排名质量、吞吐或多分片DFS结论；无新增单元测试。

Maven日志可读版只去掉行尾空格，以通过仓库空白检查；原始字节完整保存在[build.log.gz](build.log.gz)与[dependency-tree.txt.gz](dependency-tree.txt.gz)，原始解压SHA-256及规范化说明见runtime.json。没有改写构建结果或响应。
