#!/usr/bin/env python3
import datetime,hashlib,json,pathlib
D=pathlib.Path(__file__).resolve().parent;R=D.parents[2];P=R/'projects/travel-search';E=P/'review/f30'
def load(p):return json.loads(p.read_text())
http=load(D/'http-review.json');assert http['passed']
rows=load(D/'content-review.json')['rounds'];shells=[load(p) for p in sorted((E/'round1').glob('*-browser.json'))]
assert len(shells)==7 and all(s['passed'] for s in shells)
calls=[c for s in shells for c in s['calls']];assert len(calls)==28 and sum('rest_replay' in c for c in calls)==20
shell={'actual_browser_java_http':28,'independent_rest_replays':20,'success_http':20,'error_http':8,'direct_browser_es':sum(len(s['direct_es']) for s in shells),'js_errors':[x for s in shells for x in s['js_errors']],'phases':[s['stage'] for s in shells],'passed':True}
(D/'shell-review-summary.json').write_text(json.dumps(shell,ensure_ascii=False,indent=2)+'\n')
visual={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reviewer':'root author; actual tool image viewing','contact_sheets_viewed':['contact-'+str(i)+'.jpg' for i in range(1,8)],'contact_scope':'54 final HTTP reading PNGs and 28 actual shell PNGs, in 7 contact sheets','whole_diagrams_viewed':[f'whole-{s}-{t}.png' for s in ['two-decisions','shard-recovery'] for t in ['light','dark']],'code_screenshots_viewed':[f'java-{s}-{w}-{t}.png' for s in ['request','search'] for w in [1440,390] for t in ['light','dark']],'findings':['Single 880px column; mobile overflow remains inside graph/code/table containers.','First wide comparison graph was replaced with vertical groups and regenerated via D2.','Diagram labels, lines/arrows and both themes are legible; static figures do not promise animation.','Java code uses local horizontal scrolling; left and right portions observed, all 23 snippets separately copied through actual Clipboard API.','Real shell displays 60/65/70 yuan; both failure contexts clear result cards and recover afterward.'],'limitation':'Contact sheets provide layout coverage, not pixel-by-pixel or character-by-character visual review of every full-size screenshot. First code screenshot attempt captured scroll-in-progress; fixed with instant scrolling and final 8 code PNGs viewed.','passed':True}
(D/'visual-review.json').write_text(json.dumps(visual,ensure_ascii=False,indent=2)+'\n')
(E/'README.md').write_text('''# F30 真实实验：两轮通过

[正文](../../../../framework/f30.html) · [运行入口](../../labs/f30/README.md) · [作者内容交叉核对](../../../../docs/framework-review/20261028-f30-failover/content-review.json)。

ES9.4.0/Lucene10.4.0，四进程在同Docker VM。m1/m2仅master，m3 master/data/ingest，d1仅data；三票、两data、1主1副。原卷持久化，HTTP仅回环19430–19433，无认证。`setup/identity.json`保存首启形成后移除引导名单、UUID与node ID核对。

| 收据 | 每轮教学HTTP | 准备 / 轮询 | 最终资料 |
| --- | --- | --- | --- |
| [round1](round1/summary.json) | 75 REST＋7 Java接口 | 准备11次HTTP；轮询51次（含准备中的6次） | 6份完整_source；p01=7000分；两拷贝一致 |
| [round2](round2/summary.json) | 75 REST＋7 Java接口 | 准备4次HTTP；轮询38次 | 同上，先点名清理并从6000分重做 |

75 REST=初态12＋c01的16＋c02的15＋c03的32，包含配套字段核对和Java返回DSL重放。`events.jsonl`每行保存原请求、响应、状态码与阶段；Java接口内层ES请求、客户端重试没有抓包计数。guard/identity/cleanup/command另分标签，准备与轮询有交集，不能直接相加为教学数量。

- c01：两轮实际停专用master m1/m2，分别选出m3/m1，选举term增长；当时分片主副位置及primary term不变。6500分确认2拷贝，元数据创建与删除成功，原节点回归。
- c02：停m1+m2，活m3/d1没有master且block2、原三票配置保留；默认write策略下d1仍能读6500，改9900返回503 cluster_block_exception，建索引返回503 master_not_discovered_exception。回归后仍6500、6份资料，失败创建的索引404。
- c03：实验前保证专用master；两轮实际主片均在d1，停后原同步副本m3提升，primary term 1→2 / 2→3，master保持原身份。wait=1写7000确认1份；wait=all写9900拒绝。d1带原卷回归、PEER/DONE且两拷贝全字段一致。再停m3+d1，m1+m2保留两票和master，red/主副UNASSIGNED，业务搜索/写入503；wait=0创建元数据ack/shards_ack为true，但分片仍UNASSIGNED。点名删临时索引，再带原卷恢复并查回全部资料。

每轮UUID `Nhg5IH1VTh2DzrnUNUg5wA`及四个node ID前后相同。索引每轮重建，创建版本/settings/mapping分别记录，不能用green或总数代替字段核对。投票列表以集合比较，源顺序不构成语义。

[构建与运行](runtime.json)：Boot4.0.8 / Temurin25.0.4.1+1 / Java与Rest5 Client9.4.8 / Maven3.9.11；ES内置JVM26.0.1。clean package、依赖树、类路径通过；无测试源，不声称单元测试通过。共享Java/前端未改，三个静态资源源码/包内/实际HTTP字节一致。

首轮7稳定点×1440/390×浅深=28浏览器→Java真实HTTP，20成功与8错误，成功另做20 REST重放；[汇总](../../../../docs/framework-review/20261028-f30-failover/shell-review-summary.json)。浏览器直连ES=0。单入口m1停机与全部data离线都触发503 SEARCH_UNAVAILABLE，原因由原始REST区分。[一次独立Java诊断](java-failure-probe.log)在全data离线窗口证实客户端顶层ResponseException属于IOException；它不是额外的Web接口，SDK调用单计。

`attempts/`保留未算通过的执行：五进程资源试案、投票列表顺序比较问题、Java错误码预期修正及恢复。首次五进程的master限额384MiB不足；调整后VM压力意外OOM了原es-study-secure。停止本课资源后原容器/原UUID恢复healthy，正式改四进程；[影响与恢复说明](../../../../docs/framework-review/20261028-f30-failover/README.md)。没有原业务字段基线，不声称逐项对账。

[最终清理](../../../../docs/framework-review/20261028-f30-failover/workspace-state.json)：只删本课两个索引，Java SIGTERM且18081关闭；四容器及网络移除、四卷保留；原安全节点在恢复后采样至清理保持同PID/StartedAt/healthy。无网络分区、卷丢失、随机并发、跨机器、客户端多入口、性能或恢复时限验证。
''')
(D/'README.md').write_text('''# F30 内容、图解与阅读验收

[正文](../../../framework/f30.html) · [本机实验](../../../projects/travel-search/labs/f30/README.md) · [真实两轮](../../../projects/travel-search/review/f30/README.md)。只实施F30及必要目录/前课导航/当前摘要，未实施F31；共享Java与前端未改。

- **内容**：[作者自审与响应交叉核对](content-review.json)。约5400汉字（不含代码），3案例、每轮75教学REST＋7 Java接口HTTP、1独立SDK诊断、2静态D2、8练习、4陷阱。先讲入口、投票、目标分片，再看REST/Java与恢复。无独立代理，不能把作者自审称为独立审阅。
- **依据**：[sources.json](sources.json)保存5份官方v9.4.0源码与本地字节SHA一致的核对。官方动态文档与固定源码、实测分别记录；没有以源码代替运行。
- **图解**：[generation.json](../../../framework/diagrams/f30/generation.json)：D2v0.9.0、dagre、主题4/201，fmt/fmt --check/validate/四次导出及2源4SVG哈希；只修改D2、正式重新生成。初版过宽导致嵌入文字小，已改纵向分类。静态图不宣称动画。
- **HTTP阅读**：[http-review.json](http-review.json)：1920/1440/1024/768/390/320×浅深=12组；最大880px、主区边界差≤1px、整页零横向溢出。16独立图组、12必要关联页、29锚点、13折叠、23次真实剪贴板复制、主题同步/重载、已读设置/目录反映/前课隔离/取消、file双主题、reduced-motion与键盘焦点通过。最终JS/HTTP/非预期请求错误=0，Pages业务请求=0。检查器单列图源切换可取消的SVG请求，最终运行该项也为0。
- **实际视觉**：[visual-review.json](visual-review.json)。54阅读PNG与28真实观察窗PNG通过7份总览实际查看；4整图与8 Java代码截图另逐份查看。限定布局、图文与左右滚动可读性，非所有原图逐像素或完整代码逐字审阅。首次代码截图受平滑滚动影响取到页首，已改瞬时定位并重拍、复看；截图存在不等于自动通过。
- **Java与展示壳**：[构建/运行](../../../projects/travel-search/review/f30/runtime.json)、[浏览器汇总](shell-review-summary.json)。28真实Java请求中20成功/8错误，20独立REST重放。原始ES503在本客户端实际进入ResponseException/IOException分支，和m1断线一样被服务转为503；作者稿502预期已改。未新增前端或Controller，未声明多入口HA。
- **资源异常与恢复**：初始五进程试案在master384MiB限制下先OOM；调512MiB后VM压力于2026-10-28 10:35:48上海时间意外OOM原安全节点。[中断](existing-node-oom.json)有原始Docker状态。停止本课容器后，于10:38:17启动原容器，[恢复](existing-node-restored.json)验证原容器ID/原UUID与healthy。原业务字段没有事前基线，未逐项对账。改用四进程完成正式两轮；[后续监测](existing-node-monitor.jsonl)268次采样保持同PID/StartedAt/healthy，[最终状态](workspace-state.json)证明仅清本课资源、保留四卷与原安全节点。
- **运行入口偏好**：[reasoning.json](reasoning.json)。AGENTS记录xhigh；逐课提示词保存后来的gpt-6.1-sol/max。当前入口无法设置或自行读回，不声称实际切换；本轮作者实施、自审，不启动子代理。
- **边界**：单Docker VM、固定6份资料、进程SIGKILL、原卷回归；没有网络分区、磁盘丢失、随机并发、跨机器、快照、性能或恢复时间承诺。准备步骤与轮询另计，单入口失败不能推导所有data不可读。

[最终检查](checks.json)分列站点/片段/Python/JSON/Compose/图哈希；GitHub提交推送与Pages发布在实际执行后核对，发布收据保存于工作树外，避免把待执行状态写成成功。
''')
# This note is now an actual result, not future acceptance language.
p=R/'framework/f30.html';s=p.read_text().replace('正式两轮、请求统计及审阅范围由实际收据汇总。','正式两轮均通过；每轮75教学REST与7次Java接口HTTP，准备/轮询及额外浏览器请求分别计数。');p.write_text(s)
p=D/'reasoning.json';r=load(p);r['agents_md_preference']=r.pop('agencies_preference',r.get('agents_md_preference'));p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
print('F30 final reports reconciled with actual receipts')
