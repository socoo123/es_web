# 第三章交付与验证记录

第三章依照 CHAPTER_STANDARD 重写，复用 880px 阅读列与章节共用主题/重播脚本。新增两幅官方 Archify 3.0.1 图：Sequence 解释进程管道与节点启动，Lifecycle v2 解释状态转移和后续资源清理；均启用有限 trace，生成 HTML 未手改。原 ch03-boot 保留稳定 ID，更新为八步机制快照；两张 HTTP 卡保持原 ID 与只读性质。

源码仓库为 `https://github.com/elastic/elasticsearch.git`，固定 v9.4.0 提交 `2e8528e92361c3399724226deaf2b46f933e925b`。各关键节点附目标文件与行号，首次 finalize 即传入真实干净 ES Git checkout 的 --repo-root。Sequence 的内部组件是调用目标的聚合角色；图省略具体服务装配、失败清理与关机中断，正文明确这些范围及入群等待超时分支。

## 内容核对

- 9.4.0 由 ServerLauncher 启动 preparer 和 server；准备器产出 LaunchDescriptor，launcher 发送 stdin ServerArgs 并监视 stderr READY。
- Node.start 在开头设置 STARTED；GatewayMetaState 先读元数据交给 Checks，之后才接收 Transport 并发起入群。
- 初始等待默认 30s，超时告警继续、0 跳过；HTTP 后仍有可选 readiness、端口文件及插件回调，返回后入口才发送 READY。HTTP、READY、集群健康分别判断。
- 普通自动强制检查看 Transport 的 bind / publish、snapshot 与 single-node；显式强制及 alwaysEnforce 另算。
- 保留四态与未 start 直接 close 分支，标志先变、动作后执行；HTTP 较早停，关闭非机械逆序，NodeEnvironment 在 close 后段释放锁。
- CAT http 取 publishAddress；process.mlockall 报实际锁定结果，不单凭 false 反推配置；PID 可能属于容器命名空间。

各结论在章节正文、图注、动画解说、实验预期和速记同步修正；旧说法及具体源码链接登记在 STATUS 勘误表。

## 分项状态

- 站点结构与 JS：node tools/check.mjs 全绿，experiments/ch03.js 通过 node --check，git diff --check 通过。
- 原生 validate / deliver / strict check：两图均 showcase 9/9、零错误/警告，源码证据核验通过、provenance current。
- 原生 browser-check：ERR_BLOCKED_BY_ADMINISTRATOR，管理员策略禁止 file://。finalize 整体仍为 fail；没有修改政策，独立 HTTP 检查不替代该门禁。
- 独立 HTTP Chromium 检查：通过。两图各 1440 / 1600 / 1920 / 2048px 与浅深主题；第三章 1920 / 1440 / 1024 / 768 / 390 / 320px 与浅深主题，阅读列 ≤880px、边界差 ≤1px、页面/iframe 无横向溢出。节点探索、关闭、固定提交源码链接、展开、主题同步、两图暂停后重播、键盘重播、目录/进度、实验深链与 Pages 子路径正常；reduced motion 优先，八步手动播放器和 SVG 文字范围通过；无未处理 JS 错误或 HTTP 资源失败。最终记录绑定图源、HTML、章节与实验 JS 哈希，见 [ch03-http-review.json](review/ch03-http-review.json)。
- 真实 ES API：127.0.0.1:9200 连接拒绝，两张实验卡的请求及重复运行未实测。源码核对和浏览器请求填充不能代替真实响应验证。
- Pages：推送 main 触发现有根目录部署；云环境在线访问 Pages 受网络限制，部署完成未在本环境核验。

## 视觉审阅

实际查看两图独立浅/深主题、最终章节嵌入浅/深样本、390px 两图与章节首屏，以及八步播放器末帧。Sequence 使用 spread 消除多余右侧空白；Lifecycle 改为两列三行，手机完整显示全部四态和关闭分支。手机图用于总览，具体内容通过放大、节点探索、正文及逐步解说阅读，不声称手机概览字号等同正文。原机制 SVG 在自身容器内滚动，未扩宽整页。代表截图在 review/ch03-*.png。共用 CSS/JS 未修改，第一、二章代码未改。

## 重现生成与当前产物

使用上述提交的干净 ES checkout（或包含 candidate.sources 文件的 sparse checkout）；不要传教程仓库。原生浏览器需要允许其 file:// 快照的环境。改图后用新的 --out-dir 保存收据，不手改 HTML。许可证复用 [ARCHIFY-LICENSE.txt](ARCHIFY-LICENSE.txt)，生成 HTML 的字体许可保持原样。

### startup

- 类型：sequence
- 图源：[.archify/sequence-ch03-startup-20261010-165543/candidate.json](sequence-ch03-startup-20261010-165543/candidate.json)
- HTML：[startup.html](sequence-ch03-startup-20261010-165543/startup.html)
- 图源 SHA-256：`3313994bb79677629f256b161fb35cf51854de5672e86d1f4d80faf5739cacff`
- HTML SHA-256：`8854af52e55b845674fde2dc8faaac596dcb7994ff40b1d9c960cd82d9906f5a`
- 当前原生摘要：[review-3/startup.finalize-summary.json](sequence-ch03-startup-20261010-165543/review-3/startup.finalize-summary.json)
- Delivery：[startup.delivery.json](sequence-ch03-startup-20261010-165543/startup.delivery.json)

```bash
node /path/to/archify/bin/archify.mjs finalize sequence \
  .archify/sequence-ch03-startup-20261010-165543/candidate.json \
  .archify/sequence-ch03-startup-20261010-165543/startup.html \
  --repo-root /path/to/elasticsearch --quality showcase --json
```

### node-lifecycle

- 类型：lifecycle
- 图源：[.archify/lifecycle-ch03-node-lifecycle-20261010-165543/candidate.json](lifecycle-ch03-node-lifecycle-20261010-165543/candidate.json)
- HTML：[node-lifecycle.html](lifecycle-ch03-node-lifecycle-20261010-165543/node-lifecycle.html)
- 图源 SHA-256：`d481801178f917c9e3cbc5ff776df58010b9cafaf31ea3660f6bccc29b8ae160`
- HTML SHA-256：`220be809401de4b88e3fc2af18be46bc8dbadba921a43345d92b5a291c6ebd7a`
- 当前原生摘要：[review-2/node-lifecycle.finalize-summary.json](lifecycle-ch03-node-lifecycle-20261010-165543/review-2/node-lifecycle.finalize-summary.json)
- Delivery：[node-lifecycle.delivery.json](lifecycle-ch03-node-lifecycle-20261010-165543/node-lifecycle.delivery.json)

```bash
node /path/to/archify/bin/archify.mjs finalize lifecycle \
  .archify/lifecycle-ch03-node-lifecycle-20261010-165543/candidate.json \
  .archify/lifecycle-ch03-node-lifecycle-20261010-165543/node-lifecycle.html \
  --repo-root /path/to/elasticsearch --quality showcase --json
```
