# F14 静态D2图解

[受控比较源](comparison.d2)的箭头表示固定数据到独立方案、相同查询与人工判断的实验步骤，五种方案互不串联。[召回取舍源](tradeoffs.d2)是三张独立比较卡，隐形边只排版；卡内箭头表示输入分析。均省略底层倒排、评分与性能。

官方D2 v0.9.0 / dagre / 浅色4、深色201 / pad24。只改源后重新生成，不改SVG：

```bash
python3 framework/diagrams/f14/generate.py /path/to/d2
```

[生成收据](generation.json)记录版本、命令与CLI/图源/产物哈希。离线双主题SVG，静态图不承诺动画。HTTP/视觉在[本轮验收](../../../docs/framework-review/20261024-f14-analyzers/README.md)，插件/真实ES/Java另记。
