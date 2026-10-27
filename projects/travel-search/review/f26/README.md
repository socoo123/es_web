# F26 真实执行记录

环境：ES9.4.0/Lucene10.4.0，19226/tut-f26-offers，单节点一主零副本，refresh=-1，无插件；应用Boot4.0.8/JDK25.0.4.1+1/官方Java与Rest5 Client9.4.8，Wrapper3.3.4/Maven3.9.11。ES bundled JVM26.0.1+8单列于runtime.json。

每轮前先[点名清理](round1-cleanup/cleanup.json)，再24教学HTTP（prepare10+collapse4+inner4+stays6），Java内部3次搜索另计；附加[错误29HTTP](round1/errors.json)，含其Java内部搜索的调用不混进教学数。两轮分别在round1、round2目录保留完整请求/响应JSONL与常量断言摘要。不是沿用旧课的通过记录。

- [第一轮](round1/stays.json)、[第二轮](round2/stays.json)：Java完整DSL与3份固定REST JSON精确相等，再真实重放核对全部hits/source/ID/sort/total/inner_hits；typed响应只归一化省略的null评分字段。逐晚记录、独立写定金额/拒绝原因、酒店内报价次序与酒店次序逐项检查。
- 16报价/9酒店，全部源与显式mapping/settings核对；GET mapping只规范化ES省略的默认doc_values:true。10候选报价/6候选酒店；不折叠顺序[o01,o05,o09,o10,o02,o03,o06,o07,o08,o16]；折叠[o01,o05,o09,o10,o07,o16]。hits.total始终10，cardinality本次6，不声称普遍精确。
- h01 inner总数3，size1/2/10取1/2/3条；降序取o03仍不改变外层o01。完整组逐项核对，原含早query排除o04；去掉meal命中12条，h01低价变为o04。
- top-offers：[h01/o01/100000,h02/o05/120000]；top-hotels：[h01/o02/80000,h02/o06/100000]；all：[h04/o09/60000,h05/o10/60000,h01/o02/80000,h02/o06/100000]（CNY分/一间两晚）。all检查10条/6家，7条合格/4家；o07缺晚、o08售罄、o16最短入住拒绝。
- 重复建索引400、Bulk16项409、6非法输入400、4种collapse/分页约束400、strict字段400、旧快照502与恢复。注入11条高价组内附加报价，保持已知o01代表；额外REST证实源相等、组total14/返回10，再触发inner截断502、101条附加报价触发全量截断502，点名删除后恢复；不是以截断价格假装精确。

构建与依赖树、运行/资源哈希见runtime.json；没有测试源，不将“No tests to run”称测试通过。实际浏览器→Java→ES观察窗、缺索引502/资料缺失502/真实停机503与恢复，另见[阅读与本机观察窗记录](../../../../docs/framework-review/20261027-f26-collapse/README.md)。

只证明固定快照、固定日期/政策/币种/人数下的语义；未测代表性负载/性能、多节点、随机并发更新、实时供价、生产安全和订单。超时/部分分片失败只有代码防护，未注入。候选完整上限100、所选酒店组内上限10；不是大规模完整检索方案。正式清理与保留卷状态在workspace-state.json。
