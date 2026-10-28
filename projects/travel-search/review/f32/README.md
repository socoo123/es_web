# F32 真实执行记录

本目录是本课实际运行收据，不是预计输出。读者从[labs/f32](../../labs/f32/README.md)开始；阅读/图解验收另见[docs记录](../../../../docs/framework-review/20261028-f32-template-alias/README.md)。

| 证据 | 实际范围 |
| --- | --- |
| [setup](setup/summary.json) / [身份](setup/identity.json) | 独立两节点首启；移除bootstrap名单，保持UUID/node ID；19632–19633回环，无认证 |
| [round-1](round-1/summary.json) / [round-2](round-2/summary.json) | 各85教学REST（33+23+29）、6 Java搜索HTTP、6官方客户端写入；各自从点名清理开始；guard/wait/identity/cleanup另计 |
| [继承](round-2/actual-inheritance.json) | v001/v002旧设置不倒改；v003继承更新；v004显式覆盖创建设置；完整mapping/settings |
| [竞争模拟](round-2/shadow-simulation.json) / [修复模拟](round-2/repaired-simulation.json) | 高priority独立胜出；模拟不创建索引；相同priority拒绝另存 |
| [两版查询](round-2/write-alias-searches-both.json) | is_write_index不缩小搜索集合；命中_index、重复ID及60/65元分别可见 |
| [最终关系](round-2/aliases-final.json) | read只挂v002=false；write挂v001=false/v002=true |
| [缺失目标](round-2/error-missing.json) / [物理目标](round-2/error-physical.json) | require_alias=true均404/index_not_found_exception；HEAD证明缺失目标未误建 |
| [无writer](round-2/error-no-writer.json) / [两个writer](round-2/error-two-writers.json) | 400/500的原因；配置拒绝后关系仍false；修复后p08只落v002 |
| [Java缺失入口](round-2/04-missing-read-alias-java.json) / [空目标](round-2/05-wrong-empty-target-java.json) / [恢复](round-2/06-target-repaired-java.json) | 502→200/0条→200/两条65元/0元；同一配置/Java进程 |
| [运行与构建](runtime.json) | Boot4/JDK25、官方客户端、ES内置JVM、Docker内存/容器状态、源码/包/HTTP资源一致；无测试源，不称测试通过 |

每轮`events.jsonl`保留方法、路径、请求、HTTP状态、原始JSON与kind/case。独立Java命令stdout与六次`java-client`事件同存；每次只有一个官方客户端写入。两次成功是REST先created、Java再updated相同内容，四次失败是缺失/物理/read禁写/多目标无writer。所有写入使用require_alias=true，成功还要求主副2份。最终两个节点分别限定读取，核对v001原6份+p07、v002原6份（p01=6500）+p08；p09不存在，集群设置前后为空。

首轮6个稳定点通过1440/390px、浅深主题真实浏览器提交24次Java，成功点另外20次REST重放页面DSL；分别保存在`round-1/*-browser.json`与`screenshots/`，不混入主流程计数。第二轮不运行observer，全部主流程再次执行。浏览器直接ES请求为0。应用启动、构建、清理和浏览器请求独立于85计数。

[attempts](attempts/README.md)保留正式两轮前两次作者脚本失败：系统历史guard过严、require_alias错误码预期错误。均修正后点名清理重跑；不是已发布旧课勘误，失败记录不算通过。

`cleanup/`记录点名删除本课索引/模板/组件；`down/`记录只移除本课容器网络、保留卷。未执行持续并发、正式重建切换/回滚、过滤alias/routing、ILM/data stream、安全、跨机器、性能或恢复时限测试；这两份独立快照不构成持续同步方案。

Maven原始日志按字节无损压缩为build.log.gz与dependency-tree.log.gz；[原始/归档哈希及回解核对](log-archives.json)证明内容未改。暂存检查发现原始INFO空行的尾空格，归档并补全新增文件的差异检查后提交，未为去空格修改原始响应。
