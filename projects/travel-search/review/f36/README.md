# F36 实际执行记录

2026-10-29，在本机独立es-framework-f36执行；只处理F36。3案例，每轮22教学REST＋4Java搜索HTTP＋3Java Bulk调用，身份/guard/清理另计。run-01和点名cleanup-01后run-02均实际通过，全部来源与ES完整字段、ID、价格、标签、城市展示名、删除状态断言在lab.py。

- [第一轮](run-01/summary.json)、[第二轮](run-02/summary.json)：每轮四个稳定点×1440/390×浅深=16次真实浏览器→Java，另16次DSL独立REST重放；浏览器直连ES为0。截图在各轮screenshots，实际审阅范围在[阅读记录](../../../../docs/framework-review/20261029-f36-projection/README.md)。
- c01：三表→p01/p02，初次REST Bulk两项201，重复Java导入两项200/updated且仍两份；完整字段相同。
- c02：city改名、p01标签删除，attraction行未动；DB新而ES旧，重投影后两份城市名更新、p01移除游船标签。
- c03：真实REPEATABLE READ会话A固定视图，B在A未提交时事务改p01=6500、p02=closed、新增p03=3000；A两次导出相同，旧快照导入漏掉三种变化。人工已知三个键，暂停其他写入，Java index/delete/index；GET先新、SEARCH仍旧；refresh后完整字段对齐，p01/6500、p03/3000。前后count均2。

原始请求/响应见每轮http.jsonl，SQL与输出见sql.jsonl，Java逐条结果见*-java-import.txt；快照两会话证据见03-snapshot-session.json，边界见03-stage-evidence.json。SQL投影文件与对应Bulk体保留。没有实现/执行WAL/binlog、Kafka、自动消费、offset、失败重放、乱序保护、持续更新追平或物理删除事件捕获，不称CDC验收通过。

[独立手工路径](manual/summary.json)实际执行发布的requests.sh、psql snapshot-begin/end、compose cp与cmp、curl和Java，另验证第二次delete p02为无error的404/not_found。随后[点名清理](cleanup-final/summary.json)、[最终digest配置原卷重启](final-config-restart/summary.json)保持同UUID，再down；[停止核对](shutdown.json)确认本课容器/Java停止、20036/18086关闭、两数据卷和本机密码文件保留，原有es-study-secure身份与启动时间不变且healthy。

固定Boot4.0.8 / Temurin25.0.4.1+1 / Java和Rest5 Client9.4.8 / Maven3.9.11；ES9.4.0/Lucene10.4.0与bundled JVM26.0.1分列。PG17.5-bookworm锁digest；数据库无宿主机端口，ES仅回环20036，Java18086。单Docker VM、1主0副、ES关闭认证，仅验证本机合成数据功能。构建/运行身份/最终停止状态分别记录；本课不修改共享业务后端或新增前端。

当前根入口无法设置/读回最新gpt-6.1-sol/max，作者自审，没有独立内容审阅代理。
