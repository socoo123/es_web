#!/usr/bin/env python3
"""Author evidence-based review of F35; no independent reviewer claimed."""
import collections,datetime,json,pathlib,re,subprocess
D=pathlib.Path(__file__).resolve().parent;R=D.parents[2];P=R/'projects/travel-search'
def read(p):return json.loads(p.read_text())
rec={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'lesson':'F35','reviewer':'author self-review','independent':False,'checks':[]}
def check(name,ok,detail):
 assert ok,(name,detail)
 rec['checks'].append({'name':name,'passed':True,'detail':detail})
for n in ['01','02']:
 out=P/('review/f35/run-'+n);summary=read(out/'summary.json');events=[json.loads(x) for x in (out/'events.jsonl').read_text().splitlines()];teaching=[e for e in events if e['case'].startswith('f35-c')]
 check(n+'-counts',summary['passed'] and collections.Counter(e['case'] for e in teaching)=={'f35-c01':13,'f35-c02':14,'f35-c03':18} and sum(e['path']=='/api/attractions/search' for e in teaching)==8,'45 HTTP = 37 REST + 8 Java; identity/guard/cleanup/browser separate')
 tls=read(out/'tls-failures.json');check(n+'-TLS',len(tls)==2 and all(x['http_status'] is None for x in tls) and 'issuer' in tls[0]['reason'] and 'Hostname mismatch' in tls[1]['reason'],'wrong trust and verification name, same listener; no HTTP status')
 statuses=collections.Counter(e['status'] for e in teaching if e['status']>=400)
 check(n+'-errors',statuses=={401:3,403:10,502:4,503:1},str(statuses))
 for role,name in [({'data','ingest','master'},'travel-f35-n1'),({'data'},'travel-f35-n2')]:
  node=next(x for x in read(out/'identity.json')['nodes']['nodes'].values() if x['name']==name)
  check(n+'-'+name,set(node['roles'])==role and node['f35_config_evidence']['transport_verification_mode']=='full','same UUID and actual node roles; TLS settings/details checked separately')
 stages=['01-wrong-ca','02-invalid-key','03-writer-cannot-search','04-reader-after-update','05-reader-after-repair','06-revoked-key','07-file-replaced-old-client','08-restarted-rotated-key']
 expected=[None,None,None,[('p01',6500)],[('p01',6000),('p02',0)],None,None,[('p01',6000),('p02',0)]]
 browser_calls=0;replays=0
 for stage,rows in zip(stages,expected):
  java=read(out/(stage+'-java.json'))
  check(n+'-'+stage,[(x['id'],x['ticketPriceFen']) for x in java['items']]==rows if rows else java['code'] in ['SEARCH_UNAVAILABLE','SEARCH_BACKEND_REJECTED'],'canonical Java result or safe DTO')
  browser=read(out/(stage+'-browser.json'));check(n+'-'+stage+'-browser',browser['passed'] and len(browser['calls'])==4 and not browser['direct_es'] and not browser['js_errors'],'1440/390, light/dark; cards and displayed DTO checked')
  browser_calls+=len(browser['calls']);replays+=sum('rest_replay' in x for x in browser['calls'])
 check(n+'-browser-counts',browser_calls==32 and replays==12,'32 browser->Java plus 12 independent successful DSL REST replays')
 final=read(out/'final-documents.json');check(n+'-final',final['hits']['total']['value']==6 and len(final['hits']['hits'])==6,'all fixed records restored; successful full search')
 encoded=any('Authorization: ApiKey ' in json.dumps(e,ensure_ascii=False) and '[REDACTED]' not in json.dumps(e,ensure_ascii=False) for e in events)
 check(n+'-receipts',not encoded and all(e['response'].get('encoded')=='[REDACTED]' for e in teaching if isinstance(e['response'],dict) and 'encoded' in e['response']),'issuance response secret fields removed; exact-value scan separately recorded')
html=(R/'framework/f35.html').read_text();plain=re.sub(r'<pre\b.*?</pre>|<script\b.*?</script>|<style\b.*?</style>','',html,flags=re.S);plain=re.sub('<[^>]+>','',plain)
rec['chinese_characters_excluding_code']=len(re.findall('[\u4e00-\u9fff]',plain));rec['code_blocks']=html.count('class="code-block"')
check('teaching-structure',all('class="'+x+'"' in html for x in ['goal','lesson','drills','pitfalls','recap','ch-footer']) and html.count('<details')==12 and html.count('class="callout warn"')==4,'business risk, trust/authn/authz, sample, REST, Java, outcomes, rotation/recovery, cleanup; 8 folded capabilities')
check('diagrams',all(x['exit_code']==0 for x in read(R/'framework/diagrams/f35/generation.json')['checks']),'D2 v0.9.0, two sources/four exports; no manual SVG edits')
check('sources',all(x['local_equal_official_v9_4_0'] for x in read(D/'sources.json')['sources']),'two targeted official v9.4.0 sources byte-equal to local; current official API/client docs linked in lesson')
check('fresh-entry',read(P/'review/f35/fresh-init/summary.json')['passed'] and read(P/'review/f35/fresh-setup/summary.json')['passed'],'final corrected configuration initialized and formed from fresh volumes, including bootstrap removal')
check('manual',read(P/'review/f35/manual/summary.json')['passed'],'reader actual curl stages, independent manual Java update/repair/revoke/replace/restart; not a third formal automatic round')
check('build-runtime',read(P/'review/f35/runtime.json')['passed'] and read(P/'review/f35/runtime.json')['factory_review']['passed'],'Boot4.0.8 / Temurin25.0.4.1+1 / client9.4.8; package/resources equal; six invalid configurations rejected; blank legacy client constructed/closed, no legacy API request claimed')
check('http',read(D/'http-review.json')['passed'] and read(D/'supplement-review.json')['passed'],'12 viewport/theme combinations, 17 real clipboard copies, 12 details, diagram views, file/reduced motion/focus, final directory/nav/expand clicks')
check('visual',read(D/'visual-review.json')['passed'],'11 contact sheets covering 122 originals plus 3 originals actually inspected')
check('shutdown',read(P/'review/f35/shutdown.json')['passed'],'named resources/keys cleaned; F35 Java/containers stopped, three volumes preserved; original secure node unchanged')
snapshot=(P/'labs/f35/f07-client-baseline.java.txt').read_bytes();old=subprocess.check_output(['git','show','486e49bfd3241b665dafe7d56b0a6bc5544578ef:projects/travel-search/backend/src/main/java/dev/esweb/travel/EsConfiguration.java'])
check('previous-lesson-boundary',snapshot==old,'F07 visible code kept as original course snapshot; only source reference changed to preserve learning order')
rec['content_read_through']=['TLS certificate chain, validity and SAN checks precede HTTP; CA public certificate versus CA/server private key; Basic encoding does not encrypt; transport mutual TLS separate from HTTP API key identity.','Explicit role/user and key role_descriptors intersection, cluster=[] for application key, aliases versus direct physical resource authorization; read does not implement DLS/FLS or tenant isolation.','index/delete document operations versus index creation/deletion/settings/security management; require_alias is a request guard; read and write credentials are separate, refresh is admin in this fixed experiment.','REST statuses versus safe application DTO: 401/403 both map to502, TLS connection failure503; raw backend responses and secrets not delivered to browser.','Client is created once and closed by Spring; files loaded at startup; revocation and file replacement do not reload old client; intentionally disruptive learning sequence differs from production rotation.','Controlled refresh and six-record snapshot; post-write/repaired IDs and CNY integer prices; two TLS examples and HTTP operation counts separate; no frontend/CDC implementation.','Exact cleanup, isolated endpoints/subnet, original volumes/credentials lifecycle, same-VM/one-master/shared learning CA/short validity limits; no performance, HA, auto-renewal, DLS/FLS claims.']
rec['validation_corrections']=['explicit OpenSSL configuration for missing local default','SAN must include Docker numeric publish IP under full transport verification','Nodes Info filters SSL detail settings; verify actual container configuration','allow named ES internal log data streams in guard','recreated p02 is HTTP201, updated p01 HTTP200']
rec['published_old_lesson_errata']=[];rec['reasoning_runtime_limit']=read(D/'reasoning.json');rec['passed']=True
(D/'content-review.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n');print('F35 author teaching/evidence self-review passed')
