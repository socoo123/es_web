# F32 · 模板与读写 alias

[教程](../../../../framework/f32.html)先解释创建规则与访问入口。本课仅实现F32；两份独立固定快照用于观察目标，不执行F33的数据迁移/追平/升级验收。管理操作用隔离REST/配置，搜索复用F07的Java与本机观察窗，写入用独立官方客户端，不新增Controller或前端。

ES9.4.0/Lucene10.4.0；Boot4.0.8、应用JDK25、Java/Rest5 Client9.4.8。ES内置JVM另记。先将JAVA_HOME/PATH指向完整JDK25，在仓库根目录：

```bash
cd projects/travel-search
python3 labs/f32/lab.py start --out /tmp/f32-reader-setup
```

另一终端：

```bash
cd projects/travel-search/backend
./mvnw -B -ntp clean package dependency:build-classpath -Dmdep.outputFile=target/f32-classpath.txt
ES_URL=http://127.0.0.1:19632 ES_INDEX=tut-f32-attractions-read APP_PORT=18082 \
  java -jar target/travel-search-0.7.0.jar
```

回到项目目录：

```bash
export APP_URL=http://127.0.0.1:18082
python3 labs/f32/lab.py run --out /tmp/f32-reader-round1
```

每个`--out`必须是新目录。实验建好read alias之前搜索会失败。start只在两个基础卷均不存在时bootstrap，成团后移除名单并核对UUID/node ID；完整旧卷直接启动，部分卷缺失则拒绝重新引导。卷与容器必须带本课标签。

| 资源 | 独立配置 |
| --- | --- |
| 集群/网络/卷 | es-framework-f32，travel-f32-lab；两个持久卷保留 |
| n1 / 19632 | master/data/ingest，本课唯一master候选，不停止 |
| n2 / 19633 | data，主副各一份时可核对节点限定读取 |
| HTTP | 仅127.0.0.1，无认证；transport仅独立Docker网络 |
| 容器 | 每节点192MiB堆/640MiB限额；两进程同Docker VM/磁盘，非跨机器部署 |
| Java | 18082，ES_INDEX始终为tut-f32-attractions-read；一个进程完成全部观察点 |

启动前检查Docker内存及原有服务。此拓扑不提供master故障容忍。不要把本课管理脚本指向其他集群。

| 案例 | 输入/操作 | 真实判断证据 |
| --- | --- | --- |
| f32-c01-template-inheritance | 模板前建v001；两组件与priority100/version32模板；priority200/version1临时模板及同优先级冲突；模拟/修复；创建v002；组件改版后建v003；显式设置建v004 | 低优先级字段不合入；同优先级400；simulate不创建；v001仍1主/-1/无扩展字段，v002仍2主/-1/仅source_batch，v003为2主/1s/含source_note，v004覆盖3主0副/-1；完整mapping与settings |
| f32-c02-read-write-targets | 两份6篇固定快照，初始read/write挂v001；REST/Java写p07；临时隐式单目标alias；read/write加入v002 | p07只在v001，Java重写updated不加条数；write搜索也读两版，read出现4条/重复p01-p02；移除read-v002后回两条60元/0元 |
| f32-c03-errors-and-repair | require_alias的缺失/物理目标、显式false、两版均false、两版均true；修正v002唯一true后写p08；缺失read、空v003、修到v002 | 缺失/物理为404，false/无writer为400，两个true配置500且关系未变；p08只在v002；Java502→200/0条→200/65元与0元；p09均不存在；完整ID/字段与两入口关系 |

每轮85教学REST（33+23+29）、6次Java搜索接口、6次独立官方客户端写入，合计97次主流程业务/管理HTTP。85包含Java返回DSL的REST重放与重复完整字段核对。guard、身份、等待、清理、Compose和浏览器附加HTTP另计，见events/summary。客户端每次调用只发送一个写请求，成功和预期拒绝均保留响应；它不是游客写入接口。

在[本机观察窗](http://127.0.0.1:18082/)输入西湖/HZ/20000分/30.25,120.15/3km。正文手工流程可在6个观察点暂停；完整脚本迅速经过各点，作者用可选observer记录真实浏览器交互，读者无需安装Playwright。浏览器→Java→ES，浏览器不直接请求ES。DSL只含请求体，应结合配置、GET _alias与REST命中_index核对目标。

固定资料：[旧版JSON](../../data/f32/v001.json)、[旧版NDJSON](../../data/f32/v001.ndjson)、[新版JSON](../../data/f32/v002.json)、[新版NDJSON](../../data/f32/v002.ndjson)、[p07](../../data/f32/p07.json)、[p08](../../data/f32/p08.json)、[p09](../../data/f32/p09.json)。新版仅p01票价6000→6500分；p07/p08名称含西溪，不命中西湖。v003/v004保持空，用作配置/错误目标对照。全部金额CNY整数分。

手工REST请求与脚本二选一，不在脚本中途混入修改。独立Java对照（先完成对应alias配置）：

```bash
bash labs/f32/java.sh tut-f32-attractions-write p08 data/f32/p08.json
bash labs/f32/java.sh tut-f32-missing-write p09 data/f32/p09.json
```

清理后重做和退出：

```bash
python3 labs/f32/lab.py run --out /tmp/f32-reader-round2
python3 labs/f32/lab.py cleanup --out /tmp/f32-reader-cleanup
python3 labs/f32/lab.py down --out /tmp/f32-reader-down
```

每轮run先点名删除本课资源再从头开始，中断时保留原始失败后用新目录重跑。若出现外来业务资源/部分卷，先恢复隔离前提，不能用通配符强删。

清理仅针对以下完整名字，顺序为索引→index template→component template：

- 索引：`tut-f32-attractions-v001`、`tut-f32-attractions-v002`、`tut-f32-attractions-v003`、`tut-f32-attractions-v004`、`tut-f32-missing-write`（防误建）。附着的read/write/implicit alias随索引删除。
- Index templates：`tut-f32-attractions`、`tut-f32-shadow`、`tut-f32-equal`。
- Component templates：`tut-f32-settings`、`tut-f32-fields`。

guard只额外容许ES自动创建的`.ds-.logs-elasticsearch.deprecation-default-`、`.ds-ilm-history-7-`两个明确系统前缀，不清理它们；不把这些历史计入景点文档。down移除本课容器/网络，保留两卷；Java在原终端Ctrl+C停止。

read/write是命名约定，read显式false不代替权限。require_alias防止误写普通索引，不保证alias指向正确。未验证持续并发、升级一致性、过滤alias/routing、ILM/data stream、安全、跨机器或性能。正式两轮[原始记录](../../review/f32/README.md)与[图解/HTTP/实际视觉记录](../../../../docs/framework-review/20261028-f32-template-alias/README.md)分列；作者失败尝试单列，不计入通过。
