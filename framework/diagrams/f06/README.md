# F06 静态图解

两幅图均为固定教学样本的预测，不能证明真实 ES 已执行。图中箭头表示集合推导或独立请求的比较，不承诺 ES 的内部执行顺序。

- [硬条件集合](hard-constraints.d2)：[浅色](hard-constraints-light.svg) / [深色](hard-constraints-dark.svg)
- [should 默认要求](should-defaults.d2)：[浅色](should-defaults-light.svg) / [深色](should-defaults-dark.svg)
- [生成脚本](generate.py)、[版本、命令与哈希](generation.json)

使用官方 D2 v0.9.0，内置 dagre，浅色主题4、深色201、pad24。修改 D2 后先运行 `d2 fmt framework/diagrams/f06/*.d2`，再从仓库根目录运行 `python3 framework/diagrams/f06/generate.py /path/to/d2`；不手改 SVG。

字体许可沿用 [Source Sans](../../../docs/framework-diagrams/SOURCE-SANS-LICENSE.txt)。正文主题与图片、展开链接同步；生成验收和浏览器阅读记录分别保留。
