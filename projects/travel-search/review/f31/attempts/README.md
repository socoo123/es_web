# 首尝试中断与恢复

`drain-await/`不是正式通过轮次。实际运行已完成n2排空，并在恢复n2后排空n3；第一版作者脚本要求至少一条`PEER.source.name`等于被排空节点，终端首先抛出`AssertionError: No completed peer migration from drained node`。这是错误的断言：移动副本可以从另一节点的primary恢复。

异常恢复又只等一次green，未等异步规划后实际零分片，因此路由仍含n3时再次断言失败。`failure.json`保存了后一个恢复异常；第一版没有单独持久化原始异常，此处明确记录原始错误来自当时终端观察，而不是伪称它已存在于初版JSON。`events.jsonl`保留实际请求、恢复源与剩余路由，截图保留当时已完成的观察点。

脚本现已使用`wait_drained`重复读取实际路由，排空前后核对、所有拷贝STARTED、恢复DONE和完整资料；不限定PEER源必须来自被排空节点。异常分支也先保存`primary-failure.json`，恢复异常另存，避免覆盖原故障。

`drain-recovery/`是修正后的实际恢复记录；其后从点名清理开始完成`../round-1/`和`../round-2/`两轮正式实验，81教学REST＋7 Java接口HTTP各自统计。本目录的中断不混入正式通过数。
