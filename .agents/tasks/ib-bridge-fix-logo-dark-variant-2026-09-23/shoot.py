#!/usr/bin/env python3
"""Render hero + footer at desktop and mobile, element-cropped screenshots only.
NEVER full_page. Serves repo via http.server."""
import subprocess, time, os, signal
from playwright.sync_api import sync_playwright

ART = "/projects/sandbox/ib-bridge/.agents/tasks/ib-bridge-fix-logo-dark-variant-2026-09-23"
ROOT = "/projects/sandbox/ib-bridge"
PORT = 8099
URL = f"http://127.0.0.1:{PORT}/index.html"

srv = subprocess.Popen(["python3", "-m", "http.server", str(PORT)], cwd=ROOT,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.5)
try:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for label, vw, vh in [("desktop", 1280, 800), ("mobile", 390, 800)]:
            ctx = browser.new_context(viewport={"width": vw, "height": vh},
                                      device_scale_factor=2)
            page = ctx.new_page()
            page.goto(URL, wait_until="networkidle")
            page.wait_for_timeout(400)
            hero = page.locator("section.hero")
            hero.scroll_into_view_if_needed()
            hero.screenshot(path=f"{ART}/hero_{label}.png")
            foot = page.locator("footer.site-footer")
            foot.scroll_into_view_if_needed()
            page.wait_for_timeout(200)
            foot.screenshot(path=f"{ART}/footer_{label}.png")
            # horizontal overflow check
            sw = page.evaluate("document.documentElement.scrollWidth")
            cw = page.evaluate("document.documentElement.clientWidth")
            print(f"{label}: scrollWidth={sw} clientWidth={cw} overflow={sw>cw}")
            ctx.close()
        browser.close()
finally:
    srv.send_signal(signal.SIGTERM)

from PIL import Image
for f in ["hero_desktop.png", "footer_desktop.png", "hero_mobile.png", "footer_mobile.png"]:
    im = Image.open(f"{ART}/{f}")
    print(f, im.size, "OK" if im.size[0] < 8000 and im.size[1] < 8000 else "TOO BIG")
