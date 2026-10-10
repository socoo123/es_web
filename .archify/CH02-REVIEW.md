# 第二章交付与验证记录

第二章按 CHAPTER_STANDARD 重构：两张 HTTP 卡、两个源码导航图、一个有限阅读路径 trace；未新增 ESFLOWS 运行时机制播放器。两图均使用官方 Archify 3.0.1 正式 CLI，生成 HTML 未手改。

源码仓库为 `https://github.com/elastic/elasticsearch.git`，固定 v9.4.0 提交 `2e8528e92361c3399724226deaf2b46f933e925b`。节点带已检查的文件/行号，首次 finalize 即传入真实 Git checkout 的 `--repo-root`。GET 图采用 Architecture 排布阅读目标与两条分支，箭头和 trace 表达读者查找动作，明确不是运行时调用链。

## 分项状态

- 原生 validate、deliver、严格 check：两图均 showcase 9/9，零错误/警告；源证据核验通过。
- 原生 browser-check：两图均失败，原因是管理员禁止 file://，报 ERR_BLOCKED_BY_ADMINISTRATOR。未修改政策；finalize 整体仍为 fail。
- 独立 HTTP Chromium 检查：通过。两图各检查 1440 / 1600 / 1920 / 2048px 与浅深主题；第一、二章各检查 1920 / 1440 / 1024 / 768 / 390 / 320px 与浅深主题，阅读列边界差 ≤1px，页面/iframe 无横向溢出。节点探索与关闭、固定提交源码链接、展开、主题同步、暂停后重播、键盘重播、目录与进度、两张实验卡的控制台跳转、Pages 子路径和 reduced motion 均通过。第一章原 NRT 手动步进也通过。无未处理 JS 错误或 HTTP 资源失败，记录绑定最终图源/HTML 哈希，见 [ch02-http-review.json](review/ch02-http-review.json)。该检查与原生门禁分开记录。
- 真实 ES API：当前云环境 127.0.0.1:9200 无连接，两张卡的请求与重做未执行。相关字段已核对 v9.4.0 源码，不能据此声称 API 实测通过。
- GitHub Pages：代码推送触发现有 main 根目录部署；云端访问 Pages 域受网络限制，部署结果未在本环境在线核验。

## 视觉审阅

实际查看了两图独立查看器的浅深主题、最终嵌入图、章节桌面/手机首屏、手机两幅图和定位表。手机图用于总览，具体方法通过节点探索、放大及正文表格阅读；表格在自身容器内横向滚动。章节仅覆盖第二章，并回归第一章共用资产，未审阅其余章节。代表截图保存在 review/ch02-*.png。

## 重现生成

使用干净的 ES Git checkout，确认 `git rev-parse HEAD` 等于上述固定提交。普通 checkout 或含所有候选 sources 文件的 sparse checkout 均可；不要传教程仓库。修改现有图源后指定新的 --out-dir 保留旧检查证据。

```bash
node /path/to/archify/bin/archify.mjs finalize architecture \
  .archify/architecture-ch02-source-map-20261010-143543/candidate.json \
  .archify/architecture-ch02-source-map-20261010-143543/source-map.html \
  --repo-root /path/to/elasticsearch --quality showcase --json

node /path/to/archify/bin/archify.mjs finalize architecture \
  .archify/architecture-ch02-get-navigation-20261010-162448/candidate.json \
  .archify/architecture-ch02-get-navigation-20261010-162448/get-navigation.html \
  --repo-root /path/to/elasticsearch --quality showcase --json
```

许可证复用 [ARCHIFY-LICENSE.txt](ARCHIFY-LICENSE.txt)；生成 HTML 的内嵌字体保留自己的许可证。

## 当前产物与原生收据

### source-map

- 类型：`architecture`
- 图源：[architecture-ch02-source-map-20261010-143543/candidate.json](architecture-ch02-source-map-20261010-143543/candidate.json)
- HTML：[architecture-ch02-source-map-20261010-143543/source-map.html](architecture-ch02-source-map-20261010-143543/source-map.html)
- 图源 SHA-256：`b04b3c3f03a87c430d99bc25404729e303486b2c284daa9a3946bd0211cff7e5`
- HTML SHA-256：`fff0f5607c181275a02055fbecf5b377929b55ca5e95125d4dc72dae76e98695`
- 原生摘要：[review-2/source-map.finalize-summary.json](architecture-ch02-source-map-20261010-143543/review-2/source-map.finalize-summary.json)
- Delivery：[source-map.delivery.json](architecture-ch02-source-map-20261010-143543/source-map.delivery.json)


### get-navigation

- 类型：`architecture`
- 图源：[architecture-ch02-get-navigation-20261010-162448/candidate.json](architecture-ch02-get-navigation-20261010-162448/candidate.json)
- HTML：[architecture-ch02-get-navigation-20261010-162448/get-navigation.html](architecture-ch02-get-navigation-20261010-162448/get-navigation.html)
- 图源 SHA-256：`62d8f24e028fdab65a2dcf0ea9e5b86ecf6ef967a2acef91db5d3251fb458a99`
- HTML SHA-256：`47e31eb550191dfb11998daddfd6efaeffee86dbd49d2857bf0de33644e89e95`
- 原生摘要：[get-navigation.finalize-summary.json](architecture-ch02-get-navigation-20261010-162448/get-navigation.finalize-summary.json)
- Delivery：[get-navigation.delivery.json](architecture-ch02-get-navigation-20261010-162448/get-navigation.delivery.json)
