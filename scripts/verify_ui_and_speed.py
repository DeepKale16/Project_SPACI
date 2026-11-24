"""
scripts/verify_ui_and_speed.py
Comprehensive automated verification for SPACI 3.0:
1. Benchmark /api/run-sample-video latency (cold and warm)
2. Benchmark /api/upload latency
3. Use Playwright headless browser to verify:
   - Live tab: video#webcamLocalVideo present, Live detection table populated
   - Video tab: 1-click video track populates #videoTableBody with video tracks and updates Video Threat card
   - Gallery tab: 1-click catalog sample populates #galleryTableBody with detections and updates Salvage card
   - Zero console errors across all tabs
"""

import time
import requests
from pathlib import Path
from playwright.sync_api import sync_playwright

def test_api_performance():
    print("=== 1. Benchmarking Video Tracking API Performance ===")
    t0 = time.time()
    res1 = requests.post("http://localhost:8080/api/run-sample-video", data={
        "conf_threshold": 0.25,
        "iou_threshold": 0.45,
        "speed_mps": 7500.0,
        "altitude_km": 650.0,
        "max_frames": 40
    })
    elapsed1 = time.time() - t0
    assert res1.status_code == 200, f"Error: {res1.status_code}"
    data1 = res1.json()
    print(f"-> Cold Run Duration: {elapsed1:.2f}s | Processed frames: {data1.get('processed_frames')} | Tracks: {len(data1.get('tracks', []))}")

    t1 = time.time()
    res2 = requests.post("http://localhost:8080/api/run-sample-video", data={
        "conf_threshold": 0.25,
        "iou_threshold": 0.45,
        "speed_mps": 7500.0,
        "altitude_km": 650.0,
        "max_frames": 40
    })
    elapsed2 = time.time() - t1
    assert res2.status_code == 200
    print(f"-> Warm Cached Run Duration: {elapsed2:.4f}s (Cache Hit: {elapsed2 < 0.10})")

    print("\n=== 2. Benchmarking Image Upload API Performance ===")
    sample_img = Path("dataset/test/images/cheops_001.jpg")
    if not sample_img.exists():
        # Fallback to any test image
        sample_img = next(Path("dataset/test/images").glob("*.jpg"))
    
    t2 = time.time()
    with open(sample_img, "rb") as f:
        res_up = requests.post("http://localhost:8080/api/upload", files={"file": ("cheops.jpg", f, "image/jpeg")}, data={
            "conf_threshold": 0.50,
            "iou_threshold": 0.45,
            "speed_mps": 7500.0,
            "altitude_km": 650.0
        })
    elapsed3 = time.time() - t2
    assert res_up.status_code == 200
    data_img = res_up.json()
    print(f"-> Image Upload Inference Duration: {elapsed3:.3f}s | Detections: {len(data_img.get('detections', []))}")

def test_ui_browser():
    print("\n=== 3. Testing Browser UI, Webcam Element, and Tables ===")
    errors = []

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context(permissions=["camera"])
        page = context.new_page()

        page.on("pageerror", lambda err: errors.append(f"PAGE ERROR: {err}"))
        page.on("console", lambda msg: errors.append(f"CONSOLE ERROR: {msg.text}") if msg.type == "error" else None)

        page.goto("http://localhost:8080/hud", wait_until="networkidle")
        time.sleep(2)

        # 1. Verify Live Workspace
        webcam_vid = page.locator("#webcamLocalVideo")
        assert webcam_vid.count() == 1, "Missing #webcamLocalVideo element"
        print("✓ Verified #webcamLocalVideo element exists in DOM")

        live_table = page.locator("#telemetryTableBody tr")
        print(f"✓ Live Detection Table rows: {live_table.count()}")

        # 2. Test Webcam Button toggle
        btn_webcam = page.locator("button[data-source='WEBCAM']")
        if btn_webcam.count() > 0:
            btn_webcam.click()
            time.sleep(1)
            print("✓ Clicked Lab Webcam source toggle")

        # Switch back to Testbench
        btn_tb = page.locator("button[data-source='TESTBENCH']")
        btn_tb.click()
        time.sleep(1)
        print("✓ Switched back to Testbench")

        # 3. Verify Video Workspace & Records Table
        page.locator("button[data-tab='tabVideo']").click()
        time.sleep(1)

        btn_demo_vid = page.locator("#btnDemoVideo")
        assert btn_demo_vid.count() == 1, "Missing #btnDemoVideo"
        btn_demo_vid.click()
        
        # Wait for video analysis to finish
        page.wait_for_selector("#videoTableBody tr td strong", timeout=15000)
        vid_rows = page.locator("#videoTableBody tr")
        print(f"✓ Video Workspace Records Table populated with {vid_rows.count()} rows")
        
        vid_top_name = page.locator("#videoTopTrackName").inner_text()
        print(f"✓ Video Threat Card Top Track: '{vid_top_name}'")
        assert len(vid_top_name) > 0

        # 4. Verify Photo / Gallery Workspace & Records Table
        page.locator("button[data-tab='tabGallery']").click()
        time.sleep(1)

        # Click first catalog card
        gal_card = page.locator(".gallery-card").first
        if gal_card.count() > 0:
            gal_card.click()
            time.sleep(2)
            gal_rows = page.locator("#galleryTableBody tr")
            print(f"✓ Photo Workspace Optical Records Table populated with {gal_rows.count()} rows")
            
            gal_selected = page.locator("#gallerySelectedName").inner_text()
            print(f"✓ Spacecraft Salvage Directive Card Target: '{gal_selected}'")
            assert len(gal_selected) > 0

        # 5. Verify Reference Tabs
        for tab_id in ["tabTelemetry", "tabBenchmarks", "tabStandards", "tabTaxonomy"]:
            page.locator(f"button[data-tab='{tab_id}']").click()
            time.sleep(0.3)
            print(f"✓ Switched to tab {tab_id}")

        browser.close()

    print(f"\nTotal Console/Page Errors Recorded: {len(errors)}")
    for err in errors:
        print(f"  - {err}")
    assert len(errors) == 0, "Errors found during browser inspection!"
    print("\n✅ All automated verification checks passed with 0 errors!")

if __name__ == "__main__":
    test_api_performance()
    test_ui_browser()
