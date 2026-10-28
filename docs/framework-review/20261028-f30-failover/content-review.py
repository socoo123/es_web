#!/usr/bin/env python3
"""Machine cross-checks supplement the author's reading, not independent review."""
import datetime,hashlib,html,json,pathlib,re
D=pathlib.Path(__file__).resolve().parent;R=D.parents[2];P=R/'projects/travel-search'
def load(p):return json.loads(p.read_text())
reports=[]
for name in ['round1','round2']:
 out=P/'review/f30'/name;summary=load(out/'summary.json');assert summary['passed']
 e=load(out/'election.json');m=load(out/'minority.json');f=load(out/'data-failure.json');i=load(out/'identity.json')
 assert i['initial']['uuid']==i['final']['uuid'] and set(i['initial']['nodes'])==set(i['final']['nodes'])
 def coord(s):return s['metadata']['cluster_coordination']
 def shards(s):return s['routing_table']['indices']['tut-f30-attractions']['shards']['0']
 def term(s):return s['metadata']['indices']['tut-f30-attractions']['primary_terms']['0']
 assert e['before']['master_node']!=e['after']['master_node'] and coord(e['after'])['term']>coord(e['before'])['term']
 assert term(e['before'])==term(e['after'])
 assert not m['no_master_data_view'].get('master_node') and '2' in m['no_master_data_view']['blocks']['global']
 assert len(coord(m['before'])['last_committed_config'])==3
 assert set(coord(m['before'])['last_committed_config'])==set(coord(m['no_master_data_view'])['last_committed_config'])
 assert m['write_error']['error']['type']=='cluster_block_exception'
 assert m['metadata_error']['error']['type']=='master_not_discovered_exception'
 old=f['before'];prom=f['promoted'];old_replica=next(s for s in shards(old) if not s['primary']);new_primary=next(s for s in shards(prom) if s['primary'])
 assert old_replica['node']==new_primary['node'] and term(prom)>term(old)
 assert old_replica['allocation_id']['id'] in old['metadata']['indices']['tut-f30-attractions']['in_sync_allocations']['0']
 assert old['master_node']==prom['master_node']==f['all_data_down']['master_node']
 assert len(f['all_data_down']['nodes'])==2 and len(coord(f['all_data_down'])['last_committed_config'])==3
 assert all(s['state']=='UNASSIGNED' for s in shards(f['all_data_down']))
 assert f['metadata_creation_without_data']['acknowledged'] and f['metadata_creation_without_data']['shards_acknowledged']
 assert f['metadata_shards'][0]['state']=='UNASSIGNED'
 events=[json.loads(l) for l in (out/'events.jsonl').read_text().splitlines()]
 phases={c:sum(e['case']==c and e['kind']=='teaching' for e in events) for c in ['setup','f30-c01','f30-c02','f30-c03']}
 assert phases==summary['teaching_http_by_case']=={'setup':12,'f30-c01':16,'f30-c02':15,'f30-c03':32}
 assert load(out/'data-unavailable-java.json')['code']==load(out/'minority-entry-down-java.json')['code']=='SEARCH_UNAVAILABLE'
 reports.append({'round':name,'teaching_rest':sum(phases.values()),'java_interface_http':summary['java_requests'],'preparation_http':sum(e['case']=='preparation' and 'url' in e for e in events),'wait_http_including_preparation':summary['wait_http'],'elected_before':e['before']['nodes'][e['before']['master_node']]['name'],'elected_after':e['after']['nodes'][e['after']['master_node']]['name'],'stopped_primary':f['stopped_primary_service'],'primary_term_before':term(old),'primary_term_after':term(prom),'all_data_down_master':f['all_data_down']['nodes'][f['all_data_down']['master_node']]['name'],'final_count':6,'final_price_fen':7000,'in_sync_promotion_proved':True})
s=(R/'framework/f30.html').read_text();text=html.unescape(re.sub('<[^>]+>','',re.sub(r'<pre\b[\s\S]*?</pre>','',s)))
assert all('class="'+v+'"' in s for v in ['ch-header','goal','lesson','drills','pitfalls','recap','ch-footer'])
rec={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'author_self_review':True,'independent_reviewer':False,'rounds':reports,'chinese_characters_outside_pre':len(re.findall('[\u4e00-\u9fff]',text)),'cases':3,'diagrams':2,'players':0,'snippet_count':len(re.findall('<pre\\b',s)),'sha256_page':hashlib.sha256(s.encode()).hexdigest(),'content_review':[
 'Business question precedes APIs; entry reachability, voting majority and target shard availability distinguished.',
 'Mixed m3 role and preparation stops disclosed; actual master/node IDs chosen, not assumed fixed.',
 'Stable committed/accepted voting sets; majority condition not described as whole election protocol.',
 'Default no_master_block=write scoped to reachable copies and last state; no blanket read-availability promise.',
 'Primary promotion verified against prior in-sync replica allocation ID and separate primary term.',
 'wait_for_active_shards=1/all and metadata wait=0 scoped; acknowledgements do not prove available data.',
 'F07 Java request/search/error branches copied from unchanged project; real Rest5 ResponseException reconciles both 503 paths.',
 'All six complete sources checked repeatedly and separately on both copies; no green/count-only acceptance.',
 'SIGKILL process failures on one VM, original volumes, fixed data; no network partition/disk loss/SLO/HA-client claims.',
 'Initial five-node OOM interruption of pre-existing secure node disclosed with restoration and later monitoring.'
 ],'draft_corrections':['Voting config arrays compared as sets, not list ordering.','Observed Java all-data-down response is 503 via ResponseException/IOException, not proposed 502.','First D2 reflowed to vertical comparison so labels remain readable at the lesson width.'],'published_lesson_errata':[],'passed':True}
(D/'content-review.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n');print('F30 evidence cross-checks and author review recorded')
