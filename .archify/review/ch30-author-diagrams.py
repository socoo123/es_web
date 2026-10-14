"""Reproduce ch30's authored JSON; HTML is generated only by official finalize."""
from pathlib import Path
import json
root=Path(__file__).resolve().parents[2]
stamp='20261014-084552'
rev='2e8528e92361c3399724226deaf2b46f933e925b'
base='server/src/main/java/org/elasticsearch/'
def source(path,a,b,label):return {'path':base+path,'line':a,'end_line':b,'label':label}
def node(id,lane,col,label,sub,sources=None):
 n={'id':id,'lane':lane,'col':col,'type':'backend','label':label,'sublabel':sub,'width':264,'height':70}
 if sources:n['sources']=sources
 return n
def write(slug,title,lanes,nodes,labels,cards,repo=False):
 folder=root/f'.archify/workflow-ch30-{slug}-{stamp}';folder.mkdir(exist_ok=True)
 path=str((folder/f'{slug}.html').relative_to(root))
 meta={'title':title,'locale':'zh-CN','quality_profile':'showcase','animation':'trace','output':path,
 'legend':{'entries':{'backend':{'label':'职责交接' if repo else '阅读与验证步骤'}}}}
 if repo:meta['repository']={'url':'https://github.com/elastic/elasticsearch.git','revision':rev,'provider':'github','link_mode':'web'}
 for i,n in enumerate(nodes):
  n['col']=2;n['width']=420;n['yOffset']=-55 if i%2==0 else 55
 ids=[n['id'] for n in nodes]
 edges=[{'id':f'{a}-to-{b}','from':a,'to':b,'label':label,'variant':'emphasis','role':'main'} for a,b,label in zip(ids,ids[1:],labels)]
 data={'schema_version':2,'diagram_type':'workflow','meta':meta,'lanes':[{'id':i,'label':s} for i,s in lanes],
 'nodes':nodes,'edges':edges,'mainPath':ids,'cards':cards}
 (folder/'candidate.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 return path
paths={}
paths['search-handoffs']=write('search-handoffs','普通多分片搜索：请求如何交接职责',
 [('entry','REST 适配与协调入口'),('query','分片 Query → 协调归并'),('fetch','按候选取回字段 → 组装响应')],
 [node('rest','entry',1,'REST → SearchRequest','解析参数，再 execute(TYPE)',[source('rest/action/search/RestSearchAction.java',132,148,'请求适配与动作调用')]),
 node('action','entry',2,'协调节点选择分片','读取 ClusterState；启动搜索相位',[source('action/search/TransportSearchAction.java',399,409,'集群状态读取'),source('action/search/TransportSearchAction.java',2157,2190,'Query Then Fetch 分支')]),
 node('query','query',2,'分片预处理与 Query','先检查窗口；使用已取得的搜索读者',[source('search/SearchService.java',977,990,'先建上下文再执行 Query'),source('search/DefaultSearchContext.java',358,383,'结果窗口检查')]),
 node('reduce','query',1,'协调归并候选','普通分页保留全局目标结果',[source('action/search/FetchSearchPhase.java',92,99,'归并 Query 结果'),source('action/search/SearchPhaseController.java',543,555,'普通分页与 rank 分支')]),
 node('fetch','fetch',1,'Fetch 目标文档','按分片分组，只向持有者取字段',[source('action/search/FetchSearchPhase.java',130,152,'目标 docId 分组与发送')]),
 node('response','fetch',2,'组装 SearchResponse','合并结果，交给下一相位',[source('action/search/FetchSearchPhase.java',268,283,'Fetch 结果合并')])],
 ['内部调用','分片执行','候选返回','目标分组','结果合并'],
 [{'dot':'cyan','title':'图的适用范围','items':['固定 ES 9.4.0；普通多分片、按分数分页的职责图。箭头是处理与结果交接，不代表每条都走网络。','省略安全、rewrite、can-match、DFS、PIT、跨集群、rank、失败重试与提前归并。']},
 {'dot':'amber','title':'单分片实验的边界','items':['本课是一主片零副本；普通单分片无 rank 可在 Query 内执行 Fetch，不能用本课响应证明多节点网络两跳。','窗口检查发生在分片上下文 preProcess，进入主查询前；与协调归并的 from + size 算术是不同位置。']}],True)
paths['reading-loop']=write('reading-loop','从一条 API 建立可验证的源码笔记',
 [('entry','先确认 HTTP 路径与内部接头'),('mechanism','沿动作到执行点 · 标明分支与适用条件'),('evidence','定位测试约束 · 对照真实响应')],
 [node('route','entry',1,'查 routes()','确认路径模板与 HTTP 方法'),node('type','entry',2,'抄 execute(TYPE)','分开 REST 名、Action 名、相位名'),
 node('action','mechanism',2,'找动作注册与 doExecute','先沿普通成功路径阅读'),node('boundary','mechanism',1,'停在实际执行或检查点','写清发生位置、输入与条件'),
 node('tests','evidence',1,'用问题定位测试','解析找单测；HTTP 契约找 YAML'),node('api','evidence',2,'运行请求并记录差异','清理重做；把差异反馈到笔记')],
 ['内部接头','动作入口','执行边界','约束定位','响应对照'],
 [{'dot':'cyan','title':'这是一张方法图','items':['箭头表示作者的阅读顺序，不是 Elasticsearch 的运行时调用链，也不保证每个类都有同名 Tests。','路径 → routes() → TYPE 是常用入口；模块内部算法可从已确认的调用点继续，不要求都有独立 REST 路径。']},
 {'dot':'amber','title':'三类证据各自回答什么','items':['源码定位检查在哪里发生；测试列出被保护的条件；API 给出当前环境的实际响应。','状态码相同不代表检查位置相同。测试存在也不等于本轮已经运行 Gradle 测试。']}])
(root/'.archify/review/ch30-paths.json').write_text(json.dumps(paths,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(paths,ensure_ascii=False))
