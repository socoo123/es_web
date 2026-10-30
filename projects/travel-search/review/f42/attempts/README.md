# 预验收与失败

- start-before-json-ready.log：Connect启动窗口返回非JSON；等待器新增JSONDecodeError重试，start-02成功。
- run-01-id-order.log / run-01目录：最初把F07 ID升序误断言成价格序，初始观察失败；修正期望为ID序。
- run-02-summary-path.log / run-02目录：三案例已到最终状态，但汇总序列化Path失败；worker命令参数统一字符串。
- 每次失败后先点名cleanup再运行；正式完整通过只有同一最终逻辑的run-03、run-04。没有把部分记录算成正式一轮。

两次编辑脚本工作目录写错只报FileNotFoundError，没有落盘变更或链路操作。正文图初稿过宽、lazy图片妨碍整页加载检查也按实际阅读结果修正，记录在独立阅读验收attempts目录。
