#!/usr/bin/env python3
"""Author self-review: link F34 teaching conclusions to actual evidence; not independent review."""
import collections,datetime,json,pathlib,re
R=pathlib.Path(__file__).resolve().parents[3];D=pathlib.Path(__file__).resolve().parent;P=R/'projects/travel-search'
rec={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reviewer':'author self-review','independent':False,'lesson':'F34','checks':[]}
def load(p):return json.loads(p.read_text())
def check(name,ok,detail):
 assert ok,(name,detail)
 rec['checks'].append({'name':name,'passed':True,'detail':detail})
for n in ['01','02']:
 out=P/('review/f34/run-'+n);s=load(out/'summary.json');es=[json.loads(x) for x in (out/'events.jsonl').read_text().splitlines()]
 check(n+'-round',s['passed'] and s['teaching_http_total']==65 and s['http_by_kind']['java-api']==4,'65=16+25+24 teaching REST; identity/guard/cleanup/wait and browser extras separate')
 good=load(out/'before-delete-snapshot.json');partial=load(out/'missing-primary-snapshot.json');status=load(out/'missing-primary-status.json')
 check(n+'-complete',good['state']=='SUCCESS' and good['shards']=={'total':2,'successful':2,'failed':0} and not good['failures'],'Backup metadata, not accepted alone')
 check(n+'-partial',partial['state']=='PARTIAL' and partial['shards']=={'total':3,'successful':2,'failed':1}
       and partial['failures'][0]['index']=='tut-f34-risk' and status['state']=='SUCCESS' and status['shards_stats']['failed']==1,'Metadata PARTIAL vs status completed SUCCESS, failed=1')
 restore=load(out/'restore-partial-accepted-response.json')
 check(n+'-partial-restore',restore['snapshot']['shards']=={'total':3,'successful':2,'failed':1}
       and load(out/'partial-is-not-complete.json')['risk_restored_count']==0,'HTTP200 with failed1 and EMPTY_STORE: incomplete is not complete')
 check(n+'-full-restore',load(out/'restore-good-response.json')['snapshot']['shards']=={'total':2,'successful':2,'failed':0},'Isolated name; full fields and two-node reads in complete-fields.json')
 check(n+'-expected-errors',collections.Counter(e['status'] for e in es if e['kind']=='teaching' and e['status']>=400)=={500:3,404:2},'Bad path, incomplete restore, open-name collision 500; deleted document 404 twice')
 layout=load(out/'final-layout.json');check(n+'-layout',len(layout)==12 and all(x['state']=='STARTED' for x in layout),'Main4 + risk1 + complete restored4 + partial main2 + empty partial risk1')
 stages=['01-before-backup','02-delete-reaches-replicas','03-restored-isolated-live-unchanged','04-read-validated-historical-copy']
 java=[load(out/(stage+'-java.json')) for stage in stages]
 check(n+'-java', [[(x['id'],x['ticketPriceFen']) for x in v['items']] for v in java]==[[('p01',6000),('p02',0)],[('p01',6500)],[('p01',6500)],[('p01',6000),('p02',0)]],'Same process, same search contract and generated DSL replayed')
 browser=[load(out/(stage+'-browser.json')) for stage in stages]
 check(n+'-browser',all(x['passed'] and len(x['calls'])==4 and not x['direct_es'] for x in browser),'16 real browser->Java calls + 16 independent REST replays, 1440/390 light/dark')
html=(R/'framework/f34.html').read_text();plain=re.sub(r'<pre\b.*?</pre>|<script\b.*?</script>|<style\b.*?</style>','',html,flags=re.S);plain=re.sub('<[^>]+>','',plain)
rec['chinese_characters_excluding_code']=len(re.findall('[\u4e00-\u9fff]',plain));rec['code_blocks']=html.count('class="code-block"')
check('structure',all('class="'+x+'"' in html for x in ['goal','lesson','drills','pitfalls','recap','ch-footer']),'Business deletion -> replica/backup definitions -> fixed sample -> API/results/counterexamples -> capability -> F35')
check('scope',html.count('<details')==14 and html.count('class="callout warn"')==4 and '0机制播放器' in html,'8 folded exercises, 4 traps, 2 static figures; no frontend development')
check('sources',len(load(D/'sources.json')['sources'])==4 and all(x['local_equal_official_v9_4_0'] for x in load(D/'sources.json')['sources']),'4 targeted files byte-equal to official v9.4.0; separate API evidence')
check('diagrams',all(x['exit_code']==0 for x in load(R/'framework/diagrams/f34/generation.json')['checks']),'Official D2 v0.9.0; fmt/check/validate and four exports; no manual SVG edits')
check('manual',load(P/'review/f34/manual/summary.json')['passed'],'53 actual curl responses, four Java points; not a third formal run')
check('reading',load(D/'http-review.json')['passed'] and load(D/'supplement-review.json')['passed'],'HTTP/file, 12 lesson viewport-theme combinations, 24 real clipboard copies, 14 details, 16 independent SVG views, final directory clicks')
check('visual',load(D/'visual-review.json')['passed'],'94 screenshots via 12 contact sheets + 8 individual images actually viewed; 102 originals covered')
rec['content_read_through']=['Replica propagates legitimate updates and logical deletion; backup restores historical data, not automatically latest business facts.','Controlled write block + refresh make six-document baseline deterministic; not a mandatory production snapshot pause. Snapshot shard views span start/end interval.','Shared fs content/path/whitelist/filesystem permissions; same-host repository volume is not physical disaster recovery; API deletion only, no manual segment-file edits.','Accepted is not terminal; metadata vs status endpoint semantics; failures and successful shard counts independently checked; no capture of transient IN_PROGRESS claimed.','Missing risk primary, PARTIAL, returned original node does not repair old snapshot, default restore rejection, opt-in EMPTY_STORE loss demonstration; HTTP200 failed1 cannot pass complete restore.','Open-name conflict; anchored rename; exclude global/feature state and aliases; restored index retains snapshot write block; wait for replicas and inspect full data/query before read alias switch.','Same application process; operational APIs stay out of visitor interface; source retains five current docs; historical 6000 vs legitimate 6500 requires business reconciliation beyond F34.','Exact cleanup and original volumes; repeat formal runs; failed pre-runs segregated; F35 remains unimplemented.']
rec['validation_corrections']=['repository volume root permissions','health 408 waiting','status API completed-state mapping','partial restore response failed-shard count']
rec['author_review_script_correction']='The first post-run review counted literal <details> and excluded the outline with a class attribute; corrected to count <details starts. No ES or page behavior changed.'
rec['published_old_lesson_errata']=[];rec['reasoning_runtime_limit']=load(D/'reasoning.json');rec['passed']=True
(D/'content-review.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n');print('F34 author teaching/evidence review passed')
