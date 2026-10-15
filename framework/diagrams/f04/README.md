# F04 静态图解

两幅 D2 分别解释按用途选择字段与 Bulk 部分失败后的恢复顺序；均是教学决策/操作顺序，不表示 ES 内部调用。Bulk 数值为预测，本环境真实执行受阻，不能当实测图。

官方 D2 v0.9.0、内置 dagre 布局、主题4/201、pad24，图源、命令与哈希见 [generation.json](generation.json)。只改图源重新生成，未手改 SVG。沿用 [Source Sans 字体许可](../../../docs/framework-diagrams/SOURCE-SANS-LICENSE.txt)。

```bash
python3 framework/diagrams/f04/generate.py /path/to/d2
```

图解使用纵向布局、浅深资产与展开入口，离线不依赖 CDN。没有动画或 Archify，其原生门禁不适用。实际阅读记录见 [F04 验收](../../../docs/framework-review/20261015-f04-model-bulk/README.md)。
