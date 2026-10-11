# 第十四章重构验收

时间：2026-10-11T19:35:45.987540+08:00（Asia/Shanghai）。范围仅 ch14 HTML / 注册表、两幅图及本章证据、STATUS。共享 CSS/JS 与其他章节未改。已读 AGENTS→STATUS→PLAN→CHAPTER_STANDARD→CLAUDE；不重读 tutorial、不启用代理。提交与推送遵循持续授权。

## 内容与固定源码

Elasticsearch9.4.0 / Lucene10.4.0；固定源码 https://github.com/elastic/elasticsearch.git，提交 `2e8528e92361c3399724226deaf2b46f933e925b`，clean checkout `/workspace/scratch/es-v9.4.0`。只读相关目标文件与少量固定git对象。审计通过 **10文件 /39精确区间**，校对Committed bytes、工作区字节及区间边界；未落工作区的固定对象记录localCheckoutPresent=false。[审计](review/ch14-source-review.json) / [脚本](review/ch14-source-audit.py)。

章节约4238中文字符，lesson约2699；七段结构、880px阅读列、3个跳转、折叠目录、5个源码入口、5题/5陷阱、速记/上下课/已读保留。正文、图、机制、卡片与STATUS共同修正：

- 本课限定普通InternalEngine，不声称唯一可写实现或recovery后才创建；协调是角色，动画明确1主0副、去掉错误路由算式。
- 显式ID计划/版本检查后执行Lucene，再非重放来源追加日志，按计划登记版本；提前冲突无序号和已分配序号文档失败的NoOp分开，严重故障不泛化。写后同步不在index()内。
- translog.add不是fsync，request且有位置时等待同步；async仍可realtimeGET。5s为后台周期，不承诺损失上限、性能或零额外耗时。
- refresh可落NRT文件，不建立commit或因可见而裁日志；自动落段不等于SEARCH可见。INTERNAL/EXTERNAL分开，版本图不是整文档缓存，跟踪按需开启也不保证每次读日志。
- 普通flush滚代/commit/INTERNALrefresh/条件裁剪，不负责发布外部reader。safe commit与引用锁影响保留；uncommitted按所需generation汇总，非逐条待重放或未fsync数量，重复flush不承诺固定次数归零。
- 普通周期刷新检查>0，0不能说成每写触发；-1不关后台flush。10MB为磁盘保护阈值下限，不是显式flush设置的统一下限。
- 每批refresh无固定段数；无deleted_in_bytes字段；soft deletes retention保留恢复所需历史，merge不保证deleted_docs=0。force merge同步返回_shards，flush=true组合还有外部refresh。

## 46卡与真实API

原29稳定ID全部保留，新增17；**4组 /46卡：A10、B11、C13、D11、清理1**。保留 ch14-write-path、8个完整机制快照，2条Archify有限trace另计。注册/槽位顺序唯一一致；GET/HEAD无body；bulk字符串保留合法末尾换行，所有46真实卡片均跳转核对method/path/body而不发送。

资源仅tut-l14-nrt/tlog/flush/seg（均完整前缀tut-l14-）；显式standard、stored source、strict非嵌套mapping、1主0副、无default/final管道、refresh=-1、durability=request、sync5s、年龄flush1h、体积10gb、auto_expand=false、非分区routing、active1。无匹配模板/外部写入/外部refresh/配置修改前提。限定green等待，不承诺整个集群green。A用keyword/term对照realtime/非实时GET/SEARCH与外部refresh；B打底、async写与GET、恢复request读设置；C先refresh后flush，再第二篇直接flush的SEARCH0→外部refresh→1；D记录实际段状态、更新、write block停止写入、等待force merge、GET读回。重复create/setup、index/update/noop与旧视图差别明示；点名DELETE四索引，ignore_unavailable允许重复，再A0→D11完整重做。

**真实ES首次与清理后重做均NOT RUN**。当前9200 connection refused，/proc/self/coredump_filter不存在；环境启动记录 `/workspace/scratch/es_web-onboarding/start.md` 说明固定ES9.4.0在bootstrap无条件写该proc接口而失败，失败容器已移除。未循环启动Docker、降级、修改ES、伪造proc或API响应；不宣称复制、故障恢复、fsync耗时实测。页面显式写出未运行与原因。

## 官方Archify与原生门禁

使用[官方Archify3.0.1](https://github.com/tt-a1i/archify/tree/v3.0.1/archify)，本地技能 `/workspace/shared/skills/archify-3.0.1/archify/SKILL.md`；已读defaults/repository、Workflow/common schema、精确Workflow example、layout、viewer及failed-finalize/viewport契约。首次完整JSON就带真实固定源码/--repo-root；HTML完全由CLI生成，没有手改。

| 图解 | candidate SHA-256 | HTML SHA-256 |
|---|---|---|
| [index-order](workflow-ch14-index-order-20261011-192524/index-order.html) · Workflow v2 | `bc1cecae39f2947d504e9f16e385a59e3d469ca5f28c46efd244f34ff3e01976` | `cdd28c54029d432ad96cd2753c3c872c5418376db7d72a91669346cb72614974` |
| [flush-order](workflow-ch14-flush-order-20261011-192524/flush-order.html) · Workflow v2 | `bf136797d85cf6db4362f04455c517fbda23b22ab09f2c85d7ac58e4846e0ae1` | `ba1680a31475ae80474f4b12631642f8f4a7892c7f0bd3e36f26762f4a80d282` |

两图根目录收据：**validate/deliver/strict check PASS、showcase9/9、零errors/warnings、provenance current**；**browser-check FAIL /finalize整体FAIL**，原因为 `net::ERR_BLOCKED_BY_ADMINISTRATOR` 针对file://。采用技能支持的ARCHIFY_CHROME_NO_SANDBOX=1启动已有Chromium，不改管理策略、不把HTTP检查当原生通过。update.noticeRequired=false/cache-unavailable。复用[MIT许可](ARCHIFY-LICENSE.txt)，HTML保留字体许可。

index-order：5节点/4lane，普通显式ID成功路径，写后同步单独职责；flush-order：4节点/3lane，普通成功提交与有条件日志回收。图注与正文保留影响结论的条件，present隐藏卡片也能读到边界。有限trace结束后图仍完整；原八步快照是示例轨迹，不把refresh/flush/merge编成固定必经顺序。

## 独立HTTP与实际视觉审阅

[HTTP](review/ch14-http-review.json) / [局部滚动](review/ch14-scroll-review.json)，均PASS，绑定当前页面/注册表/图源/HTML。临时本地HTTP、Playwright与已有Chromium，不发送真实ES操作。

- 独立两图×1440/1600/1920/2048×浅深主题：无水平溢出，说明卡无截断；最小SVG/普通节点投影：index-order 6.963/7.958px; flush-order 8.358/9.552px。
- 章节×1920/1440/1024/768/390/320×双主题：阅读列≤880px，左右边界差≤1px；页面/iframe无横向溢出，主SVG所有节点完整。写入图高度940/780/500，flush图840/740/500px（桌面/601–800/≤600）。
- 探索与固定源码、清除/关闭/展开、主题同步、暂停→外层重播/Enter、目录/已读、八步机制前后/重置/播放/键盘通过；46卡逐一根控制台请求核对、endpoint/auth alias/raw传递、/es_web/前缀通过；JS errors/failed HTTP均空。
- reduced motion保持静止，外层重播不覆盖系统偏好，机制不自动播放但可手动步进；页面无平滑滚动。390/320源码表与旧SVG仅在自身overflow:auto并实际可滚动，整页不溢出。
- **24张最终截图已由主代理实际逐张查看**：两图独立4/嵌入4/手机4、章节头桌面/手机4、机制桌面/手机4、手机操作卡2、源码表2。捕获前等待lazy iframe的SVG/字体/主题；没有空白截图。手机Archify为完整概览，细字需探索或展开缩放；旧机制SVG局部滑动，标题窄屏省略但解说可读，不声称所有细字手机原比例清晰。

GitHub Pages部署完成未核验；提交推送结果在交付中单独核对。本文与当前文件哈希数量以manifest实际值为准（不绑定自身manifest，避免递归）。

## 检查与复现

node tools/check.mjs：30正式章节 /536卡 /22机制播放器；node --check、figwidth、git diff --check、29stable IDs/46槽位顺序、.nojekyll与本轮范围检查通过。

```bash
node tools/check.mjs
node --check experiments/ch14.js
node tools/figwidth.mjs chapters/ch14.html experiments/ch14.js
python3 .archify/review/ch14-source-audit.py
python3 .archify/review/ch14-http-review.py
python3 .archify/review/ch14-scroll-review.py
```

浏览器命令需此环境的Chromium子进程与本地HTTP权限；完整finalize命令见每图收据。源码当前字节、产物、检查记录与24截图绑定见[ch14-artifacts](review/ch14-artifacts.json)。
