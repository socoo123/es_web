# F07 · ES / Boot / Java 真实验收

2026-10-20，本机macOS arm64。仅验收F07，未替F04–F06补填历史结果。ES9.4.0 / Lucene10.4.0 / 单节点 / 1主0副本 / 无认证 / 19200，Java绑定18080；[环境与原始请求响应](es-java-review.json)、[实际构建阅读副本](build.log) / [原字节输出与SHA256](build-raw.json)、[依赖树](dependency-tree.txt)、[制品与JDK下载哈希](artifacts.json)分别保留。

## 已通过

- Boot4.0.8 / Temurin JDK25.0.4.1+1 / Java Client与Rest5 Client9.4.8 / Jackson3，Maven Wrapper3.3.4 / Maven3.9.11实际clean package并运行；日志无单元测试，不把package成功写成测试覆盖。
- f07-c01：tut-f07-attractions独立创建，十二项Bulk均created，mapping一致，refresh/count零失败；200元返回F/B/A，80元B/A，“火星”空集合；完整ID顺序、价格/币种/状态、total/relation、conditions、Java序列化DSL与REST的解析JSON逐项一致。
- f07-c02：每轮八种非法输入均400，包括小数分；索引缺失502；ES停止但Java health200/search503；ES持久恢复后同一Java进程/Client再次返回三ID。两轮各点名删除后确认404，再重建/重做；不是复用旧课成功输出。
- 正常SIGTERM关闭应用，端口不再响应，日志为正常关闭；代码以Bean destroyMethod=close关闭Client/Transport，未声称抓包证明每个连接资源。构造时的网络失败不会把Java进程健康伪装成搜索健康。

[f07-c03本机展示壳、HTTP阅读与视觉](../../../../docs/framework-review/20261020-f07-java/README.md)单列。未刻意制造真实分片部分失败、ES执行超时，也未运行多节点、插件、TLS/认证、数据库/Kafka/CDC或性能验收。

## 作者复现

选好JDK25、构建jar后，从仓库根目录执行：

```bash
python3 projects/travel-search/review/f07/verify.py
```

拒绝已占用18080与已存在本课索引；会创建/两轮点名删除本课索引，短暂停止并重启框架专用ES，最后关闭Java、保留持久卷，不触及源码篇9200/9201。读者手工路径见[labs](../../labs/f07/README.md)。

## 修正与限制

[首轮请求写法差异](attempts/first-dsl-shorthand.json)：语义相同的term简写与Client的value对象使作者严格JSON比较失败，统一REST固定文件完整写法后重跑。[重启探测工具错误](attempts/restart-probe-disconnect.json)：启动过程短暂关闭TCP，探测器原来漏捕RemoteDisconnected；修正探测后重跑完整两轮，未当成产品缺陷。依赖树发现Boot将Rest5默认管理为9.2.9，最终以elasticsearch-client.version同时锁到9.4.8并重新构建/两轮实连。

当前会话入口无法设置或确认实际xhigh，内容为作者自审，没有独立审阅代理。真实API与展示壳、图生成、教程阅读分别记录。
