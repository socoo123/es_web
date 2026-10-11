# 第九章交付与验证记录

按 CHAPTER_STANDARD 重构第九章，保留七段式、目录、课间导航、已读进度与控制台入口。远程 GET 使用 Sequence，普通请求帧编解码使用 Workflow v2，两图各有有限 trace；本章没有机制播放器，两类动画分别统计。原 7 个实验 ID 全部保留，新增 5 卡，共 2 组 / 12 张操作卡（含清理）。本轮修改范围为 ch09 正文、注册表、本章图源 / 产物 / 证据与 STATUS。

内容锚定默认自管 Elasticsearch 9.4.0 / Lucene 10.4.0，源码提交 2e8528e92361c3399724226deaf2b46f933e925b。28 个引用或补充核对的源码文件逐一与提交字节比对一致，62 个引用区间均在文件范围内；见 [源码复核](review/ch09-source-review.json)。首次 finalize 即传入真实干净 checkout 的 --repo-root，关键节点保留目标文件 / 行号。

校对覆盖 action 与 requestId、请求与响应 Reader 的查找及执行位置、DIRECT 与分片 get executor、异步接口可同步完成、普通帧 6B 前缀与 23B 固定头、length=全帧−6、请求可变头中的 ThreadContext / action、压缩与特殊握手 / PING 范围。GetRequest 按父类和字段顺序配对，版本闸门使用当前 stream 的 TransportVersion；writeString 的长度是 Java char / code unit 数，不是 UTF-8 字节数。新增连接与观测边界：CAT 实现取发布地址、本地角色修正连接画像、累计成功 NodeChannels 组数、定时应用 PING 与 TCP keepalive、低层已知版本协商和服务层集群名谓词。单节点捷径只省该跳 wire 编解码 / TCP，不声称整个 GET 零复制或验证远程兼容。

## 分项验收

| 项目 | 实际结果 |
| --- | --- |
| 站点 / 语法 / 旧 SVG | node tools/check.mjs、node --check experiments/ch09.js、node tools/figwidth.mjs chapters/ch09.html experiments/ch09.js、git diff --check 通过；30 正式页 / 441 卡 / 22 机制播放器 |
| 原生 validate / deliver / strict check | 两图 showcase 9/9、零错误 / 警告，provenance current；当前 remote-get review-4、frame-codec review-2 |
| 原生 browser-check / finalize | **失败**，管理员策略禁止 Chrome 的 file URL 快照，ERR_BLOCKED_BY_ADMINISTRATOR；未修改策略，未把整体 finalize 记为通过 |
| 独立 HTTP Chromium | 两图各 1440 / 1600 / 1920 / 2048px 双主题；章节 1920 / 1440 / 1024 / 768 / 390 / 320px 双主题，最大 880px 列、各区边界差 ≤1px、页面 / iframe 无横向溢出 |
| 实际图面节点 | 在每个 iframe 可见时检查主 SVG 的所有节点位于图面边界内；窄屏保留概览、正文条件、节点探索与展开，未将缩小文字声称为全部细节可读 |
| 交互 | 探索 / 固定源码链接 / 关闭 / 展开、主题同步、暂停后外层重播 / Enter 重播、目录 / 已读、12 张实际控制台导航的 method / path / body、endpoint / auth alias / raw、Pages 子路径通过 |
| reduced motion | 禁止自动 trace；手动重播也维持静止，章节跳转不使用平滑滚动 |
| 真实 ES API | **首次与清理后重做未执行**。9200 连接拒绝，云运行时仍缺 /proc/self/coredump_filter；既有 ES 9.4.0 启动记录确认阻塞，未重复启动、修改 ES 或模拟响应 |

实验卡中的响应均是源码预期。A 组只读核对版本、CAT 发布端口、绑定 / 发布地址、默认设置及未知 REST 路由的 400 顶层 error 字符串。B 组显式单分片 / 零副本 / strict keyword mapping / 关闭周期刷新，等待本课索引 green，固定 ID 写入并 refresh，保存写后基线，实际执行独立 GET 卡，再按同一节点 ID 对照统计，最后点名清理。首次 / 重复创建、写入、删除分别解释；清理后重做 B1→B6 并取新基线。删除索引不清累计统计，历史非零与后台 / 其他客户端流量不能归因于本次 GET，累计连接组数不能与 13 个通道比较。

## 视觉审阅与修复

实际查看 **20 张最终截图**，包括两图独立 / 章节嵌入 / 手机的双主题、桌面与手机首屏、B6 统计卡及手机源码表。截图捕获与实际查看分别记录；[当前哈希清单](review/ch09-artifacts.json) 绑定所有图源、HTML、收据、源码审计、浏览器脚本 / 报告及最终截图。[HTTP 数值与功能结果](review/ch09-http-review.json) 为当前验收依据，共享 CSS / JS 未改。

Sequence 初稿的自发消息触发零跨度 / 标签越界，修改图源为协调回调、协调发起、数据接入与分片 GET 四个角色，保留六步请求 / 响应关系。固定列在宽屏留下空白，改用 spread 列；角色说明移入参与者标题以提升最小字号。Workflow 初稿的默认列与自动端口导致主路径绕行，改为居中的纵向同列节点，主路径明确 bottom→top 直连，TCP 字节标签保留。修复只改 JSON 并调用官方生成器，未手改 HTML；旧候选和原生失败收据保留。

最终 iframe 高度分别为 remote-get / frame-codec：桌面 940 / 820px，601–800px 为 780 / 680px，≤600px 为 500 / 440px。独立页所有 SVG 文字（含来源徽标）最小实测分别约 6.95 / 6.37px，普通节点文字最小约 10.92 / 7.28px；手机按概览使用展开和缩放查看细节。两套历史 HTTP 报告及截图保留在 review/ch09-before-citation-repair 与 review/ch09-before-route-repair，分别绑定修复引用区间和流程主路径之前的产物，不能替代当前报告。

## 复现

使用上述固定提交的干净 ES checkout 并包含所有引用 sources。字体许可保留在生成 HTML 中，共用 [ARCHIFY-LICENSE.txt](ARCHIFY-LICENSE.txt)。改图源后向新 review 目录执行完整 finalize；当前环境命令会因原生 file URL 检查失败退出。独立 HTTP 与真实 API 单列结果。

```bash
ARCHIFY_CHROME_NO_SANDBOX=1 node /path/to/archify/bin/archify.mjs finalize sequence \
  .archify/sequence-ch09-remote-get-20261011-003000/candidate.json \
  .archify/sequence-ch09-remote-get-20261011-003000/remote-get.html \
  --repo-root /path/to/es-v9.4.0 --quality showcase \
  --out-dir .archify/sequence-ch09-remote-get-20261011-003000/review-next --json

ARCHIFY_CHROME_NO_SANDBOX=1 node /path/to/archify/bin/archify.mjs finalize workflow \
  .archify/workflow-ch09-frame-codec-20261011-003000/candidate.json \
  .archify/workflow-ch09-frame-codec-20261011-003000/frame-codec.html \
  --repo-root /path/to/es-v9.4.0 --quality showcase \
  --out-dir .archify/workflow-ch09-frame-codec-20261011-003000/review-next --json

python3 .archify/review/ch09-http-review.py
node tools/check.mjs
node --check experiments/ch09.js
node tools/figwidth.mjs chapters/ch09.html experiments/ch09.js
git diff --check
```

## 当前图源与产物

| 文件 | SHA-256 |
| --- | --- |
| [candidate.json](sequence-ch09-remote-get-20261011-003000/candidate.json) | `9aac21d16e23fdd6a946d1cebb52ea8497e2b2ce4034179aca279b48f62c6e03` |
| [remote-get.html](sequence-ch09-remote-get-20261011-003000/remote-get.html) | `f41dfd60bdc23ca1a4d0f4f2a188f9891f31d3103f3aee9b6925d3284e9e9789` |
| [candidate.json](workflow-ch09-frame-codec-20261011-003000/candidate.json) | `c85ea21f5289ee10ecef80c6c6e203f493078bac5bfd56ef912c7913df2ebc7d` |
| [frame-codec.html](workflow-ch09-frame-codec-20261011-003000/frame-codec.html) | `b23eefaa44c33a904cc5e46867333b7d4acd4e8f7ac79874bee1fda67b4111b8` |

按用户持续授权将本轮代码、图源、产物及验收记录提交并推送 origin/main；交付消息提供 GitHub 提交与章节阅读链接。记录时间 2026-10-11T10:04:17.672704+08:00（Asia/Shanghai）。
