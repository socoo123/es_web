# F28 探索记录（不计正式两轮通过）

- round1：首次组群/移除bootstrap成功；prepare在Java完整DSL比对中发现term简写与value形式不同，固定REST改成客户端完整形式。
- exploration/restart：保留卷重启成功；另一次mistake在重启仍进行时过早读取端点，未执行后续配置变更，已将正式流程改为严格顺序。
- exploration-discovery：空字符串discovery.seed_hosts在Docker入口转成null setting，es3 exit70；非OOM。保留退出日志并改为127.0.0.1:9300。该等待人工终止，记录未完成，不称通过。
- exploration-discovery-fixed：真实不同UUID与加入拒绝已出现，但HTTP晚于transport日志启动，读取过早失败；增加HTTP readiness等待，严格匹配实际拒绝语句而非通用警告。
- 两份recovery与exploration-end：只处理F28容器/错误空卷/索引，原三份卷先保留回挂，最终为全新首启正式验收点名清理。
- D2字符串换行与Java片段行号/HTML转义在正式验收前修正。未发布新课，无历史已发布勘误。

正式完成状态只看review/f28/round1与round2，不能把这些探索输出补成正式通过。

实际后续分支：round1-mistake-log-assumption只接受显式加入拒绝而超时；源码Coordinator的fully-formed single-node诊断与实际独立UUID表明，已有单节点集群也可能根本不发起加入。断言现分别接受明确加入拒绝或不会发现其他节点的身份诊断，同时核对UUID仍不同、主集群仍2成员；不把通用警告冒称加入请求已执行。diagnostic-recovery挂回原卷并核对完整数据后，再重做正式mistake阶段。大于200KB的探索events无损gzip，原始哈希见compressed-events.json。
