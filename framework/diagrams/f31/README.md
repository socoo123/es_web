# F31 · D2图源与双主题资产

- `allocation-gates.d2`：本课same_shard/filter/受控磁盘low拒绝与先排空后停data节点。
- `resize-choices.d2`：普通索引的2→4 split、4→2 shrink、reindex到3与目标不持续跟随的边界。
- 官方D2 v0.9.0，dagre；浅色theme 4、深色201，pad 24。静态分类图，无动画或播放器。
- 在仓库根目录生成：`python3 docs/framework-review/20261028-f31-allocation/generate-diagrams.py`。`D2_BIN`可指定同版本CLI。
- 每次修改D2后正式运行fmt、fmt --check、validate和四次SVG导出，禁止手改产物。命令、版本、退出码与图源/产物SHA-256见[generation.json](generation.json)。
- 图中是教学条件摘要，省略其他decider与恢复协议，不表达固定调用顺序；PEER source不必来自被排空节点。
- [HTTP与实际视觉审阅](../../../docs/framework-review/20261028-f31-allocation/README.md)和[真实ES/Java](../../../projects/travel-search/review/f31/README.md)分别记录。
