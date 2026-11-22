from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    try:
        browser = p.chromium.launch(channel="msedge", headless=True)
    except Exception:
        browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 900})

    console_logs = []
    page_errors = []

    page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
    page.on("pageerror", lambda err: page_errors.append(str(err)))

    print("Navigating to http://localhost:8080...")
    page.goto("http://localhost:8080", wait_until="domcontentloaded", timeout=10000)
    page.wait_for_timeout(2500)

    # 1. Check Scroll Position
    scroll_y = page.evaluate("window.scrollY")
    print(f"Window Scroll Y: {scroll_y} (Target: 0)")

    # 2. Check Live FPS pill
    fps_text = page.locator("#liveFpsPill").inner_text()
    print(f"Live FPS Pill: {fps_text}")

    # 3. Check Workspace Banner
    workspace_title = page.locator("#currentWorkspaceTitle").inner_text()
    print(f"Active Workspace Title: {workspace_title}")

    # 4. Check Navigation Buttons
    tabs = page.query_selector_all(".tab-btn")
    print(f"Found {len(tabs)} Navigation Tab Buttons:")
    for t in tabs:
        tid = t.get_attribute("data-tab")
        tclass = t.get_attribute("class")
        box = t.bounding_box()
        ttext = t.inner_text().replace("\n", " ").strip()
        print(f" - [{tid}] class='{tclass}' | box: x={round(box['x'],1)}, y={round(box['y'],1)}, w={round(box['width'],1)} | text: '{ttext}'")

    # 5. Full Page Screenshot of Initial Load
    page.screenshot(path="reports/debug_hud_view.png", full_page=True)
    print("Full page screenshot saved to reports/debug_hud_view.png")

    # 6. Test Interactive Tab Switching
    print("\nTesting Interactive Tab Switching:")
    for tab_id in ["tabVideo", "tabGallery", "tabTelemetry", "tabBenchmarks", "tabStandards", "tabTaxonomy", "tabLive"]:
        btn = page.locator(f"[data-tab='{tab_id}']")
        btn.click()
        page.wait_for_timeout(400)
        active_title = page.locator("#currentWorkspaceTitle").inner_text()
        panel_class = page.locator(f"#{tab_id}").get_attribute("class")
        btn_class = btn.get_attribute("class")
        is_active = "active" in btn_class and "hidden" not in panel_class
        print(f" -> Switched to {tab_id}: active={is_active} | Workspace: '{active_title}'")

    # Return to live tab and capture final view
    page.locator("[data-tab='tabLive']").click()
    page.wait_for_timeout(1000)
    page.screenshot(path="reports/debug_hud_final.png", full_page=False)
    print("Viewport screenshot saved to reports/debug_hud_final.png")

    print(f"\nConsole Logs ({len(console_logs)}):")
    for log in console_logs:
        print(" ", log)

    print(f"Page Errors ({len(page_errors)}):")
    for err in page_errors:
        print("  ERROR:", err)

    browser.close()
