#!/usr/bin/env python3
"""Local F40 fault injection only; never a production reverse proxy."""
import gzip, http.server, json, socket, threading, urllib.error, urllib.request

class Proxy:
    def __init__(self, out):
        self.mode='off';self.out=out;self.lock=threading.Lock()
        owner=self
        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self,*args): pass
            def do_GET(self): self.handle_request()
            def do_POST(self): self.handle_request()
            def handle_request(self):
                if self.headers.get('Transfer-Encoding','').lower()=='chunked':
                    chunks=[]
                    while True:
                        size=int(self.rfile.readline().split(b';',1)[0],16)
                        if size==0:
                            while self.rfile.readline() not in [b'\r\n',b'\n',b'']:pass
                            break
                        chunks.append(self.rfile.read(size));assert self.rfile.read(2)==b'\r\n'
                    body=b''.join(chunks)
                else:body=self.rfile.read(int(self.headers.get('Content-Length','0')))
                if self.headers.get('Content-Encoding')=='gzip':body=gzip.decompress(body)
                mode=owner.mode if self.path.startswith('/_bulk') else 'off'
                record={'path':self.path,'injection':mode,'bytes':len(body)}
                headers={k:v for k,v in self.headers.items() if k.lower() not in ['host','content-length','connection','content-encoding','transfer-encoding']}
                skipped=None
                if mode=='429':
                    status=429;value={'error':{'type':'es_rejected_execution_exception','reason':'F40 injected request 429'},'status':429}
                    raw=json.dumps(value).encode()
                else:
                    if mode=='item429_once':
                        lines=body.splitlines();record['original_items']=len(lines)//2
                        assert len(lines)>=4,'Need two or more operations'
                        skipped=json.loads(lines[-2])['update'];body=b'\n'.join(lines[:-2])+b'\n'
                        record['forwarded_items']=len(lines[:-2])//2;owner.mode='off'
                    req=urllib.request.Request('http://127.0.0.1:20440'+self.path,data=body if body else None,method=self.command,headers=headers)
                    try:
                        with urllib.request.urlopen(req,timeout=15) as response: status=response.status;raw=response.read()
                    except urllib.error.HTTPError as e:status=e.code;raw=e.read()
                    if skipped:
                        value=json.loads(raw);value['errors']=True
                        value['items'].append({'update':{'_index':'tut-f40-attractions-v001','_id':skipped['_id'],'status':429,'error':{'type':'es_rejected_execution_exception','reason':'F40 injected item 429; item was not forwarded'}}})
                        raw=json.dumps(value).encode()
                    if mode=='drop_once':
                        owner.mode='off';record.update(upstream_status=status,acknowledgement='dropped_after_real_ES_write');owner.record(record)
                        self.close_connection=True
                        try:self.connection.shutdown(socket.SHUT_RDWR)
                        except OSError:pass
                        self.connection.close();return
                record['status']=status;owner.record(record)
                self.send_response(status);self.send_header('Content-Type','application/vnd.elasticsearch+json;compatible-with=9')
                self.send_header('X-Elastic-Product','Elasticsearch');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
        self.server=http.server.ThreadingHTTPServer(('127.0.0.1',20441),Handler)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True)
    def record(self,value):
        with self.lock:
            with (self.out/'fault-proxy.jsonl').open('a') as f:f.write(json.dumps(value)+'\n')
    def start(self):self.thread.start()
    def close(self):self.server.shutdown();self.server.server_close();self.thread.join()
