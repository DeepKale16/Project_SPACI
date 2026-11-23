import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LANDING_HTML_PATH = PROJECT_ROOT / "web" / "landing.html"
FILE_URL = f"file:///{LANDING_HTML_PATH.as_posix()}"

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

        # Navigate
        page.goto(FILE_URL, wait_until="load", timeout=15000)
        page.wait_for_timeout(2000)

        # 1. Check title and hero text
        title = page.title()
        print(f"[OK] Page title: '{title}'")
        assert "SPACI" in title, f"Title does not contain SPACI: {title}"

        hero_heading = page.locator("#section-0 h1").inner_text()
        print(f"[OK] Hero heading: '{hero_heading}'")
        assert "Catch what's left behind" in hero_heading, f"Unexpected hero heading: {hero_heading}"

        # 2. Check WebGL Canvas
        canvas = page.locator("#webgl-canvas")
        assert canvas.is_visible(), "WebGL canvas is not visible!"
        print("[OK] WebGL canvas is visible and active.")

        # Capture Hero screenshot
        page.screenshot(path="reports/landing_hero.png")
        print("[OK] Saved reports/landing_hero.png")

        # 3. Test Scroll through all sections (0 to 7)
        section_ids = [
            ("section-0", "Hero", "reports/landing_hero.png"),
            ("section-1", "Problem", "reports/landing_problem.png"),
            ("section-2", "Detect", "reports/landing_detect.png"),
            ("section-3", "AimCapture", "reports/landing_capture.png"),
            ("section-4", "Retrieve", "reports/landing_retrieve.png"),
            ("section-5", "Specifications", "reports/landing_specs.png"),
            ("section-6", "GroundTest", "reports/landing_comparison.png"),
            ("section-7", "SubsystemsCTA", "reports/landing_cta.png"),
        ]

        for sec_id, name, shot_path in section_ids:
            sec_el = page.locator(f"#{sec_id}")
            sec_el.scroll_into_view_if_needed()
            page.wait_for_timeout(900)  # Allow smooth camera damping and canvas rendering

            hud_stage = page.locator("#hud-stage-name").inner_text()
            hud_lock = page.locator("#hud-lock-status").inner_text()
            print(f" -> {name} ({sec_id}) | HUD Stage: '{hud_stage}' | Target GNC: '{hud_lock}'")
            page.screenshot(path=shot_path)
            print(f"    Saved {shot_path}")

        # 4. Verify Tracking Overlays
        reticle = page.locator("#tracker-target")
        reticle_count = reticle.count()
        print(f"[OK] Target Reticle Element Found: count={reticle_count}")
        assert reticle_count == 1, "Target reticle element not found!"

        # Check callout tags
        for tag_id in ["tag-sensors", "tag-gimbal", "tag-ejectors", "tag-winch"]:
            assert page.locator(f"#{tag_id}").count() == 1, f"Missing callout tag {tag_id}"
        print("[OK] All 4 Subsystem 3D Callout Tags present in DOM.")

        # 5. Verify Sensor Feed Canvas
        feed_canvas = page.locator("#sensor-feed-canvas")
        feed_channel = page.locator("#feed-channel-label").inner_text()
        print(f"[OK] Sensor Feed Channel: '{feed_channel}'")

        # 6. Test Mobile Viewport (390 x 844)
        print("\nTesting mobile layout (390 x 844)...")
        mobile_page = context.new_page()
        mobile_page.set_viewport_size({"width": 390, "height": 844})
        mobile_page.goto(FILE_URL, wait_until="load", timeout=15000)
        mobile_page.wait_for_timeout(1500)

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
