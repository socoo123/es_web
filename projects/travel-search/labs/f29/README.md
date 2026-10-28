# F29 · 主副分片、routing 与读写路径

[正文](../../../../framework/f29.html)；ES 9.4.0 / Lucene 10.4.0，三进程在同一 Docker VM。沿用 F28 的角色形状，使用独立 `es-framework-f29` 容器/网络/三份卷，回环端口 19329/19330/19331，data 节点为后两者。无认证的隔离实验；transport 不映射宿主。每节点 256MiB 堆、768MiB 容器限制，不是生产建议。

只操作 `tut-f29-default` / `tut-f29-routed`。均显式 2 主、每主 1 副、strict、refresh=-1、whitespace；未分区、无 routing_path、无 alias、未做 resize。以本课 **新建索引的创建版本** 判断路由，不以节点版本代替。每次 Bulk 逐项核对 201/created、成功两拷贝，然后显式 refresh。不要在脚本后再重复手工建索引。

从仓库根目录进入项目；Python 3 标准库只是配套执行工具：

```bash
cd projects/travel-search
python3 labs/f29/lab.py start --out /tmp/f29-reader-setup
```

start 仅在三份卷都不存在时叠加 bootstrap.yaml，形成后立即从实际运行配置移除引导名单并核对 UUID/node ID；三份都已存在时用稳定配置恢复。部分卷缺失时拒绝自动引导。每个收据目录必须全新。

另开终端，先配置完整 JDK 25 的 JAVA_HOME/PATH，再构建并运行既有 F07 服务：

```bash
cd projects/travel-search/backend
./mvnw -B -ntp clean package dependency:build-classpath -Dmdep.outputFile=target/f29-classpath.txt
ES_URL=http://127.0.0.1:19330 ES_INDEX=tut-f29-default APP_PORT=18081 \
  java -jar target/travel-search-0.7.0.jar
```

Boot 4.0.8、Java/Rest5 Client 9.4.8；不变更共享服务或前端。`dependency:build-classpath` 仅给本课独立 Java 源文件提供同一依赖，路径文件留在被忽略的 target/。本课实际补丁、构建及应用 JDK/ES 内置 JVM 分别见 [runtime](../../review/f29/runtime.json)。

回到第一个终端，也配置 JDK 25，然后顺序执行：

```bash
export APP_URL=http://127.0.0.1:18081
export ES_URL=http://127.0.0.1:19330
export F29_OUT=/tmp/f29-reader-round1
python3 labs/f29/lab.py cleanup --out "$F29_OUT/before"
python3 labs/f29/lab.py default --out "$F29_OUT/default"
python3 labs/f29/lab.py routing --out "$F29_OUT/routing"
python3 labs/f29/lab.py reads --out "$F29_OUT/reads"
python3 labs/f29/verify-java.py --out "$F29_OUT/java"
```

3 案例：默认分布与既有搜索；自定义路由的正确/缺失/跨片/同片错误及同 ID 重复与恢复；全索引/限定范围/城市过滤和主副读取。主流程 62 次 HTTP=21+28+13，其中 1 次到 Java 接口，其他为 REST；Java 接口内部 ES 请求另计。独立 Java lab 13 次 SDK 调用、5 次独立 REST 验证另计。启动、等待、清理、作者浏览器操作也分列；不声称抓包统计底层客户端重试。

固定值先由 `_search_shards` 实测：HZ→0、SH→1、FZ→0。脚本重新核对此条件，不假定任意不同字符串必跨片。默认景点 p01–p06；路由景点 r01/r02/r05→HZ，r03/r06→SH，r04→FZ。JSON/NDJSON逐份保存。r04与杭州同片，展示 routing 不替代城市条件。两轮后完整比对 `_source`、routing 和逻辑文档数 6；故意重复的 r01/SH 和 java-probe 已删除，r01/HZ价格恢复6000分。

浏览器打开 `http://127.0.0.1:18081/`，搜索“西湖”、HZ、预算200元、中心30.25/120.15、半径3km，卡片为p01/p02；预算50元只p02。真实链路为浏览器→Java→默认索引，展示壳没有 routing 输入，自定义路由由独立 Java lab/REST 观察。Pages 不调用本机业务服务。

独立重做只需点名清理索引再用新收据目录执行以上四步，集群和 Java 无需重启：

```bash
python3 labs/f29/lab.py cleanup --out /tmp/f29-reader-between
export F29_OUT=/tmp/f29-reader-round2
python3 labs/f29/lab.py default --out "$F29_OUT/default"
python3 labs/f29/lab.py routing --out "$F29_OUT/routing"
python3 labs/f29/lab.py reads --out "$F29_OUT/reads"
python3 labs/f29/verify-java.py --out "$F29_OUT/java"
```

结束：删除两个本课索引，停止自己启动的 Java，用稳定配置 down；三份卷保留。若确需全新首启，用带显式删除标记的 reset，只删本课三份练习卷，不 prune：

```bash
python3 labs/f29/lab.py cleanup --out /tmp/f29-reader-final
docker compose -f infra/f29/compose.yaml down
# 可选：确认不再需要本课数据后再执行；会删除本课三个卷。
python3 labs/f29/lab.py reset --delete-f29-data --out /tmp/f29-reader-reset
```

不在本课实施选举/主分片提升、数据故障/恢复、扩缩容、路由热点基准、跨主机容灾或权限隔离。`_only_nodes`/`profile` 仅用于诊断指定拷贝，常规搜索不固定物理节点；副本不代替备份。
