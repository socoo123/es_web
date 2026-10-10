# 第四章交付与验证记录

第四章按 CHAPTER_STANDARD 重写，复用 880px 阅读列与共用主题/重播脚本。两图由官方 Archify 3.0.1 从 JSON 生成，未手改生成 HTML：Architecture 展示 Classic 默认隔离与显式扩展（静态）；Workflow v2 展示正常 Reindex 启动注册路径及检查失败分支（有限 trace）。保留两张实验卡的稳定 ID，本章没有原 ESFLOWS 播放器。

## 内容与依据

源码仓库 https://github.com/elastic/elasticsearch.git，固定 v9.4.0 提交 `2e8528e92361c3399724226deaf2b46f933e925b`。每个关键节点带实际检查的文件/行号；首次 finalize 已传入真实干净 ES checkout 的 --repo-root。章节 33 个固定 tag 源码链接的目标路径和行号范围也已检查。

- 区分源码区域、发行目录、Classic / Stable API 与许可；X-Pack 不是第三种加载协议，也不全是付费功能。不把删除内置模块后仍可启动当作保证。
- Bootstrap 建立加载层，Node 构造 PluginsService 与 Classic 实例，之后按接口装配。模块化、Classic 非模块化和 Stable 有不同加载分支。
- 默认无关插件不互见私有实现；显式扩展使用被扩展插件的暴露层，有单独 SPI 时用 SPI，无 SPI 时可用实现层。父路径包含核心，被扩展实例须实现 ExtensiblePlugin；JarHell、模块可见性及其他运行约束仍适用。
- ActionModule 接收 ActionPlugin 实例，分别收集 Action 与 REST 扩展；ReindexPlugin 提供 RestReindexAction，后者声明 POST /_reindex。图示正常允许的启动注册路径，不代表 HTTP 请求执行链；扩展过滤占位及其他构造异常在正文说明。
- createComponents 可返回对象、待注入类和 PluginComponentBinding；实际生命周期组件由 Node 收集。MapperSizePlugin 注册解析能力；显式 mapping enabled 后记录源字节大小，不能解释为磁盘压缩占用。
- 正常语义版本构建中，Classic 要求描述 ES 版本等于当前版本；Stable 要求同 major 且构建目标不晚于运行版本。Stable 命名组件扫描与 Classic 反射入口分开解释。
- GET 清单按各节点安装状态判断；空对象 POST 预期参数验证失败，应核对错误类型与 reason，无 handler 也会返回 400。正文、图注、卡片、答案与速记保持一致；旧说法及依据见 STATUS 勘误表。

## 分项验收

- 站点结构与 JS：node tools/check.mjs 全绿（30 章、414 实验、22 个原机制动画）；experiments/ch04.js 通过 node --check；git diff --check 通过。
- Archify 原生 validate / deliver / strict check：两图 showcase 9/9、零错误/警告，源码核验通过，provenance current。
- 原生 browser-check：管理员策略禁止 file://，仍报 ERR_BLOCKED_BY_ADMINISTRATOR；finalize 整体保留 fail。未改变或绕过浏览器管理策略。
- 独立 HTTP Chromium：通过。两图各 1440 / 1600 / 1920 / 2048px 与浅深主题；章节 1920 / 1440 / 1024 / 768 / 390 / 320px 与浅深主题，最大阅读列 880px、左右边界差 ≤1px、页面/iframe 无横向溢出，初始 SVG 在框内未横向裁切。节点探索/关闭、固定提交源码链接、展开、主题同步、路径图暂停后重播与键盘、目录/进度、实验深链、实际请求方法/路径/空对象填充及 Pages 前缀通过；静态图无可见播放入口，系统减少动态效果优先，无未处理 JS 错误或 HTTP 资源失败。记录绑定当前 JSON、HTML、章节及实验 JS 哈希，见 [ch04-http-review.json](review/ch04-http-review.json)。
- 真实 ES API：当前 127.0.0.1:9200 连接拒绝，GET 清单与空对象 POST 及重复运行未实测。源码核对及控制台请求填充不能代替真实响应验收。
- Pages：沿用推送 main 的既有部署方式；部署完成未在本环境核验，交付阅读链接供刷新查看。

## 视觉与改图记录

实际查看两图独立浅/深主题、章节嵌入浅/深样本、390px 两图及章节首屏。流程图初版共享路由段，经相连节点/端口调整修复；之后根据截图把主要路径改为两列，图框高度由首次预设调整为测量后的 840px（窄屏 680px）。隔离图为 820px（窄屏 640px）。查看器仍保留完整逻辑列的空间，未通过裁切隐藏图内容，也未手改生成器样式。手机图用于完整概览，细节通过缩放、节点探索及正文阅读；不声称手机概览字号等于正文。必要条件在正文与图注重复解释，不依赖 present 隐藏的说明卡。另在适合完整图注截取的 1440 / 390px 宽、1400px 高视口查看图注截图，并通过查看器按钮检查窄屏放大；此补充捕获高度不同于布局验收的手机高度，不代替前述六宽测试。记录见 [ch04-caption-zoom-review.json](review/ch04-caption-zoom-review.json)，代表截图在 review/ch04-*.png。

保留初次校验失败与旧布局收据，它们的旧哈希不代表当前交付；Workflow 最新门禁在 review-3。共用 CSS/JS 没有修改，第一至第三章代码保持此前交付版本。

## 重现与当前哈希

使用上述固定提交的干净 ES checkout（可仅包含 sources 所需路径），不能传教程仓库。许可证复用 [ARCHIFY-LICENSE.txt](ARCHIFY-LICENSE.txt)，生成 HTML 的字体许可原样保留。图源改变后完整 finalize 并指定新的 --out-dir 保存收据。

### plugin-isolation（architecture）

- 图源：[candidate.json](architecture-ch04-plugin-isolation-20261010-172141/candidate.json)
- HTML：[plugin-isolation.html](architecture-ch04-plugin-isolation-20261010-172141/plugin-isolation.html)
- JSON SHA-256：`f0fa580fde5eb986235cb262a3b53bc16059b2a82839399b5cc48a1e5f6f7c4b`
- HTML SHA-256：`edc2eecbad94e8a27686b27a5f9d79ce7d89c8ba2880c3c02d52ebc1d8e28873`
- 当前原生摘要：[plugin-isolation.finalize-summary.json](architecture-ch04-plugin-isolation-20261010-172141/plugin-isolation.finalize-summary.json)
- 当前 delivery：[plugin-isolation.delivery.json](architecture-ch04-plugin-isolation-20261010-172141/plugin-isolation.delivery.json)

```bash
node /path/to/archify/bin/archify.mjs finalize architecture \
  .archify/architecture-ch04-plugin-isolation-20261010-172141/candidate.json \
  .archify/architecture-ch04-plugin-isolation-20261010-172141/plugin-isolation.html \
  --repo-root /path/to/elasticsearch --quality showcase --json
```

### reindex-registration（workflow）

- 图源：[candidate.json](workflow-ch04-reindex-registration-20261010-172141/candidate.json)
- HTML：[reindex-registration.html](workflow-ch04-reindex-registration-20261010-172141/reindex-registration.html)
- JSON SHA-256：`d92c70bb5e7f3a3da57d5f6f963eb5d6cb68134b02bd500fda84a784cc74cc01`
- HTML SHA-256：`9d22451637a6bb95ebd514150cb871aeb511b74b8a244b4c5a0c38ac9a6ad83c`
- 当前原生摘要：[reindex-registration.finalize-summary.json](workflow-ch04-reindex-registration-20261010-172141/review-3/reindex-registration.finalize-summary.json)
- 当前 delivery：[reindex-registration.delivery.json](workflow-ch04-reindex-registration-20261010-172141/reindex-registration.delivery.json)

```bash
node /path/to/archify/bin/archify.mjs finalize workflow \
  .archify/workflow-ch04-reindex-registration-20261010-172141/candidate.json \
  .archify/workflow-ch04-reindex-registration-20261010-172141/reindex-registration.html \
  --repo-root /path/to/elasticsearch --quality showcase --json
```
