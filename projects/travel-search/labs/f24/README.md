# F24 · 同房型条件、inner_hits与nested排序

[正文](../../../../framework/f24.html)先解释object错拼、单个nested与三处范围。9酒店/16条报价，rooms一项代表房型×计划×币种×服务日快照，room_id可重复、offer_id唯一；不复用F23的rates object明细来联合筛选。固定2026-11-01单晚、2026-10-26快照，CNY分/USD美分，不是连住总价或实时可订。

独立ES9.4.0/Lucene10.4.0、127.0.0.1:19224；tut-f24-object与tut-f24-nested，一主零副本、strict/refresh=-1、无插件。Docker/Compose、Bash、curl、Python3，Java使用JDK25。终端一从仓库根目录：

```bash
cd projects/travel-search
export ES_URL=http://127.0.0.1:19224
export APP_URL=http://127.0.0.1:18081
export F24_OUT=/tmp/f24-reader-first
docker compose -f infra/f24/compose.yaml up -d es
bash infra/f24/wait.sh
# 已有本课两个索引时先cleanup，不删其他课
bash labs/f24/01-prepare.sh
bash labs/f24/02-matching.sh
bash labs/f24/03-sorting.sh
```

| 案例/入口 | 教学HTTP | 观察证据 |
| --- | --- | --- |
| f24-c01 / 01 | 20 | 版本/插件、两索引green/Bulk18项created/完整mapping/settings/源；roots9/9，Lucene live9/25 |
| f24-c02 / 02 | 10 | object与split各8酒店；matched仅h02/h03/h08；错误作用域0、错误path400、删人数/退改/币种与恢复 |
| f24-c03 / 03 | 6 | 无filter排序h02/h03/h08=10000/50000/50000分；正确h03/h08/h02=50000/50000/65000分；完整inner/改inner顺序/空sort集合与恢复 |
| Java↔REST / 04 | 10 | 五个固定mode，各1Java＋1真实DSL重放；Java内部5搜索另计 |
| 合计 | 46 | 探活、附加错误、清理和浏览器请求另计 |

终端二从仓库根目录，先配置JAVA_HOME/PATH为JDK25：

```bash
cd projects/travel-search/backend
./mvnw -B -ntp clean package
ES_URL=http://127.0.0.1:19224 APP_PORT=18081 java -jar target/travel-search-0.7.0.jar
```

终端一仍在projects/travel-search：

```bash
bash labs/f24/04-java.sh
# 可选手工Java调用，不计46
curl --fail-with-body -sS -X POST "$APP_URL/api/nested/inspect" \
  -H 'Content-Type: application/json' --data '{"mode":"filtered-sort"}'
```

打开http://127.0.0.1:18081/f24.html，五种选项：object/split为故意错误对照、matched按酒店ID、unfiltered-sort保留错误价格、filtered-sort修复。h02的100元与合格650元同时展示解释问题；h03的inner_total=2、size=1显示o301，_nested.offset指原_source位置而非排名。根_source不被裁剪，room_id不是报价唯一键。sort.filter不会代替query筛酒店，inner_hits.sort也不会改变酒店排序。

主流程只读报价；准备Bulk与cleanup是写操作。可选作者附加探针：

```bash
python3 labs/f24/lab.py errors --out /tmp/f24-reader-errors
```

附加13HTTP：重复创建2个400、18个Bulk条目409、5个非法Java输入400、2个类型/strict错误400、两根计数仍9。HTTP200不能代表Bulk每项成功。raw typed响应省略null的_score/max_score，重放只归一化这些评分空值，源/ID/sort/total/inner_hits逐项精确比较；REST使用完整term.value语法，整份DSL与Java相等。

清理后重做：

```bash
bash labs/f24/cleanup.sh --out /tmp/f24-reader-between
export F24_OUT=/tmp/f24-reader-repeat
bash labs/f24/01-prepare.sh
bash labs/f24/02-matching.sh
bash labs/f24/03-sorting.sh
bash labs/f24/04-java.sh
# 关闭自己启动的Java，再点名删除本课索引
bash labs/f24/cleanup.sh --out /tmp/f24-reader-final
docker compose -f infra/f24/compose.yaml stop es
```

cleanup只DELETE两个点名索引并GET404，保留卷/镜像与其他节点。日志目录不可覆盖，重跑用新F24_OUT。Compose仅回环且关闭安全，供本机隔离教学。未测性能、代表性负载、多节点、实时供价/CDC、连住库存、税费/取消罚金、订单事务；超时/部分分片失败只有代码防护，无注入。[真实两轮](../../review/f24/README.md) · [图解/HTTP/实际视觉](../../../../docs/framework-review/20261026-f24-nested/README.md) · [完整DSL](../../search/f24) · [数据契约](../../data/f24/contract.json)。F25未开始。
