import json,pathlib,urllib.request
root=pathlib.Path(__file__).resolve().parents[3]/'projects/travel-search';out=root/'review/f39'
body=json.loads((out/'run-03/reopened-apply.json').read_text())[0]['projection']['bulk_ndjson']
request=urllib.request.Request('http://127.0.0.1:20339/_bulk?require_alias=true',data=body.encode(),method='POST',headers={'Content-Type':'application/x-ndjson'})
with urllib.request.urlopen(request,timeout=20) as r:status=r.status;response=json.load(r)
assert status==200 and not response['errors'] and len(response['items'])==1 and response['items'][0]['index']['_id']=='p02'
get=json.load(urllib.request.urlopen('http://127.0.0.1:20339/tut-f39-attractions-read/_doc/p02'))
expected=json.loads((out/'run-03/summary.json').read_text())['final_documents']['p02'];assert get['_source']==expected
(out/'rest-bulk-replay.json').write_text(json.dumps({'passed':True,'source':'run-03/reopened-apply.json','method':'POST','path':'/_bulk?require_alias=true','content_type':'application/x-ndjson','body':body,'status':status,'response':response,'get_after':get,'same_final_document':True,'separate_from_round_http_counts':True},ensure_ascii=False,indent=2)+'\n')
print('F39 actual REST Bulk replay passed')
