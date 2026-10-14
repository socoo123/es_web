#!/usr/bin/env python3
"""作者用：新版 F01 导学真实 HTTP/离线阅读验收；不启动 ES 或业务工程。"""
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

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WIDTHS = [1920, 1440, 1024, 768, 390, 320]
THEMES = ["light", "dark"]
BUSINESS_PORTS = {19200, 9200, 9201, 8080}


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if not self.path.startswith("/es_web/"):
            self.send_error(404)
            return
        self.path = self.path[len("/es_web"):]
        super().do_GET()

    def log_message(self, *args):
        pass


def require(condition, evidence):
    if not condition:
        raise AssertionError(evidence)


def normal(value):
    return re.sub(r"\s+", " ", value).strip()


def static_checks():
    plan = (ROOT / "FRAMEWORK_PLAN.md").read_text()
    cases = (ROOT / "FRAMEWORK_CASES.md").read_text()
    rows = re.findall(r"^\| (F\d{2}) \| (.*?) \| (.*?) \|$", plan, re.M)
    expected = [f"F{i:02}" for i in range(1, 46)]
    require([r[0] for r in rows] == expected, {"plan_ids": [r[0] for r in rows]})
    require(re.findall(r"^\| (F\d{2}) \|", cases, re.M) == expected, "case coverage continuity")
    checked_links = []
    documents = ["FRAMEWORK_PLAN.md", "FRAMEWORK_CASES.md", "FRAMEWORK_STANDARD.md",
                 "FRAMEWORK_HISTORY.md", "STATUS.md", "PLAN.md", "README.md", "AGENTS.md",
                 "CLAUDE.md", "CHAPTER_STANDARD.md", "docs/framework-lesson-prompt.md",
                 "projects/travel-search/README.md"]
    for name in documents:
        document = ROOT / name
        contents = document.read_text()
        require(contents.count("```") % 2 == 0, {"unbalanced_fence": name})
        for target in re.findall(r"\]\(([^)]+)\)", contents):
            parsed = urlsplit(target.strip("<>"))
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            resolved = document.parent / unquote(parsed.path)
            require(resolved.exists(), {"document": name, "missing_link": target})
            checked_links.append({"document": name, "target": target})
    require((ROOT / ".nojekyll").exists(), ".nojekyll absent")
    return rows, documents, checked_links


def attach_observers(page, record):
    page.on("pageerror", lambda error: record["js_errors"].append({"page": page.url, "error": str(error)}))
    page.on("response", lambda response: record["http_failures"].append(
        {"page": page.url, "url": response.url, "status": response.status}) if response.status >= 400 else None)
    page.on("requestfailed", lambda request: record["request_failures"].append(
        {"page": page.url, "url": request.url, "failure": request.failure}))


def protect_business_requests(context, record):
    def handle(route):
        parsed = urlsplit(route.request.url)
        if parsed.hostname in {"localhost", "127.0.0.1", "[::1]", "::1"} and parsed.port in BUSINESS_PORTS:
            try:
                source = route.request.frame.page.url
            except Exception:
                source = "unknown"
            item = {"page": source, "url": route.request.url, "action": "aborted before service access"}
            record["blocked_business_requests"].append(item)
            route.abort()
        else:
            route.continue_()
    context.route("**/*", handle)


def wait_images(page, theme):
    page.wait_for_function("""theme => {
      const images = [...document.querySelectorAll('[data-d2-light]')];
      return images.length === 2 && images.every(image => {
        const expected = new URL(theme === 'dark' ? image.dataset.d2Dark : image.dataset.d2Light, location.href).href;
        const expand = image.closest('figure').querySelector('[data-expand-d2]');
        return image.complete && image.naturalWidth > 0 && image.currentSrc === expected && expand.href === expected;
      });
    }""", arg=theme)
    return page.locator("[data-d2-light]").evaluate_all("""images => images.map(image => ({
      src: image.currentSrc, naturalWidth: image.naturalWidth, naturalHeight: image.naturalHeight,
      expand: image.closest('figure').querySelector('[data-expand-d2]').href, alt: image.alt
    }))""")


def measure_chapter(page):
    measurement = page.evaluate("""() => {
      const article = document.querySelector('article.chapter');
      const main = document.querySelector('main.wrap');
      const rect = article.getBoundingClientRect(), outer = main.getBoundingClientRect();
      const blocks = [...article.querySelectorAll(':scope > header, :scope > section, :scope > footer, .lesson > h2, figure.d2-figure, figure.d2-figure > figcaption, pre.code-block, .code-tools')]
        .map(element => { const r = element.getBoundingClientRect(); return {
          tag: element.tagName, id: element.id, class: element.className,
          left: r.left, right: r.right, width: r.width
        }; });
      const scrollables = [...article.querySelectorAll('.d2-view, table.ktable, pre.code-block')].map(element => {
        const r = element.getBoundingClientRect(), style = getComputedStyle(element);
        const before = element.scrollLeft;
        element.scrollLeft = element.scrollWidth;
        const actualScroll = element.scrollLeft;
        element.scrollLeft = before;
        return {tag: element.tagName, class: element.className, left: r.left, right: r.right,
          clientWidth: element.clientWidth, scrollWidth: element.scrollWidth,
          overflowX: style.overflowX, actualScroll};
      });
      return {viewport: innerWidth, theme: document.documentElement.dataset.theme,
        pageWidth: document.documentElement.scrollWidth, bodyWidth: document.body.scrollWidth,
        outerWidth: outer.width, readingWidth: rect.width, left: rect.left, right: rect.right,
        blocks, scrollables};
    }""")
    width = measurement["viewport"]
    expected = min(880, width - (28 if width <= 600 else 44))
    require(measurement["pageWidth"] <= width and measurement["bodyWidth"] <= width, measurement)
    require(abs(measurement["readingWidth"] - expected) <= 1, measurement)
    require(measurement["outerWidth"] <= 924.1, measurement)
    for block in measurement["blocks"]:
        require(abs(block["left"] - measurement["left"]) <= 1 and
                abs(block["right"] - measurement["right"]) <= 1, {"misaligned": block, "article": measurement})
    for item in measurement["scrollables"]:
        require(item["left"] >= -1 and item["right"] <= width + 1, item)
        if item["scrollWidth"] > item["clientWidth"] + 2:
            require(item["overflowX"] in {"auto", "scroll"} and item["actualScroll"] > 0, item)
    return measurement


def anchor_checks(page):
    outline = page.locator("details.chapter-outline")
    require(outline.count() == 1, "one discoverable chapter outline required")
    outline.locator("summary").click()
    require(outline.get_attribute("open") is not None, "outline did not open")
    page.emulate_media(reduced_motion="reduce")
    anchors = page.locator(".chapter-outline a[href^='#'], .diagram-jumps a[href^='#']")
    records = []
    def check_target(href, method):
        page.wait_for_function("href => location.hash === href", arg=href, timeout=3000)
        evidence = page.evaluate("""href => ({href,
          targetTop: document.querySelector(href).getBoundingClientRect().top,
          topbarBottom: document.querySelector('.topbar').getBoundingClientRect().bottom})""", href)
        require(evidence["targetTop"] >= evidence["topbarBottom"] - 1, {"anchor_obscured": evidence})
        records.append({**evidence, "method": method})
    for index in range(anchors.count()):
        anchor = anchors.nth(index)
        href = anchor.get_attribute("href")
        require(page.locator(href).count() == 1, {"missing_anchor": href})
        anchor.click()
        check_target(href, "visible outline or diagram jump click")
    toc_targets = page.locator(".toc a[href^='#']").evaluate_all("links => links.map(a => a.getAttribute('href'))")
    tested = {r["href"] for r in records}
    for href in sorted(set(toc_targets) - tested):
        require(page.locator(href).count() == 1, {"missing_generated_toc_target": href})
        page.evaluate("href => { location.hash = href; }", href)
        check_target(href, "fragment navigation for hidden generated TOC target")
    page.emulate_media(reduced_motion="no-preference")
    return records


def lesson_interactions(page, context, base):
    require(page.locator("article.chapter").get_attribute("data-ch") == "f01-v2", "new F01 read key")
    require(page.locator(".exp-slot, .fp-slot").count() == 0, "intro must have no execution or mechanism player")
    require(page.locator(".drills details").count() >= 3, "three folded exercises required")
    require(page.locator(".pitfalls .callout.warn").count() >= 2, "two concrete pitfalls required")
    exercises = []
    for index in range(page.locator(".drills details").count()):
        detail = page.locator(".drills details").nth(index)
        require(detail.get_attribute("open") is None, {"exercise_initially_open": index})
        detail.locator("summary").click()
        require(detail.get_attribute("open") is not None, {"exercise_not_opened": index})
        answer = detail.evaluate("element => element.innerText.replace(element.querySelector('summary').innerText, '').trim()")
        require(len(answer) > 15, {"exercise_answer_empty": index})
        exercises.append({"question": detail.locator("summary").inner_text(), "answer_length": len(answer)})
        detail.locator("summary").click()
    require(page.locator("pre.code-block").count() == 1, "intro has one illustrative JSON block")
    code = page.locator("pre.code-block code").inner_text()
    require(isinstance(json.loads(code), dict), "illustrative JSON must parse as an object")
    context.grant_permissions(["clipboard-read", "clipboard-write"], origin=base.rstrip("/").split("/es_web")[0])
    copy = page.locator(".copy-code")
    copy.click()
    page.wait_for_function("document.querySelector('.copy-code').textContent === '已复制'")
    copied = page.evaluate("navigator.clipboard.readText()")
    require(copied == code, {"clipboard_mismatch": True})
    copy.focus()
    require(copy.evaluate("element => document.activeElement === element"), "copy button keyboard focus")
    bad_next = page.locator(".pager a").evaluate_all("links => links.filter(a => /f02\\.html(?:$|[?#])/.test(a.href)).map(a => a.href)")
    require(not bad_next, {"nonexistent_next_lesson": bad_next})
    require(page.locator(".pager a[href='index.html']").count() >= 1, "return to framework directory")
    return {"folded_exercises": exercises, "pitfalls": page.locator(".pitfalls .callout.warn").count(),
            "clipboard": {"exact_match": True, "characters": len(copied), "json": json.loads(copied)},
            "keyboard_focus": "copy button focused", "next_lesson": "F02 has no nonexistent page link"}


def measure_directory(page, plan_rows):
    rows = page.locator(".curriculum-list > li").evaluate_all("""lessons => lessons.map(li => [
      li.querySelector('.curriculum-no').textContent, li.querySelector('h3').textContent,
      li.querySelector(':scope > p').textContent])""")
    require([[normal(x) for x in row] for row in rows] == [[normal(x) for x in row] for row in plan_rows],
            "directory and plan lesson titles/descriptions differ")
    statuses = page.locator(".curriculum-status").all_text_contents()
    require(statuses == ["可阅读"] + ["待编写"] * 44, {"directory_statuses": statuses})
    require(page.locator(".curriculum-stage").count() == 8, "eight stages")
    link = page.locator("a.card.curriculum-lesson-link[data-ch='f01-v2']")
    require(link.count() == 1 and link.get_attribute("href") == "f01.html", "F01 directory entry")
    require(page.locator("a[href]").evaluate_all("links => !links.some(a => /f(?:0[2-9]|[1-4]\\d)\\.html(?:$|[?#])/.test(a.href))"),
            "directory links to an unimplemented lesson")
    measure = page.evaluate("""() => {
      const main = document.querySelector('main'), style = getComputedStyle(main);
      return {viewport: innerWidth, theme: document.documentElement.dataset.theme,
        pageWidth: document.documentElement.scrollWidth,
        readingWidth: main.getBoundingClientRect().width - parseFloat(style.paddingLeft) - parseFloat(style.paddingRight),
        stageWidths: [...document.querySelectorAll('.curriculum-stage')].map(e => e.getBoundingClientRect().width)};
    }""")
    require(measure["pageWidth"] <= measure["viewport"] and measure["readingWidth"] <= 880.1, measure)
    require(all(abs(w - measure["readingWidth"]) <= 1 for w in measure["stageWidths"]), measure)
    page.emulate_media(reduced_motion="reduce")
    for stage in range(1, 9):
        page.locator(f".curriculum-nav a[href='#stage-{stage}']").click()
        page.wait_for_function("""id => location.hash === '#' + id &&
          document.getElementById(id).getBoundingClientRect().top >= document.querySelector('.topbar').getBoundingClientRect().bottom - 1""", arg=f"stage-{stage}")
    page.emulate_media(reduced_motion="no-preference")
    return measure


def take_shot(page, shot_dir, names, name, locator=None):
    if locator:
        locator.evaluate("""element => window.scrollTo({top: Math.max(0,
          element.getBoundingClientRect().top + scrollY - document.querySelector('.topbar').getBoundingClientRect().bottom - 14), behavior: 'instant'})""")
    else:
        page.evaluate("window.scrollTo({top: 0, behavior: 'instant'})")
    page.screenshot(path=str(shot_dir / name))
    names.append(name)


def run():
    HERE.mkdir(parents=True, exist_ok=True)
    shot_dir = HERE / "screenshots"
    shot_dir.mkdir(exist_ok=True)
    record = {"recorded_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "scope": "new F01 orientation reading and current curriculum entry; historical F01 execution records untouched",
              "automated_status": "running", "http_prefix": "/es_web/", "browser": "Playwright Chromium",
              "measurements": [], "directory_measurements": [], "interactions": [], "anchor_checks": [],
              "image_loads": [], "js_errors": [], "http_failures": [], "request_failures": [],
              "blocked_business_requests": [], "screenshots": [], "visual_review": "pending human image inspection",
              "execution_validation": "not applicable: F01 is an orientation lesson, no environment or ES/Java experiment",
              "not_run": ["ES/Java execution", "business demo shell", "plugins/cluster/CDC", "diagram generation"]}
    server = None
    try:
        plan_rows, documents, links = static_checks()
        record["structure"] = {"plan_lessons": 45, "case_coverage_lessons": 45, "stages": 8,
                               "local_document_links": links, "nojekyll": True}
        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Handler, directory=str(ROOT)))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        base = f"http://127.0.0.1:{server.server_port}/es_web/"
        record["http_origin"] = base
        diagram_urls = {}
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            record["browser_version"] = browser.version
            for width in WIDTHS:
                for theme in THEMES:
                    context = browser.new_context(viewport={"width": width, "height": 1000 if width > 600 else 900})
                    context.add_init_script(f"localStorage.setItem('es-web:theme', '{theme}'); localStorage.setItem('es-web:read', JSON.stringify({{f01:true}}));")
                    protect_business_requests(context, record)
                    page = context.new_page()
                    attach_observers(page, record)
                    page.goto(base + "framework/f01.html", wait_until="networkidle")
                    require(page.locator("html").get_attribute("data-theme") == theme, "initial site theme")
                    require(page.locator(".lesson > details").count() == 8, "eight expandable stage outlines")
                    outline_rows = page.locator(".lesson > details li").evaluate_all("""lessons => lessons.map(li => [
                      li.querySelector('strong').textContent,
                      li.textContent.replace(li.querySelector('strong').textContent, '').replace(/^\\s*·\\s*/, '').replace(/（本课）$/, '').trim()])""")
                    require(outline_rows == [[number, title] for number, title, _ in plan_rows], "F01 outline must match all 45 ordered plan titles")
                    loaded = wait_images(page, theme)
                    record["image_loads"].append({"width": width, "theme": theme, "images": loaded})
                    for index, item in enumerate(loaded):
                        diagram_urls[(index, theme)] = item["src"]
                    record["measurements"].append(measure_chapter(page))
                    record["interactions"].append({"width": width, "theme": theme, **lesson_interactions(page, context, base)})
                    page.locator(".theme-toggle").click()
                    opposite = "dark" if theme == "light" else "light"
                    require(page.locator("html").get_attribute("data-theme") == opposite, "theme toggle")
                    wait_images(page, opposite)
                    page.locator(".theme-toggle").click()
                    wait_images(page, theme)
                    record["anchor_checks"].append({"width": width, "theme": theme, "targets": anchor_checks(page)})
                    page.goto(base + "framework/f01.html", wait_until="networkidle")
                    wait_images(page, theme)
                    if width in {1440, 390}:
                        shots = [("opening", None), ("business", page.locator(".lesson > table.ktable").nth(1))]
                        if width == 1440:
                            shots.append(("outline", page.locator(".lesson > details").first))
                        else:
                            shots += [("diagram", page.locator(".d2-figure").first), ("exercises", page.locator(".drills"))]
                        for slug, target in shots:
                            if slug == "business" and width == 390:
                                target.evaluate("table => { table.scrollLeft = table.scrollWidth; }")
                            take_shot(page, shot_dir, record["screenshots"], f"f01-{width}-{theme}-{slug}.png", target)
                    page.goto(base + "framework/index.html", wait_until="networkidle")
                    record["directory_measurements"].append(measure_directory(page, plan_rows))
                    page.locator("a.card.curriculum-lesson-link[data-ch='f01-v2']").click()
                    page.wait_for_url(base + "framework/f01.html")
                    require(page.locator("article").get_attribute("data-ch") == "f01-v2", "directory opens new lesson")
                    page.goto(base + "index.html", wait_until="networkidle")
                    require(page.evaluate("document.documentElement.scrollWidth <= innerWidth"), {"home_overflow": width, "theme": theme})
                    page.locator(".cta-actions a[href='framework/f01.html']").click()
                    page.wait_for_url(base + "framework/f01.html")
                    require(page.locator("article").get_attribute("data-ch") == "f01-v2", "home opens new lesson")
                    page.goto(base + "framework/f01-startup-legacy.html", wait_until="networkidle")
                    require(page.locator("article").get_attribute("data-ch") == "f01", "historical F01 key retained")
                    require(page.locator(".legacy-course-note").is_visible(), "historical explanation visible")
                    require(page.locator(".legacy-course-note a[href='f01.html']").count() >= 1, "legacy points to new F01")
                    require(page.evaluate("document.documentElement.scrollWidth <= innerWidth"), {"legacy_overflow": width, "theme": theme})
                    context.close()
            # 单独验证持久状态，避免初始化脚本在导航时重置新课进度。
            context = browser.new_context(viewport={"width": 390, "height": 900}, reduced_motion="reduce")
            protect_business_requests(context, record)
            page = context.new_page()
            attach_observers(page, record)
            page.goto(base + "framework/f01.html", wait_until="networkidle")
            page.evaluate("localStorage.setItem('es-web:read', JSON.stringify({f01:true})); localStorage.setItem('es-web:theme','dark')")
            page.reload(wait_until="networkidle")
            button = page.locator(".read-toggle")
            require(not button.evaluate("element => element.classList.contains('is-on')"), "old F01 must not mark new F01 read")
            button.click()
            require(page.evaluate("JSON.parse(localStorage.getItem('es-web:read'))['f01-v2'] === true && JSON.parse(localStorage.getItem('es-web:read')).f01 === true"), "mark new F01 while preserving legacy")
            page.reload(wait_until="networkidle")
            require(button.evaluate("element => element.classList.contains('is-on')"), "new F01 read persists across reload")
            button.click()
            require(page.evaluate("!JSON.parse(localStorage.getItem('es-web:read'))['f01-v2'] && JSON.parse(localStorage.getItem('es-web:read')).f01 === true"), "cancel new F01 preserves legacy")
            button.click()
            page.locator(".pager a[href='index.html']").click()
            page.wait_for_url(base + "framework/index.html")
            require(page.locator(".curriculum-lesson-link[data-ch='f01-v2']").evaluate("element => element.classList.contains('is-read')"), "directory shows new read progress")
            page.locator(".curriculum-lesson-link[data-ch='f01-v2']").click()
            page.wait_for_url(base + "framework/f01.html")
            button.click()
            page.locator(".pager a[href='index.html']").click()
            page.wait_for_url(base + "framework/index.html")
            require(not page.locator(".curriculum-lesson-link[data-ch='f01-v2']").evaluate("element => element.classList.contains('is-read')"), "directory clears new read progress")
            page.goto(base + "framework/f01.html", wait_until="networkidle")
            require(page.evaluate("getComputedStyle(document.documentElement).scrollBehavior === 'auto'"), "reduced motion disables smooth scrolling")
            wait_images(page, "dark")
            record["progress"] = {"legacy_key": "f01", "new_key": "f01-v2", "old_read_does_not_mark_new": True,
                                  "mark_cancel_reload_directory": "passed", "legacy_read_preserved": True}
            record["reduced_motion"] = {"viewport": 390, "scroll_behavior": "auto", "static_diagrams_loaded": 2}
            context.close()
            record["independent_diagrams"] = []
            for (index, theme), url in sorted(diagram_urls.items()):
                context = browser.new_context(viewport={"width": 1440, "height": 1800})
                page = context.new_page()
                attach_observers(page, record)
                page.goto(url, wait_until="networkidle")
                require(page.locator("svg").count() >= 1 and page.locator("svg").first.is_visible(), {"independent_svg": url})
                name = f"f01-independent-diagram-{index + 1}-{theme}.png"
                svg = page.locator("svg").first
                bounds = svg.bounding_box()
                require(bounds and bounds["width"] > 0 and bounds["height"] > 0, {"independent_svg_bounds": bounds})
                svg.screenshot(path=str(shot_dir / name), timeout=10000)
                record["independent_diagrams"].append({"index": index + 1, "theme": theme, "url": url,
                                                       "viewport": {"width": 1440, "height": 1800}, "bounds": bounds,
                                                       "screenshot": name, "capture": "outer SVG element"})
                record["screenshots"].append(name)
                context.close()
            # file:// 只验本课离线阅读；不冒充 HTTP 复制或真实执行验收。
            file_checks = []
            for theme in THEMES:
                context = browser.new_context(viewport={"width": 390, "height": 900}, reduced_motion="reduce")
                context.add_init_script(f"localStorage.setItem('es-web:theme', '{theme}')")
                page = context.new_page()
                attach_observers(page, record)
                page.goto((ROOT / "framework/f01.html").as_uri(), wait_until="load")
                wait_images(page, theme)
                measure = measure_chapter(page)
                require(page.locator("article").get_attribute("data-ch") == "f01-v2", "file preview lesson")
                page.locator(".theme-toggle").click()
                wait_images(page, "dark" if theme == "light" else "light")
                file_checks.append({"theme": theme, "viewport": 390, "measurement": measure, "offline_theme_toggle": True})
                context.close()
            record["file_preview"] = file_checks
            browser.close()
        framework_business = [item for item in record["blocked_business_requests"] if "/framework/" in item["page"]]
        record["framework_business_requests"] = framework_business
        require(not framework_business, {"framework_business_requests": framework_business})
        require(not record["js_errors"], record["js_errors"])
        require(not record["http_failures"], record["http_failures"])
        unexpected_failures = [item for item in record["request_failures"] if not any(
            item["url"] == blocked["url"] for blocked in record["blocked_business_requests"])]
        require(not unexpected_failures, unexpected_failures)
        files = set([name for name in documents if name != "STATUS.md"] + ["framework/index.html", "framework/f01.html", "framework/f01-startup-legacy.html",
                                "framework/assets/course.css", "framework/assets/course.js", "assets/js/nav.js",
                                "assets/js/progress.js", "assets/css/style.css", "assets/css/chapter-diagrams.css",
                                "index.html", str(HERE.relative_to(ROOT) / "review.py")])
        receipts = ["framework/diagrams/f01/generation-intro.json", "framework/diagrams/f01/generation.json"]
        record["diagram_manifest_verification"] = []
        for receipt_name in receipts:
            receipt = json.loads((ROOT / receipt_name).read_text())
            files.add(receipt_name)
            for name, declared_hash in receipt["sha256"].items():
                actual_hash = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                require(actual_hash == declared_hash, {"diagram_receipt_mismatch": name})
                files.add(name)
            record["diagram_manifest_verification"].append({"receipt": receipt_name, "declared_assets": list(receipt["sha256"]), "hash_match": True})
        files.add("framework/diagrams/f01/README.md")
        declared = set(json.loads((ROOT / receipts[0]).read_text())["sha256"])
        require(all(unquote(urlsplit(url).path.removeprefix("/es_web/")) in declared for url in diagram_urls.values()),
                "only declared new F01 diagram assets are reviewed")
        record["hashes"] = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in sorted(files)}
        record["screenshot_hashes"] = {name: hashlib.sha256((shot_dir / name).read_bytes()).hexdigest() for name in record["screenshots"]}
        record["automated_status"] = "success"
        print("PASS: new F01; 12 viewport/theme pairs; two themed diagrams; exact JSON clipboard; anchors/progress/navigation; file preview/reduced motion; screenshots await visual review")
    except Exception as error:
        record["automated_status"] = "failed"
        record["failure"] = {"error": str(error), "traceback": traceback.format_exc()}
        raise
    finally:
        record["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        (HERE / "http-review.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
        if server:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    run()
