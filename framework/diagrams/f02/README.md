# F02 · 数据到结果与搜索可见性

两幅静态 D2 图解释人工推演，不代表真实 ES 执行流程、默认中文分词或 BM25。使用官方 [D2 v0.9.0](https://github.com/d2lang/d2/releases/tag/v0.9.0)、TALA、主题 4 / 201，预生成浅深 SVG，离线阅读不依赖 CDN。

| 图 | 图源 | 浅 / 深 | 箭头和范围 |
| --- | --- | --- | --- |
| 数据与查询在哪里相遇 | [search-path.d2](search-path.d2) | [浅](search-path-light.svg) / [深](search-path-dark.svg) | 自上而下表示字段处理、按词项找候选、过滤、排序的手算逻辑顺序；实际 ES 可交织过滤与文本匹配，省略内部实现 |
| 同一更新何时对搜索可见 | [visibility.d2](visibility.d2) | [浅](visibility-light.svg) / [深](visibility-dark.svg) | 表示改价前、写入确认、相关更新可搜索三个状态；单次更新无并发，下一次普通搜索，无数据库同步或 PIT；不承诺固定时间 |

[生成记录与产物 SHA-256](generation.json)，[正文与 HTTP 阅读验收](../../../docs/framework-review/20261014-f02-model/README.md)分别记录。只编辑图源后重新生成，未手改 SVG。站点主题开关同步图片和展开链接；静态图无播放控制。图中文字也在正文表格与解释中可读。

在仓库根目录可以用 `python framework/diagrams/f02/generate.py /path/to/d2` 重新生成并记录哈希。使用 d2 v0.9.0，每个源执行：

```bash
d2 fmt --check framework/diagrams/f02/search-path.d2
d2 validate framework/diagrams/f02/search-path.d2
d2 --layout=tala --theme=4 --pad=24 --timeout=30 framework/diagrams/f02/search-path.d2 framework/diagrams/f02/search-path-light.svg
d2 --layout=tala --theme=201 --pad=24 --timeout=30 framework/diagrams/f02/search-path.d2 framework/diagrams/f02/search-path-dark.svg
```

第二幅将 search-path 替换为 visibility，完整命令见生成记录。字体采用 D2 默认 Source Sans 子集与浏览器中文字形回退，保留 [Source Sans / SIL OFL 许可](../../../docs/framework-diagrams/SOURCE-SANS-LICENSE.txt)。本课没有 Archify，其专属原生门禁不适用。
