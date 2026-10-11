# 第十五章重构验收

时间：2026-10-11T22:39:17.441851+08:00（Asia/Shanghai）。仅修改 ch15、两幅本章图与验收记录、STATUS；共享 CSS/JS 和其他章节未修改。已读 AGENTS→STATUS→PLAN→CHAPTER_STANDARD→CLAUDE，不重读 tutorial、不启用代理。提交与推送遵循持续授权。

## 内容与固定源码

ES **9.4.0 / Lucene10.4.0**；真实节点 build_hash 与固定提交 `2e8528e92361c3399724226deaf2b46f933e925b` 一致。干净稀疏 checkout `/tmp/es-ch15/es-v9.4.0`，只获取相关文件；[源码审计](review/ch15-source-review.json)核对 **24 文件 /45 精确区间**，提交对象、工作区字节和行边界一致。

约 4090 中文字符；七段结构、880px阅读列、折叠目录、3个图/机制跳转、5题/4陷阱、上下课/已读/控制台保留。勘误同步正文、图源、七步机制、卡片、问答与速记：

- 实际路由入口是 IndexRouting，限定新建普通非分区、无 routing_path / resharding；创建版本判别新取模与旧 routingNumShards/routingFactor，不以节点版本替代。
- ES hash(String)使用 **UTF-16LE / Murmur3 x86_32 seed0**。brown=998382972→片0，brown-1=-2007555306→片0，route-0=512605379→片2；旧UTF-8数字/片1及“不带routing必404”错误。离线实现通过官方7个向量，真实两轮 API对照0/0/2。
- 普通无routing搜索查全部片；routing只缩范围，不校验键身份、不替代租户过滤；required不禁止无routing搜索。GET缺省使用ID，可同片命中，跨片才构成本例404。
- GET未传ARS排名输入；普通搜索有统计时可排名，不保证最快或reader瞬时一致。单节点只验证primary可用和未分配副本，不验证远程复制。
- 主片Final更新拒绝，原设置/路由与文档不变；开放索引实际400的reason为non dynamic setting(s)，不能固定写成下层final检查文案。副本Dynamic，局部健康等待yellow→green→yellow。
- Engine在RECOVERING内打开；peer目标开Engine后再phase2应用历史，非“全部ops先落盘后开”。CAT四态、恢复stage与本地五态分开；读闸门接受POST_RECOVERY/STARTED，恢复写有独立条件，可提前close，不声称永久不能替换Engine。
- **闭合索引普通GET实测400 index_closed_exception / reason=closed**。SingleShardRequest forbids closed，具体索引解析在索引block前拒绝；关闭block的403与本地状态异常404是其他层。close保留，open恢复后读回，DELETE才删资源。

## 40卡与真实API

保留原16稳定ID及ch15-routing-formula七步播放器，新增24，共 **4组/40卡：A17、B8、C7、D6、清理2**。显式standard、3主片、副本数、auto_expand=false、routing_partition_size=1、stored source、strict keyword、无管道、refresh=-1、request耐久、active=1；写入显式refresh=true，按资源等待健康。说明首次/重复、错误恢复、同片/跨片对照，点名DELETE两索引并允许重复清理。

**真实ES两轮各40操作 PASS**：[响应和验证](review/ch15-es-review.json) / [脚本](review/ch15-es-review.py)。单节点匿名9200、版本/构建号核对；每轮由干净本章资源开始并执行完整两张清理。核对0/0/2落点、同片GET200、跨片GET404与正确键恢复、搜索2→0、yellow/green、Final拒绝后设置3且可读、required写/GET400但无routing搜索200、closeGET400、open后数据保留与EXISTING_STORE/DONE。最终HEAD两索引均404。

初期沙箱内9200不可连接、Docker CLI报告daemon未运行；随后**沙箱外HTTP实际可用**，不把CLI状态当API状态。浏览器深链检查发现console自动执行请求，初次未阻断流量的验收被判失败并完成清理；最终HTTP脚本对9200显式abort，不伪造ES响应，真实API独立运行。[初始响应](review/ch15-es-initial-responses.json)保留未修正错误预期时的事实。开放索引Final错误的最后修正只改expect文案；最终校验逐条比较本轮注册的id/method/path/body与两轮实测，requestIdentityVerified=true，保留执行时experimentSha256及当前reviewedExperimentSha256。不额外声称同次重复写updated、多节点复制、内部状态竞态或split/shrink已实测。

## 官方Archify与原生门禁

[官方3.0.1技能](https://github.com/tt-a1i/archify/blob/v3.0.1/archify/SKILL.md)，下载到`/tmp/es-ch15/archify-3.0.1/archify`；已读defaults/repository、两模式schema/common、精确example、viewer/delivery与Workflow布局/viewport修复契约。首次图源即附固定提交和真实checkout，完整finalize使用--repo-root；HTML全部CLI生成，未手改。

| 当前图 | candidate SHA-256 | HTML SHA-256 |
|---|---|---|
| workflow / workflow-ch15-routing-20261011-213048 | `431d218cd7826bbff7988b658c463317bd745ac40f1ca044b948f662fc032334` | `a094f60e510a7d4cc5540417b761dd8431b660cc0b508f56b4ff8bcfb865b782` |
| lifecycle / lifecycle-ch15-shard-life-20261011-213048 | `663271e37aee100735b360bb04a641b3f6e3a12b2907ce616415900f09d583d4` | `3a15be8bfa153282f4d323e173bf2d34ccf28d3ec0e029cf522251db16efeba7` |

**两图 validate /deliver /strict check 均showcase9/9、0 errors/warnings、provenance current；原生 browser-check及finalize整体 PASS。** 路由当前收据review-2，生命周期review-3；update.noticeRequired=false（3.0.1当前）。首次sandbox下Chrome管道失败、错误区间/主路径/画布比例诊断、手机横排裁切的历史记录保留；由JSON修复为纵向三分支及per-lane intrinsic fit。路由的两条绕行支线已经实际查看，必要分支绕过其他节点，无交叉，不表示GET再搜索再写入。生命周期关闭可提前发生。复用[MIT许可](ARCHIFY-LICENSE.txt)，生成HTML保留字体许可。

## 独立HTTP与实际视觉审阅

[HTTP](review/ch15-http-review.json) /[局部滚动](review/ch15-scroll-review.json)均PASS，绑定当前页面/注册表/图源/HTML。使用临时本地HTTP、Playwright与现有Google Chrome；ES流量显式阻断，测试真实控制台请求的method/path/body传递，不发送或伪造响应。

- 独立两图×1440/1600/1920/2048×浅深主题：无水平溢出，说明卡无截断；最小SVG/普通节点投影：routing 6.309/7.210px，shard-life 6.664/7.615px。
- 章节×1920/1440/1024/768/390/320×两主题：阅读列≤880px、各区边界差≤1px；页面/iframe无横向溢出，所有主SVG节点完整。图高度routing800/700/500、life840/740/500（桌面/601–800/≤600），实测容纳。
- 节点探索/固定源码/关闭、独立展开、主题同步、暂停后外层重播/Enter、折叠目录与锚点、已读、七步机制前后/重置/播放与键盘、40条实际控制台导航请求内容、endpoint/auth alias/raw、/es_web/前缀通过；未处理JS错误和失败静态HTTP均空。
- reduced motion优先，重播不覆盖系统偏好，旧播放器不自动播但手动步进可用；页面无平滑滚动。390/320源码表和原SVG仅在自身容器内可实际滚动。
- **24张最终截图已逐张实际查看**：两图独立4、嵌入4、手机4、章节头4、机制4、操作卡2、源码表2；捕获等待lazy iframe、字体和主题，图不空白。手机图为完整概览，细字需节点探索或展开缩放；旧SVG局部滑动，播放器标题窄屏省略、解说可读，不宣称全部细字原比例清晰。

## 检查与复现

[站点检查](review/ch15-site-check.json)：30正式页/560卡/22机制播放器；JS语法、figwidth、git diff--check、16稳定ID/40有序唯一槽位及.nojekyll通过。当前文件和24截图哈希绑定见[ch15-artifacts](review/ch15-artifacts.json)。共享文件未改。

```bash
node tools/check.mjs
node --check experiments/ch15.js
node tools/figwidth.mjs chapters/ch15.html experiments/ch15.js
ES_SOURCE_ROOT=/path/to/clean-es-v9.4.0 python3 .archify/review/ch15-source-audit.py
python3 .archify/review/ch15-es-review.py        # 实际修改/清理本章两索引并执行两轮
python3 .archify/review/ch15-es-review.py --validate-only # 验证已有响应与当前请求相同，HEAD检查清理
python3 .archify/review/ch15-http-review.py      # 需Playwright/Chrome及本地HTTP权限；阻断9200
python3 .archify/review/ch15-scroll-review.py
```

本轮按授权提交并推送origin/main；提交与远端结果在交付时另行核对。GitHub Pages部署完成尚未核验。
