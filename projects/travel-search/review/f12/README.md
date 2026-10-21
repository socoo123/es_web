# F12 · 真实ES/Java验收

[正文](../../../../framework/f12.html) · [手工入口](../../labs/f12/README.md) · [作者脚本](verify.py) · [两轮摘要](es-java-review.json)。原始[首次](initial.json)与[清理重做](repeat-after-cleanup.json)各160次真实请求；每轮主流程114=准备6+CRUD36+冲突17+Java27+结业28，附加46。早期单案例记录也保留，但不替代最终两轮。

环境沿用独立Compose ES9.4.0/Lucene10.4.0、单节点；tut-f12-attractions与tut-f12-graduation各一主零副本、strict、refresh_interval=-1。准备两轮均检查完整mapping、版本、green且未超时、四/八项Bulk created、refresh零失败及count。附加检查settings与mapping一致。

- 固定ID完整替换移除字段；_create重复409；doc局部合并保留名称，改价/closed/删除的实时GET与未刷新搜索前后对照、二次删除404、缺资料update404，恢复时created/updated按是否曾删除区分。
- 两个读取者保存真实_seq_no/_primary_term；甲6500分、乙旧令牌closed409，重读只改状态保留6500分；旧条件删除409，新条件删除成功。没有硬编码令牌或伪造主分片切换。
- Java真实create/get/index/update/delete，旧PATCH/DELETE409及重读，显式refresh前后分页，完整ID/价格/score/sort/total/relation逐项对照同PIT的真实REST。
- 新八份结业资料初始free/garden/museum，2/1；garden7000分已写但未刷的新搜索仍旧，refresh后新轮只剩free/museum，原PIT保留原三份；museum closed后只剩free，count8。另结业两编辑者7200分/closed旧409/重读合并通过。脚本成功不认证读者独立作答。
- 附加noop且序号未变、realtime=false旧值、refresh=true新值、wait_for确实等待（GET已新且Future未完成），另一请求显式refresh后返回。每轮输入错误400、ID不一致400、缺资料404、条件变化409/关闭后410；删除索引后GET/分页502，两个索引open_contexts=0、删除后404。

[最终构建](build.json)与[依赖树](dependency-tree.json)实际通过：Boot4.0.8 / Temurin25.0.4.1+1 / Java与Rest5 Client9.4.8 / Wrapper3.3.4、Maven3.9.11，无单元测试；应用JDK与ES bundled JVM分别记录。最终运行输入哈希随两轮摘要保存。[HTTP与本机观察窗](../../../../docs/framework-review/20261021-f12-crud/README.md)独立验收真实停机503/恢复和双窗口409。

未测试随机并发压测、主分片切换、多节点、性能、监听槽耗尽、TLS/权限/插件/DB/CDC或跨系统事务；搜索超时/部分分片失败仅沿用防护。资源点名清理，框架ES恢复原停止状态，源码篇节点与持久卷保留。写作/审阅xhigh当前入口无法设置核验，作者自审、无独立代理。
