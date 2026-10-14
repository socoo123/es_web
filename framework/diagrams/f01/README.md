# F01 · 从空索引到一次命中

[图源](first-search.d2) / [浅色](first-search-light.svg) / [深色](first-search-dark.svg)。箭头只表示本课手工操作顺序，不声称是 ES 内部调用图。静态图无需动画控件。

使用官方 [D2 v0.9.0](https://github.com/d2lang/d2/releases/tag/v0.9.0)，ELK 布局，主题 4 / 201。从仓库根目录重新生成，禁止手改 SVG：

```bash
d2 fmt --check framework/diagrams/f01/first-search.d2
d2 validate framework/diagrams/f01/first-search.d2
d2 --layout=elk --theme=4 --pad=24 framework/diagrams/f01/first-search.d2 framework/diagrams/f01/first-search-light.svg
d2 --layout=elk --theme=201 --pad=24 framework/diagrams/f01/first-search.d2 framework/diagrams/f01/first-search-dark.svg
```

作者 CLI 来自官方 macOS arm64 release；下载包 SHA-256 `eaf6c0c143e56dd9fa97bfb6df25ea9c1ebce40245f056a0768cf1a6c15d3064`。字体许可复用仓库内 [Source Sans / SIL OFL](../../../docs/framework-diagrams/SOURCE-SANS-LICENSE.txt)。阅读时无需安装 D2 或访问 CDN。

格式/语法/双主题生成通过；当前图源/产物 SHA-256 见 [生成记录](generation.json)。本图直接以 SVG 嵌入课程，主题开关更换对应资产，手机图框局部滚动并提供展开入口。HTTP、复制/主题/进度与实际截图审阅见[本课验收](../../../projects/travel-search/review/f01/README.md)。没有采用 Archify，不计其原生门禁。
