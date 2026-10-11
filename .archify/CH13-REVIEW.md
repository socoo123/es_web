# 第十三章重构验收

时间：2026-10-11T16:15:06.574705+08:00。范围仅 ch13 HTML / 注册表、两幅 Archify图、STATUS 与本章验收证据。共享 CSS / JS 未改；自动提交与推送遵循 AGENTS / CHAPTER_STANDARD 的持续授权。

## 内容与固定版本依据

Elasticsearch9.4.0、Lucene10.4.0；源码仓库 https://github.com/elastic/elasticsearch.git，提交 `2e8528e92361c3399724226deaf2b46f933e925b`，checkout `/workspace/scratch/es-v9.4.0`。tracked source clean，已读本章涉及的目标文件及少量固定git对象，没有重读tutorial或通读其他章。审计核对 **20文件 / 46精确区间**，在当前章节与图源中可追溯；缺少工作区文件时记录 localCheckoutPresent=false，使用固定提交字节。[审计](review/ch13-source-review.json) / [复现脚本](review/ch13-source-audit.py)。

章节约4286中文字符，lesson约2656；七段式、880px阅读列、目录、图解跳转、五个源码入口、五道折叠题、五条陷阱与速记保留。正文、图注、机制解说、实验与STATUS同步修正：

- action决定NDJSON行数，delete单行；原动画五行误写六行、按奇偶定位，已改。index/create第二行切字节，update第二行直接解析；解析失败位置受摄取/索引模式影响。
- 默认rest.incremental_bulk=true，可按压力条件拆执行批次；整包与实际流式入口分开说明。后续请求级400不能推出已执行前缀无副作用，bulk不提供回滚。
- 协调角色可同节点承接primary；管道处理在路由分组前，按完整ShardId归组，items按操作编号回填，不是物理行号/跨分片执行顺序。batch优化默认关闭，另受feature flag与操作类型限制。
- 路由公式限定新建普通非分区索引及创建版本；Final更新被拒不改变原路由，不带routing可因同片碰撞命中。普通内部版本delete不建目标，外部版本有例外。
- delete缺ID的404/not_found无error，缺索引的404带error；顶层errors按isFailed判断。请求级错误、分片失败、条级error与业务结果分开，重试须考虑已写入/脚本副作用。
- active门槛在写前，DEFAULT取索引设置；all不是复制成功票数。普通副本故障与primary降级/写后失败分开；未分配副本可total2/successful1/failed0。无固定seq_no=0承诺。
- refresh请求策略只覆盖触及分片，不改索引设置；false不承诺未可搜，wait_for可由不同刷新来源满足，监听槽耗尽可强制刷新。GET realtime、搜索reader与同步工作分开。

## 操作卡与真实API状态

保留全部13原稳定ID，新增27，**4组 / 40卡（A14、B7、C9、D7，清理3）**；保留 ch13-bulk-group 与6个完整机制快照，Archify的2条有限trace另计。槽位顺序与注册顺序一致。

资源仅 tut-l13-items、tut-l13-routed、tut-l13-waiting；tut-l13-nope只用于普通delete/HEAD缺索引前提。三个索引显式standard、stored source、strict keyword mapping、2/2/1主分片、0/0/1副本、非分区路由、无default/final管道、auto_expand=false、refresh=-1、write.wait=1、durability=request。限定健康等待；四张故意非法NDJSON卡保留raw标志；坏项后的GET、单键选片与CAT数据证据、refresh前后count/realtimeGET、all/1与读回分开。C组临时设1s后恢复-1；三索引点名删除，允许重复清理，再从A1完整重做。说明创建、index/create重复、旧搜索视图和等待恢复条件。

**真实ES首次与清理后重做均NOT RUN**。当前curl访问127.0.0.1:9200拒绝连接，/proc/self/coredump_filter不存在；既有运行环境启动记录 `/workspace/scratch/es_web-onboarding/start.md` 说明固定9.4.0在此环境bootstrap受该proc接口阻断。未循环启动Docker、降版本、修改ES、伪造proc/API响应。所有卡片为固定源码推导预期，页面也明确写出，不能宣称多节点复制故障已验证。

## 官方Archify与原生门禁

使用[官方Archify3.0.1技能](https://github.com/tt-a1i/archify/tree/v3.0.1/archify)，本地 `/workspace/shared/skills/archify-3.0.1/archify/SKILL.md`；阅读authoring defaults、repository authoring、Workflow/common schema、精确Workflow example、layout/viewer/failed-finalize契约。首次JSON就附真实源码证据及--repo-root；只生成HTML，没有手改产物。

| 当前产物 | candidate SHA-256 | HTML SHA-256 |
|---|---|---|
| [bulk-journey](../.archify/workflow-ch13-bulk-journey-20261011-155725/bulk-journey.html) · Workflow v2 | `27ea8c69843b4c2be1ef588ca6e528bb1d92e5a6fcbfa036f321d7702e3c1706` | `30a1057ca40360e2f91de25afdd6ac079812c89e2bf0c149572798a5844e044b` |
| [replication-waits](../.archify/workflow-ch13-replication-waits-20261011-155725/replication-waits.html) · Workflow v2 | `c22de627747f7e2232c6b48f9c2a37b60ee52a2009dd85e439dc0f0a36b42061` | `6e9a88e40c49c71e3910e8692956677b392206e44f854ef5d50dbb96b0afebfd` |

两图当前根目录收据：**validate/deliver/strict check PASS，showcase9/9、零error/warning、provenance current**。**原生browser-check FAIL，finalize整体FAIL**，原因net::ERR_BLOCKED_BY_ADMINISTRATOR针对file://。使用技能支持的ARCHIFY_CHROME_NO_SANDBOX=1启动已有Chromium，不修改管理策略、不把HTTP验收冒充原生门禁。update.noticeRequired=false/cache-unavailable。复用[MIT许可](ARCHIFY-LICENSE.txt)，生成HTML字体许可保留。

bulk-journey五节点/四lane，按职责展示普通写入成功主线；replication-waits五节点/三lane，强调写前检查与复制发出后并行完成条件，省略故障重试和内部Engine细节。图注、卡片保留适用范围与重要例外；present模式下正文仍可读到这些条件。

## 独立HTTP与视觉审阅

[HTTP报告](review/ch13-http-review.json) / [局部滚动](review/ch13-scroll-review.json) / [懒加载截图修复](review/ch13-capture-review.json)。临时本地HTTP+Playwright+已有Chromium，不发送实验API。报告绑定当前章节、注册表、JSON/HTML字节。

- 两图 ×1440/1600/1920/2048px ×浅深主题：无水平溢出，卡片完整。最低SVG/普通节点上下文投影：旅程6.891/7.875px，等待7.228/8.260px。
- 章节 ×1920/1440/1024/768/390/320px ×双主题：最大880px、左右差≤1px，页面/iframe水平容纳，主SVG全部节点完整；两图高度实测940 /780 /500px（桌面 /601–800 /≤600）。
- 节点探索/固定来源/清除/关闭/展开、暂停后外层重播/Enter、主题同步、目录锚点/已读、六步机制步进/前后/重置/播放/键盘通过。
- 40张实际卡片逐一跳到根控制台核对method/path/body，四非法raw深链、endpoint/auth alias、/es_web/前缀资产/iframes/console通过；未发送真实ES请求。
- reduced motion保持静止，外层重播不能覆盖系统偏好、页面无平滑滚动，机制不自动播放但可手动步进；JS错误/失败HTTP均为空。
- 390/320双主题，源码表和旧SVG舞台仅自身overflow:auto并可实际滚动，整页无水平溢出。窄屏图是完整概览，细字须探索或展开缩放，未宣称手机原比例细字可读；SVG横向内容需局部滚动。

**实际查看24张最终截图**：两图独立4、嵌入4、手机4；章节头桌面/手机4；机制桌面/手机4；手机操作卡2、源码表2。检查文字、箭头、节点、双主题、窄屏阅读列与卡片；截图生成不代替实际查看。手机等待图最初两张截图在懒加载完成前捕获，实际交互已通过；明确等待SVG/字体/主题后重捕获并复核，两张旧空白捕获保留在review/ch13-before-capture-repair且不计入最终24张。长locator捕获保持宽度、扩展高度避开sticky topbar伪影，章节与图源/产物未改。GitHub Pages部署完成未验证。

## 静态检查与复现

node tools/check.mjs：30正式页 /519操作卡 /22机制播放器，全绿；node --check、figwidth、git diff --check、13稳定ID/40唯一槽位及注册次序、.nojekyll检查通过。

```bash
node tools/check.mjs
node --check experiments/ch13.js
node tools/figwidth.mjs chapters/ch13.html experiments/ch13.js
python3 .archify/review/ch13-source-audit.py
python3 .archify/review/ch13-http-review.py
python3 .archify/review/ch13-scroll-review.py
```

浏览器命令需环境允许Chromium子进程和本地HTTP；原生完整命令见finalize收据。本章当前文件/收据/24张截图绑定见[ch13-artifacts.json](review/ch13-artifacts.json)。
