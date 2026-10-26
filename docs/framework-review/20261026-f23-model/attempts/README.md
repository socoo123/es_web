# F23 · 探索与修正保留

本目录保存开发中实际失败，正式两轮在[工程验收](../../../../projects/travel-search/review/f23/README.md)。不把这些中断流程记为正式通过。

- exploration：首次把_stats/docs误读成顶层primaries，实际是_all.primaries；后续命令在前提未建完时继续失败，原始日志保留。
- exploration-retry：GET mapping省略显式type=object；修正为只归一化这一项，其他属性仍完整比较。
- exploration-final：先单条恢复o101却未refresh，随后update_by_query读旧版本，HTTP409，updated=3/version_conflicts=1。API没有自动回滚三条成功项。
- exploration-recovered：恢复流程增加_refresh，点名清理后38＋14＋28主流程通过；此时未作为最终jar两轮验收。
- first-final-round：最终jar第一轮在Java比对处中断：官方typed response重序列化省略null的hits.max_score与hit._score。ID、源文档、sort、total一致；只归一化这两处表示差别，原_source的null仍严格检查。修正后正式round1/round2完整重跑。
- diagram-initial：320px更新图标签偏密，保留原D2/生成收据/SVG/截图；缩短源标签后官方CLI重新生成，最终HTTP全矩阵复验，并重新实际打开受影响总览与原图。
- http-initial.json：改图前首次HTTP通过收据；最终[http-review.json](../http-review.json)对应当前图源/资产。最初临时页面生成脚本在本机Python编码探测报错，加显式UTF-8声明后正常；HTML转义与同步器对引号表达不同也已修正，只改本课片段，不改检查器。

[archive.json](archive.json)记录原始JSONL压缩文件与原始/压缩SHA-256；gzip原样保存内容。正文、预期与最终脚本保持一致，没有把失败隐藏或把未测性能写成结论。

最终检查收据的早期执行还遇到两处工具问题：自审JSON的自由文本status先改为统一的passed＋独立范围字段；系统Python缺Playwright，最终在已记录的既有浏览器venv运行checks.py。没有修改站点检查器或跳过真实实验。
