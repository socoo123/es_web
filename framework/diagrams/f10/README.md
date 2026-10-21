# F10 静态D2图解

两幅图分别比较同候选的三种排序、缺值与过滤边界。图是教学抽象；隐形边仅用于纵向排版，不表示顺序、调用或真实ES内部阶段。无动画或播放器。

使用官方D2 v0.9.0、dagre、light=4/dark=201、pad24；[生成收据](generation.json)保留命令、CLI及图源/产物SHA256。

```bash
python3 framework/diagrams/f10/generate.py /path/to/d2
```

先修改[排序契约图源](sort-contract.d2)或[缺值边界图源](missing-boundary.d2)，再重新fmt/validate/生成，禁止手改SVG。主题由站点同步两份离线资产，保留独立展开。[阅读与视觉](../../../docs/framework-review/20261021-f10-sort/README.md)和[ES实测](../../../projects/travel-search/review/f10/README.md)分别记录。
