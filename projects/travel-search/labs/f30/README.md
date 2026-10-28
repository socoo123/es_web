# F30 · 选主与数据节点失效

[正文](../../../../framework/f30.html)。本课只运行隔离 `es-framework-f30`；ES9.4.0/Lucene10.4.0，四进程在同一个Docker VM，不是跨机器容灾。所有HTTP绑127.0.0.1，无认证；transport不发布宿主端口。

| 服务 | HTTP端口 | 角色 | 堆 / 容器上限 |
| --- | --- | --- | --- |
| m1 | 19430 | master | 128MiB / 512MiB |
| m2 | 19431 | master | 128MiB / 512MiB |
| m3 | 19432 | master,data,ingest | 192MiB / 640MiB |
| d1 | 19433 | data | 192MiB / 640MiB |

固定三票是m1/m2/m3；数据拷贝在m3/d1。m3兼任两种角色。案例一及数据故障前，脚本先确认当选master是m1或m2；若是m3，会在独立preparation阶段停m3，等专用候选当选后带原卷恢复它。完整日志保留这一步，不把混合角色伪装成互不影响。

运行前检查内存及端口。作者的约3.81GiB/2CPU Docker VM曾因五进程试案触发OOM，并意外终止原安全节点；已恢复原容器及原UUID，正式使用四进程。小堆只适用于6份资料，不能外推生产容量，也不应在运行重要服务且资源不足的机器上直接照搬限额。

从仓库根目录开始：

```bash
cd projects/travel-search
python3 labs/f30/lab.py start --out /tmp/f30-reader-setup
```

`start`仅在四份专属卷都不存在时叠加bootstrap，集群形成后立即重建稳定配置，核对原UUID/node ID且运行设置不再含引导名单。已有完整卷直接恢复；部分卷缺失或标签不属于本课则拒绝。首次启动中断且尚未形成集群时先查日志与实际状态，不能反复改引导名单。失败后的收据目录不能复用。

另一终端配置完整JDK25的JAVA_HOME/PATH，构建并启动既有F07服务。锁定Boot4.0.8 / Java与Rest5 Client9.4.8；不修改共享Java与前端。

```bash
cd projects/travel-search/backend
./mvnw -B -ntp clean package
ES_URL=http://127.0.0.1:19430 ES_INDEX=tut-f30-attractions APP_PORT=18081 \
  java -jar target/travel-search-0.7.0.jar
```

回到第一个终端：

```bash
export APP_URL=http://127.0.0.1:18081
python3 labs/f30/lab.py run --out /tmp/f30-reader-round1
```

run先核对本课容器标签与集群名，再点名删除 `tut-f30-attractions` / `tut-f30-metadata`，创建1主1副、strict、whitespace、refresh=-1的索引，逐条Bulk确认、显式refresh。初态p01=6000分；p01/p02匹配“西湖/HZ/20000分/3km”。所有字段、JSON和NDJSON在[data/f30](../../data/f30/)，完整mapping/DSL/input在[search/f30](../../search/f30/)。

| 案例 | 实际操作与判断 |
| --- | --- |
| f30-c01 | 动态识别当前专用master，只SIGKILL它；活入口等待新master/term增长；分片主副与primary term不变；搜索成功、p01改6500并两拷贝确认、临时元数据创建/删除成功；原节点回归 |
| f30-c02 | SIGKILL m1+m2，保留两data；活m3/d1无master且block2，原三票配置仍在；默认write策略下读到6500、改9900与创建索引503；单入口Java因m1停机返回503；回归后字段未被拒绝写改变、临时索引404 |
| f30-c03 | 准备专用master后停实际主片节点，原副本提升且primary term增长；yellow下wait=1写7000、wait=all写9900拒绝；回归目标PEER/DONE且两拷贝字段一致；再同时停m3+d1，m1+m2保留多数和master，red/业务搜索与写入503，而wait=0临时元数据创建成功但分片UNASSIGNED；带原卷回归并逐份核对 |

`events.jsonl`给每个真实请求保存时间、URL、请求体、HTTP状态及响应；teaching/identity/guard/wait/cleanup/java/command分类，preparation独立案例。HTTP教学数由summary汇总；浏览器请求、启动/轮询/清理、Java底层重试不混作教学HTTP。实际数量与两轮证据见[review/f30](../../review/f30/)。

手工阅读请求在正文；脚本是执行顺序与动态停机对象的完整实现。若自行停节点，服务名必须来自当时的角色与分片路由，不可假设primary固定落在某节点。所有操作仅限本课Compose project；脚本不写业务资源，不改集群选举超时，不清卷，不强制分配陈旧主片。

本机观察窗：<http://127.0.0.1:18081/>。浏览器 → 既有Java服务 → ES，输入西湖/HZ/预算200元/半径3km；初态60元，选举恢复65元，提升后70元。停m1+m2时Java仅配置m1，入口断开；全部data停机时m1仍活但ES返回503。两者在现有客户端/异常分支中都返回503 `SEARCH_UNAVAILABLE`，页面清空旧卡片。用原始REST证据区分原因，不能只读通用文案。

可选的Java异常诊断只在 **m1在线、m3+d1已停** 时运行；run会自动恢复，故应手工安排这个故障窗口，不在健康状态期待它成功：

```bash
# 在backend目录构建同一客户端依赖清单
./mvnw -B -ntp dependency:build-classpath -Dmdep.outputFile=target/f30-classpath.txt
# 回到projects/travel-search，JAVA_HOME/PATH仍指JDK25
cd ..
java --class-path "$(cat backend/target/f30-classpath.txt)" labs/f30/java/FailureProbe.java
```

[FailureProbe.java](java/FailureProbe.java)断言顶层为Rest5的ResponseException（IOException子类），记录ES503原文。它是一个独立SDK搜索，不能当作Java接口或浏览器调用次数。

中断恢复、清理与第二轮：

```bash
python3 labs/f30/lab.py recover --out /tmp/f30-reader-recover
python3 labs/f30/lab.py run --out /tmp/f30-reader-round2
python3 labs/f30/lab.py cleanup --out /tmp/f30-reader-cleanup
python3 labs/f30/lab.py down --out /tmp/f30-reader-down
```

recover启动原四服务，保留原卷；run每轮重新清两索引并从6000分开始。cleanup只删除两个点名索引；down只移除本课容器/网络，保留四份卷。Java在自己的终端Ctrl+C停止。`--observer`是作者浏览器证据钩子，读者不需要Playwright。

本课不验证：网络分区、磁盘损坏/卷丢失、并发随机故障、客户端多入口切换、跨机器容灾、备份、性能或恢复时间承诺。读到旧资料与能够提交新写入分别判断；副本不等于备份。
