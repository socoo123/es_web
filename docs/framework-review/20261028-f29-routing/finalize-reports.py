#!/usr/bin/env python3
"""Materialize final F29 summaries only from passed independent receipts."""
import datetime,json,pathlib
R=pathlib.Path(__file__).resolve().parents[3];D=pathlib.Path(__file__).resolve().parent;P=R/'projects/travel-search'
review=json.loads((D/'content-review.json').read_text());http=json.loads((D/'http-review.json').read_text());shell=json.loads((D/'shell-review.json').read_text());runtime=json.loads((P/'review/f29/runtime.json').read_text())
assert all(x['passed'] for x in [review,http,shell,runtime])
assert '## 2026-10-28 · F29' not in (R/'STATUS.md').read_text(), 'F29 report already finalized; review existing receipts before regenerating'
a=review['rounds'][0];b=review['rounds'][1];assert a['actual_default_shards']==b['actual_default_shards']
byshard={n:sorted(k for k,v in a['actual_default_shards'].items() if v==n) for n in [0,1]}
(P/'review/f29/README.md').write_text(f'''# F29 · 主副分片、routing与读写路径两轮实测

[正文](../../../../framework/f29.html) / [本机入口](../../labs/f29/README.md) / [构建与运行](runtime.json)。仅本课三节点、两个索引；ES9.4.0/Lucene10.4.0，同Docker VM，2主每主1副，strict/whitespace/refresh=-1。

- [首次身份](setup/identity.json)：首启后移除引导名单、UUID与三个node ID保持；配置与JVM分列。[启动收据](setup/summary.json)的等待不混入教学HTTP。
- [第一轮](round-1/default/summary.json)和[第二轮](round-2/default/summary.json)均先点名清理索引，再执行default/routing/reads。每轮62教学HTTP=21+28+13，其中1次到既有Java接口；Java内部ES请求另计。各阶段events.jsonl逐条保存URL/body/status/response，轮次输出不覆盖。
- 默认_id真实分布：组0={byshard[0]}，组1={byshard[1]}。按分片搜索逐份_source比对，再用_search_shards交叉核对；主片docs合计6，含副本12，三个入口与Java均p01/p02。
- HZ→0、FZ→0、SH→1；r01/HZ正确200、跨SH 404、缺值400 routing_missing_exception、同片错FZ仍200且存储_routing=HZ。跨片错误update404/delete404，正确update7000分后可读；故意跨片同_id创建导致两份r01，再点名删SH拷贝、恢复HZ价格6000分。
- 全索引match_all6份/_shards.total2；HZ范围r01/r02/r04/r05/total1，不能替代城市filter。完整query无routing与HZ均r01/r02、SH则0命中；HZ,SH范围合并为2组/6份。
- 两轮分别通过真实_only_nodes/profile把执行节点/shard关联到当时primary=true/false，主副读取均r01/r02、_shards.total1/failed0；不声称正常默认请求必须轮流到主副。[第一轮拷贝证据](round-1/reads/reads-proof.json)、[第二轮拷贝证据](round-2/reads/reads-proof.json)。
- 独立RoutingLab.java每轮13次SDK调用：专用probe完整CRUD、3搜索、跨片/同片/缺值GET；[第一轮](round-1/java/java-proof.json)与[第二轮](round-2/java/java-proof.json)。verify-java每轮5附加HTTP=3搜索独立重放+refresh+全6份_source/routing核对；无probe或重复残留。不抓包底层客户端重试，所以不把SDK调用数称网络报文数。
- Java构建clean package/classpath/依赖树实跑；无测试源，不将No tests to run当测试通过。原临时JDK缺jvm.cfg的失败和同版本官方归档SHA校验恢复分别保留，未更改仓库应用依赖或共享前端。
- [真实观察窗](../../../../docs/framework-review/20261028-f29-routing/shell-review.json)：8次Java请求+8次作者REST重放，双主题/1440与390/200与50元；默认索引p01/p02与p02，卡片/原文/DSL一致，浏览器直连ES=0。观察窗没有routing输入，自定义routing由独立Java/REST检验。
- [保护](guards/summary.json)：reset缺显式删除标记，变更前拒绝。[清理](../../../../docs/framework-review/20261028-f29-routing/workspace-state.json)核对全部最终资料与原身份后点名删两个索引、正常停止自启Java、移除本课容器/网络、保留三卷；原安全节点自本课启动后采样至清理的ID/Pid/StartedAt/healthy均相同。

探索与正式轮次分开：attempts保留选路由、routing/reads探查和旧JDK首次失败。没有运行选举/主分片提升/副本全丢失、跨机器、性能/热点基准、扩缩容或权限实验；这些不是本课已验收成果。
''')
(D/'README.md').write_text(f'''# F29 · 内容、图解、HTTP与视觉验收

仅实施F29，必要当前摘要/目录与F28下一课链接同步；F30未实施。正文约{review['chinese_characters_without_code']}汉字（不含代码）、七段式、3案例/62教学HTTP、13次独立Java SDK调用另计；2静态D2、8折叠练习、4陷阱、0机制播放器。

- [作者自审](content-review.json)：概念、因果、版本分支、错值反例、复制/读取、请求/Java与清理一致；无独立代理。[运行入口](reasoning.json)不能设置或读回用户最新gpt-6.1-sol/max，不以提示词冒充实际配置。
- [源码](sources.json)：四份v9.4.0官方原文件与本地字节相等；IndexRouting创建版本与Unpartitioned、OperationRouting目标组/偏好、TransportGetAction.shards、ReplicationOperation.execute/handlePrimaryResult/performOnReplicas按目标方法核对。
- [D2生成](../../../framework/diagrams/f29/generation.json)：官方v0.9.0/dagre/主题4与201，2源4SVG的fmt/validate/导出与SHA通过，改源后重生成。搜索图把两条独立请求放在同一对照卡片，避免误读为先全后缩小。
- [HTTP阅读](http-review.json)：1920/1440/1024/768/390/320×浅深12组，阅读列最大880px、边界差≤1px；29锚点、13折叠、24真实剪贴板、主题/图同步/重载/已读隔离、file双主题/reduced-motion/键盘通过，零整页横溢。独立图4桌面宽度×双主题×2图共16组，必要目录/F28共12组；无JS、HTTP或请求失败，Pages业务调用=0。
- [视觉](visual-review.json)：54张阅读/图截图经5组总览实际查看，部分最终原图单开；[额外Java代码截图](code-screens.json)8张，长行局部滚动；代码/观察窗/最终正文另20张经2组总览查看，其中最终正文4组针对性复验见[收据](final-smoke.json)。实际观测与范围写明，未声称逐像素或全部代码逐字视觉审阅。
- [真实观察窗](shell-review.json)：独立8次Java调用+8次作者REST重放，截图与source/packaged/HTTP资源字节一致性分别验证。展示壳只连接默认索引，无前端/Controller改动。
- [真实两轮ES与Java](../../../projects/travel-search/review/f29/README.md)：每轮62教学HTTP+13 SDK调用+5附加验证HTTP；启动、等待、清理与浏览器独立计数。ID/source/routing/错误与恢复、当前主副实际读取分别核对。
- [最终清理](workspace-state.json)与[检查](checks.json)记录本课资源边界与必要站点/片段/JSON/Python/Bash/Compose检查；提交后远端SHA/Pages验证在工作树外收据及交付中，不提前冒充发布成功。

单Docker VM、固定小资料；跨主机容灾、故障恢复、性能、热点、权限与后续课程均未测。未修改历史章节内容，只将必要前课导航接到F29。
''')
status=R/'STATUS.md';s=status.read_text();marker='\n## 2026-10-27 · F28';head,tail=s.split(marker,1)
head=head.replace('F01–F28可阅读','F01–F29可阅读').replace('F29–F45待实施','F29主副分片/默认与自定义routing/跨片同片错误与主副读取通过，F30–F45待实施')
head=head.replace('| F29–F45 正文与实验 | 待实施；下一课F29主副分片与routing，其后按阶段推进 |','| F29 · 主副分片、routing与读写路径 | ✅ 正文/2D2/HTTP与实际视觉/复用Java构建与观察窗/独立Java路由/真实三节点两轮62教学HTTP；跨片/同片/缺值/重复与恢复、主副实际读取通过；单VM/故障/性能未测 |\n| F30–F45 正文与实验 | 待实施；下一课F30选举与数据节点失效，其后按阶段推进 |')
head=head.replace('F29–F35的routing/故障、分配','F29真实默认/自定义routing、跨片与同片错误/重复恢复及主副分别读取通过；F30–F35的故障、分配')
head=head.replace('F01–F28共56幅静态D2、浅深112 SVG；F28角色拓扑与持久首启图','F01–F29共58幅静态D2、浅深116 SVG；F29写入路径与搜索范围图')
head=head.replace('F25/F26/F27/F28当前根入口','F25/F26/F27/F28/F29当前根入口')
head=head.replace('均由读者本机启动 |','F29复用F07接口/观察窗连接19330/tut-f29-default，三节点19329–19331；自定义路由由独立Java lab/REST核对，无新增Controller/前端；均由读者本机启动 |')
section=f'''

## 2026-10-28 · F29 主副分片、routing与读写路径两轮通过

- 仅实施F29及必要F28下一课导航/目录/当前摘要，逐课提示词转F30；没有实施F30。[正文](framework/f29.html)约{review['chinese_characters_without_code']}汉字（不含代码）、七段式/880px/双主题/独立已读；3案例/62教学HTTP=21+28+13，另13次独立Java SDK调用、5附加验证HTTP，2静态D2/8折叠练习/4陷阱/0播放器。[实验入口](projects/travel-search/labs/f29/README.md)、[作者自审](docs/framework-review/20261028-f29-routing/content-review.json)。
- 独立es-framework-f29/19329–19331/三份持久卷；3master候选、2data，角色沿F28形状但资源不复用。ES9.4.0/Lucene10.4.0，2主每主1副/strict/whitespace/refresh=-1。三进程同Docker VM约3.81GiB/2CPU，各256MiB堆/768MiB限制，无认证且仅回环HTTP；首启形成后移除引导名单并核原UUID与node ID。[环境身份](projects/travel-search/review/f29/setup/identity.json)。
- [正式两轮](projects/travel-search/review/f29/README.md)均先点名清两个索引再执行；默认6份景点实际shard0={byshard[0]}、shard1={byshard[1]}，分片命中全_source与_search_shards交叉核对，4行STARTED/每组p-r不同节点/主docs合计6，三个入口与既有Java均p01/p02。默认索引与路由索引全部字段、mapping/settings/创建版本分别保存，不用green或总数替代内容。
- 自定义路由HZ→0、FZ→0、SH→1，两轮重核；正确r01/HZ 200、跨SH 404、漏传400、同片错FZ仍200且存储_routing为HZ。错update/delete404，正确update实时GET7000分；相同_id跨片重写会创建第二份r01，ids查询比两份_source与routing后点名删SH，恢复HZ价格6000分。required只防漏传；新旧公式按索引创建版本区分，未分区/无routing_path/无resize限定写清。
- 全索引6份/2目标组，HZ范围r01/r02/r04/r05/1组仍含他城；完整query全索引与HZ都r01/r02，改SH为0命中，HZ,SH合并2组6份。两个data节点分别_only_nodes+profile，将真实执行节点/shard关联到当时primary=true/false，两者均r01/r02、_shards.total1/failed0；候选列表不当执行证据，不宣称默认轮流读主副。
- [Java构建/运行](projects/travel-search/review/f29/runtime.json)锁Boot4.0.8/Temurin25.0.4.1+1/Java与Rest5 Client9.4.8/Maven3.9.11；clean package/classpath/依赖树通过，无测试源不称测试通过，ES内置JVM26.0.1分列。原临时JDK缺jvm.cfg首次失败保留，官方同版本归档SHA校验恢复。共享Java/前端未改；独立RoutingLab复用F07完整query builder，13 SDK调用覆盖probe CRUD/三范围搜索/错误值与漏值，3 REST重放及最终6份_source/routing核对另计；底层重试未抓包。
- [观察窗](docs/framework-review/20261028-f29-routing/shell-review.json)1440/390×浅深×200/50元=8次Java调用+8独立REST重放，卡片p01/p02=60元/0元、50元只p02，输入/DSL/原文/卡片一致，浏览器直连ES=0；既有三静态资源源码/包内/HTTP字节相同。观察窗无routing输入，自定义路由由独立Java/REST观察，不虚称新界面。
- [图/HTTP/视觉](docs/framework-review/20261028-f29-routing/README.md)：D2v0.9.0/dagre/4与201、2源4SVG的fmt/validate/生成/哈希通过，四份固定v9.4.0官方源码与本地字节相同。12阅读组/16独立图组/12必要关联页，29锚点/13折叠/24真实剪贴板、主题与图同步/重载/已读隔离/file双主题/reduced-motion/键盘通过，最大880px/边界差≤1px/零整页溢出；54阅读PNG经5组总览实际查看，额外8代码与8观察窗截图，部分原图单开，非逐像素或代码全文逐字视觉审阅。最终阅读无JS/HTTP/请求失败，Pages业务调用=0。
- 作者稿按真实FZ同片改用SH跨片，图把全索引→限定的顺序画法改为两条独立请求对照；完整路由mapping/重复PUT与Java片段边界补全。F29为新课，没有已发布旧正文勘误；这些是本轮作者稿修正，不回填其他课。[reset保护](projects/travel-search/review/f29/guards/summary.json)缺标记时在HTTP/Docker变更前拒绝。[最终清理](docs/framework-review/20261028-f29-routing/workspace-state.json)核原身份/全部字段后点名删两个索引、Java正常SIGTERM/18081关闭、本课容器网络移除，三卷保留；原安全节点自本课启动后采样至清理ID/Pid/StartedAt/healthy不变。单VM/固定资料，故障选举/提升/恢复、跨机器、性能/热点/扩缩容/TLS权限未测。
- [推理入口](docs/framework-review/20261028-f29-routing/reasoning.json)不能设置或读回最新gpt-6.1-sol/max；作者实施与自审，没有独立代理，不声称已启用。[最终检查](docs/framework-review/20261028-f29-routing/checks.json)分列站点/片段/Python/Bash/JSON/Compose/图哈希；按持续授权提交推送origin/main，远端SHA与Pages在提交后验证，发布收据工作树外保存，不提前标通过。
'''
assert '## 2026-10-28 · F29' not in s
status.write_text(head+section+marker+tail)
print('F29 final summaries and STATUS updated from passed receipts')
