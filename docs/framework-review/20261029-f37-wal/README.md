# F37 · 内容、图解与HTTP阅读验收

本目录只覆盖F37及其必要目录/前课下一课链接。真实CDC/Java/ES两轮记录在[review/f37](../../../projects/travel-search/review/f37/README.md)，不以阅读测试替代。

- 内容作者自审、教学依据和代码片段对应关系见content-review.json；没有独立代理审阅。
- 图解源/CLI版本/完整命令/SHA-256见[图解生成记录](../../../framework/diagrams/f37/generation.json)，两幅静态D2及四份双主题SVG，无Archify/机制播放器。
- reading-review.py运行本机HTTP的/es_web/前缀与file路径，检查六种嵌入宽度/双主题、独立SVG四种桌面宽度/双主题、复制、折叠、锚点、导航、阅读进度、主题切换与减少动态效果；实际结果在http-review.json。
- observe-shell.py是作者附加验证，真实浏览器只访问Java搜索服务，五阶段各1440/390px与双主题；原始请求、REST重放与截图存于每轮运行目录。
- 实际查看的图片范围与结论在visual-review.json；截图生成不等于已审阅。
- 当前根入口无法设置或自行读回提示词最新gpt-6.1-sol/max，也无法确认此前xhigh；不声称已启用。事实记录见reasoning.json。

最终仓库/片段/语法、两轮收据、图源hash、实际凭据排除及定向清理检查见[checks.json](checks.json)，当前文本制品hash见[delivery-artifacts.json](delivery-artifacts.json)。

本课业务边界保持单表、固定主键、单分区与单消费者；MySQL、多表和乱序保护均未实施。构建、CDC、展示壳、图解生成、HTTP与视觉分别记录。
