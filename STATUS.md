# STATUS.md — 进度唯一真相

更新规则:做完任何一批工作就更新本文件 + 跑 `node tools/check.mjs`。

## 框架学习篇与旅游搜索实验

当前路线见 [FRAMEWORK_PLAN.md](FRAMEWORK_PLAN.md)，阅读入口见 [框架篇目录](framework/index.html)。八阶段 45 课从 ES 用途与旅游搜索问题讲起，F12/F22/F45 独立结业；只按指定课次推进。旧规划与旧首课验收摘要集中到 [历史记录](FRAMEWORK_HISTORY.md)，不作为当前待办。源码篇 ch01–ch30 编号与验收记录不变。

| 项目 | 当前状态 |
| --- | --- |
| 八阶段、45 课目录与教学路线 | ✅ 当前规划、覆盖清单与可见目录一致；F01–F28可阅读；F04/F05/F06真实ES验收受阻，F07 Java实连/展示壳、F08多字段/安全高亮、F09聚合/多维计数、F10三模式排序、F11稳定分页/PIT、F12更新/可见性/冲突与基础结业、F13分析链与中文召回、F14中文分词方案比较/三插件安装实连、F15本地词典/历史词项/受控重建与新增误匹配、F16别名/同义词图/繁简/查询集重载、F17提示/显式拼音/整名容错/下架、F18 BM25/解释评分/过滤与语料变化、F19名称/短语/多字段组合/奖励与should门槛、F20点评平滑/热度/压缩/封顶与rank_feature候选边界、F21距离/时效衰减/两层合成/硬半径与显式sort、F22固定查询集/完整标注/调整与留出/Recall与nDCG及坏例回归通过，F23酒店/房型/offer文档边界与真实更新范围通过，F24同条目条件/inner_hits与nested排序通过，F25多晚库存/精确总价与固定逐晚表核对通过，F26酒店去重/计数/最低价范围与Top K反例通过，F27两层酒店/房型次序、偏好与硬条件/缺价旧库存及完整范围通过，F28三节点身份/角色/主副布局、持久首启/重启与错误独立集群恢复通过，F29–F45待实施 |
| F01 · ES 用途、职责与全程导学 | ✅ 正文、独立内容审阅与 HTTP 阅读通过；1 个导学情境、1 份小 JSON、5 道理解题；0 条执行请求 |
| F02 · 数据到搜索结果的概念推演 | ✅ 正文、人工模型核对与 HTTP 阅读通过；2 个概念案例、6 道推演题、2 幅静态 D2；0 条执行请求 |
| F03 · 本机运行与真实首搜 | ✅ 正文、图解、HTTP 阅读与真实 ES 三案例两轮通过；12 条主流程 HTTP 请求；实际限制见本轮记录 |
| F04 · 字段设计与 Bulk | 正文/固定语料/三案例脚本/两幅 D2 已交付；HTTP阅读/图解/静态检查通过，真实 ES 两轮受云环境启动阻塞，未标通过 |
| F05 · 关键词、精确值与短语 | 正文/固定语料/三案例脚本/两幅 D2 已交付；HTTP阅读/图解/静态检查通过，真实 ES 两轮受云环境启动阻塞，未标通过 |
| F06 · bool 与组合筛选 | 正文/12份固定资料/三案例脚本/两幅D2已交付；HTTP阅读/视觉/静态检查通过，真实ES两轮受云环境启动阻塞，未标通过 |
| F07 · Java接口与本机展示壳 | ✅ 正文、两幅D2、HTTP阅读、Boot4/JDK25构建/实连、REST↔Java两轮与真实展示壳通过；未测分片部分失败/执行超时 |
| F08 · 多字段与高亮 | ✅ 正文、2幅D2、HTTP阅读、Boot4/JDK25构建、REST↔Java两轮与真实高亮展示壳通过；长字段成本/评分质量未测 |
| F09 · 聚合与筛选计数 | ✅ 正文、2幅D2、HTTP/视觉、Boot4/JDK25构建、REST↔Java两轮、真实展示壳与同节点双分片候选误差实测通过；高基数成本未测 |
| F10 · 显式排序 | ✅ 正文、2幅D2、HTTP/视觉、Boot4/JDK25构建、REST↔Java两轮、真实排序展示壳与502/503恢复通过；并发视图/分页/性能未测 |
| F11 · 稳定分页与PIT | ✅ 正文、2幅D2、HTTP/视觉、Boot4/JDK25构建、REST↔Java两轮、真实分页展示壳、关闭/过期与410/502/503恢复通过；随机并发/多节点/性能未测 |
| F12 · 更新、可见性与基础结业 | ✅ 正文、2幅D2、HTTP/视觉、Boot4/JDK25构建、CRUD/冲突/独立新样本REST↔Java两轮、真实观察窗与409/502/503恢复通过；随机并发/多节点/性能未测 |
| F13 · 分析链与中文召回 | ✅ 正文、2幅D2、HTTP/视觉、Boot4/JDK25构建、token/召回REST↔Java两轮与真实观察窗/400/502/503恢复通过；插件与中文质量评估未测 |
| F14 · 中文分词方案比较 | ✅ 正文、2幅D2、HTTP/视觉、Boot4/JDK25构建、standard基线→SmartCN/ICU/IK9.4.0安装与五方案REST↔Java两轮、真实观察窗/400/502/503恢复通过；词典/整体质量/性能未测 |
| F15 · 专有词、词典与重建 | ✅ 正文、2幅D2、HTTP/视觉、Boot4/JDK25构建、本地IK词典文件→重启→新旧词项→重建REST↔Java两轮与真实观察窗/400/502/503恢复通过；远程/多节点/整体质量/性能未测 |
| F16 · 别名、同义词与繁简 | ✅ 正文、2幅D2、HTTP/视觉、Boot4/JDK25构建、别名/词图/短语/繁简/管理集重载REST↔Java两轮与真实观察窗/400/502/503恢复通过；全站质量/多节点/性能未测 |
| F17 · 提示、拼音与容错 | ✅ 正文、2幅D2、HTTP/视觉、Boot4/JDK25构建、completion/search_as_you_type/显式拼音/整名fuzzy与下架REST↔Java两轮、真实观察窗/400/502/503恢复通过；整体质量/多节点/性能/自动转写未测 |
| F18 · BM25与解释评分 | ✅ 正文、2幅D2、HTTP/视觉、Boot4/JDK25构建、词频/长度/稀有词/must与filter/不命中语料追加REST↔Java两轮、真实解释观察窗/400/502/503恢复通过；整体质量/性能/多主分片与DFS未测 |
| F19 · 名称、短语与多字段权重 | ✅ 正文、2幅D2、HTTP/视觉、Boot4/JDK25构建、精确/短语/散词/加和/dis_max/奖励/should门槛REST↔Java两轮、真实观察窗/400/502/503恢复通过；全站质量/多分片/性能未测 |
| F20 · 点评质量、热度与function_score | ✅ 正文、2幅D2、HTTP/视觉、Boot4/JDK25构建、固定点评平滑/原热度/压缩/封顶/rank_feature的REST↔Java两轮、真实观察窗/400/502/503与恢复通过；全站质量/性能/多节点未测 |
| F21 · 距离、时效与显式排序 | ✅ 正文、2幅D2、HTTP/视觉、Boot4/JDK25构建、gauss/exp/缺值/两层合成/三种排序的REST↔Java两轮、真实观察窗/400/502/503恢复通过；全站质量/性能/多节点未测 |
| F22 · 查询集、标注与搜索质量评估 | ✅ 正文、2幅D2、HTTP/实际视觉、Boot4/JDK25构建、24份×8查询完整标注/两指标/调整与留出REST↔Java两轮、真实观察窗400/502/503及恢复通过；不代表全站质量/显著性，单人虚构标注/性能/多节点限制单列 |
| F23 · 酒店、房型与offer文档边界 | ✅ 正文/2 D2/HTTP与实际视觉/Boot4-JDK25构建/四投影两轮REST↔Java/真实观察窗400-502-503恢复通过；单晚合成快照，性能/多节点/实时供价未测 |
| F24 · 同房型条件、inner_hits与nested排序 | ✅ 正文/2 D2/HTTP与实际视觉/Boot4-JDK25构建/两轮46教学HTTP与REST↔Java/真实观察窗400-502-503恢复通过；固定单晚、性能/多节点/多晚实时供价未测 |
| F25 · 多晚库存与精确价表核对 | ✅ 正文/2D2/HTTP与实际视觉/Boot4-JDK25构建/两轮21教学＋29附加HTTP/真实观察窗400-502-503恢复通过；固定逐晚快照，非实时可订，性能/多节点/订单未测 |
| F26 · collapse、酒店去重与最低价范围 | ✅ 正文/2D2/HTTP与实际视觉/Boot4-JDK25构建/两轮24教学＋29附加HTTP/真实观察窗400-502-503恢复通过；固定快照，完整集合上限/Top K边界明确，性能/多节点/实时供价未测 |
| F27 · 酒店与房型分层排序 | ✅ 正文/2D2/HTTP与实际视觉/Boot4-JDK25构建/两轮27教学＋51附加HTTP/真实观察窗400-502-503恢复通过；固定快照，完整候选和房型范围明确，性能/多节点/实时供价未测 |
| F28 · 三节点拓扑、发现与持久首启 | ✅ 正文/2D2/HTTP与实际视觉/复用Java构建/真实三节点两轮72教学HTTP/重启与错误集群恢复通过；同Docker VM，跨机器容灾/性能/选举故障未测 |
| F29–F45 正文与实验 | 待实施；下一课F29主副分片与routing，其后按阶段推进 |
| 逐课教学问题与案例覆盖 | ✅ [覆盖清单](FRAMEWORK_CASES.md)按问题设计对照与判断证据；验收按课次实际记录 |
| 历史启动实验 | [存档正文](framework/f01-startup-legacy.html)与原工程/三案例两轮实测记录保留；F03 已使用新资源独立两轮验收，旧文件与记录保留 |
| 本机搜索展示壳与 Java | ✅ F07：Boot4.0.8 / JDK25.0.4.1+1 / Java与Rest5 Client9.4.8实际构建、实连；本机同源展示壳；F08新增多字段/安全高亮、F09新增多维计数、F10新增三模式排序、F11新增PIT分页、F12新增GET/带版本修改/可见性独立观察页，F13新增分析链/召回、F14新增分词方案比较、F15新增词典/历史词项、F16新增别名/查询词图、F17新增提示/拼音/整名容错独立观察页，F18新增BM25/完整query解释、F19新增名称/短语/多字段调权、F20新增质量/热度/数值评分、F21新增距离/时效/硬半径与三种排序独立观察页，F22新增固定查询集/人工等级/两个指标与逐查询次序独立观察页，F23新增酒店/房型/独立报价文档边界观察页，F24新增同房型资格/inner_hits/嵌套排序过滤观察页，F25新增住宿晚/库存/最短入住/精确总价与拒绝原因观察页，F26新增报价/酒店范围、去重/计数、入住最低价与Top K对照观察页，F27新增酒店三模式/酒店内总价与偏好/硬条件和候选范围观察页；F14用19214、F15用19215、F16用19216、F17用19217、F18用19218、F19用19219、F20用19220、F21用19221、F22用19222、F23用19223、F24用19224、F25用19225、F26用19226、F27用19227隔离节点；F28复用F07接口/观察窗，ES_INDEX切本课、ES_URL指19229，三节点19228–19230，无新增Controller或前端；均由读者本机启动 |
| 集群与索引运行 | ✅ F28真实三进程：三入口同UUID/3候选/2data/1ingest角色、2P+2R与完整资料、首启移除名单/原卷重启/错误独立UUID不合并与原卷恢复；单Docker VM；F29–F35的routing/故障、分配、模板/alias/重建/备份恢复/安全待实测 |
| PG WAL / MySQL binlog → Kafka → Java → ES | F36–F42 规划；两种独立环境串行学习，实际链路与恢复尚未验收 |
| 中文召回与评分质量 | F13分析链与F14五方案固定语料召回、SmartCN/ICU/IK9.4.0安装已实测；F15本地词典/历史词项/受控重建及新增误入已实测；F16显式别名/同义词图/短语/繁简与查询集重载已实测；F17提示/显式拼音/容错与误召回已实测；F18词频/字段长度/文档频率、must与filter及不命中语料追加的解释评分已实测；F19名称/短语/多字段组合、奖励与坏案例已实测；F20已实测固定点评平滑/原热度/压缩/封顶/rank_feature；F21已实测距离/核验时效衰减、缺值/未来/极端与score_mode/boost_mode/显式sort；F22已实测24份×8查询完整人工等级、4调整/2留出/2独立结业、基线与名称奖励的Recall@10/nDCG@10、短结果/漏标/失败口径与残留坏例；小固定语料不宣称全站改善 |
| 图解重构进度 | ✅ F01–F28共56幅静态D2、浅深112 SVG；F28角色拓扑与持久首启图生成、HTTP和实际视觉通过；真实运行分列 |
| 后续教程写作与内容审阅 | F01–F19历史要求xhigh；F01 作者及独立审阅已实际设置。F02/F03/F04/F05/F06/F07/F08/F09/F10/F11/F12 当前根入口无法设置/确认，作者自审且未启动独立代理，限制分别记录；F13独立作者与独立内容审阅CLI实际设xhigh，根入口不可核验单列；F14/F15/F16/F17/F18/F19根入口无法设置/核验，作者自审无独立代理，未声称实际xhigh；F20/F21/F22/F23/F24用户最新指定gpt-6.1-sol/max，主agent实际spawn按该参数，子agent无读回API，完整作者自审/实验/浏览器/提交核对由子agent执行，主agent仅调度；F25/F26/F27/F28当前根入口无法设置或读回最新gpt-6.1-sol/max，作者自审未启动代理，不声称已启用 |


## 2026-10-27 · F28 三节点拓扑、发现与持久首启两轮通过

- 仅实施F28及必要F27下一课链接、目录/当前摘要和逐课提示词转F29，未实施F29。[正文](framework/f28.html)约5299汉字（不含代码），七段式/880px/双主题/独立已读，3案例/72教学HTTP=26+22+24，2静态D2/8折叠练习/4陷阱/0播放器。[本机入口](projects/travel-search/labs/f28/README.md)、[完整作者自审](docs/framework-review/20261027-f28-cluster/content-review.json)。
- 真实ES9.4.0/Lucene10.4.0三进程，独立19228/19229/19230与es-framework-f28网络/三份持久卷；3个master候选，es1仅master、es2 master/data/ingest、es3 master/data。每节点256MiB堆/768MiB容器限制，Docker约3.81GiB/2CPU，与原安全节点共存。无认证、HTTP回环、transport只在容器网络；非三台物理机器，不证明跨机器容灾。ingest仅核角色，未执行管道。
- [正式两轮](projects/travel-search/review/f28/README.md)均先全新卷首启→共同UUID→立即移除initial_master_nodes重建→固定搜索→保留原卷完整重启→错误独立集群/恢复原卷。首启和稳定配置分文件；实际_nodes/settings证明引导名单移除，所有身份阶段比原UUID与3个node ID。第一轮UUID `J73brxk7TIC76PSrq_OdDw`，第二轮 `R5g1NciQR3-tPFU7KtduAQ`；跨独立轮次不同正常。master首启/重启/错误恢复分别02→03→02与03→03→02，不把当选节点不变当通过条件。两轮各72教学HTTP，等待分别60/62另计；其中各5条Java接口调用（502/200/503/200/200），底层客户端重试报文未抓包计数。
- 固定6份景点/whitespace/strict/refresh=-1、tut-f28-attractions显式2主每主1副；Bulk6项created、完整mapping/settings、全部6份_source/count6与4行STARTED布局通过，每组p/r分处es2/es3，es1无业务分片，主分片docs合计6。三个入口相同查询均p01/p02；复用F07 Java，完整DSL与REST精确相等并真实重放比ID/total/卡片字段/score。移除首启参数、重启及错误恢复后重复核对全部内容，不以green/计数代替字段证据。
- 错误案例保留原n3-data，另挂专用新wrong-data并误配single-node：同cluster.name却不同UUID、1成员、本课索引404。仅修seed并保留错误目录，第一轮实际触发加入验证拒绝，第二轮实际保持独立并记录不会再发现其他节点；日志与不合并结果分列。仅删错误空卷、挂回原卷后完整复验。[探索](projects/travel-search/review/f28/attempts/README.md)保留term简写、空seed变null/exit70、transport早于HTTP、日志分支假设与恢复；大型原始events无损gzip/原始哈希保留。作者稿由“必出现加入拒绝”修正为两种真实诊断，依据Coordinator/JoinValidationService与两轮日志；无新课已发布历史勘误。
- [构建/运行](projects/travel-search/review/f28/runtime.json)：Boot4.0.8/Temurin25.0.4.1+1/Java与Rest5 Client9.4.8/Maven3.9.11，clean package与依赖树通过；无测试源，不称No tests to run为测试通过。ES内置JVM26.0.1+8分列。既有F07三静态资源源码/包内/HTTP字节相等；单ES_URL指es2，无新增Controller/前端或自动发现/多地址切换能力。
- [真实观察窗](docs/framework-review/20261027-f28-cluster/shell-review.json)：1440/390×浅深×200/50元=8次实际Java调用与8次作者REST重放，浏览器直连ES=0；200元p01/p02=60元/0元，50元只p02，输入/DSL/原文/卡片相等。同Java PID贯穿本课；浏览器未重做故障注入，缺索引502与计划停机503/恢复由两轮脚本实测。
- [图/HTTP/视觉](docs/framework-review/20261027-f28-cluster/README.md)：D2v0.9.0/dagre/4与201、2源4SVG的fmt/validate/CLI/哈希通过，3份v9.4.0官方源码与本地字节相等。正文12尺寸/主题组、独立图16组、必要前课/目录12组、29锚点/14折叠/18段真实剪贴板、主题/图同步/重载/已读隔离/键盘/file双主题/reduced-motion通过；最大880px/边界差≤1px、零整页横溢。70张实际PNG以6组总览查看，9张最终原图单开；不称逐像素或代码全文逐字视觉审阅。320px眉题单字行和表格挤字已修正复验，图/表/代码右滚动实证；最终阅读无JS/HTTP/请求错误或Pages业务调用。
- [保护](projects/travel-search/review/f28/guards/summary.json)证明已有卷first与缺删除标记reset拒绝，未执行HTTP或Compose变更。[最终清理](docs/framework-review/20261027-f28-cluster/workspace-state.json)先复核第二轮原身份/全部6份文档与REST/Java，再点名DELETE/GET404、Java正常SIGTERM/18081关闭、本课容器/网络移除，三正常卷/镜像保留、错误卷不存在；原安全节点Pid/StartedAt/运行/healthy不变，未采到初始容器ID故不声称ID比较。性能/容量、跨主机、routing、随机故障/多数选举/分片故障、TLS/权限/CDC均未测，不回填其他课。
- [推理入口](docs/framework-review/20261027-f28-cluster/reasoning.json)：最新偏好gpt-6.1-sol/max保留，当前根入口无法设置或读回；作者实施和自审，无独立代理，不声称已启用。[最终检查](docs/framework-review/20261027-f28-cluster/checks.json)分列站点、片段、Python/Bash/JSON/Compose、图与收据哈希。按持续授权提交推送origin/main，提交后核对远端SHA与Pages构建/线上产物；发布结果在交付及工作树外收据记录，不提前标通过。

## 2026-10-27 · F27 酒店与房型分层排序两轮通过

- 仅实施F27与必要F26下一课链接、目录/当前摘要及共享Java增量，逐课提示词转F28，未实施F28。[正文](framework/f27.html)约5304汉字（不含代码）、七段式/880px/双主题/独立已读；3案例/27教学HTTP=13+6+8，Java内部7次搜索另计，2静态D2/8折叠练习/4陷阱/0播放器。[本机入口](projects/travel-search/labs/f27/README.md)、[完整作者自审](docs/framework-review/20261027-f27-ranking/content-review.json)。
- 独立19227/tut-f27-hotels，ES9.4.0/Lucene10.4.0，一主零副本/strict/refresh=-1/无插件；8根酒店/19nested报价摘要，根total数酒店，与F26的报价文档计数分开。快照f27-20261027-v1，杭州/双床/CNY、一间两成人、上海日期[2026-11-01,03)，同offer逐晚整数分，不含税费/换汇/实时可订。名称/描述用显式空格语料与whitespace，品质0–1000为虚构信号；固定中心点30.25/120.15，距离为球面米数。
- [正式两轮](projects/travel-search/review/f27/README.md)：每轮先2HTTP点名清理，再27教学＋51附加HTTP；版本/green/8项created/完整mapping、settings及全部_source通过。西湖候选6家/14报价；ES相关性[h01,h02,h03,h05,h06,h04]、品质[h03,h04,h02,h01,h05,h06]、距离[h04,h03,h01,h02,h05,h06]，同分/同品质/同坐标均按hotel_id。品质缺失_last、距离缺失Infinity，卡片明确缺信号，非0米。
- 逐晚合格10报价/5酒店，a05缺价、c01旧库存、c02缺晚、c03售罄；h03移除。最终三种酒店顺序分别[h01,h02,h05,h06,h04]、[h04,h02,h01,h05,h06]、[h04,h01,h02,h05,h06]。房型总价模式h01[a01,a02,a03,a04]，偏好[a03,a04,a02,a01]，酒店次序不改；最低60000分与偏好所选80000分分别计算标注，同偏好同价由r13/r14稳定。必须含早可退变5候选酒店/9摘要、5合格报价/4酒店；两个单独硬条件也实际核对。
- 库存时效按固定上海2026-10-27 08:00参考时刻、允许[0,300]秒，Duration直接比较，非电脑当前时间或ES延迟保证。品质前2家h03/h04核对后仅h04，不补位；完整模式才含h02等。上限100家/组内20条分别检查完整；注入101测试酒店证实107/100并返回502，先于未知source分支。七组完整Java DSL与固定REST JSON精确相等，真实重放比全部酒店/nested ID、源、score/sort/total/inner_hits，仅归一化typed省略的null评分字段；全部逐晚字段、身份、金额与拒绝常量独立核对。独立运河需求[h07/g01,h08/i01]各65000分，g02政策/i02币种排除。
- 附加51HTTP含重复索引400、Bulk8项409、10种非法输入400、strict400、根投影快照错配502、107/100截断502、两个单硬条件与恢复；本课DTO仅接受JSON布尔。错误后点名重建固定语料，避免只还原_source后拿变化的相关性统计冒充原次序。[探索](docs/framework-review/20261027-f27-ranking/attempts/README.md)保留权重3的稀有描述反例、布尔强转、改写统计、收据链接先后/工作目录与标题单字行等修正；Duration精度改进后重做最终两轮和浏览器，旧收据标pre-duration，不混入最终通过。新F27无已发布历史勘误。
- [构建](projects/travel-search/review/f27/runtime.json)：Boot4.0.8/Temurin25.0.4.1+1/Java与Rest5 Client9.4.8/Wrapper3.3.4/Maven3.9.11，clean package、依赖树、实际Maven通过；jar与固定表、3静态资源源文件/包内/HTTP字节相等，ES bundled JVM26.0.1+8分列。无测试源，不称No tests to run为测试通过。新增/api/hotel-ranking/inspect与/f27.html，正文显示完整查询、资格/房型排序、两层投影和失败分支，不教前端开发。
- [真实观察窗](docs/framework-review/20261027-f27-ranking/shell-review.json)：1440/768/390/320×浅深×7组=56，加400/快照错配502/缺索引502/真实停机503与各恢复，共64次实际Java调用，同PID，浏览器直连ES=0；ES操作24次分列。[窄屏补证](docs/framework-review/20261027-f27-ranking/visual-followup.json)另2次真实Java调用和7处右滚动；卡片/房型次序/所选与最低价/原文/完整DSL一致，条件变化和失败清空旧结果。
- [图/HTTP/视觉](docs/framework-review/20261027-f27-ranking/README.md)：D2v0.9.0/dagre/4与201，2源4SVG的fmt/validate/CLI/哈希通过；4份v9.4.0源码与官方字节相等。正文12组、必要前课/目录24组、独立图16组、15锚点/14折叠/17段真实剪贴板、主题/图同步/展开/重载/已读隔离/键盘/file双主题/reduced-motion通过；最大880px/边界差≤1px、无整页横溢。71张实际PNG以12组总览查看，另9张原图单开；不称逐像素或代码全文逐字视觉审阅。320px标题单字行已修正复验；目录原F01–F21旧徽标/观察页摘要同步F27后另12组复验通过；窄图/表/代码局部滚动有提示与展开。零未处理JS/网络/业务调用，主题替换取消按实际证据分列。
- [清理](docs/framework-review/20261027-f27-ranking/workspace-state.json)：浏览器后8根/19摘要源精确复核/count8/open_contexts0；点名DELETE/GET404、Java正常SIGTERM与18081关闭、F27容器/网络移除，卷/镜像保留；原安全节点ID/StartedAt/PID/运行/healthy不变。未测性能/容量、多节点、随机并发、实时供价/生产订单；未来时刻、恰300秒、最短入住、组内>20、超时/部分分片失败只有代码或固定规则，未单独注入，不回填其他课。
- [推理入口](docs/framework-review/20261027-f27-ranking/reasoning.json)：保存偏好gpt-6.1-sol/max优先历史xhigh，当前根入口无法设置或读回，作者实施和自审，无独立代理，不声称已启用。[最终检查](docs/framework-review/20261027-f27-ranking/checks.json)含站点/片段/JS/Bash/Python/JSON/数据/图哈希。按持续授权提交推送origin/main，提交后核对精确远端SHA和Pages构建/线上产物；最终发布结果在交付和工作树外收据记录，不提前标通过。

## 2026-10-27 · F26 酒店去重、计数与最低价范围两轮通过

- 仅实施F26及必要F25下一课链接、目录/当前摘要与共享Java工程；逐课提示词转F27，未开始F27正文或实验。[正文](framework/f26.html)约4842汉字（不含代码），七段式/880px/双主题/独立已读，3案例/24教学HTTP=14+4+6，Java内部3次搜索另计；2静态D2/7折叠练习/3陷阱/0播放器。[本机入口](projects/travel-search/labs/f26/README.md)、[完整作者自审](docs/framework-review/20261027-f26-collapse/content-review.json)。
- 固定16条offer/9酒店，snapshot_id=f26-20261027-v1，独立19226/tut-f26-offers，一主零副本/strict/refresh=-1/无插件。杭州、双床/含早/flexible/CNY，一间两成人，Asia/Shanghai日期[2026-11-01,03)；起价为同offer表内最低有效单晚价，总价为本次两晚整数分相加；不含税费/换汇/实时可订。o07在1日与3日有资料，中间2日缺失，离店日不能补晚。
- [正式两轮](projects/travel-search/review/f26/README.md)：每轮先2HTTP点名清理，再24教学＋29附加HTTP；版本/green/Bulk16项created/完整mapping、settings与16份_source核对。GET mapping仅规范化ES省略的显式默认doc_values:true。10候选报价/6候选酒店，collapse代表[o01,o05,o09,o10,o07,o16]；hits.total始终10，cardinality本次6是估计，不声称算法精确，候选酒店精确6由完整10条去重确认。
- h01完整query组内3报价，inner size1/2/10分别取[o01]、[o01,o02]、[o01,o02,o03]，降序size1取o03仍不改变外层o01；完整组逐项核对，非nested。去meal命中12条且h01取到不含早o04/5000分；恢复完整条件回o01/10000起价，不能标成两晚总价。
- 三份完整Java DSL与固定REST JSON精确相等，真实重放比全部ID/source/sort/total/inner_hits，仅归一化typed省略的null评分字段。前2报价：h01/o01=100000、h02/o05=120000分；前2酒店内部完整5报价：h01/o02=80000、h02/o06=100000；全10候选核对后7合格报价/4酒店，次序[h04,h05,h01,h02]与最低总价[60000,60000,80000,100000]分。完整逐晚记录、独立价格/拒绝常量、组内报价ID与次序核对，h03缺晚/售罄、h09最短入住拒绝；酒店内精确不能补回酒店范围外低价。
- 重复创建400、Bulk16项409、6非法输入400、未映射/不支持字段与带额外排序search_after/scroll4种400、strict字段400；旧快照502、inner超过10（已知o01代表、REST证实14条只取10条）和全量超过100的502与点名删除后恢复均实测。完整模式拒绝截断，Top K模式明确局部；不把上限当任意规模完整取数方案。[探索修正](docs/framework-review/20261027-f26-collapse/attempts/README.md)保留工作目录、默认mapping、inner_hits数组、折叠原文读取、收据链接先后问题及组溢出用例先撞资料校验的问题；补强已知代表与14/10的直接证据后重做正式两轮，不混入旧通过。新增正文无已发布历史F26勘误。
- [构建运行](projects/travel-search/review/f26/runtime.json)：Boot4.0.8/Temurin25.0.4.1+1/Java与Rest5 Client9.4.8/Wrapper3.3.4/Maven3.9.11，clean package/依赖树/实际Maven通过，jar与固定表、3份静态资源源文件/包内/HTTP字节相等；ES bundled JVM26.0.1+8另列。无测试源，不将No tests to run称测试通过。新增/api/collapse/inspect与/f26.html；正文给出完整query、范围保护、逐晚判断、酒店投影与错误分支，不教授前端代码。
- [真实观察窗](docs/framework-review/20261027-f26-collapse/shell-review.json)：1440/768/390/320×浅深×3范围=24组，加非法400、缺hotel_name资料502、缺索引502、真实停机503及各恢复=32次真实Java调用，同PID55322，浏览器直连ES=0；相应ES操作13次分列。卡片/原文/金额/计数/完整DSL一致，条件变化和失败清空旧结果。超时/部分分片失败只有代码防护，未注入。
- [图/HTTP/视觉](docs/framework-review/20261027-f26-collapse/README.md)：D2v0.9.0/dagre/4与201，2源4SVG的fmt/validate/CLI/哈希通过；[官方固定源码](docs/framework-review/20261027-f26-collapse/sources.json)两文件逐字节相等。正文12组、F25/目录24组、独立图16组、15锚点/13折叠/20段实际剪贴板、主题/图同步/展开/重载/已读隔离/键盘/file双主题/reduced-motion通过；最大880px/边界差≤1px、无整页横溢，窄表/代码局部滚动有提示。64张实际PNG经11组总览查看，另9张原图单开；不称逐像素或代码全文逐字视觉审阅；含窄表/代码右滚动、真实表单与400/502/503区域补证。零JS、未处理网络错误；主题替换取消单列实际证据。
- [清理](docs/framework-review/20261027-f26-collapse/workspace-state.json)：浏览器后16份源精确复核/count16/open_contexts0；点名DELETE/GET404，Java正常SIGTERM与18081关闭，F26容器/网络移除，本课卷/镜像及旧卷保留；原安全节点ID/StartedAt/PID/运行/healthy不变。未测性能/容量、多节点、随机并发、生产安全、实时供价/CDC、税费/订单锁库存；固定快照合格非实时可订，不回填其他课。
- [推理入口](docs/framework-review/20261027-f26-collapse/reasoning.json)：最新保存偏好gpt-6.1-sol/max优先历史xhigh，当前根入口无法设置或独立读回；作者实施与自审，无独立代理，不声称已启用。[最终检查](docs/framework-review/20261027-f26-collapse/checks.json)含站点/片段/JS/Bash/Python/JSON/数据/哈希。按持续授权提交推送origin/main，提交后核对精确远端SHA、Pages构建与线上产物/阅读交互，最终结果在交付消息及工作树外发布收据，不提前标通过。

## 2026-10-26 · F25 多晚库存与精确价表核对两轮通过

- 只实施F25及必要F24下一课/目录/共享工程/当前摘要，逐课提示词转F26，未开始F26正文或实验。正文约4432汉字（不含代码）、七段式/880px/双主题/独立已读，3案例/21教学HTTP=13+2+6，Java内部4次教学搜索另计；2静态D2/7折叠练习/3陷阱/0播放器。[正文](framework/f25.html)、[本机入口](projects/travel-search/labs/f25/README.md)、[完整内容自审](docs/framework-review/20261026-f25-stay/content-review.json)。
- 固定12条offer摘要/11酒店/34条逐晚记录，独立19225/tut-f25-offers，一主零副本/strict/refresh=-1/无插件。snapshot_id=f25-20261026-v1，Asia/Shanghai当地日期[入住,离店)，CNY分/每晚/每间，USD候选先排除；同offer/房型/计划/币种跨全部晚，每间相同成人数，每晚库存≥房间数，总预算覆盖全部房间/晚。入住日min_stay_arrival是显式教学规则，不泛化为完整供应商限制。
- [正式两轮ES/Java](projects/travel-search/review/f25/README.md)：每轮先2HTTP点名清理，再21教学＋29附加HTTP。准备版本/green/Bulk12项created/完整mapping/settings/全部源通过。两端日期与最大库存摘要只筛必要条件，默认8候选；逐晚核对合格o01/o04/o10=70000/65000/90000分，其余缺晚/售罄/最短入住/超总预算/缺价。两间仅o01/o10=140000/180000，o04第二晚1间不足；三晚o04/o05/o06/o10=95000/75000/140000/135000；一晚7条合格。离店3日不读3日晚，o01途经2日min_stay_arrival5不影响1日入住。
- 每轮四组完整Java候选DSL与固定REST JSON精确相等，真实重放比ID/源/sort/total，每个住宿晚字段/身份/金额和人工固定拒绝常量逐项核对，仅归一化typed省略null评分字段。附加29HTTP含重复创建400、Bulk12条409、10非法输入400、strict错误400、摘要快照错配502恢复、109候选只取100时502及点名删除测试报价后恢复。结果按offer_id，不做酒店去重或总价排名；不将min_price乘晚数当实际总价。
- [构建与运行](projects/travel-search/review/f25/runtime.json)：Boot4.0.8/Temurin25.0.4.1+1/Java与Rest5 Client9.4.8/Wrapper3.3.4/Maven3.9.11；clean package/依赖树/实际Maven通过，无测试源，不称No tests to run为测试通过。jar/固定表/服务资源哈希核对，ES bundled JVM26.0.1+8另列。新增stay/inspect与/f25.html，正文展示完整候选查询、逐晚判断、投影及错误分支，不教授前端开发。
- [真实观察窗](docs/framework-review/20261026-f25-stay/shell-review.json)：1440/768/390/320×浅深×4场景=32组，加日期400、源身份缺失502、缺索引502、真实停机503及各恢复=40次实际Java调用，同一PID，浏览器直连ES=0。原文/卡片/逐晚/总价一致，条件变化/失败清空旧结果；[视觉补证](docs/framework-review/20261026-f25-stay/visual-followup.json)另8次真实Java和15次ES操作，专门补拍错误区域，与主40次分列。超时/部分分片失败仅代码防护，无注入。
- [图/HTTP/视觉](docs/framework-review/20261026-f25-stay/README.md)：官方D2v0.9.0/dagre/4与201，2源4SVG，fmt/validate/CLI/哈希通过，只改图源。正文12组、F24/目录24组、独立图16组；16锚点/11折叠/13段实际剪贴板、主题/图同步/展开/重载/已读隔离/键盘/file双主题/reduced-motion通过，零JS与未处理网络错误；最大880px/边界差≤1px，无整页横溢，窄表/代码局部可滚且有提示。78张原PNG中68张经12组总览查看、10张补证逐张原图查看，另5张原图单开；不称每像素或代码全文逐字视觉审阅。320px/1000高组合截图少截末行图注，DOM完整、1600高和单独图注补齐；错误区域与代码/表右滚动补证完成。
- [依据](docs/framework-review/20261026-f25-stay/sources.json)中v9.4.0 RangeQueryBuilder与SearchSourceBuilder两文件和官方逐字节一致；业务规则明确来自固定契约。[探索修正](docs/framework-review/20261026-f25-stay/attempts/README.md)保留占位符判断、折叠原文innerText、主题初始化重载覆盖、右滚动截图选择器等作者脚本错误，不计作产品通过；新增正文无已发布历史F25勘误。
- [清理](docs/framework-review/20261026-f25-stay/workspace-state.json)：浏览器后12份源精确复核/open_contexts0；点名DELETE/GET404、Java正常SIGTERM与18081关闭、F25容器网络移除与19225关闭；本课卷/镜像及旧卷保留，原安全节点ID/StartedAt/PID/运行/healthy不变。未测代表性负载/性能/容量、多节点/生产安全、实时供价/CDC、税费/取消罚金/儿童/CTA/CTD、订单扣库存；固定快照合格非实时可预订，不回填其他课。
- [推理入口](docs/framework-review/20261026-f25-stay/reasoning.json)：最新gpt-6.1-sol/max优先历史xhigh，当前根入口无设置或独立读回API，作者自行实施与审阅，未启动代理，不声称已启用。站点/片段/JS/Bash/Python/数据/哈希最终检查见[checks](docs/framework-review/20261026-f25-stay/checks.json)。按持续授权提交推送origin/main；提交后以精确远端SHA、对应Pages构建与线上产物/阅读交互核对，最终结果在交付消息及工作树外发布收据，不提前标通过。

## 2026-10-26 · F24 同房型条件、inner_hits与nested排序两轮通过

- 仅实施F24及必要F23下一课/读者链接、目录、共享Java工程与当前摘要；逐课提示词转F25，F25正文与实验未开始。正文约4264汉字（不含代码）、七段式/880px/双主题/独立已读，3案例/46教学HTTP=20+10+6+Java与REST10，2静态D2/7折叠练习/3陷阱/0播放器。[正文](framework/f24.html)、[本机入口](projects/travel-search/labs/f24/README.md)、[完整内容自审](docs/framework-review/20261026-f24-nested/content-review.json)。
- 固定9酒店/16报价条目，一条rooms元素=房型×单一计划×币种×日期报价；offer_id唯一、h04/r401故意跨计划重复，不沿用F23的rates object明细做联合筛选。独立19224/tut-f24-object/nested，一主零副本/strict/refresh=-1/整数禁coerce/无插件；同_source对照，根9/9、Lucene live9/25。CNY分/USD美分、单晚2026-11-01/快照2026-10-26；缺价不当0，active不覆盖酒店paused，非实时可预订或连住总价。
- [最终两轮ES/Java](projects/travel-search/review/f24/README.md)：每轮46教学＋13附加、Java内部5搜索另计，每轮前点名清理4HTTP。版本/green/Bulk18项全created/完整mapping/settings/所有_source通过。object与每条件一个nested均命中[h01,h02,h03,h04,h05,h07,h08,h09]；一次nested放完整资格仅[h02,h03,h08]。错误根作用域0、object/path错误400；删人数/退改/币种分别暴露h05/h09/h07，完整条件恢复3家。h03 inner_total2/size1返回o301，offset与完整源逐项一致；size10取回两条，根_source不被裁剪。
- 不带sort.filter时[h02,h03,h08]用[10000,50000,50000]分，h02取到不合格o202；完整filter后[h03,h08,h02]用[50000,50000,65000]分，hotel_id打破同价。改inner排序显示h03/o30255000而酒店min仍50000；故意空sort集合仍返回3酒店，integer缺值哨兵2147483647不是价格。Java同一Query用于query和sort.filter，inner_hits沿该查询；五份完整DSL与REST JSON精确相等，响应仅归一化null的_score/max_score省略，_source/ID/sort/total/inner_hits精确重放。
- [探索与修正](docs/framework-review/20261026-f24-nested/attempts/README.md)保留integer缺值原断言、term短式/完整value语法和主题reload验收初始化错误；不把探索计最终两轮。重复创建400、Bulk18项409、5非法Java输入400、类型/strict400且计数不增均实测；本课新正文无已发布历史勘误。四份固定v9.4.0[源码](docs/framework-review/20261026-f24-nested/sources.json)逐字节一致，nested父根返回、独立排序filter与inner取回路径核对。
- [构建运行](projects/travel-search/review/f24/runtime.json)：Boot4.0.8/Temurin25.0.4.1+1/官方Java与Rest5 Client9.4.8/Wrapper3.3.4/Maven3.9.11，clean package/依赖树/实际Maven通过，jar哈希固定，ES bundled JVM26.0.1+8另列；没有测试源，不将No tests to run称通过。新接口nested/inspect与/f24.html只接服务端白名单5模式，完整条件、排序、投影和错误分支在正文，不教授前端代码。
- [真实观察窗](docs/framework-review/20261026-f24-nested/shell-review.json)：1440/768/390/320×浅深×5输入=40组；另非法输入400、酒店名缺失502、匹配房型名缺失502、缺索引502、真实停机503及各恢复，共50次实际Java调用、同一PID、浏览器直连ES=0。卡片/原文/政策/计划/币种/日期/快照、总数/明细数/完整DSL与typed响应一致；切换和失败清空旧结果。超时/部分分片失败仅代码防护，未注入。
- [图解与HTTP/视觉](docs/framework-review/20261026-f24-nested/README.md)：D2v0.9.0/dagre/4与201，2源4SVG，fmt/validate/正式CLI/哈希通过，只改图源。正文12组、F23/目录24组、独立图16组；16锚点/13折叠、16段真实剪贴板、主题/图同步/展开/重载/已读隔离/键盘/file双主题/reduced-motion通过，零未处理网络/JS错误。最大880px/边界差≤1px，整页无横溢，窄表/代码局部可滚并有提示。[84PNG实际审阅](docs/framework-review/20261026-f24-nested/visual-review.json)：80张经14组总览查看，4张新增原图单开，合计9张另开原图；不声称所有像素或代码全文逐字视觉审阅。390组合图截取曾裁到末行图注，DOM完整/独立图注及同宽更高视口补图完整，记录捕获限制与补证。
- [清理保留](docs/framework-review/20261026-f24-nested/workspace-state.json)：浏览器后两索引全部_source精确再核对、open_contexts0；各DELETE/GET404，Java正常SIGTERM/18081关闭、F24容器与网络移除、19224关闭；F24卷/镜像和全部既有卷/镜像保留。旧安全节点ID/StartedAt/PID/运行状态不变且healthy，记录不含凭据。未测代表性负载/性能/容量、多节点/生产安全、CDC/实时供价、逐晚库存/税费/取消罚金/订单事务；未回填F04–F06。
- [实际配置](docs/framework-review/20261026-f24-nested/reasoning.json)：最新gpt-6.1-sol/max优先旧xhigh，父调度报告实际spawn参数/fork_turns=none，子agent无独立读回API；作者自行完成内容/实验/浏览器/提交发布核对，主agent只调度，本实施者没有执行或声称主会话compact。站点/JS/Bash/Python/片段/图源与固定资料检查见[checks](docs/framework-review/20261026-f24-nested/checks.json)。按持续授权提交推送origin/main；提交后用发布脚本核对精确远端SHA、对应Pages部署及线上产物/导航交互，最终结果在交付消息和本机发布收据，不提前标为通过。

## 2026-10-26 · F23 酒店、房型与offer文档边界两轮通过

- 只实施F23及必要F22下一课/目录/共享工程和当前摘要，逐课提示词转F24，F24正文与实验未启动。正文约4642汉字（不含代码）、七段式/880px/双主题/独立已读，3案例/90教学HTTP=38+14+28+Java与REST10，2静态D2/7折叠练习/3陷阱/0播放器。[正文](framework/f23.html)、[读者入口](projects/travel-search/labs/f23/README.md)、[内容自审](docs/framework-review/20261026-f23-model/content-review.json)。
- 固定3酒店/5房型/8报价，一份catalog生成hotels/object/nested/offers四投影；独立19223/tut-f23-*，一主零副本/strict/refresh=-1、无插件，身份/类别keyword，整数禁coerce，日期格式显式。CNY分/USD美分、服务日2026-11-01/快照2026-10-26，不能跨币种只比数字或把active覆盖酒店paused。rooms为nested的投影中rates仍object，仅作完整明细，不保证同rate联合条件；本课报价条件均在独立offer上执行。单晚快照不代表实时库存或预订事务。
- [最终ES/Java两轮](projects/travel-search/review/f23/README.md)：每轮90教学＋19附加，Java内部5搜索另计，轮前点名清理8次、轮间缺索引502另1次。版本/green/Bulk17项全created/errors=false/有效mapping/settings/全部_source通过；GET mapping只省略type=object，验收仅归一化这处表达。root3/3/3/8，Lucene live3/3/8/8；object单房型ID命中h01，nested根term0/带path命中h01且完整_source仍含r102，GET nested房型根404。完整条件[o101,o201]；删币种/报价状态/酒店状态分别多USD o103/closed o202/paused o301，恢复后回2。550元任意房型返回[o102,o104,o203]，3报价所属[h01,h01,h02]，不冒称3酒店。
- nested改o101 60000→63000只增加h01根版本；两轮实际段观察旧段live5/deleted3、新段live3/deleted0，总live8，h02/h03版本与源不变。独立offer仅o101根变化、其余7份不变；改酒店主文档不传播，显式update_by_query更名4报价副本，随后原价/原名逐份恢复。deleted受merge影响，不作为稳定写放大计数或性能结论。[四份源码](docs/framework-review/20261026-f23-model/sources.json)与官方v9.4.0逐字节一致，UpdateHelper完整IndexRequest与InternalEngine块软更新路径核对。新课无已发布F23历史勘误。
- [探索与修正](docs/framework-review/20261026-f23-model/attempts/README.md)保留_stats层级、mapping表达、未刷新后按查询恢复HTTP409（3成功/1冲突）、typed客户端省略null评分字段与窄屏图迭代。最终流程显式refresh，再清理后两轮；Java重放只归一化null的hits.max_score/hit._score省略，_source/ID/排序/total精确一致。重复创建400、Bulk17项409、类型/strict错误400、5非法Java输入400均实测，失败写不增计数。
- [最终构建与运行](projects/travel-search/review/f23/runtime.json)：Boot4.0.8/Temurin25.0.4.1+1/官方Java与Rest5 Client9.4.8/Wrapper3.3.4/Maven3.9.11，clean package/依赖树和实际Maven版本通过，jar SHA固定、ES bundled JVM另列。工程没有测试源，不把“No tests to run”称测试通过。model/inspect服务端白名单5模式，完整查询/投影/字段与错误分支在正文，无前端代码教学。
- [真实观察窗](docs/framework-review/20261026-f23-model/shell-review.json)：1440/768/390/320×浅深×5输入=40组，另10次400/报价和房型明细不完整502/缺索引502/真实停机503与恢复，共50次实际Java调用、同一PID，浏览器直连ES=0。逐卡ID/原文/完整_source/金额币种单位/计划状态日期快照/DSL/typed响应一致，切换或失败清空旧结果。超时/部分分片失败仅代码防护，本课未故障注入。
- [图解与HTTP/实际视觉](docs/framework-review/20261026-f23-model/README.md)：D2v0.9.0/dagre/4与201，2源4SVG，fmt/validate/官方CLI/哈希通过；只改源文件。正文12组、F22/目录24组、独立图16组；16锚点/14折叠、16段真实剪贴板、主题/图同步/弹窗/重载/已读键隔离/Tab/file双主题/reduced-motion通过。最大880px/边界差≤1px、整页无横溢；窄表/代码局部横滚并给提示。320px更新图缩短标签后重新生成并完整复验。[86PNG](docs/framework-review/20261026-f23-model/visual-review.json)通过15总览全部实际查看，9张另开原图、其余77仅总览；改图后受影响总览2/3/5/6/7与320浅/390深原图复看，不冒称全文逐字或所有像素审阅。
- [清理与保留](docs/framework-review/20261026-f23-model/workspace-state.json)：浏览器验收后全部_source再核对、open_contexts0；四索引各DELETE/GET404，Java正常SIGTERM/18081关闭、F23容器/网络移除与19223关闭，F23卷/镜像和全部既有卷/镜像保留。既有安全节点ID/StartedAt/PID/运行状态不变且结束healthy。未测代表性负载、性能/容量、多节点、生产安全、供价同步/CDC、逐晚库存/税费/订单事务；未回填F04–F06。
- [实际配置](docs/framework-review/20261026-f23-model/reasoning.json)：最新gpt-6.1-sol/max，父调度实际spawn该参数/fork_turns=none的报告，子agent无独立读回API，全部作者自审/实测/截图/提交推送与远端/Pages核对由本课作者完成，根agent仅调度。本实施者没有执行或声称主会话compact。站点/JS/Bash/Python语法、片段/图源哈希/固定投影检查分别记[checks](docs/framework-review/20261026-f23-model/checks.json)；按持续授权提交origin/main，交付前核对远端精确SHA与该提交Pages构建/线上产物和导航交互；线上首轮将F22切主题主动取消的6次浅图请求计为网络失败，14产物字节及6组交互已完成，无JS错误/业务请求。发布检查器补src变更与同组替换SVG完整解码证据，保留所有requestfailed并仍拒绝未解释失败，随后以最终提交重新验收。

## 2026-10-26 · F22 查询集、完整标注与实用搜索结业两轮通过

- 只实施F22及必要F21下一课/目录/共享工程入口与当前摘要；逐课提示词转F23，未开始F23。正文约4516汉字（不含代码）、七段式/880px/双主题/独立已读；3案例、70教学HTTP=21+19+8+Java与REST22，2静态D2、7折叠练习、3陷阱、0播放器。[正文](framework/f22.html)、[本机入口](projects/travel-search/labs/f22/README.md)、[独立结业任务](projects/travel-search/labs/f22/assessment.md)。
- [内容自审](docs/framework-review/20261026-f22-evaluation/content-review.json)：24份虚构资料，20份合格、4份闭园/异城/超预算/异币种反例；8查询×24份=192个显式等级，4调整/2留出/2独立结业。作者单人按意图标注0–3，无真实游客抽样或双人一致性统计；Recall阈值≥2，1级仍有DCG增益。独立19222/tut-f22-attractions，一主零副本/strict/refresh=-1，无插件，name/description显式whitespace/lowercase/BM25。首次ES运行前冻结两策略与门槛，原计划哈希和探索日志保留；后将h-walk不被资料支持的“安静”措辞澄清为免费湖岸步行，不改查询输入、资料、等级、参数或门槛。4份[本地源码](docs/framework-review/20261026-f22-evaluation/sources.json)与官方v9.4.0字节一致；新课无历史F22正文勘误。
- [最终ES/Java两轮](projects/travel-search/review/f22/README.md)：最终jar每轮70教学＋23附加，Java内部16次搜索另计；每轮前点名清理2次，轮间缺索引502另1次。版本/green/Bulk24全created/errors=false/count24/完整mapping/settings/逐份_source通过。每个主查询20候选、前10均有标注；同一硬条件与_score/ID排序，Python独立公式、_rank_eval逐查询/宏平均、Java实际DSL/原文/ID/等级/两个指标一致。重复建索引400、Bulk24项409、10非法Java输入400、name=null/未知标签502与写回refresh恢复、缺索引502与同Java进程恢复通过；故意去掉status的回归探针能识别资格错误。
- 调整集nDCG均值0.768275→0.829090（+0.060815），Recall均值同0.916667；两条留出nDCG均值同0.731603、Recall同0.937500，无观察到的新指标退步，也无留出收益。按冻结相对门槛仅为固定教学语料选择candidate；a15纪念品店/a07文化馆/a10摄影展厅/a11用品店的坏首位仍保留，不宣称全站改善。独立结业两条输入未在正文逐步演示，任务要求先自行标注/诊断/实现改法再揭示参考；参考文件公开，不声称防作弊隔离或代替读者完成。
- 边界实测：删a15标签仍HTTP200但unrated_docs列出；一个查询非法数值时_rank_eval HTTP200且failures非空，不能用成功子集平均冒充完整评估。name AND雨天只剩a09，恢复多字段OR回20，区分候选漏召回与Top10漏召回。空结果/全0等级按0单列，不混主平均。ES9.4.0内置normalized DCG按实际返回长度截理想序列；两份3级命中/三份3级完整标注时，内置1，本课完整IDCG@10为0.765361。主8查询均返回10故三端口径一致；本例dcg的k=0实际合法，改用k=-1验证400后合法恢复，失败记录保留。
- Java沿用Boot4.0.8/Temurin25.0.4.1+1/官方Java与Rest5 Client9.4.8/Wrapper3.3.4/Maven3.9.11；最终clean package与依赖树通过，ES bundled JVM另列。[运行与制品](projects/travel-search/review/f22/runtime.json)。quality/evaluate与/f22.html按同一evaluation.json打包，浏览器不提交标签/任意DSL；每查询独立请求，不承诺跨查询原子快照。连接/transport503、ES拒绝502、不完整字段/未知标签/超时/分片失败502的职责分开；后两种故障本课未构造。
- [真实观察窗](docs/framework-review/20261026-f22-evaluation/shell-review.json)：3宽×双主题×6输入=36组、44次实际Java调用，含400/字段不完整502/缺索引502/真实停机503与同一PID恢复；[卡片细节](docs/framework-review/20261026-f22-evaluation/card-detail.json)另2次，共46次最终验收调用。完整DSL/客户端响应/DTO、每条ID/等级/原文名称/ES分数/分母/DCG/IDCG/平均逐项对照；条件和错误清空旧结果，浏览器直连ES为0。窄屏选项原先截断，已改短文案/单列表单、重建最终jar并重跑两轮/矩阵。
- [图解与HTTP/实际视觉](docs/framework-review/20261026-f22-evaluation/README.md)：D2v0.9.0/dagre/主题4与201，2源4SVG，fmt/validate/正式CLI/哈希通过；cycle箭头为设计依赖，metrics箭头为阅读顺序，两个指标独立计算。HTTP正文12组、F21/目录24回归、独立图16组，每组16锚点/10折叠，12段真实剪贴板；主题/图同步/弹窗/重载/已读键隔离/Tab/file双主题/reduced-motion通过。最大880px/边界差≤1px、无整页横溢，代码/窄表仅局部滚动。81PNG全部经11张总览实际查看，18张另逐张打开，其余63仅总览；三张资料/指标表、320表单、窄屏Java左右端和真实卡片逐项核对。补拍主题过渡/快速滚动未重绘的瞬态留档，等真实过渡结束/绘制帧后重拍复看；不冒充全文逐字/全部像素审阅。
- [探索与修正](docs/framework-review/20261026-f22-evaluation/attempts/README.md)保留k=0、临时新文档201预期、旧venv缺模块/Python3.9的Pillow版本、默认浏览器缓存缺失、目录/锚点与视觉迭代；[工具版本](docs/framework-review/20261026-f22-evaluation/tooling.json)记录Playwright1.58.0/Pillow11.3.0及显式既有Chromium1248实际156.0.8078.4，未声称默认浏览器已安装。未改检查器，未回填F04–F06。未测代表性流量、显著性、标注一致性、性能、多节点、生产安全、持续更新；超时/部分分片失败仅代码防护。[清理](docs/framework-review/20261026-f22-evaluation/workspace-state.json)：open_contexts0、点名DELETE/GET404、Java正常SIGTERM/18081关闭、F22容器/网络移除与19222关闭，卷/镜像保留；既有安全节点ID/StartedAt/Pid/运行状态不变且清理后healthy。最初health字段在收据归一化时丢失，不拿缺字段推断历史健康状态。
- [运行与编排](docs/framework-review/20261026-f22-evaluation/reasoning.json)：用户最新gpt-6.1-sol/max，父调度实际spawn该参数、fork_turns=none；子agent无读回API，danger-full-access/approval_policy=never/网络启用。全部实施、自审、实测、浏览器/实际截图、提交推送与远端/Pages核对由本课作者承担，主agent仅调度；本实施者未执行或声称已做主会话compact，历史xhigh记录保留。运行node tools/check.mjs、JS/Bash/Python语法、片段/图源哈希与必要工程检查；按持续授权提交推送origin/main，交付时核对真实远端与Pages产物/导航。

## 2026-10-26 · F21 附近与新鲜：软衰减、硬资格与显式sort两轮通过

- 只实施F21及必要F20下一课/目录/工程入口和当前摘要；逐课提示词转F22，未实施F22。正文约3700汉字（不含代码）、七段式/880px/双主题/独立已读；3案例、88教学HTTP=16+13+20+Java与REST39，2静态D2、7折叠练习、3陷阱、0播放器。[正文](framework/f21.html)、[本机入口](projects/travel-search/labs/f21/README.md)。
- [内容自审](docs/framework-review/20261026-f21-decay/content-review.json)：14份虚构资料，独立19221/tut-f21-attractions，一主零副本/strict/refresh=-1，无插件，简介whitespace/lowercase与显式BM25。游客lat30.25/lon120.15，固定核验原点2026-10-01T00:00:00.000Z；verified_at不是开放状态。gauss距离offset1km/scale5km、exp时间offset1d/scale30d，两项decay=.5，权重.5/.3；半分位置为6km/31d。5份本地源码与官方v9.4.0逐字节相同，[来源](docs/framework-review/20261026-f21-decay/sources.json)。新课无历史F21正文勘误。
- [真实ES/Java两轮](projects/travel-search/review/f21/README.md)：每轮88教学＋55附加，点名清理前后各2，轮间缺索引502与同Java进程恢复各1另计。green/Bulk14全created/errors=false/count14/有效mapping/settings/逐份_source核对；近码头约0.480km、fresh约6.003km、far约29.969km。逐份用实际arc距离与UTC日期核对G=.5D、H=.3T及B+G+H、B+G×H、B×(G+H)、G+H；max_boost=.8作用于函数部分。sum展厅第三高于远码头，replace展厅第一，保留退步，不宣称整体质量改善。
- 缺值与资格：bare缺两项衰减均1、missing错误第一；仅exists/仅weight0兜底不能保证0，教学实测sum命中总权重0仍回退1，改用weight1的常量零函数与exists互斥分支。sum missing=B，multiply missing/extreme=0仍为候选9份；显式min_score才7份。硬半径10km缩为5份，far/极远/缺坐标退出；未来与过去31d单项T同.5，主查询先排未来，附加实测原点.000允许、.001排除。停航/异城/超预算/无关山林均不能靠奖励入场；非法scale/decay/坐标/未映射排序400与合法恢复通过。
- Java沿用Boot4.0.8/Temurin25.0.4.1+1/官方Java与Rest5 Client9.4.8/Wrapper3.3.4/Maven3.9.11；最终clean package、依赖树、最终jar两轮通过，ES bundled JVM单列。[版本制品](projects/travel-search/review/f21/runtime.json)。decay-search与/f21.html六评分/三sort、13固定输入的实际DSL/卡片原文/坐标日期/金额/score/sort/总数/完整解释与REST对照；24非法输入400、重复建索引400/Bulk14项409、name=null的502/写回refresh恢复、缺索引502与同进程恢复通过。搜索与单份解释为两次请求，不承诺并发原子视图。
- [真实观察窗](docs/framework-review/20261026-f21-decay/shell-review.json)：3宽×双主题×17输入=102组、110实际Java调用；[细节补验](docs/framework-review/20261026-f21-decay/visual-detail.json)4次，总114最终验收调用。对照完整DSL/客户端响应/DTO、三排序/硬半径/原点改变/空集/4种资格排除解释，400/字段不完整502/缺索引502/真实停机503与同Java进程恢复通过；条件/错误清空旧内容，浏览器直连ES为0。距离模式仅有坐标时填distanceKm，其他模式明确提示未选距离排序，缺坐标提示缺坐标且sort保留Infinity。完整响应压缩保留，不用截图代替字段核对。
- [图解、HTTP与视觉](docs/framework-review/20261026-f21-decay/README.md)：官方D2v0.9.0/dagre/主题4与201，2源4SVG，fmt/validate/正式CLI/哈希通过；箭头为教学依赖，省略内部调度。HTTP正文12组、F20/目录24回归、独立图16组，每组15锚点/9折叠，14段真实剪贴板；主题/图同步/弹窗/重载/已读旧键隔离/Tab/file双主题/reduced-motion通过。最大880px/边界差≤1px，无整页横溢；长代码/窄表局部滚动。76PNG全部经10张总览实际查看，16张另逐张打开，其余仅总览；11样本行的价格/缺值与9条真实次序逐项对照，窄屏Java左右滚动补验，不冒充全文逐字或全部截图逐像素审阅。
- [探索修正](docs/framework-review/20261026-f21-decay/attempts/README.md)保留weight0回退、Client ScriptSource编译、默认date format响应省略、radius字符串、旧venv与图尺寸/距离null提示修正；未改检查器。未测全站查询集/留出指标、性能、多节点、生产安全、轨迹或持续核验更新，超时/部分分片失败仅代码防护；F04–F06历史状态不回填。[资源清理](docs/framework-review/20261026-f21-decay/workspace-state.json)：open_contexts0，点名DELETE/GET404，Java正常SIGTERM/18081关闭，F21容器/网络移除、19221关闭，卷/已有镜像缓存保留，既有安全节点ID/StartedAt/Pid不变且healthy。
- [运行与编排](docs/framework-review/20261026-f21-decay/reasoning.json)：用户最新gpt-6.1-sol/max，父调度实际spawn该参数、fork_turns=none；子agent无读回API。当前权限danger-full-access/approval_policy=never/网络启用，未改全局配置。全部写作、自审、实验、浏览器、截图与提交/远端/Pages核对由本课子agent承担，主agent仅调度；本实施者未执行或声称已做主会话compact。历史xhigh记录保留。运行node tools/check.mjs与适用语法/片段/哈希检查，按持续授权提交推送origin/main，交付时核对真实远端与Pages。

## 2026-10-26 · F20 点评质量与热度：平滑、压缩、封顶与特征边界两轮通过

- 只实施F20及必要F19下一课/目录/工程README和当前摘要，逐课提示词转F21；未实施F21。正文约4425汉字（不含代码）、七段式/880px/双主题/复制/独立已读，3案例、79教学HTTP=14+11+21+Java与REST33，2静态D2、7折叠练习、3陷阱、0播放器。[正文](framework/f20.html)、[本机入口](projects/travel-search/labs/f20/README.md)。
- [内容自审](docs/framework-review/20261026-f20-signals/content-review.json)：11份虚构资料，固定审核/去重/每订单一条/近30天访问快照，Q=(vR+80)/(v+20)在上游计算。5分1评约4.047619、4.8分千评约4.784314；先验20/4是教学假设，不是ES默认或置信度。独立19220/tut-f20-attractions，一主零副本/strict/refresh=-1、whitespace/lowercase/BM25，无插件。缺失与已知0保留来源区别。[五份固定ES源码](docs/framework-review/20261026-f20-signals/sources.json)与官方v9.4.0字节一致，当前文档另列；新课无旧F20正文勘误。
- [真实ES/Java两轮](projects/travel-search/review/f20/README.md)：每轮79教学＋35附加，前后点名清理各2；轮间缺索引502和同Java进程恢复各1另计。ES9.4.0/Lucene10.4.0、green/Bulk11全created/errors=false/count11/有效mapping/settings/完整_source通过。average一评满分领先，quality千评4.8领先；raw与仅ln1p压缩均把弱相关展厅抬第一，bounded降第五但仍超过缺信号/零热度者。逐份核对B+min(0.2Q+0.15ln(1+H),1.5)；huge与steady都达函数上限，总分约1.912>1.5，ID打破平局。
- function_score保留7个文本/硬条件候选；rank_feature实际REST/Java实现：文本must+特征should仍7份，rank-only去掉文本让山林入场、缺特征者退出。特征用实际编码S核对S/(S+4)，不将原double当S；单值/正数/约0.4%精度与普通字段区分，0/负/多值/排序/聚合拒绝、ln零/缺missing的400与合法查询恢复、factor位置通过。闭园/异城/超预算不能靠奖励进场。未宣称整体质量或性能改善。
- Java沿用Boot4.0.8/Temurin25.0.4.1+1/官方Java与Rest5 Client9.4.8/Wrapper3.3.4/Maven3.9.11；最终clean package、依赖树、最终jar两轮实连通过，本地已有官方ES9.4.0镜像与ES bundled JVM独立记录。[版本/制品哈希](projects/travel-search/review/f20/runtime.json)。signal-search与/f20.html八模式、11输入的实际DSL/完整query解释、卡片/原文/信号/金额/score/sort/总数/完整解释与REST核对。15非法输入400、重复建索引400/Bulk11项409、name=null的502/写回refresh恢复、缺索引502与同进程恢复通过；两次搜索/解释不是并发原子快照。
- [真实观察窗](docs/framework-review/20261026-f20-signals/shell-review.json)：3宽×双主题×15输入=90组、98实际Java调用，另[细节补验](docs/framework-review/20261026-f20-signals/visual-detail.json)3次，共101最终验收调用；探索与修正阶段另计。八模式、预算/异城/空集、缺特征、完整条件未匹配、完整DSL/客户端响应/DTO逐项对照，400/字段不完整502/缺索引502/真实停机503及同Java进程恢复通过，条件/错误清空旧内容，浏览器直连ES为0。完整浏览器响应压缩保留；JS重序列化大数按结构和相同IEEE double精确比较，REST↔Java沿用微小数值容忍。
- [图解与HTTP/视觉](docs/framework-review/20261026-f20-signals/README.md)：D2v0.9.0/dagre/主题4与201，2源4SVG，fmt/validate/正式CLI/哈希通过，箭头说明教学依赖而非内部调度。HTTP正文12组、F19/目录24回归、独立图16组，18锚点/组、9折叠/组、16段真实剪贴板；主题/图同步/弹窗/重载/已读旧键隔离/Tab/file双主题/reduced-motion通过。最大880px/边界差≤1px、无整页横溢；长代码/窄表局部滚动。65PNG全部经9张总览查看，15张另逐张打开，其余仅总览；11样本行与6次序行逐格对照真实资料/响应，窄屏Java左右滚动补验。不冒充全文逐字审阅。
- [探索修正](docs/framework-review/20261026-f20-signals/attempts/README.md)保留初价表/有效mapping默认省略/启动早请求/不完整探针字段选错/目录漏card类/大数DOM序列化/片段范围与证据脚本路径错误；修正后按相关范围重跑，未改检查器或伪造输出。未测全站查询集/留出指标、性能、多节点/多主分片、生产安全/DB/CDC/信号持续更新；超时/部分分片失败仅代码防护，F04–F06历史受阻不回填。[资源清理](docs/framework-review/20261026-f20-signals/workspace-state.json)：open_contexts0、点名DELETE/GET404、Java正常SIGTERM/端口关闭、F20容器/网络移除，卷/已有镜像/缓存保留，既有安全节点running/healthy不变。
- [运行与编排记录](docs/framework-review/20261026-f20-signals/reasoning.json)：用户本轮最新指定gpt-6.1-sol/max；主agent实际spawn按此参数，子agent无模型/强度读回API。当前权限指令danger-full-access/approval_policy=never/网络启用，无全局配置修改。全部内容自审、实验、浏览器、提交核对由本课子agent执行，主agent仅调度；后续每课新子agent按相同实际参数与权限，课间先实际compact再派下一课由专门调度辅助agent处理，本实施者未声称已compact。历史xhigh记录保留。运行node tools/check.mjs、片段/语法/哈希检查；按持续授权提交推送origin/main，交付核对实际远端。

## 2026-10-25 · F19 名称、短语与多字段权重：组合评分与候选门槛两轮通过

- 只实施F19及必要F18下一课、目录、工程入口和当前摘要；提示词转F20，未实施F20。正文约4561汉字（不含代码），七段式/880px/双主题/复制/独立已读；3案例、92教学HTTP=16+20+8+Java与REST48，2静态D2、7折叠练习、3陷阱、0播放器。[正文](framework/f19.html)、[本机入口](projects/travel-search/labs/f19/README.md)。
- 教学与勘误：新课无旧F19正文勘误。12份虚构资料、两个人工意图，独立19219/tut-f19-attractions，一主零副本/strict/refresh=-1、无插件。name/description显式standard tokenizer＋lowercase/BM25；中文逐字，name.exact为未归一keyword，与F18空格整词前提分开。整名相等/名称短语/散词、每字段AND/跨字段OR、子查询boost/固定奖励与候选门槛分开解释。5本地ES9.4.0源码与官方tag字节一致，Lucene10.4.0取大解释源码哈希。[内容自审](docs/framework-review/20261025-f19-weights/content-review.json)、[来源](docs/framework-review/20261025-f19-weights/sources.json)。根入口不可设置/核验xhigh，作者写作及自审，无独立代理，未声称提示词改变配置。
- [真实ES/Java两轮](projects/travel-search/review/f19/README.md)：每轮92教学＋39附加，两端点名清理各2、缺索引/同进程恢复各1另计；green/Bulk12全created/errors=false/count12/完整实际配置、中文token/position/offset与存储词项通过。默认整名1/短语3/名称AND4/简介AND2；split不能把两字段词项拼接。sum/best/tie保持五候选但次序改变，both字段分2.1211295/4.7019653核对A+B/max/max+.1其余；三种multi_match实际同语义对照通过。tuned/1的exact贡献约2.2787993+9.115197+8，升到第一；插空格分析不变却少8分。should可选九份/文本必需五份/强制名称短语三份；过滤始终排除闭馆/异城/超预算。
- 调权得失：主输入tuned/3、50把散词资料抬到简介提及者之前；“夜游”best/1活动领先，名称3/50与tuned/1均误抬室内摄影展。规则没有被称为上线方案或整体质量改善。Java沿用Boot4.0.8/Temurin25.0.4.1+1/官方Java与Rest5 Client9.4.8/Wrapper3.3.4/Maven3.9.11；最终clean package/依赖树/最终jar两轮实连通过，本地已有官方ES9.4.0镜像与bundled JVM另记。[版本制品](projects/travel-search/review/f19/runtime.json)。新增weight-search与/f19.html，16输入实际DSL与固定REST规范化一致、全部卡片/原文/票价/score/sort/total/完整解释核对；数值容忍区分客户端再序列化。19非法输入400、12份_source、重复建索引400、空词流、description=null的502与完整写回/refresh恢复、缺索引502及同Java进程恢复通过；未新增单元测试。
- [真实观察窗](docs/framework-review/20261025-f19-weights/shell-review.json)：3宽×双主题×16输入=96组、104实际Java调用，补充单卡/未匹配面板3次，共107。六模式、名称权重、空格、夜游退步、异城/零预算/空集、闭馆/超预算解释、完整DSL/客户端响应/DTO核对；400/字段不完整502/缺索引502/真实停机503及同Java进程恢复通过，条件/错误清空旧内容，浏览器直连ES为0。完整浏览器响应压缩保留，摘要与哈希分列。
- [图解与HTTP/视觉](docs/framework-review/20261025-f19-weights/README.md)：官方D2v0.9.0/dagre/主题4与201，2源4SVG，fmt/validate/生成与CLI/源产物哈希通过；320px实看发现文字偏小，缩短标签后重生成并重跑HTTP。名称图隐形边仅排版，候选图箭头是教学判断顺序，不冒充内部调度。正文12组、F18/目录24必要回归、独立图16组，18锚点/组、9折叠/组、16段真实剪贴板；主题/图同步/展开弹窗/重载/已读旧键隔离/实际Tab/file双主题/reduced-motion通过。最大880px/边界差≤1px，无整页横溢；长代码/窄表局部滚。57PNG全部经7张总览查看，20张另逐张打开，其余37仅总览，不冒充全文逐字；12行样本表与5行次序表对照实际资料/响应，Java左右滚动/复制补足窄屏范围。
- [探索修正](docs/framework-review/20261025-f19-weights/attempts/README.md)保留初探、工作目录生成失败/旧工程构建不计通过、增补夜游tuned后92请求重跑、错误映射片段范围/F18导航漏接/验收主题初始化及窄图修复；未改检查器或伪造响应。未测全站质量/留出指标、性能、多主分片、生产安全/DB/CDC；超时/部分分片失败仅代码防护，F04–F06历史受阻不回填。[资源恢复](docs/framework-review/20261025-f19-weights/workspace-state.json)：open_contexts0、点名DELETE/GET404、Java正常SIGTERM/端口关闭、F19容器/网络移除，卷/已有镜像/缓存保留，其他节点状态保留。运行node tools/check.mjs与片段/语法/哈希检查；按持续授权提交推送origin/main，交付核对实际远端。

## 2026-10-25 · F18 BM25与解释评分：词频、长度与语料变化两轮通过

- 只实施F18及必要F17下一课/目录/工程与当前摘要，提示词转F19；未实施F19。正文约4860汉字（不含代码），七段式/880px/双主题/复制/独立已读保留；3案例、58教学HTTP=21+6+10+Java与REST21；清理/探活/构建/Java内部调用/附加/浏览器另计。2静态D2、7折叠练习、3陷阱、0播放器。[正文](framework/f18.html)、[本机入口](projects/travel-search/labs/f18/README.md)。
- 教学与勘误：新课无旧F18正文勘误。虚构10份初始+6份闭馆山林追加资料，独立19218/tut-f18-attractions，一主零副本/strict/refresh=-1，无插件。description用空格给定中文词边界、whitespace/lowercase，不冒充生产中文方案；name不评分。显式BM25 k1=1.2/b=.75/discount_overlaps=true/norms/存储词向量，默认参数与本课配置区分。4本地ES9.4.0源码与官方tag字节一致，Lucene10.4.0官方源码哈希记录；LegacyBM25的k1+1说明解释boost≈2.2，未虚称业务调权。[自审](docs/framework-review/20261025-f18-bm25/content-review.json)、[来源](docs/framework-review/20261025-f18-bm25/sources.json)。xhigh根入口不可设置/核验，作者写作与自审，无独立代理。
- [真实ES/Java两轮](projects/travel-search/review/f18/README.md)：每轮90客户端请求=58教学+32附加，点名清理前后各2另计；green/Bulk10及6全created/errors=false/count10→16/完整有效配置通过。初始西湖六份次序four/night/short/twice/once/long；等长8词freq1→2→4饱和增分，同freq1的2/8/16词递减；完整词项/position/offset、freq、n/N与解释公式核对。初始_count10/字段N9/西湖n8/avgdl50/9，闭馆/异城仍影响统计，缺简介不计字段N。两词OR保持六候选，夜游n1、稀有词及双项加和使night第一；全filter六候选全0/ID升序，城市must增加城市贡献但本例次序不变。
- 追加六份不含西湖且closed的资料：refresh前旧分数，后N15/n8/avgdl62/15、同六候选与本例次序、原景点分数变化；hz-short原文/版本/seq_no/primary_term不变。只比较当前固定条件的相对次序与解释，不要求跨环境浮点相同，也不把分数当概率/通用阈值。存储词向量与完整_explain留原响应；匹配失败的根0与文本子句正分区分。多分片DFS仅解释边界，未实测。
- Java沿用Boot4.0.8/Temurin25.0.4.1+1/官方Java与Rest5 Client9.4.8/Wrapper3.3.4/Maven3.9.11，最终clean package/依赖树、最终jar两轮通过；本地已有官方ES9.4.0镜像，不冒充新下载，ES bundled JVM单列。[版本制品](projects/travel-search/review/f18/runtime.json)。新增score-search与/f18.html，固定字段/索引/模式/解释ID，完整query复用到_explain；两请求非并发原子视图。14组实际Java DSL与固定REST规范化一致、完整卡片/原文/价格/score/sort/total/解释树逐项核对，float→double再序列化用微小数值容忍；未关闭必填校验，无新增单元测试。12非法输入400、逐份_source、重复建索引400、缺索引502与同Java进程恢复通过。
- [真实观察窗](docs/framework-review/20261025-f18-bm25/shell-review.json)：3宽×双主题×11输入=66组，含基线N9→追加N15、400/502/503及恢复共73实际Java API；另[表格/单卡/完整条件未匹配面板](docs/framework-review/20261025-f18-bm25/visual-detail.json)4次，共77次。实际模式/两词/城市/零预算/空集/闭馆/缺简介/不含词/价格排除、卡片/完整DSL/DTO/解释叶子一致。条件/错误清空旧内容，浏览器直连ES为0。最终补明未匹配根与子句贡献区别，重建最终jar后重跑真实两轮及观察窗。
- [图解与HTTP/视觉](docs/framework-review/20261025-f18-bm25/README.md)：官方D2v0.9.0/dagre/主题4与201，2源4SVG，fmt/validate/生成与CLI/图源/产物哈希通过；独立竖卡隐形边仅排版，语料图箭头表示实际观察顺序，无Archify/播放器。正文12组、F17/目录24组必要回归、独立图16组；18锚点/组、9折叠/组、16段真实剪贴板，主题/图同步/展开弹窗/重载/已读旧键隔离/实际Tab/file双主题/reduced motion通过。最大880px/边界差≤1px、无整页横溢，长代码/窄表局部滚动。58PNG：47经8总览查看，11补充逐张打开；共20张另逐张打开，其余仅总览，不冒充全文逐字。10行完整样本表与六行评分表均对照真实源和响应。
- [探索修正](docs/framework-review/20261025-f18-bm25/attempts/README.md)保留ExplainResponse API编译误用、解释浮点比较、缺收据链接与未匹配子句展示澄清；修正后验证，未改站点检查器或伪造响应。未测全站质量/性能、多主分片/DFS、在线发布/TLS权限/DB/CDC；超时/部分分片失败仅代码防护。F04–F06历史受阻不回填。[资源恢复](docs/framework-review/20261025-f18-bm25/workspace-state.json)：open_contexts0、点名DELETE/GET404、Java正常SIGTERM、F18容器/网络移除，空卷与缓存保留，其他节点状态保留。运行node tools/check.mjs、片段/语法/哈希检查；按持续授权提交推送origin/main，交付核对实际远端。

## 2026-10-25 · F17 提示、拼音与容错：候选、误入与下架两轮通过

- 只实施F17及必要F16下一课/目录/工程与当前摘要，提示词转F18；未实施F18或其他课。正文约4812汉字（不含代码），七段式/880px/双主题/复制/独立已读保留；3案例、64教学HTTP=19+6+17+Java与REST22，清理/探活/构建/Java内部调用/作者附加/浏览器另计；2静态D2、7折叠练习、3陷阱、0播放器。[正文](framework/f17.html)、[本机入口](projects/travel-search/labs/f17/README.md)。
- 教学与勘误：新课无旧F17正文勘误。14份虚构资料/固定意图，独立19217/tut-f17-attractions，一主零副本/strict/refresh=-1，无额外插件。completion维护input与city|status单一scope、显式weight/前10/全部总数未知；普通搜索城市/open/CNY、前20/精确计数/ID升序，全部资料CNY，不提供预算过滤。拼音由资料显式给全拼/首字母，lowercase不转写汉字；整名keyword fuzzy与逐字bool_prefix分开。四目标本地源码与官方v9.4.0字节一致，[自审](docs/framework-review/20261025-f17-suggestions/content-review.json)、[来源](docs/framework-review/20261025-f17-suggestions/sources.json)。根入口无法设置/核验xhigh，作者写作与自审、无独立代理，未声称提示词改变配置。
- [真实ES/Java两轮](projects/travel-search/review/f17/README.md)：每轮115客户端请求=64教学+51附加，前后点名清理各2另计；green/Bulk14全created/errors=false/count14/完整有效配置通过，两轮完整分析token/position/offset、ID/次序/改写摘要一致。初始故宫/completion四ID，sayt多bj-infix；博物/completion空、sayt仅bj-palace。放宽scope后query仍不能过滤suggest，闭馆与外地排前；skip_duplicates=true误删同名不同ID的bj-same-b，业务按ID保留。当前同文档双input只返回一个option，不冒充已触发跨来源ID合并。
- gugong/gg均五候选，古公花园同音误入；name查询拼音空，keyword分析汉字仍汉字。天谈公园整名精确空、fuzzy/guarded均天潭/天坛；西胡/fuzzy为西河/西湖，AUTO与guarded空。收窄阈值<4 code point精确/否则首字符不变距离1是本课策略，未认证全站效果。bool_prefix加fuzziness后天谈公园还误入古公花园，真实改写保留；天坛公圆最后前缀不容错为空。03同时更新东门status与scope，GET先可见、refresh前仍提示、后两路都排除；只改status的真实附加反例触发502/SEARCH_INCOMPLETE，完整写回/refresh同Java进程恢复。
- Java沿用Boot4.0.8/Temurin25.0.4.1+1/官方Java与Rest5 Client9.4.8/Wrapper3.3.4/Maven3.9.11，clean package/依赖树、最终jar两轮实连通过；使用本地已有官方ES9.4.0镜像，不冒充重新下载。新增suggestions与/f17.html，固定字段/索引/模式；11组实际DSL重放REST，完整卡片/原文/拼音/城市/分/币种/状态/score/sort/total与计数核对。22份实际Java DSL与固定文件规范化一致；Bean校验不额外返回pinyinValid；客户端响应再序列化含completion#places，与原始HTTP字节区分。12非法输入400、空词流/大小写空白、逐份_source、重复建索引400、缺索引502与同进程恢复通过；无新增单元测试。[版本制品](projects/travel-search/review/f17/runtime.json)。
- [真实观察窗](docs/framework-review/20261025-f17-suggestions/shell-review.json)3宽×双主题×11输入共66组/73实际Java请求；六模式/城市/同名不同ID/原名与建议文字/总数未知/误匹配及0候选、完整DSL/客户端响应/DTO一致。实际400、陈旧scope502、缺索引502、真实停机503及同Java进程恢复；条件/错误清空旧内容，浏览器直连ES为0。ES内部调用、浏览器初始化资料另计。
- [图解与HTTP/视觉](docs/framework-review/20261025-f17-suggestions/README.md)：官方D2v0.9.0/dagre/主题4与201，2源4SVG，fmt/validate/生成/CLI与源产物哈希通过；独立卡片隐形边仅排版，无Archify/播放器。正文12组、F16/目录24组必要回归、独立图16组；19锚点/组、9折叠/组、16段真实剪贴板，主题/图同步/弹窗/重载/已读旧键隔离/实际Tab/file双主题/reduced motion通过；最大880px/边界差≤1px、无整页横溢，长代码与表格局部滚。57原始PNG经8张总览查看，10张另逐张打开；其余仅总览，不冒充全文逐字。Java长行与窄屏表的初始截图不代表完整右侧，复制/DOM/源与14行全表对照补足。
- [探索修正](docs/framework-review/20261025-f17-suggestions/attempts/README.md)保留初探、mapping等价序列化、Bean校验属性、括号编译、固定源码路径与浏览器主题初始化误判；未改检查器或伪造响应。未测全站质量/性能、多节点/自动转写/线上发布/TLS权限/DB/CDC；执行超时与部分分片失败仅代码防护。F04–F06历史受阻不回填。[恢复资源](docs/framework-review/20261025-f17-suggestions/workspace-state.json)：结束open_contexts0、点名DELETE/GET404、Java正常SIGTERM、F17容器/网络移除、空卷与缓存保留，其他节点状态保留。更新STATUS、运行node tools/check.mjs与片段/语法/哈希检查；按持续授权提交推送origin/main，交付核对实际远端。

## 2026-10-25 · F16 别名、同义词与繁简：词图、短语与查询集重载两轮通过

- 只实施F16及必要F15下一课/目录/工程与当前摘要，提示词转F17；未实施F17或其他课。正文约4968汉字（不含代码），七段式/880px/双主题/复制/独立已读保留；3案例、87教学HTTP=22+12+21+Java及REST32，清理/探活/构建/Java内部调用/作者附加/浏览器另计；2静态D2、7折叠练习、3陷阱、0播放器。[正文](framework/f16.html)、[本机入口](projects/travel-search/labs/f16/README.md)。
- 教学与勘误：新课无旧F16正文勘误。11份虚构目录/固定意图；独立19216/tut-f16-attractions/tut-f16-names，一主零副本/strict/refresh=-1。standard→lowercase→ICU Traditional-Simplified为写入基础，搜索再加synonym_graph；显式别名普通text/非索引alias，搜索阶段updateable=true/expand=true/lenient=false。名称/英文存储with_positions_offsets，同城市/open/CNY/0–10000分/ID升序。别名补到实体，全局同义词会误入同名商户；城市条件正确仍可能意图不合。3目标本地源码与官方v9.4.0字节一致，[内容自审](docs/framework-review/20261025-f16-synonyms/content-review.json)、[固定来源](docs/framework-review/20261025-f16-synonyms/sources.json)。根入口无法设置/核验xhigh，作者写作与自审、无独立代理，未声称提示词改变运行配置。
- [真实ES/Java两轮](projects/travel-search/review/f16/README.md)：每轮120客户端请求=87教学+33附加，两端点名清理各4另计。规则created先于索引，green/11 Bulk全created/errors=false/count11/完整有效配置通过；两轮完整token/position/length/offset/type与ID摘要一致。紫禁城/BJ：名称bj-wall，别名bj-palace/bj-wall，同义词再误入bj-theme/bj-traditional；SY别名空、同义词sy-palace属错误意图。PALACE museum实际palace从0跨到2，forbidden0→1/city1→2，再接museum；默认AND2、放宽分支4、完整phrase1、后置归一0，三个validate改写保留。故宮后置归一漏bj-wall；源繁体与已存简体分开核对，不把当前分析冒充历史。
- 别名更新皇家旧宫后搜索仍0，显式refresh后仅bj-palace。完整管理集PUT保留英文规则、增加皇城旧称，实际一个节点两搜索链重载/零失败后命中四中文候选；未重写/刷新存量名称，bj-traditional原文/版本/seq_no/primary_term/已存向量不变、count11。被引用集DELETE400，结束先删索引再删集/分别GET404。stop移除规则左侧400、10非法输入400、空流/0预算、逐份_source、重复建索引400、删索引502与同Java进程恢复通过。单节点/小语料不认证整体质量、多节点传播、在线发布或性能。
- Java沿用Boot4.0.8/Temurin25.0.4.1+1/官方Java及Rest5 Client9.4.8/Wrapper3.3.4/Maven3.9.11，clean package与依赖树通过；最终jar实连两轮与观察窗。ICU用F14官方SHA512已验证缓存，再验SHA512/descriptor后安装新F16派生镜像，不冒充新网络下载。新增synonym-search与/f16.html，服务端固定索引/字段/分析器；8组实际双分析与DSL重放REST，完整DTO/原文/英文/别名/城市/价格/币种/状态/score/sort/total/relation一致，DSL与固定文件规范化一致。explain=true保留完整属性，避免裁剪positionLength导致客户端缺bytes/termFrequency解析失败；未关闭必填校验，无新增单元测试。[版本与制品](projects/travel-search/review/f16/runtime.json)。
- [真实观察窗](docs/framework-review/20261025-f16-synonyms/shell-review.json)12组/64实际Java API，另[6次可视错误/恢复](docs/framework-review/20261025-f16-synonyms/visual-detail.json)，共70；卡片/两列当前输入词图/请求/完整DTO一致，所有六模式/城市/繁简/更新后名字/0预算与空流通过。400/502、ES真实停机503及同Java进程恢复，条件和错误清空旧内容，浏览器直连ES为0。词图两列不读取历史词项，已存证据由REST案例独立核对。
- [图解与HTTP/视觉](docs/framework-review/20261025-f16-synonyms/README.md)：官方D2v0.9.0/dagre/主题4与201，2源4SVG，fmt/validate/生成/CLI与源产物哈希通过；三卡独立、词图箭头为token跨度，无Archify/播放器。[生成收据](framework/diagrams/f16/generation.json)。正文12组、F15/目录24组、独立图16组；18锚点/组、10折叠/组、19段真实剪贴板，主题/图同步/弹窗/重载/已读旧键隔离/实际Tab/file双主题/reduced motion通过；最大880px、边界差≤1px、无整页横溢，长代码/表格局部滚。11源行/5中文ID格/3英文ID格/4词图边与真实资料/响应一致。57原始PNG看10张总览，9张另逐张打开；其余仅总览，长行及窄屏表初始横向图不代表完整右侧，由复制/源/DOM对照补足。
- [探索与修正](docs/framework-review/20261025-f16-synonyms/attempts/README.md)保留词图探查、默认mapping序列化、客户端属性解析、body不含路径参数、片段转义、验收脚本隐藏details/input事件误判、窄屏图标签与主题过渡截图修正；未改检查器绕过。未测全站质量/性能、多节点重载一致性、在线迁移、TLS权限/DB/CDC、提示/拼音/评分；执行超时与部分分片失败只有代码防护。F04–F06历史受阻不回填。结束open_contexts0、点名删除404、Java正常SIGTERM、F16容器/网络移除，已清理卷及缓存保留，其他节点状态保留。[资源恢复](docs/framework-review/20261025-f16-synonyms/workspace-state.json)。更新STATUS并运行node tools/check.mjs、片段/语法/哈希检查；按持续授权提交推送origin/main，交付核对实际远端。

## 2026-10-24 · F15 专有词、词典与重建：历史词项与新增误匹配两轮通过

- 只实施F15及必要F14下一课/目录/工程与当前摘要，提示词转F16；未实施F16或其他课。正文约4343汉字（不含代码），七段式/880px/双主题/复制/独立已读保留；3案例、84教学HTTP=基线23+文件/加载/新写25+重建20+Java及REST16，清理/探活/下载构建/作者附加/浏览器另计；2静态D2、7折叠练习、3陷阱、0播放器。[正文](framework/f15.html)、[本机入口](projects/travel-search/labs/f15/README.md)。
- 教学与勘误：新课无旧F15正文勘误。虚构云栖里/星澜湾、9旧+2新资料，独立19215/tut-f15-v1/v2，一主零副本/strict/refresh=-1，name索引与查询都ik_smart，显式存储with_positions_offsets；固定城市/open/CNY/0–10000分/AND/ID升序。仅改本地ext_dict文件不生效，重启后新查询无法匹配旧词项，新写可命中；refresh/重启不改写历史。词向量请求不传doc或per_field_analyzer，结合显式term探针与真实_search；未存向量临时生成不能冒充历史。正式两轮前固定意图/相关ID，样本先经词边界探索，不冒充盲评。2目标源码与官方v9.4.0字节一致，[内容自审/限制](docs/framework-review/20261024-f15-dictionary/content-review.json)、[来源](docs/framework-review/20261024-f15-dictionary/sources.json)。
- [真实ES/Java两轮](projects/travel-search/review/f15/README.md)：每轮158客户端请求=教学84+附加74，完整空词典→文件发布→同节点/卷重启→新写→冻结v1→预建v2→_source重建→点名删除404。完整配置/green、Bulk9与2全created、count9/11、reindex11created/0updated/0冲突/无失败，十一份原文/ID两索引一致。品牌ID：基线hz-brand，加载后空，新写hz-new，重建hz-brand/hz-new；目的地ID：基线nj-bay/nj-scattered，加载后空，新写nj-new，重建nj-bay/nj-boundary/nj-new。串字误入被排除，湾流主题馆由星/澜/湾流变成星澜湾/流后新增误入，不能把候选增加都算改善。两轮完整分析/已存向量/位置/offset/ID摘要一致。
- Java沿用Boot4.0.8/Temurin25.0.4.1+1/官方Java及Rest5 Client9.4.8/Wrapper3.3.4/Maven3.9.11，最终clean package与依赖树通过；API源码在两轮与最终构建间未变。IK9.4.0使用F14已核验缓存并重验SHA512/descriptor，新派生镜像只安装IK，重启后实际清单9.4.0；不冒充本轮再次网络下载，也不把本地指纹称独立签名。新增dictionary-search与/f15.html，固定索引/字段/analyzer/旧ID；Java实际分析/词向量/搜索DSL逐份重放REST，核对完整token/position/offset、向量、ID/次序/名称/城市/价格/score/sort/total/relation。附加10非法输入400、零预算/空流、原文、重复建索引400、写阻塞403、重复create重建409、删v2后502/原v1可用及同进程重建恢复通过；无新增单元测试。[最终构建与版本](projects/travel-search/review/f15/build/runtime.json)。
- [真实观察窗](docs/framework-review/20261024-f15-dictionary/shell-review.json)：12组/79实际Java API，卡片/查询与已存词项/请求/完整DTO一致；两索引选择不切词典，改变条件及错误清空旧内容，0候选与失败分别呈现。400/502、ES真实停机503与同Java进程恢复通过，浏览器直连ES为0。图解采用官方D2v0.9.0/dagre/主题4与201，两源四SVG，fmt/validate/生成/CLI与源产物哈希通过，[生成收据](framework/diagrams/f15/generation.json)。静态图箭头表示操作先后，取舍三卡独立；无Archify/播放器，其门禁不适用。
- [HTTP与视觉](docs/framework-review/20261024-f15-dictionary/README.md)：正文12组、F14/目录24组必要回归、独立图16组，17锚点/组、10折叠/组、19段真实剪贴板；图同步/弹窗/主题重载/已读与旧键隔离/实际Tab/file双主题/reduced motion通过。两组最终数据表/完整ID矩阵与实际源/响应逐项一致。最大880px/边界差≤1px/无整页横溢，长代码与表格局部滚。49原始PNG看9张标注总览，10张另逐张打开；其余仅总览不冒充全文逐字。Java长行及窄屏表初始横向位置不代表完整右侧，复制/DOM对照补足。最终一处“正式对照前”措辞修订后重新跑阅读/复制/表格，26阅读截图与已审阅版本逐字节相同。
- [探索与失败修正](docs/framework-review/20261024-f15-dictionary/attempts/README.md)保留分词边界探索、重复重建误期200实得409、重启后503、GET /已200但state not recovered/initialized的实际响应；wait改等隔离集群恢复至yellow/green/1节点且未超时后两轮通过，未改检查器绕过。静态链接因第二轮收据未生成的一次失败也保留；真实记录完成后通过。根入口无法设置/核验xhigh，作者自审无独立代理，未声称实际xhigh。未测远程词典/多节点传播、在线迁移、整体中文质量/性能、TLS权限/DB/CDC、同义词/繁简/拼音/评分；超时与部分分片失败只有代码防护。F04–F06历史受阻状态不回填。
- [资源恢复](docs/framework-review/20261024-f15-dictionary/workspace-state.json)：结束两索引open_contexts均0，点名删除/GET404；Java正常SIGTERM，F15容器与网络移除，已删课次索引的卷及镜像/制品缓存保留。前课19200仍停、源码篇节点状态保留。更新STATUS、运行node tools/check.mjs与片段一致性/语法检查；按持续授权提交推送origin/main，交付核对实际远端。

## 2026-10-24 · F14 中文分词方案比较：三插件9.4.0安装与五方案两轮通过

- 只实施F14及必要F13下一课/目录/工程与当前摘要，提示词转F15；未实施F15或其他课。正文约4500汉字（不含代码），七段式/880px/双主题/复制/独立已读保留；3案例、108教学HTTP=基线20+插件64+Java及REST24，清理/探活/下载/安装/作者附加/浏览器重复另计；2静态D2、7折叠练习、3陷阱、0播放器。[正文](framework/f14.html)、[本机入口](projects/travel-search/labs/f14/README.md)。
- 教学与勘误：新课无旧F14正文勘误。独立19214节点/tut-f14-attractions、12资料、4事先固定意图/相关ID；一主零副本/strict/refresh=-1，同城市/open/CNY/0–10000分、AND与ID升序。比较完整standard/smartcn/icu_analyzer/ik_smart/ik_max_word，不把归一差异都归给tokenizer。ik_smart因长词分别漏故宫博物院/长江大桥；max补短词但河流意图仍误入路名餐厅；长江大桥的max+AND三项均必需，validate/query实证；全角ｃａｆｅ/Cafe/cafe分别核对。SmartCN只在四个小查询符合同一判断，不认证全站最佳。3目标源码与官方v9.4.0字节一致，IK不以master源码冒充制品源码。[内容自审与来源](docs/framework-review/20261024-f14-analyzers/content-review.json)。
- [插件与真实ES/Java两轮](projects/travel-search/review/f14/README.md)：Elastic两包9.4.0官方SHA512、IK维护方9.4.0本地指纹与descriptor锁定，派生镜像安装/重启后节点清单均9.4.0。IK GitHub迁移公告/真实下载200、旧Security Policy/outbound_network提示保留；无自定义/远程字典。真实SmartCN9.3.0包在一次性构建容器被9.4.0拒绝（退出70），未改descriptor。每轮152客户端请求（教学108+附加44），都stock→插件切换，完整有效mapping/settings/Bulk12created/refresh/count12；35份插件分析/20搜索、6Java输入实际两分析+搜索DSL重放REST，完整token/position/offset、ID/次序/名称/城市/价格/score/sort/total/relation一致。基线插件ES400/Java502、插件mapping创建失败无索引残留、10非法输入400、预算0/空流、原文保留、未知analyzer400、删索引502/重建/点名清理404通过。另6份机制请求单列。
- Java沿用Boot4.0.8/Temurin25.0.4.1+1/官方Java与Rest5 Client9.4.8/Wrapper3.3.4/Maven3.9.11，clean package与依赖树通过；新增analyzer-search与/f14.html，服务端候选/字段/索引白名单，查询与固定写入样本分别分析，不冒充存量词项。未新增单元测试，按本课真实语义与边界验收。[真实观察窗](docs/framework-review/20261024-f14-analyzers/shell-review.json)12组/84API，五方案故宫4/2/2/1/2、长江4/2/3/1/3及CAFE0/1/1/0/0逐份核对；卡片/请求/DTO/token一致，400/502与真实ES停机503/同Java进程恢复通过，改变条件/错误清空旧结果，浏览器直连ES为0。
- 图解：官方D2v0.9.0/dagre/主题4与201，2源4SVG，fmt/validate/生成、CLI/源/产物哈希通过，[生成收据](framework/diagrams/f14/generation.json)。受控比较箭头表示实验步骤；取舍三卡独立，隐形边只排版。无Archify/机制播放器，其门禁不适用。
- [HTTP与视觉](docs/framework-review/20261024-f14-analyzers/README.md)：本课12组、F13/目录24组必要回归、独立图16组；17锚点/组、9折叠/组、13段真实剪贴板、图同步/弹窗/主题重载、已读/旧键隔离/实际Tab/file双主题/reduced motion通过。另2组最终表格/命令顺序/文字与布局核对，12源数据行/15展示token格/20完整ID格逐项一致。最大880px/边界差≤1px/无整页横溢，表格与Java长行局部滚。46原始PNG中44看8张标注总览，12张另逐张打开（含2张最终表）；其余仅总览不冒充全文逐字核验。Java与窄屏矩阵仅初始横向位置，复制/片段/DOM完整对照补足。
- [尝试修正](docs/framework-review/20261024-f14-analyzers/attempts/README.md)保留IK GitHub404迁移核对、错包bind mount缺descriptor转COPY的真实版本拒绝、初稿字符串/片段范围/引号同步、图继承700px与收尾证据链接尚未归档等记录；未修改检查器绕过失败。下载/构建放在cleanup之前，避免网络失败删除基线。当前根入口无法设置或核验xhigh，作者自审、无独立代理；未把提示词当运行配置。未测整体中文查询集质量/性能、词典/同义词/拼音/评分、多节点滚动安装、TLS权限、DB/CDC；超时/部分分片失败只有代码防护。F04–F06历史受阻状态不回填。结束open_contexts=0、点名删除/GET404，Java正常SIGTERM，F14临时容器/网络及错包失败容器移除，空卷/镜像缓存保留；前课19200仍停、源码篇节点状态保留。[资源恢复](docs/framework-review/20261024-f14-analyzers/workspace-state.json)。按持续授权提交推送origin/main，交付核对实际远端。

## 2026-10-24 · F13 分析链与中文召回：token、漏召回与误召回两轮通过

- 只实施F13及必要F12下一课/目录/工程与当前摘要，提示词转F14；未实施F14或其他课。正文约4751汉字（不含代码），七段式/880px/双主题/复制/独立已读保留；3案例、58教学HTTP=准备6+分析12+召回12+Java及REST28，清理/探活/Java内部调用/作者附加/浏览器重复另计；2静态D2、7折叠练习、3陷阱、0播放器。[正文](framework/f13.html)、[本机入口](projects/travel-search/labs/f13/README.md)。
- 教学与勘误：新课无旧F13正文勘误。独立八份语料/tut-f13-attractions，一主零副本/strict/refresh=-1；name为html_strip→standard tokenizer→lowercase，mismatch多字段索引同链/查询keyword，raw整值。故宫失配0、对齐AND4、短语3，故城宫苑/故，宫主题展逐份解释误召回；英文PALACE-MUSEUM对齐2/不转小写0，城市/状态/预算独立。field分析不是search_analyzer模拟，分析输入不是读存量词项；请求覆盖不改mapping/历史token，小写不改_source。实际保留😀/UTF16两个单位，HTML“宫”offset[4,9)可含被删标签；初查错误预期已修正。4目标源码与官方v9.4.0字节一致，[内容及源码收据](docs/framework-review/20261023-f13-analysis/content-review.json)。
- [真实ES/Java两轮](projects/travel-search/review/f13/README.md)：原Compose ES9.4.0/Lucene10.4.0，每轮81客户端请求（教学58+附加23），创建/green/完整有效mapping/settings/Bulk8created/refresh/count8。10分析/11查询/7Java输入，Java两份实际分析与搜索DSL重放REST，完整token/position/offset、ID/次序/价格/score/sort/total/relation一致。8非法输入400、0分空集、无索引自定义analyzer/未知analyzer400、覆盖后mapping仍keyword、删索引Java502/同进程重建恢复及点名清理404通过。
- Java沿用Boot4.0.8/Temurin25.0.4.1+1/官方Java与Rest5 Client9.4.8/Wrapper3.3.4/Maven3.9.11，最终clean package与依赖树通过；新增analysis-search与/f13.html，服务端四模式白名单，浏览器不传任意索引/字段/analyzer。[真实观察窗](docs/framework-review/20261023-f13-analysis/shell-review.json)12组/47实际API，0→4→3、英文2→0、SY/预算50元/空流、卡片/请求/DTO/token与响应一致；400/502、ES真实停机503与同Java进程恢复通过，改变条件/错误清空旧结果，浏览器直连ES为0。未新增单元测试，按本课真实语义与边界验收。
- 图解：官方D2v0.9.0/dagre/主题4与201，2源4SVG，fmt/validate/生成、CLI/源/产物哈希通过，[生成收据](framework/diagrams/f13/generation.json)。分析链箭头为流变换；召回卡片为独立模式，实线词项比较、隐形边只排版。无Archify/机制播放器，其门禁不适用。
- [HTTP与视觉](docs/framework-review/20261023-f13-analysis/README.md)：本课12组、F12/目录24组必要回归、独立图16组；16锚点/组、11折叠/组、22段真实剪贴板、图同步/弹窗/主题重载、已读/旧键隔离/实际Tab/file双主题/reduced motion通过；最终输入边界段落另4组补验。最大880px/边界差≤1px/无整页横溢，代码表格局部滚。48原始PNG中44张看8张标注总览，16张另逐张打开（含4补验）；32仅总览不冒充全文逐字核验。Java初始横向截图右侧不冒充完整，片段同步/剪贴板补足；卡片/token数字另由DOM/API比较。
- [xhigh实际运行](docs/framework-review/20261023-f13-analysis/reasoning.json)：根入口无法设置或核验，独立作者与独立内容审阅均使用CLI实际设xhigh并有运行元数据；初稿预测经实测校正。独立审阅无阻断问题，白名单来源/UTF16长度与整数分上界两建议已补充且HTTP补验。[失败尝试](docs/framework-review/20261023-f13-analysis/attempts/README.md)保留mapping省略默认、emoji预期、D2路径、缺Text复制控件/选择器及折叠pre误读修正。未比较插件/词典/同义词/拼音、查询集质量/评分、性能、多节点、TLS权限、DB/CDC；超时/部分分片失败仅代码防护。F04–F06历史状态不回填。结束目标索引open_contexts=0，点名删除/GET404，Java正常关闭，框架ES恢复原停止状态、卷与源码篇节点保留。[资源恢复](docs/framework-review/20261023-f13-analysis/workspace-state.json)。按持续授权提交推送origin/main，交付核对实际远端。

## 2026-10-21 · F12 更新、可见性与基础结业：CRUD/冲突与新样本两轮通过

- 只实施F12及必要F11下一课/目录/工程与当前摘要，提示词转F13；未实施F13或其他课。正文约5177汉字（不含代码），七段式/880px/双主题/复制/独立已读保留；3案例、114条教学HTTP=准备6+CRUD36+冲突17+Java27+结业28，清理/探活/作者附加断言/浏览器重复另计；2静态D2、6练习、0播放器。[正文](framework/f12.html)、[本机入口](projects/travel-search/labs/f12/README.md)。
- 教学与勘误：新课无旧F12正文勘误。新4份演示与另8份结业语料、独立tut-f12-attractions/tut-f12-graduation，一主零副本/strict/refresh_interval=-1。固定ID创建/完整替换、_create仅新建、doc合并/重新索引/noop、closed与删除分别验证；strict不检查业务必填，updated不保证搜索可见，GET不简化成只读translog。Seq_no/primary_term来自本轮GET，两读取者旧条件409，重读核对意图再提交保留他人价格，不去条件盲重试。6目标源码与官方v9.4.0逐字节一致，[内容自审](docs/framework-review/20261021-f12-crud/content-review.json)与来源收据保存。
- [真实ES/Java两轮](projects/travel-search/review/f12/README.md)：原Compose ES9.4.0/Lucene10.4.0，每轮160次调用（教学114+附加46），两索引创建/green/完整mapping/Bulk4与8项created/refresh/count。实时GET新价、未刷搜索旧价、显式刷新新搜索与旧PIT保留；完整替换字段丢失、局部保留、下架/删除、二次删除/缺资料404、旧条件更新/删除409和重读通过。另noop不变序号、realtime=false旧值、refresh=true、wait_for在GET已新但Future未完成后由外部refresh释放、输入400/ID不一致400/条件409/关闭410/缺索引502通过。
- 基础结业：先给新“星湾”数据与独立要求，参考解折叠。HZ/CNY/open/0–6000分、价格/ID升序，每页2条，free0/garden4500/museum6000为2/1；garden7000分并refresh后只剩free/museum，原PIT保留原三份，museum closed后只剩free而count仍8。五份排除项逐份解释；另结业7200分/closed旧版本409与重读合并实测。每页Java实际DSL同PIT重放REST，对照完整ID/次序/价格/score/sort/total/relation；作者参考解跑通不认证读者独立结业。
- Java沿用Boot4.0.8/Temurin25.0.4.1+1/官方Java与Rest5 Client9.4.8/Wrapper3.3.4/Maven3.9.11，最终clean package与依赖树通过，无单元测试。新增/api/attractions/changes与/f12.html，完整GET/create/带版本replace/patch/delete/refresh、独立分页会话，旧契约保留。结业同jar另起18081、启动前固定索引，不开放浏览器任意索引名。[真实观察窗](docs/framework-review/20261021-f12-crud/shell-review.json)12组/86次API，双窗口409、GET/search可见性、分页/条件/空集/404、502删索引重建、ES真实停机503/同Java进程恢复通过；补13次API/9张区域截图，浏览器直连ES为0。
- 图解：官方D2v0.9.0/dagre/主题4与201，2源/4SVG，fmt/validate/生成及CLI/源/产物哈希通过，[生成收据](framework/diagrams/f12/generation.json)。可见性图无连接卡片表示不同读取路径，隐形边只排版；冲突箭头表示受控交错次序。无Archify或机制播放器，对应门禁不适用。
- [HTTP与视觉](docs/framework-review/20261021-f12-crud/README.md)：本课12组、F11/目录24组必要回归、独立图16组；17锚点/组、12折叠/组、16段真实剪贴板逐字核对，图同步/弹窗/主题重载、已读与旧键隔离、实际Tab、file双主题/reduced motion通过。最大880px/边界差≤1px/整页无横溢，代码表格局部可滚。49原始PNG中40看标注总览，19另逐张打开（含所有9补拍）；其余仅总览不冒充逐字核对。Java截图仅初始横向位置可见部分代码，片段同步/剪贴板补足；卡片数字另由DOM/API逐项比较。
- [尝试修正](docs/framework-review/20261021-f12-crud/attempts/README.md)保留初查缺证据链接、作者脚本inner_text误读折叠JSON、viewport未完整拍到409后的补拍及预览venv缺Pillow记录；没有修改应用绕过失败。当前入口无法设置或核验xhigh，作者自审、无独立代理；提示词不是运行配置。最终站点/片段/JS/Python/Bash/JSON/SVG/NDJSON/图源与输入/截图哈希分别检查。未测随机并发/负载/性能、主分片切换、多节点、监听槽耗尽、TLS/权限/插件/DB/CDC；超时/部分分片失败仅沿用防护。F04–F06旧受阻状态不回填。结束两索引open_contexts=0，点名删除确认404，两个Java正常关闭，框架ES恢复原停止状态，持久卷/源码篇节点保留。[资源恢复](docs/framework-review/20261021-f12-crud/workspace-state.json)。按持续授权提交推送origin/main，交付核对实际远端。

## 2026-10-21 · F11 稳定分页与PIT：重漏对照、两轮实连与生命周期通过

- 只实施F11及必要F10下一课/目录/工程与当前摘要，提示词转F12；未实施F12或其他课。正文约4527汉字（不含代码），七段式/880px/双主题/复制/独立已读保留；3案例、60条教学HTTP请求=准备6+偏移4+视图19+Java/REST对照31，点名资源清理/探活/作者附加断言/浏览器重复另计；2静态D2、6练习、0播放器。[正文](framework/f11.html)、[本机入口](projects/travel-search/labs/f11/README.md)。
- 教学与勘误：完整继承F10十六份语料/字段值，主查询仍全国、CNY/open、非负价/20000分、相同multi_match，九份候选。from是跳过条数，默认10000约束from+size而非索引容量；唯一ID只确定固定视图内同值次序。首屏后far1000→15000分、tea8000→500分并明确refresh，普通from/size与无PIT search_after都far重复/tea遗漏，PIT原九份各一次且保留原价；新普通搜索显示新次序/新价。完整sort包含显式_shard_doc，原始FieldValue不从元/km显示值重建；PIT不是业务事务/备份/实时售卖保证。ES本身不替应用校验条件变化，409与固定页大小是Java契约。4份目标源码与官方v9.4.0逐字节一致，[内容自审](docs/framework-review/20261021-f11-pagination/content-review.json)与来源收据保存。
- [真实ES/Java两轮](projects/travel-search/review/f11/README.md)：原Compose ES9.4.0/Lucene10.4.0、独立tut-f11-attractions，每轮110次真实调用，创建/green/完整mapping/Bulk16项created/refresh/count，三种排序逐页在同一PIT将Java真实DSL重放REST，ID/次序/原始sort/score/价格/total9/eq一致。受控改价、截短三项sort400、from+search_after400、自动附加决胜键、显式关闭后404、Java条件/页大小/旧页序/末页409、关闭410、外部释放真实ES上下文410、2/2/2/2/1与空集、11种非法输入400、删索引502及点名清理404/重建通过。另原生1秒PIT与Java60秒闲置同时等待66秒不续期，分别实际404/410；后台清理不承诺精确到期瞬间。
- Java保持Boot4.0.8 / Temurin25.0.4.1+1 / 官方Java与Rest5 Client9.4.8 / Wrapper3.3.4、Maven3.9.11，最终clean package与依赖树通过，无单元测试。新增pages/start、next、close及/f11.html，复用F10查询/排序但PIT请求不带index。内存保存最新PIT/完整元组/条件/页序，60秒闲置、5秒扫描尽力关闭、100会话上限、退出释放；本机串行应用不承诺多实例或网络丢响应幂等重放。两轮之后仅UI补排序单位/待定位，旧输入哈希保留，最终UI由新展示壳收据覆盖；Java/语料/DSL/实验输入未变。
- [真实展示壳](docs/framework-review/20261021-f11-pagination/shell-review.json)12组尺寸/主题、79次真实API操作，三模式完整分页、5页/末页/空集、改城市关闭旧轮并从第一页开始；所有卡片ID/名称/分元/排序单位/待定位/评分/完整sort、页序/hasNext、条件/DSL/DTO一致。真实ES上下文失效410、缺索引502/重导、ES停机503/同Java进程重启恢复，错误清空旧卡片/页序；主题重载/实际Tab通过，浏览器直接ES请求0。最终16PNG均实际查看，范围与SHA逐张记录，数字另由DOM/API逐项对照。
- 图解：官方D2v0.9.0/dagre/主题4、201，2源/4SVG，fmt/validate/生成及CLI/图源/产物哈希通过，[生成收据](framework/diagrams/f11/generation.json)。实线表示受控实验/成功阶段，独立PIT或失效卡片靠隐形边纵向排版，未暗示转换/必然先后。无Archify/机制播放器，对应门禁不适用。
- [HTTP与视觉](docs/framework-review/20261021-f11-pagination/README.md)：本课12组、F10/目录24组必要回归、独立图16组；16锚点/组、11折叠/组、14段真实剪贴板逐字核对、图同步/实际弹窗、主题重载、独立已读/取消/旧键隔离、实际Tab、file双主题/reduced motion通过。最大880px/边界差≤1px/整页无横溢，代码表格局部可滚。26PNG均实际查看；Java截图仅初始横向位置可见左部，未冒充全文视觉核对，片段同步/剪贴板补足。320px图完整可展开。
- 作者失败与修正保留在[attempts](docs/framework-review/20261021-f11-pagination/attempts/README.md)：初次写文件工作目录错误、缺TotalHitsRelation导入、原生重复close404、HTML占位符误伤README链接、单位断言Python0.0与JS0字符串误判，修复后重跑相应检查。当前入口无法设置或核验实际xhigh，作者自审、无独立代理；没有把提示词当运行配置。
- 最终站点/片段/JS/Python/Bash/JSON/SVG/NDJSON/图源、截图和运行输入哈希/差异检查分别记录。未测试随机并发更新/负载/性能、多节点故障/TLS/权限/插件/DB/CDC，执行超时/部分分片失败仅代码防护，F04–F06旧受阻状态不回填。结束前本课索引open_contexts=0，点名删除确认404，Java正常关闭，框架ES恢复开始前停止状态；保留持久卷与源码篇节点。[资源恢复](docs/framework-review/20261021-f11-pagination/workspace-state.json)。按持续授权提交推送origin/main，交付核对实际远端。

## 2026-10-21 · F10 显式排序：三模式、缺值与两轮实连通过

- 只实施F10与必要F09下一课/目录/工程/当前摘要，提示词转F11；未实施分页/PIT或其他课。正文约4401汉字（不含代码），七段式/880px/双主题/复制/独立已读保留；3案例、23条教学HTTP请求=准备6+模式4+边界6+Java7，点名清理1/探活/作者附加断言/浏览器重复另计，2静态D2、6练习、0播放器。[正文](framework/f10.html)、[本机入口](projects/travel-search/labs/f10/README.md)。
- 教学与勘误：完整继承F09十六份字段和值，全国/不选主题/无半径，query保留CNY/open/非负价/预算。三模式共同9候选，相关性exhibit→tea→guide开头，价格两个免费西湖开头，距离guide/plain/xihu同距按ID；每种显式首键后唯一keyword业务ID升序。原F07–F09显式ID不是默认相关性；track_scores不是额外sort键，排序不等于召回/改价，单位分/元/km分开；固定视图内全序不保证更新中跨请求分页稳定。4份目标源码与官方v9.4.0逐字节一致，[内容自审](docs/framework-review/20261021-f10-sort/content-review.json)。
- [真实ES/Java两轮](projects/travel-search/review/f10/README.md)：原Compose ES9.4.0/Lucene10.4.0，独立tut-f10-attractions每轮创建/green/完整mapping/Bulk16项created/refresh/count，七组REST↔Java逐项完整ID次序/total/relation/精确DSL/conditions/价格/分数/原始sort/hasLocation/distanceKm；清理404及Java502后重做。另default评分降序但不承诺同分ID、km/m完整值对照、3km过滤变5份；四ID独立去预算range，缺价_last哨兵2147483647/补0反例与_source不变，主查询不允许缺价；无半径时缺坐标仍命中，sort返回字符串Infinity，展示待定位。每轮11种非法输入400，另NaN/Infinity及坐标下界5种400通过。
- Java保持Boot4.0.8 / Temurin25.0.4.1+1 / 官方Java与Rest5 Client9.4.8 / Wrapper3.3.4、Maven3.9.11；实际clean package与依赖树通过，无单元测试。新增/api/attractions/sort-search与/f10.html，F07–F09契约与代码保留。[真实展示壳](docs/framework-review/20261021-f10-sort/shell-review.json)12组尺寸/主题、24次真实搜索，所有卡片/排序值/分元/km/评分/待定位与DTO一致，城市/预算/空集、502清空旧卡片/重导、ES停机503/同Java进程重启恢复、主题重载/实际Tab通过，浏览器直接ES请求0。11张PNG实际查看10张，另1仅生成；长图数值由DOM/API逐项核对补充，不冒充全文视觉逐字核验。
- 图解：官方D2v0.9.0/dagre/主题4、201，2源/4SVG，fmt/validate/导出及CLI/图源/产物哈希通过，[生成收据](framework/diagrams/f10/generation.json)。纵向卡片比较独立模式和不同缺值前提，隐形边不表示时间顺序；双主题离线资产。无Archify/机制播放器，其门禁不适用。
- [HTTP与视觉](docs/framework-review/20261021-f10-sort/README.md)：本课12组、F09/目录24组必要回归、独立图16组，16锚点/组、14折叠/组、16段真实剪贴板逐字核对；双图同步/实际弹窗、主题重载、独立已读/取消/旧键隔离、实际Tab、file双主题/reduced motion通过。最大880px/左右边界差≤1px/整页无横溢，代码/表格局部可滚。26PNG实际查看20、另6仅生成，逐张SHA与审阅范围保留；Java截图右侧需局部滚动，未声称视觉读完所有长代码，片段同步及剪贴板补核。
- 作者失败与实际观察：[原记录](docs/framework-review/20261021-f10-sort/attempts/README.md)保留。F10目录漏card类导致已读徽标失败，修正后重跑；过快前课导航取消SVG请求，等待加载完成后无失败；静态链接检查早于恢复收据写入，完成证据后重跑。依赖树过滤误用Rest5 group，改co.elastic.clients核对9.4.8，非依赖降级。ES探活刚恢复后曾首次搜索仍503，随后同Java进程重试成功；最终脚本记录允许的重试，不将HTTP就绪当业务立即恢复保证。当前入口无法设置/核验实际xhigh，作者自审、无独立代理。
- 最终站点/片段/JS/Python/Bash/JSON/SVG/NDJSON/图源与运行输入哈希检查通过；真实ES执行超时/部分分片失败/畸形协议仅代码保护，未造故障。未测多节点、并发更新、分页/PIT、性能/评分质量、TLS/权限/插件/DB/CDC；F04–F06历史阻塞不回填。本课索引点名删除，Java正常关闭，框架专用ES恢复原停止状态，持久卷与源码篇节点保留。[资源恢复](docs/framework-review/20261021-f10-sort/workspace-state.json)。按持续授权提交推送origin/main，交付核对实际远端。

## 2026-10-20 · F09 聚合与筛选计数：两轮实连、分片候选误差与阅读通过

- 只实施F09与必要F08下一课/目录/工程及当前摘要，提示词转F10；没有实施排序切换或后续课。约4926正文汉字（不含代码），七段式/880px/双主题/复制/独立已读保留；3案例、28条教学HTTP请求=准备6+范围2+主搜索5+Java5+双分片10，清理2/探活/作者额外校验/浏览器重复另计，2静态D2、6练习、0播放器。[正文](framework/f09.html)、[本机入口](projects/travel-search/labs/f09/README.md)。
- 教学与勘误：F09明确切换全国浏览，移除F08杭州固定半径，CNY/open/非负价格/预算仍在query；保留F08十五份所有已有字段值，补themes并加上海对照，共16份。共同候选9、HZ+lake或culture命中4、城市栏保留主题范围6、主题栏保留城市范围7；筛选项计数不代表点击后总数/新增数。同维OR/跨维AND、filter子聚合不能恢复query排除文档、多值重叠/缺主题、range含from不含to、分页窗口/文档数/业务实体数分别解释。4份目标源码与官方v9.4.0逐字节一致，[内容自审与依据](docs/framework-review/20261020-f09-facets/content-review.json)保存。
- [真实ES/Java两轮](projects/travel-search/review/f09/README.md)：原Compose ES9.4.0/Lucene10.4.0；每轮两个独立索引创建/green/mapping/Bulk16及20项created/refresh/count，最后点名清理确认404再重做。五组REST↔Java逐项精确DSL、conditions、完整ID次序/total/relation、价格/主题、每个分支范围/桶/逐桶及整体误差/sum_other/缺值/range；另all-query/post-only、size2/0、九种非法输入400和缺索引502通过。单节点双主分片routing=a/b确认shard0/1，小候选返回A5（整体上界10、桶上界5、实际少1），宽候选C8/其他12，全桶C8/A6/B6；误差上界与最终桶截断分开验证。
- Java保持Boot4.0.8 / Temurin25.0.4.1+1 / 官方Java与Rest5 Client9.4.8 / Wrapper3.3.4、Maven3.9.11；实际clean package与依赖树通过，无单元测试。新增/api/attractions/facet-search与/f09.html，原F07/F08契约与实现保留。[真实展示壳](docs/framework-review/20261020-f09-facets/shell-review.json)12组尺寸/主题、20次真实浏览器→Java→ES搜索，所有选项计数/范围/缺主题、卡片/价格/主题/range、观察DSL/DTO一致；多选、重叠、空数组、100元边界、火星空集、502清空卡片与数字/同进程重导恢复、主题重载/实际Tab通过。直接浏览器ES请求0。10PNG中8张全图实际查看、2张仅生成；长图未逐字视觉检查的数字由DOM/API比较补充。
- 图解：官方D2v0.9.0/dagre/主题4、201，2源/4SVG，fmt/validate/生成/哈希通过。[生成收据](framework/diagrams/f09/generation.json)。截图发现第一版手机标签过小、重命名残留small节点，改源重写纵向范围卡片与候选流程后重新生成；手机预算输入框同步改为整行。原问题图源/截图/矩阵保留，最终重跑阅读与展示壳，无手改SVG。无Archify/机制播放器，其门禁不适用。
- [HTTP与视觉](docs/framework-review/20261020-f09-facets/README.md)：本课12组、F08/目录24组必要回归、独立图16组，16锚点/组、11折叠/组、17段真实剪贴板逐字核对；主题重载/图同步/实际弹窗/独立已读与旧键隔离/实际Tab/file双主题/reduced motion通过。最大880px、边界差≤1px、无整页横溢，代码/表格局部可滚。26PNG中18全图、4张top1000px裁切实际查看，4张仅生成；逐张状态/哈希保留，长代码未冒充全文视觉审阅。
- 作者观察/失败记录：shard_size恰好3时桶计数已完整，但上界仍可正，正式宽候选设4；首次D2保留字导致导出失败，修名后宽替换残留small节点由截图抓出；首次静态检查早于证据写完且引号转义与同步器格式不同，规范化后重查。当前入口无法设置或核验实际xhigh，作者自审、无独立代理；没有把提示词当配置。未测高基数成本/并发更新、真实ES执行超时/部分分片失败、多节点/TLS/权限/插件/DB/CDC；F04–F06原受阻状态不回填。
- 最终站点/片段/语法/JSON/SVG/NDJSON/图源与截图、运行输入哈希/差异检查分别记录。本课两个索引点名删除，Java正常关闭，框架专用ES恢复开始前停止状态，持久卷与源码篇节点保留。按持续授权提交推送origin/main，交付核对实际远端。

## 2026-10-20 · F08 多字段与高亮：两轮实连、安全卡片与阅读通过

- 只实施F08，基于travel-search的F07 Boot4/JDK25工程；历史travel-portal未使用。约4682个正文汉字（不含代码），七段式/880px/双主题/复制/独立已读保留；3案例、15条教学HTTP请求=准备6+字段3+copy/无高亮/空集3+Java3，清理1/探活/作者附加检查/浏览器重复调用另计，2静态D2、6练习、0播放器。[正文](framework/f08.html)、[本机手工入口](projects/travel-search/labs/f08/README.md)。必要F07下一课/目录/当前摘要同步，提示词转F09；没有实施聚合等后续课。
- 教学与勘误：显式区分F07名称OR与本课name-only AND基线；best_fields的AND在每字段内部，权重不保证名称在前，sort仍为ID。普通业务aliases、name.raw多字段、ES别名/同义词分别解释。copy_to复制原值再分析、不改未过滤_source，统一字段AND可跨来源拼词；高亮是附加显示，不能当评分解释或实体识别。4份本地目标源码与官方v9.4.0逐字节一致，[内容自审及依据](docs/framework-review/20261020-f08-multifield/content-review.json)记录版本/因果/答案/限制。
- [真实ES/Java两轮](projects/travel-search/review/f08/README.md)：专用ES9.4.0/Lucene10.4.0、原Compose不改，独立tut-f08-attractions保留原十二份已有值并补两组别名，增加三份对照，共十五份。每轮创建/green/完整mapping/Bulk15项created/refresh/count；名称AND三条，multi西湖完整次序boundary→guide→plain→tea→xihu（均a-hz-），别名钱塘湖仅xihu；copy额外split、原字段无highlight，去高亮同ID同分数，火星空集。REST↔Java逐项精确DSL、条件、ID/次序/总数relation、价格、分数、所有高亮文本段与回退一致；400非法预算、清理404后Java502。每轮末只删除本课索引，初次/重做各轮状态与原始请求响应保存。
- Java沿用Boot4.0.8 / Temurin25.0.4.1+1 / 官方Java与Rest5 Client9.4.8 / Wrapper3.3.4 / Maven3.9.11；clean package与依赖树通过，无单元测试。新增/api/attractions/multi-search与/f08.html，F07原接口/根路径/查询实现保留。ES encoder=html，Java先拆固定mark边界再按段解码，DTO只返回text/matched，卡片按文本节点显示；缺片段回退原文、缺别名/描述明确占位。[真实展示壳](docs/framework-review/20261020-f08-multifield/shell-review.json)12组尺寸/主题、18次真实搜索，所有卡片DOM段/亮色/价格/观察DSL与DTO一致；5→1→0、80元、缺索引502清空旧卡片/重导恢复、主题重载与实际Tab焦点通过。原文img/mark只为文字，无图片/脚本节点/事件执行，浏览器直接ES请求0；8张全图实际查看，长图未逐字视觉核对处由DOM/API逐段比较补充。
- 图解：官方D2v0.9.0/dagre/主题4、201，2源/4SVG，fmt/validate/导出/哈希通过；首图由并排改为上下两条独立路径以改善窄屏标签，布局隐形边不表示数据流，只改图源重新生成。[生成收据](framework/diagrams/f08/generation.json)。无Archify或机制播放器，其门禁不适用。
- [HTTP与视觉](docs/framework-review/20261020-f08-multifield/README.md)：本课12组尺寸/主题、F07/目录24组必要回归、独立图16组，16锚点/组、9折叠/组、12段真实剪贴板逐字核对；主题重载、已读/取消/旧键隔离、双图实际弹窗与同步、file双主题/reduced motion通过。最大880px/边界差≤1px、无整页横溢，代码/表格局部可滚。26张最终PNG实际查看21，另5仅生成，逐张状态/哈希保留；320px图较小但完整可展开。截图发现页头结构/元信息相邻粘连已恢复基线，初始图min-width700已加F08专属规则修复并重跑。
- 作者失败记录保留：Client9.4.8高亮fields须用NamedValue列表而非String/lambda，修正重建；copy_to字符串与ES规范化数组使严格mapping比较失败，统一数组后两轮通过；浏览器验收选择器/折叠区inner_text/主题初始化覆盖存储均为作者工具问题，修正后重跑，无伪造响应。当前根入口无法设置或核验实际xhigh，作者自审、无独立代理；没有把提示词当作运行配置。部分分片失败/ES执行超时/畸形高亮协议异常仅有代码分支，未造故障；未测长字段成本、相关性质量、插件、多节点、TLS/权限或DB/Kafka/CDC，F04–F06历史受阻状态不回填。
- 最终站点结构/片段/JS/Python/Bash/JSON/SVG/NDJSON/图源与截图哈希/差异检查通过。F08索引点名删除，Java正常关闭；框架专用ES恢复本轮开始前停止状态，持久卷与源码篇节点保留。按持续授权提交推送origin/main，交付核对实际远端。

## 2026-10-20 · 一并保存剩余本地草稿

- 按用户“一起提交”的要求，将此前保留的 `.gitignore` 中 `learn-code/` 排除项、F01 health-path D2/浅深 SVG、旧实验注册表、门户静态产物及 `projects/travel-portal` 工程/历史验收记录一起纳入版本管理。`node_modules`、`target`、`dist` 等本机构建缓存继续忽略。
- 门户草稿仍使用 Boot 3/JDK 21，已补充历史说明及缺失的验收说明入口；当前课程继续使用 F07 的 `travel-search` Boot 4/JDK 25 工程，不变更课次完成状态，也不把旧 health-path 计入现行图解验收进度。原 JSON/截图/运行日志保留；旧记录的视觉审阅仍 pending，F01 HTML 哈希已随现行导学变化，其余列出的文件哈希一致。
- 本次实际通过：旧门户 TypeScript/Vite 生产构建、临时目录 lesson 构建与现存 3 产物逐字节比较、JDK 21 Maven clean package（无单元测试）、JS/Python 语法、JSON/XML/SVG 解析、站点结构与片段同步检查。不重跑旧浏览器/Java 健康实验，不将历史证据当成本次验收；具体范围见 [草稿验收说明](projects/travel-portal/review/f01/README.md)。
- 提交前获取远端，main 与 origin/main 一致、无未合并文件；本次保存后按用户授权提交并推送 origin/main，交付核对实际远端提交。

## 2026-10-20 · F07 Java接口与本机展示壳：真实构建、两轮实连与阅读通过

- 先将本地main从2416daf快进到远端4638411（F04–F06三个提交），保留原.gitignore、health-path、framework/experiments、framework/labs、projects/travel-portal草稿；随后仅实施下一课F07与必要F06导航/目录/当前摘要，提示词转F08。约4756中文字、七段式/880px/双主题/进度/复制保留，3执行案例、17条教学HTTP请求=准备6+REST/Java比较6+诊断5，清理/探活/作者附加测试另计；2静态D2、6理解题、0机制播放器。[正文](framework/f07.html)、[本机手工入口](projects/travel-search/labs/f07/README.md)。未推进F08，F04–F06原受阻验收不回填。
- Java增量在projects/travel-search/backend：Boot4.0.8 / Temurin JDK25.0.4.1+1 / 官方Java与Rest5 Client9.4.8 / Jackson3 / Maven Wrapper3.3.4、Maven3.9.11，原样制品/Wrapper下载包SHA256与实际依赖树保留。明确应用JDK与ES bundled JVM不同。展示壳随Boot本机18080同源提供，浏览器→Java→19200 ES，不要求读者开发前端，Pages只承载教程。服务端固定open/CNY、输入校验、完整bool/geo、DTO、真实DSL观察、单例复用与正常close完整交付。
- [ES/Java真实两轮](projects/travel-search/review/f07/README.md)：本机macOS arm64原Compose ES9.4.0成功运行，不改二进制/安全策略。新tut-f07-attractions继承F06十二份资料与mapping，独立创建/Bulk十二项created/refresh/count、点名清理404后重做；200元F/B/A、80元B/A、火星空集的完整ID次序、价格/币种/状态、total/relation、conditions及序列化DSL与REST逐项一致。每轮八种非法输入400（含小数分），另核缺索引502；ES停止时Java health200/search503，重启ES后同一Java进程/Client恢复三ID。实际clean package与依赖树通过，无单元测试，不用构建成功代替执行验收。
- [真实本机展示壳](docs/framework-review/20261020-f07-java/shell-review.json)：1920/1440/1024/768/390/320×浅深12组，200元/80元/空集/1km/还原逐次真实调用Java，DOM卡片ID/价格、条件/DSL/响应逐项一致；主题重载、实际Tab焦点和无整页横溢通过。另做ES真实停机/503清空旧卡片/同进程恢复，浏览器直接访问ES请求0。7张原PNG：4张全图实际查看，另外3张查看顶部1500px可读裁切，4张全图中另2张也放大裁切核对；未单独视觉审阅的下方长JSON以DOM/API解析对照，范围如实列出。
- 图解：官方D2 v0.9.0/dagre/主题4、201，2源/4SVG，fmt/validate/生成与哈希通过；只改.d2生成，没有手改SVG。[图源/命令/哈希](framework/diagrams/f07/generation.json)。无Archify/机制播放器，其门禁不适用。
- [HTTP与视觉](docs/framework-review/20261020-f07-java/README.md)：12组课页、F06/目录24组必要回归、独立图16组、17锚点/组、10折叠/组、14段真实剪贴板逐字核对、已读/取消/旧键隔离、双图同步/真实展开、file双主题/reduced motion通过；最大880px、边界差≤1px、无整页横溢，长代码/表格局部可滚。26PNG实际查看20，其余6仅生成，逐张状态/哈希保留；JS/HTTP/请求失败/教程业务请求0。
- 教学纠偏/工具修正：依赖树发现Boot把Rest5管理为9.2.9，改elasticsearch-client.version统一到9.4.8后重建并重跑两轮。REST原term简写与Java完整value对象语义相同但作者严格JSON比较失败，统一完整写法；重启探测补捕RemoteDisconnected、展示壳主题脚本不再每次重载覆盖存储，均为作者验收工具问题，失败记录保留。输入小数分显式拒绝，health仅进程、正常空集与400/502/503分开，ID排序不是推荐排名。[内容自审](docs/framework-review/20261020-f07-java/content-review.json)。
- 当前入口无法设置/确认实际xhigh，作者自审，无独立代理。真实分片部分失败/ES执行超时只有代码分支，未造故障实测；未运行多节点、插件、TLS/权限、DB/Kafka/CDC或性能。本课索引已点名删除，Java已正常关闭；专用ES恢复本轮开始前的停止状态，持久卷与源码篇节点保留。站点结构、片段/JS/Python/Bash/JSON/SVG/NDJSON、图源哈希与差异检查通过；按持续授权提交推送origin/main，交付核对远端。

## 2026-10-15 · F06 bool 与组合筛选：正文交付，真实执行受阻

- 仅实施F06与必要的F05下一课、目录/工程/当前摘要，提示词转F07。约4400中文字，七段式、880px、双主题/复制/已读保留。A–E完整继承，F–L新增边界；独立tut-f06-attractions，3案例、22条教学HTTP请求（清理另1，探活/作者读取另计）、16组搜索、2静态D2、6练习、0机制播放器。[正文](framework/f06.html)、[实验](projects/travel-search/labs/f06/README.md)。未实施Java、展示壳或后续课次。
- 教学：name OR + HZ/CNY + gte0/lte20000 + 明确open + lat/lon/3km/arc，预测12→11→7→5→3，最后A/B/F；20000/20001分、免费0/缺价/null、缺状态/无坐标/半径外均有对照。must_not offline会放入K，不等于明确open；同层should无must/filter默认1，有则默认0，显式1恢复门槛；主查询短语可选/必选、filter-only零分分别解释。固定版本9份目标源码已读与哈希保留，16集合独立简单汉字/球面模型核对；不冒充API、距离实测、具体BM25/排名或性能承诺。[内容自审](docs/framework-review/20261015-f06-bool/content-review.json)。
- [真实ES状态](projects/travel-search/review/f06/README.md)：本轮重新启动原Compose，ES9.4.0仍因缺少/proc/self/coredump_filter在HTTP前退出1、OOMKilled=false，curl exit7；两轮作者脚本实际预检连接拒绝，成功F06 API=0、完成轮数=0。保留本次启动时间后的日志、状态、原始验收退出码/stdout/stderr及输入哈希。未改ES二进制、读者Compose或云安全策略，未借旧课响应通过；提供原样请求、完整投影/ID/总数/零失败与分数性质断言、每轮末点名清理后重做。
- 图解：官方D2 v0.9.0/dagre/主题4、201，2源/4SVG，fmt/validate/生成与哈希通过。实际截图发现should末节点长标签落在框外，缩短图源后重新生成、完整重跑HTTP并复查，已修正；两张问题图单独保留，不手改SVG。[生成记录](framework/diagrams/f06/generation.json)、[视觉修复](docs/framework-review/20261015-f06-bool/visual-fix/record.json)。无Archify/机制动画，其门禁不适用。
- [HTTP与视觉](docs/framework-review/20261015-f06-bool/README.md)最终通过12组尺寸/主题、17锚点/组、13折叠/组、13段实际复制；F05/目录24组必要回归、独立图16组、双图实际弹窗。列最大880px、边界差≤1px、无整页横溢；主题/重载/实际Tab/旧进度隔离/reduced motion通过，JS/HTTP/请求失败与业务请求均0。26张最终PNG全部实际查看并核对哈希；320px图较小但完整可展开。file://受管理策略拒绝，离线未验证，不以HTTP替代。
- 结构/片段/语法/JSON/SVG/12对NDJSON及末尾换行/请求覆盖/预测模型/D2哈希/差异检查通过。当前根入口无法设置或确认实际xhigh，作者自审，无独立代理。按持续授权提交推送origin/main，交付核对远端；真实ES待验收与可阅读状态分开记录。

## 2026-10-15 · F05 名称关键词、精确条件与短语：正文交付，真实执行受阻

- 仅实施F05与必要的F04下一课、目录/工程/当前摘要；下一课提示词转F06。保留七段式、880px、双主题、复制与已读。约4300中文字，3案例、22条教学HTTP请求（清理另1条，探活/作者读取另计）、2静态D2、6练习、0机制播放器；没有Java、展示壳或插件。五份资料/正确mapping逐字继承F04，在独立tut-f05-attractions准备，不依赖F04已运行。[正文](framework/f05.html)、[实验](projects/travel-search/labs/f05/README.md)。
- 教学：name的standard单字token与position、_source原文；term完整词项/默认match OR/AND；城市HZ与hz、name.raw部分/完整值；AND逆序与slop=0正序/逆序/长短语。13组预测集合逐组手算、3次分析预测与固定v9.4.0/Lucene10.4.0目标源码核对，不冒充API响应。纠偏：B的OR命中来自name中的湖而非description；term可查text已有词项，match也可用于keyword；AND不管词序、phrase不保证完整原文相等；名称命中不能代替城市/价格/状态条件。[内容自审](docs/framework-review/20261015-f05-keywords/content-review.json)。
- [真实ES状态](projects/travel-search/review/f05/README.md)：原隔离Compose本轮重试，9.4.0仍在HTTP前因缺少/proc/self/coredump_filter退出1、OOMKilled=false，curl exit7；作者验收实际运行记录blocked_before_http，成功F05 API为0、完成轮数0。提供原样脚本两轮断言/原始失败保留及点名清理；未修改ES二进制、读者Compose或云安全策略，未借F03/F04旧响应认定通过。
- 图解：官方D2 v0.9.0/dagre/主题4、201，2源/4SVG，fmt/validate/导出/哈希通过；只改图源重新生成，未手改产物。纵向图桌面/手机均完整，展开可用；无Archify或机制动画，其门禁不适用。[生成记录](framework/diagrams/f05/generation.json)。
- [HTTP与视觉](docs/framework-review/20261015-f05-keywords/README.md)通过12组尺寸/主题，16锚点/组、10折叠/组、15段真实复制；F04/目录24组回归、独立图16组；列最大880px、边界差≤1px、无整页横溢。主题/重载/键盘焦点/旧进度隔离/双图弹窗/reduced motion通过，JS/HTTP/请求失败与业务请求均0。26PNG全部实际查看；file://被管理策略拒绝，离线未验证。静态结构/片段/语法/数据/预测手算/D2哈希/差异检查通过；根入口无法设置/确认实际xhigh，作者自审，无独立代理。按持续授权提交推送origin/main，交付核对远端。修复紧邻F04日志遗留的字面+前缀，仅修Markdown排版、未改历史结论。

## 2026-10-15 · F04 字段设计与 Bulk：正文交付，真实执行受阻

- 仅实施 F04 与必要的 F03 下一课、目录/工程/当前计划摘要，下一课提示词转 F05。保留七段式、880px、双主题、复制、已读和点名重做。五份 F02 景点的业务字段不变，新增教学日期/坐标；3 案例、28 条教学 HTTP 请求（清理另1条，探活/作者读取另计）、2 静态 D2、6 道练习、0 机制播放器。
- 内容：text/keyword/name.raw 与 _source；整数分/币种、strict_date、geo_point、缺值/null/0；显式/动态/strict 与 coerce=false；NDJSON 行与末尾换行、Bulk 条级错误、只修 B/E、固定 ID 完整重导入；边界反例与新索引修复。预测3→5→5明确标注，未伪造响应或借 F03 实测通过。金额非负/状态枚举/必填仍需业务校验，完整重导入不会自动删除旧 ID。[内容自审](docs/framework-review/20261015-f04-model-bulk/content-review.json)。
- [真实 ES 状态](projects/travel-search/review/f04/README.md)：Docker/本地镜像可用，但原 Compose 启动 ES 9.4.0 退出1、OOMKilled=false，缺少 /proc/self/coredump_filter；HTTP未建立，F04写入/两轮均未执行。固定 v9.4.0 启动源已核对，普通文件挂载尝试被 OCI proc 检查拒绝，未修改安全策略/ES二进制/读者Compose。提供作者两轮验收脚本与预测，启动错误与脚本实际失败保留，不能将API标为通过。
- 图解：官方 D2 v0.9.0/dagre/主题4、201，2图源/4SVG，fmt/validate/生成通过，命令/哈希保留。截图发现末节点标签过宽被排在框外，缩短图源后重新生成复查；没有手改 SVG。[图源记录](framework/diagrams/f04/generation.json)。无 Archify，其原生门禁不适用。
- HTTP阅读通过12组尺寸/主题、17锚点/组、10折叠区/组、16段真实复制，F03/目录24组必要回归，独立两图16组；列最大880px、无整页横溢，错误/业务请求均0。26PNG实际查看22张，其余4张只生成。file://被管理策略拒绝，离线未验证；补测减少动态效果与F01–F03进度隔离通过。结构/片段/语法/数据/哈希/差异检查通过，完整结果见 [F04验收](docs/framework-review/20261015-f04-model-bulk/README.md)；HTTP与file状态分别记录，不能相互替代。当前根入口无法设置/确认实际xhigh，内容为作者自审，无独立代理。Java/展示壳、插件、多节点、DB/Kafka/CDC均不在本轮范围。

## 2026-10-15 · 完成 F03 本机运行与第一次真实搜索

- 本轮于 10-14 开始、10-15 完成交付检查，只实施 F03 与必要相邻导航/摘要，不推进 F04–F45。约 4400 中文字，七段式、880px/双主题、目录/已读/复制与点名重做保留；3 执行案例、12 条主流程 HTTP 请求、2 静态 D2、5 道练习、0 机制播放器。正文讲清 ES 运行层次、方法/资源路径、空索引与文档、mapping、固定 ID、refresh/search、mapping/count/GET 与错误恢复，F07 才引入 Java 和展示壳。
- 新资源 `tut-f03-attractions`，配套 data/search/labs/review/f03；案例 f03-c01/c02/c03 用 migrated_from 指向历史 f01-c01/c02/c03。复用隔离 Compose / 19200 / ES 9.4.0 / 1 主 0 副本 / 无认证 / 持久卷，不改历史 HTML、实验输入或原始验收。源码篇 9200/9201 不复用。
- [真实 ES 验收](projects/travel-search/review/f03/README.md)：三个案例各首次/点名清理后两轮通过。空搜索 total=0；首次 created/version=1，显式 refresh 后 total=1/eq、命中 a-hz-xihu 与四字段；mapping/count/GET、错误端口/停机 curl exit=7、持久恢复后同文档、重复创建 HTTP400、覆盖 updated/version=2/count=1。完整原始输出/选字段摘录/镜像 digest/环境/输入哈希保留；补核恢复与覆盖后的完整 _source 和 count 零分片失败。最终本课索引不存在、专用容器停止、卷保留。
- 图解：2 D2 / 4 浅深 SVG，官方 v0.9.0/TALA/主题4、201，fmt/validate/生成通过；[命令与哈希](framework/diagrams/f03/generation.json)。纵向图在正文列内完整显示，双主题与展开同步；只改图源生成，未手改 SVG，字体许可保留。无 Archify，其原生门禁不适用。
- 教学纠偏/勘误：旧课 Java F02、更新/可见性 F03 和分析链课号迁入后分别对齐 F07/F12/F13–F17；旧记录不覆写。提交前移除覆盖摘录误带的早期空搜索对象，仅保留真实覆盖与计数，并完整重跑HTTP。等待器为90次有界探测，不再声称总时长最多180秒。新增空索引查询将11条主流程改12条；额外11次对照/清理尝试含2次连接失败，探活重试另计。显式区分 green/业务命中、HTTP200/健康等待超时、curl退出码/HTTP错误、_id/业务字段、同ID替换/局部更新、手工模型/真实分析评分、refresh/备份；[内容自审](docs/framework-review/20261014-f03-first-search/content-review.json)。
- [HTTP 与视觉](docs/framework-review/20261014-f03-first-search/README.md)通过：/es_web/ 下1920/1440/1024/768/390/320×双主题12组，阅读列最大880px、边界差≤1px、无整页横溢；每组17锚点与9折叠区，22段代码实际剪贴板逐字一致，Tab焦点、主题/进度重载、旧键隔离、F02↔F03/目录导航、双图真实展开、file双主题和reduced motion通过。F02/目录24组必要回归；独立两图1440/1600/1920/2048×双主题16组。最终26 PNG实际查看22张，其余4张只生成，逐张名单/哈希保留；JS错误/HTTP失败/请求失败/业务请求均0。早期作者复制工具的隐藏按钮/innerText与异步等待错误修正后完整重跑，未以工具失败冒充产品缺陷。
- 当前根入口无法设置或确认实际 xhigh，作者与内容自审不能声称已切换；本轮无独立审阅代理。未运行 Java/Boot、插件、多节点、数据库/Kafka/CDC 或交付展示壳，均不列入F03通过。站点结构、片段一致性、JS/Python/Bash语法、JSON/SVG解析与差异检查通过；本轮代码、图源/产物与验收按持续授权提交推送origin/main，交付核对远端。原工作区 .gitignore、health-path、framework/experiments、framework/labs、projects/travel-portal 保留，不纳入提交。

## 2026-10-14 · 完成 F02 数据到结果概念推演

- 只新增指定 F02 与配套样本、图解、验收，必要更新 F01 下一课、目录/首页与进度摘要，逐课提示词转 F03；没有实施其他待编写课程或门户。约 5653 中文字，2 个概念案例 f02-c01/c02、1 份正文 JSON、6 道推演题、1 重做折叠区、4 陷阱；0 HTTP 操作、0 机制播放器。保留七段式、880px、双主题、导航、进度与复制。
- 正文沿用 F01 五份教学景点：文档/字段/索引/mapping/_id，手工中文词项与字段倒排，候选 ABCDE，城市 HZ/币种 CNY/≤20000 分/open 留下 AB；手工分数 3/1/3/4/4，相关性与价格对照、同价第二键、分页返回范围；B 8000→22000 分推演写入确认与相关更新可搜索。六题含只查名称、预算边界及新 F 对照，模型与正文表格实际验算一致。
- 图解：2 静态 D2 / 4 浅深 SVG，官方 v0.9.0/TALA/主题4、201，fmt/validate/生成通过；[图源、命令与 SHA-256](framework/diagrams/f02/generation.json)。视觉发现原横向布局/700px 下限裁掉手机图文，已重排窄纵向并解除 F02 图片最小宽度，重新生成后完整重跑；未手改 SVG，图框/图注仍与正文同列，未改 F01 图宽。无 Archify，其原生门禁不适用。
- 教学纠偏/勘误：新课无旧原教程勘误；显式区分手工词项与默认分析器、3+1 与 BM25、候选与命中页、硬条件与评分、索引与倒排、业务 ID 与元数据 ID；写入/实时 GET/搜索可见/数据库同步各自判断，refresh 不承诺固定延迟、磁盘提交或备份。官方资料与固定 v9.4.0 GetRequest 的 realtime=true 已核对，API 未运行；[内容自审](docs/framework-review/20261014-f02-model/content-review.json)。根会话没有推理强度设置/确认入口，F02 作者与自审实际 xhigh 无法确认，没有独立审阅代理，不能把偏好文本当运行配置。
- 实际阅读：[HTTP 与截图记录](docs/framework-review/20261014-f02-model/README.md)通过。/es_web/ 下 1920/1440/1024/768/390/320 × 双主题 F02 共12组、F01与目录必要回归24组，列最大880px、边界差≤1px、无整页横溢，表格局部滚动；14锚点/组、7折叠区、双图同步/真实展开、JSON实际剪贴板、Tab焦点、主题/已读持久化与旧键隔离、F01↔F02/目录导航、file双主题与reduced motion通过。独立两图1440/1600/1920/2048×双主题共16组加载。最终28 PNG实际查看16张，其余只生成；JS错误/HTTP失败/请求失败/业务请求均0。作者脚本早期焦点/嵌套SVG定位失败已记录修复，高元素截图临时隐藏固定顶栏，实际锚点与视口保持顶栏。
- ES/Java执行验收不适用，未运行ES/Java/插件/多节点/数据库/Kafka/CDC，未交付展示壳，不借旧实验记本课通过。结构、片段、JS/Python语法与差异检查通过；按持续授权提交推送本轮图源、产物、页面与记录至origin/main，交付核对远端。原工作区 .gitignore、health-path、framework/experiments、framework/labs、projects/travel-portal 保留，不纳入本轮提交。

## 2026-10-14 · 重写 F01 导学并清理旧编排

- 仅处理用户指定 F01 与配套入口/规范。正文用“西湖 + 杭州 + 200 元预算 + 可游玩”及五份样本解释检索、过滤、相关性/显式排序、聚合；再讲引入 ES 的收益/成本、数据库/Java/ES/网站职责、一份小 JSON、网站学习方式、八阶段完整 45 课和 F12/F22/F45 三个独立检查点。1 导学情境、1 JSON、5 折叠理解题、3 陷阱；没有 Docker/curl/Java 工程样板，执行验收不适用。所有样本/目标结果/未交付网站均标示意。
- 当前入口只保留新路线：F01 可阅读，F02–F45 待逐课实施。清除旧配额与反复出现的旧待办说明，六段旧规划/验收摘要迁到 FRAMEWORK_HISTORY；废弃完整门户 D2/两 SVG/六 PNG/旧夹具脚本与 JSON 共 11 文件从当前目录删除，Git 历史可查，字体许可保留。原工作区门户草稿、health-path 图和 .gitignore 没有修改，不纳入提交。
- 原启动课保存为 framework/f01-startup-legacy.html，技术正文去历史提示后与源提交 af670eb 严格一致；原案例 ID/项目路径/生成记录/ES 与 HTTP 原始 JSON、截图不覆写，迁入 F03 后重新验收。新已读键 f01-v2 与旧 f01 分开，目录显示新进度，保留读/取消和相对路径。
- 图解：两幅新静态 D2 分别解释查询/数据更新路径与八阶段；官方 v0.9.0 / TALA / 主题 4、201，fmt/validate/浅深生成通过，未手改 SVG；图源/命令/哈希见 [生成记录](framework/diagrams/f01/generation-intro.json)。本课无机制播放器或 Archify，原生门禁不适用。
- 教学纠偏/内容校对：先解释 ES 用途与学习路线，再在 F02 推演、F03 运行、F07 接入 Java；保留数据库也能搜索、ES 本身存储数据的边界。明确 DB→ES 同步延迟与 ES 内部近实时可见性分别判断，不承诺固定时限。作者与独立内容审阅实际选 xhigh，45/45 标题、样本与金额单位一致；后续 xhigh 偏好已写协作规范及默认 F02 的逐课提示词。
- 实际阅读验证：HTTP /es_web/ 下 1920/1440/1024/768/390/320 × 双主题，新课/目录/旧页各 12 组无整页横溢，列最大 880px且边界对齐；15锚点/组、主题/双图同步/展开、真实 JSON 复制、五题/八阶段折叠、新旧进度隔离与持久化、首页/目录/旧页导航、file 双主题、reduced motion通过。JS错误/HTTP失败/框架业务请求均0。最终生成18 PNG，根实际审阅11张桌面/手机/对照/大纲/理解题/独立图，范围见 [阅读验收](docs/framework-review/20261014-f01-intro/README.md)。修复图锚点顶栏遮挡后完整重跑；SVG整页截图超时及截取起点是作者工具问题，最终使用元素截图与实际区域。
- 未运行 ES/Java/插件/多节点/数据库/Kafka/CDC，未交付本机展示壳；不把旧实验当作新课完成。node tools/check.mjs、JS/Python语法、片段一致性、文档链接与差异检查通过。按持续授权将本轮页面/图源产物/清理/验收提交推送 origin/main，交付时核对远端提交。

## 进度表(30 课)

| 课 | 标题 | 状态 | 实验 | 动画 | 图解重构 |
|---|---|---|---|---|---|
| ch01 | Elasticsearch 是什么 | ✅ | 11 | 1(近实时) | ✅ 第一章基线 |
| ch02 | 项目结构全景 | ✅ | 2 | — | ✅ 源码导航（2 图） |
| ch03 | 节点启动全流程 | ✅ | 2 | 1(启动八步) | ✅ 启动与生命周期（2 图） |
| ch04 | 插件体系 | ✅ | 2 | — | ✅ 插件边界与注册（2 图，1 路径动画） |
| ch05 | 配置框架 | ✅ | 12 | — | ✅ 配置契约与动态传播（2 图） |
| ch06 | 请求入口层 | ✅ | 17 | — | ✅ REST 路由与响应边界（2 图，2 路径动画） |
| ch07 | 动作框架 | ✅ | 15 | — | ✅ 动作登记与执行边界（2 图，2 路径动画） |
| ch08 | 异步编程模型 | ✅ | 15 | 1(线程池背压) | ✅ 回调与调度边界（2 图，2 路径动画） |
| ch09 | 传输层 | ✅ | 12 | — | ✅ 远程往返与帧契约（2 图，2 路径动画） |
| ch10 | 跟踪一次文档读取 | ✅ | 26 | 1(realtime GET·9 步) | ✅ GET 旅程与读取视图（2 图，2 路径动画） |
| ch11 | 映射系统 | ✅ | 35 | 1(动态映射·9 步) | ✅ 更新候选与字段结构（2 图，2 路径动画） |
| ch12 | 摄取管道 | ✅ | 48 | — | ✅ 摄取写入与失败恢复（2 图，2 路径动画） |
| ch13 | 批量写入 | ✅ | 40 | 1(bulk 分组·6步) | ✅ 分组结果与写入等待（2 图，2 路径动画） |
| ch14 | 存储引擎 | ✅ | 46 | 1(写入全路径·8步) | ✅ 写入顺序与提交边界（2 图，2 路径动画） |
| ch15 | 索引分片 | ✅ | 40 | 1(路由公式·7步) | ✅ 路由碰撞与本地生命周期（2 图，2 路径动画） |
| ch16 | 搜索流程总览 | ✅ | 29 | 1(Query Then Fetch·旗舰) | ✅ 两阶段职责与分页窗口（2 图，2 路径动画） |
| ch17 | 搜索服务与搜索上下文 | ✅ | 32 | 1(上下文生命周期) | ✅ 执行上下文与保留读者（2图，2路径动画） |
| ch18 | 查询语法 | ✅ | 34 | 1(match→SHOULD) | ✅ 查询翻译与收集边界（2图，2路径动画） |
| ch19 | 聚合框架 | ✅ | 30 | 1(cherry/shardSize) | ✅ 收集归并与候选误差（2图，2路径动画） |
| ch20 | 评分与排序 | ✅ | 30 | 1(BM25 演算·旗舰) | ✅ 评分窗口与解释入口（2图，2路径动画） |
| ch21 | 集群状态 | ✅ | 29 | — | ✅ 快照职责与发布应用（2图，1路径动画） |
| ch22 | 主节点选举与共识 | ✅ | 18 | 1(选举时序·旗舰) | ✅ 选举资格与提交边界（2图，2路径；API/原生浏览器限制见日志） |
| ch23 | 分片分配 | ✅ | 33 | 1(均衡迁移·旗舰) | 已重构：2交互图/2路径动画；API与原生浏览器受限，见日志 |
| ch24 | 分片恢复与快照 | ✅ | 57 | 1(peer recovery·旗舰) | 已重构：2交互图/2路径动画；API与原生浏览器受限，见日志 |
| ch25 | 熔断器与背压 | ✅ | 29 | 1(熔断水位·旗舰) | 已重构：2交互图/2路径动画；API与原生浏览器受限，见日志 |
| ch26 | 脚本引擎 | ✅ | 45 | 1(编译旅程) | 已重构：2交互图/2路径动画；API与原生浏览器受限，见日志 |
| ch27 | 管道查询语言 | ✅ | 42 | 1(管道执行) | ✅ 管道计划与AVG中间态（2图，2路径动画）；API两轮通过 |
| ch28 | 索引生命周期管理 | ✅ | 40 | 1(受控 rollover·7步) | ✅ 两种时钟与相缓存（2图，2路径动画）；API两轮通过 |
| ch29 | 安全机制 | ✅ | 32 | 1(认证与授权·7步) | ✅ Basic入口与RBAC动作边界（2图，2路径动画）；API两轮通过 |
| ch30 | 全景回顾与方法论 | ✅ | 20 | 1(职责与证据·7步) | ✅ 搜索职责与阅读验证（2图，2路径动画）；API两轮/原生浏览器通过 |

转写状态与图解重构分别统计；重构已完成不代表真实 ES 实验或技能原生浏览器检查全部通过，具体结果见会话日志。

## 勘误表(tutorial 原文 → 网页修正)

| 课 | 原文说法 | 修正 | 依据 |
|---|---|---|---|
| F27（目录同步） | 目录徽标仍写F01–F21可阅读，观察页摘要停在F09 | 当前可阅读范围同步为F01–F27，观察页摘要覆盖F08–F27；F28仍待编写 | [目录](framework/index.html)、[当前摘要12组复验](docs/framework-review/20261027-f27-ranking/directory-current-summary.json) |
| F07（本轮实现校对） | 只锁Java Client9.4.8，Boot仍可把底层Rest5管理成9.2.9 | 同时覆盖Boot的elasticsearch-client.version为9.4.8，保存实际依赖树并重新构建/两轮实连；health进程正常不代表搜索就绪 | [依赖树](projects/travel-search/review/f07/dependency-tree.txt)、[真实两轮](projects/travel-search/review/f07/README.md) |
| F04（新课教学边界） | 把 strict 当业务校验、HTTP200当整批成功、固定 ID 重导入当自动集合替换 | strict只拒绝未知字段；Bulk逐项判断；index完整替换同ID且不自动删缺席的旧ID；预测与实际执行分开记录 | [F04正文](framework/f04.html)、[固定数据与脚本](projects/travel-search/labs/f04/README.md)、[执行受阻](projects/travel-search/review/f04/README.md) |
| F03（历史启动课迁移） | 旧课将 Java 放 F02、更新/可见性放 F03；等待脚本最多180秒；主流程11请求 | 当前 Java F07、更新/可见性 F12；等待器90次、每次curl≤2秒且失败后等待2秒，不承诺180秒总上限；新增空索引搜索后主流程12请求，原存档保持历史口径 | [F03 正文](framework/f03.html)、[两轮新实测](projects/travel-search/review/f03/README.md)、[wait.sh](projects/travel-search/infra/single-node/wait.sh) |
| ch07 | 未知路由(如 `GET /_cat/actions`)回 404 | 9.4.0 回 **400** `no handler found for uri [...]`;404 留给「路由命中、资源不存在」 | 本地 9.4.0 实测 |
| ch07 | 缺 id 的 `GET /{index}/_doc/` 在 PathTrie/REST 层被拒(404/缺参) | 实测 **405** `Incorrect HTTP method … allowed: [POST]`——尾斜杠归一后命中的是 POST 自动生成路由,属方法不匹配 | 本地 9.4.0 实测 |
| ch09 | `GET /_cat/transport` 当前是 404 | 同上口径:未知路由回 **400**(与 ch07 相互印证) | 本地 9.4.0 实测 |
| ch09 | 暗示单节点本机环回仍计传输层 rx/tx | 建索引+写入+GET 后 server_open/rx/tx **全 0**,本地路径不产生传输层记账 | 本地 9.4.0 实测 |
| ch08 | (线程池数字全面核对,无勘误) | search=((N*3)/2)+1、queue=size×1000、write=max(N*750,10000) 等逐项吻合 | 本地 9.4.0(N=12)实测 |
| ch06 | 原转写未形成完整代理报告 | 本轮按固定 v9.4.0 源码完成入口边界校对；详细勘误见下方第六章表 | [.archify/CH06-REVIEW.md](.archify/CH06-REVIEW.md)；本轮 API 未实测 |
| ch10 | 「RestGetAction 一共 76 行」属版本易变数字(非错误) | 网页写「不到百行」不写死;另实测确认 `?refresh=true` 在默认 realtime 下被无视,需配合 `realtime=false` 才刷新(已写进实验) | 本地 9.4.0 实测 |
| ch27 | 「`POST /_esql` 会 404」 | 实测 **405** `Incorrect HTTP method ... allowed: [GET, PUT, DELETE, HEAD]`——`/_esql` 撞上裸索引路由 `/{index}`(POST 不在 allowed),非「无 handler 400」更非 404;镜像:`GET /_query` → 405 allowed [POST] | 本地 9.4.0 实测 |
| ch28 | 「新建的 tut-l28-logs-000002 绑定同一策略名」 | 实测 alias 方式 rollover **不复制** `index.lifecycle.name`:000002 settings 无 lifecycle 键、managed=false,链条滚一代即断;正解是 index template 注入 lifecycle settings（可带 mappings/其他别名）；模板重复声明 rollover alias 本体会 ERROR step(duplicated alias) | 本地 9.4.0 实测 |
| ch28 | 课末清理用 `DELETE /tut-l28-*`(通配符) | 默认 **400** `Wildcard expressions or all indices are not allowed`——`action.destructive_requires_name` 默认 true,清理须显式点名;网站将该 400 做成实验(桥接 ch29) | 本地 9.4.0 实测 |
| ch29 | 暗示 401 只带一个 `WWW-Authenticate: Basic realm="security", charset="UTF-8"` | 9.4.0 实测为**双挑战**:`Basic realm="security", charset="UTF-8"` + `ApiKey` 两个响应头 | 本地 9.4.0(9201)实测 |
| ch01/02/20 | tutorial 与网页写 Lucene **10.3.2**、JDK **25.0.2+10**、Netty **4.1.130.Final** | Lucene **10.4.0**、bundled JDK **26.0.1+8**(节点 API 显示 `26.0.1`)、Netty **4.1.132.Final**。Jackson 2.15.0 / Log4j 2.19.0 / ANTLR 4.13.1 与 tag 一致,未改 | [v9.4.0 version.properties](https://github.com/elastic/elasticsearch/blob/v9.4.0/build-tools-internal/version.properties) |
| ch01 | 网页旧文案暗示当前 Lucene 的 StandardAnalyzer 默认去停用词 | ES standard 与 Lucene 10.4.0 无参 StandardAnalyzer 都默认使用空停用词表；显式 stop 才移除 the | [Lucene 10.4.0 StandardAnalyzer](https://github.com/apache/lucene/blob/releases/lucene/10.4.0/lucene/core/src/java/org/apache/lucene/analysis/standard/StandardAnalyzer.java#L50-L53) |
| ch01 | 网页写改主分片数只能 reindex，思考题推断直接改后 GET 找错片 | _settings 直接改 number_of_shards 会被拒，已有 GET 不受影响；满足条件时可 split/shrink 到目标索引，或 reindex。本章公式限定 9.4.0 新建普通非分区路由索引 | [IndexMetadata](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/cluster/metadata/IndexMetadata.java#L222-L239)、[IndexRouting](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/cluster/routing/IndexRouting.java#L147-L175) |
| ch01 | 网页倒排表说明易被理解为默认保存字符 offsets，refresh 默认 1s 被表述为延迟上限 | 默认 text 保存词频和位置、不保存 offsets；高亮可按需存储偏移或重分析。默认刷新间隔是调度周期，不保证可见性时限 | [TextFieldMapper](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/index/mapper/TextFieldMapper.java#L127-L136)、[IndexShard](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/index/shard/IndexShard.java#L4438-L4464) |


| ch02 | 网页依赖箭头写/画为 libs → server → 扩展，生产依赖只有 libs + Lucene | 依赖箭头从使用方指向被依赖方；server 另有 HPPC、HdrHistogram、Log4j/ECS 等生产依赖，模块测试依赖与构建枚举另判断 | [server/build.gradle](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/build.gradle#L30-L96)、[根构建插件依赖注入](https://github.com/elastic/elasticsearch/blob/v9.4.0/build.gradle#L311-L316) |
| ch02 | x-pack 一概称商业功能，libs 一概称不依赖 ES | x-pack 是扩展源码区域，包含 Basic 可用及更高许可等级功能；libs 是仓库内基础库，各有自己的库级和外部依赖 | [XPackLicenseState](https://github.com/elastic/elasticsearch/blob/v9.4.0/x-pack/plugin/core/src/main/java/org/elasticsearch/license/XPackLicenseState.java#L117-L133)、[x-content](https://github.com/elastic/elasticsearch/blob/v9.4.0/libs/x-content/build.gradle#L18-L29) |
| ch02 | SearchPhaseController 放在 search/；放任意 build.gradle 即自动发现项目 | 控制器在 action/search/；addSubProjects 只扫描指定入口，每层需 build.gradle，并有停止和排除条件 | [SearchPhaseController](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/action/search/SearchPhaseController.java#L71)、[settings.gradle](https://github.com/elastic/elasticsearch/blob/v9.4.0/settings.gradle#L128-L167) |
| ch02 | 角色与 JDK 实验预期未注明可配置条件，暗示整个 API 不带构建号 | 角色与 JVM 随配置/环境变化；jvm.version 是 java.version，vm_version 可返回完整 JVM 版本，using_bundled_jdk 标识是否使用捆绑 JVM | [JvmInfo](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/monitor/jvm/JvmInfo.java#L408-L415) |

| ch03 | server-cli 直接 fork 服务器并写 stdin | 9.4.0 由 ServerLauncher 启动 preparer 与 server；ServerCli 生成 LaunchDescriptor，launcher 把 ServerArgs 写进服务器 stdin 并等待 stderr READY | [ServerLauncher](https://github.com/elastic/elasticsearch/blob/v9.4.0/distribution/tools/server-launcher/src/main/java/org/elasticsearch/server/launcher/ServerLauncher.java#L54-L77)、[startServer](https://github.com/elastic/elasticsearch/blob/v9.4.0/distribution/tools/server-launcher/src/main/java/org/elasticsearch/server/launcher/ServerLauncher.java#L269-L325) |
| ch03 | HTTP 打开说明已入群；HTTP 是绝对最后一步，与 READY 同时 | 初始等待默认 30s，超时告警继续、0 跳过；HTTP 后仍有可选 readiness、端口文件及插件回调，启动返回后入口才发送 READY；不能替代集群健康判断 | [Node.start](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/node/Node.java#L374-L452)、[initPhase3](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/bootstrap/Elasticsearch.java#L436-L446) |
| ch03 | localhost / single-node 下所有检查失败只 WARN；只看绑定地址 | 自动强制同时看 Transport bind/publish、snapshot 和发现模式；显式 es.enforce.bootstrap.checks=true 与单项 alwaysEnforce 可另行强制 | [BootstrapChecks](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/bootstrap/BootstrapChecks.java#L113-L197) |
| ch03 | 三态简写、省略 STOPPED；关闭严格逆序、HTTP 必定第一停；CLOSED 等于锁已释放 | 保留四标志与 INITIALIZED 直接 close 分支；STARTED / STOPPED / CLOSED 先变再执行动作。HTTP 较早停，前面仍有其他组件；NodeEnvironment 在 close 后段实际释放锁 | [Lifecycle](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/common/component/Lifecycle.java#L103-L173)、[Node 清理](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/node/Node.java#L462-L629) |
| ch03 | CAT http 是 bind 地址；mlockall=false 就是未配置内存锁 | CAT http 取 HTTP publishAddress；mlockall 报实际锁定结果，false 不能单独反推配置，PID 还可能属于容器命名空间 | [CAT nodes](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/rest/action/cat/RestNodesAction.java#L373-L380)、[ProcessProbe](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/monitor/process/ProcessProbe.java#L122-L124) |

| ch04 | modules / plugins / X-Pack 三分，X-Pack 一概商业；内置模块删目录即可，删除 reindex 后仍能启动且路由 404 | 区分源码区域、发行目录、扩展 API 与许可；X-Pack 含 Basic 与更高等级功能。内置模块有依赖，不保证删除后可启动；9.4.0 无 handler 分支为 400，方法冲突可为 405 | [加载目录](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/plugins/PluginsLoader.java#L134-L164)、[许可](https://github.com/elastic/elasticsearch/blob/v9.4.0/x-pack/plugin/core/src/main/java/org/elasticsearch/license/XPackLicenseState.java#L117-L133)、[无 handler](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/rest/RestController.java#L743-L751) |
| ch04 | 每插件一个相同 ClassLoader，扩展只可见 SPI；不同 Guava 只要不撞 server 就必能启动 | 有模块化、Classic URLClassLoader、Stable 合成模块分支；扩展有独立 SPI 时暴露 SPI，无 SPI 时使用实现层。JarHell 检查本 bundle、核心与扩展传递依赖，其他兼容与运行条件仍适用 | [加载分支与暴露层](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/plugins/PluginsLoader.java#L289-L377)、[JarHell](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/plugins/PluginsUtils.java#L314-L368) |
| ch04 | createComponents 全按对象自身类型绑定，Reindex 仅返回 SSL 与 Metrics 两个组件 | 9.4.0 可返回组件对象、待注入的类和 PluginComponentBinding；Reindex 另有 Update/Delete Metrics 与 relocation picker binding。正文改为按真实装配与生命周期收集解释 | [组件装配](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/node/NodeConstruction.java#L1065-L1100)、[Reindex 组件](https://github.com/elastic/elasticsearch/blob/v9.4.0/modules/reindex/src/main/java/org/elasticsearch/reindex/ReindexPlugin.java#L109-L115) |
| ch04 | Stable 只写“升级友好”，未说明向前与跨 major 限制 | 正常语义版本构建中，Classic 要求描述 ES 版本等于当前版本；Stable 要求同 major 且插件构建目标不晚于运行版本，仍检查 Java 及其他加载条件 | [verifyCompatibility](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/plugins/PluginsUtils.java#L84-L156) |
| ch04 | plugins 数组必为空，POST /_reindex 空对象得到 400 就能证明路由存在 | 数组由各节点安装状态决定；卡片保留节点名及失败数。空对象预期参数验证 400，应核对 action_request_validation_exception 与 reason；无 handler 也可返回 400，不能单凭状态判断 | [Reindex 验证](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/index/reindex/ReindexRequest.java#L97-L115)、[无 handler](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/rest/RestController.java#L743-L751) |

### 第五章重构校对

| 课 | 网页旧说法 | 修正 | 依据 |
|---|---|---|---|
| ch05 | Setting 的 key 在编译期钉死，配置拼错不再是运行时问题 | Setting<T> 给调用方明确类型；配置 key 的注册与合法性仍由运行时框架检查 | [Setting.get](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/common/settings/Setting.java#L556-L592)、[AbstractScopedSettings.updateSettings](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/common/settings/AbstractScopedSettings.java#L869-L889) |
| ch05 | NodeScope “节点 / 集群一份”，作用域表暗示均可 PUT cluster settings | NodeScope 表示集群级或节点文件级范围；不保证节点同值，API 更新另需已注册、Dynamic 及相应权限 / 条件 | [Setting.Property](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/common/settings/Setting.java#L91-L136)、[动态更新条件](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/common/settings/AbstractScopedSettings.java#L860-L889) |
| ch05 | 改主分片数后已有 _id 会找不回来；Final “永远不行” | 原索引的 Final 更新被拒，原值 / 路由不变；关闭索引也拒绝。不同布局可按条件 resize 或 reindex 到新索引 | [IndexMetadata 声明](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/cluster/metadata/IndexMetadata.java#L222-L239)、[Final 检查](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/common/settings/AbstractScopedSettings.java#L860-L889)；resize 条件见第一章已校对依据 |
| ch05 | 收集 Runnable 后统一 run 是所有消费者 / 业务字段的原子更新，不会读到半新半旧 | 准备阶段失败时不开始执行；随后逐个 run，不保证多个字段跨线程原子可见，不提供执行异常后的通用回滚 | [AbstractScopedSettings.applySettings](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/common/settings/AbstractScopedSettings.java#L159-L183) |
| ch05 | transient 重启即还原，适合天然清理 / 先试试 | transient 不持久化，完整集群重启会丢；滚动重启不能当清理承诺。实验采用 persistent 并显式 null 删除本课覆盖 | [Metadata 持久化上下文](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/cluster/metadata/Metadata.java#L744-L750)、[官方 Cluster update settings API](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-cluster-put-settings) |
| ch05 | null 必然恢复代码默认 1000，defaults 等同硬编码默认值 | null 只删除指定层；回退还受 transient / 节点本地设置影响。defaults 由处理 REST 请求节点的 clusterSettings.diff 生成，可含本地配置 | [覆盖合并](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/cluster/metadata/Metadata.java#L1682-L1689)、[RestClusterGetSettingsAction.response](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/rest/action/admin/cluster/RestClusterGetSettingsAction.java#L81-L93) |
| ch05 | Filtered 属性让 API 输出打码 | 相关 SettingsFilter 输出会移除匹配的敏感键，不保证以星号显示 | [SettingsFilter.filterSettings](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/common/settings/SettingsFilter.java#L78-L96) |
| ch05 | 将副本数改为 0 顺带把单节点集群的 yellow 治好 | 本章索引在主分片正常分配等前提下可 green；其他索引可让整个集群仍 yellow，实验限定本章索引并等待健康 | [IndexMetadata 副本声明](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/cluster/metadata/IndexMetadata.java#L234-L239)、[MetadataUpdateSettingsService 副本更新](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/cluster/metadata/MetadataUpdateSettingsService.java#L305-L339)；真实 API 本轮未运行 |

### 第六章重构校对

| 课 | 网页旧说法 | 修正 | 依据 |
|---|---|---|---|
| ch06 | 参数只有普通 `Map<String,String>`，读 param 不区分重复值行为 | 9.4.0 用 RequestParams 保留重复查询值；param 读最后一个值，重复值有专门 API，路径捕获 put 会替换同键 | [RequestParams · get / put](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/rest/RequestParams.java#L186-L209)、[RestRequest 参数读取](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/rest/RestRequest.java#L400-L426) |
| ch06 | 全局 pretty / filter_path 只是 ALWAYS_SUPPORTED 放行，无需被消费 | AbstractRestChannel 构造时已消费 format/filter_path/pretty/human；ALWAYS_SUPPORTED 用于可选白名单，后置消费检查仍有独立规则 | [通道参数消费](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/rest/AbstractRestChannel.java#L56-L64)、[白名单与后置检查](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/rest/BaseRestHandler.java#L76-L122) |
| ch06 | 参数校验都必须放在 prepareRequest 后面，任何子类都不能提前检查 | 后置消费检查在 prepare 之后；可选白名单在之前，fields 显式拒绝在 prepare 之内；RestGetAction 默认白名单为 null | [handleRequest](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/rest/BaseRestHandler.java#L78-L122)、[fields 拒绝](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/rest/action/document/RestGetAction.java#L45-L56) |
| ch06 | 9.4.0 breaker 只预留 contentLength，不再乘 2；大 body 必定在接收前被拒 | Controller 传记账增量，子 breaker 按累计 used × overhead 估算，默认 in-flight overhead 仍为 2.0；非流式 Handler 还可能先聚合 body | [聚合与记账](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/rest/RestController.java#L392-L438)、[overhead 默认值](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/indices/breaker/HierarchyCircuitBreakerService.java#L131-L136)、[limit 估算](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/common/breaker/ChildMemoryCircuitBreaker.java#L152-L188) |
| ch06 | OPTIONS 必须路径有其他方法才 200，浏览器预检总由 RestController 处理 | 普通 OPTIONS 到达 Controller 时无合法方法也可 200，不附 Allow；启用 CORS 的预检可能由外层 CorsHandler 处理 | [无 Handler 分支](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/rest/RestController.java#L516-L539)、[OPTIONS](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/rest/RestController.java#L728-L736)、[CORS 预检](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/http/CorsHandler.java#L93-L127) |
| ch06 | GET 不该带 body，结构化 error.type 说明已进入业务 Handler | 本课文档 GET 不消费完整 body，其他 GET API 可支持 body；结构化错误也可来自 Handler 前的检查或拦截，需结合 reason 判断 | [未消费 body](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/rest/BaseRestHandler.java#L119-L122)、[Handler 前检查](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/rest/RestController.java#L412-L487)、[搜索 GET 注册](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/rest/action/search/RestSearchAction.java#L94-L96)、[搜索 body 解析](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/rest/action/search/RestSearchAction.java#L130-L141) |
| ch06 | _nodes/stats/http routes 能把整棵路由树拍平，计数是本次具体 URL / 方法的记录 | 只返回 requestCount 或 responseCount 大于 0 的模式；同一路径方法 / 版本共享 tracker，各节点累计、含其他流量，不是完整注册表 | [getStats](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/rest/RestController.java#L379-L389)、[共享 tracker](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/rest/MethodHandlers.java#L89-L109) |
| ch06 | 现代 Java 客户端直接构造服务器 GetRequest，共用 NodeClient Action 入口 | NodeClient / GetRequest 是服务器内部边界；现代 Java API Client 通过 HTTP 调用，不能沿用已移除 TransportClient 的模型 | [NodeClient 内部分发](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/client/internal/node/NodeClient.java#L78-L138)；[现代 Java API Client 官方文档](https://www.elastic.co/docs/reference/elasticsearch/clients/java) |
| ch06 | 准备卡依赖自动建索引 / 动态映射，重复运行总是 created | 增加显式一主片零副本索引和 strict mapping；首次 created、重复 updated，点名清理后从创建卡重做；补齐 HEAD 与编码 ID 对照 | 本章注册表与源码校对；真实 API 首次 / 清理后重做本轮未执行 |

### 第七章重构校对

| 课 | 网页旧说法 | 修正 | 依据 |
|---|---|---|---|
| ch07 | _tasks 的 actions 参数默认按前缀匹配 | BaseTasksRequest 调 Regex.simpleMatch；无星号按完整名称相等，加 `*` 才表达通配。列表过滤不执行或检查该动作是否登记 | [BaseTasksRequest.match](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/action/support/tasks/BaseTasksRequest.java#L174-L188)、[Regex](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/common/regex/Regex.java#L202-L217) |
| ch07 | 校验与整条过滤器链始终在入口线程；GET 构造传 GET 池就表示公共入口 fork | 校验与首次过滤在调用线程开始，filter 可异步继续；TransportSingleShardAction 给 TransportAction 传 DIRECT，GET 池用于后续分片执行 | [execute / doExecuteForking](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/action/support/TransportAction.java#L54-L101)、[单分片基类](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/action/support/single/shard/TransportSingleShardAction.java#L84-L134)、[过滤器接口](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/action/support/ActionFilter.java#L27-L62) |
| ch07 | 不调 proceed 就一定使请求永久挂起 | 主动完成 listener 是合法短路；异步 filter 可晚些继续或完成。最终两者都不做才违背完成协议，基类没有自动收尾保证 | [ActionFilter](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/action/support/ActionFilter.java#L27-L62)、[RequestFilterChain](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/action/support/TransportAction.java#L127-L143) |
| ch07 | 未登记动作的 IllegalStateException 总直接抛到调用者 | executeLocally 查表会抛；常用 client.execute 路径由 NodeClient.doExecute 捕获并送入 listener.onFailure。查表发生在 Task 登记前 | [NodeClient](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/client/internal/node/NodeClient.java#L78-L141) |
| ch07 | get_from_translog 也是 ActionType，和本地动作统一登记在同一张表 | 该类声明字符串 NAME，经 HandledTransportAction 登记 TransportService handler；本地 ActionType Map 是 ActionModule 绑定的另一集合，构造远程 handler 不自动加入 Map | [GetFromTranslog](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/action/get/TransportGetFromTranslogAction.java#L43-L53)、[HandledTransportAction](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/action/support/HandledTransportAction.java#L36-L52)、[本地绑定](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/action/ActionModule.java#L1067-L1078) |
| ch07 | mustIncRef 的引用简单理解为保护整个异步业务，到业务结束才释放 | 额外引用在链尾 handler 调用或 listener 短路时 releaseOnce；业务异步持有有自己的协议。TaskManager 包装成功 / 失败回调，先注销再通知上游 | [链引用释放](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/action/support/TransportAction.java#L90-L143)、[Task 清理](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/tasks/TaskManager.java#L195-L247) |
| ch07 | usage 是每次 Handler 调用的完整表，Task 可当动作登记或历史证据 | usage 在 prepare / 后置检查通过后、consumer 前加一，UsageService 只输出正数；_tasks 是运行采样，完成即注销，cancellable 看实现。空列表不能证明动作未登记 | [计数点](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/rest/BaseRestHandler.java#L98-L145)、[正数筛选](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/usage/UsageService.java#L71-L81)、[Task 类别](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/tasks/TaskManager.java#L155-L176)、[完成注销](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/tasks/TaskManager.java#L195-L247) |
| ch07 | 实验只看累计计数与一次任务快照，缺少比较基线和重复语义 | 保留原 9 ID，增 6 卡；显式 mapping / 刷新 / 本课健康检查，GET 前后基线、精确 / 通配对照、完成后 Task 与缺文档。清理点名，重做重新记录 N，注明重复创建 / 写入 / 清理差异 | [experiments/ch07.js](experiments/ch07.js)、[CH07-REVIEW](.archify/CH07-REVIEW.md)；本轮 API 未实测 |
| ch07 | B5 未注册 URL 的 400 预期写成 reason 含 no handler found | 该分支直接生成顶层 error 字符串，没有 error.reason；按 HTTP 状态和 error 字段对照，正文同步增加方法依据 | [RestController.handleBadRequest](https://github.com/elastic/elasticsearch/blob/v9.4.0/server/src/main/java/org/elasticsearch/rest/RestController.java#L743-L753)；复核源码，API 未实测 |

### 第八章重构校对

| 课 | 网页旧说法 | 修正 | 依据 |
|---|---|---|---|
| ch08 | void + listener 必发出后立即返回并换线程，DIRECT 用于尽快离开当前线程 | 异步接口可同步完成；DIRECT / map / wrap 不 fork，耗时工作仍占当前线程 | EsExecutors.DirectExecutorService、SubscribableListener.addListener；固定版本链接见正文 |
| ch08 | rewrite 显式提交到 search_coordination，合并发生在最后一帧回调 | rewrite 的参数是 responseExecutor，已完成订阅可同步接续；results.consumeResult 完成后才倒数，后续调度另查 | Rewriteable.rewriteAndFetch、SubscribableListener.newForked / addListener、AbstractSearchAsyncAction.onShardResult |
| ch08 | doRun 已把每个 shard 都发到网络；单分片也固定两阶段 | 每节点并发限制可暂存待发任务；普通单分片无 rank 可合并 query/fetch，单节点不证明网络往返 | AbstractSearchAsyncAction.performPhaseOnShard、SearchTransportService.sendExecuteQuery |
| ch08 | notifyOnce 保证恰好一次；生产发布包 assertOnce 必不生效 | notifyOnce 只保证至多一次，不保证完成活性；assertOnce 按 Assertions.ENABLED 生效，关闭时直接委托 | ActionListenerImplementations.NotifyOnceActionListener、ActionListener.assertOnce |
| ch08 | search 排满时 write / cluster_coordination 不受牵连；上下文只由线程池保存 | 分池仍共享 CPU / 堆 / 磁盘；任务包装和专门的 listener 包装都可保存上下文 | EsThreadPoolExecutor.wrapRunnable、SubscribableListener.preserveContext；隔离范围正文已限定 |
| ch08 | 默认公式不写取整 / 部署条件，defaults 都是代码默认，改 size 队列随之变 | 限默认自管 9.4.0、N 取向上取整 allocated_processors、整数除法；defaults 可含本地配置，size / queue_size 独立 | EsExecutors.allocatedProcessors、OsInfo.toXContent、DefaultBuiltInExecutorBuilders、FixedExecutorBuilder |
| ch08 | refresh=true 使 refresh 池 completed +1；一次搜索固定增加协调计数，write 必不动 | 刷新是可见性语义；completed 为全节点累计任务，需写后 / 搜索前基线，不作精确归因 | PostWriteRefresh → IndexShard.externalRefresh → Engine.externalRefresh；RestThreadPoolAction |
| ch08 | rejected 必全 0，generic 永不 429，拒绝必直接 throw 且顶层 HTTP 429 | rejected 可含历史；Scaling 不因有界满拒绝不保证整请求不报错；AbstractRunnable 可转 onRejection，顶层 / 部分失败 / 单项状态分别读 | EsThreadPoolExecutor.execute、EsAbortPolicy、EsExecutors.ForceQueuePolicy、ExceptionsHelper.status |
| ch08 | 创建索引即整个集群 green，自动 ID 重复写仍命中 1，清理后 transient 必空 | 显式 mapping / 固定 ID / 健康等待 / 基线；比较本课失败更新前后键，重复运行区分 created/updated，删除不清统计 | 15 卡请求与前提；源码已核对，当前 API 未实测 |

### 第九章重构校对

| 课 | 网页旧说法 / 遗漏 | 修正 | 依据 |
|---|---|---|---|
| ch09 | sendRequest 交出去就立即释放线程，未区分两个 GET handler / Reader | 异步接口可同步接续；主 action 与 get[s] 分工不同，请求查 action、响应查 requestId，DIRECT 入口与 get executor / Reader 分开 | TransportService、InboundHandler、TransportSingleShardAction；固定提交链接见正文与图 |
| ch09 | 所有帧概括为 23B 固定头，length 与可变头范围含糊 | 普通业务帧固定头 23B，length=全帧−6；PING 为 6B，V8 特殊握手有 features；请求 action 在可变头，body 可压缩 | TcpHeader、OutboundHandler、InboundDecoder |
| ch09 | 字符串长度暗示 UTF-8 字节数，错位固定静默发生 | writeString 写 Java char / code unit 数；读写父类、字段、optional 原语与 stream 版本闸门成对，错位可产生多种错误 | StreamOutput.writeString、StreamInput.readString、GetRequest |
| ch09 | 对端各按自己的发行版本读写，握手概括成简单较小版本 / 集群名必等 | 使用协商的 TransportVersion；已知版本 / bestKnownVersion 分支另看，服务层集群名按调用谓词判断，connectionValidator 使用 always 并核对节点身份 | TransportHandshaker、TcpTransport、TransportService |
| ch09 | CAT 端口称绑定值，暗示固定 9300 / 9200 | 实现取 Transport / HTTP 发布地址；_nodes/_local 明确对照绑定列表与发布地址，实际端口可配置 | RestNodesAction 描述与实现对照、RestNodesInfoAction |
| ch09 | 默认 2/3/6/1/1 即实际画像 / 整节点上限，累计出站可与 13 比 | 画像再按本地角色修正，defaults 可含本地配置；total_outbound_connections 累计成功 NodeChannels 组数，与当前接受通道 / 每组通道数不同 | ConnectionProfile、TcpTransport.openConnection / getStats、TransportStats |
| ch09 | PING 通道等于定时保活，ping_schedule=-1 暗示关闭 TCP keepalive | 请求 type 通道选择、应用层 PING 与 TCP keepalive 分开；-1 只禁定时应用 PING，节点设置不作动态更新预期 | TransportSettings、TransportRequestOptions、TcpTransport |
| ch09 | 本地零复制 / 单节点统计全零泛化，GET 成功暗示已验证 wire | 本地只跳过该跳请求 / 响应 wire 编解码；按同节点新基线观察增量，历史与其他流量可非零，不能验证远程 / 混合版本兼容 | localNodeConnection、DirectResponseChannel、StatsTracker；保留旧实测记录并限定范围 |
| ch09 | 缺独立 GET / 健康等待 / 基线，重复版本与清理条件不全 | 原 7 ID 保留、增 5 卡；显式 mapping / refresh / 健康等待 / GET 前后基线，固定 ID 版本随重写变，点名清理后重新等待并取基线；未知路由 400 是顶层 error 字符串 | [experiments/ch09.js](experiments/ch09.js)、RestController.handleBadRequest；本轮 API 未实测 |

### 第十章重构校对

| 课 | 网页旧说法 / 遗漏 | 修正 | 依据 |
|---|---|---|---|
| ch10 | 首次 GET / 动画固定为 VersionMap → translog，GET 全程不碰 Lucene、不等 refresh | location 跟踪初始 false；unsafe 检查、无可读操作 / 未命中时可能内部刷新并从 INTERNAL 读，通路仍使用 reader / fetch；响应不能证明具体分支 | InternalEngine.get / realtimeGetUnderLock / getVersionFromMap；固定提交链接见正文与图 |
| ch10 | translog 每次解析再建完整内存索引，必比 segment 更贵 | 普通 stored source 的 TranslogLeafReader 可直接提供 ID / source；synthetic 或额外字段可建内存索引；性能需按负载实测 | TranslogDirectoryReader.create / readStoredFieldsDirectly |
| ch10 | 默认 GET 加 refresh=true 在所有部署都无视，非实时 refresh 等同全索引 _refresh | 普通可提升分片显式 externalRefresh 需 refresh && !realtime，限定所选分片；非实时搜索唤醒可能刷新；不可提升分片另有刷新 / translog 接力 | TransportGetAction.asyncGet / handleGetOnUnpromotableShard、IndexShard.ensureShardSearchActive |
| ch10 | GET 缺省即自适应副本选择，_primary / _replica 有效，自定义 preference 粘住同副本 | 该 GET 未传排名统计，候选保留随机化顺序；9.4.0 不支持两旧值；自定义字符串只稳定排序，分配变化 / 失败可换拷贝 | OperationRouting.getShards / preferenceActiveShardIterator、IndexShardRoutingTable.rankShardsAndUpdateStats、Preference.parse |
| ch10 | routing 键不同几乎必 404，忘带就是 404，routing 不单独保存 | 不同键可同片；required 只拒绝缺失，错误字符串仍可通过；routing 保存为文档元数据并回显；跨不同片可有相同 ID | IndexRouting.getShard / Unpartitioned、RoutingFieldMapper.preParse、ShardGetService.innerGetFetch |
| ch10 | 图注 hash % 主分片数泛化，固定 routing 落点称本站本轮实测 | 新公式用 floorMod，按创建版本 / 普通非分区 / 无 routing_path 与 resharding 限定；固定键离线计算 4 / 2，另要求 API 比实际返回 | IndexRouting.hashToShardId / 策略分支、Murmur3HashFunction；本轮 API 未实测 |
| ch10 | 失败只换副本、不改 shard 是全部路径规则；found=false 暗示读失败 | 普通异常换同一候选迭代器；不存在是正常响应不重试；StaleRequestException 可等待路由更新并重启解析 | TransportSingleShardAction.perform / waitForRoutingUpdateAndRestart |
| ch10 | Engine 有 if_seq_no 就可在该 REST GET 带条件 | 此路由解析 version / version_type，不解析 if_seq_no / if_primary_term，getService 此入口传 UNASSIGNED；底层能力不等于 REST 参数 | RestGetAction.prepareRequest、ShardGetService.get、Engine.getFromSearcher |
| ch10 | refresh_interval=-1 就必不生成 segment，非实时只可能 404；GET 分池不会被搜索拖慢，可最多一秒旧 | -1 只关闭周期刷新；INTERNAL / EXTERNAL 分开，已发布旧值可 200；分池仍共享资源，调度周期不保证可见性时限 | InternalEngine、IndexShard、TransportGetAction.getExecutor；新增 A12–A14 新旧版本对照 |
| ch10 | 19 卡缺显式 mapping / 等待 / 重复与旧视图恢复条件 | 保留全部 19 ID，增 7 卡，共 2 组 / 26 卡；显式 standard / stored source / mapping / refresh / 健康等待，点名 清理后完整重做；预期与实测分开 | [experiments/ch10.js](experiments/ch10.js)、[本轮验收](.archify/CH10-REVIEW.md) |

### 第十一章重构校对

| 课 | 网页旧说法 / 遗漏 | 修正 | 依据 |
|---|---|---|---|
| ch11 | 第一篇文档写死全部 schema，动画“8 字段定稿” | 后续仍可增加新字段；A3 为 7 叶子 + 1 object + 3 multi-field = 11 计数字段，6 顶层键不是字段总数 | DynamicFieldsBuilder、FieldMapper / ObjectMapper / RootObjectMapper.getTotalFieldsCount；固定链接见本章 |
| ch11 | price 已 float，再写字符串 "29.99" 必 400 | 默认数值 coerce=true 可解析，mapping 仍 float、stored source 仍字符串；not-a-number 才在本例失败 | NumberFieldMapper.COERCE_SETTING / value / FLOAT.parse；新增 A7–A9，本轮 API 未实测 |
| ch11 | createDynamicUpdate 经本地 MapperService.merge 直接合并 cluster state | 本地候选随 ParsedDocument 返回；主分片预检、向主节点提交、权威元数据更新、等待版本变化重解析后才进 Engine | DocumentParser、IndexShard、TransportShardBulkAction、MetadataMappingService；图 01 |
| ch11 | FieldMapper.checkIncomingMergeType 为实际合并入口，自动保旧就使文档必错 | 9.4.0 MapperService 合并 builder；FieldMapper.Builder.mergeWith / throwMergeTypeConflict 检查类型，auto update 可保旧，重解析是否失败仍看输入 / coercion | MapperService 624–626、FieldMapper 1737–1779 |
| ch11 | term / 聚合 / sort 都要 keyword，match 只能 text；查询必用写入同分析器 | text 的准确词项可被 term 命中；keyword match 可走单词项快捷路径；term 匹配倒排词项；search_analyzer / 请求 analyzer / normalizer 改变规则 | TermBasedFieldType、MatchQueryParser、KeywordFieldMapper；B3–B7 |
| ch11 | false 是安静丢失，字段无处安身 | 本例 stored source 保留未知原值；GET 可见、刷新后普通 exists 不可见，也可提供请求级 runtime 视图 | DocumentParser.parseDynamicValue；C7–C10 |
| ch11 | runtime 不撑 mapping，小数沿用 float；高基数逼近字段总数 | 映射 runtime 仍计入 total_fields，字符串 keyword、小数 double；值基数与字段路径数分开 | DynamicFieldsBuilder.Runtime、RootObjectMapper.getTotalFieldsCount；C11–C13 |
| ch11 | dense_vector 必显式，浮点数组永远普通多值 float | 满足创建版本、128–4096 个 float、无模板覆盖 / 非 copy_to 等条件可自动映射 vector | DocumentParser.postProcessDynamicArrayMapping、DenseVectorFieldMapper 243–246 |
| ch11 | mapping 除 type 都可改，新增子字段立即用于旧文档 | 参数按 mapper 的更新规则判断；新增 mapping 不自动回填历史值，相关文档需重新解析 | FieldMapper.Builder / 参数合并规则；D1–D3 与正文 |
| ch11 | 19 卡缺健康等待、重复条件，false 缺原值 / 查询证据 | 原 19 ID 保留，增 16，共 5 组 / 35 卡；显式配置、局部等待 / refresh、错误恢复、四索引点名清理并重做 | [experiments/ch11.js](experiments/ch11.js)、[验收记录](.archify/CH11-REVIEW.md) |

### 第十二章重构校对

| 课 | 网页旧说法 / 遗漏 | 修正 | 依据 |
|---|---|---|---|
| ch12 | 链是单线程顺序；bulk 吞吐受 ingest 线程池限制 | 顺序依赖允许异步回调换线程；普通 bulk 协调使用 write_coordination，不能假设统一 ingest 池 | CompoundProcessor 149–219；TransportAbstractBulkAction 114–122、364–370 |
| ch12 | on_failure 成功只说文档留下，没有区分续接位置 | 处理器包装层补救成功继续外层主列表；管道根补救成功结束当前管道；ignore 优先且不承诺回滚 | ConfigurationUtils / OnFailureProcessor / Pipeline / CompoundProcessor；图 02，A5 / A7–A9 |
| ch12 | final 总最后，所有写入都经过，不可绕过安全门 | 普通 index 正常保留路径才继续 final，失败 / drop 提前停；重定向重解析，不泛化到所有修改 API | IngestService 1204–1236、1270–1288、1333–1347；D5–D16 |
| ch12 | _simulate 与写入差别只有路由 / 落盘；GET 只会 404 | 模拟不组合完整写入管道、不做 mapping / final 执行后约束；不影响原有数据，逐文档 error 也可 HTTP 200 | SimulatePipelineRequest / SimulateExecutionService / IngestService；A2–A9 |
| ch12 | 不带 / 不同 routing 的 GET 必 404，当前节点可套单一取模公式 | 对照实际分片号，键可碰撞；本课公式限定新建 9.4.0 普通非分区索引，旧创建版本另有分支 | IndexRouting 147–175、309–321；C4–C9 |
| ch12 | refresh=true 让下一 GET 立即可见 | 显式 refresh 服务搜索视图；默认 realtime GET 不依赖搜索刷新 | 第十章已校对机制；B3–B6、C6 / C9 |
| ch12 | 管道新字段仍动态建 text + keyword | 仅在本章显式 standard / dynamic:true、检测关闭、无模板覆盖等条件成立；不迁移旧字段或旧文档 | B1 / B7 创建配置；第十一章动态映射依据 |
| ch12 | pipeline 只说存在本地表，删除即全集群生效 | 定义提交集群状态 IngestMetadata，节点应用后构造本地对象；响应与发布 / 应用不等于瞬间同步 | IngestService 182–198、579–595、1547–1573 |
| ch12 | DELETE /_ingest/pipeline/fields,routing 能删除列表 | 删除 id 按单名称 / 简单通配匹配，不拆逗号；仍被 default / final 引用会拒删，先删索引再逐条点名删 | RestDeletePipelineAction 42–47；IngestService 470–490、494–534；D9 / 六张清理卡 |
| ch12 | 20 卡缺显式配置、等待、重复与恢复条件 | 保留 20 ID，增 28 卡，共 4 组 / 48 卡；三索引显式配置、局部等待 / 刷新、固定 ID、final 恢复与完整重做 | [注册表](experiments/ch12.js)、[验收记录](.archify/CH12-REVIEW.md)；本轮真实 API 未运行 |

### 第十三章重构校对

| 课 | 网页旧说法 / 遗漏 | 修正 | 依据 |
|---|---|---|---|
| ch13 | 两行一组 / action固定奇数行；动画五行却写六行 | action决定行数；delete单行，本例五行三项；操作编号不是物理行号 | BulkRequestParser268–295；保留机制六步 |
| ch13 | 所有source第二行原样到primary解析 | index/create切字节；update第二行立即fromXContent；文档解析时机受摄取/索引模式影响 | BulkRequestParser540–563；A6–A9 |
| ch13 | 结构坏发生在切条目前，整请求400无其他已写项 | 9.4.0增量入口可先拆批执行；后续解析失败不回滚先前执行块。错误卡用单项限定前提 | RestBulkAction100–149、235–271；IncrementalBulkService156–194 |
| ch13 | 协调节点不写Lucene；分组后不再有批；primary始终while | 协调是角色，可本地承接primary；按执行批次分组；批量优化默认关闭、受feature flag及操作类型约束 | BulkOperation278–345；TransportReplicationAction940–973；ShardBatchIndexer38–72 |
| ch13 | 改主分片数导致原GET找错；公式适用普通索引未限创建版本 | Final更新拒绝，不改变原路由；公式限定新建普通非分区索引，旧创建版本另分支；routing可同片碰撞 | IndexRouting147–175、309–321；既有Final依据 |
| ch13 | 只逐项扫status；条目完全独立；delete不自动建索引泛化 | error/result/status一起读；delete缺ID404无error，缺索引404有error；同组可有依赖，普通内部版本delete不建索引有外部版本例外 | BulkItemResponse420–422；DeleteResponse63–66；TransportBulkAction315–320 |
| ch13 | 副本失败不会影响请求、已领号即成功；动画seq_no=0 | 普通故障通常另记_shards，primary降级/写后失败可重试或失败；已领号失败可noop；无固定序号承诺 | ReplicationOperation213–228、303–335、423–455；TransportShardBulkAction795–824 |
| ch13 | false返回一定不可搜、wait_for只搭自动刷新且更便宜 | 是否可搜取决于刷新/旧视图；wait_for可由外部刷新满足或强制刷新，只覆盖触及分片、不改设置，无性能/耗时上限承诺 | PostWriteRefresh43–102；TransportWriteAction476–549；C1–C9 |
| ch13 | 13卡缺完整配置、等待、读回、首次/重复与恢复条件 | 原13ID保留、增27，共4组40卡；三索引显式配置/限定健康等待、错误后GET、刷新对照、all/1、点名清理再完整重做 | [注册表](experiments/ch13.js)、[验收](.archify/CH13-REVIEW.md)；本轮真实API未运行 |

### 第十四章重构校对

| 课 | 网页旧说法 / 遗漏 | 修正 | 依据 |
|---|---|---|---|
| ch14 | 可写实现唯一、Engine 在 recovery 完成后才创建 | 本课限定普通 InternalEngine，不泛化插件与其他形态；移除错误的创建时机断言 | Engine 抽象接口、IndexService1094–1096；本课未重读 tutorial |
| ch14 | 协调节点不存数据；动画用带符号 murmur3 %5 / 固定 shard0 | 协调是角色，可同节点承接存储；示例明确1主0副，去掉不适用的路由算式 | 本课前提与既有 ch13 角色依据；八步机制同步 |
| ch14 | refresh 不碰磁盘 / 每次一个新段，写入时任何 segment 都没有 | NRT reader 打开可落文件，IndexWriter 也可自动落段；可见性由 reader 决定，无固定段数 | InternalEngine2374–2438；A3/A7、D3–D5 |
| ch14 | flush 后一定可搜、translog归零 | 普通 flush 只刷新 INTERNAL；safe commit与引用影响裁剪，统计及文件字节不保证归零 | InternalEngine2621–2625；Engine244–250；Translog1878–1939；C9–C13 |
| ch14 | uncommitted是精确待重放条数，flush两次必为0；空基线“0或个位数” | 按 safe commit 后所需generation汇总，可夹带已覆盖操作；等待checkpoint后复查，不承诺固定次数；空基线明确0 | Translog1020–1034、1827–1836；B4/C8 |
| ch14 | async最多丢约5s，写后GET接口不能开且GET零额外耗时 | sync_interval是调度周期非损失上限；async仍可实时GET，业务决定耐久风险；删除未经实测性能承诺 | IndexService1106–1119、1222–1245；TransportWriteAction476–487；B7–B11 |
| ch14 | refresh_interval=0每次写入都refresh，-1完全控制维护 | 普通周期刷新检查>0；不能把0说成写入触发；-1不关后台flush；本课显式1h年龄阈值仍有后台条件 | IndexService1123–1139；InternalEngine2526–2560；IndexSettings380–395 |
| ch14 | 失败都补NoOp，GET第一次固定开跟踪且之后稳定走日志 | 提前冲突可无seq_no，已分配序号的特定文档失败可NoOp；GET按条目/location与读取条件走日志或INTERNAL | InternalEngine1247–1311、927–1008、1613–1736 |
| ch14 | flush阈值下限一概10MB、segment deleted_in_bytes字段、merge后deleted=0 | 10MB仅为磁盘保护阈值下限，显式flush值可更低；无deleted_in_bytes；软删除保留受safe commit/leases约束 | IndexSettings362–379、1762–1775；IndicesSegmentResponse121–137；SoftDeletesPolicy99–151 |
| ch14 | forcemerge无响应body/只提交后台；实验只给1主0副、无等待与恢复 | 默认同步等待返回_shards，flush=true还有外部刷新；原29ID保留，增17，共4组46卡，显式配置、健康、设置恢复、write block和重复清理 | RestForceMergeAction49–59；InternalEngine2802–2838；[注册表](experiments/ch14.js)、[验收](.archify/CH14-REVIEW.md)；本轮API未实测 |

### 第十五章重构校对

| 课 | 网页旧说法 / 遗漏 | 修正 | 依据 |
|---|---|---|---|
| ch15 | OperationRouting.generateShardId伪源码；公式不限定创建版本/模式 | 实际IndexRouting，限定新建普通非分区、无routing_path/resharding；旧创建版本用routingNumShards/routingFactor | 固定源码IndexRouting59–72、147–175、309–350；24文件/45区间审计 |
| ch15 | brown=741580288→片1，brown-1=-616020358→片2 | 字符串UTF-16LE而非UTF-8；真实998382972/−2007555306均片0，缺省GET仍200；route-0=512605379→片2作确定404反例 | Murmur3HashFunction27–48，官方7向量；ES9.4.0两轮实测0/0/2 |
| ch15 | 不同键必错片，忘routing的搜索也漏；required等于键内容正确 | 不同键可同片；无routing普通搜索查全部片，routing只缩范围；required拒文档请求缺失、不禁无routing搜索 | OperationRouting140–193，IndexRouting文档/搜索分支；两轮API同片200/跨片404/搜索2→0 |
| ch15 | GET与搜索都默认ARS，读副本瞬时一样 | 普通GET不传排名统计；搜索有统计时可ARS，不承诺最快或所有reader同步；单节点不是复制证据 | OperationRouting62–115、IndexShardRoutingTable328–345 |
| ch15 | Final失败后所有键换片、数据蒸发、只能reindex；固定final检查文案 | 更新拒绝、原设置3及GET不变；不同布局按条件resize/reindex；开放索引入口实际400 reason为non dynamic setting(s) | IndexMetadata222–239、MetadataUpdateSettingsService258–285；B4–B6两轮实测 |
| ch15 | 副本是整份文件拷贝，UNASSIGNED不在复制组却total=2 | 同逻辑数据不保证segment布局相同；配置total可含未分配拷贝，未分配不是本次复制失败；局部等待yellow/green | 本课抽象范围、两轮写入_shards=2/1/0及限定健康 |
| ch15 | peer先落完全部ops再开Engine，五态唯一链、第二Engine永不可能 | 文件/已有目录准备后RECOVERING内开Engine，再重放/phase2；可提前close，恢复写独立；省略替换与迁移细节 | IndexShard、StoreRecovery、RecoveryTarget371–379、RecoverySourceHandler298–351 |
| ch15 | _close后GET固定403 cluster_block_exception | 本例实测400 index_closed_exception/closed；SingleShardRequest禁止closed，具体解析先于索引block，403是block自身映射；本地闸门404另层 | IndexNameExpressionResolver805–818、TransportSingleShardAction190–203、IndexClosedException；两轮API |
| ch15 | 16卡缺显式mapping/等待/重复条件，健康请求含无效v | 原16ID及七步机制保留，增24共4组40卡；显式配置、同片/跨片、search/required、Final读回、close/open与两索引点名清理重做 | [注册表](experiments/ch15.js)、[两轮真实响应](.archify/review/ch15-es-review.json)、[验收](.archify/CH15-REVIEW.md) |

### 第十六章重构校对

| 课 | 网页旧说法 / 遗漏 | 修正 | 依据 |
|---|---|---|---|
| ch16 | 三片size=10固定回30元组、hits恰等size，collector只扫描窗口 | 普通窗口为上限且限定分支，实际受匹配/reader限制；本例12/9/9→候选上限28、最终10；维护Top-k不等于只扫描k | QueryPhaseCollectorManager225–260、SearchPhaseController543–558；两轮真实分布/响应 |
| ch16 | SEARCH必打所有片、单节点代表网络往返；跨片快照暗示同一时刻 | 默认目标分片组每组选一份，routing/can-match可缩范围；角色可共节点，各片读者非全局事务时刻 | TransportSearchAction1984–2005、IndexShard1772–1798；本章抽象范围 |
| ch16 | 发完就释放线程，归并永远在最后网络回调线程 | 每节点并发可排队、同步回调；consume完成再倒数，FetchSearchPhase.run经context.execute调度reduce | AbstractSearchAsyncAction249–279/503–527/796–798、FetchSearchPhase78–119 |
| ch16 | doc是段内文档号，Query只有doc/score固定小字段 | doc属于当前分片reader空间；sort还有排序值，Query可带聚合/统计等，不保证固定字节 | SearchPhaseController100–169/202–214；QueryPhaseCollectorManager237–260 |
| ch16 | profile过滤掉searches；把时间当加载篇数，关闭source等同无Fetch | 保留searches与fetch；load_stored_fields_count本例合计10，next_reader_count是段切换；source-off仍fetch，size0仍聚合；profile不测完整网络/协调 | [注册表](experiments/ch16.js)、[两轮响应](.archify/review/ch16-es-review.json)、官方profile范围 |
| ch16 | 超窗顶层400 illegal_argument_exception，合法空页过滤后可见[] | 顶层search_phase_execution_exception/all shards failed，内层illegal_argument_exception；failed_shards可分组；空页filter_path保留hits.hits | DefaultSearchContext359–380、AbstractSearchAsyncAction328–356；真实400/200及修复前响应 |
| ch16 | 单片无条件合并；9.x默认批量Query；DFS大数据几乎白付、所有向量强制DFS | 普通无rank/kNN单片QTF可合并；批量/预过滤受开关与其他条件；hasKnnSearch分支改DFS，收益按查询/数据判断 | SearchService977–1034/308–317、FetchSearchPhase101–108、TransportSearchAction790–813、SearchQueryThenFetchAsyncAction472–495 |
| ch16 | from/size与search_after“无上下文”，refresh=-1使NRT绝对确定 | 普通仍创建临时reader；PIT/scroll跨请求保留；-1只关周期刷新，C组先删并refresh建0基线，无其他刷新条件下0→1 | SearchService1105–1177；官方分页说明；两轮GET/count0→refresh/count1 |
| ch16 | 14卡缺健康/设置/完整profile/可见性重置/单片对照 | 保留14ID和七步；增15共4组29卡，显式mapping/设置、排序翻页、NRT重置、点名清理重做；步骤2/5快照底部排印修复 | [验收](.archify/CH16-REVIEW.md)、[HTTP](.archify/review/ch16-http-review.json)、[真实API](.archify/review/ch16-es-review.json) |

### 第十七章重构校对

| 课 | 网页旧说法 | 修正 | 依据 |
|---|---|---|---|
| ch17 | 每次Query必创建context、handler立即返回；private两参数/markAsUsed在try内 | 正常异步分支private有reader参数，包装持使用引用；can-match可提前空返回，executor有普通/系统分支 | SearchService768–844/977–1034/1362–1371；本章固定源码链接 |
| ch17 | Profile/Highlight/Explain均对originalQuery，Lucene rewrite才展开quick/brown | 默认高亮parsedQuery，Explain用rewrittenQuery，Profile执行树含过滤；toQuery已分析构造SHOULD，无filter可返回原query | DefaultSearchContext438–492/766–776；ExplainPhase44；[两轮过滤别名证据](.archify/review/ch17-es-review.json) |
| ch17 | 小数据一次超时检查都没有、1ms只看收集粒度 | 叶子开始与分批检查；默认相对时钟缓存200ms；非全请求截止线，单片Fetch清除查询超时 | QueryPhase285–302；ContextIndexSearcher452–484；ThreadPool245–251/788–798 |
| ch17 | 33篇加500万循环必200超时/429，不触发继续加零 | 真实400脚本保护；有界2万计算×3003篇先完整基线，再两轮200 timed_out与严格429；少量合法负载仍false | [原响应](.archify/review/ch17-original-responses.json)、[最终两轮](.archify/review/ch17-es-review.json)、CompilerSettings66 |
| ch17 | PIT sort只[ts]、后卡沿用最初id，没有真正第二页 | PIT加_shard_doc，复制末项完整数组；最新pit_id逐次传，新增第二页/换查询/关闭ID404，本轮[2,1]仅例子 | 官方分页规则；[两轮响应](.archify/review/ch17-es-review.json) |
| ch17 | open_contexts为全节点0→1→0，每PIT独占reader/到点立即放；PIT重建可无条件重试并发 | 本索引基线N比较；解除上下文引用不保证底层全放，后台reaper/使用引用保护；相同searcher重建有条件，不承诺所有故障恢复 | ReaderContext87–96/134–154；SearchService1460–1488/1887–1900；PIT官方API |
| ch17 | 18卡缺mapping/健康/配置/基线/重做，关闭响应只笼统succeeded | 保留18ID增14，3组32卡；显式配置、局部健康/统计、合法脚本基线、PIT完整游标与点名清理重做；关闭true/num_freed1 | [注册表](experiments/ch17.js)、[验收](.archify/CH17-REVIEW.md) |

### 第十八章重构校对

| 课 | 网页旧说法 | 修正 | 依据 |
|---|---|---|---|
| ch18 | 两卡 GET _explain 带 body，可在网页直接运行 | 浏览器 ESClient 不发送 GET body，旧卡真实400缺query；保留ID改POST后200 | [原响应](.archify/review/ch18-original-responses.json)、[当前两轮](.archify/review/ch18-es-review.json) |
| ch18 | _explain / highlight 都只对 originalQuery 说话 | 默认高亮取原ParsedQuery；Explain先preProcess，再解释rewrittenQuery，别名约束参与；search Explain亦然 | TransportExplainAction156–179/ExplainPhase40–49；[别名实测](.archify/review/ch18-es-review.json) |
| ch18 | keyword match一定到parser才短路，term所有字段原样不变 | 默认keyword可先Builder改写；parser另有短路，normalizer单词项归一化/显式analyzer有条件 | MatchQueryBuilder360–409；KeywordFieldMapper1085–1101；本轮normalizer实测 |
| ch18 | standard按空白分；_analyze直接看词典 | 词边界tokenizer+lowercase、默认空停用词；analyze是分析输出，本例显式保存词向量核对词项/位置/offsets | [固定Lucene核对](.archify/review/ch18-lucene-source-review.json)、[真实词向量](.archify/review/ch18-es-review.json) |
| ch18 | 多token一概SHOULD；更多词必排更高；反向短语是“两词不相邻” | 本例无同义词/模糊两位置OR；跨文档排名有其他统计；反向两词相邻但词序不符，另测同序间隔 | MatchQueryParser410–450/621–645；OR/AND/phrase真实对照 |
| ch18 | must必评分，keyword term为常数分；should通常可选 | must评分限定普通评分上下文；本例keyword用相似度；should门槛按同层must/filter及显式minimum判断 | BoolQueryBuilder305–327；C5/C6/C7/C8/C9实测 |
| ch18 | post_filter在hits已排完/聚合已算完后再删Top-N | Query阶段无分Weight，hits收集路径检查，聚合独立收集；query.bool.filter缩小两路 | QueryPhase191–221/QueryPhaseCollector286–318；聚合两轮对照 |
| ch18 | filter可直接缓存回放，精确命中≥1%选bitset | 仍受策略/可缓存性/segment/容量约束；表示按scorer.cost估计选择，四篇不证明性能 | XLRUQueryCache501–513/730–776；Lucene固定策略 |
| ch18 | 19卡无就绪等待/完整重做，重复bulk永远201 | 保留19ID增15；显式配置/局部green/固定ID+refresh；重复创建400、写入updated200、重复清理404分别实测 | [注册表](experiments/ch18.js)、[两轮+8项](.archify/review/ch18-es-review.json) |

### 第十九章重构校对

| 课 | 网页旧说法 / 遗漏 | 修正 | 依据 |
|---|---|---|---|
| ch19 | 聚合Query已算完，所有聚合不碰Fetch；统计所有命中 | Query是局部结果、后续仍归并；普通桶/指标不依赖主hits Fetch，top_hits另取字段；范围按query/global/nested等条件 | AggregationPhase、TopHitsAggregator199–231/252–265；A6/A7实测 |
| ch19 | innerBuild按字段选执行器，keyword固定GlobalOrdinals计数 | Builder创建Factory，字段供应商选Aggregator；本轮profile为StringTermsAggregatorFromFilters/FilterByFilter，有其他优化分支 | TermsAggregatorFactory95–150/449–592；两轮C6实测 |
| ch19 | 每片实际回桶至少size；默认公式没有取整与上限 | shardSize≥size只约束容量，实际桶可少；未显式且非_key套floor(size×1.5+10)，上限MAX | BucketUtils26–34、TermsAggregator91–111、Factory294–305 |
| ch19 | error_bound是没送桶文档总数，过采样无法为0/只有全量才0 | 是保守计数上界，聚合/桶级分开；本例容量2聚合7/桶0和3，默认13为0，显式3计数准确但上界仍5 | AbstractInternalTerms120–140/250–340；B9–B12实测 |
| ch19 | sum_other18全是分片队列丢弃，证明20计数器 | 局部/最终都可贡献，不是key数/内存布局；bucket_sort裁剪不回记terms账，B13仍7/B14仍0 | GlobalOrdinals构建、AbstractInternalTerms；BucketSortPipelineAggregator50–83；两轮实测 |
| ch19 | partial都不裁、avg等父桶截完才算；nested或需分数都强制depth | count降序partial保候选，_key有特例；depth/breadth影响子聚合时机；nested与需分数为合取，时序条件另列 | AbstractInternalTerms283–331、TermsAggregator213–226/269–272 |
| ch19 | size完全不省内存、百万值必百万计数器先撞breaker；tripped应0 | 队列/候选/子聚合亦受容量影响，策略与负载决定状态；5120B初始估计，tripped累计且可非0；20值非压力测试 | AggregatorBase39–42/148–158；Factory优化分支；C组实测 |
| ch19 | histogram/date_histogram key请求预列，各片同key仅加总 | 由字段值和间隔/日历/时区算key；range预给区间，空桶/bounds有条件；没有terms Top-N截断不等于无其他边界 | A5月计数2/2/3/1、range4/2/2；正文限定 |
| ch19 | 自动ID重复bulk累加、缺健康/恢复；均价写死349.99 | 保留17ID增13，固定ID/显式配置/三组健康/refresh/点名清理重做；float尾数容差；加权avg42/10=4.2 | [注册表](experiments/ch19.js)、[两轮30卡+29观察](.archify/review/ch19-es-review.json) |

### 第二十章重构校对

| 课 | 网页旧说法 | 修正 | 依据 |
|---|---|---|---|
| ch20 | Query就定全部名次；Fetch不算分、只搬_source | 分片局部候选仍经协调全局归并；Fetch可算Explain/补rescore说明及加载其他字段，不据解释重选窗口 | QueryPhase142–147；SearchPhaseController145–170；ExplainPhase40–67；FetchPhase592–627 |
| ch20 | GET _explain带body可在网页执行 | ESClient不发送GET body，旧卡真实400 query is missing；稳定ID改POST后200；存在不匹配200/缺失404，非realtime读者 | [原响应](.archify/review/ch20-original-responses.json)、[两轮与补充](.archify/review/ch20-es-review.json)；TransportExplainAction156–179 |
| ch20 | 所有写入不相干文档都涨分；N等于总篇数 | N是字段docCount；本例含title长度2的c使N3/avgdl2涨分，缺title的d使索引4篇而N仍3；更新/删除旧版本可暂留统计 | A5/C1–C5实测；[Lucene核对](.archify/review/ch20-lucene-source-review.json) |
| ch20 | Legacy常数永远不改排名；Deprecated代表新索引该换了；堆词买不到排名 | 9.4.0内置BM25仍Legacy、boost2.2；统一倍数只在同参数纯BM25不改次序；复杂混分尺度有影响，饱和仍增长且堆词可能改长度 | SimilarityService41–57/Providers256–264；Legacy71–74；Lucene固定10.4.0；两轮A6–A9 |
| ch20 | 任意sort都TopField/DocValues，显式_score响应有sort | 单_score desc由buildSort优化为默认TopScore、本例无sort数组；普通views用字段键，track_scores不改键；特殊sort各自处理 | SortBuilder157–198；QueryPhaseCollectorManager418–435；B5–B7/B10实测 |
| ch20 | rescore禁与所有sort同用；窗口外保持原分 | 允许无sort或_score降序，源码另有升序_shard_doc tie-break条件；views/score asc拒绝。窗口外仍乘query_weight；1/2窗口只每片 | RescorePhase102–124；QueryRescorer61–72/120–136；B8–B11及query_weight2实测 |
| ch20 | 乘views还可保证相关性主序，views=0不失去高名次 | 乘积可翻盘，乘零归0可失去高名次；replace仍用query限制匹配集合，同函数分可并列；max_boost裁剪须考虑 | CombineFunction20–54/FunctionScoreQueryBuilder；B1–B4实测 |
| ch20 | 单篇Explain与所有search是同一棵树，且可读未refresh写入 | 同读者/查询/统计的单片普通search可对齐；DFS与rescore等有差异；未刷文档GET可见、_explain404，刷新后200 | TransportExplainAction非realtime Get/preProcess；ExplainPhase补rescore；13补充实测 |
| ch20 | 12卡缺健康/完整配置/重复恢复，精确重做只重写文档 | 保留12ID增18，3组30卡；strict/stored source/standard/BM25/norms/Doc Values、局部green、refresh、点名清理重建；mapping序列化省略默认true项，API词向量字段总频名sum_ttf | [注册表](experiments/ch20.js)、[验收](.archify/CH20-REVIEW.md)、[两轮30卡+13观察](.archify/review/ch20-es-review.json) |

### 第二十一章重构校对

| 课 | 网页旧说法 / 遗漏 | 修正 | 依据 |
|---|---|---|---|
| ch21 | minVersions 非 final，列出的字段不完整；读側都无锁 | minVersions 是 final；另有 compatibilityVersions/clusterFeatures；routingNodes 惰性同步慢路径，概念不可变不要求全树深拷贝 | ClusterState163–196/437–458/1190–1203；[固定源码审计](.archify/review/ch21-source-review.json) |
| ch21 | metadata.version 可与顶层并排 REST 输出，且一定更小 | API 上下文不序列化内部版本，filter_path 不能创造；等待比较内部≥门槛且需≥1，超时200无状态 | Metadata730–758；ClusterStateRequest162–175；[两轮与补充](.archify/review/ch21-es-review.json) |
| ch21 | 成功建索引 version 只+1，成功任务都发布 | 一份新状态加一，一次 API 可触发多批；两轮创建均+3；相同动态设置重交可 no-op，版本/UUID不变 | MasterService336–382/652–675；两轮402→405、414→417与406/418 no-op |
| ch21 | term 固定1；投票字段名 config，按换届描述递增 | term 按实际选举历史判断；last_committed_config/last_accepted_config/voting_config_exclusions，无 config | CoordinationMetadata33–47/105–111；两轮 term1仅参考 |
| ch21 | pending 只列还没算的批，insertOrder/timeInQueue | 同时含执行中与待处理任务，executing 指示；REST键 insert_order/time_in_queue_millis，非历史/文档队列 | MasterService2010–2025；PendingClusterTasksResponse83–98 |
| ch21 | Listener可慢，重活移过去不会挡；主最后apply代表所有节点先完成 | 同步Listener仍占应用线程，挡下一状态；两回调都应快；可有落后节点，提交/本地可见/各节点应用分别解释 | ClusterStateListener15–27；ClusterApplierService538–571/617–639；Publisher23–53 |
| ch21 | Metadata每次更新都写盘（未说明条件），其他三块均从Metadata+复制恢复 | 按角色/持久化上下文和全量/增量路径理解；全重启需重新发现、恢复与分配，旧引用不代表各组件全局原子 | GatewayMetaState617–641；ClusterState78–106；图注与正文限定 |
| ch21 | 16卡无健康等待/完整恢复，删ver索引顺手还原集群设置 | 原16ID保留增13成3组29卡；改本索引refresh 1s→5s、no-op、恢复读回、门槛等待、两索引点名清理后重做；集群配置前后相同 | [注册表](experiments/ch21.js)、[两轮29卡+18观察](.archify/review/ch21-es-review.json)、[验收](.archify/CH21-REVIEW.md) |

### 第二十二章重构校对

| 课 | 网页旧说法 / 遗漏 | 修正 | 依据 |
|---|---|---|---|
| ch22 | term只在成功换主时+1，API term可当选举次数；高term自动获胜 | StartJoin先持久化currentTerm后收Join，可失败/跳号/原节点再当选；API term属快照，仍验任期/状态新鲜度/双多数 | CoordinationState169–210/220–300；Coordinator583–606；[固定源码审计](.archify/review/ch22-source-review.json) |
| ch22 | 默认读Master，local=true换成本地；各API ID必同时一样 | 9.4状态动作直接读本地已应用状态，local弃用无效果；CAT master同动作，独立快照可不同，CAT nodes加full_id=true | TransportLocalClusterStateAction38–92；RestUtils351–365；RestMasterAction48–59；RestNodesAction349–373 |
| ch22 | 有m就都在配置且可当选，3台节点必2票 | 资格与实际名单分开，名单内不同ID计票；重配置可选子集/保留离线成员；voting_only另有策略/状态转移特例 | Reconfigurator107–144；VoteCollection603–621；VotingOnlyNodePlugin114–159/172–219 |
| ch22 | pre-vote只问能否连到多数，已有leader一概拒，term绝不受影响 | 健康/已知leader自身例外/更鲜响应过滤；假Join试探双多数，仍观察maxTermSeen，高信息可触发后续推进 | StatefulPreVoteCollector89–118/175–227；Coordinator560–585 |
| ch22 | 全局任意时刻最多一台自认Master；隔离还能收到另外两台拒票、几秒必恢复 | 旧本地Mode可滞后；固定名单少数侧不能正常提交新状态，完全隔离联系不到多数；检测/竞争/请求重试有条件 | Coordinator979–1036/1077–1111；Publication142–166；[七步概念动画](experiments/ch22.js) |
| ch22 | 收到Publish才FOLLOWER；所有Mode箭头一条链；发布完成等于全体应用 | 满足条件的follower check也可跟随；leader先候选再跟随；默认双多数accept形成提交，通知/mark/apply分开，leader apply延后 | Coordinator411–438/441–459/1077–1111/2097–2135；CoordinationState452–459/471–518 |
| ch22 | commit通知收到才有提交，四门是全部保证；失败即一定没发生 | 默认beforeCommit立即成功，插件可延后/失败；FailedToCommit允许不确定性且动作可重试，读回确认不宣称回滚；集群状态不等于文档复制 | ElectionStrategy116–118；Coordinator2227–2255；FailedToCommitClusterStateException18–36 |
| ch22 | 建索引version恰好+1、term=1，全群health应green；single-node无条件验自己的多数 | 变化状态版本推进，创建/分配/其他活动可多次；同mapping可无变化；局部就绪等待；single-node已有非空配置才验quorum | MasterService652–674；MetadataMappingService190–198/235–242；Coordinator1185–1202/2050–2062 |
| ch22 | 10卡缺版本/空前提/配置读回/重做；静态三图与七步多个绝对论断 | 保留10ID增8共18，2官方交互图/2路径/七步；显式配置、局部等待、点名清理HEAD404；纠正链式发布和角色矛盾 | [验收](.archify/CH22-REVIEW.md)、[HTTP](.archify/review/ch22-http-review.json)；真实API未跑，原因见运行证据 |

### 第二十三章重构校对

| 课 | 网页旧说法 / 遗漏 | 修正 | 依据 |
|---|---|---|---|
| ch23 | 先过滤NO才算权重，balancer根本看不到NO节点 | 约束贯穿规划/当前动作，解释先算权重并保留NO排名；默认后台算新目标，本轮可先按旧目标reconcile | BalancedShardsAllocator1495–1565；DesiredBalanceShardsAllocator277–299；[固定源码审计](.archify/review/ch23-source-review.json) |
| ch23 | 三种决定只有一条序；THROTTLE也会开始；NO永久待人工修 | 四种决定，汇总与节点比较中THROTTLE/NOT_PREFERRED顺序相反；初始化可接受YES/NOT_PREFERRED，THROTTLE暂缓；条件变可重评 | Decision194–224；AllocationDeciders209–237；DesiredBalanceReconciler317–365/692–734 |
| ch23 | index系数强制主副角色交错，threshold=片数差，磁盘系数只微调 | 四维归一化模型：片数/同索引数/预测写负载/分片字节；index不均衡主角色，小系数乘大字节；门槛结合minWeightDelta | BalancedShardsAllocator86–119/690–704；WeightFunction52–104/145–168 |
| ch23 | 源搬迁时仍STARTED；副本B→C一定从B复制；新节点必达2/1/1 | 源RELOCATING仍active，目标独立INITIALIZING；普通replica目标向active primary恢复；2/1/1是可能示意 | ShardRouting135–153/217–228/500–537/594–614；IndicesClusterStateService1006–1027 |
| ch23 | 任何恢复失败都变UNASSIGNED；所有恢复总共最多2 | 目标失败且源仍在可取消源搬迁、删除目标；incoming/outgoing各2，初始本地primary另4，均可调整 | RoutingNodes645–662；ThrottlingAllocationDecider48–78 |
| ch23 | 达85/90/95%必依次拒绝/迁移/封写，存量过low必不动 | headroom默认有配置条件，比例已用/绝对空闲分开，考虑估计大小/预留/路径；low豁免新空/clone主有条件，high不保证找到目标 | DiskThresholdSettings38–103/478–505；RelativeByteSizeValue59–72；DiskThresholdDecider221–328/397–482 |
| ch23 | flood-stage写入都403；Green意味着可写，允许删除等于能删文档 | 默认flood read_only_allow_delete WRITE块429；普通write块403；健康与准入分开，文档删除也是WRITE | IndexMetadata117–143；DiskThresholdMonitor214–239/404–433；C组普通写块对照 |
| ch23 | explain总选第一个未分配、包含所有YES、排名证明可落位 | 优先可访问未分配primary再replica；ALWAYS不进数组，在途可NOT_TAKEN；当前Balanced解释不等于目标历史，缺磁盘信息可fail-open | TransportClusterAllocationExplainAction123–168；AllocationDeciders209–237；DiskThresholdDecider547–558 |
| ch23 | 11卡无版本/就绪/过滤恢复与清理确认，三静图与七步有绝对结论 | 保留11ID增22共33卡，2官方交互图/2trace/七步；显式配置、等待、过滤解除、普通写块恢复、点名两索引HEAD404重做 | [验收](.archify/CH23-REVIEW.md)、[HTTP](.archify/review/ch23-http-review.json)；真实API未实测，原因见运行证据 |

## 第二十四章重构校对（ES 9.4.0）

本章源码固定到 `2e8528e92361c3399724226deaf2b46f933e925b`，Lucene 10.4.0；26 个文件 / 64 个相关范围的固定字节与行号核对通过。API 首次运行、清理重做、peer 与快照实测均未运行；证据及限制见 [.archify/CH24-REVIEW.md](.archify/CH24-REVIEW.md)。下表是已有网页与动画的修正，保留旧会话的历史记录。

| 旧说法 | 本轮正确结论与条件 | 依据 |
| --- | --- | --- |
| phase2 就是源端未 flush 的 translog，uncommitted_operations 就是发送数量 | 文件恢复的所选 safe commit 可能旧于 latest commit；操作恢复起点来自目标，区间与本地统计不同。普通 InternalEngine 从 Lucene 读取操作历史，统计不能对等 | RecoverySourceHandler.recoverToTarget；CombinedDeletionPolicy；InternalEngine.newChangesSnapshot |
| refresh 后文档只能靠 phase2；先 flush 则一定改为 phase1 | refresh 不能证明覆盖于本次基线；flush 不能独自决定分支与安全提交。有完整历史时可跳过传文件 | RecoverySourceHandler 206–287；CombinedDeletionPolicy 272–304 |
| 所有 peer 都先传文件，skip 意味着从不 replay 本地 translog | 目标先尝试临时 Engine 本地恢复到 GCP 并关闭；正式 prepare 开启网络 Engine 时 skip 本地 replay。操作分支可不传文件 | IndexShard.recoverLocallyUpToGlobalCheckpoint；PeerRecoveryTargetService；RecoveryTarget.prepareForTranslogOperations |
| 只按 size + checksum 全同就复用 | isSame 还比较 hash 与适用 writer UUID；peer 的段分组 diff 可能影响重传集合。按计划也可从快照辅助获取文件 | StoreFileMetadata.isSame；Store.MetadataSnapshot.recoveryDiff；RecoverySourceHandler.phase1 |
| phase2 不限速、必然尽快追平 | 操作链不调用 FILE_CHUNK 的同一 RateLimiter；仍受分批、请求并发、CPU/磁盘/网络约束。复制先接入再采样 endingSeqNo | RemoteRecoveryTargetHandler；RecoverySourceHandler 303–348 / 1136–1167 |
| finalize 后直接 STARTED 并必然集群 Green | 恢复 DONE、IndexShard POST_RECOVERY、Master 路由更新和应用 active 后 STARTED 分开；其他分片仍影响颜色 | RecoveryTarget.markAsDone；IndexShard 578–585 / 1987–2019 |
| _recovery 两块计数就是网络两阶段，保存恢复全历史 | 各来源都有恢复账；本地准备可参与操作计数、total 可未知或变化，文件 size 有快照来源字节。当前分片保存的记录不能代替完整历史或未开始副本 | RecoveryState.toXContent / Translog / Index；RestRecoveryAction |
| 新文件数量等于上传次数，快照按 checksum 全局共享 | 按物理名查找并比较完整元数据，完整清单含旧/新引用；小内容可内联，段合并改变增量量。每份成功快照独立恢复，删除按存活引用清理 | BlobStoreRepository.doSnapshotShard / unusedBlobs；BlobStoreIndexShardSnapshots.findPhysicalIndexFile |
| fs 注册必定失败，列表必为空；失败一定未登记 | 默认 Compose path.repo 为空时创建校验失败；已配置环境可成功，后续验证失败可能已登记。点名检查本章仓库，不要求所有仓库为空 | FsRepository；RepositoriesService 264–337 / 477–498 |
| 清理卡称删两个索引，实际只删 rec；重复创建继续操作 | 57 张卡显式前提、等待、单写入、快照条件扩展、逐项点名清理及 404 核对；保留全部旧 20 IDs。注销仓库不删除仓库文件 | experiments/ch24.js；本轮源码与注册表检查；真实重做未实测 |

## 第二十五章重构校对（ES 9.4.0）

本章已按七段式与统一阅读列重构；22文件/58处固定源码行段、站点与独立 HTTP/视觉审阅通过，真实 API 与原生 file 浏览器限制单列。完整依据与哈希见 [.archify/CH25-REVIEW.md](.archify/CH25-REVIEW.md) 和 [.archify/review/ch25-artifacts.json](.archify/review/ch25-artifacts.json)。

| 旧说法 / 旧实验 | 当前结论与适用条件 | 固定 ES 9.4.0 依据 |
| --- | --- | --- |
| 聚合内存曲线为“6KB预留 + 5KB重量 + 数组” | 预留包装器覆盖缓冲内消费；超过预留只补差，满后直通。不能重复相加 | [PreallocatedCircuitBreakerService](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/server/src/main/java/org/elasticsearch/common/breaker/PreallocatedCircuitBreakerService.java#L108-L171) |
| Parent 首次真实堆加预留超过95%就立即拒绝 | 首次超限后调用策略，策略结果仍超限才计数并抛；G1可复测，不保证回收成功，实际限额可配置 | [checkParentLimit](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/server/src/main/java/org/elasticsearch/indices/breaker/HierarchyCircuitBreakerService.java#L414-L434)、[策略选择](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/server/src/main/java/org/elasticsearch/indices/breaker/HierarchyCircuitBreakerService.java#L510-L534) |
| -1 只记账永不跳 | 只跳过子限额，仍检查 Parent；0立即拒绝子检查入口 | [Child 分支与 Parent 调用](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/server/src/main/java/org/elasticsearch/common/breaker/ChildMemoryCircuitBreaker.java#L105-L132) |
| 默认 Parent 应明显大于三本子账之和；只有四本账 | 子统计是 raw used，Parent随模式采样真实堆或全部注册子账加权和；不规定与三子裸 used 的大小关系，其他 breaker 可存在 | [stats/memoryUsed](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/server/src/main/java/org/elasticsearch/indices/breaker/HierarchyCircuitBreakerService.java#L328-L385) |
| Parent 本次 request 调用就几乎总是 TRANSIENT；fielddata PERMANENT只能清缓存才退 | Parent durability按全部子账 transient/permanent 占比；类别是提示，不是严格释放时限或唯一清理方式 | [类别配置](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/server/src/main/java/org/elasticsearch/indices/breaker/HierarchyCircuitBreakerService.java#L178-L210)、[Parent类别](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/server/src/main/java/org/elasticsearch/indices/breaker/HierarchyCircuitBreakerService.java#L428-L434) |
| 调用方从不先分配，熔断保证节点活、堆不变和下一次成功 | BigArrays包含分配前与已创建后核算；记账释放不同于GC。熔断降低风险，不能覆盖全部分配或保证后续成功 | [BigArrays](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/server/src/main/java/org/elasticsearch/common/util/BigArrays.java#L511-L589) |
| size/shard_size只管返回；min_doc_count收窄就节省收集内存；cardinality等价替换terms | 窗口可影响候选内存，不能限制全部收集；min_doc_count无普遍收集内存上限，cardinality只适用于近似计数业务语义 | [收集与候选](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/server/src/main/java/org/elasticsearch/search/aggregations/bucket/terms/GlobalOrdinalsStringTermsAggregator.java#L558-L579)、[桶状态](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/server/src/main/java/org/elasticsearch/search/aggregations/bucket/terms/GlobalOrdinalsStringTermsAggregator.java#L621-L655) |
| Bulk超过水位，>1MB或>4MB就拆 | 增量 maybeSplit 比较当前 combined+replica 与当前块字节两项 >=，高水位先判断；不等于任意HTTP包体积规则 | [双条件](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/server/src/main/java/org/elasticsearch/index/IndexingPressure.java#L212-L237)、[增量调用](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/server/src/main/java/org/elasticsearch/action/bulk/IncrementalBulkService.java#L144-L174) |
| transient单节点重启即丢；null必回60%且保底恢复 | 不依赖重启清理；null只删除指定覆盖，生效值可能来自persistent/节点配置/默认。只在无原覆盖前提执行，核对来源和实际基线限额 | [删除覆盖](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/server/src/main/java/org/elasticsearch/common/settings/AbstractScopedSettings.java#L860-L890)、[集群层合并](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/server/src/main/java/org/elasticsearch/cluster/metadata/Metadata.java#L1680-L1688)、[节点回落](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/server/src/main/java/org/elasticsearch/common/settings/AbstractScopedSettings.java#L159-L183) |
| 匿名ID反复bulk仍20文档；tripped>=1证明本次拒绝 | 固定ID1–20，首次created/重复updated；显式refresh/count/Green；计数以本次前后增量判断，不限定一次REST只加1 | [子计数与检查](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/server/src/main/java/org/elasticsearch/common/breaker/ChildMemoryCircuitBreaker.java#L73-L132)；本章操作卡，API未实测 |
| 同一size=0 terms必重新走同一执行过程 | 三次对照请求显式request_cache=false，排除缓存路径干扰；该参数不改索引缓存配置 | [请求参数](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/server/src/main/java/org/elasticsearch/rest/action/search/RestSearchAction.java#L258-L260)、[缓存准入](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/server/src/main/java/org/elasticsearch/indices/IndicesService.java#L1675-L1686)、[缓存或执行](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/server/src/main/java/org/elasticsearch/search/SearchService.java#L750-L765) |
| 1GB示例混用二进制单位，Parent拒绝动画reason写request；健康色仍Green | 明示H=1000MiB用于算术，实际看字节API；Parent例名称[parent]，子拒绝例[request]；健康色与内存准入分开 | [Parent文案](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/server/src/main/java/org/elasticsearch/indices/breaker/HierarchyCircuitBreakerService.java#L447-L461)；正文与7步示意同步 |

## 第二十六章重构校对（ES 9.4.0）

本章固定源码 29 文件 / 55 行段、20 稳定 ID / 45 顺序操作卡；两个官方 workflow v2 图与七步机制同步校正。源码、站点、独立 HTTP 与实际视觉审阅完成；真实 API、首次/清理重做未运行，原生 file 浏览器失败单列。详情见 [.archify/CH26-REVIEW.md](.archify/CH26-REVIEW.md) 与 [最终哈希](.archify/review/ch26-artifacts.json)。保留旧会话历史，不用它替代本轮实测。

| 旧说法 / 旧实验 | 当前结论与条件 | 固定源码与记录 |
| --- | --- | --- |
| Loader 继承 SecureClassLoader，CodeSource 指向 UNTRUSTED_CODEBASE | 9.4.0 继承 ClassLoader，用普通 defineClass；以固定版本实现为准 | [Loader](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/modules/lang-painless/src/main/java/org/elasticsearch/painless/Compiler.java#L51-L95) |
| findClass 只认 Lookup，因此 JVM 无法加载其他类 | findClass 支持 additionalClasses 与 Lookup，仍存在父加载器委派；File 拒绝的直接证据是语义检查 | [类型检查](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/modules/lang-painless/src/main/java/org/elasticsearch/painless/phase/DefaultSemanticAnalysisPhase.java#L1807-L1825) |
| 缓存 key=context+源码+params（动画），或仅 context+源码（正文） | 键含 projectId、lang、解析后的 source、context、编译 options；执行 params 不在键中 | [CacheKey](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/server/src/main/java/org/elasticsearch/script/ScriptCache.java#L207-L237) |
| 同一句脚本整个集群生命周期通常只编一次 | 当前节点缓存可复用；容量、过期、重启、配置替换或不同键均可能导致重编译 | [缓存生命周期](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/server/src/main/java/org/elasticsearch/script/ScriptCache.java#L60-L70)、[配置替换](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/server/src/main/java/org/elasticsearch/script/ScriptService.java#L829-L857) |
| 执行期没有查表；eval 必每次重新理解字符串 | Painless 缓存编译产物，def 的成员解析仍可在执行期查 runtime Lookup；不泛化所有 eval 实现 | [Def.lookupMethod](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/modules/lang-painless/src/main/java/org/elasticsearch/painless/Def.java#L179-L206) |
| Lookup 实现完全没有 Class.forName | 普通未知类型无任意加载兜底；已允许元素类型的数组分支存在 Class.forName | [类型/数组分支](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/modules/lang-painless/src/main/java/org/elasticsearch/painless/lookup/PainlessLookupUtility.java#L89-L153) |
| 字节码常量池只能含 txt 白名单类型 | 编译生成还涉及 factory、运行支持与动态调用基础设施；不作这种绝对保证 | [生成与 factory](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/modules/lang-painless/src/main/java/org/elasticsearch/painless/PainlessScriptEngine.java#L100-L112) |
| new File 会建磁盘文件；用路径不存在证明安全 | File 构造本身也不创建文件；本课定位默认语义拒绝，不虚构本轮磁盘或 API 实测 | [visitNewObj](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/modules/lang-painless/src/main/java/org/elasticsearch/painless/phase/DefaultSemanticAnalysisPhase.java#L1790-L1825) |
| script_score 永远完全替换；function_score 总乘一层 | 本课默认 boost=1 用脚本分数；实现再乘外层 boost；function_score 组合由 boost_mode 等决定 | [返回分数与 boost](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/server/src/main/java/org/elasticsearch/common/lucene/search/function/ScriptScoreQuery.java#L320-L340) |
| 每篇命中文档都必执行 script_score | 实际评分需求与收集影响执行；不需分数且无 minScore 时存在委托内层查询分支 | [createWeight](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/server/src/main/java/org/elasticsearch/common/lucene/search/function/ScriptScoreQuery.java#L91-L105) |
| text 默认 .value 会读取分析后的词来算数字 | 默认 text 无 doc values 且禁 fielddata，不能直接当数值读取；实验显式 keyword/long/double 与 strict mapping | [本章注册表](experiments/ch26.js)；数值读取条件显式列出 |
| simulate 的 fullname 在 docs[0]._source | 普通 simulate 结果为 docs[0].doc._source，模拟不写入索引 | [doc 包装](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/server/src/main/java/org/elasticsearch/action/ingest/WriteableIngestDocument.java#L119-L132) |
| stored ingest 不缓存 factory，等同完全不缓存编译 | processor 不长期持有预编译 factory；执行重新解析当前 stored source，ScriptCache 仍可命中 | [processor 创建](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/modules/ingest-common/src/main/java/org/elasticsearch/ingest/common/ScriptProcessor.java#L124-L139)、[stored 解析](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/server/src/main/java/org/elasticsearch/script/ScriptService.java#L607-L616) |
| test execute 返回 Object；score context 固定 404 个类 | 默认 test 返回值被序列化为字符串；context API 为内部调试接口，类数由版本和扩展决定 | [test 返回字符串](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/modules/lang-painless/src/main/java/org/elasticsearch/painless/action/PainlessExecuteAction.java#L649-L655)、[内部 API](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/modules/lang-painless/src/main/java/org/elasticsearch/painless/action/PainlessContextAction.java#L48-L55) |
| update 固定 _version=2；失败 PUT 证明同名管道永远不存在 | 版本取决于历史；失败不删除同名旧资源。新增空白前提、固定 ID、计数、等待和清理后 404 对照 | [45 卡顺序](.archify/review/ch26-operations-order.json)；真实重做未实测 |
| null 直接恢复默认 true；可以清掉未知原覆盖 | null 删除指定 transient 键；E 及相应设置清理只在起步两层无该键且节点基线 true 时执行 | [设置层合并](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/server/src/main/java/org/elasticsearch/cluster/metadata/Metadata.java#L1680-L1688) |

### 第二十七章重构校对

| 网页旧说法 | 修正 | 依据 |
| --- | --- | --- |
| “你写的一行已经是执行模型”、Unix pipe是同一件事、每命令让表变小 | 管道规定输入关系与结果语义；解析/分析/优化完整计划，物理算子可合并下推，SORT改序、EVAL可加列 | [组合计划](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/x-pack/plugin/esql/src/main/java/org/elasticsearch/xpack/esql/parser/LogicalPlanBuilder.java#L202-L219)、[验收](.archify/CH27-REVIEW.md) |
| PushDownAndCombineFilters直接下推Lucene；profile名称直接证明内部range且只有两条Driver | 逻辑移动与PushFiltersToSource物理翻译分开；可下推部分合入query、剩余过滤保留。真实profile有中转Driver；算子名称不足以证明具体range | [物理翻译](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/x-pack/plugin/esql/src/main/java/org/elasticsearch/xpack/esql/optimizer/rules/physical/local/PushFiltersToSource.java#L109-L143)、[两轮profile及残留过滤](.archify/review/ch27-es-review.json) |
| AVG分母是过滤后的全部行数；先局部再合并就一定是原索引全集 | 分母是有效字段值Count：四篇含多值/缺失/null时有效值3、sum70；聚合输入受前置LIMIT影响，225/200对照。空输入无BY一行AVG=null/COUNT(*)0 | [有效值计数](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/x-pack/plugin/esql/compute/src/main/java/org/elasticsearch/compute/aggregation/CountAggregatorFunction.java#L71-L123)、[真实API](.archify/review/ch27-es-review.json) |
| Page只剩views列，默认约256KB固定切批；Driver单线程即整个执行模型 | Page可带文档位置等实现列，单位置可空/单/多值；256KiB是按估算行宽求批次的目标，不是固定大小或上限。Driver一条单线程链，多Driver可并行 | [pageSize分支](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/x-pack/plugin/esql/src/main/java/org/elasticsearch/xpack/esql/planner/LocalExecutionPlanner.java#L1742-L1759)、[源码审计](.archify/review/ch27-source-review.json) |
| ES|QL没有_score、全文排名必须回_search、列式就不会读_source | 9.4支持MATCH与METADATA _score / _source；本课STATS不请求评分。没有hits包装不代表没有评分能力 | [固定元数据文档](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/docs/reference/query-languages/esql/esql-metadata-fields.md#L24-L34)、[MATCH实测](.archify/review/ch27-es-review.json) |
| 固定版本文档表把_score写float，验收初稿沿用该断言 | 本轮_score列响应double；MetadataAttribute明确注册DataType.DOUBLE。文档/断言冲突按运行与固定源码纠正，失败原响应保留 | [DOUBLE注册](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/x-pack/plugin/esql/src/main/java/org/elasticsearch/xpack/esql/core/expression/MetadataAttribute.java#L45-L61)、[失败证据](.archify/review/ch27-es-review-score-type-diagnostic.json) |
| 默认Limit999/1000固定；DSL卡只过滤_id却宣称响应含_source | 普通FROM默认输出1000/最大10000可配置，非聚合输入上限；profile内部计数不当契约。DSL保留实际hits与_source，size0空数组也保留 | [输出限制](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/docs/reference/query-languages/esql/_snippets/common/result-set-size-limitation.md#L1-L47)、[原14卡响应](.archify/review/ch27-original-responses.json) |
| 14卡缺完整等待、显式mapping、首次/重复和搜索视图重置 | 原14ID保留，4组42卡；两索引1P0R/strict、固定ID/显式refresh/green/count、关闭自动refresh排除竞态、D恢复200、点名清理并HEAD404，两轮真实验收 | [注册表](experiments/ch27.js)、[操作顺序](.archify/review/ch27-operations-order.json)、[验收](.archify/CH27-REVIEW.md) |

### 第二十八章重构校对

| 网页旧说法 | 修正 | 依据 |
|---|---|---|
| warm后“再满24h”进入delete；默认零点无条件适用于所有索引 | 本课无origination_date时warm2h/delete24h共用rollover零点，不逐相累加；显式origination_date优先分支另说明 | [起算与门槛](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/x-pack/plugin/ilm/src/main/java/org/elasticsearch/xpack/ilm/IndexLifecycleRunner.java#L123-L175) |
| 初始化必须第一轮poll后发生；new为稳定响应，rollover最多迟到一轮、约80秒完成 | 周期与状态变化runner入口不同；new可能已推进。等待hot/step、alias、新代存在，poll不构成完成上限 | [服务分工](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/x-pack/plugin/ilm/src/main/java/org/elasticsearch/xpack/ilm/IndexLifecycleService.java#L453-L568)、[两轮真实API](.archify/review/ch28-es-review.json) |
| “须在一分钟内改策略”，自动ID重复写改变文档数 | 保留原20ID；显式min_docs2+固定ID+refresh，一篇保持等待，观察缓存后写第二篇放行；40操作卡两轮重做 | [注册表](experiments/ch28.js)、[验收](.archify/CH28-REVIEW.md) |
| 每次PUT都version+1；只改条件必然刷新 | 同策略与安全headers可no-op；刷新还看缓存、非ERROR、当前步骤存在、解析及实际StepKey集合 | [no-op](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/x-pack/plugin/ilm/src/main/java/org/elasticsearch/xpack/ilm/PutLifecycleMetadataService.java#L123-L136)、[资格与集合](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/x-pack/plugin/core/src/main/java/org/elasticsearch/xpack/core/ilm/PhaseCacheManagement.java#L88-L251) |
| data stream省掉模板接力；模板不能带任何alias；缺is_write_index=true都失败 | data stream仍需ILM模板设置，省手工rollover alias/bootstrap；只禁止重复声明rollover alias本体；单目标经典alias有隐式写分支 | [alias兼容分支](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/x-pack/plugin/core/src/main/java/org/elasticsearch/xpack/core/ilm/WaitForRolloverReadyStep.java#L127-L193)、[重复alias检查](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/server/src/main/java/org/elasticsearch/action/admin/indices/rollover/MetadataRolloverService.java#L612-L639)、[模板应用](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/server/src/main/java/org/elasticsearch/cluster/metadata/MetadataCreateIndexService.java#L976-L1005) |
| min_docs暗门混同本课显式参数；allocate笼统列hot/warm | 默认只在没有文档min条件时补min_docs1，本课显式2；至少一max且全部min，max_primary_shard_size看最大主片；allocate属warm/cold | [默认条件](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/x-pack/plugin/core/src/main/java/org/elasticsearch/xpack/core/ilm/WaitForRolloverReadyStep.java#L234-L275)、[动作顺序](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/x-pack/plugin/core/src/main/java/org/elasticsearch/xpack/core/ilm/TimeseriesLifecycleType.java#L49-L82) |
| indexing_complete暗示只读；删策略靠引用计数；poll=null总回10m | 该标记不等于index.blocks.write；删除扫描索引策略名；null去掉该层覆盖，有原配置须恢复原值 | [策略扫描](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/x-pack/plugin/ilm/src/main/java/org/elasticsearch/xpack/ilm/action/TransportDeleteLifecycleAction.java#L78-L100)、[两轮恢复原值](.archify/review/ch28-es-review.json) |

### 第二十九章重构校对

| 网页旧说法 | 修正 | 依据 |
|---|---|---|
| CONTINUE就是“不是我的凭据”；Realms错密码CONTINUE后由链生成统一异常 | CONTINUE可带失败信息；本版本错Basic由consumeNullUser→authenticationFailed失败回调生成用户文案 | [链迭代](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/x-pack/plugin/security/src/main/java/org/elasticsearch/xpack/security/authc/AuthenticatorChain.java#L122-L195)、[Realm失败](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/x-pack/plugin/security/src/main/java/org/elasticsearch/xpack/security/authc/RealmsAuthenticator.java#L288-L315) |
| handleNullToken意味着从未抽出任何token | 已抽取的伪造ApiKey校验失败也可到该方法；是否回退受context和匿名配置决定 | [回退条件](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/x-pack/plugin/security/src/main/java/org/elasticsearch/xpack/security/authc/AuthenticatorChain.java#L270-L320)、[两轮真实API](.archify/review/ch29-es-review.json) |
| reserved永远第一，LDAP不认Basic | 默认列表与成功缓存后的实际校验顺序分开；LDAP/AD等用户名密码Realm也可认Basic | [缓存重排](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/x-pack/plugin/security/src/main/java/org/elasticsearch/xpack/security/authc/RealmsAuthenticator.java#L388-L407)、[Basic抽取](chapters/ch29.html#auth-chain) |
| 同时塞ApiKey+Basic则API Key赢；一次请求只能有一个主体 | 双Authorization值真实400，不演示凭据后备；普通认证得到一份Authentication，run-as/附加认证另有流程 | [两轮双头请求](.archify/review/ch29-es-review.json)、[抽象边界](chapters/ch29.html#auth-model) |
| 9.4.0总有Basic+ApiKey两挑战 | 本课无匿名、token service关闭、API Key开启才是该两项；挑战列表取决于配置 | [挑战汇集](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/x-pack/plugin/security/src/main/java/org/elasticsearch/xpack/security/Security.java#L1503-L1528)、[真实服务开关](.archify/review/ch29-es-review.json) |
| _authenticate免授权；索引授权只查checkIndicesAction | 自查经过同用户授权分支获准；索引还解析具体资源并建立访问控制 | [同用户授权](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/x-pack/plugin/security/src/main/java/org/elasticsearch/xpack/security/authz/RBACEngine.java#L205-L267)、[索引访问控制](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/x-pack/plugin/security/src/main/java/org/elasticsearch/xpack/security/authz/RBACEngine.java#L418-L455) |
| FLS/DLS逐个AND再削一刀 | 普通角色允许权限组合；同资源DLS组合不逐个AND，不受限授权可去掉限制；本课未实测许可扩展 | [合并条件](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/x-pack/plugin/security/src/main/java/org/elasticsearch/xpack/security/authz/store/CompositeRolesStore.java#L748-L762) |
| 关闭安全人人是匿名superuser；_security任意URL都400；available只表示发行版存在 | 无该认证授权且不构造匿名superuser；仅指定路由400，任意URL/方法另判断；available含许可可用性 | [Handler注册](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/x-pack/plugin/security/src/main/java/org/elasticsearch/xpack/security/Security.java#L1847-L1856)、[指定API对照](.archify/review/ch29-es-review.json) |
| 重复删除用户/角色仍200；缓存残留后“下次完整认证必然失败” | 实测重复404 found=false；删除用户成功清理Realm缓存，本课新请求401，不推断在途请求/其他凭据失效 | [删除缓存](https://github.com/elastic/elasticsearch/blob/2e8528e92361c3399724226deaf2b46f933e925b/x-pack/plugin/security/src/main/java/org/elasticsearch/xpack/security/authc/esnative/NativeUsersStore.java#L579-L606)、[两轮清理与重做](.archify/review/ch29-es-review.json) |
| 原实验只有拒绝，缺少read成功数据、重做语义；用户JSON密码进控制台URL | 19原ID保留，5组32卡，显式mapping/固定ID/refresh；允许/拒绝/权限自查及点名清理；用户卡控制台入口手动填写，密码不进URL | [注册表](experiments/ch29.js)、[验收](.archify/CH29-REVIEW.md) |

## 第三十章重构校对（ES 9.4.0）

| 旧说法 | 修正 | 依据 |
|---|---|---|
| from+size窗口在扇出前检查，10010是getTopDocsSize抛出的错误 | 分片DefaultSearchContext.preProcess读取窗口设置、主Query前检查；协调getTopDocsSize是归并窗口算术，rank有分支 | 固定源码与两轮400 failed_shards；[CH30-REVIEW](.archify/CH30-REVIEW.md) |
| usage包含非法search_type次数，可当本课搜索/成功数 | prepareRequest和后置检查后、consumer前计数；非法类型不计，窗口失败计；无并发每卡一次时本课增量5 | BaseRestHandler.handleRequest；两轮N+5实测 |
| _refresh用_shard过滤；每次刷新必开新段 | 返回复数_shards，实测1/1/0；刷新不保证每次创建新段，也不是flush提交证明 | 两轮真实_refresh；Engine与本课读取视图说明 |
| listener意味着等待不占线程；RoutingTable必是所有节点同时最新的真理 | listener仅是结果协议，具体调度另查；本次读取一份状态快照，不保证全节点同时最新 | SearchService.executeQueryPhase、TransportSearchAction.executeRequest |
| match单token必走SHOULD；每片固定回from+size；Fetch只取_source；单片能证明两跳 | 单token可直接词项查询；候选可少于窗口；Fetch也取其他字段；普通单片无rank可合并Query/Fetch | 固定源码、单节点单片响应边界 |
| realtime GET根本不看searcher、必从translog读；关闭定时刷新保证所有结果绝对零竞态 | GET响应不证明读取来源；读者取得/保留及外部刷新影响结果，固定mapping并禁外部刷新；完整清理重建恢复前提 | 两轮SEARCH0/GET200/非实时GET404/refresh后SEARCH1 |
| Painless、安全等全是另一入口，不在搜索链；catch文案永远不可改；入口永远只能HTTP | Painless可参与_search；认证与授权分层；测试断言保护具体条件，不等于本轮已执行；内部算法可沿已确认调用点深入 | 固定生产/测试源码与章节适用范围 |

## 会话日志

### 2026-10-14（ch30 全景回顾与方法论重构）
- 只处理ch30，保留原13实验ID与ch30-finale七步ID；按七段式重写并补齐条件/源码链接、目录/图解跳转、上下课/课程入口与已读进度。5组20卡，2交互图/2路径动画/1机制动画；统一880px阅读列与双主题。
- 重点勘误见上表：窗口分片预处理位置、usage计数边界、_shards复数、单片优化/异步签名/读者视图/Painless参与搜索。固定ES commit核对13文件24范围；未运行Gradle源码测试。
- 官方Archify3.0.1：当前搜索图review-4、方法图review-3；validate/deliver/strict check均showcase9/9、零错误/警告、零交叉绕行，native browser-check全部pass。只改JSON，正式CLI再生成；旧失败/布局证据保留。
- 真实API：9200匿名单节点ES9.4.0/Lucene10.4.0，两轮20卡（共40次）均通过；usage均N+5，SEARCH0/实时GET200/非实时GET404/刷新后SEARCH1；最终本章索引不存在。未实测多节点网络、安全开启/PIT/rank/kNN/跨集群与性能。
- 独立HTTP：两图各4桌面尺寸双主题；章节6宽度双主题，边界误差≤1px、图节点全部包含、页面/iframe无横向溢出；主题/探索/关闭/键盘/暂停后重播/reduced motion/七步播放器/进度/目录/20条深链/Pages前缀通过。ES请求在UI验证中明确abort，与真实API证据分开。
- 实际查看31张最终截图/7联系表；手机图概览可探索/放大/展开，机制SVG和源码表局部滚动另在390/320双主题通过。记录与SHA-256绑定见[CH30-REVIEW](.archify/CH30-REVIEW.md)、review/ch30-artifacts.json。
- node --check、展开机制快照figwidth、node tools/check.mjs通过，全站823操作/22机制动画。本轮代码、图源、产物及验收记录按授权提交并推送origin/main；Git结果与提交链接见交付。


### 2026-10-13（ch29 安全机制重构）

- 按规范只读/改本章及首页对应卡片，不通读tutorial、不用子代理；已有.gitignore修改保留、不纳入本轮提交。固定9.4.0/10.4.0，真实源码Git 19文件/37段核对，校正认证回调、Realm缓存、null-token回退、双头/挑战、自查与索引授权、关闭安全/角色组合及重复清理，详见上表。
- 原19实验ID与七步机制ID保留；5组32卡，1P0R/strict keyword/refresh_interval=-1，固定ID显式refresh。管理员准备，alice读取/搜索200与cluster/CAT/创建/写入/范围外403、自查200对照；9200/9201端点与认证显式固定。
- **真实API两轮各32卡通过**，每轮另10项重复/副作用/双Authorization观察；重复删身份404 found=false，双Authorization400，三种401双挑战，403无挑战。finally逐项点名清理确认资源不存在，两个节点留跑。原始响应与历史失败保留，[API记录](.archify/review/ch29-es-review.json)。未实测真实密钥、外部Realm、TLS、多节点、匿名/run-as/附加认证、FLS/DLS与性能。
- 两幅官方Archify3.0.1 workflow-v2/trace只改JSON生成：当前Basic review-2、RBAC review-4，validate/deliver/strict/browser-check全部PASS，showcase9/9、零错误/警告，原生file浏览器可用。初稿高度、一次路由交叉及HTTP390px裁切按诊断修复；旧收据保留。许可、字体说明与delivery哈希保留。
- HTTP两图4桌面尺寸×双主题、章节6尺寸×双主题通过；桌面880px，390正文362px、320正文292px，边界≤1px、页面/iframe不横溢、节点完整。主题/探索/键盘/展开/暂停外层重播/reduced-motion/七步/目录/已读、31请求深链+含密码body手动控制台入口、/es_web/前缀通过；ApiKey头不进深链的限制已明确。表格/机制仅自身横滑；HTTP自动ES流量abort，不代替真实API。
- 已实际view_image审阅7联系表（24章节/图截图+全部7机制快照），另看完整浅色Basic与深色RBAC；手机图为总览，通过探索/展开/正文读细节。首图左侧成功绕行可追踪；独立图最小SVG字7.258/7.466px，节点字8.295/8.533px。
- 站点816卡/22动画/30正式页、JS语法、figwidth、diff、19原ID/32有序唯一槽位、GET/HEAD无body和.nojekyll通过。[验收](.archify/CH29-REVIEW.md)、[源码](.archify/review/ch29-source-review.json)、[HTTP](.archify/review/ch29-http-review.json)、[产物绑定](.archify/review/ch29-artifacts.json)分别留存；按授权自动提交推送origin/main，交付另核对GitHub提交与Pages。

### 2026-10-13（ch28 索引生命周期管理重构）

- 已按序读取规范，仅处理ch28、首页对应卡片及证据；不重读tutorial、不使用子代理。开工与origin/main一致，已有.gitignore修改保留，不纳入提交。
- 固定ES9.4.0提交2e8528e92361c3399724226deaf2b46f933e925b / Lucene10.4.0；18文件/30行段源码审计。校正两种时钟、同一rollover零点、origination_date条件、调度非期限、相缓存安全资格、PUT no-op、模板/alias/data stream边界、indexing_complete与清理原值；详见上表。
- 原20实验ID与七步机制ID保留，2组40操作（前置3/A23/B7/清理7）。1P0R/strict/refresh_interval=-1、固定ID显式refresh；min_docs2屏障消除一分钟内改策略竞态。两交互图/两trace，880px统一阅读列与共用主题/重播控制。
- **真实API两轮各40卡通过**，状态等待产生81/85请求，每轮7补充观察：A活v2/旧缓存v1、两代alias翻转/新代模板托管/旧complete；B条件改10m缓存v2；同策略PUT no-op仍v2、重复写updated200、重复创建400、三个索引分别HEAD404。点名清理模板/策略/索引，poll恢复前置原值及finally复核，完整原始响应见[API证据](.archify/review/ch28-es-review.json)。
- 官方Archify3.0.1两workflow v2，zh-CN/showcase/trace、逐节点固定源码、真实--repo-root；仅改JSON正式finalize。当前validate/deliver/strict check/browser-check全通过，9/9且0错误0警告；当前本机file检查可用。phase-cache初稿高度失败、rollover初稿HTTP字偏小诊断保留，按布局测量重新生成；当前收据rollover review-3 / cache review-2。
- HTTP两图4桌面尺寸×双主题、章节6宽度×双主题；880px列/边界≤1px、整页与iframe不横溢、节点完整。900px桌面/≤800px620px嵌入；主题/源码探索/Enter与Escape/暂停后外层重播/展开/reduced motion/七步/目录/已读/40控制台请求和Pages前缀全通过，JS/资产无错误。源码表与机制SVG仅局部滚动。
- 已实际view_image审阅7联系表（24章节/图截图+全部7机制快照）及完整浅色rollover、深色cache图。手机图作路径总览，细节用探索/展开/正文；绕行建议实际审阅后可追踪，无交叉遮挡。源码、原生、HTTP、API、视觉与最终SHA分别记录于[CH28-REVIEW](.archify/CH28-REVIEW.md)与[产物绑定](.archify/review/ch28-artifacts.json)。warm2h/delete24h长时动作、跨节点/CCR/快照/data stream及认证权限未实测。
- node tools/check.mjs：30正式页 / **803操作卡 / 22机制播放器**；JS语法、figwidth、源码/HTTP/局部滚动/机制与diff检查通过。按持久授权提交推送origin/main，提交与Pages交付另核对。

### 2026-10-13（ch27 管道查询语言重构）

- 已按序读取AGENTS/STATUS/PLAN/CHAPTER_STANDARD/CLAUDE；仅ch27、首页对应卡片及本轮证据，未重读tutorial、未用子代理。开工fetch与origin/main一致；原.gitignore修改保留，不纳入提交。
- 固定ES9.4.0提交2e8528e92361c3399724226deaf2b46f933e925b / Lucene10.4.0；19文件/31精确行段核对。校正管道语义/计划、下推分类、AVG有效值计数/空输入、Page/Driver/256KiB目标、前置LIMIT与输出截断、MATCH/_score/_source能力及_score的DOUBLE注册，勘误见上表。
- 原14实验ID和ch27-esql-pipeline七步保留，4组42操作（前置3/A14/B7/C6/D8/清理4），两交互图/两trace。专属两索引显式1P0R/strict/refresh_interval=-1，固定ID、局部green/count/refresh，D组删除六号并refresh恢复200，再点名删除两索引和HEAD404完整重做。
- **真实API两轮各42卡通过，另13补充观察通过**：主值200/175/150、LIMIT前225/后200；类型400、三个路由方法405；DSL真实_source/size1仍均值200；四篇有效值3/sum70/mean≈23.333333、空聚合null/0；MATCH两行正分数且列double；未刷新GET可见/FROM5篇、刷新225、恢复200。补充updated200/重复创建400/strict400后正确200/LENGTH残留FilterOperator与162.5/重复清理404，两索引最终不存在。真实响应及两次初稿失败诊断保留，无合成响应或集群设置修改。
- 官方Archify3.0.1最终两幅workflow v2，zh-CN/showcase/trace、真实固定checkout与逐节点源码；只改JSON并正式finalize。当前validate/deliver/strict check/browser-check全通过，showcase9/9、0错误0警告；本机原生file检查实际可用，不把旧云限制沿用。旧dataflow原生通过但手机裁切，改为两列Page数据流程；再据测量展开纵向，当前AVG收据review-2，原稿/失败记录保留。
- HTTP两图4桌面尺寸×双主题、章节6宽度×双主题通过，880px列/边界≤1px/整页与iframe不横溢/节点完整。900px桌面嵌入、≤800px600/560px；探索源码/关闭/键盘/主题/暂停后外层重播/展开/reduced-motion/七步/目录/已读/42控制台请求及认证端点raw/Pages前缀通过，无JS/资产错误。390/320表和旧SVG仅局部横滚。
- 实际view_image审阅7联系表（24最终截图+7完整机制快照），另看完整两图与裁切诊断；手机图为路径总览，细字通过探索/展开/正文读取。源码/原生/HTTP/API/视觉与最终SHA分别记录于[CH27-REVIEW](.archify/CH27-REVIEW.md)及[产物绑定](.archify/review/ch27-artifacts.json)。跨机器Exchange/性能、异步结果生命周期和安全权限未实测。
- node tools/check.mjs：30正式页 / **783操作卡 / 22机制播放器**；JS语法、figwidth、源码/HTTP/局部滚动/七步与diff检查通过。按持久授权提交并推送origin/main，提交与Pages交付结果另核对。


### 2026-10-13（ch26 脚本引擎重构）

- 已读 AGENTS/STATUS/PLAN/CHAPTER_STANDARD/CLAUDE，仅重构 ch26 与首页对应卡片；开工 fetch 与远程一致，保留此前更新及日志。
- 固定 ES9.4.0 提交 `2e8528e92361c3399724226deaf2b46f933e925b` / Lucene10.4.0，29 文件 / 55 区间字节与行号核对。重写上下文、允许列表、ClassLoader、缓存键/失效、def 动态分发、评分 boost、stored ingest、响应路径与 null 恢复条件；勘误见上表。
- 保留全部20实验ID与 `ch26-script-compile` 七步；5组实验共45卡（前置6/A11/B2/C8/D5/E6/清理7），显式1P0R/strict mapping、固定ID/refresh/count、参数编译统计对照、设置来源确认、点名清理与重做。
- 两幅 workflow v2 使用官方 Archify3.0.1 JSON/finalize、zh-CN/showcase/trace、真实源码身份与 --repo-root；两幅 validate/deliver/strict check 9/9、零错误/警告，首次布局均通过、无JSON修复。原生 browser-check 都因 ERR_BLOCKED_BY_ADMINISTRATOR 失败，finalize整体 fail；独立 HTTP 不替代原生检查。许可保留。
- 独立 HTTP：两图4桌面尺寸×双主题、章节6宽度×双主题；880px列/边界≤1px/整页与iframe不溢出。桌面最小 SVG 字约6.888px、节点字约7.872px；两图嵌入1080px、≤800px640px，手机总览配节点探索/正文/展开。探索/键盘/主题/暂停后外层重播/展开/reduced-motion/七步/目录/已读/45控制台请求/认证端点raw标记/Pages前缀均通过，无JS/资产错误。390/320表与旧机制仅局部横滚。
- 实际查看7张联系表：24张章节/图截图与7张完整机制快照，双主题与手机已审阅，无观察到文字越框或节点遮挡；手机完整细节通过展开/探索读取。截图、当前源码与生成产物 SHA 绑定于 review/ch26-artifacts.json。
- **真实 ES API 未实测**：本轮官方容器09:05:23.13002633Z启动、09:05:26.510366235Z退出1，Could not set coredump filter / NoSuchFileException /proc/self/coredump_filter，9200探测退出7。45卡首次/重做、统计、错误链与设置恢复均未运行，没有合成响应，网页明确标注；见 ch26-es-runtime.json。
- `node tools/check.mjs`：30正式页 / **755操作卡 / 22机制动画**；JS语法、figwidth、固定源码/注册表、HTTP、局部滚动、七步与git diff检查通过。按持久授权提交并推送origin/main；提交及Pages结果在交付时核对。

### 2026-10-13（ch25 熔断器与背压重构）

- 同步origin/main无新增/分歧，按AGENTS/CHAPTER_STANDARD仅处理ch25；官方Archify3.0.1生成2幅workflow v2（拒绝/回滚、聚合预留覆盖），zh-CN/showcase/trace，真实固定ES仓库证据；保留并校正7步旗舰机制。
- 原14操作ID全部保留，重排为29卡：前提5、A6、B10、C4、清理4；固定ID与refresh/count/Green、request_cache=false、两层设置及运行时限额原基线恢复、计数增量和点名清理。既有覆盖时跳过B变更，未覆盖未知值。
- 22文件/58行段源码核对；修正预留重复相加、Parent超限复核、-1边界、统计/durability、BigArrays分配时序、terms优化语义、增量Bulk的>=条件与恢复口径。完整记录见[CH25-REVIEW](.archify/CH25-REVIEW.md)。
- 真实官方ES容器启动退出1：缺少/proc/self/coredump_filter，9200不通；API/清理/重做全部未实测，无合成响应。仅记录本次启动错误[运行证据](.archify/review/ch25-es-runtime.json)。
- 两图validate/deliver/strict check均showcase9/9、0错误0警告；原生browser-check仍被file导航策略阻止，finalize整体fail，与独立HTTP pass分别记录。聚合图按44px共享通道诊断作1次JSON修复，保存初稿和诊断。
- 独立图1440/1600/1920/2048双主题、章节1920/1440/1024/768/390/320双主题通过；880px列与边界≤1px、iframe/整页无横向溢出。高度1080/640与980/620；桌面最小SVG字约7.041px、节点字约8.047px。
- 实际查看7张联系表（24张最终阅读/图解截图+7完整机制快照）；手机图为可展开/探索的路径总览，源码表与原SVG局部滚动，正文与解说保留。主题、暂停后外层重播、节点Enter/Escape、reduced motion、29控制台链接、Pages前缀和导航/进度通过，无JS错误。原生限制未改记为通过。
- node tools/check.mjs：30正式页/730操作卡/22机制；node --check、figwidth、源码/HTTP/局部滚动/七步快照与实际视觉审阅、diff检查通过。最终[哈希绑定](.archify/review/ch25-artifacts.json)单列API与原生浏览器限制。完成后按持续授权提交并推送origin/main。


### 2026-10-13（ch24 恢复与快照重构）

- 已读取 AGENTS、STATUS、PLAN、CHAPTER_STANDARD、CLAUDE，fetch 后 HEAD 与 origin/main 一致；只重构指定 ch24，主页只更新对应卡片。保留 880px、双主题、目录、已读进度和上下课导航，复用共用图解 CSS/JS。
- 当前 3 组 / 57 张操作卡（3 前提、A17、B13、条件 C14、10 清理），全部旧 20 IDs 保留；两幅官方 Archify workflow v2 中文 showcase/trace 图，保留 ch24-peer-recovery 七步机制动画并校正基线、操作来源、临时 Engine、复制与路由启动边界。
- 固定 ES v9.4.0 / Lucene 10.4.0 源码核对：26 文件 / 64 范围通过；站点结构、node --check、SVG 估宽通过，当前全站 30 正式页 / 715 操作 / 22 机制。
- 两图 validate、deliver、strict check 为 showcase 9/9、零错误/警告；原生 browser-check 仍因 file 导航 ERR_BLOCKED_BY_ADMINISTRATOR 失败，finalize 整体失败。图源修复与收据分开保留；独立 HTTP 不替代原生门禁。
- 独立 HTTP 两图 1440/1600/1920/2048 双主题、章节 1920/1440/1024/768/390/320 双主题及 57 控制台深链通过；节点包含、iframe/整页无横溢、同列左右差≤1px、主题/探索/关闭/键盘/暂停后外层重播/展开/reduced motion/导航/Pages 前缀通过。390/320 双主题的表格与旧 SVG 仅自身滚动。初次恢复图文字小于桌面标准，已按实测压缩 JSON 纵向排布重新 finalize 并复验。
- 已实际查看 7 张最终联系表（24 张双主题章节/图解截图 + 7 个机制步骤）及初次文字失败截图；视觉记录绑定当前源码与截图 SHA。手机图解为完整概览，细字用探索/展开；原表格与 SVG 局部滚动、播放器控制与解说可用。
- 实际重试官方 Compose ES 9.4.0：容器退出 1，setCoredumpFilter 因 /proc/self/coredump_filter 不存在失败，9200 无服务。全部真实 API、首次及清理后重做、multi-node peer、快照注册/增量/恢复未实测；没有合成响应或改运行策略。默认无 path.repo 与成功仓库扩展的预期明确分开。
- 本轮完成后按既有授权提交并推送 origin/main；交付提交和 ch24 阅读链接。详细源码/图源 SHA、收据、HTTP、截图和运行限制见 [.archify/CH24-REVIEW.md](.archify/CH24-REVIEW.md)。


### 2026-10-13（第二十三章按统一规范重构）

- 固定ES9.4.0/Lucene10.4.0，24目标源码文件/56精确区间核对PASS。区分默认后台目标计算与当前Master执行、已有副本优先、两种决定序及各动作准入、四维权重/threshold、搬迁配对与replica恢复源、headroom条件与水位分支、默认flood429/普通write403、explain当前观察边界。正文/两图/七步/33卡/5问答/5陷阱/速记一致；未重读tutorial、未用子代理。
- 原11稳定ID和七步旗舰保留，增22共3组33操作（A13/B3/C13/清理4）；两专属索引显式1主1副或1主0副、auto-expand=false/strict，HEAD空前提、局部yellow/green与在途等待、过滤NO解除、普通写块恢复、固定文档ID和点名清理后两HEAD404重做。全站30正式页/678卡/22机制。首页仅更新ch23计数及去掉错误的先过滤后打分简介，共享CSS/JS及其他章节未改。
- 官方Archify3.0.1 Workflow v2 + Lifecycle v2，固定源码/真实checkout、只改JSON、许可保留；当前两图validate/deliver/strict check均showcase9/9、0errors/warnings、provenance current。**原生browser-check失败，finalize整体非成功**：file导航ERR_BLOCKED_BY_ADMINISTRATOR。迁移图初稿手机节点裁切真实失败，改JSON为三阶段两列后完整finalize，review-2与初稿/失败截图保留；未改生成HTML/策略或以HTTP替代原生门禁。
- **真实API及两轮重做未实测**：本轮实际重新Compose启动官方9.4.0进程，仍因缺/proc/self/coredump_filter、setCoredumpFilter抛RuntimeException/NoSuchFileException退出1。Docker和缓存镜像可用而9200无服务，实际启动错误已存，没有模拟API成功或修改ES绕过。多节点搬迁、真实磁盘压力/水位和性能均只据源码解释。
- 独立HTTP两图四档桌面/双主题、章节六档、≤880px/≤1px对齐、页面/iframe/全部节点容纳、探索关闭/键盘Enter/Escape/展开、暂停后重播/Enter、目录/已读、七步控制键盘、33条真实控制台导航method/path/body、endpoint/auth/raw、Pages前缀、reduced motion均PASS；390/320表格/旧SVG局部滚动PASS。实际查看7拼图覆盖24最终截图和全部7步。手机图为概览，细字探索/展开，正文/图注保留结论；旧机制局部横滑，标题省略而控制/步数/解说可读。图高桌面850/700、≤800px540/480。
- 站点、JS语法、figwidth、diff、11原ID/33有序唯一槽、GET/HEAD无body与.nojekyll PASS；源码/HTTP/滚动/机制/实际审阅记录绑定当前文件。[CH23-REVIEW](.archify/CH23-REVIEW.md)、[HTTP](.archify/review/ch23-http-review.json)、[运行限制](.archify/review/ch23-es-runtime.json)、[产物](.archify/review/ch23-artifacts.json)。按授权提交推送origin/main，远端与Pages交付另核对。

### 2026-10-13（第二十二章按统一规范重构）

- 固定ES9.4.0/Lucene10.4.0，21目标源码文件/65精确区间核对PASS；围绕选举资格与提交边界修正名单/角色、term先推进后收票、快照term、本地状态API及local弃用、pre-vote新鲜度/高任期信息、双多数/插件约束、accept/commit/apply、分区本地认知与请求不确定性、version差值/no-op。正文/两图/七步/18卡/5问答/5陷阱/速记一致；未重读tutorial、未用子代理。
- 保留原10稳定实验ID与七步旗舰，增8共3组18卡（A5/B3/C8/清理2），2交互图/2有限trace；显式1主0副/auto-expand=false/strict、HEAD空前提、局部green/初始化/迁移等待、配置读回、mapping首次/重复语义、点名清理和HEAD404重做。全站30正式页/656卡/22机制；首页只更新ch22计数，共享CSS/JS及其他章节未改。
- 官方Archify3.0.1 Workflow v2，首次固定源码/真实checkout，JSON生成，许可保留。两图validate/deliver/strict check均showcase9/9、0errors/warnings、provenance current；**原生browser-check失败，finalize整体非成功**：file导航ERR_BLOCKED_BY_ADMINISTRATOR。发布图review-2补beforeCommit默认/插件边界，旧图源与收据保留；独立HTTP不替代原生门禁。
- **真实API及两轮重做未实测**：云Docker与官方镜像可用，实际Compose启动后ES9.4.0因缺/proc/self/coredump_filter、setCoredumpFilter抛RuntimeException/NoSuchFileException退出1。已存真实启动错误，没有模拟响应、修改ES或绕过策略；多节点选举/分区/配置变更与时序仅据源码。
- HTTP两图四档桌面/双主题、章节六档、≤880px/≤1px对齐、页面/iframe/节点容纳、探索关闭/展开、暂停后重播/Enter、目录/已读、七步控制键盘、18条真实控制台导航method/path/body、endpoint/auth/raw、Pages前缀、reduced motion均PASS；390/320表格/旧SVG局部滚动PASS。实际看7最终拼图覆盖24截图及全部7步，收紧图框至桌面760/900、≤800px460/500；手机图为概览，细字探索/展开，必要说明在正文/图注。原生与API受限项单列。
- 站点、JS语法、figwidth、diff、10原ID/18有序唯一槽、GET/HEAD无body与.nojekyll PASS；当前源码/HTTP/滚动/机制记录绑定当前文件。[CH22-REVIEW](.archify/CH22-REVIEW.md)、[HTTP](.archify/review/ch22-http-review.json)、[运行限制](.archify/review/ch22-es-runtime.json)、[产物](.archify/review/ch22-artifacts.json)。按授权提交推送origin/main；远端与Pages状态交付另核对。




### 2026-10-13（第二十一章按统一规范重构）

- 固定 ES9.4.0/Lucene10.4.0，20源码文件/46精确区间核对；纠正字段/final与读缓存、隐藏Metadata.version、term/投票字段、API与批次数、no-op、pending执行项、Listener阻塞及本地可见/落后节点。正文/两图/29卡/5问答/4陷阱/速记一致；未重读tutorial、未使用子代理。旧2026-09-24记录保留为首次转写历史，以本次结果为准。
- 保留原16稳定ID，3组29卡（A10/B7/C8/清理4），2交互图/1有限trace/0机制播放器。显式配置/strict keyword/局部green/声明字段写入、本索引refresh恢复、no-op与元数据等待、点名删两索引重做；全站30正式页/648卡/22机制。共享CSS/JS与其他章节未改。
- 官方Archify3.0.1 Architecture与Workflow v2，首次附固定源码/真实checkout、只改JSON。当前静态图根收据、流程review-3；validate/deliver/strict check showcase9/9、0errors/warnings、provenance current，原生browser-check/finalize整体PASS。源码越界初稿拒绝、HTTP小字布局诊断及旧候选/收据保留；三职责纵向流程改善字径，许可保留。
- **真实API两轮各29卡PASS，另18补充请求PASS**：V1/V2/V3=402/405/405、414/417/417，创建均+3/写已知字段不变；5s设置变化与no-op版本406/406、418/418；metadata.version缺席，门槛1满足、最大long超时200无状态；term1只属本次历史。重复创建400/写updated且文档version2/strict未知字段400、green只读写403/恢复、重复删除404确认。最终两索引HEAD404、集群设置前后相同。初稿门槛0真实400、flat_settings过滤读回空对象守卫失败保留；修正后清理重做，不模拟响应。
- HTTP两图四档桌面×双主题、章节六档×双主题、880px/≤1px对齐、页面/iframe/节点完整、探索/来源/关闭/Escape/键盘/展开、暂停后外层重播、主题/目录/已读、29真实控制台导航与method/path/body、endpoint/auth/raw、Pages前缀、reduced motion PASS。静态图无motion属性/按钮，不假定still；桌面图高760/900、≤800px500/580。实际复看5拼图覆盖20当前截图，另看完整浅色流程；手机概览细字探索/展开、源码表自身横滑。关闭/静态态测试假设诊断保留，最终全量通过。
- 站点、JS语法、figwidth、diff、16原ID/29有序唯一槽位、GET/HEAD无body、.nojekyll PASS。验收[CH21-REVIEW](.archify/CH21-REVIEW.md)、[API](.archify/review/ch21-es-review.json)、[HTTP](.archify/review/ch21-http-review.json)、[哈希](.archify/review/ch21-artifacts.json)。多节点Diff/选举/落后追赶、全重启持久化、真实安全认证和性能未实测。按授权提交推送origin/main，交付另核对远端/Pages；原.gitignore修改不纳入。


### 2026-10-12（第二十章按统一规范重构）

- 固定ES9.4.0/Lucene10.4.0，17源码文件/25精确区间及Lucene公式核对；修正Query局部/全局窗口、Fetch解释、字段N/旧版本、Legacy倍数、业务乘零、单_score优化、rescore排序/窗口外权重和非realtime Explain。正文/图/七步/30卡/5问答/4陷阱/速记一致；未重读tutorial、未使用子代理。
- 保留原12稳定ID与七步旗舰，增18共3组30卡（A12/B12/C5/清理1），2交互图/2有限trace。显式配置/strict/stored source/standard/BM25/norms/Doc Values、局部green、bulk固定ID+refresh、点名清理重建。全站30正式页/635卡/22机制；共享CSS/JS和其他章节未改。
- 官方Archify3.0.1 Workflow v2，首次带固定源码/真实checkout，只改JSON。ranking当前review-3、Explain根收据；validate/deliver/strict check均showcase9/9、0errors/warnings、provenance current，原生browser-check和finalize整体PASS；旧候选/收据/HTTP截图保留，许可完整。
- HTTP两图四档桌面/双主题、章节六档、880px/≤1px对齐、页面/iframe/节点容纳、探索/关闭/展开、暂停后重播/Enter、主题/目录/已读、七步控制/键盘、30真实控制台导航method/path/body/endpoint/auth/raw、Pages前缀、reduced motion PASS。390/320表格/旧SVG局部横滑PASS。实际查看7拼图覆盖24最终截图及全部7步，另看独立浅色ranking/手机深色Explain；手机图为概览，细字探索/展开缩放，必要说明在正文/图注。
- **真实API两轮每轮30卡PASS，另13补充观察PASS**：单词b/a=.250692/.182322、双词a/b=.875469/.250692、boost2.2/字段N2/avgdl2；两个Explain/size1窗口/不匹配200/缺失404；weight2/业务乘积/乘零/replace；views排序/track_scores/单_score desc无sort数组；rescore窗口1/2、a≈4.559665翻盘、score desc成功/views或score asc400、窗口外query_weight2也翻倍；c使N3涨分、缺title的d仍N3；未刷写入GET可见而Explain404，refresh后200。重复创建400/写入updated200/清理404确认，最终本课索引HEAD404。验证器初稿的API字段/优化假设按真实响应纠正，复用已采集60请求，不伪造响应。
- 站点、JS语法、figwidth、diff、12稳定ID/30有序唯一槽位、GET/HEAD无body与.nojekyll PASS。验收[CH20-REVIEW](.archify/CH20-REVIEW.md)、[HTTP](.archify/review/ch20-http-review.json)、[真实API](.archify/review/ch20-es-review.json)、[artifacts](.archify/review/ch20-artifacts.json)。多节点DFS/PIT tie-break/其他rescorer/量化对照/性能未实测。按授权提交推送origin/main；远端/Pages交付时另核对，原有.gitignore修改不纳入。


### 2026-10-12(第十九章按统一规范重构)

- 固定ES9.4.0/Lucene10.4.0核对17源码文件/36精确区间；重排输入与hits、四层职责、候选截断/保守误差、avg与Pipeline、执行策略与资源。正文/两图/六步/卡片/5问答/4陷阱/速记一致；不重读tutorial、不用子代理。
- 原17稳定ID保留，3组30卡（A7/B15/C7/清理1）、2交互图/2有限trace/1六步机制。显式1主0副/strict/stored source/无管道/周期refresh关闭/request cache关闭；固定ID、三组局部green、bulk refresh、完整点名清理与重做。全站30正式页/617卡/22机制；共享CSS/JS与其他章节未改。
- 官方Archify3.0.1 Workflow v2，首次附固定源码/真实checkout，只改JSON。两图review-2：validate/deliver/strict check均showcase9/9、0errors/warnings、provenance current；原生browser-check与finalize整体PASS。初稿源码行号越界门禁拒绝，修正实际区间后通过，旧候选与失败收据保留；许可及HTML字体许可保留。
- HTTP两图四档桌面/双主题、章节六档宽度、880px/≤1px对齐、页面/iframe/节点完整、探索/关闭/展开、暂停后重播/Enter、目录/已读、六步控制/键盘、30真实控制台导航method/path/body/endpoint/auth/raw、Pages前缀、reduced motion PASS。390/320源码表/旧SVG局部横滑PASS。实际查看7张拼图覆盖24最终截图及全部6步，另查看独立旅程/深色手机候选图；手机图为概览，细字探索或展开缩放，必要说明在正文/图注。
- **真实API两轮每轮30卡PASS，另29重复性观察PASS**：小店3/3/2、月份2/2/3/1、range4/2/2，1 hit仍聚合8篇/query只books3；两片各11篇、cherry全局5；容量2→apple10/date4、other8/error7/桶0和3，默认13→apple10/cherry5、other7/error0，抬3→准确前三、other3但保守error5；key序apple/banana、other9/error0；两次bucket_sort仅cherry5/date4，terms.other仍7/0；apple均值42/10=4.2；20值size2/20的other18/0，两轮profile实为StringTermsAggregatorFromFilters/FilterByFilter。四索引settings/mapping、重复创建400/写入updated200/计数不增/重复清理404确认，最终HEAD四索引404。浏览器阻断ES自动执行，API单列；未实测多节点/slice/百万基数/故障/熔断/性能。
- 站点、JS语法、figwidth、diff、17稳定ID/30有序唯一槽位、GET/HEAD无body与.nojekyll PASS。验收[CH19-REVIEW](.archify/CH19-REVIEW.md)、[HTTP](.archify/review/ch19-http-review.json)、[真实API](.archify/review/ch19-es-review.json)、[artifacts](.archify/review/ch19-artifacts.json)。按授权提交推送origin/main；远端/Pages交付时另核对，原有.gitignore修改不纳入。

### 2026-10-12(第十八章按统一规范重构)

- 固定ES9.4.0/Lucene10.4.0：18源码文件/39精确区间及2个Lucene固定tag文件；重排Builder/Lucene改写、字段分析/工厂、词项/位置、评分/should门槛、缓存条件、两路收集和Explain。正文/两图/六步/卡片/5问答/4陷阱/速记一致。
- 保留原19稳定ID，3组34卡（A13/B9/C11/清理1）、2交互图/2有限trace/1六步机制；显式standard/keyword normalizer/strict/stored source/词向量、一主零副/无管道/周期刷新关闭/局部green/固定ID+refresh/点名清理与重做。全站30正式页/604卡/22机制；共享CSS/JS和其他章节未改。
- 官方Archify3.0.1 Workflow v2，首次附真实固定源码/checkout、仅改JSON。translation当前review-2，collection review-3；validate/deliver/strict check showcase9/9、0errors/warnings、provenance current，原生browser-check与finalize整体PASS。双列手机裁切修复为纵向独立路径，主收集路径直连；聚合绕行保留且实际审阅无交叉/语义错误。旧图源/收据/诊断保留，许可及HTML字体许可保留。
- HTTP两图四档桌面/双主题、章节六档宽度、880px/≤1px对齐、页面/iframe/节点完整、探索/来源/关闭/展开、暂停后重播/Enter、目录/已读、六步控制/键盘、34实际控制台导航method/path/body、endpoint/auth/raw、Pages前缀、reduced motion PASS。390/320源码表/旧SVG局部滚动PASS。实际查看24张最终截图与全部六步；手机图为概览，细字需探索/展开，必要解释在正文/图注。
- **真实API两轮每轮34卡PASS**：旧GET Explain两卡真实400缺query，POST后200；词项/保存位置/标点小写、text match/term/keyword normalizer、OR/AND/反向与间隔phrase、stop零词项none0/all4、validate OR、两入口Explain/别名false且含status约束；filter→must分数1.1608025→1.5174774，纯filter三篇0，should默认可选与显式门槛对照；post_filter聚合published3/draft1，query.filter只published3。另8条重复性观察确认重复创建400/写入updated200/删除404及实际mapping/settings。mapping冗余search_analyzer省略导致初始验收守卫失败，修正后针对性重做通过，最终父索引/别名HEAD404。浏览器阻断ES自动执行，真实API单列；未实测多节点/词图/模糊/缓存收益或性能。
- 站点、JS语法、figwidth、diff、19稳定ID/34有序唯一槽位、GET/HEAD无body与.nojekyll PASS。验收[CH18-REVIEW](.archify/CH18-REVIEW.md)、[HTTP](.archify/review/ch18-http-review.json)、[真实API](.archify/review/ch18-es-review.json)、[artifacts](.archify/review/ch18-artifacts.json)。按授权提交推送origin/main；远端与Pages在交付时另核对，原有.gitignore修改不纳入。

### 2026-10-12(第十七章按统一规范重构)

- 固定ES9.4.0/Lucene10.4.0核对15源码文件/43精确区间；重排上下文所有权/普通Query-Fetch/PIT读者、真实入口调度、三个查询字段、检查点与200ms缓存时钟、脚本保护与超时、PIT最新ID/完整sort/条件恢复。正文/两图/六步/卡片/问答/速记一致，原18稳定ID保留。
- 3组32卡（A8/B7/C15/清理2）、2交互图/2有限trace/1六步机制；显式mapping/设置/刷新、局部健康/上下文基线、完整顺序及点名清理重做。全站30正式页/589操作卡/22机制播放器，共享CSS/JS与其他章节未改。
- 官方Archify3.0.1 Workflow v2，首次附固定源码/真实checkout，只改JSON。context根收据、query review-2；validate/deliver/strict check showcase9/9、0errors/warnings、provenance current；原生browser-check与finalize整体PASS。旧query候选/收据保留，许可与HTML字体许可保留。
- HTTP两图四档桌面/双主题、章节六档宽度、880px/≤1px对齐、页面/iframe无横溢/节点完整、探索/固定来源/关闭/展开、暂停后重播/Enter、目录/已读、六步键盘与控制、32真实控制台导航method/path/body及endpoint/auth/raw、Pages前缀、reduced motion均PASS。390/320源码表/旧SVG局部滚动、3000篇bulk卡340px内滚动PASS。实际看26张截图及六步；手机图框收紧540px、表格列宽修复后复看，手机细字需探索/展开。早期导航等待/Chrome启动诊断不当通过，最终重试与回归通过。
- **真实API两轮每轮32卡PASS**：匿名单节点9200、build匹配；alias仅1且profile/explain含n过滤；旧500万循环真实400脚本保护，新合法基线total3003/took519与517ms、短查询200+timed_out（本例total仍3003）、严格429；PIT0→1→0、第一页1/2与完整[2,1]、写new刷新后旧第二页4/旧重搜1/2/4/新搜索多new，同PIT换查lazy得3，最新ID关闭num_freed1，关闭后404。清理后重做，最终两索引/别名HEAD404。浏览器阻断ES自动执行，真实API单列；未实测scroll/取消/多节点/并发故障/自动过期。
- 站点、JS语法、figwidth、diff、稳定ID/有序唯一槽位与.nojekyll PASS。验收[CH17-REVIEW](.archify/CH17-REVIEW.md)、[HTTP](.archify/review/ch17-http-review.json)、[真实API](.archify/review/ch17-es-review.json)、[artifacts](.archify/review/ch17-artifacts.json)。按授权提交推送origin/main；远端与Pages在交付时另行核对，原有.gitignore修改不纳入。

### 2026-10-12(控制台样式与交互修复)

- 独立控制台工作区与 CSS：连接栏、示例/历史页签、请求编辑器、响应视图；双主题、六档宽度、桌面并排/手机纵排，路径栏宽度保护与代码块内部滚动。章节内容、图解重构进度、共享阅读 CSS、图源及实验注册表未改。
- 修复深链整体解码截断 `|`、徽章检查错误端点、旧请求/旧连接检查覆盖新结果、损坏历史崩溃、无效 JSON 错发 NDJSON、Basic Unicode/密码空格和高亮文本转义。课程深链保留自动执行及 endpoint/auth alias/raw/Pages 前缀；预设和历史点击改为先填入编辑器。
- 新增请求停止/超时设置、JSON/NDJSON 格式化与原样发送、完整原文/响应头/复制回退、服务端错误摘要、Bulk 200 部分失败提示、空响应说明、历史清空和键盘操作。分词、search 线程池及 explain 示例的依赖/查询词修正；NDJSON 末尾换行不自动修复。
- **连接层与真实 ES 15/15、Chrome 浏览器 27/27 PASS**：9200 实际为 ES 9.4.0/Lucene 10.4.0；真实健康/CAT/HEAD/含 `|` 分词/非法 JSON 400/Bulk 成功、缺换行400、坏 source 条级400/点名清理均通过。六档320–1920px × 双主题无页面横溢；实际审阅桌面/390px浅深截图。取消竞态/超时/复制拒绝等客户端桩与真实 ES 结果分列；9201未启动，真实认证未验收。
- 站点检查全绿（30正式页/575卡/22播放器），JS语法与diff通过；本轮无 Archify 生成/原生门禁。证据与复现：[验收](.archify/review/console-20261012/REVIEW.md)、[连接层/真实ES](.archify/review/console-20261012/client-and-es.json)、[浏览器](.archify/review/console-20261012/browser.json)。按授权提交推送 origin/main；远端与Pages状态在交付时另行核对，原有 `.gitignore` 修改未纳入。

### 2026-10-12(第十六章按统一规范重构)

- 固定ES9.4.0/Lucene10.4.0核对13源码文件/30精确区间；重排搜索范围/EXTERNAL读者、两阶段职责、受控异步/归并调度、普通候选上限与窗口、profile证据、单片/DFS/批量与预过滤条件。正文/两图/七步/卡片/问答/速记一致，保留14稳定ID。
- 4组29卡（A6/B10/C7/D3/清理3）、2交互图/2有限trace/1七步机制。显式设置/mapping、局部健康、同组重置、完整顺序和点名清理；全站30正式页/575卡/22机制播放器。共享CSS/JS与其他章节未改。
- 官方Archify3.0.1 Workflow v2，首次附固定源码/真实checkout，只改JSON；当前两图review-2。validate/deliver/strict check均showcase9/9、0errors/warnings、provenance current；原生browser-check与finalize整体PASS。page-window可选绕行提示经实际浅深截图审阅，无交叉/含糊路径；旧图源/收据保留。
- HTTP两图四档桌面/双主题、章节六档宽度、880px/≤1px对齐、页面/iframe/所有节点完整、探索/固定来源/关闭/展开、暂停后外层重播/Enter、目录/已读、七步与键盘、29真实控制台深链请求内容、endpoint/auth alias/raw、Pages前缀及reduced motion均PASS；390/320表格/旧SVG局部滚动PASS。实际查看24张章节/图截图和7步快照，修复2/5步底部说明并复看、回归。手机细字需探索/展开，旧SVG局部滚动。
- **真实API两轮各29卡PASS**：匿名单节点9200、9.4.0/构建号匹配；分布12/9/9、候选上限28与最终10、3 searches/size1单fetch、source-off仍fetch、size0聚合sum465、超窗顶层/内层错误、合法空页、末页21..30、search_after1..5→6..10、重置后GET可见/count0→refresh/count1、单片query/fetch。清理后重建重做、最终HEAD两索引404。浏览器深链验收显式阻断ES自动执行，真实API单列；未制造多节点/部分失败/DFS/kNN/PIT并发场景。
- 站点、JS语法、figwidth、diff、14稳定ID/29有序唯一槽位和.nojekyll通过。验收[CH16-REVIEW](.archify/CH16-REVIEW.md)、当前证据[ch16-artifacts](.archify/review/ch16-artifacts.json)；按授权提交推送origin/main，远端提交和Pages部署在交付时单独核对。


### 2026-10-11(第十五章按统一规范重构)

- 固定ES9.4.0/Lucene10.4.0核对24源码文件/45精确区间；重写路由策略/创建版本、UTF-16LE哈希、同片碰撞与搜索范围、GET/搜索ARS差异、Final与动态副本、本地五态/恢复/关闭层次。正文、两图、七步机制、卡片、问答与速记同步，保留16稳定ID。
- 4组40卡（A17/B8/C7/D6/清理2）、2图/2条有限trace/1七步机制。显式standard/stored source/strict keyword/3主片/非分区/无管道/刷新/active条件；限定健康等待、错误恢复、首次/重复与点名清理。全站30正式页/560卡/22机制播放器。
- 官方Archify3.0.1，首次附固定源码/真实checkout，只改JSON；routing当前review-2、life当前review-3。两图validate/deliver/strict check showcase9/9、0errors/warnings、provenance current；原生browser-check与finalize整体均PASS。历史沙箱Chrome、画布比例与手机横排裁切诊断保留，纵向支线和intrinsic fit修复后HTTP通过。
- HTTP：两图四档桌面/双主题、章节六档宽度、880px/≤1px对齐、页面/iframe/所有节点完整、探索/来源/关闭/展开、暂停后外层重播/Enter、目录/已读、七步与键盘、40真实控制台深链及请求内容、endpoint/auth alias/raw、Pages前缀、reduced motion通过；390/320源码表与SVG局部滚动通过。实际查看24张最终截图；手机图细字需探索/展开缩放，旧SVG局部滑动。共享文件未改。
- **真实API两轮40卡PASS**：沙箱外9200实际提供9.4.0，build_hash匹配；0/0/2落点、同片缺省GET200/跨片404、无routing搜索2/错误routing0、required文档400/搜索200、Final拒绝后仍3与可读、yellow→green→yellow、closeGET实际400/index_closed_exception、open后数据保留及EXISTING_STORE/DONE。点名清理后重做，最后HEAD两索引404。初期探测失败不代表当前未实测；最终浏览器检查阻断console深链自动执行，API响应单独保存。
- JS语法、figwidth、diff、16稳定ID/40有序唯一槽位及静态路径/站点检查通过。验收[CH15-REVIEW](.archify/CH15-REVIEW.md)，证据绑定[ch15-artifacts](.archify/review/ch15-artifacts.json)；按授权提交推送origin/main，Pages部署完成未核验。


### 2026-10-11(第十四章按统一规范重构)

- 固定 ES9.4.0 核对10源码文件/39精确区间；章节约4238中文字符、lesson约2699。重写成功/失败写入、两套reader、日志追加/同步、safe commit与代次统计、flush可见性及合并历史保留；勘误同步正文、图、解说、卡片、问答和速记。
- 保留29原操作ID与ch14-write-path，新增17，共4组46卡（A10/B11/C13/D11/清理1）、2幅Workflow v2/2条有限trace/1个八步播放器。显式standard/stored source/strict mapping/1主0副/管道/refresh/耐久/年龄阈值、限定健康等待、async恢复、flush后仍不可搜、停止写入后merge、读回与四索引点名重复清理。全站30正式页/536卡/22机制播放器。
- 官方Archify3.0.1首次附固定源码与--repo-root，只改JSON；两图validate/deliver/strict check为showcase9/9、0errors/warnings、provenance current。原生file URL政策使browser-check及finalize整体FAIL；update.noticeRequired=false。HTTP独立检查分开记录。
- HTTP通过：两图四档桌面/双主题、章节六档宽度、880px/≤1px对齐、页面/iframe/所有节点容纳、探索/来源/关闭/展开、暂停后外层重播/Enter、目录/已读、八步机制控制与键盘、46实际控制台请求深链、endpoint/auth alias/raw传递、Pages前缀、reduced motion。390/320源码表和SVG局部滚动通过；24张截图实际复核。手机图细字需探索或展开缩放，旧SVG可局部滑动。共享文件未改。
- 站点、JS语法、figwidth、diff、29稳定ID/46唯一有序槽位、GET/HEAD无body与静态路径检查通过。真实API首次与清理后重做均未执行：9200拒绝连接、已知runtime缺/proc/self/coredump_filter；未循环启动/降版/改ES/伪造响应。验收[CH14-REVIEW](.archify/CH14-REVIEW.md)，证据绑定[ch14-artifacts](.archify/review/ch14-artifacts.json)；按授权提交推送origin/main，Pages部署未核验。

### 2026-10-11(第十三章按统一规范重构)

- 固定ES9.4.0核对20源码文件/46精确区间，章节约4286中文字符，重写NDJSON类型解析、增量与错误副作用、角色/分组/有序结果、路由创建版本、primary/复制/写后条件及refresh可见性；勘误同步图注、实验、问答、速记与六步机制解说。
- 原13稳定操作ID及ch13-bulk-group保留，增27卡，共4组/40卡，2幅Workflow v2/2条有限trace/1机制播放器。显式standard/stored source/strict mapping/分片/副本/管道/refresh/active/durability；局部等待、首次/重复、错误读回、周期恢复与三索引点名清理。全站30正式页/519卡/22机制播放器。
- 官方Archify3.0.1首次附固定源码与真实checkout，只改JSON；两图当前根收据，validate/deliver/strict check均showcase9/9、0errors/warnings、provenance current。原生file URL管理策略使browser-check及finalize整体fail，HTTP独立验收分开记录。
- HTTP通过：两图四档桌面/双主题、章节六档宽度、880px/≤1px对齐、页面/iframe/所有节点容纳、探索/来源/关闭/展开、暂停外层重播/Enter、目录/已读、六步机制与键盘、40实际控制台deep links及请求内容、四raw错误卡、endpoint/auth alias、Pages前缀、reduced motion。390/320源码表和SVG局部滚动通过；实际查看24张最终截图，手机图细字需探索/展开缩放。共享文件未改。
- 站点、JS语法、figwidth、diff、稳定ID/槽位/路径通过；真实API首次和清理后重做均未执行：9200拒绝连接、已知runtime缺/proc/self/coredump_filter，未伪造响应或修改环境策略。验收[CH13-REVIEW](.archify/CH13-REVIEW.md)，当前证据绑定[ch13-artifacts](.archify/review/ch13-artifacts.json)；按授权提交推送origin/main，Pages部署未核验。

### 2026-10-11(第十二章按统一规范重构)

- 固定 ES v9.4.0 提交核对 23 个源码文件 / 56 个区间，重写摄取 / 回写 / 路由边界、顺序与异步、模拟范围、失败恢复层级、两个管道槽、drop / final 约束与路由碰撞；章节约 4344 中文字，勘误同步图源、实验、问答与速记。
- 保留原 20 个稳定实验 ID，新增 28 卡，共 4 组 / 48 卡、0 原机制播放器；显式 standard / stored source / 动态映射 / 管道槽 / 分片 / refresh，限定健康等待、首次 / 重复差异、final 错误恢复；先点名删三索引，再逐条删五管道。全站 30 正式页 / 492 卡 / 22 机制播放器；本章 2 图 / 2 条有限 trace。
- 官方 Archify 3.0.1 的两幅 Workflow v2 首次附真实源码 checkout 与固定证据，只改 JSON。ingest-journey 当前根收据，failure-scope review-3；原生 validate / deliver / strict check 均 showcase 9/9、0 errors / warnings、provenance current。file URL 管理策略使原生 browser-check / finalize 整体仍 fail；初稿桌面比例与手机节点裁切的历史诊断 / 修复证据保留。
- 独立 HTTP 检查通过：两图四档桌面尺寸、章节六档宽度 / 双主题、880px 列 / ≤1px 对齐、页面 / iframe / 所有节点容纳、探索 / 来源 / 关闭 / 展开、暂停后重播 / Enter、目录 / 已读、48 张实际控制台深链与 method / path / body、端点 / 认证别名 / raw、Pages 前缀及 reduced motion。390 / 320px 源码表自身滚动通过。实际查看 20 张最终截图，长卡截图固定栏伪影另作捕获修复；手机图细字需探索 / 展开缩放。共享 CSS / JS 未改。
- 站点结构、注册 JS 语法、文字估宽、稳定 ID 与 diff 检查通过。9200 拒绝连接、运行时缺 /proc/self/coredump_filter，真实 API 首次 / 清理后重做均未执行，没有模拟 ES 响应或改运行策略。验收见 [.archify/CH12-REVIEW.md](.archify/CH12-REVIEW.md)，当前文件 / 收据 / 20 图绑定见 [.archify/review/ch12-artifacts.json](.archify/review/ch12-artifacts.json)；按持续授权提交并推送 origin/main。


### 2026-10-11(第十一章按统一规范重构)

- 固定 ES v9.4.0 提交核对 16 个源码文件 / 43 个区间，重写映射候选 / 主节点发布 / 等待重解析、动态推断、字段结构、四种 dynamic 与合并护栏；正文约 4035 中文字。勘误同步图源、解说、实验、问答与速记。
- 保留原 19 操作 ID 和 ch11-dynamic-mapping；新增 16 卡，共 5 组 / 35 卡，机制动画改为 9 步。显式 standard / stored source / coerce / ignore_malformed / 分片 / 刷新条件，限定健康等待、错误与重复预期，四索引点名清理。全站 30 正式页 / 464 卡 / 22 机制播放器；本章 2 图 / 2 条有限 trace。
- 官方 Archify 3.0.1 两图 Workflow v2 从首次附固定源码与真实 checkout，只改 JSON。mapping-update 当前根目录收据、field-paths review-4；原生 validate / deliver / strict check 均 showcase 9/9、0 errors / warnings、provenance current。原生 file URL 策略使 browser-check / finalize 整体仍 fail；旧候选、原生收据、初始 mainPath 与 390px 裁切的历史证据保留。
- 独立 HTTP 最终通过：两图四档桌面尺寸 / 双主题、章节六档宽度 / 双主题、880px 列 / ≤1px 对齐、页面 / iframe 容纳与全 SVG 节点、探索 / 来源 / 关闭 / 展开、暂停外层重播 / Enter、目录 / 已读、九步播放器 / 键盘、35 卡实际控制台导航核对 method / path / body、端点 / auth alias / raw、Pages 前缀与 reduced motion。390 / 320px 舞台 / 源码表局部滚动通过；实际查看 24 张最终截图，共享文件未改。
- 站点、JS、figwidth、stable ID 与 diff 检查通过。9200 连接拒绝、运行时缺 /proc/self/coredump_filter，真实首次 / 清理后重做未执行，未模拟 ES 返回。验收见 [.archify/CH11-REVIEW.md](.archify/CH11-REVIEW.md)，当前哈希 / 收据 / 24 图绑定见 [.archify/review/ch11-artifacts.json](.archify/review/ch11-artifacts.json)；按持续授权提交并推送 origin/main。

### 2026-10-11(第十章按统一规范重构)

- 固定 ES v9.4.0 提交核对 19 个文件 / 49 个区间，修正首次实时读取、reader / refresh、偏好、routing、重试 / REST 参数及性能承诺。按请求旅程、目标分片、读取视图和字段输出重写七段式；正文、图注、播放器、思考题、实验与速记同步。
- 原 19 个实验 ID 与 ch10-realtime-get ID 保留：新增 7 卡，2 组 / 26 卡；播放器由 7 步修正为 9 步。显式 settings / mapping / 健康等待 / 新旧版本对照 / 预期错误与点名清理。全站 30 正式页 / 448 卡 / 22 机制播放器，本章 2 图 / 2 条有限 trace / 1 机制播放器。
- 官方 Archify 3.0.1 两幅 Workflow v2 首次即附固定源码证据与真实 checkout；只改 JSON。get-journey 当前收据 review-2、realtime-read review-7，旧候选与失败记录保留。两图原生 validate / deliver / strict check 均 showcase 9/9、零错误 / 警告、provenance current；file URL 策略使原生 browser-check 与 finalize 整体仍 fail。读取分支图的通道共用和手机裁切按测量修复。
- 独立 HTTP 检查通过：两图四档桌面尺寸、章节六档宽度 / 两主题、880px 列 / ≤1px 对齐、页面与 iframe 容纳、主 SVG 全节点、探索 / 来源 / 关闭 / 展开、暂停后重播 / Enter、目录 / 已读、九步播放器及键盘、26 卡实际控制台导航与请求内容、端点 / 认证别名 / raw、Pages 前缀及 reduced motion。390 / 320px 原 SVG 舞台 / 表格自身滚动另测通过。实际查看 24 张最终截图；共享 CSS / JS 未改。
- 站点结构、JS、文字估宽、stable ID 与 diff 检查通过。9200 连接拒绝、运行时缺 /proc/self/coredump_filter，真实 API 首次 / 清理后重做未执行；源码离线 hash 计算与 API 预期均未冒充实测。验收见 [.archify/CH10-REVIEW.md](.archify/CH10-REVIEW.md)，当前哈希 / 收据 / 24 图绑定见 [.archify/review/ch10-artifacts.json](.archify/review/ch10-artifacts.json)；按持续授权提交并推送 origin/main。

### 2026-10-11(第九章按统一规范重构)

- 固定 ES v9.4.0 提交核对 28 个源码文件、62 个引用区间，文件字节与提交一致。围绕远程 GET 往返、普通帧、读写镜像、本地捷径及连接 / 统计边界重写七段式，新增勘误见上表。
- 保留原 7 个实验 ID，新增版本、绑定 / 发布地址、本课健康等待、GET 前基线及实际 GET 共 5 卡，合计 2 组 / 12 卡；显式 settings / mapping / refresh，限定同节点统计与重做条件。全站 30 正式页 / 441 卡 / 22 机制播放器，本章 2 图 / 2 条有限路径动画 / 0 机制播放器。
- 官方 Archify 3.0.1 从首次 finalize 即传真实干净固定源码 checkout。只改 JSON 修复 Sequence 自发消息 / 列留白 / 字号和 Workflow 主路径绕行，当前原生收据 remote-get review-4、frame-codec review-2；validate / deliver / strict check 均 showcase 9/9、零错误 / 警告、provenance current。原生 browser-check 因 file URL 策略失败，finalize 整体仍为 fail，旧候选与收据保留。
- 最终独立 HTTP Chromium 通过：两图四档桌面尺寸、章节六档宽度与双主题、880px 列 / ≤1px 对齐、页面 / iframe 容纳、实际主 SVG 全部节点、探索 / 源码 / 关闭 / 展开、暂停后重播 / Enter、目录 / 已读、12 张实际控制台导航的请求字段、端点 / 认证别名 / raw、Pages 前缀及 reduced motion。实际查看 20 张最终截图，图框分档高度记录在验收报告，共享 CSS / JS 未改。
- 站点、JS 语法、文字估宽、稳定 ID 与 diff 检查通过。9200 连接拒绝，云运行时仍缺 /proc/self/coredump_filter，真实 ES 首次与清理后重做均未执行，未模拟 API。验收见 [.archify/CH09-REVIEW.md](.archify/CH09-REVIEW.md)，当前哈希 / 报告 / 截图绑定见 [.archify/review/ch09-artifacts.json](.archify/review/ch09-artifacts.json)；本轮按持续授权提交并推送 origin/main。

### 2026-10-11(第八章按统一规范重构)

- 本地时间 Asia/Shanghai，图目录在 2026-10-10 创建，跨零点于本日交付。固定 ES v9.4.0 目标源码 23 文件逐一比对提交字节一致；按“返回与完成 → 回调组合 → 完成协议 → 默认线程池 → 背压与观测”重写，不重复阅读原教程。新增勘误见上表。
- 保留原 10 个实验 ID 与六步 ESFLOWS，补 5 卡，共 2 组 / 15 张操作卡；显式 mapping / 固定 ID / 关闭周期刷新 / 显式 refresh / 本课健康等待 / 写后搜索前基线 / 更新前后读回。清理、重复与统计不归零的条件写清。全站 30 正式页 / 436 卡 / 22 机制播放器，Archify trace 另计。
- 官方 Archify 3.0.1 的两幅 Workflow v2 从首次即传真实固定源码 checkout。只改 JSON 修正主路径、逻辑列留白与手机裁切；当前原生收据 async-search 为 review-4，listener-map 为 review-9。两图 validate / deliver / strict check 均 showcase 9/9、零错误 / 警告、provenance current；原生 browser-check 仍因 file URL 管理策略失败，finalize 整体如实 fail，旧收据保留。
- 最终独立 HTTP Chromium 检查通过：两图四档桌面尺寸，章节六档宽度与双主题，880px 列 / ≤1px 对齐，页面与 iframe 容纳，额外逐图确认所有实际 SVG 节点可见；探索 / 源码 / 关闭 / 展开、暂停后重播 / 键盘、目录 / 已读、15 张卡实际控制台请求字段、端点 / 认证别名 / raw 与 Pages 前缀、reduced motion 及六步机制播放器。手机机制图在自身容器内滚动，共享 CSS / JS 未改。实际查看本轮 24 张最终截图。
- 站点、JS 语法、旧 SVG 文字估宽、稳定 ID 与 diff 检查通过。9200 探测拒绝连接，环境仍缺 /proc/self/coredump_filter，真实 ES 首次与清理后重做未执行，未模拟 API。完整验收见 [.archify/CH08-REVIEW.md](.archify/CH08-REVIEW.md)；按持续授权提交并推送 origin/main。


### 2026-10-10(第七章复核与实验预期修正)

- 重新核对动作身份、两张登记表、查表 / Task 先后、校验 / 异步过滤 / 引用清理、GET 的基类与分片 executor、任务匹配和 REST 计数，以及实验初始 / 重做条件。本章引用的 18 个源码文件与固定 ES 提交逐一比对一致。
- 修正 B5 未注册 URL 的 400 预期：消息直接位于顶层 error 字符串，旧卡片误写 reason；正文补充 RestController.handleBadRequest 固定版本依据。原 15 个 ID 保留，图源和生成 HTML 未变，无需重新生成图。
- 修改后完整独立 HTTP Chromium 检查通过：两图四档桌面尺寸、章节六档宽度与双主题、探索 / 关闭 / 展开、暂停后重播 / 键盘 / reduced motion、目录 / 已读、15 张实际控制台深链与 Pages 前缀。实际查看并保留 8 张复核截图，含修正卡片与说明的手机双主题显示；站点、JS 语法和 diff 检查通过。
- 9200 仍连接拒绝，运行时仍缺 /proc/self/coredump_filter，真实 API 未执行；原生 file 浏览器限制不变。新报告与源码复核见 [.archify/CH07-REVIEW.md](.archify/CH07-REVIEW.md)，当前产物清单绑定新报告并保留旧证据；本轮按持续授权提交并推送 origin/main。

### 2026-10-10(第七章按统一规范重构)

- 按固定 ES v9.4.0 源码校对本地名字查表、Task 登记 / 注销、公共执行链、异步过滤、GET 的协调 / 分片 executor 与远程 handler 登记。正文、两幅 Workflow v2、图注、预期、思考题和速记保持一致，8 项新增勘误见上表；不重复通读原教程。
- 保留原 9 个实验 ID，补 6 卡，共 2 组 / 15 张操作卡：显式 mapping、刷新与本课索引健康检查，GET 前后计数基线，完成后查 Task，精确 / 通配 / 无星号前缀和缺文档对照。点名清理、重复创建 / 写入 / 清理差异与每轮新基线写清。全站 431 操作卡 / 22 个机制播放器，Archify trace 另计。
- 两图首次 finalize 即用真实固定源码 checkout；执行图的初稿路径歧义只改 JSON 修复，后续按截图压紧纵向布局。当前原生收据均为 review-4，validate / deliver / strict check 为 showcase 9/9、零错误 / 警告、provenance current。原生 browser-check 仍因管理员 file URL 策略失败，finalize 整体如实为 fail。
- 独立 HTTP Chromium 覆盖两图四档桌面宽度及章节六档宽度、浅深主题、880px 列与 ≤1px 边界对齐、页面 / iframe 容纳、节点探索 / 源码 / 关闭、两图暂停后重播 / 键盘 / reduced motion、目录 / 已读、15 张实际控制台深链及请求内容、端点 / 认证别名 / raw、Pages 前缀。实际查看 20 张独立 / 嵌入 / 桌面 / 手机 / 操作卡 / 源码表截图；图框收紧为 760 / 680 / 440px，共享 CSS / JS 未改。
- 站点、JS 语法、稳定 ID 保留与 diff 检查通过。允许的网络权限下再次探测 9200 无连接；既有运行时缺 /proc/self/coredump_filter 的 ES 9.4.0 阻塞仍适用，真实 API 首次和清理后重做均未执行，未模拟响应。完整验收、当前哈希与命令见 [.archify/CH07-REVIEW.md](.archify/CH07-REVIEW.md)，HTTP 证据见 [.archify/review/ch07-http-review.json](.archify/review/ch07-http-review.json)。本轮按持续授权提交并推送 origin/main。

### 2026-10-10(第六章按统一规范重构)
- 按“路由 → 参数消费 → GET / HEAD → 保护与统计”重写 ch06，保留七段式、课间导航与已读，增加目录、两图跳转、五道折叠思考题与固定 v9.4.0 文件 / 方法依据；勘误同步正文、图注、实验与速记。
- 官方 Archify 3.0.1 生成两幅 Workflow v2，均带有限 trace；所有语义节点引用固定 ES 提交 `2e8528e92361c3399724226deaf2b46f933e925b` 的目标源码，并传真实 checkout。路由图失败分支按测量修复，旧收据保留，当前收据 review-4；两图 validate / deliver / strict check 均为 showcase 9/9、零错误 / 警告。
- 原生 browser-check 仍因管理员 file URL 策略失败，finalize 整体如实为 fail；独立 HTTP Chromium 检查覆盖两图四档桌面宽度及章节六档宽度、浅深主题、880px 列与 ≤1px 边界对齐、页面 / iframe 容纳、探索与关闭、两图暂停后重播 / 键盘 / reduced motion、目录 / 已读、17 张真实控制台深链及请求内容、端点 / 认证别名 / raw 与 Pages 前缀。已实际查看桌面与窄屏截图，≤600px 图高收紧至 540 / 600px；共享 CSS / JS 未改动。
- 保留原 10 个实验 ID，新增 7 卡，共 2 组 / 17 张操作卡。显式创建索引与 mapping，首次 / 重复写入区分，清理点名 tut-l06-docs，补齐 GET/HEAD、_source 与编码 ID。全站 425 操作卡 / 22 个机制播放器，Archify trace 另计；站点、JS 语法与 diff 检查通过。
- 本轮 9200 无连接，既有运行时缺 /proc/self/coredump_filter 的 ES 9.4.0 启动阻塞仍适用。真实 API 首次及清理后重做未执行，页面 / curl 状态与响应头是源码预期，没有模拟响应。完整验收、图源 / HTML 哈希和生成命令见 [.archify/CH06-REVIEW.md](.archify/CH06-REVIEW.md)，独立 HTTP 证据见 [.archify/review/ch06-http-review.json](.archify/review/ch06-http-review.json)。本轮按用户持续授权提交并推送 origin/main。

### 2026-10-10(重构完成后自动提交 GitHub)
- 用户授权每次章节重构完成后自动提交并推送 GitHub；AGENTS / CHAPTER_STANDARD / CLAUDE 已同步写明 `origin/main` 为现有发布目标，无需逐次确认，并要求交付 GitHub 提交链接、如实记录验证限制与推送失败。
- 本次将第五章已完成的重构、图源 / 产物 / 验收证据及规则更新一并提交、推送；第五章的具体检查结果与未实测项目见下方日志及 .archify/CH05-REVIEW.md。

### 2026-10-10(第五章按统一规范重构)
- 按“配置快照与契约 → 作用域 / 可变性 → 覆盖与寿命 → 动态更新边界”重排第五章；保留七段式、课间导航、已读进度，增加目录、图解跳转、四道折叠思考题和固定 v9.4.0 文件 / 方法依据。
- 官方 Archify 3.0.1 生成两图：静态 Architecture 解释 Settings / Setting<T> 读值关系，Workflow v2 以有限 trace 展示主节点校验与各节点应用。图内源证据固定到 ES 提交 2e8528e92361c3399724226deaf2b46f933e925b，首次生成即通过真实源码 checkout 的 --repo-root 核验；未手改生成 HTML。根据嵌入截图把 Workflow 主路径改为纵向分组，当前嵌入高度为 800 / 1020px，窄屏为 560 / 780px。
- 修正 NodeScope “集群一份”、Final 失败会破坏路由、consumer 执行原子性、transient “重启即清理”、null 必回默认、defaults 均为硬编码默认及 Filtered 必定显示掩码等说法；正文、图注、实验、思考题与速记同步。原有 8 个实验 ID 保留，改用 persistent + null 显式清理，新增范围校验、索引设置读回、限定索引健康等待与清理后读回，总计 2 组 / 12 张操作卡。
- 原生 validate / deliver / strict check：两图 showcase 9/9、零错误 / 警告，源码证据核验通过。原生 browser-check 因管理员禁止 file:// 报 ERR_BLOCKED_BY_ADMINISTRATOR，finalize 整体保留 fail；未修改浏览器政策。
- 独立 HTTP Chromium 检查通过：两图各 1440 / 1600 / 1920 / 2048px、浅深主题；章节 1920 / 1440 / 1024 / 768 / 390 / 320px、浅深主题，正文 / 图框 / 表格 / 实验边界差 ≤1px、桌面列最大 880px，页面与 iframe 无横向溢出。节点来源探索 / 关闭、展开、主题同步、暂停后重播、键盘重播、目录、进度、12 张卡的真实控制台导航、端点 / 认证别名 / raw 标记、Pages 子路径与 reduced motion 均通过。共用 CSS / JS 未修改；结构与 JS 语法检查全绿。
- 源码已核对、API 未实测：127.0.0.1:9200 无连接，云环境仍缺 /proc/self/coredump_filter，已有启动记录确认该运行时无法正常启动 ES 9.4.0；首次运行与清理后重做未执行，HTTP 测试只验证请求传递，不模拟 ES 响应。
- 实际查看两图独立与嵌入的浅深截图、章节桌面 / 手机首屏、手机图框 / 实验 / 表格；最终图源 / HTML 哈希、原生收据、HTTP 记录、许可与重现方式见 .archify/CH05-REVIEW.md。

### 2026-10-10(第四章按统一规范重写)
- 按“分类轴 → 可见性 → 接口装配 → mapper-size 副作用 → Classic / Stable 兼容范围”重写。校正 X-Pack、删除模块、加载分支与扩展暴露层、组件绑定以及仅凭 400 判断路由等表述；补齐固定 v9.4.0 文件/方法链接、源码检索任务、五道思考题和四条陷阱。
- 新增 Archify Architecture 静态隔离图与 Workflow v2 Reindex 启动注册图（有限 trace）；真实 ES checkout 与固定提交核验。原生流程图首次发现共享路由段，调整相连节点/端口后修复；根据截图改为两列并测量图框高度。复用共用脚本与 880px 阅读列，无共享文件或前三章代码改动。
- 两张实验卡保持稳定 ID；GET 增加节点名称与失败信息，预期随安装情况判断。POST 保持无效空对象，不创建资源；说明认证、错误正文、重复运行与无需清理。当前 127.0.0.1:9200 连接拒绝，两个真实 ES 请求及重复运行未执行。
- 两图原生 validate / deliver / strict check 均 showcase 9/9、零错误/警告，源码证据通过、provenance current。file:// browser-check 仍因 ERR_BLOCKED_BY_ADMINISTRATOR 失败，finalize 整体如实保留失败。
- 独立 HTTP Chromium 验收通过：两图四种桌面尺寸/双主题；章节六种宽度/双主题，同列边界差 ≤1px、最大 880px、页面与 iframe 无横向溢出，初始 SVG 未裁切。探索/关闭/固定提交源码、展开、路径图暂停后重播及键盘、主题、目录/进度、实验请求填充与 Pages 前缀正常；减少动态效果优先，静态图无可见播放入口。实际查看独立、嵌入、浅深、390px 与章节首屏截图；手机图提供总览，通过放大/探索及正文阅读细节。站点结构、JS 语法与源码链接路径/行号检查通过；哈希及收据见 .archify/CH04-REVIEW.md。

### 2026-10-10(第三章按统一规范重写)
- 按“进程入口 → 构造锁盘 → 启动门禁 → 检查条件 → 生命周期”重写第三章，补齐 v9.4.0 的 ServerLauncher / preparer 关系、初始入群等待超时、显式强制检查与 alwaysEnforce、状态标志先变及关闭后处理等边界。
- 新增 Archify Sequence 启动时序与 Lifecycle v2 状态图，均带有限 trace、固定源码提交与真实 checkout 核验；复用共用主题/重播控制和 880px 阅读列。时序图采用 spread 列布局；生命周期按两列三行排布，修复初版手机裁切。
- 保留两个稳定实验 ID，校正 publishAddress、实际内存锁状态与 PID 命名空间解释，说明只读重复与观测范围；保留 ch03-boot ID，将旧六步快照更新为八步并改为每行两段文字，消除并排长文本挤压。增加源码检索任务和五道折叠思考题。
- 原生 validate / deliver / strict check 均通过 showcase 9/9、零错误/警告；file:// browser-check 因 ERR_BLOCKED_BY_ADMINISTRATOR 失败，finalize 整体保留失败。云端 127.0.0.1:9200 无连接，两个真实 ES 请求未执行；源码校验不能代替 API 实测。
- 独立 HTTP Chromium 验收通过：两图各四种桌面尺寸 / 双主题，第三章六种宽度 / 双主题，边界差 ≤1px、阅读列 ≤880px、页面/iframe 无横向溢出；节点探索/关闭及源码链接、暂停后重播、键盘、展开、主题、目录/进度、实验深链与 Pages 前缀正常。减少动态效果优先，八步手动动画及 SVG 文字范围通过。实际查看独立、嵌入、浅深、手机和逐步动画截图；收据与哈希见 .archify/CH03-REVIEW.md。站点结构与修改的 JS 语法检查通过。

### 2026-10-10(第二章按统一规范重构)
- 以“源码区域 → GET 定位 → 发布与构建”重排第二章，保留两张只读 HTTP 卡及稳定 ID；增加可折叠课内目录、源码检索任务、四道思考题与固定 v9.4.0 文件/方法链接。
- 两幅 Archify Architecture 图均携带真实 ES 源码提交 2e8528e92361c3399724226deaf2b46f933e925b 的节点证据，并通过 --repo-root 核验。区域图是静态代表性编译依赖；GET 图通过有限 trace 展示阅读目标及分支，明确不是运行时调用链。
- 共用布局与主题/重播控制提取为 chapter-diagrams.css/js，第一章同步引用；两章维持 880px 正文与图同列。图高按内容分别设定，第二章不再统一套用首章高度。
- 校正依赖箭头、生产依赖遗漏、x-pack 付费概括、SearchPhaseController 路径与 Gradle 发现条件；节点实验增加 vm_version / using_bundled_jdk，区分构建版本、运行版本与可配置角色。
- 原生 validate/deliver/strict check 均通过 showcase 9/9、零错误/警告；file:// browser-check 仍受管理员策略阻塞，整体 finalize 保留失败。当前云环境 9200 无连接，真实 ES 请求未执行；用户侧数据不据此计为云端实测。
- 最终 HTTP Chromium 检查通过：两图各四种桌面尺寸/双主题；两章各六种页面宽度/双主题，边界差 ≤1px，页面与 iframe 无横向溢出；源码节点探索/关闭、展开、主题、暂停后重播、键盘、减少动态效果、目录/进度、实验深链及 Pages 前缀正常。第一章 NRT 减少动态效果下手动步进回归通过。已实际查看独立、嵌入、浅深及手机截图；记录见 .archify/CH02-REVIEW.md。站点结构/JS 语法检查全绿。

### 2026-10-10(后续章节统一重构规范)
- 新增 CHAPTER_STANDARD.md，以第一章 8a11c97 为视觉基线，规定 880px 同列布局、按机制选 Archify 类型、有限路径动画、主题/重播/reduced motion、内容版本依据、可重复实验及分项验收。
- 新增 AGENTS.md 协作入口，并在 PLAN / CLAUDE / README 接入规范。消除仅限内联 SVG、固定每课 2–4 实验、实测不可运行时无法继续等旧约束冲突；实验与旧快照播放器 schema 保留。
- 进度表新增图解重构列：第一章已改造，ch02–30 待改造。本轮只建立规范，未批量修改后续章节或抽取通用运行时文件；通用文件提取作为下一章接入步骤明确记录。
- 文档链接与基线数值已核对，站点结构检查通过；本轮仅修改文档，运行中的章节与图源未改变。

### 2026-10-10(第一章图解与正文宽度对齐)
- 修正首章外层 1200px、正文 880px 导致的宽度差异：外层改为 924px(含桌面两侧各 22px padding)，标题、正文、图解、实验统一为 880px 阅读列。窄屏沿用响应式侧边距，未改生成的 Archify HTML。
- HTTP Chromium 验证 1920 / 1440 / 1024 / 768 / 390 / 320px 六种视口：各区域左右边界一致，页面及三幅 iframe 无横向溢出；主题同步、暂停后重播通过。站点结构检查通过。

### 2026-10-10(第一章内容复查与 GitHub 提交)
- 补充 ES 的定义与应用场景；改正把关系数据库查询一概视为全扫描、把倒排成本只归因于列表长度的表述。补充单文档原子性与跨文档事务的区别，以及 match / term 的分析行为差异。
- 依据 v9.4.0 / Lucene 10.4.0 官方源码修正默认停用词、offsets 默认存储、集群定义、主分片设置与 resize、路由公式适用范围、refresh 间隔非延迟上限等结论；正文新增可折叠的源码依据，勘误表登记网页旧说法。
- 保留 11 个实验操作：显式设置 body 字段 standard；说明 _analyze 不会改变 mapping、acknowledged 与 shards_acknowledged 的区别；健康检查仅针对 tut-l01-docs；补充「清理 → 创建 → 重做」流程，避免旧文档使近实时对照失效；修正实验编号引用。
- 修复 ESClient.consoleLink 从章节页跳到不存在的 chapters/console.html 的问题，使用脚本位置定位站点根，保留 Pages 子路径、file:// 和深链参数。
- 三幅 Archify 图从修改后的 JSON 重新生成；原生 validate/deliver/strict check 为 9/9、零错误/警告，file:// browser-check 仍受管理策略阻塞，如实保留失败收据。最终 HTML 哈希对应的独立 HTTP 检查通过：四种桌面尺寸、三图嵌入、主题、暂停重播、节点探索、NRT 步进、390px 布局、reduced motion，以及章节/Pages 前缀下控制台跳转。
- 本轮仅审阅第一章内容；11 个实验的真实 ES 请求仍未执行，云运行时阻塞原因不变。代码沿用 main 根目录的 Pages 自动部署方式；图源、许可及验证记录随代码提交，详见 .archify/README.md 与 REVIEW.md。

### 2026-10-10(第一章 Archify 交互图解试读)
- 使用官方 Archify 3.0.1 CLI 从 `.archify/` 内的 JSON 图源生成三幅自包含 HTML：倒排索引(Architecture)、显式分析链(Workflow v2)、双节点分片放置(Architecture)。第一章相对路径嵌入图解，保留 11 个实验和五步近实时播放器；新增图解跳转、节点探索、展开查看、主题同步和重播。仍是零构建、零 CDN，可静态托管到 Pages，尚未发布。
- 三幅图显式启用 trace 动画，可暂停和重播；系统减少动态效果设置优先。已有 flow-player 在减少动态效果模式下不再自动播放，手动步进保留。
- 图义修正：standard tokenizer 的输出保留 The / Quick / Brown / FOX，lowercase 随后才小写，stop 再移除 the；速记改为写入与查询 token 对齐，不保证分析链相同。近实时文案改为 refresh 发布新的可搜索视图，不与持久化提交/flush 混同。
- 检查：站点 `check.mjs` 通过；三幅 Archify validate/deliver/strict check 均 9/9 showcase、零错误/警告。Archify 原生 browser-check 因云浏览器策略禁止 file:// 报 ERR_BLOCKED_BY_ADMINISTRATOR，保持真实失败记录，未修改策略。
- 独立 HTTP Chromium 检查通过：三图 × 四种桌面宽度无横向溢出，三 iframe 初始化、深浅主题同步、暂停后重播、节点探索/关闭、NRT 步进、390px 整页包含、减少动态效果。实际查看了整页嵌入图截图。原生 browser-check 失败与 HTTP 检查通过分别记录，后者不替代前者。
- 真实 ES 请求本轮未跑(当前云运行时缺少 ES 9.4.0 必需的 /proc/self/coredump_filter)。阅读、图解和动画不依赖 ES。

### 2026-09-25(GitHub Pages 上线 ✅)
- 本机装了 gh CLI 2.95.0(brew),用户已 `gh auth login`(socoo123)。API 查 Pages 已开通(用户网页端点过):main /(root),status=**built**。
- 线上核验:**https://socoo123.github.io/es_web/** —— 11 个关键路径(首页/架构/控制台/速查表/章节/样式/脚本/实验注册表/compose/README)全 200;headless Chrome 打开线上 architecture.html 渲染与本地一致(子路径下相对链接全部正常)。
- 提醒:线上跑实验需重建 docker 容器使新 CORS 白名单生效 + 浏览器本地网络授权;阅读不受影响。

### 2026-09-25(GitHub Pages 部署准备)
- 可部署性结论:纯静态零构建,Pages 完整托管阅读体验;实验连本机 9200 受两层管控——① CORS 白名单需含 Pages 域,② 浏览器本地网络权限(实测 ES 9.4.0 `CorsHandler` 不回 `Access-Control-Allow-Private-Network` 头,严格模式浏览器会拦)。
- 改动:两份 compose 的 `http.cors.allow-origin` 加入 `https://socoo123.github.io`(需 `docker compose up -d` 重建容器生效,尚未在跑容器上应用);根目录加 `.nojekyll`;README 增「部署到 GitHub Pages」章节(开关步骤 + 实验限制 + 本地兜底)。
- 开通动作在仓库网页端:Settings → Pages → Deploy from branch → main /(root),本机无 gh CLI 故未代开。

### 2026-09-25(架构总览页 + README)
- 新增 `architecture.html`:全景大图(fig-wide 变体,放宽至 1000px)——纵向数据流(客户端→入口层 L06-09→写入路 L13→15→12→11→14 / 搜索路 L10→16→17→18→19/20→汇于 Lucene 底座→集群平面 L21-25)+ 横向六篇行(L01-05 地基、L26-30 横切);**30 课方块全部 SVG `<a>` 可点击直达**。图下:四条走读路线(写一篇/搜一次/集群自愈/系统搭建,含排序理由)+ 源码地图 ktable(19 行,目录与入口类逐一对照本地 es-src 校验:RestController/ActionModule/ThreadPool/TransportService/ShardGetService/MapperService/IngestService/TransportBulkAction/InternalEngine/IndexShard/OperationRouting/SearchService/ClusterState/MasterService/Coordinator/AllocationService/CircuitBreaker/ScriptService/AstBuilder/IndexLifecycleRunner/Security)。
- 导航:全站 33 页 topbar 统一加「架构」入口(console 的 class="here" 分支单独处理);index CTA 加「看架构总览」按钮。style.css 增 `figure.fig.fig-wide svg` 上限与 `figure.fig a:hover` 描边反馈。
- 新增 `README.md`:快速开始 / 站点地图 / 六篇结构表 / 版本锚点 / 工具命令 / es-src+tutorial 不入库说明与下载命令。
- `check.mjs` 全绿;`figwidth.mjs architecture.html` 全部文本估宽在盒内;headless Chrome 截图验收浅色渲染(深色全部走既有 CSS 变量,未引入新颜色字面量)。

### 2026-09-25(基础设施:本地源码 + docker 现状核验)
- 新增 `es-src/`:GitHub v9.4.0 tag 源码 tarball,解压后 453MB,server/modules/libs/x-pack 等全量在位。`build-tools-internal/version.properties` 实测 Lucene 10.4.0、bundled JDK 26.0.1+8,与勘误表口径互证。**只准 grep/读目标文件,勿整目录通读**(token 纪律)。
- docker 现状核验:`docker compose config -q` 两份均过;es-study(9200)、es-study-secure(9201)已跑 23 小时且 healthy,9200/9201 API 均应答 9.4.0。本轮未改任何 compose 配置——用户要求的「配好」此前已完成,本轮仅验证。
- `node tools/check.mjs` 全绿(见本轮末次运行)。
- 站点入库 GitHub `socoo123/es_web`(main,init 提交 db7e1c3,81 文件约 1.6MB)。`.gitignore` 排除 `es-src/`、`tutorial/` 与 .DS_Store——**这两目录只存本地,换机器需重新下载**。

### 2026-09-25(审查计划 P0:版本锚点、Bulk 控制台、第 29 课深链)
- 版本:ch01/ch02/ch20 与 ch02 实验预期改为 Lucene 10.4.0、JDK 26.0.1+8、Netty 4.1.132.Final。Jackson/Log4j/ANTLR 对照 tag 未改。tutorial 旧数字只登记勘误,不回灌。
- 控制台不再 `trim` 请求体;JSON 检查失败时提供「仍然发送原文」。深链 `?ep=&am=anon|elastic|wrong|alice&raw=1`,口令不进 URL。Basic 凭据不再写入 localStorage,控制台有清除按钮。
- ch13 写明 NDJSON 发 `application/x-ndjson`。速查表 `GET /` 改为版本/集群名/节点名。第 1/13/14 课 refresh 补上 search idle;第 1 课分析器图标明是显式 stop 示例。
- Docker 端口改为 `127.0.0.1` 绑定,CORS 收成 localhost/127.0.0.1/`null`。已在跑的容器要重建才生效。
- `tools/check.mjs` 增加上述回归点。浏览器逐课验收与第 13/24/28/29 课全流程仍未做。P1 里源码动手闭环、多节点/快照成功路径、FLS/DLS、实验分组和速查表六组索引尚未做。

### 2026-09-25(前端双主题与图表配色调整)
- `assets/css/style.css`：浅色改为暖白纸面/清晰白卡，深色改为深海蓝；提高文字、边框和组件的层次，首页首屏、按钮、卡片与 HTTP 方法徽章同步调整。
- SVG/动画统一用蓝青过程节点和暖金重点节点，箭头使用独立的高对比颜色；移动端表格与图在容器内横向滚动，正文长标识可换行。
- 用 Chrome headless 检查了首页、第 14 课的浅色/深色及窄屏渲染；图中文字与各节点背景的抽样对比度均超过 4.5:1。`node tools/check.mjs`、`node tools/figwidth.mjs` 通过。

### 2026-09-25(全站审查计划)
- 新增 `GROK_REVIEW_GUIDE.md`：对 30 章、414 个实验、22 个动画及站点工具做静态审查，列出 P0 错误/阻断、P1 内容缺口、P2 验收标准。
- 只读核对本机 ES 9.4.0 与固定 v9.4.0 源码：Lucene 实为 10.4.0、bundled JDK 为 26.0.1+8、Netty 为 4.1.132.Final；网站及 tutorial 的版本数字有误。尚未逐一运行实验或做浏览器验收。
- `node tools/check.mjs`、`node tools/figwidth.mjs` 通过；两项工具不覆盖事实准确性和控制台实验执行。

### 2026-09-24(P6 收官 ✅,ch30 全站转写完成)
- 用户指示「完成最后一张」,主会话单读单写 lesson30,全部论断先实测后落笔(9200)
- ch30 ✅ 13 实验/2 图(六篇接链竖排、阅读主链三步)+ 全链回放收官动画 7 步(把 29 课串到一次 POST _search 上:认证→路由→两套名字→快照选 shard→两阶段→EXTERNAL searcher→方法论三步);自测清单主线:refresh_interval=-1 冻结竞态 → match brown 1 hit → 三种 400(未注册路由 no handler、非法 search_type No search type(与 RestSearchActionTests 断言同文案)、from=10000 的 10010(root_cause,与 yaml 30_limits catch 同文案))→ SEARCH/GET 分道当场演(doc2 未 refresh:SEARCH 0 hits、GET 200、refresh 后 1 hit)→ _nodes/usage 指认 rest_actions.search_action(两套名字)
- 勘误:0 条(lesson30 论断与 9.4.0 实测全部吻合:10010 在 root_cause、No search type 文案一字不差、双 400 口径一致)
- **全站 30/30 课正式,实验 414,动画 22;check.mjs + figwidth 全绿。六篇全部转写完成**
- 下一步(待用户定):P7(速查表扩充、动画补漏、全站终检)或直接验收

### 2026-09-24(P6 完成 ✅,ch26+ch27+ch28+ch29 轮写)
- 用户指示「完成 ch26 ch27 ch28 ch29」,主会话逐课单读单写;本批起了本地 docker:9200 学习节点全程在跑,ch29 另起 9201 安全节点——每课论断先实测后落笔
- ch26 ✅ 20 实验/3 图 + 编译旅程动画 7 步:白名单类型宇宙(txt 装表,无 java.io/Runtime/Class)→ ANTLR → 语义分析 Lookup(null,无 Class.forName 后路)→ IR+ASM byte[] → SecureClassLoader+ScriptCache;三连破坏:File 直测 _execute(400 compile error + Not a type)、塞 script_score(root_cause 同句)、写 pipeline(PUT 当场 400);def vs 静态 getClass 对照(runtime dynamic vs compile member method);expensive 关/恢复;三个 context 同台(score/script_fields/update/ingest)
- ch27 ✅ 14 实验/2 图 + 管道执行动画 7 步:POST /_query 唯一路由;visitCompositeQuery 左喂右,WHERE→Filter(下推进 Lucene)、STATS→Aggregate;avg=Sum/Count(INITIAL/FINAL)+协调端 DivDoublesEvaluator——profile 两条 Driver 实测链直接入图入动画;变体四连 + DSL 三连对照 + /_esql 405 与 /_query/async 存在性
- ch28 ✅ 20 实验/3 图 + 一分钟 rollover 动画 7 步:poll 15s → 策略(1m/2h/24h)→ **接力模板**(rollover 不复制 lifecycle.name 的实测正解)→ 首索引;explain 三时刻(new→hot/check-rollover-ready→滚后);PUT v2 分叉(活策略 v2+forcemerge vs 索引缓存 v1 只 rollover);wildcard DELETE 400 与 in-use 400 做成破坏实验;全部 ILM 时序在真实节点走通(两轮完整 rollover)
- ch29 ✅ 19 实验/2 图 + 认证链动画 7 步;**站点基础设施升级**:docker/docker-compose-secure.yml + start-secure.sh(9201,xpack.security.enabled=true,elastic/elastic-password,CORS 已含 Authorization)、es-client 新增 auth()/setAuth + raw 的 opts.endpoint/auth/headers、实验运行器支持实验级端点/凭据/自定义头(@9201 徽章)、console 加凭据输入框;401 两兄弟(missing vs unable)+伪造 ApiKey(security_exception 另一文案)+alice 403 三连(GET / cluster、_cat/indices index、PUT names×privileges)+checkSameUserPermissions 例外(_authenticate 200)+9200/9201 双集群对照;node 烟测四条覆盖路径全对
- 勘误:4 条(ch27 /_esql 实为 405 非 404;ch28 rollover 不复制 lifecycle.name 需模板接力、模板带 alias 本体则 ERROR;ch28 wildcard DELETE 默认 400;ch29 WWW-Authenticate 实为双挑战 Basic+ApiKey)
- 全站:29/30 课正式,实验 401,动画 21;check.mjs + figwidth 全绿;两个 docker 节点(9200/9201)留跑供用户验收,收起 9201 用 `docker compose -f docker/docker-compose-secure.yml down`
- 下一步:ch30 收官(全景回顾与方法论,2 图配额)→ P7(速查表扩充、动画补漏、全站终检)

### 2026-09-24(P5 完成 ✅,ch24+ch25 轮写)
- 用户指示「再写后面 2 章」,同前模式:主会话逐课单读单写,无代理、零 docker
- ch24 ✅ 20 实验/3 图(两阶段映射、Engine 双入口、快照增量)+ **peer recovery 旗舰动画 7 步**(PLAN 旗舰清单 #7):家底(commit 0-9 + translog 10-12)→ RECOVERING 接棒 → safeCommit 对账 reuse → phase1 FILE_CHUNK 限速拷 → PREPARE_TRANSLOG 开 Engine(skip 本地 tlog)→ phase2 发 ops(PEER_RECOVERY origin、不走限速)→ finalize 对照「先 flush 则 phase1 就有」;实验三条线:tut-l24-rec 的 EMPTY_STORE→close/open→EXISTING_STORE+reused 变奏、加副本不出现 PEER 行(第 23 课互证)、fs 仓库如实失败(path.repo 空,非 200)、tut-l24-gap 复刻第 14 课缝(uncommitted_operations=1,refresh 后可见但仍 1)
- ch25 ✅ 14 实验/3 图(层级账本、两种跳法对照、terms 内存曲线并入正文)+ **熔断水位旗舰动画 7 步**(旗舰清单 #11):1GB 堆家底(真实堆 900MB)→ +500MB terms 记账构成(preallocate 6kb→agg 5kb→BigArrays)→ 子账 CAS 后 550≤600 → Parent 900+500=1400>950 → addWithoutBreaking(-500) 回滚 → 429 节点活着(vs IndexingPressure 另一本账)→ 恢复+tripped 计数器+「解法在查询」;实验主线:stats 字段名 + parent.estimated≈真实堆预测 → transient 1kb 亲眼看 429(preallocate[aggregations]、bytes_limit=1024、TRANSIENT)→ tripped≥1 → null 恢复 200⇄429 对照 → match_all 证明 tripped 不锁死
- 修复 2 处自检/chcek 报错:ch24 动画 step5 note 超 200 字(压缩);ch25 实验标题误写 &gt; 实体(experiments.js 用 textContent,会原样显示,改回纯字符);ch24 陷阱图标 🗑 误用改回 🕳
- 勘误:0 条(lessons 24/25 论断与 9.4.0 一致:六种 RecoverySource.Type 含 RESHARD_SPLIT、phase1/2 限速差、DEFAULT_PREALLOCATION 6kb / DEFAULT_WEIGHT 5kb、use_real_memory 95%/70% 两分支、IndexingPressure 10%/15% 与拆 Bulk 水位 5%/7.5%;fs 仓库 path.repo 失败文案按源码原文引用)
- 全站:25/30 课正式,实验 328,动画 17;check.mjs + figwidth 全绿。**P5 验收点,等用户过目**
- 下一步:P6(ch26-30 收官:脚本引擎/ES|QL/ILM/安全/全景回顾;旗舰清单已全部完成,余下按章节配常规图与动画)

### 2026-09-24(P5 进行中:ch21+ch22+ch23 轮写)
- 用户指示「开写 ch21 ch22 ch23,轮着写」,主会话逐课单读单写,无代理、零 docker(同 P4 模式)
- ch21 ✅ 16 实验/3 图(快照替换链、四块 2×2、双单线程舞台);实验主线:metric vs filter_path 对照(version 写进 metric 才出现)→ term 住 metadata.cluster_coordination → 建索引 +1/写文档不动/改设置又 +1 → ClusterState.version 与 Metadata.version 两套计数器并排
- ch22 ✅ 10 实验/3 图(四道门横排、Mode 双竖链、多数派 vs 少数派)+ **选举时序旗舰动画 7 步**(PLAN 旗舰清单 #5):健康集群 → 拔线分区 → 两侧检测失联 → pre-vote 假投票(已有 leader 拒绝)→ term 5→6 真选举 → 新主两阶段 publish/commit、旧主 FailedToCommit+no-master block → 愈合跟更高 term;实验含 voting config 读 quorum=1、discovery.type=single-node、version+1 而 term 不动
- ch23 ✅ 11 实验/3 图(单节点 Yellow 链、过滤→打分两段、磁盘三档水位)+ **均衡迁移动画 7 步**(旗舰 #6):单节点 same_shard NO → B 加入候选集{B} → R0 落 B INITIALIZING → Green → 新索引 P/R 交错 → C 加入 DesiredBalance relocation → 终态 2/1/1+水位收束;实验主线:explain 读出 same_shard 那一票(含 include_yes_decisions 对照)→ 水位/平衡因子默认值核对 → 副本 0↔1 的 Yellow⇄Green 开关
- 勘误:0 条(lessons 21-23 论断与 9.4.0 源码口径一致:GlobalRoutingTable/ProjectMetadata、hasQuorum 公式、AllocationDeciders NO 短路、水位三档与 max_headroom、LegacyBM25 之外的数字均无需修正;docker discovery.type=single-node 已在实验预期中对准)
- 全站:23/30 课正式,实验 294,动画 15;check.mjs + figwidth 全绿
- 下一步:P5 收尾 ch24(peer recovery·旗舰动画待做)+ ch25(熔断器水位动画待做),然后 P6 收官

### 2026-09-24(P4 完成 ✅,ch19+ch20 单课直写)
- 用户指示「把 P4 的剩下两课写完」,主会话直写,无代理、零 docker
- ch19 ✅ 17 实验/3 图(同车不走 Fetch、三层对象竖链、cherry 词频账本)+ cherry/shardSize 演算动画 6 步;实验三条线:小店 Bucket 套 Metric + 固定 key 对照 → s0+s1 两个单分片索引合搜(真实全局 apple:10/cherry:5 → shard_size=2 挤掉 cherry → 默认 13 救回 → size=3+shard_size=2 被 ensureValidity 抬底)→ 20 个唯一 user_id 看 sum_other=18 + breaker 只看名字限额
- ch20 ✅ 12 实验/3 图(名次 Query 已定、BM25 三件套、explain 两入口)+ **BM25 现场演算旗舰动画 7 步**(PLAN 旗舰清单 #9):语料统计 → 公式 → IDF → 饱和 → 单词 b 赢 → 双词 a 翻盘 → Legacy (k1+1) 折进 boost;实验含 explain boost=2.2 指认、function_score 翻倍、sort 换尺子 + track_scores、加不相干文档看老文档分数变大(ln(1.2)→ln(1.6))
- 勘误:0 条(shardSize 公式、mustReduceOnSingleInternalAgg、LegacyBM25Similarity、rescore 与 sort 互斥等论断与 9.4.0 一致)
- ch19 一次引号笔误(node --check 抓出)当场修复,其余首过全绿
- 全站:20/30 课正式,实验 257,动画 13;check.mjs + figwidth 全绿。**P4 验收点,等用户过目**
- 下一步:P5(ch21-25 分布式机制;ch22 选举时序、ch23 均衡迁移动画、ch24 peer recovery、ch25 熔断器动画待做)

### 2026-09-24(P4 续:ch18 单课直写)
- ch18 ✅ 19 实验/3 图(两套 rewrite 对照、match 切词 vs term 整串、must vs filter)+ match→SHOULD 翻译动画 6 步
- 实验一个索引打全场:_analyze 看词典 → match/term 四连(整串 0 hits / 碰巧命中 / 大写 miss / keyword 天作之合)→ operator:and 对照 → _explain 指认两条 should(含 explain:true 双入口)→ must/filter 同条件分数对照 → post_filter 聚合不看 → keyword 上 match 短路 → phrase 三档严格度(SHOULD<MUST<PHRASE)
- 勘误:0 条(keyword 短路、zero_terms_query、UsageTrackingQueryCachingPolicy 等论断与 9.4.0 一致)
- 全站:18/30 课正式,实验 228,动画 11;check.mjs + figwidth 全绿
- 下一步:ch19(聚合)、ch20(评分 + BM25 演算动画),P4 收尾

### 2026-09-24(P4 续:ch17 单课直写)
- 同 ch16 模式:主会话直写,无代理、零 docker
- ch17 ✅ 18 实验/3 图(SearchContext vs ReaderContext、三层查询字段、超时双出口)+ 上下文生命周期动画 6 步
- 实验两条线:tut-l17-timeout 先证明「3 篇 + timeout=1ms 快到看不见」,再用 script_score 忙循环把收集拉过检查点(timed_out: true → 禁部分结果后同因 429);tut-l17-pit 用 open_contexts 记账走 PIT 完整闭环(开 → 快照内写入不可见 → 对照普通搜索 → DELETE /_pit → 归零)
- PIT 实验链:站点 runner 无法自动串联返回值,id 由用户手动粘进后续 pit.id(predict/expect 里已写明操作)
- 勘误:0 条(原文自带的「旧课说错」更正已吸收进正文,如 SearchContext 不跨请求、QUERY_AND_FETCH 已删)
- 全站:17/30 课正式,实验 209,动画 10;check.mjs + figwidth 全绿
- 下一步:ch18-20(查询语法/聚合/评分;ch20 BM25 演算动画),token 允许时 3 个一批或继续单课直写

### 2026-09-23(P4 开局:ch16 单课直写)
- 此节为首次转写的历史记录；当前数量、勘误与实测以第十六章重构校对及 2026-10-12 日志为准。
- 背景:用户 token 紧张,指示「单独把 ch16 写完」,不起转写代理,主会话直写
- ch16 ✅ 14 实验/3 图 + **Query Then Fetch 两阶段旗舰动画 7 步**(PLAN 旗舰清单 #2):扇出即返回 → 每 shard 收 from+size 条 → 30 选 10 归并 → fillDocIdsToLoad 分组 → 只向持有者发 fetch → merge 组装,末帧对照 GET
- 实验设计:索引 refresh_interval=-1 冻结自动 refresh,让「GET 可见 / SEARCH 不可见」实验(9-12)无 1 秒竞态、结果确定;profile 用 size=10 与 size=1 对照观察「谁的 fetch 消失」
- 勘误:0 条(原文 max_result_window 公式、单 shard 优化、profile 两段论断均与 9.4.0 口径一致;原文 curl 示例给 _bulk 带 application/json 头属历史惯例问题,网站 console 已按 x-ndjson 正确发送,不登记)
- 全站:16/30 课正式,实验 191,动画 9;check.mjs + figwidth 全绿
- 下一步:token 恢复后按 3 个一批续 P4(ch17-20;ch20 BM25 演算动画待做)

### 2026-09-23(P3 完成 ✅,3+2 分批并行)
- 方式:按用户要求 3 个一批(ch11/12/13 → ch14/15),禁 docker 写进 prompt 最高纪律,错误码阶梯(未知路由 400/资源 404/方法 405/body 400)直接下发,agent 自检加 figwidth.mjs
- ch11 ✅ 19 实验/3 图 + 动态映射动画 7 步;ch12 ✅ 20/3(_simulate 为主);ch13 ✅ 13/4 + bulk 分组动画 6 步(严格避开 ch14 旗舰);ch14 ✅ 29/3 + **写入全路径旗舰动画 8 步**(双层舞台,refresh 与 flush 分叉一眼可辨);ch15 ✅ 16/3 + 路由公式动画 7 步
- 结构重排(有意为之,非勘误):tutorial lesson15 原主题是 IndexShard 生命周期,与 PLAN 旗舰清单「ch15 路由公式」方向不同——按清单立路由公式为主线,生命周期内容完整吸收为第 6、7 节与思考题,无丢失
- 勘误:本批 0 条(第三篇原文无「未知路由 404」类问题;ch12 正确区分了资源不存在 404 与未知路由 400)
- 集成期修复(全站性):bulk 实验暴露 es-client 对字符串 body 一律发 application/json(ES 的 _bulk 只认 x-ndjson,用户一跑必拒)→ raw() 改为按内容识别(JSON→json,其余→x-ndjson,且不自动补换行——「缺末尾换行 400」是 ch13 的教学点);console 校验门同样放行 ndjson;check.mjs 学会验证 ndjson + 新增 `allowInvalidBody: true` 豁免标记(ch13-02/04 故意写坏的 body 用)
- 全代理零 docker 违规;全站:15/30 课正式,实验 177,动画 8;check.mjs + figwidth 全绿
- 下一步:P4(ch16-20 搜索查询;ch16 Query Then Fetch 两阶段动画、ch20 BM25 演算动画)。P3 验收点,等用户过目

### 2026-09-23(P2 完成 ✅,多代理并行 + 一次限流中断)
- 方式:用户批准后 5 个转写代理并行(ch06-10 各一),只写各自 chNN.html/js,共享文件由主会话统一集成;每课原文仍只读一遍
- ch06 ✅ 10 实验/3 图(代理限流中断未交报告,结构自检全过);ch07 ✅ 9/3,2 勘误;ch08 ✅ 10/3 + 线程池 429 动画(6 步),线程池数字逐项实测吻合;ch09 ✅ 7/3,2 勘误;ch10 ✅ 19/3 + realtime GET 旗舰动画(7 步),实测发现 `?refresh=true` 默认被无视
- 中断:09-22 23:42 五小时限流 429(ch06/09/10 中断);窗口重置后 ch09 自行续完、ch10 复活续写、ch06 落盘内容已完整无需复活
- 修复:docker-compose.yml `allow-origin=*` YAML alias bug(代理实测坐实并验证修法,exit 70 → 正常启动);新增 tools/figwidth.mjs(SVG 估宽检查,配合 PLAN 排印纪律);index 5 张卡转正
- 纪律执行:叫停代理 docker 后各自清干净(es-tmp/es-study/es-verify 容器与 es 卷全部移除,机器无残留);用户将自己装环境,主会话未起 docker
- 全站:10/30 课正式,实验 80,动画 4;check.mjs + figwidth 全绿
- 下一步:P3(ch11-15 数据写入;ch11 动态映射、ch13/14 写入路径、ch15 路由公式动画)。P2 验收点,等用户过目

### 2026-09-21(规划)
- 探索阶段因「广度 agent 通读 1.1MB 教程 + 逐条 GitHub 对源码」触发 429(5h 限额),确立 token 硬纪律(见 CLAUDE.md)
- 已确认有价值结论:tutorial 30 课对齐 **ES v9.4.0** 源码(抽查 lesson08 线程池数字与 `DefaultBuiltInExecutorBuilders` 一致);`.pre-refactor-backup/` 为旧稿可忽略
- 用户三项决策:**保持源码深读 / 连本地真实 ES / 30 课全转**;vim_study 设计系统分析完成并作为视觉基线

### 2026-09-22(P0 脚手架)✅
- 落地:style.css(蓝青 accent 双主题)、nav/progress、es-client(fetch+ping+徽章+JSON 高亮+深链)、
  flow-player(快照式动画引擎,选区守卫)、experiments(章内实验运行器)、console(.js+.html,预设/历史/深链)、
  docker(compose+start.sh,9.4.0 单节点 CORS)、tools/check.mjs、index(30 卡)、cheatsheet 初版、
  CLAUDE/PLAN/STATUS 三件套、chapters/ 30 个 stub 页
- 待办:P1(ch01-05 转写,定标杆);docker 起 ES 后人工过一遍 console 全链路

### 2026-09-22(图示排印修复)
- 用户反馈 ch01 图内文字显示不全。根因:**CSS 覆盖 SVG font-size 属性**——.fig-name 在 CSS 是 15px,元素上的 font-size="13" 全部无效,长文本按 15px 渲染溢出盒子
- 修复:字号统一收进 CSS 并调小(fig-name 15→13 / fig-key 13→12 / fig-sub 12.5→12);清光所有 SVG 上的无效 font-size 属性;ch01 图1 左列盒子 170→230 重排;ch01 图2 箭头标签上移避让;ch03 图1、ch04 图2 长类名改两行(盒高 66→78);ch04 图1、ch05 图2 两处 sub 缩短
- 连带修掉两个潜伏 bug:CSS 里 .fig-arrow 写死 marker-end:url(#fig-arrowhead)(该 id 不存在)导致**全部箭头无头**——改回元素级引用;补 .fig-arrowhead 填色规则(原为纯黑,深色主题下不可见)
- 排印纪律已写入 PLAN.md(估宽公式、禁 font-size 属性、禁 CSS 级 marker-end),P2 起生效
- node --check ×2 + tools/check.mjs 全绿

### 2026-09-22(P1 完成 ✅)
- ch01 ✅:正文五节 + 3 张静态 SVG(倒排对照/分析链/分片放置)+ 1 个 flow 动画(近实时 5 步)+ 11 个实验
- ch02 ✅:结构课,2 实验(版本核对/节点角色);原仓库实验并入思考题
- ch03 ✅:2 实验 + 1 个竖版时间线动画(Node.start() 六站点亮顺序)
- ch04 ✅:2 实验(modules 数组/空 body 400 证路由归属);ClassLoader 隔离图 + 加载三步图
- ch05 ✅:8 实验(max_shards_per_node 全周期 + Final 对照);两图(契约对照/动态更新链)
- 勘误:第一篇五课原文论断抽查均正确,暂无登记项
- 用户指示(本篇期间):不启动 docker,代码按经验写
- 下一步:P2(第二篇 ch06-10,请求处理;ch10 有 realtime GET 动画)
