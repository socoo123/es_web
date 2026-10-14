# F03 真实 Elasticsearch 验收

日期：2026-10-14。执行的是 [F03 正文](../../../../framework/f03.html)对应的 labs/f03 脚本；[es-review.json](es-review.json)保存本轮实际响应、环境版本、镜像 digest、输入 SHA-256 与两轮断言。旧 F01 记录保留，未用其响应冒充本课实测。

- f03-c01（来自 f01-c01）：隔离单节点 ES 9.4.0、版本/节点数、显式 mapping、1 主/0 副本、限定健康、空搜索 total=0、首次 created/version=1、refresh 后 total=1/eq、命中 a-hz-xihu、_source/mapping/count/GET。
- f03-c02（来自 f01-c02）：未监听端口 19299 与停止本工程后的 19200 均连接拒绝 curl exit=7，无 HTTP 响应；重启并等待本课索引，刷新搜索仍取回样本，证明持久卷保留资料。
- f03-c03（来自 f01-c03）：重复创建 HTTP 400 / resource_already_exists_exception；同 ID 完整覆盖 updated/version=2、count=1；点名清理 tut-f03-attractions，第二轮重新 created/version=1。

三个案例各两轮通过；raw/ 保存每步 stdout/stderr（连接故障的原样合并文本用 JSON 转义存储，并保留原字节 SHA-256），outputs/ 保存首轮真实响应或选字段摘录，完整搜索没有改值。固定断言核对 ID、字段、计数、错误类型与版本；不固定 took、_score、容器 IP 或索引 UUID。主流程 12 请求，扩展与清理另有 11 尝试（含 2 连接失败），探活/重试另计。

macOS arm64 / Docker / Compose 的实际版本、镜像 digest 与 bundled JVM 见 JSON。本轮没有执行 Java/Boot、插件、多节点、数据库、Kafka、CDC 或展示壳；这些不属于 F03。阅读/图解检查单列在 [HTTP 验收](../../../../docs/framework-review/20261014-f03-first-search/README.md)。

最终状态：F03 索引不存在；专用容器停止，数据卷保留，源码篇安全节点不受影响。

作者复现（会启动和停止专用容器，并点名删除两轮实验资源；已有本课索引时拒绝自动清理）：

```bash
python3 projects/travel-search/review/f03/verify.py
```

读者按 [本机手工入口](../../labs/f03/README.md) 操作即可，不需要安装验收工具。
