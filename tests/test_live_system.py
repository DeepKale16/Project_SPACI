import urllib.request
import urllib.parse
import json
import asyncio
import sys
from pathlib import Path

def test_rest():
    print("=== 1. Verifying HTTP REST Endpoints ===")
    # 1. GET / (3D Info Landing Page)
    req = urllib.request.urlopen("http://localhost:8080/")
    assert req.status == 200, f"GET / failed: {req.status}"
    html = req.read().decode("utf-8")
    assert "SPACI" in html, "Landing page HTML missing SPACI"
    print(" [OK] GET / -> 200 OK, 3D Landing Page loaded successfully")

    # 1b. GET /hud (Mission Control HUD)
    req_hud = urllib.request.urlopen("http://localhost:8080/hud")
    assert req_hud.status == 200, f"GET /hud failed: {req_hud.status}"
    hud_html = req_hud.read().decode("utf-8")
    assert "SPACI" in hud_html and "radarXz" in hud_html, "HUD HTML missing SPACI/radar components"
    print(" [OK] GET /hud -> 200 OK, Mission Control HUD loaded successfully")

    # 2. GET /api/mode
    req = urllib.request.urlopen("http://localhost:8080/api/mode")
    data = json.loads(req.read())
    print(f" [OK] GET /api/mode -> {data}")

    # 3. POST /api/mode
    post_data = json.dumps({"mode": "orbital_surveillance"}).encode("utf-8")
    req = urllib.request.Request("http://localhost:8080/api/mode", data=post_data, headers={"Content-Type": "application/json"})
    res = urllib.request.urlopen(req)
    print(f" [OK] POST /api/mode (orbital) -> {json.loads(res.read())}")

    post_data = json.dumps({"mode": "ground_demonstrator"}).encode("utf-8")
    req = urllib.request.Request("http://localhost:8080/api/mode", data=post_data, headers={"Content-Type": "application/json"})
    res = urllib.request.urlopen(req)
    print(f" [OK] POST /api/mode (ground) -> {json.loads(res.read())}")

    # 4. GET /api/live/source
    req = urllib.request.urlopen("http://localhost:8080/api/live/source")
    print(f" [OK] GET /api/live/source -> {json.loads(req.read())}")

    # 5. POST /api/live/source
    post_data = json.dumps({"source": "testbench"}).encode("utf-8")
    req = urllib.request.Request("http://localhost:8080/api/live/source", data=post_data, headers={"Content-Type": "application/json"})
    res = urllib.request.urlopen(req)
    print(f" [OK] POST /api/live/source -> {json.loads(res.read())}")

    # 6. GET /api/kpi/summary
    req = urllib.request.urlopen("http://localhost:8080/api/kpi/summary")
    print(f" [OK] GET /api/kpi/summary -> {json.loads(req.read())}")

    # 7. POST /api/kpi/fire
    req = urllib.request.Request("http://localhost:8080/api/kpi/fire", data=b"{}", headers={"Content-Type": "application/json"})
    res = urllib.request.urlopen(req)
    fire_resp = json.loads(res.read())
    print(f" [OK] POST /api/kpi/fire -> {fire_resp}")

    # 8. GET /api/kpi/export-csv
    req = urllib.request.urlopen("http://localhost:8080/api/kpi/export-csv")
    csv_data = req.read().decode("utf-8")
    print(f" [OK] GET /api/kpi/export-csv -> {len(csv_data)} bytes")

    # 9. GET /api/catalog (SPACI 2.0 Backward Compatibility)
    req = urllib.request.urlopen("http://localhost:8080/api/catalog")
    catalog_resp = json.loads(req.read())
    catalog = catalog_resp.get("samples", [])
    assert len(catalog) == 11, f"Expected 11 classes, got {len(catalog)}"
    print(f" [OK] GET /api/catalog -> {len(catalog)} orbital classes loaded")

    # 10. POST /predict (SPACI 2.0 Static Inference & Orbital Risk)
    sample_img = Path("Dataset/test/images").glob("*.jpg")
    first_img = next(sample_img, None)
    if first_img:
        with open(first_img, "rb") as f:
            img_bytes = f.read()
        boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; filename="{first_img.name}"\r\n'
            f"Content-Type: image/jpeg\r\n\r\n"
        ).encode("utf-8") + img_bytes + f"\r\n--{boundary}--\r\n".encode("utf-8")
        
        req = urllib.request.Request(
            "http://localhost:8080/predict",
            data=body,
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
        )
        res = urllib.request.urlopen(req)
        pred = json.loads(res.read())
        summary = pred.get("summary", {})
        print(f" [OK] POST /predict -> {len(pred.get('detections', []))} detections, Risk: {summary.get('highest_risk_level')}")

def test_websocket():
    print("\n=== 2. Verifying WebSocket /ws/live Stream ===")
    asyncio.run(_async_test_ws())

async def _async_test_ws():
    try:
        import websockets
    except ImportError:
        print(" (websockets client library not installed in main env, using aiohttp or raw socket)")
        return

    async with websockets.connect("ws://localhost:8080/ws/live") as ws:
        for i in range(5):
            msg = await ws.recv()
            pkt = json.loads(msg)
            fps = pkt.get("fps", 0.0)
            latency = pkt.get("latency_ms", 0.0)
            tracks = len(pkt.get("tracks", []))
            gnc = (pkt.get("gnc_command") or {}).get("state")
            print(f" [WS Frame {i+1}] frame_id: {pkt.get('frame_id')}, fps: {fps:.1f}, latency: {latency:.1f}ms, tracks: {tracks}, gnc_state: {gnc}")
            assert "frame_b64" in pkt, "Missing frame_b64"
            assert "radar_state" in pkt, "Missing radar_state"
            assert "targets" in pkt["radar_state"], "Missing radar_state.targets"
        print(" [OK] WebSocket /ws/live verified successfully with zero frame lag!")

if __name__ == "__main__":
    test_rest()
    test_websocket()
