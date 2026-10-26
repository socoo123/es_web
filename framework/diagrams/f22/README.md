# F22 图源与生成

cycle解释怎样分开调整与留出；metrics解释相关等级怎样形成两个指标。cycle箭头为评估设计依赖；metrics箭头为阅读顺序，两个指标独立计算，省略ES内部执行、标注协商与线上实验。静态图不承诺动画。

官方D2 v0.9.0、dagre、主题4/201；离线SVG随课交付。源文件改后重新生成，不编辑SVG。[实际生成收据与哈希](generation.json)。

```bash
/path/to/d2 fmt --check framework/diagrams/f22/cycle.d2
/path/to/d2 validate framework/diagrams/f22/cycle.d2
/path/to/d2 --layout=dagre --theme=4 --pad=24 framework/diagrams/f22/cycle.d2 framework/diagrams/f22/cycle-light.svg
/path/to/d2 --layout=dagre --theme=201 --pad=24 framework/diagrams/f22/cycle.d2 framework/diagrams/f22/cycle-dark.svg
```

metrics同样运行。实际记录还包含fmt；图解生成、HTTP/截图、ES/Java验收分列。[官方导出](https://d2lang.com/tour/exports/)、[主题](https://d2lang.com/tour/themes/)。
