# F39 · 真实执行证据

正文[framework/f39](../../../../framework/f39.html)，读者步骤[labs/f39](../../labs/f39/README.md)。独立es-framework-f39，PG主库→Debezium→三个Kafka单分区topic→单Java消费者→ES，浏览器经既有Boot搜索服务读取。

- 正式首轮[run-02/summary.json](run-02/summary.json)，点名清理[cleanup-02](cleanup-02/summary.json)后完整重做[run-03](run-03/summary.json)。各轮三案例、20条业务记录，17个消费者Bulk/20条目；45教学HTTP（35 ES＋3 Connect＋7 Java搜索），身份/轮询/SQL/清理/浏览器另计。
- c01：三表8个快照r，最终3份搜索文档；FULL/两读取角色SELECT与42501写入拒绝、完整字段、GET已新/SEARCH未refresh仍空分别保存。
- c02：城市改名影响[p01,p02]、根改价和子新增；t02完整before/after从p01转至p02。只写after的真实反例让夜间查询错误命中[p01,p02]，完整重算旧新两份文档后只命中[p02]。`transferred-apply.json`保存完整JSON、NDJSON、条目结果与分区提交。
- c03：最后标签删掉后父文档保留且tags=[]；下架删p02；p03物理删与t04级联产生两次delete（deleted/not_found）；p02重开按当前三表重建。最终p01/6500/[]、p02/0/[亲水,夜景]，p03不存在。三个分区末端/提交分别3/8/9，再drain0。
- 七个观察点initial/shared/transferred/empty-tags/closed/root-deleted/reopened，每轮7次Java接口与同契约REST重放；作者observer每点1440/390×双主题真实点击搜索，单列浏览器请求与截图。
- [follow附加](follow/summary.json)：t02从p02→p01→p02，offset9/10提交next10/11，每次重算[p01,p02]，夜间查询与完整字段恢复；SIGINT停止并等组无人活动。2 Bulk/4条目与两轮分列。[REST Bulk重放](rest-bulk-replay.json)用最终p02同一NDJSON成功重放，完整字段不变。
- [构建](build.json)、[制品/身份](runtime.json)、[停止核对](shutdown.json)单列。最终清理本课资源、down移除容器/网络，三具名卷与.local保留；既有es-study-secure未变。
- [预验收run-01](run-01)：作者在start尚未返回时提前运行，仅完成身份读取即遇Connect启动期间RemoteDisconnected，没有创建本课表或topic；不列完整通过。启动命令返回成功后开始run-02。

每轮HTTP原始证据在http.jsonl、SQL在sql.jsonl，事件在`*-events.json`，每事件affected_ids/文档/Bulk/条目与提交在`*-apply.json`。完整_Source按独立SQL投影逐字段比较，价格/命中和ES可见性单独核对。构建、身份、制品与最终清理记录在本目录相应文件，章节HTTP/图生成/视觉另见[章节验收](../../../../docs/framework-review/20261029-f39-projection/README.md)。

适用范围：稳定表主键、PG主库回查、单消费者、三个各单分区topic、每个教学阶段暂停其他写入。每事件的REPEATABLE READ只保证回查视图一致，不是原事件时间状态、跨topic事务快照或数据库/ES/Kafka原子事务。没有验证任意崩溃/乱序/延迟副本/失败重放/重试与DLQ、HA、主键变更/TRUNCATE、在线重建、高扇出或性能，不宣称恰好一次。仅本地合成环境明文/无ES认证，部署安全另按F35。
