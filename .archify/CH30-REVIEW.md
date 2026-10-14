# 第30课重构与验收 · 2026-10-14

本轮仅重构 ch30。依据 AGENTS、STATUS、PLAN、CHAPTER_STANDARD、CLAUDE 与官方 Archify 3.0.1 技能；不重复读取 tutorial，不改其他章节与共用控制代码。

## 内容与实验

保留七段式、三个可验证目标、章节目录/图解跳转、上一课与课程入口、已读进度。两幅交互图分别解释普通多分片搜索的职责交接、读者的源码阅读顺序；后者是方法概念图，不声称是运行时调用链。单节点单分片 API 与多分片概念分开。

保留原13个实验ID、`ch30-finale` ID与七步播放器；扩充到5组20卡：A准备与基线5 / B失败3 / C可见性6 / D统计与Task4 / E清理2。显式端点9200、匿名认证、1主片0副本、strict title:text/standard、refresh_interval=-1、max_result_window=10000；健康/count限定本章资源。点名清理、重复创建/写入/删除语义、完整重做与重新记N均明确。无全局配置修改。

主要勘误：

- 窗口检查在分片 `DefaultSearchContext.preProcess`、主Query之前，不是协调扇出前；`getTopDocsSize` 是协调归并逻辑，rank有分支。
- `prepareRequest`和后置检查后才增加REST usage；非法search_type不计，分片窗口失败计。本课一次顺序执行增量5；count内部复用搜索不等于search_action入口。
- refresh响应是复数 `_shards`；成功refresh不保证每次生成新段，不代表flush提交。
- `void + listener`只说明结果协议；不能单独证明换线程或不阻塞。快照不代表所有节点同时最新；Task是运行中采样，不能证明动作注册或历史。
- 单token match不一定生成SHOULD布尔查询；候选可少于from+size；Fetch可取_source及其他字段。单分片优化不证明两次网络往返。
- 实时GET可读未对搜索可见的写入，但响应不证明必从translog读；读者取得时间、外部refresh、旧PIT等条件需另判。
- Painless可以参与_search，安全认证与Action授权有不同位置；不能把所有高级专题都排除在搜索链外。

固定源码身份 ES v9.4.0 / `2e8528e92361c3399724226deaf2b46f933e925b`，Lucene10.4.0。手工读取相关生产/测试方法；`review/ch30-source-review.json`验证13文件24范围的固定字节与有效行号、原ID与操作顺序。字节检查不独立证明语义。

## 真实 ES

`review/ch30-es-review.json`记录本地9200版本、构建号、实际HTTP状态/响应头/body、两轮20张操作卡（共40次）。两轮均通过，usage均N+5；未刷新搜索0、实时GET200/true、非实时GET404/false，显式refresh后新搜索1；窗口400含failed_shards；重复清理404。最终HEAD确认tut-l30-docs不存在。

未运行ES Gradle单测/YAML套件；本轮测试文件只是源码约束依据。未实测多节点网络两跳、安全开启、PIT、rank、kNN、跨集群与性能；不把单节点响应当这些场景的证明。

## Archify 正式门禁

图源/HTML见 `review/ch30-paths.json`。搜索图携带固定源码证据，正式finalize传 `--repo-root /tmp/es-ch15/es-v9.4.0`；方法图明确为概念图。

- 搜索图当前收据：`workflow-ch30-search-handoffs-20261014-084552/review-4/`。
- 方法图当前收据：`workflow-ch30-reading-loop-20261014-084552/review-3/`。
- 当前 validate / deliver / strict check / native browser-check全部pass；两图均showcase 9/9，零错误/警告，零交叉/路由绕行。update回执为current 3.0.1，无升级提醒。

保留早期失败/修复收据：一处源码引用尾行超范围后改为实际merge方法范围；蛇形列违反mainPath非递减规则后改为同列纵向；截图发现主链偏左，经JSON扩大节点并调整逻辑列后正式重新生成。HTML未手改。旧原生收据与 `review/ch30-initial-visual/` 不代表当前产物。

复用 `.archify/ARCHIFY-LICENSE.txt`，生成HTML保留字体许可及delivery哈希。当前source/HTML、门禁、HTTP/API/source/visual/scroll证据的SHA-256绑定见 `review/ch30-artifacts.json`。

## HTTP、布局、交互与视觉

独立HTTP报告 `review/ch30-http-review.json`：两图各1440/1600/1920/2048浅深主题；章节1920/1440/1024/768/390/320浅深主题，12组合。桌面阅读列880px、标题/正文/图框/图注/表格/实验/章节尾边界误差≤1px；390正文362px。页面与iframe无横向溢出，全部图节点在初始面板内；嵌入高度桌面900、≤800宽620，根据实际内容验证。

验证节点探索/关闭、搜索图源码链接、Enter/Escape、暂停后外层重播、键盘重播、父图主题同步、展开完整图、七步播放器步进/键盘/播放暂停、目录锚点、已读切换、20条控制台请求的端点/匿名别名/method/path/body、`/es_web/`前缀与相对资源、reduced motion优先（图静止、重播不强制动态、播放器不自动播放且可步进、无平滑滚动）。无未处理JS错误或失败HTTP资产。

此HTTP检查明确abort ES端点请求，防止控制台自动运行重复改变实验；真实API是独立Python执行的上节记录。两类证据不互相替代。

实际查看31张最终截图组成的7张联系表：章节头桌面/390浅深、两图独立1440浅深与嵌入浅深、两图390浅深、实验卡与源码表390浅深、机制播放器桌面/390浅深、全部七步快照（深色）。纵向主链现居中、直连箭头清楚，无节点/文字截断。手机图保留完整概览，细节可点节点/放大/展开；必要解释全部写在正文与图注。机制SVG与源码表可局部横向滚动，提示明确；`ch30-scroll-review.json`另外验证390/320双主题确实可滚到末端，整页仍无溢出。

`node --check experiments/ch30.js`、实际展开机制快照的figwidth、`node tools/check.mjs`通过；全站823操作/22机制动画。未改变其他章节共享样式/脚本，因而无需全站视觉回归。

脚本可通过Python+Playwright/Pillow复现；source-audit需要固定版本Git checkout，es-review要求本章索引不存在的专用节点。visual-sheets只生成联系表，不替代实际查看；visual-review记录审阅范围。

本轮按仓库授权提交并推送origin/main；交付提交链接。Git push实际结果另记STATUS会话日志。
