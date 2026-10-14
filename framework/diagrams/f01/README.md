# F01 · 职责与学习路线图

当前导学有两幅静态图，使用官方 [D2 v0.9.0](https://github.com/d2lang/d2/releases/tag/v0.9.0) / TALA / 浅色主题 4、深色主题 201，预生成产物本地交付。

| 图 | 图源 | 浅色 / 深色 | 含义 |
| --- | --- | --- | --- |
| 搜索系统各自负责什么 | [search-roles.d2](search-roles.d2) | [浅](search-roles-light.svg) / [深](search-roles-dark.svg) | 左侧双向箭头表示请求/结果返回；右侧箭头表示搜索数据流。两边是同一套服务与 ES；网站/数据库同步均为课程目标示意 |
| 八阶段怎样推进 | [learning-route.d2](learning-route.d2) | [浅](learning-route-light.svg) / [深](learning-route-dark.svg) | 自上而下、每行从左到右；箭头表示学习推进，F12/F22/F45 为三个独立检验点 |

[生成命令、实际检查与 SHA-256](generation-intro.json)，[HTTP 阅读验收](../../../docs/framework-review/20261014-f01-intro/README.md)分别记录。仅修改 D2 图源后经 CLI 重新生成，没有手改 SVG；主题由课程开关选择对应产物。未使用 Archify 或机制动画。

复现示例（仓库根目录，d2 v0.9.0）：

```bash
d2 fmt --check framework/diagrams/f01/search-roles.d2 framework/diagrams/f01/learning-route.d2
d2 validate framework/diagrams/f01/search-roles.d2
d2 validate framework/diagrams/f01/learning-route.d2
d2 --layout=tala --theme=4 --pad=24 --timeout=30 framework/diagrams/f01/search-roles.d2 framework/diagrams/f01/search-roles-light.svg
d2 --layout=tala --theme=201 --pad=24 --timeout=30 framework/diagrams/f01/search-roles.d2 framework/diagrams/f01/search-roles-dark.svg
```

learning-route 按生成记录中相同命令替换源与产物名。字体使用 D2 默认 Source Sans 子集及浏览器中文字形回退，保留 [Source Sans / SIL OFL](../../../docs/framework-diagrams/SOURCE-SANS-LICENSE.txt)。阅读无需安装 D2 或访问 CDN。

## 历史启动实验图

[first-search.d2](first-search.d2) / [浅](first-search-light.svg) / [深](first-search-dark.svg) 与 [原生成记录](generation.json)仅对应[历史启动课](../../f01-startup-legacy.html)，保留原产物和验收。箭头表示旧课手工操作顺序；不能用于证明新 F03 已完成。原实验和证据不改名。
