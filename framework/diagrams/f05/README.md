# F05 静态图解

两幅图分别回答字段/查询如何共同决定命中，以及 AND 与短语位置约束有何不同。所有命中集合均为固定语料和源码推导的预测，真实 ES 状态见 [执行记录](../../../projects/travel-search/review/f05/README.md)。箭头为阅读与对照顺序，省略线程、分片、评分实现；无动画或播放器。

- [字段与查询图源](field-query.d2)
- [短语位置图源](phrase-position.d2)
- [生成命令、版本与哈希](generation.json)

官方 [D2 v0.9.0](https://github.com/terrastruct/d2/releases/tag/v0.9.0)，内置 dagre，浅色主题 4、深色主题 201，pad=24。安装该版本 CLI 后，从仓库根目录执行：

```bash
python3 framework/diagrams/f05/generate.py /path/to/d2
```

只改 `.d2` 图源，先 `d2 fmt`，再执行生成脚本的 fmt --check / validate / 双主题导出；不手改 SVG。页面同步浅深资产并提供展开入口。D2 内嵌 Source Sans Pro 字体许可沿用 [现有许可](../../../docs/framework-diagrams/SOURCE-SANS-LICENSE.txt)。图源生成与 [HTTP/实际截图审阅](../../../docs/framework-review/20261015-f05-keywords/README.md) 分别记录。本课不使用 Archify。
