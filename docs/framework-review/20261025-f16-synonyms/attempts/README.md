# F16 · 探索与失败修正

- [probe.json](probe.json)：固定意图后、正式两轮前的样本/分析/管理集重载探索；[点名恢复](probe-cleanup.jsonl)。用于选择可解释边界，不声称盲评。
- [默认mapping序列化](default-mapping-serialization.jsonl)：ES省略相等search_analyzer与默认gap=100；核对有效配置时补回这两个已声明默认值，没有改掉服务端前提。
- [裁剪属性的Java503](analyze-client-missing-bytes.jsonl)、[实际bytes必填栈](analyze-client-missing-bytes.log)、[继续缺termFrequency栈](analyze-client-missing-termfrequency.log)：详细分析仅请求positionLength导致9.4.8客户端解析ES200失败。最终explain=true保留完整详细属性，未关闭客户端必填检查；两轮与观察窗使用最终jar。
- [请求路径序列化](request-body-path-serialization.jsonl)：初始验收错误地要求index出现在body；官方客户端将它作为路径参数。本课REST重放显式点名固定索引，并比较完整body；没有放宽任意索引访问。

- [片段转义检查](fragment-escaping-check.log)：初次HTML生成把引号也编码，现有同步器要求只转义&/尖括号；通过官方tools/sync-framework-code.mjs同步，未修改检查器。
- [初始默认值](shell-initial-defaults.json)、[隐藏details的innerText](shell-hidden-details-innertext.json)：验收脚本误把“默认值未变”当input变化，又用innerText读取关闭折叠区而得到空字符串；改为真实改变输入、读取textContent。产品清空逻辑未变，最终12组通过。
- [图解优化前HTTP](http-before-diagram-refinement.json)与[390浅色旧图](choices-before-390-light.png)：视觉审阅发现长标签缩小过多，缩短D2源标签后官方CLI重新生成，并重跑图解与阅读验证；不手改SVG。

- [主题过渡中的表格](table-during-theme-transition.png)：点击主题后立即截图捕获到CSS过渡色；table-recheck.py只重拍8张静态表，加载前固定主题，不重复ES/Java实验。原始6次错误/恢复API记录保留。

- 浏览器使用独立/tmp/es-f16-browser环境：旧F07临时环境没有可导入的Playwright；实际安装Playwright1.64.1并使用本机缓存Chromium，版本以HTTP/观察窗收据为准。未把旧环境当作本轮通过证据。

- [原始构建日志](raw-build-logs.json)：暂存后Git发现Maven空日志行尾空格与Docker CR进度。保留逐字节UTF-8原文及哈希，再将提交文本去尾空格/CR分行；运行、制品与结论未变，runtime记录提交日志的新哈希。
