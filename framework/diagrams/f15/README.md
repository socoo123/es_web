# F15 静态D2图解

[词典到重建](lifecycle.d2)箭头表示本课操作先后，不表示重启会改写旧资料。[召回取舍](tradeoffs.d2)为独立的三种状态，隐形边只用于排版。字段、ID、意图与正文/固定样本一致，省略插件内部歧义处理、倒排实现和在线迁移。

官方D2 v0.9.0 / dagre / 浅色4、深色201 / pad24。只改图源再生成，不手改SVG：

```bash
python3 framework/diagrams/f15/generate.py /path/to/d2
```

[生成收据](generation.json)记录实际版本、命令与CLI/图源/产物哈希。离线双主题静态图，可展开；无播放器。[HTTP/视觉](../../../docs/framework-review/20261024-f15-dictionary/README.md)与真实ES/Java分别验收。
