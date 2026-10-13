# 第二十三章重构验收

2026-10-13（Asia/Shanghai）。已按AGENTS依次读取STATUS本章记录/最近日志、PLAN、CHAPTER_STANDARD和CLAUDE；使用本会话已读的官方Archify3.0.1技能、repository authoring、Workflow v2/common schema、viewer与delivery契约，并补读Lifecycle v2 schema/example/布局契约。只重构ch23，更新首页该课计数/简介、STATUS及本课图源/产物/验收；复用共享CSS/主题/重播脚本，未重读tutorial、未使用子代理。

## 内容与固定源码

[源码审计](review/ch23-source-review.json)：**24个目标文件 / 56个精确区间 PASS**。实际干净ES v9.4.0 checkout，固定提交`2e8528e92361c3399724226deaf2b46f933e925b`；引用路径/区间合法，文件与固定Git对象字节一致，version.properties对应Lucene10.4.0。代码范围已实际读取；自动引用检查不代替机制核对。

保留七段结构、3个可验证目标、折叠目录/图解跳转、5道折叠问答、5条陷阱、速记、上下课及已读入口。正文、两图、七步动画和33卡统一了以下边界：

- 默认desired_balance后台以Balanced模型计算新目标，模型可模拟start；提交新输入后本轮也可先按已有目标reconcile。已有副本分配器先处理未分配primary，再replica；初始化、必要移动和普通平衡各检查当前动作条件。
- 不是“过滤NO才轮到打分”：Balanced explain先算权重，也给NO节点排名。Decider汇总取更严格结论，普通OFF可NO短路；解释模式保留更多具体票，ALWAYS哨兵仍不进数组。四种决定的汇总/节点比较中THROTTLE与NOT_PREFERRED顺序不同；默认初始化可接受YES/NOT_PREFERRED，THROTTLE本轮暂缓，其他动作的准入另分支。NO可在条件改变后重评。
- 四维归一化模型含总片数、同索引片数、预测写入负载和分片字节；index因子不强制主角色均匀。2e-11乘大字节差不等于小影响；threshold结合minWeightDelta，不是片数差公式，2/1/1仅示意。
- 源RELOCATING仍active，目标独立INITIALIZING；目标启动后移除源路由，“路由已移除”不是状态枚举。普通replica目标向active primary恢复，B/C搬迁配对不能推出数据B→C。目标失败且源仍在可取消源搬迁并删除目标，其他失败另有路径；incoming/outgoing各2与初始本地primary4分开。
- 水位比例表示已用、字节表示最低空闲。headroom默认200/150/100GB以相应watermark未显式配置为条件，否则未配headroom默认为-1；换算限额不额外相加。新空/clone非active primary低水位豁免有条件，high不保证有可行目标，实际还考虑大小/预留/路径/统计。缺磁盘统计有fail-open YES，CAT百分比不是完整政策输入。
- 默认普通flood的read_only_allow_delete WRITE块为429，普通index.blocks.write为403；文档删除也是WRITE。Green与可写分别解释，不将普通块实验当作真实水位触发。
- 空explain优先可访问未分配primary再replica，不保证本课索引；POST明确selectors，初始化/迁移中的在途说明可NOT_TAKEN。默认desired explain委托Balanced按当前状态解释，不是未来目标历史，也不执行分配。

## 实验与实际运行限制

原**11个稳定ID全部保留**，增22共33操作：A13/B3/C13/清理4；旗舰七步ID保留。HTML槽与注册顺序一一对应、ID唯一，GET/HEAD无body，修改只点名`tut-l23-yellow`与`tut-l23-filter`（1主1副/1主0副、auto-expand=false、refresh1s、strict keyword）。A限定一个合格数据节点，等待局部Yellow/Green和在途结束，恢复副本需求后再解释；区分INDEX_CREATED/REPLICA_ADDED历史原因与当前NO。

C先确认虚构节点名无人匹配，require过滤使P0未分配，创建wait_for_active_shards=0，明确解释与配置读回；移除过滤后等Green，固定ID写入基线，设置普通写块，对照Green与预期403/文档删除拒绝，显式恢复后更新同ID。普通块避免手工flood块被Monitor自动释放造成操作快慢依赖。末尾点名删除两索引、分别HEAD404，明确重复创建400/重复删除404及清理重建流程。

**真实API、本课初次运行及两轮重做均未实测。** [本轮启动证据](review/ch23-es-runtime.json)：Docker daemon与官方缓存镜像可用；正常Compose实际重启ES9.4.0后，进程因环境缺`/proc/self/coredump_filter`，在`Elasticsearch.setCoredumpFilter`抛RuntimeException/NoSuchFileException，容器退出1，9200无服务。未模拟成功响应、修改ES二进制或绕过云端策略。所有卡片预期为固定源码支持的条件化预测。

多节点目标计算/迁移/主提升、真实磁盘压力及水位、恢复并发与性能未实测；七步动画是概念示意。两个node不自动代表独立物理故障域，颜色不证明写入、性能或零数据丢失。

## 官方图解门禁

Workflow v2 `desired-reconcile`、Lifecycle v2 `relocation-pair`，zh-CN/showcase/trace，首次附固定源码并传实际checkout `--repo-root`；只编辑candidate JSON、官方完整finalize生成HTML，保留Archify及字体许可。当前文件/收据哈希见[产物绑定](review/ch23-artifacts.json)。

| 图 | 当前收据 | validate / deliver / strict check | 原生browser-check / finalize整体 |
|---|---|---|---|
| desired-reconcile | 图目录根收据 | PASS，showcase9/9，0 errors/warnings，provenance current | FAIL，file导航被管理员策略阻止 |
| relocation-pair | review-2 | PASS，showcase9/9，0 errors/warnings，provenance current | FAIL，同上 |

两图原生浏览器均报`net::ERR_BLOCKED_BY_ADMINISTRATOR`，finalize整体**非成功**。没有修改检查器/运行策略，也没有将独立HTTP结果改写为原生PASS；update unavailable、noticeRequired=false。

迁移图初稿三列两行在390px被Reader强制720px宽、左右节点裁切；实际失败[几何证据](review/ch23-containment-failure.json)及[截图](review/ch23-containment-failure.png)保留。改JSON为搬迁前/并存/恢复后三行两列，画布由902×424变为640×620，重新完整finalize得到当前review-2；保留candidate-initial及根原生收据。未手改HTML/CSS，不以页面无横溢掩盖图内裁切。

## 独立HTTP与实际视觉审阅

[HTTP](review/ch23-http-review.json)、[局部滚动](review/ch23-scroll-review.json)、[七步捕获](review/ch23-mechanism-review.json) PASS，哈希绑定当前章节/JS/图源与HTML。使用本机Chromium、Python Playwright与临时同源HTTP服务器；控制台深链ES流量明确abort，只测页面导航与请求填入，不代表真实API成功。

- 两图各1440/1600/1920/2048×双主题，说明卡完整、整页无横溢。最小SVG/普通节点投影：workflow6.3314/7.2359px、lifecycle8.3344/9.5250px，均达到桌面门槛。
- 章节1920/1440/1024/768/390/320×双主题；桌面列≤880px，正文/图框/图注/卡/源码表左右差≤1px。页面及iframe无横溢，全部实际节点完整容纳，iframe无垂直裁切；图高桌面850/700、≤800px540/480。
- 节点关系/固定源码探索及关闭、键盘Enter/Escape、展开完整图、主题同步、暂停后外层重播/Enter、目录锚点/已读与七步前后/播放/暂停/重置/左右键PASS。
- 33张卡逐张实际打开控制台，method/path/body与注册请求一致；endpoint/auth别名/raw参数、`/es_web/`前缀资产/图/控制台验证PASS；`.nojekyll`在库中。未处理JS错误/异常HTTP响应为空。
- reduced motion覆盖重播，图运动按钮禁用；机制不自动播放、可步进；无平滑滚动。390/320源码表及旧SVG只在自身容器横滑，整页无横溢。
- **实际查看全部7张拼图，覆盖24张独立/嵌入/桌面/390px/实验/源码表/机制双主题截图与全部7步完整快照**；见[实际审阅绑定](review/ch23-visual-review.json)。无节点/文字/路径遮挡。手机图为概览，细字可探索/展开缩放，必要结论在正文/图注；旧机制画布局部滚动、标题省略，控制/步数/解说可读。截图生成本身不等于审阅。

先通过后的“从低到高”比较说明及清理文字校对触发最终检查；此前完整HTTP/截图记录保存在`review/ch23-before-final-copy`，以根目录当前哈希验收为准。手机初稿失败证据另外保留。

## 复现与交付

`node tools/check.mjs`：30正式页/678卡/22机制PASS；JS语法、figwidth、diff、11原ID/33有序唯一槽、无GET/HEAD body、点名修改范围PASS。首页只改ch23卡片，其他章节与共享运行时未改。

```bash
node tools/check.mjs
node --check experiments/ch23.js
node tools/figwidth.mjs chapters/ch23.html experiments/ch23.js
ES_SOURCE_ROOT=/path/to/clean-es-v9.4.0 python3 .archify/review/ch23-source-audit.py
python3 .archify/review/ch23-http-review.py
python3 .archify/review/ch23-scroll-review.py
python3 .archify/review/ch23-mechanism-review.py
python3 .archify/review/ch23-visual-sheets.py # 生成不等于实际审阅
python3 .archify/review/ch23-bind-artifacts.py # 需已有当前实际审阅记录
# finalize <workflow|lifecycle> candidate.json output.html --repo-root ... --quality showcase --out-dir 新收据目录 --json
```

Python需Playwright/Pillow，当前执行器`/usr/bin/chromium`。受管理策略限制时如实保留原生失败。按仓库持续授权提交并推送origin/main，交付时另核对远端；本地HTTP通过不证明GitHub Pages已经部署。
