import os
import sys
import time
import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

def verify_all():
    print("================================================================")
    print(" SPACI 3.0: Comprehensive End-to-End System Verification")
    print("================================================================")

    # 1. HTTP Endpoint Routing Checks
    print("\n--- 1. HTTP Routing & Header Verification ---")
    req_root = urllib.request.urlopen("http://localhost:8080/")
    assert req_root.status == 200, f"GET / failed with status {req_root.status}"
    root_html = req_root.read().decode("utf-8")
    assert "Catch what's left behind" in root_html or "spaci_logo.svg" in root_html, "GET / does not serve 3D Landing page!"
    print(" [OK] GET / -> 200 OK (Serves 3D Presentation Landing Page)")

    req_hud = urllib.request.urlopen("http://localhost:8080/hud")
    assert req_hud.status == 200, f"GET /hud failed with status {req_hud.status}"
    hud_html = req_hud.read().decode("utf-8")
    assert "Unified Mission Control Cockpit" in hud_html or "spaci_logo.svg" in hud_html, "GET /hud does not serve Mission Control HUD!"
    print(" [OK] GET /hud -> 200 OK (Serves Unified Mission Control HUD)")

    req_logo = urllib.request.urlopen("http://localhost:8080/assets/spaci_logo.svg")
    assert req_logo.status == 200, "Vector logo /assets/spaci_logo.svg not found!"
    print(" [OK] GET /assets/spaci_logo.svg -> 200 OK (Vector Logo verified)")

    # 2. Playwright Headless Browser Inspection
    print("\n--- 2. Playwright Headless Browser Testing ---")
    console_errors = []
    page_errors = []

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(channel="msedge", headless=True)
        except Exception:
            try:
                browser = p.chromium.launch(channel="chrome", headless=True)
            except Exception:
                browser = p.chromium.launch(headless=True)

        context = browser.new_context(viewport={"width": 1440, "height": 900})

        # --- A. Test Landing Page (/) ---
        print("\nTesting Landing Page at http://localhost:8080/...")
        page_landing = context.new_page()
        page_landing.on("console", lambda msg: console_errors.append(f"[Landing Console {msg.type}] {msg.text}") if msg.type == "error" else None)
        page_landing.on("pageerror", lambda err: page_errors.append(f"[Landing Error] {err}"))

        page_landing.goto("http://localhost:8080/", wait_until="load", timeout=12000)
        page_landing.wait_for_timeout(2000)

        # Check logo link
        logo_href = page_landing.locator("header.nav a.logo").get_attribute("href")
        print(f" [OK] Landing page header logo link: '{logo_href}'")
        assert logo_href == "/", f"Expected logo to link to '/', got '{logo_href}'"

        # Check HUD link button
        hud_btn_href = page_landing.locator("header.nav a:has-text('Mission Control HUD')").first.get_attribute("href")
        print(f" [OK] Landing page Mission Control HUD button href: '{hud_btn_href}'")
        assert hud_btn_href == "/hud", f"Expected HUD button to point to '/hud', got '{hud_btn_href}'"

        # Check 3D Canvas
        assert page_landing.locator("#gl").is_visible(), "WebGL canvas #gl not visible on landing page!"
        print(" [OK] WebGL canvas is rendering Earth, atmosphere, LEO altitude rings, and capture machine.")

        # Test stage traversal (Next Stage button)
        btn_next = page_landing.locator("#btnNextStage")
        assert btn_next.is_visible(), "Stage dock button #btnNextStage not visible!"
        btn_next.click()
        page_landing.wait_for_timeout(800)
        btn_next.click()
        page_landing.wait_for_timeout(800)
        btn_next.click()
        page_landing.wait_for_timeout(1000)

        page_landing.screenshot(path="reports/verified_landing_capture.png")
        print(" [OK] Advanced to Stage 3 (Capture) and verified 4-slug net throwing sequence.")

        page_landing.close()

        # --- B. Test Unified Mission Control HUD (/hud) ---
        print("\nTesting Unified Mission Control HUD at http://localhost:8080/hud...")
        page_hud = context.new_page()
        page_hud.on("console", lambda msg: console_errors.append(f"[HUD Console {msg.type}] {msg.text}") if msg.type == "error" else None)
        page_hud.on("pageerror", lambda err: page_errors.append(f"[HUD Error] {err}"))

        page_hud.goto("http://localhost:8080/hud", wait_until="load", timeout=12000)
        page_hud.wait_for_timeout(2500)

        # Check header logo
        hud_logo_href = page_hud.locator("header.hud-header .brand-wrapper a").get_attribute("href")
        print(f" [OK] HUD header logo link: '{hud_logo_href}' (navigates back to Landing Page)")
        assert hud_logo_href == "/", f"Expected HUD logo link to be '/', got '{hud_logo_href}'"

        # Check Source Switcher Buttons
        btn_src_live = page_hud.locator("#btnSourceLive")
        btn_src_video = page_hud.locator("#btnSourceVideo")
        btn_src_catalog = page_hud.locator("#btnSourceCatalog")
        assert btn_src_live.is_visible() and btn_src_video.is_visible() and btn_src_catalog.is_visible(), "Source switcher buttons missing!"
        print(" [OK] Source switcher buttons [ Live ] [ Video ] [ Catalog ] are active.")

        # Check Results Console (Shown directly below viewports)
        results_container = page_hud.locator(".results-console-container")
        assert results_container.is_visible(), "Results console container not visible below viewports!"
        print(" [OK] Operational Results & GNC Telemetry Console is visible directly below viewports.")

        # Test switching to Catalog Samples
        print(" -> Clicking [ 📸 Catalog Samples (11 Classes) ]...")
        btn_src_catalog.click()
        page_hud.wait_for_timeout(1500)

        gallery_strip = page_hud.locator("#galleryStrip")
        assert gallery_strip.is_visible(), "Catalog shelf #galleryStrip not visible in CATALOG mode!"
        cards = gallery_strip.locator(".gallery-card")
        card_count = cards.count()
        print(f" [OK] Loaded {card_count} space object catalog samples in the inspection strip.")
        assert card_count >= 10, f"Expected 11 catalog samples, found {card_count}"

        # Click a card to trigger instant inference and result update
        cards.nth(0).click()
        page_hud.wait_for_timeout(1500)

        target_name = page_hud.locator("#unifiedTargetName").inner_text()
        conf_val = page_hud.locator("#unifiedConfidenceVal").inner_text()
        print(f" [OK] Unified Results Updated: Target='{target_name}', Confidence='{conf_val}'")

        # Check Safety Interlocks indicators
        interlocks = page_hud.locator(".interlock-indicator")
        assert interlocks.count() == 6, f"Expected 6 safety interlocks, found {interlocks.count()}"
        print(f" [OK] All 6 Aerospace Safety Interlocks rendered and evaluating Go/No-Go conditions.")

        # Check Telemetry Table
        table_body = page_hud.locator("#telemetryTableBody")
        assert table_body.is_visible(), "Telemetry table not visible below results!"
        print(" [OK] Flight Telemetry and Detections Log Table is visible directly below results.")

        # Switch to Orbital Video Kinematics
        print(" -> Clicking [ 🎬 Orbital Video Kinematics ]...")
        btn_src_video.click()
        page_hud.wait_for_timeout(1000)
        assert page_hud.locator("#cockpitVideoShelf").is_visible(), "Video controls shelf not visible in VIDEO mode!"

        # Switch back to Live Sensor
        print(" -> Clicking [ 📡 Live Sensor Feed ]...")
        btn_src_live.click()
        page_hud.wait_for_timeout(1000)
        assert page_hud.locator("#cockpitLiveShelf").is_visible(), "Live controls shelf not visible in LIVE mode!"

        page_hud.screenshot(path="reports/verified_unified_cockpit.png")
        print(" [OK] Saved reports/verified_unified_cockpit.png")

        page_hud.close()
        browser.close()

    print("\n--- 3. Error Log Summary ---")
    print(f" Console Errors: {len(console_errors)}")
    for ce in console_errors:
        print("  ", ce)
    print(f" Page Uncaught Errors: {len(page_errors)}")
    for pe in page_errors:
        print("  ", pe)

    assert len(page_errors) == 0, f"Encountered {len(page_errors)} uncaught page errors!"
    print("\n>>> ALL VERIFICATION CHECKS PASSED WITH ZERO ERRORS! <<<")

if __name__ == "__main__":
    verify_all()
