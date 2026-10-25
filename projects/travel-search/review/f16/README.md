# F16 · 真实ES与Java两轮

[执行收据](execution.json)与round-1/2-*.jsonl逐份保留完整请求/响应。每轮先点名删除索引与同义词集并分别GET404，再完整执行三个案例、Java重放、附加错误恢复，结束同样点名清理。每轮87教学+33附加客户端请求；两端清理各4另计。Java内部ES调用不重复计数。

- 22：版本9.4.0/Lucene10.4.0、唯一ICU9.4.0、规则created→索引green、11created/errors=false、count11、完整有效mapping/settings与中文矩阵。
- 12：palace跨两位置/forbidden-city两边、完整token/position/length/offset/type；AND2、loose4、phrase1、late0；三个query改写；stop移除规则左侧400且正常搜索恢复。
- 21：源繁体/存储简体、别名更新后旧搜索0/refresh后1、完整管理集PUT/两分析器实际重载、旧原文/版本/seq_no与已存向量不变、被引用集删除400。
- 32：8组Java输入实际双分析与搜索DSL重放REST；完整分析响应、token与每卡ID/名称/英文/别名/城市/价格/币种/状态/score/sort/total/relation一致，DSL与固定文件规范化后相同。
- 附加33：10非法输入400、空token/0结果与0预算、11份_source、重复索引400、删索引502与同Java进程恢复、open_contexts=0。

[构建](build.log)、[依赖树](dependency-tree.txt)、[插件来源与descriptor](plugin-fetch.json)、[派生镜像安装](plugin-build.log)、[版本与制品](runtime.json)。应用Boot4.0.8/JDK25.0.4.1+1，Java/Rest5 Client9.4.8；容器bundled JVM单列。无新增单元测试，使用本课真实语义和边界验收。

初步探索与客户端详细分析属性失败在[attempts](../../../../docs/framework-review/20261025-f16-synonyms/attempts/README.md)，未删除失败记录或关闭必填校验。独立[HTTP/真实观察窗](../../../../docs/framework-review/20261025-f16-synonyms/README.md)不以接口200替代UI核对。多节点、性能/全站中文质量与权限未测；执行超时/分片部分失败仅有代码防护。
