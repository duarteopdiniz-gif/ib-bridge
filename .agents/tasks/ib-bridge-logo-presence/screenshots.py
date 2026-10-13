#!/usr/bin/env python3
"""Viewport/element screenshots + overflow + EN/ES toggle check. NEVER fullPage."""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path("/projects/sandbox/ib-bridge")
OUT = ROOT / ".agents/tasks/ib-bridge-logo-presence"
URL = (ROOT / "index.html").as_uri()


def overflow(page):
    return page.evaluate(
        "() => ({sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth})"
    )


with sync_playwright() as p:
    browser = p.chromium.launch()

    # ---- Desktop 1280x800 ----
    ctx = browser.new_context(viewport={"width": 1280, "height": 800})
    page = ctx.new_page()
    page.goto(URL)
    page.wait_for_timeout(400)
    # hero element crop
    page.locator(".hero").screenshot(path=str(OUT / "hero-desktop.png"))
    print("desktop overflow:", overflow(page))
    # scroll to footer, element crop
    page.locator(".site-footer").scroll_into_view_if_needed()
    page.wait_for_timeout(200)
    page.locator(".site-footer").screenshot(path=str(OUT / "footer-desktop.png"))
    # navbar colored logo crop
    page.locator(".site-header").scroll_into_view_if_needed()
    page.wait_for_timeout(100)
    page.locator(".site-header").screenshot(path=str(OUT / "navbar-desktop.png"))

    # EN/ES toggle check (desktop)
    en_h1 = page.locator("h1").inner_text()
    page.locator('.lang-btn[data-lang="es"]').click()
    page.wait_for_timeout(200)
    es_h1 = page.locator("h1").inner_text()
    hero_logo_src_es = page.locator(".hero-logo").get_attribute("src")
    page.locator('.lang-btn[data-lang="en"]').click()
    page.wait_for_timeout(200)
    en_h1_back = page.locator("h1").inner_text()
    print("EN h1:", repr(en_h1[:40]))
    print("ES h1:", repr(es_h1[:40]))
    print("EN h1 restored:", repr(en_h1_back[:40]))
    print("toggle changes text:", en_h1 != es_h1, "| restores:", en_h1 == en_h1_back)
    print("hero-logo src unchanged by ES:", hero_logo_src_es)
    ctx.close()

    # ---- Mobile 390x800 ----
    ctx = browser.new_context(viewport={"width": 390, "height": 800})
    page = ctx.new_page()
    page.goto(URL)
    page.wait_for_timeout(400)
    page.locator(".hero").screenshot(path=str(OUT / "hero-mobile.png"))
    print("mobile overflow:", overflow(page))
    page.locator(".site-footer").scroll_into_view_if_needed()
    page.wait_for_timeout(200)
    page.locator(".site-footer").screenshot(path=str(OUT / "footer-mobile.png"))
    # mobile nav open check
    page.locator(".site-header").scroll_into_view_if_needed()
    page.locator(".nav-toggle").click()
    page.wait_for_timeout(250)
    expanded = page.locator(".nav-toggle").get_attribute("aria-expanded")
    print("mobile nav aria-expanded after click:", expanded)
    page.locator(".site-header").screenshot(path=str(OUT / "mobile-nav-open.png"))
    ctx.close()

    browser.close()
print("screenshots done")
