# F34 · 快照、隔离恢复与完整性证明

[教程](../../../../framework/f34.html)先解释副本与历史备份，再逐层验证仓库、终态与可恢复资料。只处理ES9.4.0/Lucene10.4.0；复用Boot4.0.8 / 应用JDK25 / 官方Java与Rest5 Client9.4.8。运维请求留在REST，无新增Controller或前端。ES内置JVM另记。

在仓库根目录：

```bash
cd projects/travel-search
python3 labs/f34/lab.py start --out /tmp/f34-reader-setup
```

另一终端先将JAVA_HOME/PATH指向完整JDK25：

```bash
cd projects/travel-search/backend
./mvnw -B -ntp clean package dependency:build-classpath -Dmdep.outputFile=target/f34-classpath.txt
ES_URL=http://127.0.0.1:19834 ES_INDEX=tut-f34-attractions-read APP_PORT=18082 \
  java -jar target/travel-search-0.7.0.jar
```

回到项目目录，执行完整三案例：

```bash
export APP_URL=http://127.0.0.1:18082
python3 labs/f34/lab.py run --out /tmp/f34-reader-round1
```

每个收据目录必须为新目录，run先点名清理。read alias建立前暂不提交搜索。不要在自动执行中途混入其他写入。自动脚本与[手工请求](requests.sh)二选一；手工先cleanup，再逐节执行并核对，预期500保留错误体（使用curl -sS）。正式脚本的首次快照走accepted+轮询；手工路径用wait_for_completion=true，二者均核对终态，不要求捕捉短暂IN_PROGRESS。节点等待需timed_out=false且节点数/状态正确；408只表示尚未满足等待条件。异常先恢复原卷n2，再停止后续操作。

| 资源 | 配置与范围 |
| --- | --- |
| 集群 | es-framework-f34 / travel-f34-lab；独立网络；不修改9200/9201 |
| n1 / 19834 | master/data/ingest；唯一master候选，始终运行 |
| n2 / 19835 | data；本课只停止它，finally恢复；同Docker VM/宿主盘 |
| HTTP/内存 | 仅127.0.0.1，无认证；每节点192MiB堆/640MiB上限 |
| 数据卷 | es-framework-f34-n1-data、es-framework-f34-n2-data |
| 仓库卷 | es-framework-f34-snapshots；两节点同挂/mnt/f34-repository，path.repo同值 |
| 初始化 | repo-init仅chown 1000:0及chmod0770仓库卷根目录，不递归；新卷默认root权限不能假定ES可写 |
| 备份 | 仓库tut-f34-fs，location=travel-f34；before-delete与missing-primary两快照 |
| 主索引 | tut-f34-attractions-v001：2主/每主1副/strict/refresh=-1/name=text-whitespace |
| 风险索引 | tut-f34-risk：1主/0副，只分配到travel-f34-n2；单条risk-01，故意制造不可用主分片 |
| 恢复索引 | tut-f34-restore-attractions-v001；tut-f34-partial-attractions-v001、tut-f34-partial-risk |
| Java | 同一18082进程，ES_INDEX固定tut-f34-attractions-read；浏览器→Java→ES |

首次仅两个数据卷都不存在才bootstrap；成团后移除初始名单，核对相同UUID/node ID。完整原卷直接重启，部分数据卷缺失拒绝引导。start先核对已有卷标签，避免误用外来仓库卷。三个卷都保留，不能据此宣称物理容灾。

| 案例 | 对照 | 实际判断证据 |
| --- | --- | --- |
| f34-c01-repository-and-complete-snapshot | 错仓库路径/修正；固定六份资料；异步请求/终态 | 500 repository_exception，未注册；verify两节点；accepted=true后元数据SUCCESS，2成功/0失败、空failures；不含全局/功能状态 |
| f34-c02-logical-delete-and-incomplete-snapshot | 改p01/删p02；停无副本risk所在n2；部分备份与恢复 | 两节点均5份/p01=6500/无p02；快照元数据PARTIAL 2成功1失败，_status却SUCCESS/failed1；n2回来risk仍1条；默认restore500；显式partial=true返回200但failed1，隔离risk为空且EMPTY_STORE/DONE |
| f34-c03-isolated-complete-restore-and-search | 同名拒绝/改名；完整字段与查询；隔离恢复/移动read | 已打开同名索引500；新目标6份/p01=6000/p02存在；mapping/设置、两节点读取、SNAPSHOT恢复、无alias；Java隔离时不变，核对后读取历史副本 |

本机观察窗`http://127.0.0.1:18082/`输入西湖/HZ/20000分/30.25,120.15/3km；四点Java为`p01=6000,p02=0 → p01=6500 → p01=6500 → p01=6000,p02=0`。每点Java生成DSL独立REST重放，核对ID/金额/字段。恢复目标继承备份时write block=true，保持历史只读；本课只切read alias，没有建立新写入入口。历史p01价格6000说明备份恢复并不等于最新业务已恢复，合法改价/删除需另按来源对账与补齐。

固定资料在[data/f34](../../data/f34/)，所有请求体在[search/f34](../../search/f34/)。金额CNY整数分，空格合成名称隔离中文插件差异。正文代码与文件通过data-source逐段核对。

重做与结束：

```bash
python3 labs/f34/lab.py run --out /tmp/f34-reader-round2
python3 labs/f34/lab.py cleanup --out /tmp/f34-reader-cleanup
python3 labs/f34/lab.py down --out /tmp/f34-reader-down
```

cleanup先恢复n2，再删除上表五个准确索引名、两快照、tut-f34-fs和失败仓库名tut-f34-outside；删除快照会销毁本轮备份，只在重做/结束时执行。注销仓库不等于删备份文件。只用Snapshot API操作内容，不手动删卷内文件。guard只额外允许ES自建deprecation/ILM历史两个明确前缀，不清理它们；发现外来索引、仓库、未知/运行中快照即拒绝。down仅移除本课容器/网络，保留三卷。Java原终端Ctrl+C停止。未修改全局persistent/transient设置。

[两轮正式记录](../../review/f34/README.md)每轮65教学REST+4 Java HTTP；guard、身份、清理、等待、浏览器附加另计。预演失败保留在attempts，不冒充完整轮次。当前运行入口不能设置/读回gpt-6.1-sol/max，作者自审不称独立审阅。

只验证同VM小样本、同版本、手动快照；未验证跨机器/异地、仓库损坏/只读访问故障、宿主盘故障、跨版本、SLM/保留策略、系统/功能状态、安全、持续追平、性能或恢复时限。F35安全、F36–F42持续来源更新按课次另学。
