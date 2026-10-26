# F21 探索与修正

这些是正式验收前的实际探索，不冒充最终通过。

- `weight-zero-only/`保存最初仅weight=0兜底的完整响应：缺两项在sum仍回退1；正式实现改成weight=1的常量零函数，教学02持续复现旧反例。
- `probe-*.json`是修正后的单轮探测；正式两轮在工程review/f21。
- 初次Java写文件命令工作目录错误，未生成目标文件，构建的旧工程未算本课通过；修正绝对根路径后重新实现。
- 初次脚本source参数按旧API字符串编写，Client9.4.8需要ScriptSource.scriptString；失败构建保留日志，修正后clean package与最终jar实连两轮。
- ES映射响应省略默认date format；首次完整字面比较失败后改按有效配置比较。radius DSL统一10.0km，与Java保持相同字符串。
- 旧浏览器venv缺少可导入模块，改用现有完整es-f16-browser环境；未降低浏览器检查。
- 图初次按全文宽度放大过高，最终按420px上限居中，保留320px内完整可读图；相关HTTP矩阵重新运行。

最终收据独立保存，不修改检查器或伪造响应。

- 视觉自审发现非距离模式的distanceKm=null容易被误读成缺坐标；最终窗口分别提示未选择距离排序/缺坐标，DTO仅距离模式填数值。重建最终jar后重跑两轮、观察窗与相关阅读/截图验证。

- 最终语法门禁发现Docker逐行JSON基线误用.json扩展名（Extra data），已改为.jsonl并按逐行JSON检查；未放宽JSON解析。
