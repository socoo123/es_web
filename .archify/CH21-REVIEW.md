# 第二十一章重构验收

2026-10-13（Asia/Shanghai）。按 AGENTS → STATUS → PLAN → CHAPTER_STANDARD → CLAUDE 执行，只处理 ch21、对应图源/产物/验收和 STATUS；未重读 tutorial，未使用子代理。复用共享 880px 布局、双主题与重播控制，没有修改其他章节或共享 CSS/JS。原有 `.gitignore` 的 learn-code/ 修改不纳入本次提交。

## 内容与固定依据

版本 **ES 9.4.0 / Lucene 10.4.0**，实际单节点 build_hash 与固定提交 `2e8528e92361c3399724226deaf2b46f933e925b` 一致。[源码审计](review/ch21-source-review.json)：**20 文件 / 46 精确区间 PASS**，只读取本章涉及的目标源码；本地字节与干净固定 checkout 的 git 对象一致，源码链接行号有效。

保留七段式、3 个学习目标、目录、图解跳转、5 道折叠问答、4 条陷阱、速记、已读/上下课链接。正文围绕快照职责、REST 观察、版本与 no-op、计算/提交/本地可见、Diff 基准推进。两幅官方图替换三个旧 SVG：静态 Architecture 四块职责，Workflow v2 一个有限 trace。原章无 ESFLOWS 机制播放器，本轮仍为 0，不把 trace 计入全站机制数量。

主要勘误：

- minVersions 实为 final；compatibilityVersions、clusterFeatures 也是字段。routingNodes 是按需缓存，慢路径同步；概念不可变并非每个读方法无锁，不要求深拷贝整棵树。
- REST API 上下文不序列化内部 Metadata.version，旧“两套计数器并排”卡无法得到原预期；wait_for_metadata_version 仍比较内部版本≥门槛，并要求门槛≥1。超时 HTTP 200/wait_for_timed_out=true，没有状态快照。
- 一份改变的状态递增一次，一个创建索引 API 可触发多个更新；两轮实测均 +3。相同设置重交本例成功但不换版本/UUID。
- term 随选举历史变化，不能固定为 1；投票字段为 last_committed_config、last_accepted_config、voting_config_exclusions，没有 config。
- pending_tasks 也包含 executing 项；字段 insert_order/time_in_queue_millis，不是历史更新统计或写入队列。
- Listener 在 state.set 后，但同步回调仍占用应用线程，慢回调挡后续状态；Applier 应读 event.state()。发布完成不意味着每个节点瞬时应用，主本地应用靠后也不等于每个落后节点先完成。
- Metadata 持久化按角色/上下文/全量与增量路径理解；路由表和成员在全部重启后需恢复/重新发现，不能说所有三块都从“Metadata + 节点复制”完整恢复。
- 原清理没有真的恢复 cluster.max_shards_per_node。稳定 ID ch21-12-settings 改为本课索引 refresh_interval 1s→5s；新增 1s 恢复与读回。全轮不写集群级设置，提供旧版配置迁移提示。

## 真实 ES 与完整重做

[真实响应](review/ch21-es-review.json)、[复现脚本](review/ch21-es-review.py)：**两轮各 29 个当前注册请求 PASS**（method/path/body 与注册表逐项相同），第二轮从第一轮点名清理后的空资源开始；**18 条补充真实请求 PASS**。原 16 稳定 ID 保留，新章 3 组 / 29 操作卡（A10/B7/C8/清理4）。

- 匿名单节点 localhost:9200；显式 1 主 0 副、auto-expand=false、strict keyword、source enabled、refresh=1s、无 default/final pipeline。两索引局部 green/无 initializing/relocating 后取基线。
- 第一轮 V1/V2/V3=402/405/405；第二轮=414/417/417。创建 +3 且 UUID 换新；已有字段写入集群版本不变，GET 文档 _version=1、found=true。
- 设置 1s→5s 后第一轮状态 version=406，重交同值仍 406；第二轮=418/418。C2 输出 5s，但 metadata.version 缺席。显式恢复 1s 后实际读回成功。
- 不含 version/master_node metric 时对应字段缺席；加 metric 出现。term=1 为本次历史值，两份投票配置指认本节点，pending tasks 空数组为本次窗口观察。
- 等待门槛 1：HTTP 200/wait_for_timed_out=false 且有状态；最大 long+1ms：200/true 且只有 cluster_name 与超时标志。补充门槛 0：400，reason 为 provided waitForMetadataVersion should be >= 1。
- 补充：重复创建 400/resource_already_exists_exception；重复写已声明字段 200/updated/_version=2，集群版本/UUID 不变；strict 未知字段 400 且未写入 GET404。
- 补充索引 read-only：blocks 中 id5/write+metadata_write，健康仍 green，写入 403/cluster_block_exception；显式复原 false 后 blocks 空。只操作本章索引。
- 两轮最后两个索引 HEAD404，补充重复删除 404/index_not_found_exception；集群级设置前后完全一致。

初稿诊断与修复真实保留：`ch21-es-review-initial-fail.json` 是门槛 0 的真实 400；`ch21-es-review-readback-fail.json` 保留 flat_settings 下过细 filter_path 得 {} 导致读回守卫失败。门槛改 1、读回改嵌套 settings 输出，点名清理后重新完成最终两轮。没有用伪造响应补通过；早期失败不当作最终请求通过。

单节点未验证远程 Diff、选举/投票容错、失主、落后节点追赶、全重启持久化或性能；这些只据固定源码说明边界。

## 官方 Archify 门禁

使用[官方 Archify 3.0.1 技能](https://github.com/tt-a1i/archify/blob/v3.0.1/archify/SKILL.md)，已读 authoring defaults/repository authoring、Architecture 与 Workflow v2/common 完整 schema、所选 examples、viewer/runtime、delivery/repair 与 Workflow 视口布局契约。首次附固定源码证据并传真实 checkout `--repo-root`，只改 JSON，通过完整 finalize 生成，未手改 HTML。复用 ARCHIFY-LICENSE.txt，生成 HTML 的字体许可保留。

| 图 | candidate SHA-256 | HTML SHA-256 | 当前收据 |
|---|---|---|---|
| architecture / snapshot-parts | `0177dcceb8853b495ff65820a3ef61815c27069ef981052deb4e710b79f92c62` | `71d0235bea94c0ed1638a37ca290e68796558fce1e8f5a24ad067268d2bd2e09` | 根目录 |
| workflow / publication-apply | `3a937d828058c9afa84dcb5d358594aae039af723c2115750903d93456b12269` | `eecb710aa8d1d0f83e71ed54346de2a0b7a7e01a5b8dbbbdadb10a73d40ef89a` | review-3 |

两图 validate/deliver/strict check 均 **showcase 9/9、0 errors/warnings、provenance current**；原生 **browser-check 和 finalize 整体 PASS**。update.noticeRequired=false。原生 visualReview=not-requested 是自动门禁状态，不替代下面的实际审图。

Workflow 初稿引用 Listener 到第29行越界，原生拒绝；修正到真实第27行后通过，保留 candidate-v1 与 source-range-fail 收据。独立 HTTP 初稿 1440px 最小普通节点说明约6.829px；移动逻辑列没有改善，继续按实测将 commit 并入发布职责分组，当前3个职责区、更紧凑的纵向主路径，普通节点说明7.155px、来源徽标6.261px。历史 candidate-v2/v3、根收据、review-2/3 与两份失败 HTTP 测量分别保留。

## HTTP、交互和实际截图审阅

[独立 HTTP](review/ch21-http-review.json) **PASS**：临时本地 HTTP + Python Playwright + 本机 Chrome。浏览器明确 abort ES 端点自动请求，真实 API 单列，没有模拟服务端响应。

- 两图独立 1440/1600/1920/2048 × 浅深主题，无横溢、说明卡无裁切。1440px 最小普通节点说明 Architecture 11.554px、Workflow 7.155px。
- 章节 1920/1440/1024/768/390/320 × 浅深；桌面阅读列≤880px，各类标题/正文/图框/图注/表格/操作卡/尾部边界差≤1px。页面/iframe 无横溢，所有节点包含在图框，iframe 无垂直裁切。高度桌面760/900px，≤800px500/580px，实际看图后收紧空白。
- 节点探索、固定源码链接、关闭/Escape、节点键盘 Enter、展开不带 present 的完整查看器、父子主题同步通过。静态图没有可见动画按钮，motion 属性省略；trace 暂停→外层重播恢复、外层 Enter 重播通过。
- 目录/已读、29 张卡的实际控制台导航与 method/path/body、endpoint/auth alias/raw 传递、/es_web/ 前缀和相对资产通过；.nojekyll 存在，未处理 JS 错误/失败 HTTP 为空。
- 390/320 节点探索与源码表自身横滑通过；系统 reduced motion 优先，trace 静止且按钮禁用，重播不覆盖系统偏好，页面无平滑滚动。无机制播放器需验收。
- **实际查看最终5张拼图，覆盖20张当前截图**：两图独立/桌面嵌入/390px、章节首屏、C2操作卡、源码表的浅深主题；另看完整浅色独立 Workflow。无交叉/节点截断；手机图为概览，细字需要探索或展开缩放，必要机制在正文/图注。源码表允许自身横滑。截图生成没有替代实际查看。

测试脚本曾在 Escape 已关闭后重复点隐藏关闭按钮，以及假定静态图必有 data-motion=still；两次是验收脚本假设，诊断报告保留并修正，最终全量重新检查通过，未修改生成 HTML 绕过。

[视觉证据绑定](review/ch21-visual-review.json)、[最终文件与原生收据哈希](review/ch21-artifacts.json)绑定本次当前版本。

## 结构、复现与交付

`node tools/check.mjs`：30正式页 / 648实验操作 / 22机制播放器 PASS；`node --check experiments/ch21.js`、figwidth、git diff --check、16原ID/29有序唯一槽位、GET/HEAD无body PASS。实验注册数量和 trace 动画分别统计。

```bash
node tools/check.mjs
node --check experiments/ch21.js
node tools/figwidth.mjs chapters/ch21.html experiments/ch21.js
ES_SOURCE_ROOT=/path/to/clean-es-v9.4.0 python3 .archify/review/ch21-source-audit.py
python3 .archify/review/ch21-es-review.py # 要求两索引不存在，实际两轮，最终清理
/path/to/playwright-python .archify/review/ch21-http-review.py
/path/to/pillow-python .archify/review/ch21-visual-sheets.py # 仅生成拼图
# 图源更改后：完整 finalize <type> candidate.json output.html --repo-root ... --quality showcase --out-dir 新收据目录 --json
```

按持续授权将本轮章节、图源/产物/验收与 STATUS 提交并推送 origin/main。交付时另核对远端提交与 Pages 部署，本地 HTTP 通过不等于线上已经更新。
