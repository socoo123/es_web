# F45 交付验收

范围：[F45正文](../../../framework/f45.html)、本课独立数据/DSL/SQL/Java/CDC/双节点配置、两幅静态D2，以及必要目录、前课导航与进度摘要。没有批量实施其他课，也没有重新认定F04–F06历史待验收项。

[本机运行记录](../../../projects/travel-search/review/f45/README.md)分别登记构建、ES、主副分片、PG/Kafka/Connect、故障恢复、重做与真实观察窗。图解生成和HTTP阅读不能代替这些实测。

页面验收与截图实际查看结果在本目录保存。图解使用D2v0.9.0/dagre/themes4+201/pad24，[生成命令与哈希](../../../framework/diagrams/f45/generation.json)保留2图源/4SVG，静态图不承诺动画。五个[固定v9.4.0源码文件](sources.json)HTTP200、与本地目标文件字节一致，只读当前问题相关位置，没有通读源码。

推理偏好按AGENTS保留xhigh，逐课提示词记录较新的gpt-6.1-sol/max。当前会话入口没有模型/强度设置或自行读回接口，无法确认实际配置；没有声称提示词改变运行配置，也没有启动子代理。作者自行完成写作与内容自审，实际限制单列记录。

独立任务与答案层次：TASK和SUBMISSION先给需求/证据，参考DSL/酒店结果/恢复步骤折叠；run是参考实现复现，不代表读者已独立完成。明确区分旧F07观察窗5→4条与新增DSL2→1条，酒店为两晚固定快照。本轮冻结唯一来源写入者后验收，不以Kafka末端冒充持续并发fence，不以双节点green推断可承受任意单节点故障。

正式两轮[结果与数量](results.json)均通过；[初次HTTP阅读](reading.json)覆盖1920/1440/1024/768/390/320×浅深12组合、880px/390下362px/边界差≤1/零整页溢出、19段真实复制与既有控件。最终新增逐晚候选片段后20段源文件一致性另检查，[参考区展开补验](supplement.json)覆盖1440浅色/320深色、全部折叠打开和两张结果表左右滚动。用[reading.py](reading.py)/[supplement.py](supplement.py)复现；原临时venv跨日后丢失pyvenv.cfg，补验使用新本机venv的Playwright1.64.1，浏览器Chromium156.0.8078.4，未安装测试工具到项目依赖。

[实际查看](visual-review.json)明确列出8张教程/图解＋2张真实观察窗截图，其他截图只作为生成证据，不冒称逐张审阅。[内容自审](content-review.json)、[图与代码数量](inventory.json)、[推理限制](reasoning.json)和[最终资源](workspace-state.json)分列；F45六端口关闭，五容器已停/网络已移除，四具名卷保留，原9201安全节点仍running/healthy。当前提交与GitHub发布核对在实际推送后记录。
