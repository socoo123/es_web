# F34 真实运行验收

仅F34，ES9.4.0/Lucene10.4.0；隔离两节点19834–19835，与既有es-study-secure独立。应用复用Boot4.0.8 / JDK25 / Java与Rest5 Client9.4.8，无共享后端或前端改动。

[run-01/summary.json](run-01/summary.json)与[run-02/summary.json](run-02/summary.json)均完整通过。各65教学REST（16+25+24）+4 Java接口HTTP；guard/身份/等待/清理另计，浏览器附加请求不冒充教学数。两轮各四个观察点×1440/390×浅深=16次真实浏览器→Java，生成DSL均单独REST重放；两轮共32次，直接浏览器→ES为0。

- c01：错误仓库路径500且未注册；修正后_verify两节点；accepted后元数据SUCCESS、2成功/0失败；固定六份资料、source write block、无全局/功能状态。
- c02：改p01=6500、删p02，两份拷贝均5条；单主零副risk在n2，停n2后UNASSIGNED；missing-primary元数据PARTIAL 2成功1失败，_status却SUCCESS且failed1。原卷n2回来risk仍1条；默认恢复500，显式partial返回200但failed1、隔离risk=0、EMPTY_STORE/DONE。源risk仍1条。
- c03：打开同名目标冲突500；改名恢复完整快照2成功0失败、再等副本green；两节点读取完整六份_source，mapping/设置、p01=6000/p02=0、代表查询、SNAPSHOT/DONE与无alias均核对。隔离恢复后Java仍实时源p01=6500；移动read后同Java进程返回历史p01/p02；源仍5条。

正式轮次events.jsonl保留完整请求/响应与分组；snapshot/status/restore/field/alias/recovery关键收据分文件。setup记录首启后移除bootstrap与不变身份，setup-permissions记录仓库卷权限初始化后原卷重启。

[attempts](attempts/README.md)保留预演失败，不冒充正式通过。构建/运行、手工请求与清理状态独立记录。阅读/图解/实际视觉见[审阅目录](../../../../docs/framework-review/20261028-f34-snapshot/README.md)。

范围为同Docker VM/宿主盘、小样本、同版本、手动快照和串行变更。仓库卷独立于数据卷但非独立故障域；未验证物理容灾、跨版本、安全/系统状态、持续业务追平、SLM、性能和恢复时限。历史备份中的6000分不是最新合法6500分，未宣称最新业务已恢复。

[构建与运行](runtime.json)记录应用Temurin25.0.4.1+1、Maven3.9.11、ES内置JVM26.0.1、镜像/资源/源码包HTTP哈希；clean package/依赖树/classpath实际通过，没有测试源，不称“测试通过”。[manual/summary](manual/summary.json)另记录53个手工curl响应，其中4 Java接口、3预期500；不是第三轮正式运行。

[cleanup](cleanup/summary.json)、[final-state](final-state.json)、[down](down/summary.json)与[shutdown](shutdown.json)记录五索引/两快照/仓库已清，persistent/transient仍空，两节点身份保持，三个卷保留，本课Java停止、容器/网络移除。既有es-study-secure的ID/PID/启动时间/健康均未改变，监测明细在审阅目录。
