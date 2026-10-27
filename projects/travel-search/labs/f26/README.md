# F26 · collapse、酒店去重与最低价范围

[正文](../../../../framework/f26.html) · [固定逐晚表](../../data/f26/stay-table.json) · [完整DSL](../../search/f26) · [真实验收](../../review/f26/README.md)

固定条件：杭州/双床/含早/flexible/CNY、一间两成人，2026-11-01入住、03离店（Asia/Shanghai）。16条报价/9酒店；ES静态条件10条/6酒店，逐晚合格7条/4酒店。只比较固定快照的两晚房费，不含税费、不锁库存。

从仓库根目录启动，单独使用19226，不清理其他课资源：

```bash
cd projects/travel-search
docker compose -f infra/f26/compose.yaml up -d
bash infra/f26/wait.sh
export ES_URL=http://127.0.0.1:19226
export APP_URL=http://127.0.0.1:18081
export F26_OUT=/tmp/f26-reader-round1
bash labs/f26/01-prepare.sh
bash labs/f26/02-collapse.sh
bash labs/f26/03-inner.sh
```

另一终端从仓库根目录，先将JAVA_HOME/PATH配置为JDK25：

```bash
cd projects/travel-search/backend
./mvnw -B -ntp clean package
ES_URL=http://127.0.0.1:19226 APP_PORT=18081 java -jar target/travel-search-0.7.0.jar
```

返回第一终端，执行Java与REST精确重放核对；访问本机 `http://127.0.0.1:18081/f26.html`：

```bash
bash labs/f26/04-stays.sh
curl --fail-with-body -sS -X POST "$APP_URL/api/collapse/inspect" \
  -H 'Content-Type: application/json' --data-binary @search/f26/all-input.json
```

`top-offers`只核对前2条，h01/o01=100000、h02/o05=120000分；`top-hotels`折成前2家、组内完整核对5条，h01/o02=80000、h02/o06=100000；`all`完整核对10条，酒店[h04,h05,h01,h02]、最低总价[60000,60000,80000,100000]。h03缺晚/售罄，h09最短入住失败。起价与总价单位分别为每晚每间、整段一间，均整数CNY分。USD报价排除。

三案例24教学HTTP（14+4+6），Java内部3搜索另计。准备含完整mapping/settings/source检查；GET mapping省略显式默认doc_values:true时仅规范化该项。主流程响应、预期错误、重复与清理分别留收据。接收目录须新建，防止覆盖旧证据。命令里的额外手工curl不计入24条。

```bash
python3 labs/f26/lab.py errors --out /tmp/f26-reader-errors
bash labs/f26/cleanup.sh --out /tmp/f26-reader-between
export F26_OUT=/tmp/f26-reader-round2
bash labs/f26/01-prepare.sh
bash labs/f26/02-collapse.sh
bash labs/f26/03-inner.sh
bash labs/f26/04-stays.sh
```

附加错误29HTTP：重复创建400、Bulk16项409、6种输入400、4种collapse/分页约束400、strict错误400、旧快照/组内超过10/全量超过100时502与恢复。新建索引不是幂等成功，Bulk HTTP200不表示条目全成功。实验假定准备后的快照不被并发写入；不是生产库存一致性或并发分页方案。

结束时关闭自己启动的Java，只清理点名索引；下述stop保留本课数据卷：

```bash
bash labs/f26/cleanup.sh --out /tmp/f26-reader-final
docker compose -f infra/f26/compose.yaml stop es
```

若要移除自己启动的本课容器/网络，可执行同一compose文件的`down`，不要加`-v`。教学节点只绑定回环地址、无认证；生产安全在F35。浏览器经Java访问ES，Pages正文不连接本机服务。完整模式上限100、所选酒店组内上限10，检查截断后拒绝精确输出；不是任意规模完整检索的通用方案。
