# F09 · 聚合范围与候选误差

- facet-scopes.d2：共同候选、结果、忽略自身维度的城市/主题范围。四张卡片分别写明集合约束；无可见箭头，隐形边只控制纵向排布，无实现时序含义。
- terms-candidates.d2：同节点双主分片的固定单标签分布；三次独立请求的候选宽度与最终桶数对照。省略并行收集与归并内部实现。

均为静态教学图，带浅深主题及展开入口，无机制播放器。数字对应[本课](../../f09.html)的固定数据与[实际ES记录](../../../projects/travel-search/review/f09/README.md)。

官方 D2 v0.9.0 / dagre / 浅色4、深色201 / pad24。可复现：

```bash
python3 framework/diagrams/f09/generate.py /path/to/d2
```

[生成收据](generation.json)保存CLI哈希、fmt/validate/导出命令及源/产物哈希。只改.d2后重新生成，不手改SVG。HTTP/实际截图查看另记在[阅读验收](../../../docs/framework-review/20261020-f09-facets/README.md)。
