# F06 · bool 与城市、预算、状态和半径组合

[正文](../../../../framework/f06.html) · [案例清单](cases.json) · [真实执行状态](../../review/f06/README.md)

**当前真实 ES 验收受阻，以下集合为预测，不是响应。** ES9.4.0 在当前云环境缺少 `/proc/self/coredump_filter`，HTTP前退出；原Compose和读者脚本没有为此改动。读者在能运行原环境的本机复现。

## 前提与固定输入

Docker/Compose v2、Bash、curl7.76+。复用课程专用Compose，127.0.0.1:19200、travel-search-lab、ES9.4.0、1主0副本、无认证、持久卷；不访问源码篇9200/9201。无需Java、展示壳、中文插件或数据库。

- [12份源文档](../../data/f06/attractions.json)、[24行NDJSON](../../data/f06/attractions.ndjson)、[A–L与ID](../../data/f06/labels.json)
- [显式mapping](../../search/f06/index.json)：逐字继承F05；A–E源文档也完整保留，F–L是新增合成对照
- [预测与断言目标](../../search/f06/expected.json)，按ID字典序核对完整集合，不是按A–L顺序或相关性排序

金额整数分，币种CNY，0=免费；200元=20000分。H省略价格，I显式null，K缺status，L缺location。没有价格null_value，strict不要求必填、不限制状态枚举、不自动拒绝负数。主查询明确价格gte0/lte20000、status=open。

所有坐标是合成WGS84教学点，不代表真实景点位置。圆心lat30.25/lon120.15、3km、arc；A圆心、B约1.47km、J约38.92km。球面近似只帮助判断集合，未实测ES距离，也不测试3km厘米边界。对象lat/lon；数组是[lon,lat]。地理半径不是路线距离或行政区划。

## 首次运行

从仓库根目录：

```bash
cd projects/travel-search
docker compose -f infra/single-node/compose.yaml up -d
bash infra/single-node/wait.sh
bash labs/f06/01-prepare.sh
bash labs/f06/02-hard.sh
bash labs/f06/03-boundaries.sh
bash labs/f06/04-should.sh
```

或者进入工程目录后 `bash labs/f06/run.sh`；它启动原Compose、等待，再原样执行四组脚本，不自动清理初始索引。env.sh固定专用ES_URL并切换到工程目录，因此也可以在仓库根用完整脚本路径调用。启动等待探测不计入教学请求。

1. **f06-c01 / 01+02**：准备6条请求（版本、PUT索引、限定健康、mapping、Bulk、refresh），搜索6条（all/keyword/city/budget/open/near）。先核对9.4.0/travel-search-lab、创建确认、green且未超时、mapping、12项created/version1、refresh无失败。集合12→11→7→5→3。
2. **f06-c02 / 03**：4条搜索，严格上限、免费、缺价、未下架对照。主查询保留全部硬条件；missing-price是独立HZ/CNY数据诊断。
3. **f06-c03 / 04**：6条搜索，主查询短语可选/必选，独立should选A/B、加城市默认/显式要求，最后filter-only评分上下文对照。

每轮共22条教学HTTP请求；点名清理另1条，启动探活和作者预检/断言读取另计。HTTP200不证明Bulk每项成功，也不证明命中语义合格。

## 完整请求与预测

所有搜索均 `POST /tut-f06-attractions/_search`，脚本顺序与下表一致。size20覆盖12条，track_total_hits=true，track_scores=true；投影包括ID、名称、城市、价格、币种、状态、location；按attraction_id asc只为稳定核对。

| 完整请求体 | 预测样本 | total |
| --- | --- | --- |
| [all.json](../../search/f06/all.json) | A / B / C / D / E / F / G / H / I / J / K / L | 12 |
| [keyword.json](../../search/f06/keyword.json) | A / B / C / D / E / F / G / H / I / J / K / L | 12 |
| [city.json](../../search/f06/city.json) | A / B / D / E / F / G / H / I / J / K / L | 11 |
| [budget.json](../../search/f06/budget.json) | A / B / E / F / J / K / L | 7 |
| [open.json](../../search/f06/open.json) | A / B / F / J / L | 5 |
| [near.json](../../search/f06/near.json) | A / B / F | 3 |
| [strict-upper.json](../../search/f06/strict-upper.json) | A / B | 2 |
| [free.json](../../search/f06/free.json) | A | 1 |
| [missing-price.json](../../search/f06/missing-price.json) | H / I | 2 |
| [not-offline.json](../../search/f06/not-offline.json) | A / B / F / K | 4 |
| [should-optional.json](../../search/f06/should-optional.json) | A / B / F | 3 |
| [should-required.json](../../search/f06/should-required.json) | A / F | 2 |
| [should-only.json](../../search/f06/should-only.json) | A / B | 2 |
| [should-filter-default.json](../../search/f06/should-filter-default.json) | A / B / D / E / F / G / H / I / J / K / L | 11 |
| [should-filter-required.json](../../search/f06/should-filter-required.json) | A / B | 2 |
| [filter-only.json](../../search/f06/filter-only.json) | A / B / F | 3 |

near必须返回a-hz-xihu、a-hz-tea、a-hz-boundary的集合。检查timed_out=false、_shards.failed=0、total的value/relation=eq、全部_id与投影_source；缺字段仍缺，null价格仍null。字母顺序不是响应顺序。完整expected.json按ID字典序列出断言目标。

- keyword仍为name的OR：B因name里有湖命中，不是description。
- strict-upper只将lte20000改lt20000，排除F；free只把价格条件改为term0，其他硬条件不变，得到A。
- missing-price以must_not exists诊断无索引价格的H/I，不等于免费，也不含其他主查询要求。
- not-offline移除明确open，改排除offline，K因缺状态被放进来，得到A/B/F/K。
- should-optional给主查询加短语偏好，默认0，B仍入选；显式minimum_should_match=1后只剩A/F。
- should-only只选A/B，默认1；should-filter-default增加同层城市filter后默认0，返回全部HZ；should-filter-required显式1恢复A/B。这三条独立请求没有预算/状态/半径要求。
- filter-only把match也移入filter，集合仍A/B/F，预计_score均0；near与主should对照预计为正分，不锁定具体BM25、排名或性能。

逐条执行例子（在工程目录，先source环境）：

```bash
source labs/f06/env.sh
curl --fail-with-body -sS -X POST "$ES_URL/tut-f06-attractions/_search?pretty" \
  -H 'Content-Type: application/json' --data-binary @search/f06/near.json
```

## 重复、错误与点名清理

重复执行查询不改文档；重复准备时索引已存在会失败，不能忽略后继续拿旧样本验收。确认本课资料可删后：

```bash
bash labs/f06/cleanup.sh
bash labs/f06/01-prepare.sh
bash labs/f06/02-hard.sh
bash labs/f06/03-boundaries.sh
bash labs/f06/04-should.sh
```

cleanup只发DELETE tut-f06-attractions，ignore_unavailable=true便于点名重做；没有通配符，不触碰F03/F04/F05、业务索引或卷。脚本失败先保留stdout/stderr、HTTP体、mapping和版本，按层集合定位。连接拒绝时先查原Compose日志；资源已存在先判断是否保留。不要用去掉所有过滤或删除卷来让输出“看起来成功”。

结束课程专用节点可手工 `docker compose -f infra/single-node/compose.yaml stop`，卷保留；同节点其他课索引也暂不可访问。

作者的 [两轮验收](../../review/f06/verify.py) 原样调用本课脚本并保留响应，拒绝自动删除初始已存在资源；每轮成功后只清理本课索引再重做。读者不必学习测试框架。当前执行状态不能以预测、源码或截图替代。
