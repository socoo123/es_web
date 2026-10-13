# 第二十二章重构验收

2026-10-13（Asia/Shanghai）。已读 AGENTS、STATUS 本章进度/勘误与最近日志、PLAN、CHAPTER_STANDARD 和 CLAUDE；使用官方 Archify 3.0.1 技能及 Workflow v2/common schema、指定 example、repository authoring、viewer 与 delivery/布局契约。只重构 ch22，并更新首页该课计数、STATUS 和本课图源/产物/验收；未重读 tutorial、未使用子代理，复用共享 CSS/主题/重播脚本。

## 内容与源码依据

[源码审计](review/ch22-source-review.json)：**21个目标文件 / 65个精确区间 PASS**。ES固定提交 `2e8528e92361c3399724226deaf2b46f933e925b`（v9.4.0），干净实际 checkout；每个链接和图节点源区间合法、当地文件与固定 Git 对象字节一致。version.properties 对应 Lucene10.4.0。自动引用检查不代替人工机制核对，所引用目标代码已实际读取。

保留七段结构、3个可验证目标、目录和图解跳转、5道折叠问答、5条陷阱、速记和上下课/已读入口。正文按两个检查点组织：选举资格、发布状态的多数接受；再解释角色与名单、任期与本地模式、提交与应用、分区和请求不确定性。

主要修正及统一：

- `currentTerm` 先在 StartJoin 持久化再收 Join；失败选举也会推进，提议 `max(currentTerm,maxTermSeen)+1` 可跳号，同一节点也可再当选。API coordination.term 属于返回状态快照，不是 currentTerm 全历史。
- 9.4.0 ClusterStateAction 继承 TransportLocalClusterStateAction，直接读接入节点已应用状态；`?local=true/false` 已弃用且无效果。CAT master 也走该状态动作，无 master 视图可显示 `-`；不能沿用默认转发 master/强制等待发现的旧解释。CAT nodes 显式 full_id=true，修正短ID误比。
- master-eligible 角色不等于配置名单；只数配置成员内不同 ID。重配置可选子集/保留离线成员；选举 committed/accepted 双多数及附加策略，发布 committed/latestPublished 双多数，不能把名单并成一个N。voting_only 的额外策略/更鲜状态转移例外另列源码，不进入普通节点主图。
- pre-vote 过滤健康、已知 leader 及更鲜状态，有已知 leader 请求来自其自身的例外；是假 Join 试探而非正式票。请求/响应仍观察 maxTermSeen，高任期信息可能触发推进，不能承诺任意试探无副作用。
- Mode三值，leader先退候选再跟随；有效发布及满足条件的 follower check 都可能建立跟随，非仅收到任意 PublishRequest 即成立。
- 默认策略下发布双多数接受形成提交决定；后续提交通知、mark committed、apply 与请求确认分开。额外 beforeCommit 钩子可延后/失败；leader 的本地 apply 在发布结束阶段；非投票者也收状态，不把保存接口一概说成各角色相同落盘。
- 固定三节点分区中少数侧不能正常提交新状态，不代表旧节点立刻不自认 leader；完全断网是联系不到多数，不是收到拒票。检测、竞争与请求重试不保证固定恢复秒数；FailedToCommit契约允许提交不确定性，不宣称请求自动回滚或把集群状态共识等同于文档复制。
- `version` 对变化状态推进，建索引/分配/其他活动可多次推进；相同 mapping 合并可以返回原状态。移除 term=1 / version恰好+1 /全群green 的固定预期；single-node 启动检查限定已有非空 committed 配置，默认发布30s的调度在single-node中另处理。

正文、两图、七步机制解说、18卡、问答与速记一致。原动画中的 n1→n2→n3 链式发布、两侧角色矛盾和“任意高term自动胜出”已去掉；动画明确固定名单、默认策略、普通节点及单条概念路径。

## 实验设计与实际运行限制

原 **10个稳定ID全部保留**，新增8个，3组18操作（A5/B3/C8/清理2），七步旗舰ID不变。GET/HEAD没有body，18个HTML槽与注册顺序唯一对应。A确认版本/完整ID/本地读取与local弃用，B读实际两份名单/发现/默认和覆盖值，C用专属 `tut-l22-vote` 显式1主0副/auto-expand=false/strict mapping，HEAD空前提、创建、局部green等待、版本比较、配置读回、增字段、点名删除和HEAD404重做。不修改集群发现/投票配置；区分重复创建400、相同mapping可能无变化、重复删除404的条件。

**真实 API、本课初次运行和两轮重做：未实测。** [运行证据](review/ch22-es-runtime.json)：云端 Docker daemon 可用且已有官方9.4.0镜像；按仓库 Compose 实际启动 `es-study` 后，官方进程因运行环境缺少 `/proc/self/coredump_filter`，在 `Elasticsearch.setCoredumpFilter` 抛 RuntimeException/NoSuchFileException，容器退出1。实际启动日志显示固定9.4.0 build hash；没有可服务的9200节点，没有生成或模拟成功 API 响应。没有修改 ES 二进制或云端策略绕过该问题。

多节点竞争、失败轮次、投票配置变更、分区恢复、voting_only、提交/应用时序、发布超时及性能均未真实运行，只据固定源码解释。操作卡预期是待对应版本节点核对的条件化预测，不是本次测量结论。

## 官方 Archify 门禁与许可

两幅 Workflow v2，首次附固定源码证据并传实际 checkout `--repo-root`。只编辑candidate JSON，用完整finalize生成；HTML未手改。复用 `.archify/ARCHIFY-LICENSE.txt`，生成HTML保留字体许可。发布图review-2补明默认beforeCommit/插件边界，初稿及原收据保留。

| 图 | 当前 candidate SHA-256 | 当前 HTML SHA-256 | 当前收据 |
|---|---|---|---|
| election-gates | `5378b0d47824630f24306a388f6a9ea4e0981d4e6874d9e14be6d7241c6e1c4c` | `3615aa568199e1ba54b119e82e7cf9e747449fb325c35891bd1eb51f8b97ab9c` | 根目录 |
| publication-boundaries | `9988ec6b154929cc73ba1db7f0936c2db4b8df4ff6d872248270c3715c772db8` | `2cd620f71dba12921823eb41e20debfa571816a5bd1773c536384e4fcdc122d7` | review-2 |

两图 **validate、deliver、strict check：showcase9/9、0 errors/warnings、provenance current**。两图 **原生browser-check失败，finalize整体非成功**：Chrome导航报 `net::ERR_BLOCKED_BY_ADMINISTRATOR`，云浏览器禁止 `file://` 快照。没有修改策略/技能检查器或把HTTP结果改写成原生PASS。更新检查 unavailable、noticeRequired=false。

## 独立 HTTP、交互与实际视觉审阅

[HTTP](review/ch22-http-review.json)、[局部滚动](review/ch22-scroll-review.json)、[七步捕获](review/ch22-mechanism-review.json) PASS，文件哈希与当前章节/注册表匹配。HTTP用本机 Chromium/Python Playwright/临时同源静态服务器；深链控制台的ES请求显式abort，只验证真实页面导航与填写，不代表 API 成功。

- 两图各1440/1600/1920/2048×浅深，无整页横溢、说明卡完整。最小SVG/普通节点投影：election7.3418/8.3906px；publication6.3357/7.2408px（小号来源/辅助标记低于普通正文，但达到6px门槛）。
- 章节1920/1440/1024/768/390/320×浅深，桌面阅读列≤880px，各区左右边界差≤1px；页面与iframe无横溢，所有节点容纳完整、iframe无垂直裁切。初稿留白经实际截图审阅后收紧：桌面图高760/900px，≤800px460/500px。
- 节点源码探索/关闭、展开完整图、主题同步、暂停后外层重播/Enter、目录锚点/已读、七步前后/播放/暂停/重置/左右键全部PASS。
- 18张卡实际跳转控制台，method/path/body与注册请求对应；endpoint/auth别名/raw参数、`/es_web/`前缀资产/图/控制台验证PASS；`.nojekyll`在库中。未处理JS错误/异常HTTP响应为空。
- reduced motion覆盖图重播、图运动按钮禁用、机制不自动播放但可步进、页面无平滑滚动；390/320源码表和旧SVG仅在自身容器横滑PASS。
- **实际查看全部7张最终拼图，覆盖24张独立/嵌入/桌面/390px/实验/源码表/机制双主题捕获及全部7步完整快照**；之前较高图框也实际查看并据此收紧后重查。无文字/路径遮挡。手机Archify为概览，细字需要节点探索或展开缩放；必要结论在正文与图注。手机旧机制标题省略、画布局部横滑，步数、控制和解说可读。截图生成不等于审阅，另存[实际审阅绑定](review/ch22-visual-review.json)。

保留初稿 HTTP 与图高修正前的记录/截图作为历史，当前验收只使用根目录当前文件/当前哈希；最终[产物绑定](review/ch22-artifacts.json)明确区分通过项和受限项。

## 结构、复现与交付

`node tools/check.mjs`：30正式页/656实验卡/22机制 PASS；`node --check experiments/ch22.js`、figwidth、diff检查、10原ID/18有序唯一槽、GET/HEAD无body、点名资源范围PASS。首页只改ch22卡片计数，共享CSS/JS与其他章节未改。

```bash
node tools/check.mjs
node --check experiments/ch22.js
node tools/figwidth.mjs chapters/ch22.html experiments/ch22.js
ES_SOURCE_ROOT=/path/to/clean-es-v9.4.0 python3 .archify/review/ch22-source-audit.py
python3 .archify/review/ch22-http-review.py
python3 .archify/review/ch22-scroll-review.py
python3 .archify/review/ch22-mechanism-review.py
python3 .archify/review/ch22-visual-sheets.py # 生成拼图不代表已审阅
python3 .archify/review/ch22-bind-artifacts.py # 需已有当前真实审阅记录
# finalize workflow candidate.json output.html --repo-root ... --quality showcase --out-dir 新收据目录 --json
```

Python需要Playwright/Pillow，本环境使用 `/usr/bin/chromium`。其他环境可调整执行器路径；原生file导航受管理策略限制时如实保留失败。

按用户持续授权提交并推送origin/main。GitHub远端与Pages交付时另核对；本地HTTP通过不意味着Pages已经部署完成。

推送前同步远端新增 ch21 提交 `8518c6c`，保留该章代码/验收及STATUS表、勘误、日志；仅冲突的STATUS按两个章节分别合并。同步后站点统计为656卡（本课新增8卡），章节/图/JS与本课HTTP审阅字节不变。
