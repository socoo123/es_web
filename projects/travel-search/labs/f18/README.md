# F18 · BM25与解释评分

[正文](../../../../framework/f18.html)先解释词频/文档频率/字段长度，再执行请求。虚构10份初始资料、6份闭馆山林追加资料；[清单](../../data/f18/manifest.json)。description用空格给定中文词边界，whitespace+lowercase；不是生产中文分词推荐。name不评分。

ES9.4.0/Lucene10.4.0，独立19218/tut-f18-attractions，一主零副本/strict/refresh=-1、无插件。显式BM25 k1=1.2/b=.75/discount_overlaps=true，norms开启并存词向量。固定HZ/SZ、open、CNY、非负整数分票价/预算；默认10000分。按_score降序、业务ID升序，前20/精确计数。ES兼容BM25的k1+1会使解释树出现boost≈2.2，没有业务查询boost。

需要Docker/Compose、Bash、curl、Python3.10+；Java需要JDK25。终端一，从仓库根目录：

```bash
cd projects/travel-search
export ES_URL=http://127.0.0.1:19218
docker compose -f infra/f18/compose.yaml up -d es
bash infra/f18/wait.sh
# 已有本课索引时，先按下面cleanup再从01开始
bash labs/f18/01-bm25.sh
bash labs/f18/02-contexts.sh
bash labs/f18/03-unrelated.sh
```

| 案例 | 教学HTTP | 输入与证据 |
| --- | --- | --- |
| 01 / c01 | 21 | 版本/插件/完整有效配置/green/Bulk10/refresh/count；分析/六份存储词向量；主搜索/四份完整_explain |
| 02 / c02 | 6 | 西湖＋夜游OR、全部filter、城市也must；各一次搜索＋一次完整query的_explain |
| 03 / c03 | 10 | 追加六份前/refresh前/后；原文档版本不变，候选不变，字段统计与分数变化 |
| 04 Java↔REST | 21 | 七输入，每组Java＋实际搜索DSL重放＋实际_explain重放；全部卡片/解释结构与数值容忍比较 |
| 总计 | 58 | 清理/探活/构建/Java内部ES调用/作者附加/浏览器另计 |

终端二，从仓库根目录：

```bash
cd projects/travel-search/backend
# JAVA_HOME/PATH先选择JDK25
./mvnw -B -ntp clean package
ES_URL=http://127.0.0.1:19218 APP_PORT=18080 java -jar target/travel-search-0.7.0.jar
```

终端一仍在projects/travel-search：

```bash
bash labs/f18/04-java.sh
# 可选单次重放，不计58
curl --fail-with-body -sS -X POST http://127.0.0.1:18080/api/attractions/score-search -H 'Content-Type: application/json' --data-binary @search/f18/input-scored.json
```

打开http://127.0.0.1:18080/f18.html，使用课程观察窗，不用开发前端。默认scored，filtered把文本也放filter，city-scored把城市移到must；explainId选十个固定ID。搜索与解释复用完整query，但它们是两次请求，不是并发下原子快照。只读服务不会追加资料。浏览器→Java→ES；Pages不连接本机服务。ES端点/凭据不进入浏览器。

初始语料：count10、字段N9、西湖n8、avgdl50/9、六份候选。主次序hz-four,hz-night,hz-short,hz-twice,hz-once,hz-long。等长一次/两次/四次递增且饱和；同频短2词＞8词＞16词。输入“西湖 夜游”OR后hz-night先于hz-four，其余不变；夜游n1，稀有词与双项加和共同产生变化。全filter候选不变、全0分、ID升序；城市must增加城市贡献，当前次序不变。

03追加六份不含西湖且closed的资料。refresh前旧分数；之后count16、N15、西湖n8、avgdl62/15。候选与当前次序不变，旧景点分数变化，hz-short原文/版本/seq_no/primary_term不变。04在03之后，默认卡片显示N15；不能拿它同正文初始N9的小数逐位比较。

默认零预算只剩hz-short，SZ仅sz-copy，海滩为0份；选择hz-closed/hz-missing/hz-other可观察完整query的matched=false。空结果200、非法输入400、ES拒绝502、连接/transport503；不完整搜索或字段502。条件变化和错误清空旧卡片/解释/DSL。官方客户端解释数值再序列化可能展开float为double小数；完整结构/描述逐项一致，数值容忍微小误差，不宣称原始字节相同。

点名清理与重做：

```bash
bash labs/f18/cleanup.sh
bash labs/f18/01-bm25.sh
bash labs/f18/02-contexts.sh
bash labs/f18/03-unrelated.sh
bash labs/f18/04-java.sh
# 结束，另关闭自己启动的Java
bash labs/f18/cleanup.sh
docker compose -f infra/f18/compose.yaml stop es
```

cleanup仅DELETE tut-f18-attractions、GET404，不删其他资源或卷。重复01索引已存在400；重复03的create会条级409，不能忽略errors。完整请求见[search/f18](../../search/f18)；脚本把完整请求和响应输出JSONL，验收工具不是学习前提。

[真实两轮](../../review/f18/README.md)、[内容/图解/HTTP/观察窗](../../../../docs/framework-review/20261025-f18-bm25/README.md)分别记录。未测全站质量/性能、多主分片/DFS、生产安全、CDC；执行超时与部分分片失败仅代码防护。只实施F18，F19调权尚未实施。
