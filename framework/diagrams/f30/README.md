# F30 D2 图源与双主题产物

- `two-decisions.d2`：固定三票的多数/少数与数据可达分别观察。m3是master/data/ingest混合节点。
- `shard-recovery.d2`：实际主片停机、提升、原卷回归、全部数据离线和再次恢复。
- 官方D2 v0.9.0，dagre；浅色主题4、深色201，pad24。静态图，无动画或播放器承诺。
- 生成入口：`python3 docs/framework-review/20261028-f30-failover/generate-diagrams.py`；`D2_BIN`可指定同版本CLI。每次修改D2后执行fmt、fmt --check、validate及四次导出，不手改SVG。
- 命令、退出状态、CLI及所有图源/产物SHA-256见[generation.json](generation.json)。
- 图解抽象故障条件，不是网络抓包。m1/m2专用master，m3兼data，d1仅data；投票与分片角色分别解释。
- 真实HTTP/视觉证据及范围见[本课阅读验收](../../../docs/framework-review/20261028-f30-failover/README.md)，真实ES故障见[实验验收](../../../projects/travel-search/review/f30/README.md)。
