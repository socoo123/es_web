#!/usr/bin/env python3
"""本地浏览器验收：python3 tools/console-review-server.py，然后打开 /tools/console-browser-check.html。"""
import json
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit
ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / '.archify/review/console-20261012/browser.json'
class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)
    def do_GET(self):
        if self.path.startswith('/es_web/'):
            self.path = self.path[7:]
        if urlsplit(self.path).path == '/console.html' and '__qa=1' in self.path:
            html = (ROOT / 'console.html').read_text().replace('<head>', '<head><script>window.__qaErrors=[];addEventListener("error",e=>__qaErrors.push(e.message));addEventListener("unhandledrejection",e=>__qaErrors.push(String(e.reason)));</script>', 1).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(html)))
            self.end_headers()
            self.wfile.write(html)
        else:
            super().do_GET()
    def do_POST(self):
        if self.path != '/__qa/report':
            self.send_error(404)
            return
        report = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        self.send_response(204)
        self.end_headers()
if __name__ == '__main__':
    ThreadingHTTPServer(('127.0.0.1', 8766), Handler).serve_forever()
