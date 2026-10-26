# F23 · 酒店、房型与offer文档边界

[正文](../../../../framework/f23.html)先解释酒店/房型/报价三种身份，再看搜索单位、隐藏文档与更新范围。本课3家酒店/5房型/8报价，一份[canonical catalog](../../data/f23/catalog.json)生成四个搜索投影；不是生产同时维护四索引的建议。

独立ES9.4.0/Lucene10.4.0、127.0.0.1:19223，一主零副本、strict/refresh=-1、无插件。金额为最小货币单位整数，CNY分/USD美分；单晚2026-11-01，snapshot_at=2026-10-26T00:00:00Z，非实时库存或订单能力。nested只声明rooms，内部rates仍object，仅作完整明细取回；本课报价组合条件全部在独立offer执行。F24多条件nested/inner_hits/sort尚未实施。

需要Docker/Compose、Bash、curl、Python3；Java需JDK25。终端一从仓库根目录：

```bash
cd projects/travel-search
export ES_URL=http://127.0.0.1:19223
export APP_URL=http://127.0.0.1:18081
export F23_OUT=/tmp/f23-reader-first
docker compose -f infra/f23/compose.yaml up -d es
bash infra/f23/wait.sh
# 已有本课索引先cleanup；不要删其他课
bash labs/f23/01-prepare.sh
bash labs/f23/02-boundaries.sh
bash labs/f23/03-updates.sh
```

| 案例/入口 | 教学HTTP | 逐项证据 |
| --- | --- | --- |
| f23-c01 / 01 | 38 | 版本/插件；四索引green/Bulk17项created/count/mapping/settings/底层docs/全部_source |
| f23-c02 / 02 | 14 | 酒店/单房型ID返回单位、错误nested作用域0/正确h01、房型GET404、独立offer及删币种/两层状态反例与恢复 |
| f23-c03 / 03 | 28 | nested根改价、实际段观察、旧版本409/错根ID404；独立offer改价、更名四副本、精确恢复 |
| Java↔REST / 04 | 10 | 五种固定mode：5Java＋5实际DSL重放；Java内部5ES搜索另计 |
| 合计 | 90 | 探活/清理/作者附加/真实浏览器调用另计 |

终端二从仓库根目录：

```bash
cd projects/travel-search/backend
# JAVA_HOME/PATH先选JDK25
./mvnw -B -ntp clean package
ES_URL=http://127.0.0.1:19223 APP_PORT=18081 java -jar target/travel-search-0.7.0.jar
```

终端一仍在projects/travel-search：

```bash
bash labs/f23/04-java.sh
# 可选手工调用，不计90
curl --fail-with-body -sS -X POST "$APP_URL/api/model/inspect" \
  -H 'Content-Type: application/json' --data '{"mode":"offers-flex"}'
```

打开http://127.0.0.1:18081/f23.html，按五个选项核对实际根ID、完整_source与DSL。前三项返回h01，后两项返回[o101,o201]与[o102,o104,o203]；total是当前模型根文档单位，不能把3报价直接称作3酒店。客户端重序列化响应会省略null的_score/max_score，重放只归一化这两处，_source/ID/排序/total完整一致。完整预算结果所属酒店[h01,h01,h02]，本小结果手工去重2家，不是通用计数算法。

四索引root数3/3/3/8，Lucene live3/3/8/8。一次o101改价：nested更新h01根并重写h01＋2个房型块；独立offer仅o101根变化，其余7份不变。h01更名后四条报价副本不会自动传播，显式update_by_query更新4条且核对failures/冲突。该API不是跨文档事务；refresh=-1时先刷新已写版本再发起后续按查询更新。本课探索保留了未刷新造成3成功/1冲突409的原始失败，最终流程修正后两轮完整复跑。deleted段统计会随merge回收，不是稳定写放大计数；不声称性能结论。

清理与重做：

```bash
bash labs/f23/cleanup.sh
export F23_OUT=/tmp/f23-reader-repeat
bash labs/f23/01-prepare.sh
bash labs/f23/02-boundaries.sh
bash labs/f23/03-updates.sh
bash labs/f23/04-java.sh
# 完成后另关闭自己启动的Java
bash labs/f23/cleanup.sh --out /tmp/f23-reader-final-cleanup
docker compose -f infra/f23/compose.yaml stop es
```

cleanup只DELETE tut-f23-hotels/object/nested/offers四索引，各GET404，保留卷、镜像与其他节点。日志不覆盖旧收据，重跑换F23_OUT或显式--out。未清理重建400，Bulk create条级409；不能把重复导入当新实验。所有Compose只绑定回环且关闭安全，供独立教学，非生产配置。

[全部数据](../../data/f23) · [完整DSL](../../search/f23) · [真实两轮](../../review/f23/README.md) · [内容/图解/HTTP/实际截图](../../../../docs/framework-review/20261026-f23-model/README.md)。不测真实供价同步、并发库存、税费、连住、生产安全、多节点或性能；超时/部分分片失败只有代码防护，无故障注入。
