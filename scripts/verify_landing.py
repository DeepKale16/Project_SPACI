import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LANDING_HTML_PATH = PROJECT_ROOT / "web" / "landing.html"
FILE_URL = f"file:///{LANDING_HTML_PATH.as_posix()}"
HTTP_URL = "http://localhost:8080/landing"

def run_landing_test():
    console_logs = []
    page_errors = []

    print(f"Testing landing page via Playwright from: {FILE_URL}")
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(channel="msedge", headless=True)
        except Exception:
            try:
                browser = p.chromium.launch(channel="chrome", headless=True)
            except Exception:
                browser = p.chromium.launch(headless=True)

        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
        page.on("pageerror", lambda err: page_errors.append(str(err)))

        # Navigate via HTTP
        target_url = HTTP_URL
        print(f"Navigating to: {target_url}")
        page.goto(target_url, wait_until="load", timeout=15000)
        page.wait_for_timeout(2500)

        # 1. Check title and hero text
        title = page.title()
        print(f"[OK] Page title: '{title}'")
        assert "SPACI" in title, f"Title does not contain SPACI: {title}"

        hero_heading = page.locator("#s0 h1").inner_text()
        print(f"[OK] Hero heading: '{hero_heading.replace(chr(10), ' ')}'")
        assert "Catch what's" in hero_heading, f"Unexpected hero heading: {hero_heading}"

        # 2. Check WebGL Canvas
        canvas = page.locator("#gl")
        assert canvas.is_visible(), "WebGL canvas is not visible!"
        print("[OK] WebGL canvas is visible and active.")

        # Capture Hero screenshot
        page.screenshot(path="reports/landing_hero.png")
        print("[OK] Saved reports/landing_hero.png")

        # 3. Test Scroll through all sections (s0 to s5)
        section_ids = [
            ("s0", "Hero", "reports/landing_hero.png"),
            ("s1", "Problem", "reports/landing_problem.png"),
            ("s2", "Detect", "reports/landing_detect.png"),
            ("s3", "AimCapture", "reports/landing_capture.png"),
            ("s4", "Retrieve", "reports/landing_retrieve.png"),
            ("s5", "Specifications", "reports/landing_specs.png"),
        ]

        for sec_id, name, shot_path in section_ids:
            sec_el = page.locator(f"#{sec_id}")
            sec_el.scroll_into_view_if_needed()
            page.wait_for_timeout(1000)  # Allow smooth camera damping and canvas rendering

            hud_sys = page.locator("#hSys").inner_text()
            hud_obj = page.locator("#hObj").inner_text()
            print(f" -> {name} (#{sec_id}) | HUD System: '{hud_sys}' | Simulated Objects: '{hud_obj}'")
            page.screenshot(path=shot_path)
            print(f"    Saved {shot_path}")

        # 4. Verify Tracking Reticles & Subsystem Callouts
        for ret_id in ["rA", "rB", "rC", "rT"]:
            assert page.locator(f"#{ret_id}").count() == 1, f"Missing reticle {ret_id}"
        print("[OK] All 4 tracking reticles present in DOM.")

        for tag_id in ["tgLid", "tgGim", "tgEj", "tgWin"]:
            assert page.locator(f"#{tag_id}").count() == 1, f"Missing callout tag {tag_id}"
        print("[OK] All 4 Subsystem 3D Callout Tags present in DOM.")

        # 5. Verify Sensor Feed Canvas
        feed_canvas = page.locator("#feed")
        assert feed_canvas.count() == 1, "Missing sensor feed canvas"
        print("[OK] Sensor Feed canvas verified.")

        # 6. Test Mobile Viewport (390 x 844)
        print("\nTesting mobile layout (390 x 844)...")
        mobile_page = context.new_page()
        mobile_page.set_viewport_size({"width": 390, "height": 844})
        mobile_page.goto(HTTP_URL, wait_until="load", timeout=15000)
        mobile_page.wait_for_timeout(2000)

        # Check horizontal overflow
        scroll_width = mobile_page.evaluate("() => document.documentElement.scrollWidth")
        client_width = mobile_page.evaluate("() => window.innerWidth")
        print(f"[Mobile] scrollWidth: {scroll_width}, innerWidth: {client_width}")
        assert scroll_width <= client_width + 1, f"Horizontal scroll overflow detected! {scroll_width} > {client_width}"

        mobile_page.screenshot(path="reports/landing_mobile.png")
        print("[OK] Saved reports/landing_mobile.png")
        mobile_page.close()

        # 7. Check Console Logs & Errors
        print(f"\n--- Console Logs ({len(console_logs)}) ---")
        for log in console_logs:
            if "error" in log.lower() or "warn" in log.lower():
                print(" ", log)

        print(f"\n--- Page Errors ({len(page_errors)}) ---")
        for err in page_errors:
            print("  PAGE ERROR:", err)

        assert len(page_errors) == 0, f"Found {len(page_errors)} page errors!"
        print("\nAll landing page Playwright tests PASSED successfully!")
        browser.close()

if __name__ == "__main__":
    run_landing_test()
