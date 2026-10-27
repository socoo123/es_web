# F26 图解

两幅图：`collapse.d2`解释匹配报价→酒店代表→组内范围；`scope.d2`解释前2条报价、前2家酒店、完整候选的两晚价格差别。箭头表示筛选或扩大集合，虚线表示遗漏反例；静态概念图，不表示库存事务。

D2 v0.9.0、dagre，浅色主题4、深色201。保留图源与4份SVG，SVG只由官方CLI生成。命令/二进制与产物SHA-256见[generation.json](generation.json)：

```bash
D2_BIN=/path/to/d2 python3 docs/framework-review/20261027-f26-collapse/generate-diagrams.py
```

从仓库根目录运行；fmt、fmt --check、validate和导出实际结果与HTTP/视觉阅读、ES实验分别记录。没有机制播放器或动画控制需要验收；主题由站点替换浅深资产，提供独立展开入口。
