# F13 静态D2图解

[分析链图源](analyzer.d2)表示原字符流经字符过滤、分词与词项过滤的变换；箭头表示该输入的分析过程。[召回图源](recall.d2)比较失配、AND、短语三种查询；实线表示索引/查询词项比较，隐形边只排版，各模式不是ES内部依次执行的流程。范围为固定八份语料、BJ/open/CNY/0–10000分，省略底层倒排实现、评分与插件。

官方D2 v0.9.0 / dagre / 浅色4、深色201 / pad24。只改源，再生成：

```bash
python3 framework/diagrams/f13/generate.py /path/to/d2
```

[生成收据](generation.json)含版本、命令与CLI/图源/产物SHA256。预生成离线双主题SVG，提供展开入口，不承诺动画；未使用Archify或机制播放器。HTTP/视觉与真实ES/Java分别记录在[本轮验收](../../../docs/framework-review/20261023-f13-analysis/README.md)。
