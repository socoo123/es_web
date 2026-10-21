# F12 静态D2图解

[可见性图源](visibility.d2)比较同一次改价的实时GET、refresh前后搜索与已有PIT；无连接的卡片表示不同读取路径，隐形边只排版。[冲突图源](conflict.d2)表示受控的两位编辑者操作次序，不代表所有并发请求的调度。省略分片内部实现、持久化与副本复制。

官方D2 v0.9.0 / dagre / 浅色4、深色201 / pad24。仅修改图源，再生成：

```bash
python3 framework/diagrams/f12/generate.py /path/to/d2
```

[生成收据](generation.json)含版本、命令及CLI/图源/产物SHA256。双主题离线图，不承诺动画。HTTP与视觉、ES/Java实测在[本轮记录](../../../docs/framework-review/20261021-f12-crud/README.md)分别记录。
