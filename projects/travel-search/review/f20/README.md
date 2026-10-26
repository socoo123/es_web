# F20 真实 ES / Java 验收

[可重做入口](../../labs/f20/README.md) · [正文](../../../../framework/f20.html) · [图解/HTTP/观察窗](../../../../docs/framework-review/20261026-f20-signals/README.md)。

`run.py`在固定ES9.4.0单节点与最终Boot4/JDK25 jar上，点名清理前后各一次，执行两轮相同的79教学HTTP及附加错误/恢复。原始请求/状态/响应保存在round-1与round-2；`es-java-review.json`给计数与实际断言，`ranking-summary.json`保存真实次序，`explain-summary.json`保存函数与编码精度摘要。

构建、依赖树、应用JDK、ES bundled JVM、镜像来源与jar哈希另见runtime.json。不含凭据；固定资料虚构，未测全站质量/留出集、性能、多主分片/多节点、生产安全/CDC。超时/部分分片失败仅代码防护。
