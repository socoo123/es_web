# STATUS.md — 进度唯一真相

更新规则:做完任何一批工作就更新本文件 + 跑 `node tools/check.mjs`。

## 框架学习篇与旅游搜索实验

规划见 [FRAMEWORK_PLAN.md](FRAMEWORK_PLAN.md)。新增第一部分采用独立 F 编号；现有源码篇 ch01–ch30 的编号、链接与图解重构状态继续保留。

| 项目 | 当前状态 |
| --- | --- |
| 两部分课程规划、45 课目录与交付顺序 | ✅ 新规划已落盘，替代最初 14 课方案；尚未实施入口改造 |
| F01–F45 框架课程与项目实验 | 待编写与真实验收；第一部分为学习核心 |
| 155 个核心案例 | ✅ [案例设计清单](FRAMEWORK_CASES.md)；代码/运行/验收待做 |
| 旅游门户前台/Java 后端/管理后台/教学订单 | 待实现；贯穿景点、酒店、房型、日期报价与库存 |
| PostgreSQL WAL / MySQL binlog → Kafka → Java → ES | 必修链路已规划；连接器、投影与故障恢复尚未实测 |
| 中文分词对比、词典与同义词实验 | 已规划比较方法；插件安装与效果未实测 |
| Java / Spring Boot 版本组合 | 已核对官方集成路线；依赖锁定、构建与真实连接待做 |

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
| ch23 | 分片分配 | ✅ | 11 | 1(均衡迁移·旗舰) | 待改造 |
| ch24 | 分片恢复与快照 | ✅ | 20 | 1(peer recovery·旗舰) | 待改造 |
| ch25 | 熔断器与背压 | ✅ | 14 | 1(熔断水位·旗舰) | 待改造 |
| ch26 | 脚本引擎 | ✅ | 20 | 1(编译旅程) | 待改造 |
| ch27 | 管道查询语言 | ✅ | 14 | 1(管道执行) | 待改造 |
| ch28 | 索引生命周期管理 | ✅ | 20 | 1(一分钟 rollover) | 待改造 |
| ch29 | 安全机制 | ✅ | 19 | 1(认证链) | 待改造 |
| ch30 | 全景回顾与方法论 | ✅ | 13 | 1(全链回放) | 待改造 |

转写状态与图解重构分别统计；重构已完成不代表真实 ES 实验或技能原生浏览器检查全部通过，具体结果见会话日志。

## 勘误表(tutorial 原文 → 网页修正)

| 课 | 原文说法 | 修正 | 依据 |
|---|---|---|---|
| ch07 | 未知路由(如 `GET /_cat/actions`)回 404 | 9.4.0 回 **400** `no handler found for uri [...]`;404 留给「路由命中、资源不存在」 | 本地 9.4.0 实测 |
| ch07 | 缺 id 的 `GET /{index}/_doc/` 在 PathTrie/REST 层被拒(404/缺参) | 实测 **405** `Incorrect HTTP method … allowed: [POST]`——尾斜杠归一后命中的是 POST 自动生成路由,属方法不匹配 | 本地 9.4.0 实测 |
| ch09 | `GET /_cat/transport` 当前是 404 | 同上口径:未知路由回 **400**(与 ch07 相互印证) | 本地 9.4.0 实测 |
| ch09 | 暗示单节点本机环回仍计传输层 rx/tx | 建索引+写入+GET 后 server_open/rx/tx **全 0**,本地路径不产生传输层记账 | 本地 9.4.0 实测 |
| ch08 | (线程池数字全面核对,无勘误) | search=((N*3)/2)+1、queue=size×1000、write=max(N*750,10000) 等逐项吻合 | 本地 9.4.0(N=12)实测 |
| ch06 | 原转写未形成完整代理报告 | 本轮按固定 v9.4.0 源码完成入口边界校对；详细勘误见下方第六章表 | [.archify/CH06-REVIEW.md](.archify/CH06-REVIEW.md)；本轮 API 未实测 |
| ch10 | 「RestGetAction 一共 76 行」属版本易变数字(非错误) | 网页写「不到百行」不写死;另实测确认 `?refresh=true` 在默认 realtime 下被无视,需配合 `realtime=false` 才刷新(已写进实验) | 本地 9.4.0 实测 |
| ch27 | 「`POST /_esql` 会 404」 | 实测 **405** `Incorrect HTTP method ... allowed: [GET, PUT, DELETE, HEAD]`——`/_esql` 撞上裸索引路由 `/{index}`(POST 不在 allowed),非「无 handler 400」更非 404;镜像:`GET /_query` → 405 allowed [POST] | 本地 9.4.0 实测 |
| ch28 | 「新建的 tut-l28-logs-000002 绑定同一策略名」 | 实测 alias 方式 rollover **不复制** `index.lifecycle.name`:000002 settings 无 lifecycle 键、managed=false,链条滚一代即断;正解是 index template 接力,且模板只带 settings——模板带 rollover alias 本体会 ERROR step(duplicated alias) | 本地 9.4.0 实测 |
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

## 会话日志

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

### 2026-10-12（框架篇提升为核心：45 课旅游门户与 155 案例）

- 用户明确至少 30 课、从零完成旅游门户、前后端代码纳入实验，并强调景点/房型评分排序与 PG/MySQL 日志同步。将未实施的 14 课规划改为 F01–F45 / 九个单元；源码 ch01–ch30 编号、路径与本轮重构状态保留。
- 新增 FRAMEWORK_CASES：35 课各 3 案例、评分/酒店 F16–F25 各 5，共 155 个已设计/未实现案例。完整系统规划 Vue 前台/后台、Java、数据/索引、中文搜索、报价/教学预订、PG/MySQL CDC、重建与运维；按课提供代码入口、数据与可运行阶段快照。
- 将日志驱动同步提升为必修，核对 Debezium PG/MySQL、PG 重复消息、ES 评分/nested/collapse/版本与 Vue 官方文档。明确同房型条件、符合条件最低价、多晚库存、准确总价排序范围、数据库下单复核、至少一次处理、多表投影和删除重放保护；当前仅调研/规划，没有新工程或链路运行。
- 45 课连续编号、155 案例序号/数量、50 个评分与酒店案例、文档本地引用/代码块、`git diff --check` 与 `node tools/check.mjs` 全部 PASS。本轮仅规划，无新页面/工程/链路，前后端构建、业务 API、浏览器、真实 CDC/ES 案例未执行。按授权只提交五份规划文档并推送 origin/main，远端交付时核对；其他任务代码/图源/验收与 .gitignore 修改不纳入。

### 2026-10-12(第十八章按统一规范重构)

- 固定ES9.4.0/Lucene10.4.0：18源码文件/39精确区间及2个Lucene固定tag文件；重排Builder/Lucene改写、字段分析/工厂、词项/位置、评分/should门槛、缓存条件、两路收集和Explain。正文/两图/六步/卡片/5问答/4陷阱/速记一致。
- 保留原19稳定ID，3组34卡（A13/B9/C11/清理1）、2交互图/2有限trace/1六步机制；显式standard/keyword normalizer/strict/stored source/词向量、一主零副/无管道/周期刷新关闭/局部green/固定ID+refresh/点名清理与重做。全站30正式页/604卡/22机制；共享CSS/JS和其他章节未改。
- 官方Archify3.0.1 Workflow v2，首次附真实固定源码/checkout、仅改JSON。translation当前review-2，collection review-3；validate/deliver/strict check showcase9/9、0errors/warnings、provenance current，原生browser-check与finalize整体PASS。双列手机裁切修复为纵向独立路径，主收集路径直连；聚合绕行保留且实际审阅无交叉/语义错误。旧图源/收据/诊断保留，许可及HTML字体许可保留。
- HTTP两图四档桌面/双主题、章节六档宽度、880px/≤1px对齐、页面/iframe/节点完整、探索/来源/关闭/展开、暂停后重播/Enter、目录/已读、六步控制/键盘、34实际控制台导航method/path/body、endpoint/auth/raw、Pages前缀、reduced motion PASS。390/320源码表/旧SVG局部滚动PASS。实际查看24张最终截图与全部六步；手机图为概览，细字需探索/展开，必要解释在正文/图注。
- **真实API两轮每轮34卡PASS**：旧GET Explain两卡真实400缺query，POST后200；词项/保存位置/标点小写、text match/term/keyword normalizer、OR/AND/反向与间隔phrase、stop零词项none0/all4、validate OR、两入口Explain/别名false且含status约束；filter→must分数1.1608025→1.5174774，纯filter三篇0，should默认可选与显式门槛对照；post_filter聚合published3/draft1，query.filter只published3。另8条重复性观察确认重复创建400/写入updated200/删除404及实际mapping/settings。mapping冗余search_analyzer省略导致初始验收守卫失败，修正后针对性重做通过，最终父索引/别名HEAD404。浏览器阻断ES自动执行，真实API单列；未实测多节点/词图/模糊/缓存收益或性能。
- 站点、JS语法、figwidth、diff、19稳定ID/34有序唯一槽位、GET/HEAD无body与.nojekyll PASS。验收[CH18-REVIEW](.archify/CH18-REVIEW.md)、[HTTP](.archify/review/ch18-http-review.json)、[真实API](.archify/review/ch18-es-review.json)、[artifacts](.archify/review/ch18-artifacts.json)。按授权提交推送origin/main；远端与Pages在交付时另核对，原有.gitignore修改不纳入。

### 2026-10-12（框架学习篇与旅游搜索综合实验规划）

此条为初始 14 课方案的历史记录，当前范围已由上方 45 课/155 案例规划替代。

- 根据用户需求规划「框架学习篇 → 旅游搜索实验 → 源码篇」路线，新增 FRAMEWORK_PLAN；14 课覆盖基础 API、DSL/分页/聚合/地理查询、中文分析、Java/Spring Boot、数据同步与相关性评估。综合实验按 REST 原型、可用搜索页、工程完善三次交付。
- 新篇使用 F01–F14 / fNN- 实验前缀，课程进度与项目里程碑分别统计；规划首页与目录、校验器扩展、旧深链与已读兼容。只修改规划文档，现有源码章节、编号、图源与重构状态未改。
- 核对官方 Java API Client、Spring Data 版本矩阵、SmartCN/ICU/IK 与 synonym_graph 文档。中文插件安装/效果、Java 依赖下载/构建/运行、旅游业务 API 和浏览器验收均未执行，不将调研写为运行通过。
- 文档本地引用、14 课连续编号、`git diff --check` 与 `node tools/check.mjs` 均 PASS；本轮仅文档，没有新页面、图解或项目，HTTP 浏览器、Archify 原生门禁及真实 ES 实验不适用。按仓库授权仅提交本轮四份规划文档并推送 origin/main，远端结果交付时核对；已有 .gitignore 与 ch18 章节/实验/图源/验收工作文件不纳入。

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
