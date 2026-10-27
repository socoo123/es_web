# F28 · 三节点拓扑、角色、发现与持久首启

[正文](../../../../framework/f28.html) · [隔离配置](../../infra/f28/compose.yaml) · [固定数据](../../data/f28/attractions.json) · [DSL](../../search/f28/search.json) · [实际验收](../../review/f28/README.md)

三个ES9.4.0进程在同一Docker VM内，不是三台物理机器。三个master候选；es1仅master，es2为master/data/ingest，es3为master/data。每节点256MiB堆、768MiB容器限制；无认证、HTTP只绑定回环，transport9300只在本课网络内。端口19228/19229/19230，不触碰9200/9201和其他课。

案例f28-c01：首次形成同UUID、移除首启参数、角色/主副/固定搜索；f28-c02：保留卷完整重启；f28-c03：新错误空卷形成独立UUID，修seed不能合并，挂回原卷恢复。错误实验不删除原n3-data。

从仓库根目录，只启动本课：

```bash
cd projects/travel-search
export APP_URL=http://127.0.0.1:18081
export F28_OUT=/tmp/f28-reader-round1
bash labs/f28/01-topology.sh
```

first拒绝任何已存在的F28数据卷，不自动删数据。它先叠加bootstrap.yaml，等三节点共同形成，再仅用稳定compose.yaml重建容器，立刻移除初始名单并比较UUID/node ID。已有本课数据用稳定配置up -d，不重新bootstrap。

另一终端配置JDK25的JAVA_HOME/PATH，从仓库根目录：

```bash
cd projects/travel-search/backend
./mvnw -B -ntp clean package
ES_URL=http://127.0.0.1:19229 ES_INDEX=tut-f28-attractions APP_PORT=18081 \
  java -jar target/travel-search-0.7.0.jar
```

Boot4.0.8、Java/Rest5 Client9.4.8，复用F07服务，不新增Controller或前端。本机观察窗仍显示F07；打开 http://127.0.0.1:18081/ ，输入西湖/杭州/200元/3公里。浏览器经Java查询，Pages只承载教程。

回到第一个终端，Java已运行：

```bash
bash labs/f28/02-search.sh
bash labs/f28/03-restart.sh
bash labs/f28/04-discovery.sh
```

6份合成景点、2主每主1副、strict/refresh=-1、无插件；每个主副分开在es2/es3，count仍6，全部_source精确核对。三个ES入口均返回p01/p02，卡片60元/0元。Java完整DSL与固定REST JSON精确相等，重放比较ID/计数/卡片字段和score。缺索引502、计划停机503与恢复在实际脚本中核对；/api/health只表示Java进程运行。

restart使用down（无-v）与稳定up，比较原UUID/3个node ID/全部_source/分片/查询，master或主副所在节点允许变化。mistake暂时把es3挂到专用新wrong-data并误配single-node；旧n3-data保留。改回seed、保留错误UUID会有保持独立或加入拒绝的诊断日志，最后只删错误空卷、挂回原n3-data并核对原身份与数据。错误配置不可套用于业务目录。

每个阶段的输出目录必须新建，events.jsonl保存每个实际HTTP（teaching与wait分列）和Docker命令；summary.json单列计数。主流程不包括额外手工curl、Java内部ES请求和读者自己的观察窗点击。等待按真实节点/green/无迁移与初始化重试，超时明确失败。

独立重做首启前，明确清除本课练习资料：

```bash
bash labs/f28/cleanup.sh --out /tmp/f28-reader-between-index
python3 labs/f28/lab.py reset --delete-f28-data --out /tmp/f28-reader-between-volumes
export F28_OUT=/tmp/f28-reader-round2
bash labs/f28/01-topology.sh
bash labs/f28/02-search.sh
bash labs/f28/03-restart.sh
bash labs/f28/04-discovery.sh
```

reset只点名四个es-framework-f28-{n1,n2,n3,wrong}-data卷及本课容器/网络；不prune、不处理其他环境。不同全新轮次UUID应不同，每轮内部应保持原UUID。第一次/重复建索引和Bulk的created/冲突不可混淆。

结束时停止自己启动的Java，删除本课索引并移除容器/网络，保留三份正常卷：

```bash
bash labs/f28/cleanup.sh --out /tmp/f28-reader-final-index
docker compose -f infra/f28/compose.yaml down
```

未测：跨物理机器/随机故障/多数选举/路由/扩缩容/容量性能/TLS/管道/多地址客户端切换。F29讲routing，F30分别讲master和数据副本故障，F35讲安全连接。
