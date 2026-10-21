# F11 · 稳定分页与PIT（本机手工入口）

先读[正文](../../../../framework/f11.html)。ES9.4.0 / Lucene10.4.0，Boot4.0.8 / JDK25（作者Temurin25.0.4.1+1）/ 官方Java与Rest5 Client9.4.8 / Wrapper3.3.4、Maven3.9.11。应用JDK与ES bundled JVM分开，先让JAVA_HOME/PATH指向JDK25。脚本只依赖Bash、curl、Python3标准库。Pages只承载教程。

仓库根目录，终端一：

```bash
cd projects/travel-search
docker compose -f infra/single-node/compose.yaml up -d es
bash infra/single-node/wait.sh
bash labs/f11/01-prepare.sh
bash labs/f11/02-offsets.sh
bash labs/f11/03-view.sh
```

只创建tut-f11-attractions，1主0副本/strict，完整保留F10十六份全部字段值；准备六请求检查版本、acknowledged、green且未超时、Bulk16项created/errors=false、refresh零失败、count16。curl只检查HTTP错误，200不替代条级/等待响应核对。重复建索引先停下按本课清理，不拿updated当首次created。

02按from=0/3/6、size=3读三页，再观察9999+3超默认10000窗口的400。03先固定ID重导（updated）/refresh，普通与PIT首屏后明确把far1000→15000分、tea8000→500分并refresh；普通from/size与无PIT search_after均far重复、tea遗漏，PIT保留原9份各一次及原价。脚本打印每条完整HTTP请求/响应，动态搬运真实PIT id和完整sort；不用猜_id、_shard_doc或格式化价格拼游标。

原次序（均完整ID）：a-fz-xihu、a-hz-xihu、a-hz-far、a-hz-guide、a-hz-missing-location、a-hz-plain、a-hz-tea、a-sh-exhibit、a-hz-boundary。原价0/0/1000/1000/1000/1000/8000/10000/20000分。

新普通搜索：a-fz-xihu、a-hz-xihu、a-hz-tea、a-hz-guide、a-hz-missing-location、a-hz-plain、a-sh-exhibit、a-hz-far、a-hz-boundary。03还截短显式三项sort触发400，关闭PIT后搜索404，finally释放本次未关闭的最新PIT并重导/refresh原资料。遇连接故障，记录当前PIT id并恢复后点名关闭；不能声称finally保证外部服务故障时立即释放。ES keep_alive兜底。

终端二从仓库根目录：

```bash
cd projects/travel-search/backend
./mvnw -version
./mvnw -B -ntp clean package
java -jar target/travel-search-0.7.0.jar
```

终端一继续：

```bash
bash labs/f11/04-java.sh
```

Java沿用F10全部硬条件与三模式，显式加_shard_doc，PIT请求无index/routing/preference。04三模式逐页将Java实际DSL在同一PIT中重放REST，逐项核对ID、完整sort、评分与票价；总数9/eq，九份各一次。末页next409、关闭后410、条件改变或错误页序409。三案例共60条教学HTTP请求=准备6+偏移4+视图19+Java/REST对照31；点名清理、探活及作者附加故障/过期检查另计。

## 本机观察页与接口

打开 http://127.0.0.1:18080/f11.html 。点击“从第一页开始”→“下一页”两次→末页禁用→“关闭这一轮”；修改条件清空旧卡片/页序并关闭旧轮，再重新搜索。每页卡片与下方真实DSL/DTO一致。课程提供界面，不需前端开发；浏览器→同源Java→ES，没有浏览器直连ES。

- POST /api/attractions/pages/start：输入为[PageInput样本](../../search/f11/input-price.json)，search含F10全部必填参数；pageSize整数1–5。
- POST /api/attractions/pages/next：cursor、afterPage（当前已读页号，从1开始）、conditions（完整原PageInput）；一轮固定所有条件与页大小，旧页序/改变409，末页409。
- POST /api/attractions/pages/close：`{"cursor":"从响应复制真实cursor"}`；Java已无会话时幂等200；原生ES重复close可能404，二者契约分开。

cursor是Java内存句柄，不是ES PIT id。服务端保留最新pit_id和List<FieldValue>，不会从卡片重建sort。PIT keep_alive=1m，每次查询续期；Java闲置60秒失效，每5秒扫描尝试释放，最多100会话。正常结束须主动关闭，页签离开只尽力发起关闭；ES期限兜底。程序重启会丢内存会话，从第一页开始。并发next按afterPage防重复消费，网络丢响应不提供幂等重放，重新开始；本机串行服务不是生产多实例方案。

400非法输入、409条件/页序/末页、410关闭/过期/ES视图失效、502缺索引或不完整搜索、503连接不可用；正常空集200。失败清空旧卡片与页序，关闭后重新搜索。ES端点只在服务端，默认ES_URL=http://127.0.0.1:19200；TRAVEL_F11_INDEX可覆盖本课默认索引，手工REST脚本固定隔离名称，不把环境变量当任意资源删除入口。

## 点名清理与重做

先在观察页关闭本轮，然后：

```bash
bash labs/f11/cleanup.sh
bash labs/f11/01-prepare.sh
bash labs/f11/02-offsets.sh
bash labs/f11/03-view.sh
bash labs/f11/04-java.sh
```

仅删除本课索引，200/404可继续。重建16项再次created，视图案例重置为updated；同一ID/价格基线再次成立。关闭自己启动的Java；框架ES原来停止时用相同compose stop es恢复，不删卷/旧课/源码篇资源。

[作者两轮ES/Java](../../review/f11/README.md)与[HTTP/视觉/展示壳](../../../../docs/framework-review/20261021-f11-pagination/README.md)分别记录。附加原生PIT1s等待66秒失效、Java60秒闲置410不计入正常主流程。验收脚本不是读者学习前提。
