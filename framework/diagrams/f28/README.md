# F28 · 三节点身份与持久首启

[角色与端口](topology.d2)、[首次与已有集群](lifecycle.d2)是静态概念图。拓扑图只画部分transport连接，不表示转发必须经过es1，也不固定当选master或分片归属；所有节点都有协调能力。三进程在一台Docker VM内，不证明跨机器容灾。

官方D2 v0.9.0 / dagre / 浅色4、深色201，保留2源4SVG；只改源，再生成产物。

```bash
python3 docs/framework-review/20261027-f28-cluster/generate-diagrams.py
```

可用D2_BIN指定同版本CLI。[生成收据](generation.json)含fmt、validate、版本与哈希。来源：[D2导出](https://d2lang.com/tour/exports/)。图生成、浏览器视觉与真实集群分别验收。
