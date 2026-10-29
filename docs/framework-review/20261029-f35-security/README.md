# F35 内容、图解与阅读验收

本轮仅F35，必要的F34下一课链接/目录/进度摘要与共享Java连接配置同步。F07正文与代码保持原教学基线，仅将片段来源改到F35保留的原配置快照，避免把本课TLS实现提前塞进F07；快照字节等于本轮前HEAD的配置文件。模型/推理入口限制见reasoning.json；作者自审，不称独立内容审阅。最新逐课提示词偏好gpt-6.1-sol/max，入口无法切换或自行读回；此前xhigh要求保留。

真实ES/Java/浏览器见[执行证据](../../../projects/travel-search/review/f35/README.md)。官方固定v9.4.0定向源码核对见sources.json；官方API/Java文档在正文逐项链接。图源、CLI及检查哈希见[图解目录](../../../framework/diagrams/f35/generation.json)，本课两幅静态D2，没有Archify门禁或机制播放器。

reading-review.py检查带`/es_web/`前缀的HTTP页面、6种宽度×浅深、880px阅读列、局部滚动、图解同步/展开、全部实际剪贴板复制、折叠题、导航/独立已读进度，以及file/reduced-motion/键盘焦点；http-review.json记录实际结果。截图必须实际查看后才在visual-review.json中标记通过，不能把生成截图当作视觉审阅。

内容自审逐项核对业务问题→定义与因果→固定样本→REST→Java→允许/拒绝→轮换恢复→清理与边界，并与两轮输出、工程片段保持一致。结构/片段/语法检查与构建、真实ES、HTTP、图生成、实际视觉分别记录。

实际结果：HTTP/file与补充点击检查通过；17代码块复制、12折叠；11联系页覆盖122原图及3张单图已实际查看。两轮与手工路径、构建/资源/六项配置拒绝、清理及原节点不变由content-review.json逐项核对。
