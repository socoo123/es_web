import importlib.util,pathlib,time,json
r=pathlib.Path(__file__).resolve().parents[4];p=r/'projects/travel-search'
spec=importlib.util.spec_from_file_location('f11lab',p/'labs/f11/lab.py');lab=importlib.util.module_from_spec(spec);spec.loader.exec_module(lab)
conditions=lab.load('search/f11/input-price.json')
pit=lab.call('POST','/tut-f11-attractions/_pit?keep_alive=1s&allow_partial_search_results=false')['id']
a=lab.call('POST','/api/attractions/pages/start',conditions,app=True)
t0=time.monotonic();print('Waiting 66 seconds without searching or renewing either view',flush=True)
time.sleep(66)
b=lab.load('search/f11/pit-page.json');b['pit']={'id':pit,'keep_alive':'1m'}
lab.search(b,True,expected=404)
lab.call('POST','/api/attractions/pages/next',{'cursor':a['cursor'],'afterPage':1,'conditions':conditions},app=True,expected=410)
result={'scope':'real native 1s PIT expiry and Java 60s idle cursor expiry','elapsed_without_renewal_s':time.monotonic()-t0,'operations':lab.RECORD,'status':'passed'}
(p/'review/f11/expiry.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
