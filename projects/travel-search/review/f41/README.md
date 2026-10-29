# F41 · 真实执行记录

正文[framework/f41](../../../../framework/f41.html)，读者入口[labs/f41](../../labs/f41/README.md)，图解/HTTP阅读/视觉与内容审阅在[本轮审阅目录](../../../../docs/framework-review/20261029-f41-rebuild/README.md)。

[run-03](run-03/summary.json)及点名清理后的[run-04](run-04/summary.json)完成同一最终实现的三案例两轮。每轮19来源事件（15文档=3初始r+12业务c，另4fence c）、16次留档Java命令执行（只读轮询另列）、92项协调/观察HTTP（82 ES＋4 Connect＋6 Java接口，含身份/验收）；12次含Bulk条目的Java命令/36项结果分列（客户端每个HTTP请求未单独抓取），不与92项混计。见[execution-audit.json](execution-audit.json)。

- c01：保存Kafka L=3后固定真实PG Repeatable Read视图，保持该事务打开，第二会话提交改价/删除/新增/关联城市五份完整投影。导出仍是p01/6000、p02/0、p03/3000、各revision1。v2先处理L到backfill H9，未完成全量时gate拒绝；加载旧快照时p01/p02 noop、p03创建，p04保留。两版完整四ID核对通过。初始一次reindex created3，后续仍含已删p02、缺p04、p01仍6000，反例真实留档。
- c02：p01/7000 v4、p03下架标记v2、p04夜景标签v3；来源cutover fence offset12/H13。v1到13、v2停9时拒绝；真实ES index.blocks.write让三Bulk item均403，v2无commit，仍9，alias未改。解除block后原位重放至13。随后SQL继续提交p01/7200 v5及p04删除v4，Kafka end15，两消费者仍限在H13。gate按保存的fence投影核对并明确积压2，然后查询alias切v2；当前观察仍7000/4500，v2 price_band筛under_50只p04。没有声称72元已同步。
- c03：追加rollback fence offset15/H16，仅v2到16，观察p01/7200及p04已删。v1仍13，回滚被拒绝；v1追到16并逐ID完整核对后再回滚，仍7200，既有Java进程PID不变。再改p01/7600 v6、同ID重开p04/4800 v5空标签，两版追到final H19。最初快照再重放三项全noop，两组再drain0。

每轮36项Bulk结果为25项200、8项201、3项403；5项noop（首次旧快照2、最后重放3）。任何失败阻止该批提交，无DLQ豁免；本课未测试F40的429重试。四个拒绝分别为全量未完成、目标落后、目标写入失败后仍落后、旧版落后不能回滚；每次均留前后alias相同证据。

最终p01/v6/7600、p02/v2/删除、p03/v2/下架、p04/v5/4800/空tags；每版原始4份、可搜索2份，next都19。两版布局分别schema1/2，v2派生price_band；各自sync_hash包含投影版本和同一规范JSONB文本。全部字段、标记、revision、hash和过滤alias均核对，不只比较条数。

每轮六稳定点×1440/390×双主题=24次真实浏览器提交及24次独立REST重放，卡片ID/整数分价格、Java请求/结果与完整ES投影逐项核对。initial60+0、backfill65+45、cutover70+45、new-live72、rollback72、final76+48元。同一观察进程贯穿一轮，浏览器不直接访问ES；不是Pages在线业务。

预验收run-01在首次真实Java搜索后因选择的Python环境缺Playwright退出；run-02在管理客户端默认请求超时大于default.api.timeout.ms时拒绝初始化。没有作为完整通过轮次。修正环境及显式request.timeout.ms后清理，再执行run-03；失败记录保留。

另保留启动前编译探针：javac成功后误执行seed，因broker尚未启动超时，未写消费位置；不作为运行通过。构建、依赖树和真实应用JDK25、镜像digest及ES bundled JDK26.0.1见[runtime.json](runtime.json)与压缩构建日志。

[最终清理](cleanup-final/summary.json)、[down](down/summary.json)及[shutdown](shutdown.json)通过。F41容器/网络移除，五个端口关闭，三个具名卷与.local秘密保留；既有es-study-secure容器ID/启动时间/healthy均不变。

限制：单VM/broker、单topic单分区、一个task、合作业务写入者/完整不可变outbox/持久clock、串行本机worker。全量期间可写，来源fence只短事务串行化，消费者按H分段停止。未验证任意断电/Kafka故障/HA、跨分区事务屏障、分布式协调、保留耗尽、吞吐或自动回滚。alias改变与本地job保存不构成共同事务；该崩溃窗口需先核对真实alias人工恢复。本课只证明固定边界完整，不承诺切换瞬间等于最新DB或跨ES/Kafka恰好一次。
