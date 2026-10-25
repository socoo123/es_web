# F18 · 两幅评分图

[factors.d2](factors.d2)以独立竖卡比较词频、长度和稀有度；隐形边只排版，无时间含义。[corpus.d2](corpus.d2)按追加、refresh、重搜的实际观察顺序连接；不表现segment、删除统计或多分片执行。全部数字来自本课固定初始/追加语料。

官方D2 v0.9.0，dagre，主题4（浅）与201（深），pad24。两个源生成四个SVG，不手改产物。[生成命令/检查/CLI及文件哈希](generation.json)，[生成脚本](../../../docs/framework-review/20261025-f18-bm25/generate-diagrams.py)。示例：

```bash
d2 fmt --check framework/diagrams/f18/factors.d2
d2 validate framework/diagrams/f18/factors.d2
d2 --layout=dagre --theme=4 --pad=24 --timeout=30 framework/diagrams/f18/factors.d2 framework/diagrams/f18/factors-light.svg
```

再生成dark/201与corpus两主题，完整命令以generation.json为准。无Archify、iframe或播放器；主题与展开使用现有course.js。最大540px图宽受880px阅读列约束；手机不靠横向滚动阅读图。图源生成、HTTP与实际视觉审阅分别记录在[本轮验收](../../../docs/framework-review/20261025-f18-bm25/README.md)。
