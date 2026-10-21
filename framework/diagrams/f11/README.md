# F11 静态D2图解

两幅图分别解释页间改价导致重漏、PIT分页的生命周期。实线说明受控顺序/成功阶段；独立PIT/失效卡片靠隐形边纵向排版，不表示转换、必然先后或ES内部实现。无动画播放器。

官方D2 v0.9.0 / dagre / light=4、dark=201 / pad24。先改[分页视图图源](page-window.d2)或[游标生命周期图源](cursor-life.d2)，再fmt/validate/生成，禁止手改SVG。

```bash
python3 framework/diagrams/f11/generate.py /path/to/d2
```

[生成收据](generation.json)保存版本、命令、CLI/图源/产物SHA256。双主题离线资产由站点同步；[阅读与视觉](../../../docs/framework-review/20261021-f11-pagination/README.md)、[真实ES](../../../projects/travel-search/review/f11/README.md)分别记录。
