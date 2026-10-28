# F29 · 分片组与请求范围

[写入路径](write-path.d2)概括协调、当前主片与同步副本的阶段依赖，省略网络确认回程、translog、重试和故障处理；不是抓包时序。[搜索范围](search-scope.d2)比较两条独立请求，不表示先全索引再缩小；每组只选一份主/副拷贝，routing不替代query城市过滤。

只适用本课在ES9.4.0新建的普通未分区索引、2主1副、无routing_path或resize。HZ→0、SH→1、FZ→0来自实际_search_shards；不固定物理节点。

官方D2 v0.9.0 / dagre / 主题4与201；2源4SVG，只改源后重新生成。

```bash
python3 docs/framework-review/20261028-f29-routing/generate-diagrams.py
```

可用D2_BIN指定同版本CLI。[生成收据](generation.json)含fmt、validate、命令、版本与SHA-256；生成、HTTP视觉、真实ES分别验收。官方依据：[D2导出](https://d2lang.com/tour/exports/)。
