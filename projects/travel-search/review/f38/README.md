# F38 · 真实MySQL链路证据

阅读[正文](../../../../framework/f38.html)，运行[labs/f38](../../labs/f38/README.md)。本目录只记录F38，PG原记录保持独立。

- [runtime.json](runtime.json)与[构建日志](build.json.gz)：MySQL8.4.5、Kafka4.0.1、Debezium3.3.1.Final、ES9.4.0以及Boot4/JDK25真实构建、镜像digest/容器端口与源码哈希。
- 两正式轮为run-02与点名cleanup-02后的run-03。每轮3案例，41教学HTTP=26 ES REST＋10 Connect REST＋5 Java搜索；消费者另9次index/delete。身份/资源guard五条，轮询/清理/浏览器附加另计。
- c01受限账户SELECT/快照/复制成功、UPDATE1142拒绝；两个r→Java提交2，GET/SEARCH分离，refresh后p01/6000与p02/0。
- c02 c/u/u→p01/6500、p03/3000并移除closed p02；物理d.before含完整p03旧行，随后tombstone，next=7；refresh后只剩p01。
- c03整个worker正常停止，原卷保留；停机DDL加列和三种变化使binlog前进，Kafka仍7、ES仍旧。恢复原worker后u/c/d+tombstone，无新增r；新列正确解码，history含ALTER。Java至11、refresh后完整_source等于SQL开放行，p02/p03 404，再drain0。
- 保留source offsets临时指向空history，task FAILED；恢复原history后RUNNING、仍11事件、drain0。失败trace保存在每轮c03-missing-history-failure.json。
- 五稳定点每轮1440/390×双主题真实浏览器→Java→ES；每轮20次浏览器搜索并独立REST重放，原始响应/截图在*-browser.json及screenshots。

[预验收说明](attempts/README.md)保留run-01的多行history解析失败及修正，不列作完整通过。正式轮summary.json、原始SQL/HTTP与事件分别保留；全部完成后的实际检查、清理/停止与限制以[章节验收](../../../../docs/framework-review/20261029-f38-binlog/README.md)和各收据为准。

范围：单MySQL主节点、1业务分区/1消费者、固定主键、短时正常worker停启，独立profile；没有长停机/日志清除、崩溃/HA、GTID切换、多表投影、任意重复乱序、重试/DLQ或在线重建，不宣称恰好一次或吞吐指标。
