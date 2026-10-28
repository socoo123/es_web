# F33 · 受控 reindex、切换与回滚

[教程](../../../../framework/f33.html)先解释字段变更与数据边界。ES9.4.0/Lucene10.4.0；Boot4.0.8、应用JDK25、Java/Rest5 Client9.4.8。管理操作使用本课REST；复用F07搜索服务与本机观察窗，无新增Controller或前端。ES内置JVM另记。

将JAVA_HOME/PATH指向完整JDK25，在仓库根目录：

```bash
cd projects/travel-search
python3 labs/f33/lab.py start --out /tmp/f33-reader-setup
```

另一终端：

```bash
cd projects/travel-search/backend
./mvnw -B -ntp clean package dependency:build-classpath -Dmdep.outputFile=target/f33-classpath.txt
ES_URL=http://127.0.0.1:19733 ES_INDEX=tut-f33-attractions-read APP_PORT=18082 \
  java -jar target/travel-search-0.7.0.jar
```

回到项目目录：

```bash
export APP_URL=http://127.0.0.1:18082
python3 labs/f33/lab.py run --out /tmp/f33-reader-round1
```

每个收据目录必须是新目录。每轮run先点名删除本课两个索引，然后执行三个案例。首次无alias时，Java搜索失败属于前置尚未完成；实验建立入口后再观察。完整脚本与[手工请求顺序](requests.sh)二选一；手工请求包含预期400/403/404，用`curl -sS`保留错误体。不要在自动脚本中途混入写请求。手工核对不符时停止，不能继续切换。

| 资源 | 配置 |
| --- | --- |
| 集群/网络 | es-framework-f33 / travel-f33-lab，独立Docker网络 |
| n1 / 19733 | master/data/ingest；本课唯一master候选，不停止 |
| n2 / 19734 | data；两节点同Docker VM/磁盘，非跨机器容灾 |
| 两持久卷 | es-framework-f33-n1-data、es-framework-f33-n2-data；down保留 |
| HTTP | 仅127.0.0.1，无认证；transport只在独立网络 |
| 内存 | 每节点192MiB堆、640MiB容器上限，仅供本课小样本 |
| Java | 同一18082进程，ES_INDEX固定tut-f33-attractions-read |
| 两个索引 | tut-f33-attractions-v001：1主/每主1副；v002：2主/每主1副；均refresh=-1、strict、显式refresh |
| 两个alias | tut-f33-attractions-read显式false、write显式true；始终只挂一版 |

start仅在两个基础卷都不存在时bootstrap；成团后移除名单并核对UUID/node ID。原卷完整时直接启动，部分卷缺失则拒绝重新引导。启动前检查Docker资源，不修改其他课或原有节点。

| 案例 | 输入与对照 | 判断证据 |
| --- | --- | --- |
| f33-c01-schema-and-fixed-copy | name=keyword旧版不能直接改text；预建whitespace新目标，复制固定6篇 | 400；token不同；6 created/0 updated/0冲突/空failures；全ID/字段一致，新版西湖为p01/p02，Java入口仍旧版0条 |
| f33-c02-drift-and-frozen-rebuild | 旧版p01改6500分、删除p02、新增p07；再次向非空目标复制；暂停全部写入、旧版write block、refresh；丢弃未上线目标后重建 | 两版各6条却不同；重跑目标7条/p02残留；403且p09不存在；最终两边6条、全字段一致、p02消失；新查询p01/p07 |
| f33-c03-atomic-switch-and-rollback | 错must_exist前提；四动作同时切换read/write；无新业务写入时反向回滚；再次切换后允许写p08 | 404且关系不变；同Java进程0→2→0→3；p08只落v002；旧索引保留不代表恢复写入后可简单回滚 |

主流程请求的实际计数以[两轮summary/events](../../review/f33/README.md)为准，包含断言用全字段/配置/DSL重放；身份、guard、等待、清理与作者浏览器附加请求另计。独立官方Java写入每次仅发送一个请求，成功与403均保留响应。它是实验写入任务，不是游客接口。

固定样本：[旧版JSON](../../data/f33/v001.json)/[Bulk NDJSON](../../data/f33/v001.ndjson)、[p01改价](../../data/f33/p01-updated.json)、[p07新增](../../data/f33/p07.json)、[p08恢复写入](../../data/f33/p08.json)、[p09拒绝样本](../../data/f33/p09.json)。金额CNY整数分。名称带空格以隔离中文插件；whitespace只用于机制观察，不代表中文效果评估。

本机观察窗`http://127.0.0.1:18082/`输入西湖/HZ/20000分/30.25,120.15/3km；`requests.sh`标注5个暂停观察点。浏览器→Java→ES；Pages只承载教程。目标上线前的查询直接通过REST核对，避免为预览改动正式Java入口。

```bash
python3 labs/f33/lab.py run --out /tmp/f33-reader-round2
python3 labs/f33/lab.py cleanup --out /tmp/f33-reader-cleanup
python3 labs/f33/lab.py down --out /tmp/f33-reader-down
```

cleanup只删除`tut-f33-attractions-v001`与`tut-f33-attractions-v002`，附着alias/写阻断随之删除。没有模板、快照仓库或集群设置改动。guard仅额外容许ES自建的`.ds-.logs-elasticsearch.deprecation-default-`和`.ds-ilm-history-7-`两个系统前缀，不清理系统历史。down仅移除本课容器/网络，保留两卷；在Java原终端Ctrl+C停止。

中断后保留失败收据，使用新目录重新run。只有未上线v002可在冻结重建时删除；正式两轮末尾v001保留write block、v002可写，最终cleanup恢复为空课次环境。若手工回滚后决定留在旧版，保持所有写入者暂停、确认alias均回旧版后，才可用`PUT /tut-f33-attractions-v001/_settings`、`{"index.blocks.write":false}`解除阻断；本课正式流程保持暂停并再次切新，没有执行该恢复分支。

未验证随机并发、长任务/中断续作、外部版本、脚本转换、自定义routing、持续增量/删改追平、安全、跨机器、性能或恢复时限。回滚试验严格位于业务写入暂停窗口；新版p08出现后，不执行不安全回滚。F34练独立备份恢复，F41再处理持续变更下的重建。
