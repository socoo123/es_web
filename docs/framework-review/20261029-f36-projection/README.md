# F36 内容、图解与阅读验收

本轮仅实施F36及必要目录/前后导航/进度。教程先讲业务事实、投影职责与稳定键，再SQL/REST/Java、关联变化、快照缺口、人工补齐和清理。真实执行与阅读分开；没有声称已交付自动CDC。

- 内容：作者逐段自审，SQL字段/整数分/ID、Java契约、图注、能力检查与实际结果相互核对；运行两轮在[review/f36](../../../projects/travel-search/review/f36/README.md)。
- 图解：两份静态D2、浅深四SVG，v0.9.0/dagre/light4/dark201；生成命令与SHA-256在[生成记录](../../../framework/diagrams/f36/generation.json)。未采用Archify或机制播放器。
- HTTP/交互与实际视觉：由reading-review.py和截图记录，最终结果见http-review.json、visual-review.json；截图生成与实际查看分开记录。
- 运行偏好：AGENTS的历史xhigh、逐课提示词最新gpt-6.1-sol/max都保留；当前入口无法设置或自行读回，不声称实际启用。没有启动子代理，内容为作者自审。

WAL/binlog/Kafka/offset/自动事件路由/持续追平等未实施项目留到F37–F42；不以图或浏览器截图代替这些实验。

HTTP实际通过1920/1440/1024/768/390/320×浅深12组合、880px边界与局部滚动、20次真实剪贴板复制、12折叠、主题/已读隔离、16独立图视图和file/reduced motion/键盘焦点；/es_web/相对路径有效，JS/HTTP错误和业务直连均0。supplement-review实际点击目录/前后课/四次主题匹配展开，并检查全部折叠打开时1440/390/320无整页溢出。实际查看8接触表覆盖94原图，另查看4张原图（含独立浅/深图、真实390px最终卡片及补充Java阅读图）；视觉记录未以截图生成冒称已审阅。

最终仓库门禁、语法与片段一致性见checks.json；作者自审清单见content-review.json，运行与停止见projects/travel-search/review/f36。实验进程已停止，读者按手工入口自己启动。
