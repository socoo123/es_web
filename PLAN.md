# PLAN.md — 实施规范

进度看 STATUS.md;本文只定义「什么是正确的」。2026-09-22 定稿,P0 已落地。

2026-10-10 补充：[CHAPTER_STANDARD.md](CHAPTER_STANDARD.md) 是后续章节重构的专项细则，采用用户已确认的第一章基线。章节内容、Archify 图解、宽度、动画交互与验收按专项细则；实验与旧机制动画 schema 仍按本文。转写进度与图解重构进度分别记录在 STATUS。

框架学习篇按 [FRAMEWORK_PLAN.md](FRAMEWORK_PLAN.md)、[FRAMEWORK_CASES.md](FRAMEWORK_CASES.md) 的八阶段 F01–F45 推进。[F01 导学](framework/f01.html)已重写，讲 ES 用途、旅游搜索问题、数据库职责和全程路线；F02 用样本解释数据到结果，F03 首搜，F07 引入 Boot 4/JDK 25 与课程提供的本机搜索展示壳。F12 基础结业、F22 实用搜索结业、F45 完整复现。F01–F10可阅读；F04/F05/F06已交付正文与实验脚本、真实ES待验收；F07已交付Java实连与本机展示壳、F08已交付多字段与高亮、F09已交付聚合与筛选计数、F10已交付显式排序，F11–F45待实施，验收见 STATUS；源码篇 ch01–ch30 编号不变。

框架篇写作按 [FRAMEWORK_STANDARD.md](FRAMEWORK_STANDARD.md)：先业务体验、定义/职责与因果，再展示本课需要的 REST/DSL、Java、结果和反例；F01/F02 允许无执行代码。网站贯穿教学，读者使用配套展示壳观察结果，不学习前端开发；浏览器经本机 Java 调用 ES，Pages 只承载教程。D2 优先、Mermaid 可用，复杂机制可用 SVG；阅读列/双主题/重做方式参考源码篇。下述模板与 chNN 注册规则继续适用于源码篇，框架执行课的完整关键实现不受源码走读篇幅限制。

后续教程写作与内容审阅使用用户指定的 xhigh 推理强度，实际运行入口的设置与限制按 FRAMEWORK_STANDARD 记录。

## 1. 站点形态

纯静态、零构建、零 CDN。双击 `index.html` 即用(file:// 场景靠 `.js` 注册表而非 fetch JSON)。
真实 ES 交互 = fetch → `http://localhost:9200`(docker 起 9.4.0,CORS 已开,见 `docker/`)。

```
index.html / console.html / cheatsheet.html
chapters/ch01..ch30.html          # data-status="stub" → 转写完成后去掉
experiments/chNN.js               # 同时注册 window.ESEXPERIMENTS 与 window.ESFLOWS
assets/css/style.css              # 双主题变量体系(accent 蓝青系)
assets/js/{nav,progress,es-client,flow-player,experiments,console}.js
tools/check.mjs                   # 结构+注册表校验,改完必跑
```

## 2. 章节页七段式模板

```html
<article class="chapter" id="chNN" data-ch="chNN">   <!-- 转写完成后不带 data-status -->
  <header class="ch-header">kicker(LESSON NN · 篇名)/ h1 / meta-line(时长·前置·实验数)</header>
  <section class="goal">     学习目标:3 条,可被实验验证,禁空话</section>
  <section class="lesson">   N.1 心智模型(1 图 1 段)→ N.2 关键源码文件表(≤5)→ N.3+ 每节一个机制
                             穿插:figure.fig(旧 SVG 或 Archify 图解) / .exp-slot / .fp-slot / callout tip|warn / ktable</section>
  <section class="drills">   思考题 ≥3,details 折叠答案</section>
  <section class="pitfalls"> 陷阱 ≥2(callout warn)</section>
  <section class="recap">    速记 ktable + 一句话心法</section>
  <footer class="ch-footer">read-toggle + pager(上下课)</footer>
</article>
脚本顺序:demos 先(experiments/chNN.js)→ nav → es-client → flow-player → experiments → progress
```

写作:正文 2500-6000 字作为参考范围，以完整解释本课机制为准;类名/路径一律 `code`;API 动作用 `span.mth.mth-get/post/...`;
源码走读给「文件 → 方法」级别的锚点,不贴大段源码,贴关键行。

## 3. 实验 schema(experiments/chNN.js)

```js
window.ESEXPERIMENTS = window.ESEXPERIMENTS || {};
window.ESEXPERIMENTS['ch08-01-thread-pool'] = {
  version: 1, id: 'ch08-01-thread-pool',
  title: '看看 write 池的真实队列',        // ≤60 字
  method: 'GET',
  path: '/_cat/thread_pool?v&h=name,size,queue,rejected',
  body: null,                              // POST/PUT 可给对象或 JSON 字符串
  predict: '先猜:…',                       // 预测→操作→对照,≤200 字
  expect: '对照:…'                          // ≤300 字
};
```
id 规则:`chNN-序号-语义slug`,前缀必须属于本章。实验组与操作卡数分开统计，数量由本课教学覆盖决定；重构时保留已有稳定 ID。

## 4. 动画 schema(同一文件注册)

```js
window.ESFLOWS = window.ESFLOWS || {};
window.ESFLOWS['ch14-write-path'] = {
  version: 1, id: 'ch14-write-path', title: '一次写入的完整旅程',
  speed: 1800,                             // 600-6000
  steps: [ { svg: '<svg viewBox="0 0 760 300">…</svg>', note: '≤200 字解说' } ]
};
```
快照语义:每步一张**完整** SVG(自包含,含 fig-arrowhead defs 若用箭头),引擎不 diff。
快照内动效类(插入即播):`fp-pop` 弹入 / `fp-slide-right` 滑入 / `fp-draw` 描线(配 `pathLength="1"`)/
`fp-pulse` 呼吸 / `fp-glow` 发光。步骤 2-40。SVG 颜色一律用 `var(--…)` 类(fig-box/fig-box-hot/fig-name/fig-sub/fig-key/fig-arrow)保证双主题可读。

**SVG 文字排印纪律(2026-09-22 ch01 文字溢出修复后确立)**:
- 以下纪律用于手写内联 SVG 与 ESFLOWS 快照；Archify HTML 的布局、字体和主题由其 JSON 与生成器维护，不手改生成文件。
- 字号只在 style.css 定一次(fig-name 13 / fig-key 12 / fig-sub 12);SVG 元素上**禁止**写 `font-size` 属性——CSS 会把它覆盖掉,纯属误导
- 箭头一律元素级 `marker-end="url(#本图唯一id)"` 引用本图 defs 里的 marker;**不要**在 CSS 里写 marker-end(会全局覆盖所有 id)
- 估宽公式:fig-name/fig-key(等宽)0.6em/字符、中文 1em;fig-sub 英数 0.55em、中文 1em。**文本估宽 ≤ 盒宽 − 12**,放不下就改两行(盒高加到 78)或缩短文字,不许溢出

## 5. 转写流程(每课)

这是原教程首次转写流程；已有网页的逐章重构按 CHAPTER_STANDARD 第 8 节执行，不重复通读原教程。

1. `Read tutorial/lessonNN-*.md`(**仅此一次**)
2. 对照运行中的 ES 实验验证可疑论断 → 需要时单文件核对源码
3. 写 `chapters/chNN.html`(去 stub)+ `experiments/chNN.js`
4. 更新 STATUS.md(进度表 + 勘误若有),`node tools/check.mjs` 全绿

## 6. 分期

以下为原首次转写阶段划分；当前完成状态及逐章图解重构进度以 STATUS 为准。

| 期 | 内容 | 状态 |
|---|---|---|
| P0 | 脚手架:样式/导航/进度/连接层/控制台/动画引擎/实验运行器/docker/check/三件套/index+速查表 | ✅ |
| P1 | 第一篇 ch01-05(定标杆) | ⬜ |
| P2-P6 | 第二~六篇,每篇 5 课一个可停点 | ⬜ |
| P7 | 速查表扩充、动画补漏、全站终检 | ⬜ |

## 7. 约定

- 12 个旗舰动画清单(优先级序):ch13/14 写入全路径、ch16 两阶段搜索、ch15 路由公式、
  ch10 realtime GET、ch22 选举时序、ch23 分片均衡、ch24 peer recovery、ch08 线程池背压、
  ch20 BM25 演算、ch03 启动时序、ch25 熔断水位、ch11 动态映射推断
- localStorage keys:`es-web:theme` / `es-web:read` / `es-web:endpoint` / `es-web:history`
- 深链:`console.html?ep=&am=anon|elastic|wrong|alice&raw=1#run=METHOD|PATH|BODY`(各段独立 encodeURIComponent)。`am` 是实验别名,口令不进 URL;凭据只活在控制台当页内存。由 `ESClient.consoleLink` 生成
