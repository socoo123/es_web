#!/usr/bin/env python3
"""Verify cached F14 ICU9.4.0 bytes, or download exact official bytes."""
import hashlib, io, json, pathlib, urllib.request, zipfile
HERE=pathlib.Path(__file__).resolve().parent
lock=json.loads((HERE/'plugins.lock.json').read_text())
p=lock['plugins'][0]
target=HERE/'.artifacts/analysis-icu.zip'
previous=HERE.parent/'f14/.artifacts/analysis-icu.zip'
source=target if target.exists() else previous
if source.exists():
    data=source.read_bytes(); origin='verified cache: '+str(source)
else:
    with urllib.request.urlopen(p['url'], timeout=60) as response: data=response.read()
    origin=p['url']
if hashlib.sha512(data).hexdigest()!=p['sha512']: raise SystemExit('ICU SHA512 mismatch')
properties=dict(line.split('=',1) for line in zipfile.ZipFile(io.BytesIO(data)).read('plugin-descriptor.properties').decode().splitlines() if '=' in line and not line.startswith('#'))
if properties.get('elasticsearch.version')!=lock['es_version'] or properties.get('version')!=lock['es_version']: raise SystemExit('ICU descriptor version mismatch')
target.parent.mkdir(exist_ok=True);target.write_bytes(data)
print(json.dumps({'source':origin,'sha512':p['sha512'],'descriptor':properties},ensure_ascii=False,indent=2))
