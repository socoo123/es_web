# F13 · 用分析链解释中文召回

[教程](../../../../framework/f13.html) · [固定八份资料](../../data/f13/attractions.json) · [完整索引配置](../../search/f13/index.json) · [两轮实测](../../review/f13/README.md)。只操作`tut-f13-attractions`，不依赖前课索引，不安装中文插件。

ES9.4.0/Lucene10.4.0；单节点、一主零副本、`dynamic:strict`、`refresh_interval:-1`。金额为整数分/CNY，城市BJ/SY、状态open/closed。索引创建后Bulk八项必须全部created、errors=false，再显式refresh，count=8；重复创建遇到400已存在应停下，点名清理后重做。这个学习拓扑不代表生产建议。

需要Docker/Compose、Bash、curl、Python3.10+（标准库）与JDK25。应用沿用Boot4.0.8、官方Java与Rest5 Client9.4.8、Maven Wrapper3.3.4/Maven3.9.11；应用JDK与ES bundled JVM分开。作者本轮为macOS arm64 / Temurin25.0.4.1+1，其余平台未声称实测。

从仓库根目录开始，第一终端：

```bash
cd projects/travel-search
docker compose -f infra/single-node/compose.yaml up -d es
bash infra/single-node/wait.sh
bash labs/f13/01-prepare.sh
bash labs/f13/02-chain.sh
bash labs/f13/03-recall.sh
```

第二终端从仓库根目录开始，确认`java -version`为25；JDK配置见[应用说明](../../backend/README.md)：

```bash
cd projects/travel-search/backend
./mvnw -B clean package
java -jar target/travel-search-0.7.0.jar
```

回第一终端（仍在`projects/travel-search`）：

```bash
bash labs/f13/04-java.sh
```

脚本打印实际请求、状态、响应，任何不符即停止；辅助断言无需读者掌握。手工用curl可以完成同一对照，不以脚本跑绿替代解释。ES默认`http://127.0.0.1:19200`，Java默认`http://127.0.0.1:18080`。环境变量`ES_URL`同时供脚本与Java使用；脚本的`APP_URL`和Java的`APP_PORT`需自行对应。服务端可在启动前以`TRAVEL_F13_INDEX`配置本课索引，读者主流程保持默认。浏览器不接收ES凭据、任意索引名或分析器名。

## 三个案例与58条教学HTTP

| 案例 | 操作 | 请求数 |
| --- | --- | --- |
| f13-c01 · 输入怎样成为token | 准备6；mapping/settings2；分析10 | 18 |
| f13-c02 · 漏召回与误召回 | 11份搜索与一次原文GET | 12 |
| f13-c03 · 同一语义的Java观察 | 7份Java输入，每份Java1 + REST重放两份分析及搜索3 | 28 |

总58指脚本显式发出的HTTP请求；Java内部另有每次两份分析与一次搜索，不把它们重复计入58。清理、探活、构建、作者附加断言、浏览器重复操作另计。

## c01：先预测，再核对流

[十份完整分析请求](../../search/f13/analyze/01-field.json)，顺序与`02-chain.sh`一致。

```bash
curl --fail-with-body -sS -X POST http://127.0.0.1:19200/tut-f13-attractions/_analyze -H 'Content-Type: application/json' --data-binary @search/f13/analyze/01-field.json
curl --fail-with-body -sS -X POST http://127.0.0.1:19200/tut-f13-attractions/_analyze -H 'Content-Type: application/json' --data-binary @search/f13/analyze/05-explain.json
```

输入“故宫 Palace-MUSEUM（东门）”，`field:name`得到故/宫/palace/museum/东/门，position=0–5。只用standard tokenizer时英文仍是Palace/MUSEUM，加lowercase才转小写；whitespace得到故宫及Palace-MUSEUM（东门）两项。纯标点“！！！”为空流，不是连接失败。

`explain:true`按charfilters/tokenizer/tokenfilters检查变化；`html_strip`只改变分析流，不修改_source，更不是网页安全净化。本例`<b>故宫</b>…`中“宫”的offset是[4,9)，覆盖了被过滤的闭合标签，区间长度无需等于词面长度。

“故宫😀 Palace”本轮四项：故pos0/[0,1)，宫pos1/[1,2)，😀pos2/[2,4)，palace pos3/[5,11)。offset按原输入UTF-16单位计，不是UTF-8字节数；不是所有符号都被standard丢弃。

`field:name.mismatch`仍输出故/宫，因为field选择索引分析器；要模拟这个字段的查询链，显式指定`analyzer:keyword`，得到完整故宫。`_analyze`处理你提供的文本，不读取已有文档词项；需再查mapping/数据/实际search。

## c02：同一资料、不同规则

所有查询都有BJ/open/CNY/0–10000分的硬条件（第11个换SY），按业务ID升序。不比较评分质量。八份资料和价格见固定JSON，以下核对完整ID：

| 文件 `search/f13/queries/` | 完整命中ID（依次） | 解释 |
| --- | --- | --- |
| 01-mismatch.json | 空 | name.mismatch索引是单字，查询keyword是完整故宫 |
| 02-aligned.json | bj-mixed, bj-palace, bj-punctuation, bj-separated | AND只要求两个词项都出现 |
| 03-phrase.json | bj-mixed, bj-palace, bj-punctuation | 故城宫苑不相邻；故，宫仍相邻 |
| 04-raw-short.json | 空 | keyword字段按完整原值，不是子串 |
| 05-raw-full.json | bj-palace | term完整匹配北京故宫博物院 |
| 06-english.json | bj-dash, bj-mixed | PALACE-MUSEUM经分词与小写归一 |
| 07-case-sensitive.json | 空 | 请求局部选择case_sensitive，查询大写对不上索引小写 |
| 08-query-override.json | 与02相同四份 | 单次覆盖mismatch查询analyzer，未改mapping或历史词项 |
| 09-term-text.json | 空 | term不分析完整故宫，text字段没有这个完整词项 |
| 10-punctuation-only.json | 空 | 默认空分析结果不产生候选 |
| 11-other-city.json | sy-palace | 词项相同，城市过滤仍独立生效 |

```bash
curl --fail-with-body -sS -X POST http://127.0.0.1:19200/tut-f13-attractions/_search -H 'Content-Type: application/json' --data-binary @search/f13/queries/01-mismatch.json
curl --fail-with-body -sS -X POST http://127.0.0.1:19200/tut-f13-attractions/_search -H 'Content-Type: application/json' --data-binary @search/f13/queries/02-aligned.json
curl --fail-with-body -sS -X POST http://127.0.0.1:19200/tut-f13-attractions/_search -H 'Content-Type: application/json' --data-binary @search/f13/queries/03-phrase.json
```

“故，宫主题展”和“故城宫苑”是课程人为给出的不相关项，误召回是相对此需求判断的，不是ES判断了它们的旅游含义。修正漏召回与取得可用中文语义搜索是不同层次。默认standard没有被证明“搜不到故宫”；故意失配才导致第一个空集。

## c03：浏览器 → Java → ES

打开`http://127.0.0.1:18080/f13.html`：默认“故宫/BJ/100元/故意失配”为0；切“对齐分析链”为4；切“短语”为3。英文PALACE-MUSEUM在对齐模式2份、不转小写反例0份；SY城市1份、纯标点0份。查看实际token、分析请求、搜索DSL与结果。改变条件后旧结果清空，须重新提交。

```bash
curl --fail-with-body -sS -X POST http://127.0.0.1:18080/api/attractions/analysis-search -H 'Content-Type: application/json' --data-binary @search/f13/inputs/02-aligned.json
```

两边分析的是同一查询输入，不代表读到文档中现存词项。`04-java.sh`把Java实际序列化的两份分析请求和搜索DSL逐份重放到REST，核对完整token/position/offset、ID/顺序/价格/score/sort/total/relation。普通业务搜索不用每次额外做两次分析；本课额外调用是诊断观察功能。

关键词非空且最长60个UTF-16单位，预算0–100000000整数分，mode四选一；输入错误400；ES拒绝或索引缺失502；连接不可用503；不完整搜索502。错误清空旧结果，修复前提后再提交。ES9.4.0与单次对照无法替代中文质量评估、插件兼容或性能测试。Pages仅承载教程，不调用本机ES/Java。

## 点名清理与重做

第一终端执行；会删除本课八份固定资料，只点名一个索引：

```bash
bash labs/f13/cleanup.sh
bash labs/f13/01-prepare.sh
bash labs/f13/02-chain.sh
bash labs/f13/03-recall.sh
bash labs/f13/04-java.sh
```

清理后GET索引404；重建Bulk八项全created，之后结果应相同。本课没有PIT或写入观察会话，Java可保持同一进程。脚本不暗中删除已存在索引、不清卷、不碰前课数据。结束后关闭自己启动的Java；如果框架ES原来停止，用相同Compose的`stop es`恢复，保留卷和源码篇节点。

作者两轮验收入口（仍在`projects/travel-search`，会点名清理本课索引，Java需已启动）：

```bash
python3 review/f13/verify.py
```
