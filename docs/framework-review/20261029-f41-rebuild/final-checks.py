#!/usr/bin/env python3
"""F41 scoped final checks; live integrations were executed in run-03/04."""
import ast, collections, datetime, gzip, hashlib, json, os, pathlib, subprocess
R=pathlib.Path(__file__).resolve().parents[3];D=pathlib.Path(__file__).resolve().parent;P=R/'projects/travel-search'
REC={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'commands':[]}
BASE=[os.environ['F41_BASE']] if os.environ.get('F41_BASE') else []
def check(ok,detail):
    if not ok:raise AssertionError(detail)
def command(args):
    r=subprocess.run(args,cwd=R,text=True,capture_output=True,timeout=90)
    row={'args':args,'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr};REC['commands'].append(row);check(r.returncode==0,row);return r.stdout
def main():
    command(['node','tools/check.mjs']);command(['node','tools/sync-framework-code.mjs','--check'])
    command(['bash','-n','projects/travel-search/labs/f41/java.sh']);command(['git','diff',*BASE,'--check'])
    scripts=list((P/'labs/f41').glob('*.py'))+list(D.glob('*.py'))
    for path in scripts:ast.parse(path.read_text(),filename=str(path))
    REC['python_ast']=[str(p.relative_to(R)) for p in scripts]
    rounds=[]
    for name in ['run-03','run-04']:
        p=P/'review/f41'/name;s=json.loads((p/'summary.json').read_text());check(s['passed'],name)
        check(s['source_events']==19 and s['fences']==4 and s['worker_runs']==16 and s['http_requests']==92,s)
        check(s['final_positions']['committed_next']=={'v1':19,'v2':19} and s['final_positions']['end']==19,s)
        check(s['final_revisions']=={'p01':6,'p02':2,'p03':2,'p04':5},s)
        events=json.loads((p/'final-events.json').read_text());check(len(events)==19,name)
        envelopes=[json.loads(e['value']) for e in events]
        check(collections.Counter(e['op'] for e in envelopes)=={'r':3,'c':16},name)
        check(sum(e['after']['kind']=='fence' for e in envelopes)==4,name)
        blocked=json.loads((p/'blocked-new-target.json').read_text());check(blocked['exit_code']==1,blocked)
        check([x['status'] for x in blocked['records'] if x['kind']=='item']==[403,403,403],blocked)
        check(not any(x['kind']=='commit' for x in blocked['records']),blocked)
        for key in ['snapshot-incomplete','lag','target-failure']:
            rejected=json.loads((p/('gate-reject-'+key+'.json')).read_text());check(rejected['rejected'] and rejected['aliases_unchanged'],rejected)
        rejected=json.loads((p/'rollback-reject-old-lag.json').read_text());check(rejected['rejected'] and rejected['aliases_unchanged'],rejected)
        late=json.loads((p/'late-snapshot-again.json').read_text());check([x['result'] for x in late['records'] if x['kind']=='item']==['noop']*3,late)
        for v in ['v1','v2']:check(json.loads((p/('empty-'+v+'.json')).read_text())['records'][-1]['processed']==0,name)
        switch=json.loads((p/'switch-cutover.json').read_text());check(switch['active']=='v2' and switch['gate']['backlog_after_fence']==2,switch)
        rollback=json.loads((p/'switch-rollback.json').read_text());check(rollback['active']=='v1' and rollback['gate']['high']==16,rollback)
        stages=['initial','backfill','cutover','new-live','rollback','final'];pids=[]
        for stage in stages:
            b=json.loads((p/(stage+'-browser.json')).read_text());check(b['passed'] and len(b['calls'])==4,b)
            pids.append(json.loads((p/(stage+'-java-search.json')).read_text())['pid'])
        check(len(set(pids))==1,pids)
        http=[json.loads(x) for x in (p/'http.jsonl').read_text().splitlines()]
        check(collections.Counter(x['base'] for x in http)=={'http://127.0.0.1:20541':82,'http://127.0.0.1:18341':4,'http://127.0.0.1:18091':6},name)
        items=[];bulk_commands=0
        for entry in s['workers']:
            result=json.loads((p/(entry['name']+'.json')).read_text());batch=[x for x in result['records'] if x['kind']=='item'];items.extend(batch);bulk_commands+=bool(batch)
        check(collections.Counter(x['status'] for x in items)=={200:25,201:8,403:3},name)
        check(bulk_commands==12,bulk_commands)
        rounds.append({'name':name,'source_events':19,'worker_runs':16,'coordinator_http':92,'java_commands_with_bulk_items':bulk_commands,'client_http_request_count':'not individually traced','bulk_items':36,'statuses':dict(collections.Counter(x['status'] for x in items)),'browser_submissions':24,'browser_rest_replays':24})
    (P/'review/f41/execution-audit.json').write_text(json.dumps({'at':REC['at'],'passed':True,'rounds':rounds,'counts_separated':True},ensure_ascii=False,indent=2)+'\n')
    for name in ['http-review.json','supplement-review.json','visual-review.json','content-review.json']:
        check(json.loads((D/name).read_text())['passed'],name)
    generation=json.loads((R/'framework/diagrams/f41/generation.json').read_text());check(generation['passed'],'D2 generation')
    for f,h in generation['sha256'].items():check(hashlib.sha256((R/'framework/diagrams/f41'/f).read_bytes()).hexdigest()==h,f)
    source=json.loads((D/'source-evidence.json').read_text());check(all(x['http_status']==200 and x.get('local_matches',True) for x in source['files']),source)
    for name in ['cleanup-final','down']:check(json.loads((P/'review/f41'/name/'summary.json').read_text())['passed'],name)
    check(json.loads((P/'review/f41/shutdown.json').read_text())['passed'],'shutdown')
    files=sorted(set(command(['git','diff',*BASE,'--name-only']).splitlines()+command(['git','ls-files','--others','--exclude-standard']).splitlines()))
    allowed={'STATUS.md','PLAN.md','FRAMEWORK_PLAN.md','FRAMEWORK_STANDARD.md','docs/framework-lesson-prompt.md','framework/index.html','framework/f40.html','framework/f41.html','projects/travel-search/README.md'}
    prefixes=['docs/framework-review/20261029-f41-rebuild/','framework/diagrams/f41/']+['projects/travel-search/'+x+'/f41/' for x in ['infra','cdc','data','labs','search','review']]
    check(all(f in allowed or any(f.startswith(prefix) for prefix in prefixes) for f in files),'Unrelated changed files')
    check(not any('/.local/' in f or '/target/' in f or '__pycache__/' in f or f.endswith('.class') for f in files),'Private/cache/build files included')
    secret_values=[]
    for f in ['pg-password.txt','cdc.properties']:
        raw=(P/'infra/f41/.local'/f).read_text().strip();secret_values.append((raw.split('=',1)[1] if f.endswith('.properties') else raw).encode())
    for f in files:
        raw=(R/f).read_bytes()
        if f.endswith('.gz'):raw=gzip.decompress(raw)
        check(all(secret not in raw for secret in secret_values),'Actual local secret in '+f)
    REC.update(passed=True,final_rounds=rounds,actual_secret_values_absent=True,changed_scope_files=len(files))
    (D/'checks.json').write_text(json.dumps(REC,ensure_ascii=False,indent=2)+'\n')
    # Exclude the manifest itself; it cannot contain a hash of itself.
    files=sorted(set(files+['docs/framework-review/20261029-f41-rebuild/checks.json','projects/travel-search/review/f41/execution-audit.json']))
    entries={f:hashlib.sha256((R/f).read_bytes()).hexdigest() for f in files if not f.endswith('/delivery-artifacts.json')}
    (D/'delivery-artifacts.json').write_text(json.dumps({'at':REC['at'],'sha256':entries},ensure_ascii=False,indent=2)+'\n')
    print('F41 site/snippets/syntax, two real rounds, evidence/diagram hashes, scope and actual secret exclusion: passed')
if __name__=='__main__':main()
