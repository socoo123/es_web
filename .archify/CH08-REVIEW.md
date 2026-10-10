# 第八章交付与验证记录

按 CHAPTER_STANDARD 重构第八章，保留七段式、目录、课间导航、已读进度与控制台入口。两幅 Workflow v2 各使用有限 trace，原 ch08-reject 六步机制播放器保留；两类动画分别计数。原 10 个实验 ID 全部保留，新增 5 卡，共 2 组 / 15 张操作卡（含清理）。本轮只改 ch08 正文、注册表及本章图源 / 证据与 STATUS，共用 CSS / JS 未改。

内容锚定自管 Elasticsearch 9.4.0 / Lucene 10.4.0；ES 源码提交 2e8528e92361c3399724226deaf2b46f933e925b。所有关键节点有目标文件和行号，首次 finalize 就传入真实干净 checkout 的 --repo-root；23 个引用或补充核对的文件与提交字节比对一致，见 [源码复核](review/ch08-source-review.json)。勘误覆盖同步完成、responseExecutor、消费后倒数、完成活性、共享资源、默认参数条件、刷新与统计归因及拒绝 / HTTP 边界。

## 分项验收

| 项目 | 实际结果 |
| --- | --- |
| 站点 / 语法 / 旧 SVG | node tools/check.mjs、node --check experiments/ch08.js、node tools/figwidth.mjs chapters/ch08.html experiments/ch08.js、git diff --check 通过；30 页 / 436 卡 / 22 机制播放器 |
| 原生 validate / deliver / strict check | 两图 showcase 9/9、零错误 / 警告，provenance current；当前 async-search review-4、listener-map review-9 |
| 原生 browser-check / finalize | **失败**，管理员策略禁止 Chrome 的 file URL 快照，ERR_BLOCKED_BY_ADMINISTRATOR；未修改策略，未把整体 finalize 记为通过 |
| 独立 HTTP Chromium | 两图各 1440 / 1600 / 1920 / 2048px 双主题；章节 1920 / 1440 / 1024 / 768 / 390 / 320px 双主题，最大 880px 列、各区边界差 ≤1px、页面 / iframe 无溢出 |
| 图的窄屏可见性 | 在每个 iframe 可见时检查实际主 SVG 的所有节点均位于图面边界内；窄屏保留概览、正文条件、节点探索与展开，未将缩小文字声称为全部细节可读 |
| 交互 | 探索 / 固定源码链接 / 关闭 / 展开、主题同步、暂停后外层重播 / 键盘重播、目录 / 已读、15 张实际控制台导航的 method / path / body、endpoint / auth alias / raw、Pages 子路径通过 |
| 机制播放器与 reduced motion | 六步、前后步进、重置、实际渲染与手机容器内滚动检查通过；reduce 禁自动播放、图 trace 与平滑滚动，手动步进可用 |
| 真实 ES API | **首次与清理后重做未执行**。9200 连接拒绝，云运行时缺 /proc/self/coredump_filter，已有 ES 9.4.0 启动记录确认阻塞；未重复启动、修改 ES 或模拟响应 |

实验卡的响应均是源码预期，HTTP 检查只验证站点与请求传递。配置观察不代替运行时压测，单节点实验不证明远程网络路径。读回只比较本课键；统计按同一节点取前后基线，删除索引不会重置累计值。

## 视觉与修复范围

实际查看 24 张最终截图，包括两图独立页 / 章节嵌入 / 手机的双主题、桌面与手机首屏、失败更新卡、源码表和机制播放器。最终产物与截图绑定见 [当前哈希清单](review/ch08-artifacts.json)，浏览器数值与功能结果见 [HTTP 记录](review/ch08-http-review.json)，复现脚本见 [ch08-http-review.py](review/ch08-http-review.py)。截图生成与实际查看分别记录。

图源初稿通过前三个门禁；截图中的主路径绕行改为明确端口，六个逻辑列默认占位导致的空白通过调整分支的逻辑列消除。一次显式小 viewBox 尝试被容量校验拒绝，旧收据 / 候选保留，最终恢复自动画布。第二图最初手机默认视图裁切节点，重新按 MappedActionListener.onResponse 的转换、委托与返回组成纵向阶段卡片，保留所有节点、关系、文字和源码证据；最终额外逐图检查节点容纳。未手改生成 HTML。

图框最终测量为桌面 760px、601–800px 680px、≤600px 440px；手机机制快照保持 720px 最小宽度，在自身容器滚动，解说与控制保持可读。只用了章节内小范围 CSS。独立查看器普通节点上下文最小约 8.25px，全部 SVG 文字（含来源徽标）最小约 7.22px。

历史 HTTP 证据在 review/ch08-initial、review/ch08-review-2、review/ch08-review-4、review/ch08-review-7，分别绑定当时文件；早期布局通过不代表手机节点未裁切。当前验收以 ch08-http-review.json 及当前清单为准。最初手机交互测试受滚动位置干扰，脚本在点击前稳定 iframe；最终节点检查只选择主 SVG，避免把隐藏的查找索引元数据误当作画面节点。

## 复现

使用固定提交的干净 ES checkout，包含所有所引 sources；字体许可保留在生成 HTML 中，共用 [ARCHIFY-LICENSE.txt](ARCHIFY-LICENSE.txt)。图源改动后用新 review 目录完整 finalize，不改 HTML；当前云浏览器限制下命令以 browser-check 失败退出。独立 HTTP 记录不能替代原生门禁或真实 API。

```bash
ARCHIFY_CHROME_NO_SANDBOX=1 node /path/to/archify/bin/archify.mjs finalize workflow \
  .archify/workflow-ch08-async-search-20261010-234753/candidate.json \
  .archify/workflow-ch08-async-search-20261010-234753/async-search.html \
  --repo-root /path/to/es-v9.4.0 --quality showcase \
  --out-dir .archify/workflow-ch08-async-search-20261010-234753/review-next --json

ARCHIFY_CHROME_NO_SANDBOX=1 node /path/to/archify/bin/archify.mjs finalize workflow \
  .archify/workflow-ch08-listener-map-20261010-234753/candidate.json \
  .archify/workflow-ch08-listener-map-20261010-234753/listener-map.html \
  --repo-root /path/to/es-v9.4.0 --quality showcase \
  --out-dir .archify/workflow-ch08-listener-map-20261010-234753/review-next --json

python3 .archify/review/ch08-http-review.py
node tools/check.mjs
node --check experiments/ch08.js
node tools/figwidth.mjs chapters/ch08.html experiments/ch08.js
git diff --check
```

## 当前图源与产物

| 文件 | SHA-256 |
| --- | --- |
| [candidate.json](workflow-ch08-async-search-20261010-234753/candidate.json) | `ee373d1faad822a886eaa751101d7b7c8294ec6723570a431c5c260b77f03963` |
| [async-search.html](workflow-ch08-async-search-20261010-234753/async-search.html) | `3453990c1b48889f17e65d6bd976f08bd8723308a66055cd2039504852918cc9` |
| [candidate.json](workflow-ch08-listener-map-20261010-234753/candidate.json) | `7cfb1eae170387c33abf881e8780b25f9024d3484c8e4c11bfec9957743345d6` |
| [listener-map.html](workflow-ch08-listener-map-20261010-234753/listener-map.html) | `3189ab93e07dadd91a21fb2fd5cad3035c308bafef9318e0e16146fd6233d4f9` |

本轮依用户持续授权提交并推送 origin/main；交付消息提供 GitHub 提交链接与章节阅读链接。记录时间 2026-10-11T00:23:05.827568+08:00（Asia/Shanghai）。
