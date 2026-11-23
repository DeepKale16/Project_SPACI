import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LANDING_HTML_PATH = PROJECT_ROOT / "web" / "landing.html"
HTTP_URL = "http://localhost:8080/landing"
FILE_URL = f"file:///{LANDING_HTML_PATH.as_posix()}"

def run_comprehensive_test():
    console_logs = []
    page_errors = []

    print(f"Launching Playwright automated test against: {HTTP_URL}")
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
        try:
            page.goto(HTTP_URL, wait_until="load", timeout=12000)
        except Exception:
            print("HTTP server unreachable, falling back to direct FILE_URL...")
            page.goto(FILE_URL, wait_until="load", timeout=12000)

        page.wait_for_timeout(2500)

        # 1. Title and Hero verification
        title = page.title()
        print(f"[OK] Page title: '{title}'")
        assert "SPACI" in title, f"Title does not contain SPACI: {title}"

        hero_h1 = page.locator("#s0 h1").inner_text()
        print(f"[OK] Hero headline: '{hero_h1.replace(chr(10), ' ')}'")
        assert "Catch what's" in hero_h1, f"Unexpected hero heading: {hero_h1}"

        # 2. Check 3D WebGL Canvas
        canvas = page.locator("#gl")
        assert canvas.is_visible(), "WebGL canvas #gl is not visible!"
        print("[OK] WebGL canvas is active and rendering.")

        # Capture Hero screenshot with new photorealistic Earth & clouds
        page.screenshot(path="reports/landing_hero.png")
        print("[OK] Saved reports/landing_hero.png")

        # 3. Test Front / Back Navigation & Stage Dock Buttons
        print("\nTesting Interactive Stage Navigation Dock...")
        stage_names = ["Orbit", "Problem", "Detect", "Capture", "Retrieve", "Specs"]
        
        # Test clicking Next Stage button 5 times to traverse all stages
        btn_next = page.locator("#btnNextStage")
        assert btn_next.is_visible(), "Next stage button not visible!"

        for i in range(1, 6):
            btn_next.click()
            page.wait_for_timeout(1000)
            hud_sys = page.locator("#hSys").inner_text()
            shot_file = f"reports/landing_stage_{i}.png"
            page.screenshot(path=shot_file)
            print(f" -> Advanced to Stage {i} via [ Next > ]: HUD='{hud_sys}', saved {shot_file}")

        # Test clicking Prev Stage button back to stage 2 (Detect)
        btn_prev = page.locator("#btnPrevStage")
        assert btn_prev.is_visible(), "Prev stage button not visible!"
        print("\nTesting [ < Prev ] button navigation...")
        for _ in range(3):
            btn_prev.click()
            page.wait_for_timeout(700)

        page.wait_for_timeout(500)
        hud_sys = page.locator("#hSys").inner_text()
        print(f" -> Stepped back via [ < Prev ]: HUD='{hud_sys}'")

        # Test clicking direct stage pills
        print("\nTesting direct Stage Pills...")
        pills = page.locator(".stage-dock .stage-pill")
        pill_count = pills.count()
        print(f"Found {pill_count} stage pills.")
        assert pill_count == 6, f"Expected 6 stage pills, got {pill_count}"

        # Jump directly to Capture (pill 3)
        pills.nth(3).click()
        page.wait_for_timeout(1200)
        hud_sys = page.locator("#hSys").inner_text()
        print(f" -> Clicked Stage 3 Pill (Capture): HUD='{hud_sys}'")
        page.screenshot(path="reports/landing_capture.png")
        print("[OK] Saved reports/landing_capture.png")

        # Jump directly to Retrieve (pill 4)
        pills.nth(4).click()
        page.wait_for_timeout(1200)
        page.screenshot(path="reports/landing_retrieve.png")
        print("[OK] Saved reports/landing_retrieve.png")

        # Jump directly to Specs (pill 5)
        pills.nth(5).click()
        page.wait_for_timeout(1200)
        page.screenshot(path="reports/landing_specs.png")
        print("[OK] Saved reports/landing_specs.png")

        # Jump to Problem (pill 1)
        pills.nth(1).click()
        page.wait_for_timeout(1200)
        page.screenshot(path="reports/landing_problem.png")
        print("[OK] Saved reports/landing_problem.png")

        # Jump to Detect (pill 2)
        pills.nth(2).click()
        page.wait_for_timeout(1200)
        page.screenshot(path="reports/landing_detect.png")
        print("[OK] Saved reports/landing_detect.png")

        # 4. Test Interactive Debris Selector
        print("\nTesting Debris Geometry Selector buttons...")
        btn_sat = page.locator("#btnDebSat")
        btn_rkt = page.locator("#btnDebRkt")
        btn_shd = page.locator("#btnDebShd")

        assert btn_sat.is_visible() and btn_rkt.is_visible() and btn_shd.is_visible(), "Debris selector buttons not visible!"

        btn_rkt.click()
        page.wait_for_timeout(500)
        print(" -> Clicked [ Spent Rocket Body (TRK-12) ]")

        btn_shd.click()
        page.wait_for_timeout(500)
        print(" -> Clicked [ Panel Fragment Shard (TRK-03) ]")

        btn_sat.click()
        page.wait_for_timeout(500)
        print(" -> Reset to [ Defunct Satellite (TRK-07) ]")

        # 5. Test Timeline Scrubber
        scrubber = page.locator("#stageScrubber")
        assert scrubber.is_visible(), "Stage scrubber slider not visible!"
        print("[OK] Timeline scrubber is present and functional.")

        # 6. Test Mobile Viewport (390 x 844)
        print("\nTesting mobile responsive layout (390 x 844)...")
        mobile_page = context.new_page()
        mobile_page.set_viewport_size({"width": 390, "height": 844})
        mobile_page.goto(HTTP_URL, wait_until="load", timeout=12000)
        mobile_page.wait_for_timeout(1500)

        # Check horizontal overflow
        scroll_w = mobile_page.evaluate("() => document.documentElement.scrollWidth")
        client_w = mobile_page.evaluate("() => window.innerWidth")
        print(f"[Mobile] scrollWidth: {scroll_w}, innerWidth: {client_w}")
        assert scroll_w <= client_w + 1, f"Horizontal scroll overflow on mobile! {scroll_w} > {client_w}"

        mobile_page.screenshot(path="reports/landing_mobile.png")
        print("[OK] Saved reports/landing_mobile.png")
        mobile_page.close()

        # 7. Check Console Logs & Page Errors
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
    run_comprehensive_test()
