# F24 · 同条目资格与价格作用域

same-entry对照h01的object错拼与单个nested；price-scope解释query、其inner_hits和独立sort.filter的职责。实线表示模型判定/匹配明细，虚线表示对照与条件复用，不是调用先后。省略分片与实现细节。静态图不承诺动画。

官方D2 v0.9.0 / dagre / 浅色4、深色201。只改.d2，再运行[生成脚本](../../../docs/framework-review/20261026-f24-nested/generate-diagrams.py)，未手改SVG。[实际命令/退出码/哈希](generation.json)。

```bash
/path/to/d2 fmt --check framework/diagrams/f24/same-entry.d2
/path/to/d2 validate framework/diagrams/f24/same-entry.d2
/path/to/d2 --layout=dagre --theme=4 --pad=24 framework/diagrams/f24/same-entry.d2 framework/diagrams/f24/same-entry-light.svg
/path/to/d2 --layout=dagre --theme=201 --pad=24 framework/diagrams/f24/same-entry.d2 framework/diagrams/f24/same-entry-dark.svg
```

price-scope同样执行。离线产物随课交付，图源与正文绑定；[官方导出](https://d2lang.com/tour/exports/)与[主题](https://d2lang.com/tour/themes/)。图生成、HTTP/视觉与真实ES分别记录于[验收入口](../../../docs/framework-review/20261026-f24-nested/README.md)。
