# F23 · 业务身份与更新范围图源

boundaries解释酒店、房型与报价三层身份；updates比较o101改价与h01更名的不同更新范围。实线表示业务归属/模型对照，虚线表示对照阅读，不是请求先后；省略副本、merge、同步链路和未展开数据。静态图不承诺动画。

官方D2 v0.9.0 / dagre / 浅色主题4、深色201。只改.d2源文件，正式CLI重新生成SVG；离线资产随课交付，未手改SVG。[实际命令、退出码和SHA-256](generation.json)。

```bash
/path/to/d2 fmt --check framework/diagrams/f23/boundaries.d2
/path/to/d2 validate framework/diagrams/f23/boundaries.d2
/path/to/d2 --layout=dagre --theme=4 --pad=24 framework/diagrams/f23/boundaries.d2 framework/diagrams/f23/boundaries-light.svg
/path/to/d2 --layout=dagre --theme=201 --pad=24 framework/diagrams/f23/boundaries.d2 framework/diagrams/f23/boundaries-dark.svg
```

updates同样执行。[生成脚本](../../../docs/framework-review/20261026-f23-model/generate-diagrams.py)允许D2_BIN指向正式CLI。[官方导出](https://d2lang.com/tour/exports/)与[主题](https://d2lang.com/tour/themes/)。生成、HTTP/视觉、ES/Java实测分列；[验收入口](../../../docs/framework-review/20261026-f23-model/README.md)。
