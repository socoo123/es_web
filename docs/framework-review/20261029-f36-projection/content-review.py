#!/usr/bin/env python3
"""Evidence-linked author self-review; this is not independent model review."""
import datetime, hashlib, json, pathlib, re
D=pathlib.Path(__file__).resolve().parent;R=D.parents[2];P=R/'projects/travel-search'
def read(p):return json.loads(p.read_text())
rec={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reviewer':'author self-review',
     'independent_reviewer':False,'scope':'F36 plus necessary navigation/progress only','checks':[]}
def check(name,ok,detail):
    assert ok,(name,detail);rec['checks'].append({'name':name,'passed':True,'detail':detail})
html=(R/'framework/f36.html').read_text()
plain=re.sub('<[^>]*>','',re.sub(r'<pre\b[\s\S]*?</pre>','',html))
rec['chinese_characters_excluding_code']=len(re.findall('[\u4e00-\u9fff]',plain))
check('teaching-structure',all('class="'+x+'"' in html for x in ['goal','lesson','drills','pitfalls','recap','ch-footer']) and html.count('<details')==12 and html.count('class="callout warn"')==4,
      'business need -> source facts/projection/key -> SQL/REST/Java -> relation change -> two-session snapshot gap -> controlled reconciliation -> next lesson/cleanup; eight folded capabilities')
for run in ['01','02']:
    out=P/('review/f36/run-'+run);summary=read(out/'summary.json');check('formal-round-'+run,summary['passed'],'SQL/ES/Java and observer records passed')
    teaching=sum(r['count'] for r in summary['http_counts'] if r['case'].startswith('f36-c'))
    check('operation-count-'+run,teaching==26 and summary['java_bulk_calls']==3,'22 REST + 4 Java search entrypoints + 3 Java Bulk calls; setup/cleanup/browser extras separate')
    snap=read(out/'03-snapshot-session.json');check('snapshot-'+run,snap['same'] and snap['first_projection']==snap['second_projection'],'first query RR view retained through B commit; actual separate SQL sessions')
    stages=read(out/'03-stage-evidence.json');check('boundaries-'+run,stages['source_and_es_full_fields_equal'] and not stages['automatic_event_capture'] and stages['checkpoint'] is None,
      'known three keys and no other writer, GET versus SEARCH, full-field equality; no continuous catch-up claim')
    for stage in ['01-initial','03-snapshot-gap','03-before-refresh','03-after-refresh']:
        obs=read(out/(stage+'-browser.json'));check('real-browser-'+run+'-'+stage,obs['passed'] and len(obs['calls'])==4 and not obs['direct_es'],'1440/390 x light/dark, actual Browser -> Java, independent DSL REST replay')
check('manual-reader-path',read(P/'review/f36/manual/summary.json')['passed'] and read(P/'review/f36/manual/summary.json')['missing_delete_404_without_error_accepted'],
      'published SQL/curl/Java scripts executed separately after cleanup; psql begin/end files and cmp; missing-delete branch actually exercised')
check('build-runtime',read(P/'review/f36/runtime.json')['passed'],'Boot4.0.8/JDK25.0.4.1+1/Java-Rest5 Client9.4.8/Maven3.9.11 actual build; PG17.5 digest and ES9.4.0 identities; bundled JVM separate; no unit-test pass claimed')
check('diagram-generation',read(R/'framework/diagrams/f36/generation.json')['passed'],'D2 v0.9.0/dagre, two sources/four SVGs, fmt/check/validate/export/sha256')
http=read(D/'http-review.json');check('http-and-interaction',http['passed'] and len(http['copies'])==20 and http['details_toggled']==12,'six widths x two themes, 880px, relative URLs, all real clipboard copies, progress isolation, reduced motion/file/focus and independent figures')
check('final-navigation',read(D/'supplement-review.json')['passed'],'real directory and previous/next lesson clicks, theme-correct expansion popups, all details open on 1440/390/320')
check('actual-visual-review',read(D/'visual-review.json')['passed'],'eight contact sheets/94 originals plus four directly inspected originals; supplemental screenshot included separately')
check('shutdown',read(P/'review/f36/shutdown.json')['passed'],'named schema/index cleanup, final digest config restart same UUID, app/ES ports closed, containers stopped/two volumes preserved, existing secure node unchanged')
rec['read_through']=[
 'Database source of truth versus ES derived search projection; SQL join is in PG, no automatic ES cross-index join or sync is implied.',
 'Three minimal tables, per-attraction boundary, stable explicit _id and complete tags array, integer CNY fen and coordinates, open index versus retained closed delete.',
 'Fixed ID prevents duplication for repeated same payload; it is not stale-write or tombstone version protection. Java full index replaces source, partial update is not used.',
 'City/tag changes affect projected fields even when attraction row is unchanged; entire tiny set is re-exported here, no automatic multi-table event router claimed.',
 'REPEATABLE READ first SELECT fixes the read view, not BEGIN; B commits while A remains open, A exports same old data. Database read snapshot distinguished from F34 ES backup.',
 'Artificially known keys and stopped other writers give a bounded reconciliation demonstration; no WAL coordinate, Kafka offset or CDC checkpoint is manufactured.',
 'HTTP Bulk/item status and complete fields, GET and SEARCH refresh separation, same count but changed IDs and prices, real shell only displays original card fields.',
 'Initial import errors, absent-delete branch, cleanup/restart/secret files/isolated ports are explicit; security disabled in this separate localhost fixture is not deployment validation.',
 'F37 single-table PG log pipeline, F38 independent MySQL, F39 routing, F40 replay/order, F41 continuous rebuild, F42 delay/reconciliation retain their boundaries.'
]
rec['published_errata']=[]
rec['limitations']=['WAL/binlog/Debezium/Kafka not implemented','no event consumer/offset/capture/restart recovery','no physical-delete capture','no continuous multi-table catch-up','no ordering/replay protection','same Docker VM, no HA/performance/security deployment validation']
rec['reasoning']=read(D/'reasoning.json');rec['passed']=True
(D/'content-review.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n');print('F36 author teaching/evidence self-review passed')
