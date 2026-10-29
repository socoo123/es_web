# F38预验收与修正

run-01先完成c01快照/Java写入/refresh/真实观察窗，随后在读取schema history证据时停止。Kafka ConsoleConsumer输出的记录值本身是多行JSON，原辅助解析按每行JSON读取，触发JSONDecodeError。真实链路未判失败，但这轮不列作三案例通过。

[初始原始CLI输出](history-console-initial.json)保留多行值与实际返回码0、有限观察超时诊断及6条计数。修正为JSONDecoder连续读取完整值，并核对CLI报告条数、topic分区/保留配置，未修改业务捕获/投影契约。cleanup-preflight点名清理后，重新从干净条件执行两正式轮；正式轮见上级README。
