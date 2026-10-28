# F33 真实运行收据

ES9.4.0/Lucene10.4.0，独立两节点19733–19734。n1唯一master候选，n2为data，两个data在同Docker VM/磁盘；无认证，HTTP仅回环。每节点192MiB堆/640MiB限额。运行与构建见[runtime.json](runtime.json)，首次引导移除/身份见[setup](setup/identity.json)。应用JDK25.0.4.1+1、Boot4.0.8、Java/Rest5 Client9.4.8；ES内置JVM26.0.1另列。

| 轮次 | 真实范围 | 收据 |
| --- | --- | --- |
| 首次正式执行 | 3案例；75教学REST=19+28+28，5 Java搜索HTTP，4官方客户端写入 | [summary](run-01/summary.json)、[逐请求/原始响应](run-01/events.jsonl) |
| 点名清理后重做 | 删除本课两个索引，再执行同样全部案例与断言 | [summary](run-02/summary.json)、[逐请求/原始响应](run-02/events.jsonl) |

每轮84次主流程HTTP。75包含实际mapping/settings、全ID/字段、删除、代表查询与Java DSL重放；guard/identity/wait/cleanup另计，见summary。首轮作者观察器另外运行5点×1440/390×浅深=20次真实浏览器→Java请求及20次独立REST重放；浏览器直接请求ES为0。观察器输出与20张截图在run-01，各阶段`*-browser.json`包含输入、响应、DSL重放与错误列表；读者不必安装Playwright。

- c01：旧name=keyword不能直接改text，400；新name=text/whitespace，name.raw=keyword。1主旧版/2主新版，均每主1副、strict/refresh=-1。token由[西湖 湖畔]变[西湖,湖畔]；初次6 created/0 updated/0冲突/无failures，全部_source相同。新目标查询p01/p02，入口仍旧版，Java200/0条。
- c02：复制结束后旧版p01改6500、删除p02、新增p07=1500；REST/Java写响应均v001。两版各6条却ID/字段不同。向非空目标重跑5 updated/1 created、无失败，仍残留p02，目标7条。暂停全部写入者、源专用write block成功/refresh，REST及Java写p09均403且未落盘；只删除未上线v002后完整重建。第三次6 created/0 updated，完整ID为p01/p03/p04/p05/p06/p07，全_source相同，p02两边404；新查询p01/p07。
- c03：错误must_exist前提返回404/aliases_not_found_exception，实际关系不变；四动作同时把read/write切到v002，Java200/2条；暂停业务写入时反向切旧，Java200/0条，旧版write block仍403。再切新后允许Java写p08，仅v002新增，Java200/3条，旧版GET p08=404。没有宣称p08出现后可简单安全回滚。
- 每轮结尾核对同UUID/node ID、两个节点限定读取的完整字段、全部主副分片STARTED、集群persistent/transient设置前后为空。索引级旧版write block保留到最终cleanup；目标无write block。只做受控小样本，不推断随机并发、长任务/失败重试、持续追平、跨机器或性能。

另用读者[手工curl顺序](manual/summary.json)独立执行一次，53个响应对象包括5次Java搜索与4次官方客户端写入；结果同为0/0/2/0/3，未冒充第三轮正式lab.py验收。

`clean package`、classpath和依赖树构建成功，工程无测试源，未称为测试通过。构建日志原始字节无损gzip保留；复用Java资源的源码/包内/真实HTTP一致。单Java进程贯穿两轮，无新增共享Java/前端改动。

[cleanup](cleanup/summary.json)只删除两索引及附着alias/阻断；[down](down/summary.json)仅移除本课容器/网络、保留两卷；[最终状态](final-state.json)另记。没有删除ES自建历史或操作原es-study-secure节点。[HTTP/图/实际视觉](../../../../docs/framework-review/20261028-f33-reindex/README.md)分列。
