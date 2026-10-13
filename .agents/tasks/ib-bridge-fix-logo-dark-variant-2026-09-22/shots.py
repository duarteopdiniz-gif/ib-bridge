#!/usr/bin/env python3
import sys, subprocess, time, functools, http.server, socketserver, threading, os
from playwright.sync_api import sync_playwright

OUT = "/projects/sandbox/ib-bridge/.agents/tasks/ib-bridge-fix-logo-dark-variant-2026-09-22"
ROOT = "/projects/sandbox/ib-bridge"
PORT = 8099
URL = f"http://localhost:{PORT}/index.html"

def start_server():
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
    httpd = socketserver.TCPServer(("127.0.0.1", PORT), handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd

def run(tag):
    httpd = start_server()
    time.sleep(0.5)
    with sync_playwright() as p:
        b = p.chromium.launch()
        for label, w, h in [("desktop", 1280, 900), ("mobile", 390, 844)]:
            pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=2)
            pg.goto(URL, wait_until="networkidle")
            pg.wait_for_timeout(500)
            # horizontal overflow check
            ow = pg.evaluate("document.documentElement.scrollWidth")
            iw = pg.evaluate("window.innerWidth")
            print(f"[{label}] scrollWidth={ow} innerWidth={iw} overflow={ow>iw}")
            pg.screenshot(path=f"{OUT}/{tag}_{label}_full.png", full_page=True)
            # hero crop
            hero = pg.query_selector(".hero")
            if hero:
                hero.screenshot(path=f"{OUT}/{tag}_{label}_hero.png")
            # footer crop
            footer = pg.query_selector(".site-footer")
            if footer:
                footer.scroll_into_view_if_needed()
                footer.screenshot(path=f"{OUT}/{tag}_{label}_footer.png")
            # EN/ES toggle test (desktop only)
            if label == "desktop":
                before = pg.inner_text("h1")
                pg.click("button[data-lang='es']")
                pg.wait_for_timeout(300)
                after = pg.inner_text("h1")
                print(f"  toggle EN->ES h1 changed: {before.strip()[:20]!r} -> {after.strip()[:20]!r} changed={before!=after}")
                pg.screenshot(path=f"{OUT}/{tag}_{label}_es.png", full_page=True)
            pg.close()
        b.close()
    httpd.shutdown()

if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "variant")
