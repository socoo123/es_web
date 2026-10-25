# F17 · 真实运行验收

由[execute.py](execute.py)执行两轮；每轮点名清理，01→02→03→04，附加检查，再清理。完整请求/响应保留在round-1/2的JSONL；[执行收据](execution.json)记录实际计数、token/位置/offset、ID及两轮一致性。无mock，无其他ES版本替代。

- 每轮64教学HTTP＝19前缀/context/去重＋6拼音＋17容错/下架＋22 Java与REST；51附加；清理前后各2另计。Java内部ES调用不重复计客户端次数。
- 14份Bulk全created/errors=false，green/count14，完整有效mapping/settings通过。ES返回sayt.doc_values=false和CATEGORY大小写作等价规范化；不修改服务器输出绕过。
- 11组Java完整DTO与实际DSL重放核对卡片ID/顺序/原文/拼音/价格/状态/score/sort/计数；completion的total未知与普通总数分开。
- 附加12非法输入400、空分析200、空白与小写规范化、逐份完整_source、重复建索引400通过。
- 真实仅改status造成陈旧scope，Java502/SEARCH_INCOMPLETE；写回完整资料/refresh，同Java进程恢复。缺索引502/SEARCH_BACKEND_REJECTED；重建本课14份并正确下架东门，同进程恢复。open_contexts=0。
- HTTP停机503与恢复、观察窗真实调用在[浏览器验收](../../../../docs/framework-review/20261025-f17-suggestions/README.md)分列，不计这两轮51附加。

[构建日志](build.log)、[依赖树](dependency-tree.txt)、[运行版本/制品](runtime.json)。应用Boot4.0.8/Temurin25.0.4.1+1，官方Java与Rest5 Client9.4.8，Maven Wrapper3.3.4/Maven3.9.11；ES自带JVM另列。本课无额外插件；使用本地已有官方ES9.4.0镜像，不冒充重新下载。

[探索与修正](../../../../docs/framework-review/20261025-f17-suggestions/attempts/README.md)保留初探及失败记录。只认证单节点固定小语料，未测全站相关性、性能、多节点、自动拼音质量、线上发布、安全、DB/CDC；执行超时/部分分片失败只有代码防护，无实触发。
