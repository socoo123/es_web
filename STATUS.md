# STATUS.md — 进度唯一真相

更新规则:做完任何一批工作就更新本文件 + 跑 `node tools/check.mjs`。

## 进度表(30 课)

| 课 | 标题 | 状态 | 实验 | 动画 |
|---|---|---|---|---|
| ch01 | Elasticsearch 是什么 | ✅ | 11 | 1(近实时) |
| ch02 | 项目结构全景 | ✅ | 2 | — |
| ch03 | 节点启动全流程 | ✅ | 2 | 1(启动时序) |
| ch04 | 插件体系 | ✅ | 2 | — |
| ch05 | 配置框架 | ✅ | 8 | — |
| ch06 | 请求入口层 | ✅ | 10 | — |
| ch07 | 动作框架 | ✅ | 9 | — |
| ch08 | 异步编程模型 | ✅ | 10 | 1(线程池 429) |
| ch09 | 传输层 | ✅ | 7 | — |
| ch10 | 跟踪一次文档读取 | ✅ | 19 | 1(realtime GET) |
| ch11 | 映射系统 | ✅ | 19 | 1(动态映射) |
| ch12 | 摄取管道 | ✅ | 20 | — |
| ch13 | 批量写入 | ✅ | 13 | 1(bulk 分组) |
| ch14 | 存储引擎 | ✅ | 29 | 1(写入全路径·旗舰) |
| ch15 | 索引分片 | ✅ | 16 | 1(路由公式) |
| ch16 | 搜索流程总览 | ✅ | 14 | 1(Query Then Fetch·旗舰) |
| ch17 | 搜索服务与搜索上下文 | ✅ | 18 | 1(上下文生命周期) |
| ch18 | 查询语法 | ✅ | 19 | 1(match→SHOULD) |
| ch19 | 聚合框架 | ✅ | 17 | 1(cherry/shardSize) |
| ch20 | 评分与排序 | ✅ | 12 | 1(BM25 演算·旗舰) |
| ch21 | 集群状态 | ✅ | 16 | — |
| ch22 | 主节点选举与共识 | ✅ | 10 | 1(选举时序·旗舰) |
| ch23 | 分片分配 | ✅ | 11 | 1(均衡迁移·旗舰) |
| ch24 | 分片恢复与快照 | ✅ | 20 | 1(peer recovery·旗舰) |
| ch25 | 熔断器与背压 | ✅ | 14 | 1(熔断水位·旗舰) |
| ch26 | 脚本引擎 | ✅ | 20 | 1(编译旅程) |
| ch27 | 管道查询语言 | ✅ | 14 | 1(管道执行) |
| ch28 | 索引生命周期管理 | ✅ | 20 | 1(一分钟 rollover) |
| ch29 | 安全机制 | ✅ | 19 | 1(认证链) |
| ch30 | 全景回顾与方法论 | ✅ | 13 | 1(全链回放) |

## 勘误表(tutorial 原文 → 网页修正)

| 课 | 原文说法 | 修正 | 依据 |
|---|---|---|---|
| ch07 | 未知路由(如 `GET /_cat/actions`)回 404 | 9.4.0 回 **400** `no handler found for uri [...]`;404 留给「路由命中、资源不存在」 | 本地 9.4.0 实测 |
| ch07 | 缺 id 的 `GET /{index}/_doc/` 在 PathTrie/REST 层被拒(404/缺参) | 实测 **405** `Incorrect HTTP method … allowed: [POST]`——尾斜杠归一后命中的是 POST 自动生成路由,属方法不匹配 | 本地 9.4.0 实测 |
| ch09 | `GET /_cat/transport` 当前是 404 | 同上口径:未知路由回 **400**(与 ch07 相互印证) | 本地 9.4.0 实测 |
| ch09 | 暗示单节点本机环回仍计传输层 rx/tx | 建索引+写入+GET 后 server_open/rx/tx **全 0**,本地路径不产生传输层记账 | 本地 9.4.0 实测 |
| ch08 | (线程池数字全面核对,无勘误) | search=((N*3)/2)+1、queue=size×1000、write=max(N*750,10000) 等逐项吻合 | 本地 9.4.0(N=12)实测 |
| ch06 | (未收到代理报告,限流中断;内容按正文自纠口径核对过结构) | — | — |
| ch10 | 「RestGetAction 一共 76 行」属版本易变数字(非错误) | 网页写「不到百行」不写死;另实测确认 `?refresh=true` 在默认 realtime 下被无视,需配合 `realtime=false` 才刷新(已写进实验) | 本地 9.4.0 实测 |
| ch27 | 「`POST /_esql` 会 404」 | 实测 **405** `Incorrect HTTP method ... allowed: [GET, PUT, DELETE, HEAD]`——`/_esql` 撞上裸索引路由 `/{index}`(POST 不在 allowed),非「无 handler 400」更非 404;镜像:`GET /_query` → 405 allowed [POST] | 本地 9.4.0 实测 |
| ch28 | 「新建的 tut-l28-logs-000002 绑定同一策略名」 | 实测 alias 方式 rollover **不复制** `index.lifecycle.name`:000002 settings 无 lifecycle 键、managed=false,链条滚一代即断;正解是 index template 接力,且模板只带 settings——模板带 rollover alias 本体会 ERROR step(duplicated alias) | 本地 9.4.0 实测 |
| ch28 | 课末清理用 `DELETE /tut-l28-*`(通配符) | 默认 **400** `Wildcard expressions or all indices are not allowed`——`action.destructive_requires_name` 默认 true,清理须显式点名;网站将该 400 做成实验(桥接 ch29) | 本地 9.4.0 实测 |
| ch29 | 暗示 401 只带一个 `WWW-Authenticate: Basic realm="security", charset="UTF-8"` | 9.4.0 实测为**双挑战**:`Basic realm="security", charset="UTF-8"` + `ApiKey` 两个响应头 | 本地 9.4.0(9201)实测 |
| ch01/02/20 | tutorial 与网页写 Lucene **10.3.2**、JDK **25.0.2+10**、Netty **4.1.130.Final** | Lucene **10.4.0**、bundled JDK **26.0.1+8**(节点 API 显示 `26.0.1`)、Netty **4.1.132.Final**。Jackson 2.15.0 / Log4j 2.19.0 / ANTLR 4.13.1 与 tag 一致,未改 | [v9.4.0 version.properties](https://github.com/elastic/elasticsearch/blob/v9.4.0/build-tools-internal/version.properties) |

## 会话日志

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
