# F43 · 真实负载实验与限制

[F43正文](../../../../framework/f43.html)先讲测量语义，[本机入口](../../labs/f43/README.md)给完整命令。以下为两轮真实运行，第二轮在点名清理后执行；相同最终负载逻辑、相同语料哈希与固定顺序。所有正常请求与全字段核对通过，受控429及配置恢复通过，不构成生产容量上限。

| 验收 | 实际证据 |
| --- | --- |
| 构建 | [build.log](build.log)：Boot4.0.8/JDK25.0.4.1+1/官方Java与Rest5 Client9.4.8实际clean package；[Java编译](java-compile.log)退出0；ES bundled JVM从节点另读 |
| 正式第一轮 | [summary](run-01/summary.json)、[环境](run-01/environment.json)、[HTTP计数](run-01/http-accounting.json)、[逐文件哈希](run-01/archive-manifest.json) |
| 点名清理后第二轮 | [summary](run-02/summary.json)、[环境](run-02/environment.json)、[HTTP计数](run-02/http-accounting.json)、[逐文件哈希](run-02/archive-manifest.json) |
| 正确性 | 每次导入后REST/Java相同查询，2000/10000份分别500/2500命中、首页p000001/5/9/.../37；每项正常配置停止写入、refresh后遍历全部_source，和生成器＋唯一更新线程最后确认价格完全一致 |
| 展示壳 | [首轮初始](run-01/initial-browser.json)/[首轮改价](run-01/changed-browser.json)、[次轮初始](run-02/initial-browser.json)/[次轮改价](run-02/changed-browser.json)：每轮2稳定点×1440/390×浅深，浏览器→Java→ES，p000001由6100变7000分、2500命中、20卡片；无JS/HTTP错误、无浏览器直连ES |
| 清理与还原 | [首启](start01/)、[第一轮后](cleanup01/)、[第二轮后](cleanup02/)、[down](down/)，四索引明确删除并GET404，恢复正常n1限额，容器/网络移除、卷与身份保留；[最终环境](../../../../docs/framework-review/20261030-f43-capacity/workspace-state.json) |
| 原始样本复算 | [复算脚本](../../../../docs/framework-review/20261030-f43-capacity/recompute.py)和[结果](../../../../docs/framework-review/20261030-f43-capacity/recomputed.json)：逐请求起止/队列串行性/正式样本边界、分位数与吞吐、Bulk失败与重试、两轮输入哈希及全部压缩原始字节哈希 |

c01每轮4组：2000份/批100/并发1→10000/100/1→10000/500/1→10000/500/4。成功份/秒轮1为2421.6、5089.3、9793.0、12398.3；轮2为2671.1、4806.5、7711.0、14291.7。Bulk批次p95及原始样本另存，不能当单份文档延迟；尤其较短导入与JIT/顺序/缓存相关，没有寻找最优拐点。

c02每轮6项，每项预热3秒、发出窗口15秒、分母含排空：单节点1主0副4搜索→加1更新→8搜索1更新→单节点2主0副4+1→两节点2主0副4+1→两节点2主1副4+1。更新每批20份完整index覆盖，HTTP连接每线程复用；只有一个更新者。第一轮正式47844次HTTP，第二轮44094次，均成功。含预热的混合请求分别56279/51712次。原始samples保留全部起止与成功/错误；search/update分开计量，p50/p95/p99用nearest-rank，未平均分组分位数。

每轮另有329次Python协调/验证HTTP（319个200、10个预期404）、316次显式Java测量Bulk调用、10次Java预热Bulk、20次Java导入后refresh/search、102次监控API；观察窗10次API对应10次ES搜索（2次脚本＋8次浏览器）。已知ES API调用总计57066/52499；不含未完整计数的应用资产、就绪轮询或可能发生于SDK内部的底层传输尝试。不能把线程池任务数当HTTP请求数。头部只统计正式混合负载请求，其他操作分列。

c03两轮均为真实ES受控拒绝：n1原卷重启后写入压力限额1024字节，2000份/批500/并发1，4批各初次＋最多3重试，16次显式调用都HTTP429；coordinating_rejections增加16，rejected item尝试8000，逻辑成功0/失败2000。首条reason协调操作1035字节超过1024。移除覆盖后正常限额恢复，批100/并发1全部成功；2000份_source、500命中与10个首页ID核对通过。受控限额不是自然饱和阈值。400/未知传输结果处理有代码，未在本课注入，不能称所有失败分支已验证。

每配置保留before/after节点统计、每秒资源样本、索引store/segment/merge/refresh等统计及实际shard分布。计数器区间含预热/监控，堆为采样最大值；未发生窗口内重启，未注入同node ID计数器重置。两个节点仍共享Docker VM的2 CPU/约3.81GiB与磁盘；每节点配置1 CPU/768MiB、堆256MiB。原9201安全节点始终运行，PID/StartedAt/healthy前后不变。宿主写作与阅读活动未隔离，也没有证明压测客户端永不成为瓶颈。

大响应和JSONL采用无损gzip；[archive-run.py](../../../../docs/framework-review/20261030-f43-capacity/archive-run.py)保存压缩前后字节哈希，原始响应没有用摘要替换。正式两轮之外的[预验收](../../../../docs/framework-review/20261030-f43-capacity/attempts/preflight-note.md)单列，不进入正文结果。

限制：重复合成文本、均匀分布、单热查询、单更新者、短窗口和固定顺序；闭环慢时自动降发出率，未做独立到达率、客户端排队或coordinated omission修正。未测真实长尾/热点、大磁盘工作集、长期merge/GC稳态、冷启动、CDC端到端容量、故障后余量、HA或生产SLO。只报告固定条件下观测值，未找到容量上限。图解/HTTP/视觉与推理入口限制在[阅读验收](../../../../docs/framework-review/20261030-f43-capacity/README.md)独立记录。

契约边界：负载query.json为size10，独立Java加载同一DSL；F07观察窗仍用自己的字段组合和size20，每次以实际esRequest重放验证。两条路径在固定语料上均2500命中，但没有声称它们DSL或请求成本完全相同。
