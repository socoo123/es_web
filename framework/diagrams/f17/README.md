# F17 · 静态D2图源

- choices.d2：completion/search_as_you_type/显式拼音三种线索，取01/02初始状态；卡片独立，隐形边只排版。
- guard.d2：本课guarded策略与短/长输入案例；独立卡片，不表示短词先于长词执行。普通query外层城市/open/CNY省略。
- 每源生成浅色主题4与深色201，官方D2 v0.9.0、dagre、pad24；SVG离线字体/样式由CLI生成，不手改产物。站点按钮切换浅深资产。

从仓库根目录，安装[官方D2 v0.9.0](https://github.com/terrastruct/d2/releases/tag/v0.9.0)后：

```bash
python3 framework/diagrams/f17/generate.py /path/to/d2
```

[生成收据](generation.json)保存CLI版本/哈希、fmt --check、validate、完整生成命令、图源/产物SHA256。静态图无播放器，不承诺暂停或重播。实际HTTP与截图阅读记录在[本课验收](../../../docs/framework-review/20261025-f17-suggestions/README.md)，ES实验另列；图生成不替代运行证据。
