# F21 · 附近、新鲜与显式排序

[正文](../../../../framework/f21.html)先讲用户意图、软衰减与硬资格。[14份虚构资料](../../data/f21/attractions.json)、[字段/时间/缺值契约](../../data/f21/contract.json)。参数不是生产推荐。

独立ES9.4.0/Lucene10.4.0、19221/tut-f21-attractions，一主零副本/strict/refresh=-1、无插件。简介whitespace/lowercase/显式BM25，空格给定整词；名称keyword不评分。游客lat30.25/lon120.15，固定核验原点2026-10-01T00:00:00.000Z；资料核验时间不是开放状态。

需要Docker/Compose、Bash、curl、Python3；Java需JDK25。终端一从仓库根目录：

```bash
cd projects/travel-search
export ES_URL=http://127.0.0.1:19221
export APP_URL=http://127.0.0.1:18081
docker compose -f infra/f21/compose.yaml up -d es
bash infra/f21/wait.sh
# 已有本课索引先cleanup再从01重做
bash labs/f21/01-decay.sh
bash labs/f21/02-combine.sh
bash labs/f21/03-sort.sh
```

| 案例 | 教学HTTP | 判断 |
| --- | --- | --- |
| f21-c01 / 01 | 16 | 版本/插件/green/Bulk14/refresh/count/有效mapping/settings；text、单项衰减、未来探针、3次解释 |
| f21-c02 / 02 | 13 | 六评分模式、实际arc距离、逐份公式、5次解释、weight=0回退反例 |
| f21-c03 / 03 | 20 | 三意图、硬半径/原点改变/预算/异城/空集，默认sort/track_scores/min_score、4个400、6次排除解释 |
| Java↔REST / 04 | 39 | 13输入，每组Java＋实际搜索DSL重放＋完整query解释重放 |
| 合计 | 88 | 清理/探活/构建/Java内部调用/作者附加/浏览器另计 |

终端二从仓库根目录：

```bash
cd projects/travel-search/backend
# JAVA_HOME/PATH先选择JDK25
./mvnw -B -ntp clean package
ES_URL=http://127.0.0.1:19221 APP_PORT=18081 java -jar target/travel-search-0.7.0.jar
```

终端一仍在projects/travel-search：

```bash
bash labs/f21/04-java.sh
# 可选手工调用，不计88
curl --fail-with-body -sS -X POST "$APP_URL/api/attractions/decay-search" -H 'Content-Type: application/json' --data-binary @search/f21/input-sum.json
```

打开http://127.0.0.1:18081/f21.html。六评分模式与三种排序意图分别选择；硬半径可空，空不等于取消地理软奖励。D=0.5^[max(0,dKm-1)/5]^2；T=0.5^[max(0,绝对日期差天数-1)/30]。G=0.5D、H=0.3T，函数值先max_boost=0.8。

- sum：B+G+H；product：B+G×H；multiply：B×(G+H)；replace：G+H。四模式缺失项贡献0；两个互斥函数分支对应每个逻辑信号。
- bare反例：缺值衰减返回1。仅exists或仅weight=0不保证缺两项为0，见02真实反例。本实现缺值用weight=1的Painless常量0.0，不读取用户数据。
- sum仍将弱相关展厅抬到第三；replace展厅第一。不据此宣布质量改善。
- price、distance用显式首sort键，业务ID升序收尾。track_scores=true供观察，不参与排序；缺坐标sort为字符串Infinity，卡片距离为null并提示缺坐标；非距离模式明确提示未选择距离排序。
- 无min_score时零分extreme/missing仍命中；硬半径10km才缩为5份。关闭/异城/超预算/未来核验/无关山林先排除。future-probe故意绕过硬资格验证日期对称性。

每次返回完整DSL、客户端再序列化的完整响应/DTO与_explain。两次请求不是并发原子视图。非法输入400、ES拒绝502、连接/transport503、不完整字段/超时/分片失败502；本课实际未构造超时/部分分片失败。条件变化/失败清空旧内容。浏览器→Java→ES，不直连ES，不含凭据。

点名清理和重做：

```bash
bash labs/f21/cleanup.sh
bash labs/f21/01-decay.sh
bash labs/f21/02-combine.sh
bash labs/f21/03-sort.sh
bash labs/f21/04-java.sh
# 结束，另关闭自己启动的Java
bash labs/f21/cleanup.sh
docker compose -f infra/f21/compose.yaml stop es
```

cleanup只DELETE tut-f21-attractions、GET404，不删其他索引/卷；重复建索引400，重复Bulk create条级409。停止不清持久数据；本课安全关闭且只映射回环端口，不是生产配置。

[完整查询](../../search/f21) · [真实两轮](../../review/f21/README.md) · [图解/HTTP/观察窗](../../../../docs/framework-review/20261026-f21-decay/README.md)。未测整体质量/留出指标、性能、多节点、生产安全、轨迹或持续核验更新。本目录保留F21实验；下一课[F22查询集与质量评估](../f22/README.md)提供独立评估。
