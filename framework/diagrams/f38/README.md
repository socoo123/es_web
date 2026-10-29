# F38 · MySQL binlog与恢复证据

两幅静态D2：binlog-chain回答变化怎样到搜索，recovery-evidence回答停机/DDL/history怎样证明恢复。箭头为数据传递或本课观察顺序，不承诺耗时或跨系统原子性；无动画控制。窄屏局部滚动或展开，站点切换浅深SVG。

官方D2 v0.9.0、dagre、浅色theme4/深色theme201、pad24。图源修改后重新生成，不手改SVG。环境CLI位于/tmp/es-framework-d2-20261013/d2；读者可替换为自己的同版本d2路径：

```bash
d2 fmt binlog-chain.d2 recovery-evidence.d2
d2 fmt --check binlog-chain.d2 recovery-evidence.d2
d2 validate binlog-chain.d2
d2 validate recovery-evidence.d2
d2 --layout=dagre --theme=4 --pad=24 binlog-chain.d2 binlog-chain-light.svg
d2 --layout=dagre --theme=201 --pad=24 binlog-chain.d2 binlog-chain-dark.svg
d2 --layout=dagre --theme=4 --pad=24 recovery-evidence.d2 recovery-evidence-light.svg
d2 --layout=dagre --theme=201 --pad=24 recovery-evidence.d2 recovery-evidence-dark.svg
```

[generation.json](generation.json)记录实际逐条命令、退出码、版本与SHA-256；阅读/截图见[章节验收](../../../docs/framework-review/20261029-f38-binlog/README.md)，真实链路见[运行验收](../../../projects/travel-search/review/f38/README.md)。D2生成不替代MySQL/Java/ES或浏览器验证；未采用Archify。
