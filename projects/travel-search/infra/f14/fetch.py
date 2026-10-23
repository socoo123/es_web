#!/usr/bin/env python3
"""Download exact F14 plugin bytes. A failed download leaves the baseline usable."""
import hashlib
import io
import json
import pathlib
import urllib.request
import zipfile

HERE = pathlib.Path(__file__).resolve().parent
lock = json.loads((HERE / 'plugins.lock.json').read_text())
cache = HERE / '.artifacts'
cache.mkdir(exist_ok=True)
for plugin in lock['plugins']:
    target = cache / (plugin['name'] + '.zip')
    data = target.read_bytes() if target.exists() else urllib.request.urlopen(plugin['url'], timeout=60).read()
    if hashlib.sha512(data).hexdigest() != plugin['sha512']:
        raise SystemExit(f"Hash mismatch: {plugin['name']}; do not install these bytes")
    archive = zipfile.ZipFile(io.BytesIO(data))
    descriptor = archive.read('plugin-descriptor.properties').decode()
    properties = dict(line.split('=', 1) for line in descriptor.splitlines() if '=' in line and not line.startswith('#'))
    if properties.get('elasticsearch.version') != lock['es_version']:
        raise SystemExit(f"Wrong ES version: {plugin['name']}")
    target.write_bytes(data)
    print(plugin['name'], 'verified SHA512 and ES', properties['elasticsearch.version'])
