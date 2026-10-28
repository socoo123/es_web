# F34 预演失败与修复

以下四次不是完整通过轮次，failure.json/events.jsonl原样保留：

1. repository-permissions：新Docker仓库卷根目录默认root权限，正确白名单路径仍500/access_denied_exception。修复：start先以隔离repo-init设置本课卷根目录1000:0和0770，不递归改文件；记录在setup-permissions。
2. health-wait-408：节点离线/回归期间等待条件暂未满足，健康接口408被旧等待器误判成终止错误。修复：轮询保留408响应，只有节点数/状态/无初始化迁移/timed_out=false满足才继续。
3. status-api-state：作者初始断言误以为_status的state必然与元数据相同；实际元数据PARTIAL而_status=SUCCESS/failed1。固定v9.4.0源码确认完成态映射，改按元数据与失败分片分别判断，正文/图解同步。
4. partial-restore-counts：作者初始断言把所有HTTP200恢复都当零失败。实际显式partial恢复返回200但total3/successful2/failed1；缺失risk以EMPTY_STORE重建为空。修正仅该损失演示的预期，完整恢复仍要求2成功/0失败。

未修改任何旧课内容论断。最终同一脚本两轮从点名清理开始完整通过，分别在run-01/run-02；失败截图仅作预演证据，不计正式观察窗验收次数。
