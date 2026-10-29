# F37 · 静态 D2 图解

wal-chain解释一次数据库变更经过哪些职责；restart-boundaries解释三案例中的停机、日志保留、恢复与Kafka已新/ES仍旧。前图箭头是数据流，后图箭头是受控实验先后；不表示真实耗时。两图均为静态图，不承诺动画或重播。

官方D2 v0.9.0，dagre，浅色4/深色201。保留.d2与四份预生成SVG，修改图源后重新执行fmt、fmt --check、validate和渲染，未手改产物。CLI/图源/产物SHA-256及实际命令见[generation.json](generation.json)。命令示例：

```bash
d2 fmt framework/diagrams/f37/wal-chain.d2
d2 fmt --check framework/diagrams/f37/wal-chain.d2
d2 validate framework/diagrams/f37/wal-chain.d2
d2 --layout=dagre --theme=4 --pad=24 --timeout=30 framework/diagrams/f37/wal-chain.d2 framework/diagrams/f37/wal-chain-light.svg
d2 --layout=dagre --theme=201 --pad=24 --timeout=30 framework/diagrams/f37/wal-chain.d2 framework/diagrams/f37/wal-chain-dark.svg
```

restart-boundaries同样处理。正文复用course.js切换图与展开目标；窄屏局部滚动，必要信息同时写入图注和正文。图生成、HTTP阅读/视觉与真实CDC分别记录。本课未使用Archify。
