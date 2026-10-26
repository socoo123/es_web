# 探索与验收脚本修正

ES/Java探索先运行21教学HTTP与29附加错误；全部通过，不计入最终round1/round2。正式两轮有各自点名清理与新收据。

静态正文生成器曾用`'{{' not in page`粗判未替换占位符，误把Java二维数组的双左花括号当占位符；在写文件前失败，改为只识别大写占位符的正则后生成成功。

观察窗首次验收用inner_text读取关闭details中的pre，浏览器返回空文本，导致JSON解码失败。实际接口成功、卡片和完成状态正常；修正为text_content核对完整原文。保留[shell-hidden-innertext.json](shell-hidden-innertext.json)及日志。

第二次验收的add_init_script在每次reload都覆盖主题存储，导致主题持久化断言失败。改为只在键不存在时写初值，产品主题逻辑未变。保留[shell-theme-init.json](shell-theme-init.json)及日志。日期400探针同时改为两个字段各自在有效范围内但入住=离店，确保请求能越过浏览器单字段约束而真实到达Java。

最终[shell-review.json](../shell-review.json)记录32矩阵场景与400/502/503恢复，共40次真实Java请求、同一PID；没有用mock响应，也没有把前两次脚本失败计为产品通过。另有一次临时Playwright诊断将内建print直接作事件处理器而报参数绑定错，改为lambda后只读页面状态确认正常；不计正式验收。

视觉补证首次Java右滚动截图用了:first-of-type，选到折叠区而等待可见性超时；改为同一源的首个可见代码段。未到ES变更阶段。保留visual-selector.json/log；最终10张补证逐张查看。

附带日志可读版仅移除末尾空白，原始字节另存同名.log.gz；提交前修正了视觉选择器日志末尾空行的git diff --check提示。
