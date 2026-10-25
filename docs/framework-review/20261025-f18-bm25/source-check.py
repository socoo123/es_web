import pathlib,json,urllib.request,hashlib,datetime
R=pathlib.Path(__file__).resolve().parents[3];D=pathlib.Path(__file__).resolve().parent;rows=[]
files=['server/src/main/java/org/elasticsearch/index/similarity/SimilarityService.java','server/src/main/java/org/elasticsearch/index/similarity/SimilarityProviders.java','server/src/main/java/org/elasticsearch/lucene/similarity/LegacyBM25Similarity.java','server/src/main/java/org/elasticsearch/action/explain/TransportExplainAction.java']
for f in files:
 url='https://raw.githubusercontent.com/elastic/elasticsearch/v9.4.0/'+f
 with urllib.request.urlopen(url,timeout=40) as r:official=r.read()
 local=(R/'es-src'/f).read_bytes();assert local==official,f
 rows.append({'path':f,'url':url,'sha256':hashlib.sha256(local).hexdigest(),'local_matches_official':True})
f='lucene/core/src/java/org/apache/lucene/search/similarities/BM25Similarity.java';url='https://raw.githubusercontent.com/apache/lucene/releases/lucene/10.4.0/'+f
with urllib.request.urlopen(url,timeout=40) as r:data=r.read()
rows.append({'path':f,'url':url,'sha256':hashlib.sha256(data).hexdigest(),'local_matches_official':'downloaded official tag; ES counterpart has compatibility factor'})
(D/'sources.json').write_text(json.dumps({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'version':'ES9.4.0/Lucene10.4.0','files':rows,'docs':['https://www.elastic.co/docs/reference/elasticsearch/index-settings/similarity','https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-explain','https://www.elastic.co/docs/reference/query-languages/query-dsl/query-filter-context','https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-search'],'limits':'Current docs supplement the pinned source and real runtime; not a source for untested version behavior'},ensure_ascii=False,indent=2)+'\n')
print('Pinned ES sources match; official Lucene10.4.0 downloaded')
