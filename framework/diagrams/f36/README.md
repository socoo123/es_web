# F36 静态 D2

source-projection解释三张业务表如何组装一景点一份投影与Java导入边界；snapshot-gap解释真实两会话实验的读视图、后续提交和人工补齐。箭头分别表示数据流/本课实验先后，不表示耗时。均为静态图，不承诺暂停或重播。

官方D2 v0.9.0，dagre，浅色4/深色201。修改.d2后重新fmt、fmt --check、validate与生成SVG；没有手改SVG。命令、版本、CLI及图源/产物SHA-256见[generation.json](generation.json)。

```bash
d2 fmt framework/diagrams/f36/source-projection.d2
d2 fmt --check framework/diagrams/f36/source-projection.d2
d2 validate framework/diagrams/f36/source-projection.d2
d2 --layout=dagre --theme=4 --pad=24 --timeout=30 framework/diagrams/f36/source-projection.d2 framework/diagrams/f36/source-projection-light.svg
d2 --layout=dagre --theme=201 --pad=24 --timeout=30 framework/diagrams/f36/source-projection.d2 framework/diagrams/f36/source-projection-dark.svg
```

snapshot-gap同样处理。正文由course.js同步主题与展开目标；窄屏图内可横向滚动/展开。图生成、HTTP与实际视觉、SQL/ES/Java运行分别验收，不互相替代。本课未采用Archify。
