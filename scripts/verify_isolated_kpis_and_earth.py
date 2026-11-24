import time
import sys
from playwright.sync_api import sync_playwright

def verify_spaci():
    print("[SPACI TEST] Launching Chrome verification...")
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        console_errors = []
        page_errors = []

        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda exc: page_errors.append(str(exc)))

        # 1. Test Landing Page (Photorealistic Earth & 3D WebGL)
        print("[TEST 1] Visiting landing page http://localhost:8080/landing.html ...")
        page.goto("http://localhost:8080/landing.html", wait_until="networkidle", timeout=30000)
        time.sleep(2.0)

        # Check canvas and window.__spaci
        has_spaci = page.evaluate("() => !!window.__spaci && !!window.__spaci.earth")
        print(f" -> 3D Engine initialized: {has_spaci}")
        assert has_spaci, "Expected window.__spaci with earth mesh to be initialized"

        # Check Earth material uniforms
        earth_info = page.evaluate("""() => {
            const S = window.__spaci;
            return {
                earthRadius: S.earth.geometry.parameters.radius,
                cloudsRadius: S.clouds.geometry.parameters.radius,
                detailGroupChildren: S.earthDetailGroup.children.length,
                leoRingsChildren: S.leoRingsGroup.children.length
            };
        }""")
        print(f" -> Earth & Atmosphere setup: {earth_info}")
        assert earth_info["cloudsRadius"] < 1.010, f"Expected realistic clouds radius (< 1.010), got {earth_info['cloudsRadius']}"
        assert earth_info["detailGroupChildren"] == 0, f"Expected artificial on-globe latitude rings removed, got {earth_info['detailGroupChildren']}"
        assert earth_info["leoRingsChildren"] == 3, f"Expected 3 space LEO altitude debris rings, got {earth_info['leoRingsChildren']}"

        # Test scroll interpolation
        page.evaluate("window.scrollTo(0, 1500)")
        time.sleep(1.0)
        page.evaluate("window.scrollTo(0, 3000)")
        time.sleep(1.0)
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(0.5)

        # 2. Test Mission Control HUD (Isolated KPI Grids)
        print("\n[TEST 2] Visiting Mission Control HUD http://localhost:8080/hud ...")
        page.goto("http://localhost:8080/hud", wait_until="networkidle", timeout=30000)
        time.sleep(2.0)

        # Verify Live Tab has its dedicated KPI elements
        live_kpis = page.evaluate("""() => ({
            total: document.getElementById('liveKpiTotal')?.textContent,
            hazardous: document.getElementById('liveKpiHazardous')?.textContent,
            reusable: document.getElementById('liveKpiReusable')?.textContent,
            active: document.getElementById('liveKpiActive')?.textContent,
            risk: document.getElementById('liveKpiRisk')?.textContent,
        })""")
        print(f" -> Live Tab initial KPIs: {live_kpis}")
        assert live_kpis["total"] is not None, "Live KPI Total element missing"

        # Check Telemetry Tab dedicated KPIs
        telem_kpis = page.evaluate("""() => ({
            total: document.getElementById('telemetryKpiTotal')?.textContent,
            success: document.getElementById('telemetryKpiSuccess')?.textContent,
            distance: document.getElementById('telemetryKpiDistance')?.textContent,
            error: document.getElementById('telemetryKpiError')?.textContent,
            latency: document.getElementById('telemetryKpiLatency')?.textContent,
        })""")
        print(f" -> Telemetry Tab dedicated KPIs: {telem_kpis}")
        assert telem_kpis["total"] is not None, "Telemetry KPI Total missing"

        # 3. Test Video Tab: Trigger 1-Click Video Track
        print("\n[TEST 3] Switching to Video Tab and triggering 1-Click Video Track...")
        page.click("#tabBtnVideo")
        time.sleep(0.5)

        # Check Video initial KPIs before run
        video_kpis_before = page.evaluate("""() => ({
            total: document.getElementById('videoKpiTotal')?.textContent,
            hazardous: document.getElementById('videoKpiHazardous')?.textContent,
            risk: document.getElementById('videoKpiRisk')?.textContent
        })""")
        print(f" -> Video KPIs before run: {video_kpis_before}")

        # Click 1-Click Video Track
        page.click("#btnDemoVideo")
        print(" -> Waiting for BoT-SORT video kinematics to process...")
        # Wait up to 15s for video processing
        page.wait_for_selector("#insightsBanner:visible", timeout=20000)
        time.sleep(1.0)

        video_kpis_after = page.evaluate("""() => ({
            total: document.getElementById('videoKpiTotal')?.textContent,
            hazardous: document.getElementById('videoKpiHazardous')?.textContent,
            reusable: document.getElementById('videoKpiReusable')?.textContent,
            active: document.getElementById('videoKpiActive')?.textContent,
            risk: document.getElementById('videoKpiRisk')?.textContent
        })""")
        print(f" -> Video KPIs AFTER processing: {video_kpis_after}")
        assert int(video_kpis_after["total"]) > 0, "Expected video tracks count > 0"

        # 4. Test Gallery Tab: Select a Space Object Sample
        print("\n[TEST 4] Switching to Gallery Tab and selecting a Space Object Sample...")
        page.click("#tabBtnGallery")
        time.sleep(0.5)

        # Click on the first sample card
        sample_cards = page.query_selector_all(".gallery-card")
        if sample_cards:
            sample_cards[0].click()
            time.sleep(2.0)

        gallery_kpis_after = page.evaluate("""() => ({
            total: document.getElementById('galleryKpiTotal')?.textContent,
            hazardous: document.getElementById('galleryKpiHazardous')?.textContent,
            reusable: document.getElementById('galleryKpiReusable')?.textContent,
            active: document.getElementById('galleryKpiActive')?.textContent,
            risk: document.getElementById('galleryKpiRisk')?.textContent
        })""")
        print(f" -> Gallery KPIs AFTER sample selection: {gallery_kpis_after}")
        assert int(gallery_kpis_after["total"]) > 0, "Expected gallery detections count > 0"

        # 5. Switch back to Video Tab and verify Video KPIs were NOT overwritten by Gallery!
        print("\n[TEST 5] Switching back to Video Tab to verify NO cross-tab leakage...")
        page.click("#tabBtnVideo")
        time.sleep(0.5)
        video_kpis_check = page.evaluate("""() => ({
            total: document.getElementById('videoKpiTotal')?.textContent,
            hazardous: document.getElementById('videoKpiHazardous')?.textContent,
            risk: document.getElementById('videoKpiRisk')?.textContent
        })""")
        print(f" -> Video KPIs re-checked: {video_kpis_check}")
        assert video_kpis_check["total"] == video_kpis_after["total"], "Video KPIs were corrupted by Gallery!"

        # 6. Check console & page errors
        print(f"\n[TEST 6] Error check: Console errors={len(console_errors)}, Page errors={len(page_errors)}")
        if console_errors:
            print("Console errors:", console_errors)
        if page_errors:
            print("Page errors:", page_errors)

        assert len(page_errors) == 0, f"Encountered page errors: {page_errors}"

        browser.close()
        print("\n✅ ALL TESTS PASSED SUCCESSFULLY! Both per-tab KPI isolation and realistic Earth verified.")

if __name__ == "__main__":
    verify_spaci()
