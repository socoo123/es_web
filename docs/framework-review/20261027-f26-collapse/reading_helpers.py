#!/usr/bin/env python3
"""F26 作者验收：真实 HTTP/离线阅读；ES 运行记录在工程 review/f26。"""
import copy
import datetime
import functools
import hashlib
import http.server
import json
import pathlib
import re
import threading
import traceback
from urllib.parse import unquote, urlsplit
from playwright.sync_api import sync_playwright
import os
BROWSER = os.environ.get("F26_BROWSER_EXECUTABLE", str(pathlib.Path.home()/"Library/Caches/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-mac-arm64/chrome-headless-shell"))

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WIDTHS = [1920, 1440, 1024, 768, 390, 320]
THEMES = ["light", "dark"]


def require(value, detail):
    if not value:
        raise AssertionError(detail)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if not self.path.startswith("/es_web/"):
            self.send_error(404); return
        self.path = self.path[len("/es_web"):]
        super().do_GET()

    def log_message(self, *args):
        pass


def observe(page, record):
    page.on("pageerror", lambda error: record["js_errors"].append(str(error)))
    page.on("response", lambda response: record["http_failures"].append({"url": response.url, "status": response.status}) if response.status >= 400 else None)
    page.on("requestfailed", lambda request: record["request_failures"].append({"url": request.url, "failure": request.failure}))


def diagrams(page, theme):
    page.wait_for_function("""theme => [...document.querySelectorAll('[data-d2-light]')].every(img => {
      const expected = new URL(theme === 'dark' ? img.dataset.d2Dark : img.dataset.d2Light, location.href).href;
      return img.complete && img.naturalWidth > 0 && img.currentSrc === expected && img.closest('figure').querySelector('[data-expand-d2]').href === expected;
    })""", arg=theme)
    result = page.locator("[data-d2-light]").evaluate_all("images => images.map(i => ({src:i.currentSrc, width:i.naturalWidth, height:i.naturalHeight, alt:i.alt}))")
    require(len(result) == 2, result)
    return result


def measure(page, chapter=True):
    result = page.evaluate("""chapter => {
      const art = chapter ? document.querySelector('article.chapter') : document.querySelector('main.wrap');
      const rect = art.getBoundingClientRect();
      const blocks = chapter ? [...art.querySelectorAll(':scope > header, :scope > section, :scope > footer, .lesson > h2, .d2-figure, .d2-figure > figcaption, .lesson > pre.code-block, .lesson > .code-tools')].map(el => {
        const r=el.getBoundingClientRect(); return {tag:el.tagName,id:el.id,left:r.left,right:r.right};}) : [];
      const scrollables = [...art.querySelectorAll('table.ktable, .d2-view, pre.code-block')].map(el=>{
        const initial=el.scrollLeft; el.scrollLeft=el.scrollWidth; const moved=el.scrollLeft; el.scrollLeft=initial;
        return {tag:el.tagName,id:el.id,client:el.clientWidth,scroll:el.scrollWidth,overflow:getComputedStyle(el).overflowX,moved};});
      return {viewport:innerWidth,page:document.documentElement.scrollWidth,body:document.body.scrollWidth,
        theme:document.documentElement.dataset.theme,left:rect.left,right:rect.right,width:rect.width,blocks,scrollables};
    }""", chapter)
    require(result["page"] <= result["viewport"] and result["body"] <= result["viewport"], result)
    if chapter:
        require(abs(result["width"] - min(880, result["viewport"] - (28 if result["viewport"] <= 600 else 44))) <= 1, result)
        for block in result["blocks"]:
            require(abs(block["left"] - result["left"]) <= 1 and abs(block["right"] - result["right"]) <= 1, {"misaligned":block})
        for container in result["scrollables"]:
            if container["scroll"] > container["client"] + 2:
                require(container["overflow"] in ["auto", "scroll"] and container["moved"] > 0, container)
    return result


def anchors(page):
    page.emulate_media(reduced_motion="reduce")
    page.locator(".chapter-outline summary").click()
    links = page.locator('.chapter-outline a, .diagram-jumps a[href^="#"]')
    result = []
    for i in range(links.count()):
        href = links.nth(i).get_attribute("href")
        require(page.locator(href).count() == 1, href)
        links.nth(i).click()
        signals = page.evaluate("""href=>({href,top:document.querySelector(href).getBoundingClientRect().top,bar:document.querySelector('.topbar').getBoundingClientRect().bottom})""", href)
        require(signals["top"] >= signals["bar"] - 1, signals)
        result.append(signals)
    page.locator(".chapter-outline summary").click()
    return result


def shot(page, name, target=None):
    path = HERE / "screenshots" / (name + ".png")
    if target:
        header = page.locator(".topbar")
        if header.count():
            header.evaluate("el=>el.style.visibility='hidden'")
        try:
            page.locator(target).first.screenshot(path=str(path), timeout=20000)
        finally:
            if header.count():
                header.evaluate("el=>el.style.visibility=''")
    else:
        page.screenshot(path=str(path), timeout=20000)
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path), "visual_review": "pending"}


def static_links():
    checked = []
    for name in ['framework/f26.html', 'framework/f25.html', 'framework/index.html', 'framework/diagrams/f26/README.md',
                 'projects/travel-search/README.md', 'projects/travel-search/labs/f26/README.md', 'projects/travel-search/review/f26/README.md',
                 'docs/framework-review/20261027-f26-collapse/README.md']:
        path=ROOT/name
        contents=path.read_text()
        links=re.findall(r'(?:href|src|data-d2-light|data-d2-dark)="([^"]+)"',contents) if path.suffix=='.html' else re.findall(r'\]\(([^)]+)\)',contents)
        for link in links:
            parsed=urlsplit(link)
            if parsed.scheme or parsed.netloc: continue
            target=path.parent/unquote(parsed.path) if parsed.path else path
            require(target.exists(), {'file':name,'link':link})
            if parsed.fragment and target.suffix=='.html':
                require(f'id="{parsed.fragment}"' in target.read_text(), {'missing_anchor':link})
            checked.append({'file':name,'link':link})
    return checked
