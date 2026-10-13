# ch28 索引生命周期管理重构验收

本轮范围：ch28、首页对应卡片、STATUS及本章图源/产物/验收证据。按序读取AGENTS/STATUS/PLAN/CHAPTER_STANDARD/CLAUDE；未重新阅读tutorial，未使用子代理。开工HEAD与origin/main一致；已有.gitignore修改保留，不纳入本轮提交。

## 内容与源码

Elasticsearch9.4.0固定提交 `2e8528e92361c3399724226deaf2b46f933e925b` / Lucene10.4.0。真实干净源码checkout按目标方法阅读；18个文件、30段固定源码字节与行号核对见 `review/ch28-source-review.json`。HTML给具体文件/方法链接，图中每个语义节点有固定源码证据，正式finalize使用真实 `--repo-root`。

修正：warm2h与delete24h使用同一个生命周期零点，不是warm后再加24h；本课无origination_date，rollover更新老索引起算日期，自定义origination_date另有优先分支。rollover.max_age仍从创建年龄计算；普通alias条件路径至少一max、全部min。默认空索引保护与本课显式min_docs2分开；周期调度与状态变化推进入口分开，不保证一次poll或固定80秒完成。初始化new是快照，不是稳定响应。

策略相缓存的安全刷新还需元数据、非ERROR、当前步骤存在和定义可解析，最终比较实际StepKey集合。相同策略与安全headers可no-op，不是每次PUT都增版本。模板注入下一代生命周期设置，不重复声明rollover alias本体；模板可含mappings，其他别名不在禁令内。data stream仍需ILM模板配置，不能混同Data Stream Lifecycle。显式true是本课配置，单目标经典alias未设write_index也有可写分支。indexing_complete不是index.blocks.write；allocate在warm/cold，不笼统列作hot动作。删除策略检查扫描索引策略名，不是单独维护的引用计数；poll=null去除一层覆盖，不总是恢复默认。

## 实验与真实ES

原20实验ID和 `ch28-ilm-rollover` 七步机制ID保留。两组40卡：前置3 / A23 / B7 / 清理7。专用单节点localhost:9200匿名节点真实根响应确认9.4.0/10.4.0及固定build_hash；ILM RUNNING，初始poll无覆盖、默认10m，destructive_requires_name=true。

A：1P0R、strict keyword msg、refresh_interval=-1，固定ID写入显式refresh；先一篇让min_docs2不满足，等待实际hot/check-rollover-ready及max_age=true，添加Hot forcemerge后稳定观察活策略v2与老相缓存v1，第二篇放行。随后确认两代出现、alias旧false/新true、老相hot/complete与新相Hot缓存v2、生命周期日期更新、indexing_complete=true。alias后续写入实际落000002，其一篇未再触发下一代。

B：独立空索引/alias/策略，显式min_docs2；仅将max_age从1m改10m，缓存实际刷新v2/10m。空索引保持等待，不发生B组rollover。

**两轮各40张卡均真实通过**，状态等待产生每轮81/85次请求；每轮另7项真实观察：同策略PUT的no-op与版本仍2、固定IDupdated200、重复创建400、三个索引各自HEAD404。顺序与原始完整请求/响应见 `review/ch28-es-review.json`；不是合成响应。模板与两策略点名删除，poll在每轮与finally恢复真实原值，三个索引最后分别不存在。页面的合并HEAD404不能单独证明每个名称均不存在，卡片与验收脚本已明确区分。

本轮不等待warm2h/delete24h，不实测跨节点迁移、CCR、searchable_snapshot、data stream/DSL或认证权限；这些结论按固定源码/适用条件说明。历史无模板及重复alias错误不冒充本轮API实验。

## 官方Archify原生门禁

官方Archify3.0.1、workflow v2、zh-CN/showcase/trace。只编辑JSON并正式finalize，未手改HTML。两幅当前validate、deliver、strict check与原生file:// browser-check全部通过，showcase **9/9，0错误0警告**；当前本机file浏览器可用，不沿用旧云环境限制。update.noticeRequired=false。

当前收据：rollover-clocks `review-3`（补全匹配模板源码证据）；phase-cache `review-2`。原稿与旧收据保留：phase-cache初稿因共享高度触发composition/viewport-height，通过同列纵向步骤测量修复；rollover初稿原生通过，但独立HTTP最小字5.401px，保留诊断后将delete放入阶段计时行，保留全部8节点/7关系并重新生成。最终HTTP最小SVG字6.477/6.772px，普通节点字7.402/7.739px（1440px）。原生建议关注old→wait与keep→transition绕行；已查看完整浅色rollover与深色cache图，关系方向、分支和标签均可追踪，没有交叉遮挡；建议不计作警告通过数。

复用 `.archify/ARCHIFY-LICENSE.txt`，保留生成HTML内字体许可与delivery哈希。根/旧revision收据属于历史候选，不能当当前产物绑定；当前SHA与门禁绑定见 `review/ch28-artifacts.json`。

## HTTP、布局与实际视觉审阅

两独立图：1440/1600/1920/2048px × 浅深；章节：1920/1440/1024/768/390/320px × 浅深均通过。桌面880px阅读列，各区左右差≤1px；390正文362px、320正文292px，整页及iframe无横溢、所有节点包含、独立说明卡无截断。桌面嵌入900px，≤800px为620px，两图按实际测量设置；未改共用CSS/控制逻辑。

主题同步、节点源码探索/关闭、Enter/Escape、展开无present、暂停后外层重播与键盘重播、reduced-motion静止且禁动态切换、七步/回退/播放/重置、目录锚点、已读、全部40请求method/path/body深链、端点/认证别名/raw及/es_web/资产前缀通过。HTTP控制台自动执行流量明确abort，导航检查与真实ES API记录分开；无未处理JS或失败HTTP资产。390/320的源码表与760px机制SVG在自身容器内可横向滚动，不引起整页滚动。

**已实际通过view_image查看7张联系表（24张章节/图解双主题及窄屏截图，全部7个完整机制快照），另查看完整浅色rollover和深色cache图。** 图片生成与实际审阅分开记入 `review/ch28-visual-review.json`。图的手机版为完整路径总览，细字通过探索/展开/正文读取，不宣称小屏显示全部桌面细节；展开入口与控制可发现。动画手机快照局部横滑，控制和解说可读。

## 检查与复现

`node tools/check.mjs`：30正式页、803操作卡、22机制播放器全绿；`node --check experiments/ch28.js`、figwidth、diff检查通过；.nojekyll保留。操作顺序/原ID、源码、API、HTTP、局部滚动、机制截图、视觉审阅及当前产物SHA分别保存。

Python验收使用Playwright/Chromium与Pillow；`review/ch28-es-review.py`仅用于无本课资源遗留的专用匿名单节点，创建并点名清理本章资源，临时修改poll并恢复。`ch28-source-audit.py`核对固定checkout（ES_SOURCE_ROOT可覆盖）；`ch28-http-review.py`/`scroll-review.py`/`mechanism-review.py`独立验证；`visual-sheets.py`只生成联系表，不能替代实际查看；`ch28-bind.py`绑定当前图源/HTML、当前原生收据与其他验收哈希。
