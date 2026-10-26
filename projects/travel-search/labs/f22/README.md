# F22 · 查询集、标注与搜索质量评估

[正文](../../../../framework/f22.html)先解释意图、相关等级、两个指标与留出职责。24份虚构资料，20份合格＋4硬资格反例；8查询×24份完整等级；4调整、2留出、2独立结业。作者单人教学标注，无真实游客抽样或双人一致性统计。标签文件含结业参考键，先做[独立任务](assessment.md)再看assessment部分。

独立ES9.4.0/Lucene10.4.0，19222/tut-f22-attractions，一主零副本/strict/refresh=-1、无插件。name/description显式whitespace/lowercase/BM25；给定中文空格词，不测分词器效果。HZ/open/CNY/0..10000分；按_score降序、业务ID升序。应用沿用Boot4.0.8/JDK25/官方Java与Rest5 Client9.4.8、Wrapper3.3.4/Maven3.9.11。

需要Docker/Compose、Bash、curl、Python3，Java用JDK25。终端一从仓库根目录：

```bash
cd projects/travel-search
export ES_URL=http://127.0.0.1:19222
export APP_URL=http://127.0.0.1:18081
docker compose -f infra/f22/compose.yaml up -d es
bash infra/f22/wait.sh
# 已有本课索引先cleanup，再从01重做
bash labs/f22/01-prepare.sh
bash labs/f22/02-adjust.sh
bash labs/f22/03-holdout.sh
bash labs/f22/04-boundaries.sh
```

| 案例/入口 | 教学HTTP | 判断 |
| --- | --- | --- |
| f22-c01 / 01＋02 | 9＋12 | 版本/插件/green/Bulk24/count/mapping/settings；4调整×2策略搜索，再用2种_rank_eval核对Python完整公式 |
| f22-c02 / 03＋04 | 8＋11 | 2留出×2策略、冻结门槛；未标注/短结果/空集/全0标签/候选漏召回/非法k/HTTP200内失败与恢复 |
| f22-c03 / 06 | 8 | 先保存独立作答，再揭示2新查询的固定策略结果 |
| Java↔REST / 05 | 22 | 六种输入：6Java＋16实际搜索DSL重放；Java内部16ES搜索另计 |
| 合计 | 70 | 探活/清理/作者附加/浏览器调用另计 |

终端二从仓库根目录：

```bash
cd projects/travel-search/backend
# JAVA_HOME/PATH先选JDK25
./mvnw -B -ntp clean package
ES_URL=http://127.0.0.1:19222 APP_PORT=18081 java -jar target/travel-search-0.7.0.jar
```

终端一仍在projects/travel-search：

```bash
bash labs/f22/05-java.sh
# 先完成assessment.md，保存自己的判断与改法，再揭示参考输出
bash labs/f22/06-assessment.sh
# 可选手工调用，不计70
curl --fail-with-body -sS -X POST "$APP_URL/api/quality/evaluate" -H 'Content-Type: application/json' --data '{"split":"adjust","strategy":"candidate"}'
```

打开http://127.0.0.1:18081/f22.html。切换查询集/策略会清空旧结果；展开完整DSL、ES响应和DTO，核对ID、人工等级、ES_score和指标。浏览器→Java→ES，无直连或凭据；Pages只承载教程。每条查询顺序执行，不承诺跨请求原子快照，固定资料才能直接比较。

等级0–3，Recall相关阈值≥2；标准DCG=sum((2^等级−1)/log2(名次+1))，IDCG由完整标注取理想前10。先逐查询后等权平均，调整/留出分开。ES9.4.0内置normalized DCG在返回不足K时截断理想长度：短探针1，与本课完整IDCG口径0.765361不同。八条主查询都返回10；REST内置、Python与Java因此一致。无相关查询按0另列，不混主平均。

[预先冻结计划](../../data/f22/decision-plan.json)未因留出改参数。调整nDCG0.768275→0.829090、Recall同0.916667；留出nDCG同0.731603、Recall同0.937500。固定语料内选择candidate，但没有全站收益证据；a15/a07/a10/a11首位坏例仍在。独立任务参考输出在[验收记录](../../review/f22/README.md)，先作答再打开。

非法Java输入400、ES拒绝502、连接/transport503、不完整字段/未知标签/超时/部分分片失败502。真实故障范围见证据；超时/部分分片失败未构造。_rank_eval必须另查failures、details覆盖和unrated_docs，HTTP200不代表完整评估。

点名清理与完整重做：

```bash
bash labs/f22/cleanup.sh
bash labs/f22/01-prepare.sh
bash labs/f22/02-adjust.sh
bash labs/f22/03-holdout.sh
bash labs/f22/04-boundaries.sh
bash labs/f22/05-java.sh
bash labs/f22/06-assessment.sh
# 结束后另关闭自己启动的Java
bash labs/f22/cleanup.sh
docker compose -f infra/f22/compose.yaml stop es
```

cleanup只DELETE tut-f22-attractions并GET404，不删卷或其他索引；重复创建400、重复Bulk create24项409。停止保留数据。仅回环、无安全的隔离教学节点不作生产配置。

[完整请求](../../search/f22) · [资料/标注](../../data/f22) · [真实两轮](../../review/f22/README.md) · [内容/图解/HTTP与视觉](../../../../docs/framework-review/20261026-f22-evaluation/README.md)。未测代表性流量、显著性、标注者一致性、性能、多节点、生产安全或持续更新；F23未实施。
