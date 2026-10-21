# F11 真实ES/Java验收

作者专用verify.py只访问tut-f11-attractions，初次与点名删除后重做均实际创建/导入/运行/清理。读者入口是[labs/f11](../../labs/f11/README.md)，无需先学验收工具。

[两轮摘要](es-java-review.json)、[初次原始请求响应](initial.json)、[清理重做原始请求响应](repeat-after-cleanup.json)、[真实过期](expiry.json)（可用expiry.py复现，需先导入本课资料并启动Java）、[构建](build.json)、[依赖树](dependency-tree.json)与[Java进程日志](java.log)分别记录。探索阶段offsets-initial/view-initial/java-initial只证明那些当时调用，正式两轮以initial/repeat-after-cleanup为准。

语料16份、九份共同候选；偏移窗口、普通search_after重漏、PIT完整元组/原价、三种排序逐页REST↔Java、末页/空集、每页2条、条件/页大小/页序409、关闭410、外部释放真实ES上下文410、400非法输入及缺索引502均按实际响应断言。expiry记录原生1秒PIT等待66秒无续期后404、Java闲置60秒410；ES清理是后台过程，不承诺到期瞬间清理。

单节点单主分片小样本、受控请求间改价，非随机并发/负载基准。未测试多节点/权限/TLS、真实执行超时/部分分片失败。资源最终恢复见[工作区恢复](../../../../docs/framework-review/20261021-f11-pagination/workspace-state.json)。
