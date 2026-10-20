# F09 · 聚合与筛选计数（本机手工入口）

先读[教程](../../../../framework/f09.html)。沿用 F07 工程的 Boot4.0.8 / JDK25 / 官方 Java与Rest5 Client9.4.8，ES9.4.0 / Lucene10.4.0。Pages只承载教程；实验在本机执行。应用 JDK 与 ES bundled JVM 分开。先选择 JDK25，让 JAVA_HOME / PATH 指向它。

在仓库根目录：

```bash
cd projects/travel-search
docker compose -f infra/single-node/compose.yaml up -d es
bash infra/single-node/wait.sh
bash labs/f09/01-prepare.sh
bash labs/f09/02-scopes.sh
bash labs/f09/03-facets.sh
```

只用 tut-f09-attractions，1主0副本/strict；F08十五份原字段不变，补themes并增加上海合成资料，共16份。共同查询用 multi_match/best_fields/AND，CNY/open/非负价格/预算。**全国浏览，不使用F08杭州圆心和距离条件。**name/aliases/description仍参与查询，当前观察页不请求高亮。

准备的六个响应依次核对：版本9.4.0、创建acknowledged、green且未超时、16项created且errors=false、refresh零失败、count16。curl只判断HTTP错误；必须人工核对Bulk条级状态、分片与超时。初次应不存在本课索引；重复创建失败就停下，按末尾清理重做。

02对照：相同四个命中 boundary/far/guide/xihu（完整ID前缀a-hz-）。all-query只看到HZ4；post-only看到全国基础候选的HZ7/FZ1/SH1。两者统计范围不同。

03依次是：

| 请求 | 命中与聚合观察 |
| --- | --- |
| selected | HZ+lake或culture，共4；城市范围6，HZ4/FZ1/SH1；主题范围7，culture3/walk3/garden1/lake1，缺主题1；价格3/0/1 |
| multi-city | HZ或FZ，共5；城市桶不变；主题范围8，walk4/culture3/lake2/garden1；价格4/0/1 |
| overlap | HZ+lake或walk，共3：guide/missing-location/xihu；lake1和walk3不能相加；价格3/0/0 |
| empty | 火星零命中，空terms桶，固定range桶三个0 |
| unselected | 空数组不限维度，9个候选，城市HZ7/FZ1/SH1；主题culture4/walk4/lake2/garden1，缺主题1；价格7/1/1 |

价格桶单位分：[0,10000)、[10000,20000)、[20000,+∞)；共同预算仍生效。桶内为文档计数，主题可重叠；数字不是点击后总数、增加数或可售库存。

另开终端，在仓库根目录：

```bash
cd projects/travel-search/backend
./mvnw -version
./mvnw -B -ntp clean package
java -jar target/travel-search-0.7.0.jar
```

回到第一终端：

```bash
bash labs/f09/04-java.sh
bash labs/f09/05-candidates.sh
```

Java接口 POST /api/attractions/facet-search，字段q/cityCodes/themes/maxPriceFen；空数组不限，字段全部必填。cityCodes允许HZ/FZ/SH（最多3项）、themes允许lake/walk/garden/culture（最多4项）；预算整数分0–100000000；q非空最长60。服务端固定索引 tut-f09-attractions（TRAVEL_F09_INDEX可在服务启动前覆盖），其余课次配置保留。对照conditions/esRequest/items/total与各范围、桶、误差字段。非法输入400，ES缺索引502，连接不可用503；正常空集200。

打开 http://127.0.0.1:18080/f09.html ，点击查询，勾选/取消城市或主题，再提交，核对数字/ID/价格与观察区实际请求。数字保留另一维条件；失败清除旧卡片与计数。展示壳由课程提供，不需编写前端。

05只用 tut-f09-candidates，2主0副本，仍在同一学习节点，不是多节点实验。routing=a/b须分别落到shard0/1，两份_search_shards响应先核对不同。20份单标签文档：分片0 A5/C4/B1，分片1 B5/C4/A1。核对create/green、Bulk20项created、refresh、count20。size1/shard_size1→A5，整体误差上界10，A桶上界5，其他计数15；size1/shard_size4→C8，上界0、其他计数12；size3/shard_size4→C8/A6/B6，上界0、其他计数0。都是size0不返回卡片，hits.total仍20。误差上界不是实际误差；上界0也不能保证返回了所有桶。

本课3个案例，28条教学HTTP请求=准备6+范围2+主搜索5+Java5+候选10。点名清理2、启动探活、作者附加检查/错误场景/浏览器重复调用另计。脚本输出连续JSON，逐个看完整响应；不把构建成功当实验通过。

## 点名清理与第二轮

```bash
bash labs/f09/cleanup.sh
```

仅删除本课两个索引，200/404都表示已清理，不删除卷、不碰F03–F08或业务资源。再次从01到05完整运行，Bulk应重新created；Java进程可复用。清理后F09页面搜索应502，重新01导入后恢复。结束时关闭自己启动的Java；专用ES原本停止时可用同一compose的stop es恢复，不执行down -v。

作者[两轮真实记录](../../review/f09/README.md)与[阅读验收](../../../../docs/framework-review/20261020-f09-facets/README.md)分别保存；作者脚本可选，不是学习前提。
