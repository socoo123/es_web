# F14 · 中文分词方案的受控比较

[教程](../../../../framework/f14.html) · [12份资料](../../data/f14/attractions.json) · [4份意图与相关ID](../../data/f14/judgments.json) · [实际token/漏召回/误召回矩阵](../../search/f14/expected.json) · [两轮原始证据](../../review/f14/README.md)。只操作独立F14节点19214及`tut-f14-attractions`，前课19200和源码篇9200/9201不参与。

ES9.4.0/Lucene10.4.0，单节点/一主零副本/strict/refresh_interval=-1，金额整数分/CNY。所选城市、open、0–10000分（含端点），match AND，业务ID升序；没有评分排名结论。name=standard，name.smartcn=smartcn，name.icu=icu_analyzer，name.ik_smart=ik_smart，name.ik_max=ik_max_word；各字段索引与查询用相同方案。对比完整analyzer及随包规则，不是只控制tokenizer的实验。

需要Docker/Compose、Bash、curl、Python3.10+标准库，应用需JDK25。沿用Boot4.0.8、官方Java与Rest5 Client9.4.8、Wrapper3.3.4/Maven3.9.11；作者应用Temurin25.0.4.1+1/macOS arm64，ES使用镜像自带JVM。没有外部字典、同义词、拼音或数据库。运行前19214/18080应空闲；已有F14索引要先明确点名清理。

## c01：独立可用的内置基线，20条教学HTTP

从仓库根目录开始：

```bash
cd projects/travel-search
export ES_URL=http://127.0.0.1:19214
docker compose -f infra/f14/compose.yaml up -d es
bash infra/f14/wait.sh
bash labs/f14/01-prepare-baseline.sh
bash labs/f14/02-baseline.sh
```

准备6请求=版本/PUT创建/green/Bulk12created/refresh/count12；后续14=节点插件清单+mapping+settings、4分析、4搜索、3个未安装analyzer返回400。创建已存在应停下，不以更新覆盖代替清理。初始节点插件清单应为空。

实际基线：故宫/BJ命中bj-east,bj-palace,bj-punctuation,bj-separated；长江/NJ命中nj-bridge,nj-hotel,nj-restaurant,nj-scattered；长江大桥/NJ命中nj-bridge,nj-restaurant；CAFE/BJ空。误入/漏掉的判断见固定人工意图，未执行插件列不能填0。

## c02：版本、哈希、安装与真实比较，64条教学HTTP

下载可能受网络与制品变化影响；失败时保留基线，其他方案记不可用，不能改锁文件来接受未知包。记录目前兼容事实：[制品锁](../../infra/f14/plugins.lock.json)、[下载/descriptor收据](../../review/f14/artifacts.json)。Elastic两个包核对官方SHA512；IK使用维护方地址及本地指纹，不声称有独立官方签名。Dockerfile的`--batch`接受安装器要求；IK本轮提示旧Security Policy及outbound_network，完整日志保留。

以下会删除F14索引中的12份资料；不删卷和别课资源。仍在projects/travel-search：

```bash
python3 infra/f14/fetch.py
docker compose -f infra/f14/compose.yaml -f infra/f14/compose.plugins.yaml build es
bash labs/f14/cleanup.sh
docker compose -f infra/f14/compose.yaml stop es
docker compose -f infra/f14/compose.yaml -f infra/f14/compose.plugins.yaml up -d --no-build es
bash infra/f14/wait.sh
bash labs/f14/03-prepare-plugins.sh
bash labs/f14/04-compare.sh
```

只把插件加到独立派生镜像，基础Compose仍为原版；新容器启动加载插件。官方要求所有集群节点安装/重启，本课只有1节点。两个索引配置均从固定文件创建，插件安装不替旧字段重新分析。准备6、节点/mapping/settings3、五方案各7份分析35、四查询×五方案20=64。脚本核对插件名与版本、完整有效mapping/settings、所有token/position/offset与ID矩阵。大表与原始响应不要只看返回码。

三段样本分析：北京故宫博物院、南京市长江大桥、全角Ｃａｆｅ 城市咖啡馆；另分析4个查询。五方案索引/查询都用同一analyzer，未测试max索引+smart查询组合。ik-smart分别漏故宫博物院与长江大桥；ik-max补回短词，但长江/NJ仍误入餐厅；ICU对全角归一不代表已解决路名语义。SmartCN本轮四个小查询全符判断，不代表旅游搜索总体最佳。

手工等价操作：

```bash
curl --fail-with-body -sS -X POST http://127.0.0.1:19214/tut-f14-attractions/_analyze -H 'Content-Type: application/json' --data-binary @search/f14/analyze-bridge.json
curl --fail-with-body -sS -X POST http://127.0.0.1:19214/tut-f14-attractions/_search -H 'Content-Type: application/json' --data-binary @search/f14/icu/bridge.json
```

## c03：Java与真实观察窗，24条教学HTTP

第二终端，从仓库根目录；确认java -version为25，环境配置见[backend说明](../../backend/README.md)：

```bash
cd projects/travel-search/backend
./mvnw -B clean package
ES_URL=http://127.0.0.1:19214 java -jar target/travel-search-0.7.0.jar
```

回第一终端（projects/travel-search）：

```bash
bash labs/f14/05-java.sh
```

6份输入（standard/SmartCN/ICU故宫，IK两模式长江，ICU CAFE），每份Java1+REST重放两份分析和搜索3=24。比较token/position/offset、ID/次序/价格/score/sort/total/relation。108=20+64+24指脚本显式发出的教学请求，Java每次内部两分析+一搜索另计，不重复纳入108；清理/探活/下载/安装/作者附加与浏览器重复操作另计。

打开`http://127.0.0.1:18080/f14.html`。故宫/BJ由standard4→SmartCN2/ICU2→ik-smart1→ik-max2；长江/NJ分别4/2/3/1/3；CAFE/BJ分别0/1/1/0/0。观察完整ID和两列token，不只看数字。右侧固定样本为NJ桥、SY故宫、BJ故宫（CAFE输入用全角咖啡馆）；只是当前方案模拟写入，不是读取存量词项。条件改变清空结果，再提交。

API`POST /api/attractions/analyzer-search`，输入白名单：q非空白且1–60 UTF-16单位，BJ/NJ/SY，0–100000000整数分预算，五个candidate之一。错误400；插件/索引拒绝502；连接不可用503；不完整搜索502。默认Java端点18080，脚本APP_URL与JavaAPP_PORT自行对应。默认索引可在Java启动前由TRAVEL_F14_INDEX配置，浏览器不能改索引或analyzer。基线时只选standard，插件不可用显示502，不伪报0。浏览器→Java→ES，Pages只承载教程。

## 点名清理与重做

在projects/travel-search，删除本课索引后GET应404：

```bash
bash labs/f14/cleanup.sh
bash labs/f14/03-prepare-plugins.sh
bash labs/f14/04-compare.sh
bash labs/f14/05-java.sh
```

若重做完整未安装→安装：先cleanup，插件Compose stop es；用`docker compose -f infra/f14/compose.yaml up -d --force-recreate es`恢复stock镜像，wait后从01/02继续，再按c02/c03走。每次重导必须12created，不静默删数据、不清卷、不碰前课。

结束cleanup、关闭自己启动的Java，插件Compose stop es保留卷。没有PIT或词典热更新资源。作者完整两轮命令（会反复只重建F14容器、清理本课索引，Java需保持启动）：

```bash
python3 review/f14/verify.py
```

没有执行的插件/性能/多节点/质量评估要标未验，不能把作者快照当本机执行。
