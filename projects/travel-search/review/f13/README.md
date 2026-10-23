# F13 · ES与Java真实验收

[入口](../../labs/f13/README.md) · [两轮摘要](execution.json) · [第一轮原始请求/响应](round-1.jsonl) · [第二轮](round-2.jsonl) · [点名初始清理](initial-cleanup.jsonl) · [复现脚本](verify.py)。

ES9.4.0/Lucene10.4.0，macOS arm64 / Docker隔离单节点19200，一主零副本、strict、关闭自动refresh；全程只操作tut-f13-attractions。每轮点名删除后重新创建，Bulk8项created、显式refresh、count8。两轮各81次客户端HTTP=教学58+作者附加23，Java内部额外调用不重复计入58。无模拟响应。

教学：mapping有效回退、settings、10组分析；token/position/offset、大小写、whitespace、HTML explain、原始offset校正、emoji保留/UTF16、空流；11组查询、原文GET；7组Java输入，两份实际分析请求和SearchRequest重放REST，完整token/位置/偏移、命中ID/次序/价格/score/sort/total/relation逐项一致。失配0/AND4/短语3/英文2/不转小写0；SY城市1，空流0。人为相关性标签另见正文，未将ES规则命中当作旅游语义正确。

附加：8种非法输入400、0分预算空集、索引外自定义analyzer400、不存在analyzer400、请求覆盖后mapping仍keyword、删除目标索引后Java502、同Java进程重建恢复200、清理后GET404。搜索超时/部分分片失败仅代码防护，未故障注入；未比较插件、性能、多节点、TLS/权限、中文质量查询集或CDC。

构建沿用Boot4.0.8 / Temurin25.0.4.1+1 / 官方Java与Rest5 Client9.4.8 / Wrapper3.3.4、Maven3.9.11，应用JDK与ES bundled JVM分开；最终构建/依赖收据、HTTP/真实观察窗/视觉与结束资源恢复见[本轮记录](../../../../docs/framework-review/20261023-f13-analysis/README.md)。没有新增单元测试；验证针对真实ES语义和可复现契约。
