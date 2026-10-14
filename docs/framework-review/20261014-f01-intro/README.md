# F01 导学与旧编排清理：本轮验收

对应 [F01 正文](../../../framework/f01.html) 与 [框架目录](../../../framework/index.html)，2026-10-14。内容以游客搜索“西湖”的固定情境、ES 职责、数据库分工、课程路线和学习方式为主；人工设计结果与将来的展示壳均注明示意。F01 写作与本轮验收脚本审阅使用实际设置的 xhigh 子代理。

## 分别记录的验证

- 内容依据：官方 [文档与索引](https://www.elastic.co/docs/manage-data/data-store)、[全文检索与过滤](https://www.elastic.co/docs/reference/query-languages/query-dsl/full-text-filter-tutorial)、[近实时搜索](https://www.elastic.co/docs/manage-data/data-store/near-real-time-search)。数据库事实/Java 搜索服务/ES 搜索视图是本课程的架构选择。
- 图源生成：[D2 图源、命令与产物](../../../framework/diagrams/f01/README.md)；官方 v0.9.0、TALA、主题 4/201、格式/语法/双产物生成通过。两幅静态概念图，未使用 Archify 或动画。
- HTTP 阅读：[review.py](review.py) 与 [http-review.json](http-review.json)最终通过；Chromium 经 `/es_web/` 前缀访问，1920/1440/1024/768/390/320px × 双主题。新课/目录/旧页各 12 组有限回归，阅读列 880/724/362/292px、各区边界对齐，无整页横溢；表格/图/代码只在自身容器滚动。每组 15 个锚点避开固定顶栏，图解同步/展开、真实 JSON 剪贴板、五题折叠、八阶段大纲、导航、新旧进度隔离/标记/取消/持久化、file 双主题与 reduced motion 通过。无 JS 错误或 HTTP 失败，框架没有 Java/ES 请求；源码首页既有探测另列并阻断，不把它当成本课实验。
- 执行验收：导学不适用，未启动 ES、Java、数据库、Kafka、插件或多节点；未交付本机网站展示壳。旧实验的两轮真实结果保留在 [原记录](../../../projects/travel-search/review/f01/README.md)，不算新 F03 通过。

## 内容与视觉审阅

独立 xhigh 内容审阅通过：情境、四种搜索能力、数据库职责、单位、示意边界与后续课次一致，45 个标题逐一对应规划。写作审阅时明确分开 DB→ES 的同步延迟与 ES 内部搜索可见性，避免把整条同步链路统称近实时。

共生成 18 张 PNG。根代理实际查看最终 11 张：桌面浅色开头、深色业务对照、浅色完整大纲；手机浅色开头/业务对照/理解题、深色嵌入职责图；两幅独立图各浅深主题。具体文件与哈希见 HTTP 记录；其余七张只生成，不声称已独立查看。桌面与手机文字可读，窄屏表格/图的裁切限于可滚动容器，展开入口清楚；两图标签/箭头无重叠。独立 SVG 截图的空白边缘属于 SVG 浏览器视口，正文嵌入按自身比例显示。

首次 HTTP 检查发现图跳转没有滚动偏移，图框被固定顶栏遮挡；已在课程 CSS 补桌面 90px/手机 110px，并最终完整重跑。作者脚本的 SVG 文档整页截图曾超时，改为首个 SVG 元素截图；业务/大纲截图起点也调整到实际对照表与阶段清单。最终成功记录来自修复后的完整脚本，这些早期失败不计通过。

## 历史资产处理

旧首课正文存档至 [f01-startup-legacy.html](../../../framework/f01-startup-legacy.html)，技术正文与来源提交 `af670eb` 相同，只更新历史提示；原项目路径、案例 ID、图源、生成及 ES/HTTP 原始 JSON/截图未覆写。原 HTTP 脚本是源提交的验收脚本，重跑需独立 checkout 该提交。

六段旧规划/旧首课摘要从 STATUS 集中归档至 [FRAMEWORK_HISTORY.md](../../../FRAMEWORK_HISTORY.md)。废弃完整门户的图源、两份 SVG、六张 PNG、夹具脚本和验收 JSON 从当前目录删除，Git 历史仍可查阅；字体许可保留。原工作区未提交的 .gitignore、门户草稿及 health-path 图未改动、不纳入本轮提交。

## 作者复现

使用装有 Playwright / Chromium 的 Python，从仓库根目录运行：

```bash
python docs/framework-review/20261014-f01-intro/review.py
node tools/check.mjs
```

脚本自建临时 HTTP 服务并关闭，不运行实验后端。截图生成不等于视觉审阅；重跑会覆盖本轮检查产物并把视觉状态重设为待审阅，需要重新检查图片后记录范围。
