# F25 · 多晚库存与精确价表核对

[正文](../../../../framework/f25.html)解释为什么摘要命中不能证明连住可售。ES保存12条offer摘要；Java随jar读取同一份[固定逐晚表](../../data/f25/stay-table.json)，逐晚核对并返回拒绝原因。所有样本虚构，快照f25-20261026-v1；酒店当地日期Asia/Shanghai，[入住,离店)，日期范围2026-11-01至04。

每间安排同样成人数，同一房型/计划/币种跨全部住宿晚；capacity为每间人数上限，available_rooms为该晚剩余间数，price_minor为每晚每间金额，CNY整数分（USD样本在候选层排除）。总预算覆盖全部房间/住宿晚。min_stay_arrival只在入住日判断。缺晚/缺价不能当0，不跨offer拼房；不含税费/儿童/入住离店限制细则，不锁库存或实现订单。[完整数据契约](../../data/f25/contract.json)。

独立ES9.4.0/Lucene10.4.0、127.0.0.1:19225，tut-f25-offers，一主零副本、strict/refresh=-1，无插件。Docker/Compose、Bash、curl、Python3与JDK25。终端一从仓库根目录：

```bash
cd projects/travel-search
export ES_URL=http://127.0.0.1:19225
export APP_URL=http://127.0.0.1:18081
export F25_OUT=/tmp/f25-reader-first
docker compose -f infra/f25/compose.yaml up -d es
bash infra/f25/wait.sh
# 已有本课索引时，先用cleanup；不要删除其他课资源
bash labs/f25/01-prepare.sh
bash labs/f25/02-candidates.sh
```

终端二从仓库根目录，先将JAVA_HOME/PATH配置为JDK25：

```bash
cd projects/travel-search/backend
./mvnw -B -ntp clean package
ES_URL=http://127.0.0.1:19225 APP_PORT=18081 java -jar target/travel-search-0.7.0.jar
```

应用基线Boot4.0.8、Java与Rest5 Client9.4.8、Wrapper3.3.4/Maven3.9.11。应用JDK25与ES bundled JVM独立记录。Jar打包../data/f25/stay-table.json；更改价表后需重新打包并重启。Java不回退到F24索引、不把逐晚表放浏览器配置中。

终端一继续：

```bash
bash labs/f25/03-stays.sh
bash labs/f25/04-variations.sh
# 可选手工观察，不计教学21次
curl --fail-with-body -sS -X POST "$APP_URL/api/stay/inspect" \
  -H 'Content-Type: application/json' --data-binary @search/f25/two-nights-input.json
```

| 案例 | 教学HTTP | 实际判断 |
| --- | --- | --- |
| f25-c01 / 01+02 | 13 | 准备10次＋候选/摘要3次；12条完整源；默认8候选，o02/o03摘要两端覆盖仍缺晚/售罄 |
| f25-c02 / 03 | 2 | Java＋完整DSL的REST重放；o01/o04/o10分别70000/65000/90000分，5种拒绝原因 |
| f25-c03 / 04 | 6 | 两间/三晚/一晚各Java＋REST；合格数2/4/7；核对每个住宿晚和总价 |
| 合计 | 21 | Java内部另有4次ES搜索；探活/错误/清理/浏览器另计 |

打开http://127.0.0.1:18081/f25.html。切换四个对照，再提交。修改条件和失败都会清空旧结果。卡片显示报价/酒店/房型/计划、逐晚库存/价格/入住日最短晚数、失败日期和总价。候选数与合格offer数不同；不做酒店去重或总价排名。输入也可手改，但必须在固定日期窗内；每间成人1–4、房间1–3、总预算1–2000000整数分。

ES只筛必要条件：静态政策/人数、日期最小值和最大值加一日、整个表的最大库存。max库存不保证每晚足够，min_price_minor不是连住总价；本课不以最低单晚价限制预算。Java要求精确total与实际取回数量一致，并逐条检查ES摘要与打包表完整相等，再核对逐晚规则。完整候选过100条会502，不能静默只核对前100条并宣称全部；这不是扩展到大数据集的方案。

可选附加29HTTP：

```bash
python3 labs/f25/lab.py errors --out /tmp/f25-reader-errors
```

重复创建400、重复Bulk12项409、10种非法输入400、快照错配502及恢复、109候选仅取100的502及恢复、strict错误400。响应中的null评分字段仅在REST↔typed响应比较时归一化，ID/排序/源/total/每晚字段/价格全量核对。独立手工价格和拒绝常量在脚本中，不把Java计算本身当真值。

清理后重做：

```bash
bash labs/f25/cleanup.sh --out /tmp/f25-reader-between
export F25_OUT=/tmp/f25-reader-repeat
bash labs/f25/01-prepare.sh
bash labs/f25/02-candidates.sh
bash labs/f25/03-stays.sh
bash labs/f25/04-variations.sh
# 关闭自己启动的Java后，点名清理本课
bash labs/f25/cleanup.sh --out /tmp/f25-reader-final
docker compose -f infra/f25/compose.yaml stop es
```

cleanup仅DELETE tut-f25-offers并GET404；不删卷/镜像/其他课。日志目录不覆盖，重复用新的F25_OUT。Compose绑定回环、关闭安全，只用于本机隔离教学。主流程只读快照，prepare/cleanup和可选错误探针有写操作。未测性能、代表性负载、多节点/生产安全、实时供价/CDC、税费/取消罚金/订单事务；超时/部分分片失败只有代码防护，未注入。[两轮实际记录](../../review/f25/README.md) · [图/HTTP/视觉](../../../../docs/framework-review/20261026-f25-stay/README.md)。F26未实施。
