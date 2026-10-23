# F14 · 真实插件、ES与Java验收

[本机入口](../../labs/f14/README.md) · [教程](../../../../framework/f14.html) · [固定判断](../../data/f14/judgments.json) · [token/召回矩阵](../../search/f14/expected.json)。仅独立19214节点、tut-f14-attractions。

[执行收据](execution.json)、[第一轮](round-1.jsonl)、[第二轮](round-2.jsonl)分别保存真实请求/状态/完整响应。每轮20条内置基线+64条插件比较+24条Java/REST=108条教学HTTP；附加边界、清理与恢复单列，计数以收据为准。两轮都真实stock→插件镜像切换，不以旧F13结果替代。首次探索记录[基线](baseline-initial.jsonl)/[插件](plugins-initial.jsonl)保留，最终两轮有锁定断言。

[制品](artifacts.json)记录来源、SHA512/SHA256和9.4.0 descriptor。[版本错误](mismatch.json)为真实SmartCN9.3.0包在9.4.0一次性构建容器中被拒绝；不改descriptor、不留业务数据卷。安装日志见[构建记录](build/plugin-image.log)。IK的旧Security Policy与outbound_network安装提示未隐藏；本课没有自定义/远程字典。

实际完整mapping/settings、Bulk12项created/refresh/count12、节点清单/插件9.4.0、四查询/三名称样本的五方案token/位置/offset与召回矩阵均由[verify.py](verify.py)断言。Java6输入实际序列化DSL重放REST，核对完整ID/次序/名称/城市/价格/score/sort/total/relation与两次分析结果。附加检查未安装插件ES400/Java502、插件mapping创建失败无残留索引、10种非法输入400、预算0与纯标点空流、原文不被归一改变、未知analyzer400、删索引502/重建恢复、点名清理404。

应用与依赖版本/构建见[运行信息](build/runtime.json)、[Maven构建](build/build.log)与[依赖树](build/dependency-tree.txt)。应用JDK25与ES镜像JVM分开。本机展示壳真实请求、503停机恢复、HTTP阅读和视觉见[本轮审阅](../../../../docs/framework-review/20261024-f14-analyzers/README.md)，与本收据分开。

本课不证明整体中文质量、性能、词典生效、同义词/拼音、评分、多节点滚动安装、TLS权限或CDC；超时/部分分片失败只有服务端防护，未主动触发。最终资源状态见[恢复收据](../../../../docs/framework-review/20261024-f14-analyzers/workspace-state.json)。
