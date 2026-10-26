# F21 · D2 图源与生成

两幅静态规则图，箭头表示阅读依赖，不表示ES内部执行顺序；省略数据采集、并发与内部调度。不承诺动画，无播放器。

- `decay.d2` → `decay-light.svg` / `decay-dark.svg`：衰减、缺值、score_mode与boost_mode。
- `intent.d2` → `intent-light.svg` / `intent-dark.svg`：硬资格、文本与用户排序意图。

官方D2 v0.9.0，dagre，主题4/201。CLI来源沿用仓库已验证缓存；实际版本/命令/哈希见[generation.json](generation.json)。只改D2源，再用官方CLI生成，不手改SVG。

```bash
d2 fmt decay.d2
d2 fmt --check decay.d2
d2 validate decay.d2
d2 --layout=dagre --theme=4 --pad=24 --timeout=30 decay.d2 decay-light.svg
d2 --layout=dagre --theme=201 --pad=24 --timeout=30 decay.d2 decay-dark.svg
# intent.d2同样处理
```

[正文](../../f21.html) · [HTTP与实际视觉审阅](../../../docs/framework-review/20261026-f21-decay/README.md)；图生成、HTTP、视觉、真实ES分别记录。
