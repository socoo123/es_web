# F03 图解

两幅静态 D2 分别回答：怎样从空索引得到第一条真实命中；停机恢复后应逐层核对什么。箭头是读者操作/检查顺序，省略 ES 内部调用和数据复制。图中样本、路径和条件对应 [正文](../../f03.html)与 [本轮 ES 验收](../../../projects/travel-search/review/f03/README.md)。

保存 first-search.d2 / readiness.d2 与浅深四份 SVG，官方 D2 v0.9.0、TALA、主题 4/201、pad=24；[命令与哈希](generation.json)。只改图源再生成，未手改 SVG。静态图没有机制动画，Archify 原生门禁不适用。

```bash
python3 framework/diagrams/f03/generate.py /path/to/d2
```

预生成资产不依赖 CDN；父页主题切换会同步图片和展开链接。窄纵向布局在 320/390px 与桌面列内完整显示，详细实际范围见 [HTTP 阅读验收](../../../docs/framework-review/20261014-f03-first-search/README.md)。

字体保留既有 [Source Sans / SIL OFL](../../../docs/framework-diagrams/SOURCE-SANS-LICENSE.txt)，中文由浏览器字体回退显示。
