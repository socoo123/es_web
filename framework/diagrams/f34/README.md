# F34 图解

两幅静态 D2：副本与历史备份的边界；仓库、快照终态、隔离恢复三道检查。不使用机制播放器，不承诺动画。

图源是本目录的 `.d2`；浅色主题4、深色201，官方D2 v0.9.0、dagre、pad24。不能手改SVG。执行仓库内的生成脚本（用 `D2_BIN` 指定已安装的官方CLI）：

```bash
D2_BIN=/path/to/d2 python3 docs/framework-review/20261028-f34-snapshot/generate-diagrams.py
```

[生成收据](generation.json)记录版本、CLI和图源/产物SHA-256、fmt/check/validate及导出命令。HTTP双主题/实际视觉验收另见[阅读记录](../../../docs/framework-review/20261028-f34-snapshot/README.md)。图为受控实验的概念归纳，不代表时间比例、物理隔离或恢复时限。
