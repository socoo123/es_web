# 第十一章重构验收

审阅时间：2026-10-11T13:45:28.466762+08:00（Asia/Shanghai）。本轮范围为 ch11、实验注册表、STATUS 与本章图源 / 产物 / 验收。共享 CSS / JS、其他章节和 ES 源码未改。

## 内容与实验

- 锚定 ES 9.4.0 / Lucene 10.4.0、官方提交 `2e8528e92361c3399724226deaf2b46f933e925b`。干净 checkout 核对 **16 个文件 / 43 个区间**，字节匹配提交、行号有效；见 [源码记录](review/ch11-source-review.json)。
- 七段式、约 4035 个中文字符；880px 阅读列、目录、三个跳转、五行源码入口、五道折叠思考题、五条陷阱、上下课与已读保留。
- 原 **19 个操作 ID 全保留**，新增 16 卡，共 **5 组 / 35 张操作卡**（含清理）。补版本、限定健康等待、coercion 成功 / source / 失败、text term / keyword match、strict 未创建、false 原值 / exists、runtime 类型 / 查询、合并读回。四个点名索引，显式 standard / stored source、1 主分片 / 0 副本、周期 refresh=-1、coerce=true、ignore_malformed=false、字段限制；搜索写入明确 refresh=true。创建已存在、重复固定 ID、错误后恢复和完整清理重做单列。
- 原 `ch11-dynamic-mapping` ID 保留，7 步改为 **9 步**，完整 SVG 与每步独有 marker。修正 tags 子字段、候选 / 发布 / 重试、数值字符串接受与无效数字失败；窄屏舞台局部滚动提示。
- 校正：第一篇文档永久定全部字段；数值字符串必 400；本地 merge 等同集群发布；旧 checkIncomingMergeType 当作实际合并入口；term / match 类型互斥、查询分析必相同 / keyword 永不规范化；false 丢原值；runtime 不占 mapping、浮点也为 float；vector 必显式；高基数等于字段数、错误的 8 字段计数；新增 mapping 自动补历史值与所有参数可改。正文、图注、解说、实验、问答与速记一致；STATUS 登记。

## 图解与原生门禁

使用官方 [Archify 3.0.1 技能](/workspace/shared/skills/archify-3.0.1/archify/SKILL.md)。两幅 Workflow v2，中文图例、showcase、有限 trace；首次 candidate 即带固定 ES 仓库与节点源码证据，传入真实 `--repo-root`。只改 JSON，正式 CLI 生成；HTML 未手改。

| 图 | 当前 JSON SHA-256 | 当前 HTML SHA-256 | 当前收据 |
|---|---|---|---|
| mapping-update | `7f61675bd35801343169f5fdeb5a5005520a7e4a743aea00e15f9e9581b4a353` | `0d44ac6229ab32cb2615e7ebd0f50cf43f6bf861e7b27322f0f4d3a0703cace3` | 根目录 |
| field-paths | `3722ce14217564326d3252b59edb0e9565619fd55cba83dcc28c6d6b85e4b21d` | `b34a1a408fe3e8accf22e0dccec9fc7f97cdbeed41e023f6ccf5f41f521ec8ad` | review-4 |

两图 validate / deliver / strict check 均 **showcase 9/9、0 errors / 0 warnings、provenance current**。原生 browser-check 均因 file URL 管理策略 **ERR_BLOCKED_BY_ADMINISTRATOR** 而 fail；finalize 整体 **fail**，独立 HTTP 结果单列，没有修改浏览器政策。

field-paths 首版 mainPath 逻辑列倒退，调整主路径声明后通过；HTTP 在 390px 发现顶节点越出画布 4.89px，依据 layout 记录重排为全文 / 完整值两条纵向分支。最后缩短图题避免孤字换行。初稿 / 修复候选与根目录、review-2/3/4 收据保留；[历史布局失败证据](review/ch11-before-viewport-repair/failure.json) 包含旧 HTML / layout / 四张旧独立截图，不作为当前验收。mapping-update 首次即通过内容门禁。

复用 [Archify MIT 许可](ARCHIFY-LICENSE.txt)，生成 HTML 内字体许可完整；两图 update.noticeRequired=false。当前 SHA 绑定见 [artifact manifest](review/ch11-artifacts.json)。

## 独立 HTTP、滚动与视觉审阅

[HTTP 脚本](review/ch11-http-review.py) / [报告](review/ch11-http-review.json)：**pass**。两图各 1440×900 / 1600×1000 / 1920×1080 / 2048×1320，浅深主题；章节 1920 / 1440 / 1024 / 768 / 390 / 320px，浅深主题。阅读列 ≤880px、区域边界差 ≤1px；页面与 iframe 无横向溢出，主 SVG 全部实际节点在画布中，说明卡不截断。

- 探索 / 固定源码 / 关闭、展开窗口、主题同步、暂停后外层重播及 Enter、目录 / 已读，**35 张卡实际导航到控制台逐一核对 method / path / body**；端点 / 认证别名 / raw、Pages `/es_web/` 前缀、相对资产、锚点和唯一章节 ID 通过。无未处理 JS 错误、无失败 HTTP。
- 九步机制动画计数、SVG 文本范围、唯一 ID、前后 / 重置 / 播放暂停 / 键盘步进通过。reduced motion 下 Archify 静止、重播不越权，机制播放器不自动播但可步进，页面不平滑滚动。
- [局部滚动](review/ch11-scroll-review.json)：390 / 320px 双主题，SVG 舞台与源码表确实只在自身容器横向滚动；滚至右端可见右侧头部标签，页面不溢出。完整宽 SVG 可按位置查看，不承诺整张宽卡同时容纳手机。初版 harness 要求宽字段框整块容纳窄舞台，改为验证局部滚动与目标标签可见，未改页面消除真实约束。
- 独立最小 SVG 文本 / 普通节点文本：mapping-update **6.37 / 7.28px**；field-paths **7 / 8px**。手机为完整总览，细小文字需探索 / 放大 / 展开；关键解释在正文与图注。
- 图框测量高度：桌面 **940 / 820px**、601–800px **780 / 700px**、≤600px **500 / 450px**，共享文件未改。
- 已实际通过图像工具审阅 **24 / 24 张最终截图**：两图独立、嵌入、390px 图框各双主题；章节桌面 / 手机首屏；九步机制桌面 / 手机；手机 coercion GET 卡和源码表。核对布局、箭头、文字、主题、卡片、控制和图注；旧截图不计。浏览器测试只验证页面与请求传递，不发送 / 模拟 ES 实验响应。

## 真实 ES 与站点检查

真实 API **首次 / 清理后完整重做均未运行**：本轮 127.0.0.1:9200 连接拒绝，仍缺 `/proc/self/coredump_filter`；既有 [启动记录](/workspace/scratch/es_web-onboarding/start.md) 记录 ES 9.4.0 bootstrap 阻塞。未反复起 Docker、降版本、补丁 ES、伪造运行环境或响应；页面 / 卡片明确“源码预期、API 未实测”。

站点 `node tools/check.mjs`：**30 正式页 / 464 卡 / 22 个机制播放器**。本章 JS 语法、figwidth、stable ID、diff 检查通过；`.nojekyll` 保留。Archify 2 条 trace 单独计数。按用户持续授权提交并推送 `origin/main`，不把代码推送等同于已验证 Pages 部署。

## 重现

在仓库根目录运行；浏览器需已有 Python / Playwright / Chromium：

```bash
ARCHIFY_CHROME_NO_SANDBOX=1 node /workspace/shared/skills/archify-3.0.1/archify/bin/archify.mjs finalize workflow .archify/workflow-ch11-mapping-update-20261011-133120/candidate.json .archify/workflow-ch11-mapping-update-20261011-133120/mapping-update.html --repo-root /workspace/scratch/es-v9.4.0 --quality showcase --out-dir .archify/workflow-ch11-mapping-update-20261011-133120/review-next --json
ARCHIFY_CHROME_NO_SANDBOX=1 node /workspace/shared/skills/archify-3.0.1/archify/bin/archify.mjs finalize workflow .archify/workflow-ch11-field-paths-20261011-133120/candidate.json .archify/workflow-ch11-field-paths-20261011-133120/field-paths.html --repo-root /workspace/scratch/es-v9.4.0 --quality showcase --out-dir .archify/workflow-ch11-field-paths-20261011-133120/review-next --json
python3 .archify/review/ch11-http-review.py
python3 .archify/review/ch11-scroll-review.py
node tools/check.mjs
node --check experiments/ch11.js
node tools/figwidth.mjs chapters/ch11.html experiments/ch11.js
```

兼容环境重新运行原生 browser-check 后才可更新原生结果；真实 ES 节点可用时，按页面四索引完整顺序执行首次与清理后重做。当前环境限制不妨碍交付已验证的阅读样稿。
