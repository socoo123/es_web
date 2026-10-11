# 第十章重构验收

审阅时间：2026-10-11T12:56:54.421741+08:00（Asia/Shanghai）。本轮仅修改 ch10、实验注册表、STATUS 与本章图解 / 验收文件。共享 CSS / JS、其他章节与 ES 源码未改。

## 内容与实验

- 锚定 ES 9.4.0 / Lucene 10.4.0；官方源码提交 `2e8528e92361c3399724226deaf2b46f933e925b`。干净 checkout 核对 19 个文件、49 个区间，所有文件字节匹配提交、行号有效。详见 [源码审阅](review/ch10-source-review.json)。
- 七段式、880px 阅读列、目录 / 三个跳转、五行源码入口、五道折叠思考题、五条陷阱、课间导航与已读保留。
- 原 19 个实验 ID 全部保留，新增版本、两个索引健康等待、更新 / 实时新值 / 非实时旧值与无效 preference 共 7 卡：2 组 / 26 卡。显式普通索引 / stored source / mapping / -1 refresh / 0 副本；第一次与重复写入、创建已存在、点名清理与恢复顺序单列。
- 原 `ch10-realtime-get` 保留，由 7 步修正为 9 步，条件化解释 INTERNAL / translog、EXTERNAL 发布及新旧版本。每步完整 SVG，marker ID 唯一；没有模拟 ES 返回。
- 修正：首次 GET 固定走 translog、GET 不用 Lucene / 绝不刷新、每次 translog 重建完整索引且必较慢、GET 全索引刷新、_primary / _replica 偏好、缺省 GET 套用 SEARCH 的 ARS、自定义 preference 永远同副本、routing 不同必 404 / 不保存、忽略索引创建版本 / stale 重路由、REST GET 暴露 if_seq_no、分池不受共享资源影响及“最多一秒旧”等。详见 STATUS 勘误。
- 固定键 `3` / `user123` 在本组新建普通 5 分片索引上的源码离线计算为 4 / 2；明确是计算，不是 API 实测，实验仍要求比较实际 `_search_shards`。

## 图源、产物与原生门禁

官方 [Archify 3.0.1 技能](/workspace/shared/skills/archify-3.0.1/archify/SKILL.md)，两幅 Workflow v2、有限 trace、中文图例与固定 ES 仓库证据。只改 JSON，再正式 CLI 生成；HTML 未手改。

| 图 | 当前 JSON SHA-256 | 当前 HTML SHA-256 | 当前收据 |
|---|---|---|---|
| get-journey | `df5ff94c5f9f281b1b8ad53432bff7de65b780bdc9974df1d0e14175e08d5f04` | `2799b0891c2c7c7048fcf9149cddf60a5fa76cf77dddd55602d44bb2fc0793e5` | review-2 |
| realtime-read | `690ab884a271c7951a0202b87b7aad0f735280be5290cef60cfdcc169db4b425` | `dd391375078cc6ab1e7bfdcb81447280a3e04e0b5bb85e4cb1c4bce7c494783c` | review-7 |

两图 validate / deliver / strict check 均 showcase **9/9、0 errors / 0 warnings、provenance current**。原生 browser-check 均 **fail：ERR_BLOCKED_BY_ADMINISTRATOR**（file URL 策略），finalize 整体 **fail**，没有把 HTTP 检查替代原生结果。

get-journey 首次原生启动遇 SUID / crashpad 阻塞；使用技能支持的 `ARCHIFY_CHROME_NO_SANDBOX=1` 后明确落在既有 file URL 策略限制。realtime-read 首版共用通道失败，修复端口 / 路由后通过；HTTP 窄屏发现右侧节点裁切。单设容量相同 viewBox 没改变 HTML，随后按语义堆叠 VersionMap / INTERNAL，修复外侧分支端口；最终所有节点完整。旧候选与各轮收据保留，旧收据 / `review/ch10-before-viewport-repair/` 截图属于历史产物，不作为当前通过证据。没有改浏览器管理策略。

当前收据与全部当前文件绑定见 [artifact manifest](review/ch10-artifacts.json)。复用 [Archify MIT 许可](ARCHIFY-LICENSE.txt)，保留生成 HTML 内字体许可。update.noticeRequired=false，无更新声明。

## 独立 HTTP 与交互

[HTTP 检查脚本](review/ch10-http-review.py) / [报告](review/ch10-http-review.json)：**pass**。独立图各 1440×900、1600×1000、1920×1080、2048×1320，浅深主题；章节 1920 / 1440 / 1024 / 768 / 390 / 320px，浅深主题。阅读列 ≤880px、区域边界差 ≤1px，页面 / iframe 无横向溢出，主 SVG 实际节点全部在画布内，无裁切；说明卡未截断。

- 两图探索 / 固定提交来源 / 关闭 / 展开、主题同步、暂停后外层重播、Enter；目录与已读；26 张真实控制台导航逐一核对 method / path / body（相同路径的不同版本写入也分别核对）；端点 / 认证别名 / raw 与 Pages `/es_web/` 路径通过。
- 九步机制播放器逐一核对计数、SVG 文字范围、唯一 ID；前进 / 后退 / 重置 / 播放暂停 / 键盘步进通过。系统 reduced motion 下 Archify 强制静止、重播不越权，机制动画不自动播，手动步进保留，页面无平滑滚动。
- 原 SVG 舞台与源码表在窄屏用自身滚动容器。[局部滚动检查](review/ch10-scroll-review.json) 对 390 / 320px、两主题实际滚至右端，验证 Engine 节点可见、整页仍无溢出。手机图为完整概览，细小标签需放大 / 探索 / 展开；没有宣称手机总览文字均可直接阅读。
- 最小独立 SVG 文本 / 普通节点文本：get-journey 6.37px / 7.28px；realtime-read 8.08px / 9.24px。
- iframe 高度按实测：桌面 940 / 820px，601–800px 780 / 700px，≤600px 500 / 450px；共享文件未修改。JS 未处理错误与失败 HTTP 均为空，资产、章节锚点、控制台路径及 `.nojekyll` 已检查。
- 视觉审阅：实际通过图像工具查看 **24 / 24 张最终截图**：两图独立 / 嵌入 / 390px 图框，各浅深；章节桌面 / 手机首屏；机制播放器桌面 / 手机；手机实验 A14 与源码表，各浅深。已检查标题、条件标签、箭头、卡片、正文、控制按钮与图注。历史截图不计入审阅。
- 浏览器检查只验证页面和请求传递，不发送实验请求，不模拟 API。harness 的 `getBBox().toJSON` 不兼容已改为显式取坐标；仅复用当前哈希绑定且完整通过的布局记录补完交互，最终默认脚本可完整重现。

## 真实 ES 与站点检查

真实 API **首次 / 清理后重做均未执行**：本轮 127.0.0.1:9200 连接拒绝，运行时仍缺 `/proc/self/coredump_filter`；既有 onboarding 启动记录确认 ES 9.4.0 在此 bootstrap 失败。没有降版本、补丁 ES、反复尝试未变条件或伪造响应。页面与卡片如实标为源码预期。

`node tools/check.mjs`：30 正式页 / 448 卡 / 22 个机制播放器，通过。`node --check experiments/ch10.js`、本章 figwidth、stable ID 与 `git diff --check` 通过；最终 STATUS 后再跑结构检查。Archify trace 与机制播放器分开统计。

## 重现

在仓库根执行（环境需已有 Python / Playwright / Chromium）：

```bash
ARCHIFY_CHROME_NO_SANDBOX=1 node /workspace/shared/skills/archify-3.0.1/archify/bin/archify.mjs finalize workflow .archify/workflow-ch10-get-journey-20261011-123611/candidate.json .archify/workflow-ch10-get-journey-20261011-123611/get-journey.html --repo-root /workspace/scratch/es-v9.4.0 --quality showcase --out-dir .archify/workflow-ch10-get-journey-20261011-123611/review-next --json
ARCHIFY_CHROME_NO_SANDBOX=1 node /workspace/shared/skills/archify-3.0.1/archify/bin/archify.mjs finalize workflow .archify/workflow-ch10-realtime-read-20261011-123611/candidate.json .archify/workflow-ch10-realtime-read-20261011-123611/realtime-read.html --repo-root /workspace/scratch/es-v9.4.0 --quality showcase --out-dir .archify/workflow-ch10-realtime-read-20261011-123611/review-next --json
python3 .archify/review/ch10-http-review.py
python3 .archify/review/ch10-scroll-review.py
node tools/check.mjs
node --check experiments/ch10.js
node tools/figwidth.mjs chapters/ch10.html experiments/ch10.js
```

原生 file URL 门禁预期仍受本环境策略阻塞；在兼容环境重新执行后才能另行更新原生浏览器结论。真实实验需可运行的 9.4.0 节点，按页面完整顺序首次与清理后重做。本轮按用户持续授权提交并推送 origin/main。
