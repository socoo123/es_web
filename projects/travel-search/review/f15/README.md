# F15 · 实际ES与Java验收

范围：本地IK扩展词典文件发布、重启加载、新旧文档词项、固定_source受控重建、误召回与REST↔Java。与[HTTP阅读/观察窗](../../../../docs/framework-review/20261024-f15-dictionary/README.md)分列。[读者入口](../../labs/f15/README.md)。

[verify.py](verify.py)是作者语义/边界验收，不要求读者学习它。两轮各从empty重新加载开始，经点名清理后完整重做，原始请求与完整响应包含在[round-1](round-1.jsonl)/[round-2](round-2.jsonl)；仅84条教学请求的子集也分别保存。[执行摘要](execution.json)记录实际命令、阶段计数、token/position/offset、已存向量、ID及漏/误召回。每轮完整配置、九份/两份Bulk全created、count9/11、green、无失败分片与完整_reindex11created；源/目标十一份_source逐字值相同。两轮分析/向量/查询摘要一致。

Java对照重放实际序列化的分析请求、固定旧ID的已存向量请求与搜索DSL，比较完整token/position/offset、term_vectors、ID/次序/名称/城市/价格/score/sort/total/relation。另测基线与重启尚无新文档两阶段、十项非法输入400、零预算/空流、显式term探针与refresh后旧词项不变、未知analyzer400、重复创建400、v1写阻塞403、重复create重建冲突、删v2导致Java502/原v1可用及同进程重建恢复、点名清理GET404。各请求真实状态以执行摘要/原始记录为准。

[插件锁](../../infra/f15/plugins.lock.json)核对IK9.4.0下载字节SHA512与descriptor；该指纹不是独立发布校验。派生镜像实际安装、同节点保留数据卷重启后插件清单实际加载9.4.0。只验证本地词典重启路径，未验证远程热更新、多节点一致性、性能或在线重建。

[构建日志](build/build.log)、[依赖树](build/dependency-tree.txt)、[插件镜像构建](build/plugin-image.log)、[运行锁定](build/runtime.json)。应用Boot4.0.8/Temurin25.0.4.1+1/官方Java与Rest5Client9.4.8，Wrapper3.3.4/Maven3.9.11；ES9.4.0/Lucene10.4.0的内置JVM另列。未新增单元测试，按真实ES语义与边界验收。截图/静态图不替代实测，自动收据不替代视觉审阅。
