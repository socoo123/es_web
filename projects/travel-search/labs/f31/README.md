# F31 · 分配、扩缩容与 resize 条件

[教程](../../../../framework/f31.html)先解释旅游搜索中“能读、但副本未分配”的现象。实验复用F07的Java搜索与观察窗，运维请求直接操作本课隔离ES，不新增Controller或前端。ES 9.4.0 / Lucene 10.4.0；Boot 4.0.8、应用JDK 25、Java与Rest5 Client 9.4.8；ES内置JVM另记。

在仓库根目录执行（JAVA_HOME/PATH须先指向完整JDK25）：

```bash
cd projects/travel-search
python3 labs/f31/lab.py start --out /tmp/f31-reader-setup
```

另一终端：

```bash
cd projects/travel-search/backend
./mvnw -B -ntp clean package
ES_URL=http://127.0.0.1:19531 ES_INDEX=tut-f31-attractions APP_PORT=18081 \
  java -jar target/travel-search-0.7.0.jar
```

回到项目目录：

```bash
export APP_URL=http://127.0.0.1:18081
python3 labs/f31/lab.py run --out /tmp/f31-reader-round1
```

每个`--out`必须是新目录。start首次只在n1/n2基础卷均不存在时使用bootstrap，形成后实际移除名单、核对UUID/node ID；完整旧卷直接启动，缺部分基础卷则拒绝自动引导。n3仅data，按实验加入。已有同名卷必须带本课标签。默认拓扑n1(master/data/ingest)+n2(data)，扩容n3(data)；19531–19533仅回环HTTP，transport仅本课网络，无认证。唯一master候选n1在本课不停止，不是高可用拓扑。每节点192MiB堆/640MiB上限只用于6份小资料，先检查Docker及原服务可用内存；三容器共用Docker VM/磁盘，不能代表独立物理机器。

| 案例 | 输入与操作 | 应解释的输出 |
| --- | --- | --- |
| f31-c01-filter-and-expansion | 显式2主/每主1副/routing shards=8、strict、whitespace、refresh=-1；require只准n1；Bulk/refresh；增加n3；解除require | 0号副本在n1被same_shard拒绝、n2/n3被filter拒绝；新增节点仍yellow；修复后4份STARTED覆盖3节点，完整6份_source与搜索p01/p02不变 |
| f31-c02-disk-and-drain | 实际free先需在2GiB–10TiB之间；临时low=10tb/high=1gb/flood=512mb；副本1→2；恢复水位等6份启动，再回1副；排空n2/停机/恢复n2/排空停n3 | 新需2份因disk_threshold=NO未分配，旧4份可读；没有实际写满磁盘或触发high/flood；排空反复等实际零分片、STARTED与PEER/DONE并逐字段核对后才停；最终n1+n2原身份，集群临时设置清空 |
| f31-c03-resize-conditions | 直接更新主片数、未阻塞源split、阻塞后split到3/6、合法split到4；强制4片各2分散→shrink拒绝→集中n1→shrink2；预建3主mapping→reindex；仅源p01改价 | 400/500/403各有具体原因；2→4、4→2与reindex→3均保存6个ID、全部字段、mapping与代表查询；最后源65元/三个目标60元，目标不持续跟随 |

完整执行顺序与断言见[lab.py](lab.py)。教学REST每轮81次（12+23+46），Java接口另7次；Java返回的DSL再用REST重放已计入81次。启动/身份/guard/恢复/轮询/清理/Compose命令分别标记；首轮作者可选浏览器钩子产生的28次Java调用及28次REST重放另记，不混作教学HTTP。浏览器并不直连ES。

本机观察窗 <http://127.0.0.1:18081/> 使用西湖/HZ/预算20000分/30.25,120.15/3km：初始、加节点仍yellow、修复、磁盘拒绝与排空均为p01/p02、60元/0元；最后源单独改价为65元/0元。卡片和DSL需与原始REST核对。源与目标ID次序使用显式`attraction_id`升序，不比较不同分片数量的浮点评分。

中断恢复和清理后重做：

```bash
python3 labs/f31/lab.py recover --out /tmp/f31-reader-recover
python3 labs/f31/lab.py run --out /tmp/f31-reader-round2
python3 labs/f31/lab.py cleanup --out /tmp/f31-reader-cleanup
python3 labs/f31/lab.py down --out /tmp/f31-reader-down
```

recover启动原n2，恢复本课三水位/exclude/require/写阻塞，排空后停n3，回到基础两节点；仅适用本课专用配置。它不保留自行混入的水位定制；guard拒绝外来索引。run每轮先点名删除8个索引，再建6000分资料。cleanup只删`attractions/split4/shrink2/reindex3/bad-open/bad3/bad6/bad-shrink`八个`tut-f31-`完整名字。down移除本课容器/网络，保留三卷；Java在原终端Ctrl+C停止。不触及其他课、其他容器或原业务数据，不用通配符清理，不强制分配陈旧主片。

磁盘百分比为已用比例，字节为至少保留的可用量；阈值不能跨两种口径随意混配。本课提高low仅用于制造可解释的拒绝，未关闭磁盘保护。排空以路由为准；green不是异步规划完成证明，移动副本的PEER source不一定是被排空节点。

[两轮实际记录](../../review/f31/README.md)与[阅读/图解记录](../../../../docs/framework-review/20261028-f31-allocation/README.md)分开。未验证真实满盘/high/flood写封锁、磁盘扩容、跨机器、持续并发、性能或恢复时限。F32/F33才系统学习模板、alias与受控重建切换。
