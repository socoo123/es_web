# ch12 重构与验收

时间：2026-10-11T14:30:26.427946+08:00（Asia/Shanghai）。范围：ch12 章节 / 实验、两图源 / 生成物 / 本章记录、STATUS；其他章节及共享 CSS / JS 未改。阅读路径：[ch12](../chapters/ch12.html)。用户持续授权按 AGENTS / CHAPTER_STANDARD 提交并推送 origin/main。

## 内容与实验

七段式、880px 阅读列 / 924px 外层、双主题、三个跳转 / 折叠目录、五个源码入口、四道折叠思考题 / 五条陷阱 / 速记 / 已读 / ch11–ch13 导航。章节约 4344 中文字（正文机制段约 2625）。修正线程断言、失败恢复位置、final 条件、模拟验证范围、路由碰撞 / 创建版本、GET 与 refresh、管道定义存储 / 删除；详见 STATUS 的第十二章勘误。

4 组实验 / **48 张操作卡**，保留原 **20 个 ID**；原无 ESFLOWS，本轮仍无机制播放器。两幅图有两条有限 trace，单独统计。分组数量 A10 / B7 / C9 / D16 / 清理6；顺序与注册表一致。三索引显式 standard、stored source、主副本数、周期 refresh=-1、普通非分区路由、default / final 槽及 mappings。涉及搜索的写入显式 refresh=true，三次局部健康等待；首次 / 重复写入、已有索引、noop / 失败、D16 恢复与清理后重做条件写清。清理点名三索引并允许不存在，再分别删除五管道；重复删管道可 404，引用保护错误须处理。

### 源码依据

官方仓库 `https://github.com/elastic/elasticsearch.git`，固定 v9.4.0 提交 `2e8528e92361c3399724226deaf2b46f933e925b`，真实 checkout `/workspace/scratch/es-v9.4.0` 清洁。只访问本课目标 ingest / bulk / mapper / routing 文件，未通读 tutorial 或目录。**23 文件 / 56 区间**逐一校验边界与 committed bytes；可用的 checkout 字节一致。两个通用异常辅助文件由固定 git 对象定点读取，记录 localCheckoutPresent:false，没有把未提交修改作证据。

- TransportAbstractBulkAction：两个槽解析、执行 / 转发、异步后切回协调；IngestService：定义写入元数据、PipelineIterator、失败 / drop 返回、final 禁改目标、重定向解析、metadata / source 回写、删除引用检查与本地对象更新。
- ConfigurationUtils / OnFailureProcessor / Pipeline / CompoundProcessor：处理器包装层和管道根层的续接差异、ignore 优先、临时失败元数据、同步与回调。
- Set / Rename / Grok / Date：实际字段变换、默认参数、局部恢复、字符串捕获与日期解析；IngestDocMetadata / IngestDocument / DropProcessor：元数据类型、活动栈与 null。
- SimulatePipelineTransportAction / Request / ExecutionService：模拟构造和执行、逐文档 error；BulkRequestModifier：drop 的 noop；BulkOperation / IndexRouting / IndexShard：路由、创建版本、映射与 Engine 边界。
- D14 是 IngestPipelineException 包装 IllegalStateException；ElasticsearchException.status / ExceptionsHelper.status 证明默认 HTTP 500 的代码路径。API 没有实测，卡片仍要求核对真实错误原因和响应。

记录及复现脚本：[source-review.json](review/ch12-source-review.json)、[source-audit.py](review/ch12-source-audit.py)。

### 真实 Elasticsearch

**首次实验未运行；清理后完整重做未运行。** 当前 `curl http://127.0.0.1:9200/` 连接拒绝；`/proc/self/coredump_filter` 不存在，已有启动记录 `/workspace/scratch/es_web-onboarding/start.md` 证明 9.4.0 bootstrap 在该接口失败。没有重新循环启动 Docker、降版、修补 ES 或伪造 proc。没有代发清理或使用模拟 ES 响应；预测均是固定源码预期。

## Archify 图源、产物与原生门禁

使用[官方 Archify 3.0.1](https://github.com/tt-a1i/archify/tree/v3.0.1/archify)及[已读取的 SKILL.md](/workspace/shared/skills/archify-3.0.1/archify/SKILL.md)，并读取 Workflow / common schema、例子与相关 authoring / repository / viewer / repair 契约。MIT 许可复用 [ARCHIFY-LICENSE.txt](ARCHIFY-LICENSE.txt)，生成 HTML 的嵌入字体许可保留。仅编辑 JSON，使用正式 CLI `finalize workflow --repo-root ... --quality showcase --json`，没有手改 HTML。

| Workflow v2 | 图源 SHA-256 | HTML SHA-256 | 当前收据 |
|---|---|---|---|
| [ingest-journey](workflow-ch12-ingest-journey-20261011-141434/ingest-journey.html) | `0b226c0eacf26fd7f4257a86b528fc1cd0c7437afa0483b80f4897879fb13e00` | `5572119454016ddc4e8fd2af699c1c7739ebd60be637a96799b47bc458fb59f2` | `workflow-ch12-ingest-journey-20261011-141434/ingest-journey.finalize.json` |
| [failure-scope](workflow-ch12-failure-scope-20261011-141434/failure-scope.html) | `012206bcd2371386f146327731082cc0a512e45d330a575688ec502d4b1507a7` | `20a4a35954b3a5061c5dd90147321cf90ad84e157346cd3838dbffd43d583b0c` | `workflow-ch12-failure-scope-20261011-141434/review-3/failure-scope.finalize.json` |

两图当前 **validate / deliver / strict check 均 PASS，showcase 9/9，0 errors / warnings，provenance current**。原生 **browser-check FAIL，finalize 整体 FAIL**：Chromium 对 file URL 报 ERR_BLOCKED_BY_ADMINISTRATOR。技能支持的 ARCHIFY_CHROME_NO_SANDBOX=1 仅用于运行沙盒中的 Chromium，没有改管理策略、注入文件内容或把独立 HTTP 验证冒充原生门禁通过。update.noticeRequired=false / cache-unavailable，无升级提示。

ingest-journey 用六个步骤分三条职责 lane；失败 / drop / 重定向和模拟范围在正文及卡片明确。failure-scope 两条独立有向链，处理器包装与根管道分上下 lane，不把对照关系画成执行顺序。两图箭头表示调用 / 回调 / 返回，省略的写入实现条件写明。

### 修复历史

failure-scope 首稿双列 `823×534` 比例在原生交付阶段触发 composition/viewport-height；保留 candidate-initial 与根失败收据。按诊断拓宽节点，review-2 原生结构全绿，但 HTTP 390px 下 local-error 出现在 x=-48.44，确有裁切。读取 viewport 修复契约后，只重排 JSON，完整保留六节点 / 四关系 / 语义 / 来源，改为两个窄的独立竖向栈；review-3 当前原生结构及 HTTP 容纳通过。旧候选、旧 HTML、失败测量 / 两张旧独立截图见 [before-viewport-repair](review/ch12-before-viewport-repair/failure.json)，旧图不计入最终视觉审阅。

## 独立 HTTP 与视觉审阅

独立 Python / Playwright / 已安装 Chromium，通过临时本地 HTTP 服务验证，不发送实验 API。报告：[HTTP](review/ch12-http-review.json)、[局部滚动](review/ch12-scroll-review.json)、[长卡捕获修复](review/ch12-card-capture.json)。测试脚本可复现；所有报告绑定当前 chapter / experiment 或图源 / HTML 字节。

- 两幅独立图在 1440 / 1600 / 1920 / 2048px × 浅深主题，说明卡不裁切、页面无横向溢出；最小 SVG 文本 / 普通节点上下文投影分别约 6.371 / 7.281px（旅程）、6.599 / 7.542px（恢复）。
- 章节 1920 / 1440 / 1024 / 768 / 390 / 320px × 两主题：阅读列 ≤880px、各区左右差 ≤1px、目录不覆盖、页面 / iframe 无水平溢出；主 SVG 的所有节点完整位于图面板。
- 实测 iframe 高度：旅程桌面940、601–800px 780、≤600px 500；恢复820 / 700 / 450。缩窄时内容完整；390 / 320px 的源码表自身 overflow:auto / scrollLeft>0，整页仍容纳。
- 两图节点探索 / 固定源码 / 清除 / 展开弹窗、双主题同步、暂停后外层重播、Enter 重播；目录锚点 / 已读开关、48 张实际卡片到根控制台并核对 method / path / body、端点 / 认证别名 / raw、/es_web/ 前缀资产及深链通过。
- reduced motion 保持两图静止，外层重播不能强行恢复动态、按钮状态正确、页面无平滑滚动；原无机制播放器。JS errors=[]、failed HTTP=[]。

**实际查看20张最终截图**：两图独立4、嵌入4、手机4、章节头桌面 / 手机4、手机实验卡2 / 源码表2。长卡旧 locator 截图曾把 sticky topbar 合成在中间；调整捕获视口高度、保持390px宽，重捕获两张并实际复核。没有改页面去掩盖问题。布局 / 箭头 / 节点内容 / 双主题 / 手机卡片与阅读列通过视觉审阅；桌面两图都完整。

窄屏图是完整概览，细字需节点探索或展开缩放，未声称手机原比例细字可读。源码表只在自己的容器左右滚动，截屏部分列并非整页溢出。未验证 GitHub Pages 部署完成。

## 静态检查与复现

`node tools/check.mjs`：30正式页、492操作卡、22机制播放器，全绿。`node --check experiments/ch12.js`、`node tools/figwidth.mjs chapters/ch12.html experiments/ch12.js`、`git diff --check` 通过；全部20稳定ID保留，48唯一槽位和注册次序一致，.nojekyll 存在。

```bash
node tools/check.mjs
node --check experiments/ch12.js
node tools/figwidth.mjs chapters/ch12.html experiments/ch12.js
python3 .archify/review/ch12-source-audit.py
python3 .archify/review/ch12-http-review.py
python3 .archify/review/ch12-scroll-review.py
```

HTTP / 原生浏览器命令需执行环境允许 Chromium 子进程和本地网络。原生复现命令保留在 finalize 收据；该命令整体失败是环境 file URL 门禁，不能以其他报告改写为成功。

当前验收文件与20张已审阅截图的 SHA-256 绑定见 [ch12-artifacts.json](review/ch12-artifacts.json)。
