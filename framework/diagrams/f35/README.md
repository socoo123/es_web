# F35 静态 D2

`three-checks.d2` 解释TLS、认证、授权各自的失败；`privilege-boundaries.d2` 解释浏览器/Java/ES和读/写/管理职责。图是本课概念归纳，卡片布局不表达耗时或物理隔离，均无动画播放器。

官方D2 v0.9.0、dagre布局，light=4、dark=201；图源/命令/版本/CLI与全部产物SHA-256见[generation.json](generation.json)。只改D2源后重新fmt、fmt --check、validate并导出；没有手改SVG。正文复用course.js同步主题与展开链接。

```bash
d2 fmt framework/diagrams/f35/three-checks.d2
d2 fmt --check framework/diagrams/f35/three-checks.d2
d2 validate framework/diagrams/f35/three-checks.d2
d2 --layout=dagre --theme=4 --pad=24 --timeout=30 framework/diagrams/f35/three-checks.d2 framework/diagrams/f35/three-checks-light.svg
d2 --layout=dagre --theme=201 --pad=24 --timeout=30 framework/diagrams/f35/three-checks.d2 framework/diagrams/f35/three-checks-dark.svg
```

另一图同样处理。首次源文件中的裸换行被CLI拒绝，修正为转义换行后重新生成，最终检查记录全绿。HTTP/实际视觉/ES与Java实测分别记录，不互相替代；本课不采用Archify，不冒称通过其门禁。
