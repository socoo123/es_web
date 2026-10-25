# F16 · 别名与同义词图解

[三种改法](choices.d2)是三个独立方案与共同边界，隐形边只排版。[实际词图](graph.d2)来自ES9.4.0对PALACE museum的详细分析：每个token从position指向position+positionLength，边不是时间先后；同义词分支是可选路径，不是全部词同时必需。省略倒排/评分与多个字段合并。

官方D2 v0.9.0 / dagre / 浅色4、深色201 / pad24。只改D2源，再生成SVG：

```bash
python3 framework/diagrams/f16/generate.py /path/to/d2
```

[生成收据](generation.json)记录版本、命令、CLI/源/产物SHA256；[HTTP/视觉](../../../docs/framework-review/20261025-f16-synonyms/README.md)与真实ES/Java分列。静态图无播放器，离线可读，提供主题同步与展开入口。
