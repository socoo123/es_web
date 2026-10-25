# F17 · 提示、拼音与容错

[正文](../../../../framework/f17.html)先解释三条候选路径。14份虚构资料、[固定判断](../../data/f17/judgments.json)；ES9.4.0/Lucene10.4.0，独立19217/tut-f17-attractions，一主零副本/strict/refresh=-1。只用内置字段与查询；拼音由资料显式维护，不声称ES自动转写中文，也不要求装插件。

需要Docker/Compose、Bash、curl、Python3.10+。Java观察需要JDK25。终端一，从仓库根目录：

```bash
cd projects/travel-search
export ES_URL=http://127.0.0.1:19217
docker compose -f infra/f17/compose.yaml up -d es
bash infra/f17/wait.sh
# 若本课索引已存在，先按下文cleanup，再从01开始
bash labs/f17/01-prefix.sh
bash labs/f17/02-pinyin.sh
bash labs/f17/03-fuzzy-and-close.sh
```

| 案例 | 教学HTTP | 输入与证据 |
| --- | --- | --- |
| 01 / c01 | 19 | 版本/插件/完整配置/green/Bulk14/refresh/count；4字段分析；completion/context/query反例、文字去重与sayt中间词 |
| 02 / c02 | 6 | name/keyword分析、小写不转写中文；主字段与全拼/首字母、同音误入 |
| 03 / c03 | 17 | 整名精确/fuzzy/AUTO/收窄；bool_prefix两个错字位置与真实改写；同时更新状态与scope、GET/refresh前后两路候选 |
| 04 Java↔REST | 22 | 11组：各1次Java＋1份真实DSL重放REST；完整卡片/ID/次序/score/sort/计数 |
| 合计 | 64 | 清理、探活、构建、Java内部ES调用、浏览器、可选重复与作者附加另计 |

终端二，从仓库根目录：

```bash
cd projects/travel-search/backend
# JAVA_HOME/PATH先选择JDK25
./mvnw -B -ntp clean package
ES_URL=http://127.0.0.1:19217 APP_PORT=18080 java -jar target/travel-search-0.7.0.jar
```

终端一仍在projects/travel-search：

```bash
bash labs/f17/04-java.sh
# 可选重复，不计64
curl --fail-with-body -sS -X POST http://127.0.0.1:18080/api/attractions/suggestions -H 'Content-Type: application/json' --data-binary @search/f17/input-pinyin.json
```

打开http://127.0.0.1:18080/f17.html。只读观察窗经Java访问ES，Pages不连接本机。六种模式：completion按input开头和city|open取前10，skip_duplicates=false；sayt用根与2/3gram bool_prefix；pinyin查全拼/首字母前缀；exact查name.whole；fuzzy整名距离1/首字符可改；guarded少于4 code point精确，否则距离1/首字符不变。非补全模式均城市/open/CNY、前20、ID升序；本课全部资料CNY，不提供预算过滤。拼音接受2至40个ASCII字母，去两端空白与转小写；q通用上限60 UTF-16单位。

- 01/02初始：故宫/completion为bj-palace,bj-gate,bj-same-a,bj-same-b；sayt多bj-infix，博物/sayt仅bj-palace而completion空。
- completion-unsafe放宽scope后，即使query过滤open/BJ，仍出现bj-closed、sy-palace；context与普通query分开。
- skip_duplicates=true把同名不同ID的bj-same-b丢掉。本课按业务ID保留不同实体，当前单节点无重复ID option，不声称实际触发跨来源ID合并。
- gugong/gg补回故宫资料，也误入bj-garden；name搜gugong空。拼音normalizer不转写中文。
- 天谈公园/exact空；fuzzy与guarded均bj-pond,bj-temple。西胡/fuzzy为bj-river,bj-west；AUTO与guarded空。
- bool_prefix加fuzziness=1：天谈公园误入古公花园；天坛公圆空，最后前缀不容错。完整改写保留。
- 03最后把bj-gate的status与scope同时改closed；GET先可见，refresh前completion仍旧4份，refresh后3份。sayt故宫剩bj-infix,bj-palace,bj-same-a,bj-same-b；04 Java使用此时状态。GuGong/gg此时4份，不再有东门。

所有DTO保留原名/拼音/城市/价格/score/sort；completion另有建议text，total=null表示全部候选未知，returnedCount仅为本次保留数量。esResponse是官方客户端结构化响应再序列化，键可能为completion#places，不是原始HTTP字节。400输入错误、ES拒绝502、连接/transport503；不完整搜索或不一致原文502。条件或错误清空旧卡片/DSL。0候选为200。

点名清理与重做，恢复bj-gate的初始open状态，再由03下架：

```bash
bash labs/f17/cleanup.sh
bash labs/f17/01-prefix.sh
bash labs/f17/02-pinyin.sh
bash labs/f17/03-fuzzy-and-close.sh
bash labs/f17/04-java.sh
# 结束；另关闭自己启动的Java
bash labs/f17/cleanup.sh
docker compose -f infra/f17/compose.yaml stop es
```

cleanup仅DELETE tut-f17-attractions并GET404，不删卷或其他资源。重复01索引已存在400，不能忽略。全量手工REST可在[search/f17](../../search/f17)逐份重放；body文件不含路径参数。脚本保留完整请求与响应为JSONL，验收工具不是读者的学习前提。

[真实两轮](../../review/f17/README.md)、[内容/图解/阅读/观察窗](../../../../docs/framework-review/20261025-f17-suggestions/README.md)分别记录；未测整体质量/性能/多节点/自动转写，未提前实施F18。
