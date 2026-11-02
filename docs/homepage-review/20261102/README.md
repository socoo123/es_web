# 首页上下分区改版验收

范围：`index.html`、仅首页加载的`assets/css/home.css`与进度/验收记录。框架篇45课按八阶段置于上方，源码篇30课完整目录置于下方；课程正文和公共脚本未修改。

[浏览器记录](validation.json)来自本机Chromium156.0.8078.4与临时HTTP服务，使用`/es_web/`前缀验证Pages相对路径。覆盖1440/768/390/320px×浅深8组合：两部分同为最大880px内容列，390px下362px，所有组合无整页横向溢出。

已验证阶段入口、F01/F45、源码第1课与页内跳转；首页全部不同链接的本地文件/目标锚点存在。主题切换后刷新仍保留；预置`ch01/ch30/f45`已读时源码计数为`2 / 30`、2张已读卡，保持原有localStorage协议。键盘焦点、减少动态效果及`file://`离线样式通过。无浏览器JS异常、HTTP错误；未运行ES/Java/CDC，首页布局改版不涉及这些实验。

实际查看以下5张截图，确认标题、卡片、分区层级与深色/手机排版可读：

- [桌面首页](screenshots/1440-light-opening.png)
- [框架篇八阶段](screenshots/1440-light-framework.png)
- [桌面源码区](screenshots/1440-light-source.png)
- [手机深色首页](screenshots/390-dark-opening.png)
- [手机深色源码区](screenshots/390-dark-source.png)

`node tools/check.mjs`、`git diff --check`通过。浏览器自动检查覆盖上述8组合，实际截图审阅仅为这里列出的5张。
