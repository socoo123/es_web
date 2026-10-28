# F31 · 两轮真实ES / Java验收

隔离ES 9.4.0 / Lucene 10.4.0；正式初态n1(master/data/ingest)+n2(data)，n3(data)按需加入。19531–19533仅回环HTTP，无认证；同Docker VM和宿主磁盘。每节点192MiB堆/640MiB上限。唯一master n1不停止；不以此拓扑宣称master高可用。

[启动身份](setup/identity.json)、[首轮汇总](round-1/summary.json)与[清理后第二轮](round-2/summary.json)保存原始输出。每轮run先点名删除本课8个索引，再重建6份固定资料，从p01=6000分开始；不沿用上一轮65元。

| 证据 | 每轮实际结果 |
| --- | --- |
| f31-c01 / 12教学REST | n1有主片被same_shard拒绝副本，n2及新增n3被filter拒绝；3节点仍yellow；清require后4份STARTED覆盖3节点，0号每份2篇/1号每份4篇，完整_source及搜索p01/p02一致 |
| f31-c02 / 23教学REST | 检查实际free；人为low=10tb/high=1gb/flood=512mb，新需2份副本被disk_threshold拒绝，旧4份可读；恢复阈值后6份启动再回4份；排空/停n2、恢复n2、排空/停n3，实际零分片后才停，最终原n1+n2与空集群临时设置 |
| f31-c03 / 46教学REST | 非动态主片数400；可写源split为500 read-only；写阻塞后PUT为403；split到3为400 factor、到6为500 routing shards；合法2→4；分散4片shrink为500 same node，集中后4→2；预建3主完整mapping再reindex，created/total=6、零conflict/failure；4索引字段/ID/mapping/代表查询核对，最终仅源p01=6500、3目标仍6000 |
| Java接口 / 7次另计 | 复用原F07服务，西湖/HZ/预算20000分/30.25,120.15/3km；按ID固定p01/p02，前6点60元/0元，最后65元/0元；返回DSL的独立REST重放包含于81教学REST |

每轮81教学REST=12+23+46，Java接口7次另计。启动、identity、guard、recover、wait、cleanup与命令分别按`events.jsonl`的kind分类；首轮轮询32次，第二轮30次。第二轮初始化恢复读取旧split4并解除临时项，故recovery HTTP为7次，首轮6次。异步等待次数不是教学请求数或性能指标。

首轮另以作者观察钩子在7点×1440/390×浅深共28次真实浏览器→Java调用与28次独立REST重放，见各`*-browser.json`与`screenshots/`。展示输入、原文、DSL、卡片、票价核对，浏览器直连ES=0；这些附加调用没有混入81或7。第二轮不重复浏览器钩子，完整Java/REST仍重跑。

[运行时](runtime.json)、[clean package](build.log.gz)、[依赖树](dependency-tree.log.gz)、[服务日志](application.log)分列：应用Temurin JDK25.0.4.1+1、Boot4.0.8、官方Java/Rest5 Client9.4.8；ES内置JVM26.0.1。无测试源，不将`No tests to run`称测试通过。两份Maven日志按[原始字节哈希](log-archives.json)无损gzip保留，包含Maven原有尾随空格，未改写输出。共享Java/前端源码未改；打包静态资源与源文件、真实HTTP响应逐字节核对。

[失败尝试](attempts/drain-await/events.jsonl)不算正式首轮：作者脚本错误要求PEER.source必须来自被排空节点，且恢复仅等green，先后断言失败。实际副本可从另一节点的primary恢复；规划也可能在green之后继续。修正为检查实际全索引路由归零、STARTED、恢复DONE与完整数据后，[恢复](attempts/drain-recovery/summary.json)成功，再清理执行两轮正式实验。失败记录、截图与原错误保留，未将中断算通过。

末轮临时require/total_shards_per_node/blocks.write/exclude与磁盘水位已恢复；最终配置、原身份与布局见每轮`settings-before/after.json`、`identity-final.json`、`final-layout.json`。最终点名清理/容器与网络移除及三卷保留另记在[工作区状态](../../../../docs/framework-review/20261028-f31-allocation/workspace-state.json)。原安全节点持续只读监测，未做其业务字段对账。

未验证：真实磁盘耗尽/high迁出/flood写封锁、物理磁盘扩容、文件系统硬链接方式、大文档数上限、跨机器迁移、持续并发、性能、恢复时限或在线切换。源65元/目标60元特意证明目标不持续跟随；alias与受控重建后续按F32/F33学习。
