# F13 初查与修正

- `chain-mapping-default.log`：作者初次把序列化mapping与输入逐字比较。ES省略与索引analyzer相同的search_analyzer；脚本改为比较有效回退，未改ES配置。
- `chain-emoji-expectation.log`：作者初次以为😀不成token，实际ES9.4.0保留😀且占两个UTF16单位；修正断言与正文，并重跑两轮。
- D2初次把已存在的二进制路径误当目录，命令报NotADirectoryError；改为真实CLI路径，fmt/validate/四SVG重新生成通过。未改产物绕过。
- `http-before-code-controls.json`/`.log`：两个分析输入的Text块缺复制控件，复制验证还使用了所有pre而非code-block对应索引。补控件并约束选择器；最终12组阅读与22段真实剪贴板通过。
- `shell-hidden-pre-check.json`：验收脚本对折叠区pre用inner_text导致空值误判；改用text_content读取保存的JSON，不改应用绕过。完整重跑12组与400/502/实际停机503/恢复通过。

失败证据保留，不将旧失败标成通过。最后独立内容审阅没有阻断问题，两个非阻断建议补充白名单来源与精确输入边界，由四组最终段落HTTP/截图补验；既有ES/Java输入与执行代码未因建议改变。

首次暂存后git diff --cached --check发现作者初稿Markdown硬换行和Maven原始日志空白行带尾空格；仅去除尾空白，正文/构建输出文本不变，原始与保存后哈希分别记在reasoning/runtime收据。补入暂存区差异检查，最终通过。
