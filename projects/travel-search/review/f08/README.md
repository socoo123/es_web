# F08 · 真实 ES / Java 验收

[正文](../../../../framework/f08.html) · [手工入口](../../labs/f08/README.md) · [原始响应与断言](es-java-review.json) · [阅读/展示壳记录](../../../../docs/framework-review/20261020-f08-multifield/README.md)。

本轮为macOS arm64 / ES9.4.0 Docker / Lucene10.4.0，沿用F07 Boot4.0.8、Temurin25.0.4.1+1、官方Java与Rest5 Client9.4.8。原Compose/ES二进制/安全策略未修改。`verify.py`在真实Java服务运行时执行，拒绝已有F08索引，只删除`tut-f08-attractions`；无mock。

两轮均通过：建索引、green、完整mapping、15项Bulk created、refresh/count；六组REST完整ID/次序/total/relation；三组Java与REST精确DSL/源字段/整数分/分数/逐字段片段/全部回退；原文HTML逐字符还原为DTO文本；400非法预算、清理后404与Java502缺索引。两轮各自点名删除后重建。六组REST为name-only/multi/alias/copy/no-highlight/empty；三组Java为multi/alias/empty。

额外80元迁移与去高亮分数比较、实际手工脚本、构建与展示壳记录在阅读验收目录。[构建原始日志](build.json)与[依赖树](dependency-tree.json)独立保存，JSON按原样保存换行/空格及SHA256；没有单元测试，不用构建成功替代执行。真实部分分片失败/ES执行超时未造故障；未测排名质量、大字段成本、插件、多节点、TLS或数据库/CDC。F04–F06历史受阻状态不回填。

复验：启动专用ES、构建启动本课Java、确保本课索引不存在后，从仓库根运行`python3 projects/travel-search/review/f08/verify.py`。它输出两轮并保留原始请求/响应和输入哈希；结束会删除本课索引。不要在展示壳实验同时运行此清理脚本。
