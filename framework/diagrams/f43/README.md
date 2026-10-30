# F43 图源与生成

两幅静态D2：一次测量的边界、逐个改变主要比较条件。箭头为实验组织顺序，观测卡内客户端与ES并行；不表示生产最优路线，也不承诺动画。

官方D2 v0.9.0、dagre、浅theme4/深theme201、pad24。当前CLI `/tmp/es-framework-d2-20261013/d2`；修改图源后重新生成，禁止手改SVG：

```bash
d2 fmt measurement.d2 compare.d2
d2 fmt --check measurement.d2 compare.d2
d2 validate measurement.d2
d2 validate compare.d2
d2 --layout=dagre --theme=4 --pad=24 measurement.d2 measurement-light.svg
d2 --layout=dagre --theme=201 --pad=24 measurement.d2 measurement-dark.svg
d2 --layout=dagre --theme=4 --pad=24 compare.d2 compare-light.svg
d2 --layout=dagre --theme=201 --pad=24 compare.d2 compare-dark.svg
```

[generation.json](generation.json)保存真实命令、版本、退出码、源与产物SHA-256。首版并行分支过宽，改图源合成观测卡并重新生成；前版哈希与命令保留在修订记录。站点双主题切换对应SVG；手机只在图内滚动并有展开入口。未采用Archify。

[HTTP/视觉](../../../docs/framework-review/20261030-f43-capacity/README.md)、[真实ES/Java](../../../projects/travel-search/review/f43/README.md)独立记录。
