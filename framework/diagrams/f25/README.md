# F25 · 住宿晚与逐晚核对

nights解释o01的两晚、离店边界与o02缺晚；verify解释ES摘要→Java完整性检查→同offer逐晚核对→结论。实线是数据处理关系，虚线是对照或适用范围，不承诺请求时延或并发先后。静态图，未实现播放器。

官方D2 v0.9.0 / dagre / 浅色4、深色201。只编辑.d2，再运行[生成脚本](../../../docs/framework-review/20261026-f25-stay/generate-diagrams.py)。[命令、退出码与SHA256](generation.json)，未手改SVG。

```bash
/path/to/d2 fmt --check framework/diagrams/f25/nights.d2
/path/to/d2 validate framework/diagrams/f25/nights.d2
/path/to/d2 --layout=dagre --theme=4 --pad=24 framework/diagrams/f25/nights.d2 framework/diagrams/f25/nights-light.svg
/path/to/d2 --layout=dagre --theme=201 --pad=24 framework/diagrams/f25/nights.d2 framework/diagrams/f25/nights-dark.svg
```

verify执行相同命令，预生成产物离线交付。依据：[官方导出](https://d2lang.com/tour/exports/)、[主题](https://d2lang.com/tour/themes/)。图生成、阅读/实际视觉与ES/Java执行分别记录于[验收入口](../../../docs/framework-review/20261026-f25-stay/README.md)。
