# F19 · 名称、短语与多字段权重

[正文](../../../../framework/f19.html)先解释三种名称证据、字段得分组合与候选门槛。12份虚构资料，[完整原文](../../data/f19/attractions.json)、[人工意图](../../data/f19/judgments.json)。name/description采用standard tokenizer＋lowercase，中文逐字；name.exact为未归一keyword。不是生产中文方案推荐。

独立ES9.4.0/Lucene10.4.0，19219/tut-f19-attractions，一主零副本/strict/refresh=-1，无插件。显式BM25 k1=1.2/b=.75/discount_overlaps=true；应用JDK和ES bundled JVM另列。默认HZ/open/CNY/0–10000整数分，_score降序＋业务ID升序，前20/精确计数/explain诊断。

需要Docker/Compose、Bash、curl、Python3；Java需要JDK25。终端一，从仓库根目录：

```bash
cd projects/travel-search
export ES_URL=http://127.0.0.1:19219
docker compose -f infra/f19/compose.yaml up -d es
bash infra/f19/wait.sh
# 已有本课索引先按文末cleanup，再从01开始
bash labs/f19/01-levels.sh
bash labs/f19/02-weights.sh
bash labs/f19/03-gates.sh
```

| 案例 | 教学HTTP | 输入与判断 |
| --- | --- | --- |
| f19-c01 / 01 | 16 | 版本/插件/green/Bulk12/refresh/count/实际配置/分析/存词项；整名1、短语3、名称AND4、简介AND2；散词不满足短语 |
| f19-c02 / 02 | 20 | sum/best/tie/tuned与名称1/3/50；夜游负例；空格边界；三种multi_match等价；六次完整query解释 |
| f19-c03 / 03 | 8 | optional九份/required五份/强制短语三份；山林matched变化与三份硬条件排除 |
| Java↔REST / 04 | 48 | 16输入，每组Java＋实际搜索DSL重放＋解释重放；全部卡片和解释树 |
| 合计 | 92 | 清理/探活/构建/Java内部调用/浏览器/作者附加另计 |

终端二，从仓库根目录：

```bash
cd projects/travel-search/backend
# JAVA_HOME/PATH先选择JDK25
./mvnw -B -ntp clean package
ES_URL=http://127.0.0.1:19219 APP_PORT=18080 java -jar target/travel-search-0.7.0.jar
```

终端一仍在projects/travel-search：

```bash
bash labs/f19/04-java.sh
# 可选单次请求，不计92
curl --fail-with-body -sS -X POST http://127.0.0.1:18080/api/attractions/weight-search -H 'Content-Type: application/json' --data-binary @search/f19/input-tuned.json
```

打开http://127.0.0.1:18080/f19.html。六模式sum/best/tie/tuned/optional/required，每字段AND。nameWeight只乘名称match，1至50整数；tuned用tie0.1作为must，再加名称短语4倍和整名固定8，两项should可选。q保留原值，不自动去空格。浏览器→Java→ES；Pages只承载教程，读者不用开发前端。

主输入“西湖博物馆”：sum为both/description/exact/scatter/prefix；best为description/both/exact/scatter/prefix；tie恢复sum次序；tuned/1为exact/both/prefix/description/scatter。以上ID均加hz-。名称match权重3和50让scatter升到description前，但不改变五份候选。hz-split在两字段合起来字齐，单个字段AND不成立，仍被排除。

反例“夜游”：best/1是cruise/photo，best/3与50均photo/cruise；tuned/1也因短语奖励使photo领先。人工意图是水上活动，不是室内照片展。只说明本课规则有代价，不能据两条输入选出生产方案。输入“西湖 博物馆”保持分析词项但失去整名8分，both领先exact。

optional只有过滤和可选文本：九份，后四cruise/noise/photo/split均0；required在同层minimum_should_match=1恢复五份；将名称短语奖励移到must缩为exact/both/prefix三份。奖励不能绕过城市/open/CNY/票价条件。零预算仅hz-exact，SZ仅sz-exact，海滩零命中200。

每次提交显示实际输入、搜索与解释DSL、完整客户端序列化响应/DTO；完整query复用，但两次请求不是并发原子快照。条件变化/失败清空旧卡片、DSL与解释。非法输入400，ES拒绝502，连接/transport503，不完整结果502；超时/部分分片失败只有防护，未构造。客户端解释float经double再序列化会展开小数，比较结构与微小容忍，不宣称字节相同。

点名清理和重做：

```bash
bash labs/f19/cleanup.sh
bash labs/f19/01-levels.sh
bash labs/f19/02-weights.sh
bash labs/f19/03-gates.sh
bash labs/f19/04-java.sh
# 结束；另关闭自己启动的Java
bash labs/f19/cleanup.sh
docker compose -f infra/f19/compose.yaml stop es
```

cleanup仅DELETE tut-f19-attractions、GET404；不删其他索引/卷。重复01建索引400，重复Bulk create条级409；停止容器不清数据。首次与清理后从01重做分别核对created/errors/计数，不能忽略错误。

[完整查询](../../search/f19)、[真实两轮](../../review/f19/README.md)、[图解/HTTP/真实观察窗](../../../../docs/framework-review/20261025-f19-weights/README.md)分别记录。未测全站质量/性能、多分片/生产安全/DB/CDC。本课只实施F19，F20仍为规划。
