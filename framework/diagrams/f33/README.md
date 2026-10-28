# F33 图解

两幅静态概念图：[复制与追随边界](rebuild-boundary.d2)、[切换与回滚窗口](switch-rollback.d2)。只改D2图源后用官方CLI重新生成，没有手改SVG。

- D2 v0.9.0，dagre，浅色4/深色201；CLI哈希、fmt/check/validate、4次导出命令及资产哈希见[generation.json](generation.json)。
- 在仓库根目录复现：`D2_BIN=/path/to/d2 python3 docs/framework-review/20261028-f33-reindex/generate-diagrams.py`。
- 卡片表示本课受控状态，箭头文字表示复制或入口路由，不代表全局并发顺序、耗时或生产可用性保证。
- v001/v002均省略`tut-f33-attractions-`前缀。固定资料视图不是备份Snapshot；未绘制持续CDC方案。
- 880px阅读列、双主题SVG与展开链接同步、窄屏局部滚动。0播放器，静态图不承诺动画控制。

图生成与[HTTP/实际视觉验收](../../../docs/framework-review/20261028-f33-reindex/README.md)分列，不替代[ES/Java真实实验](../../../projects/travel-search/review/f33/README.md)。
