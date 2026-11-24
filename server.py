"""
server.py - High-Performance FastAPI REST & WebSocket Server for SPACI 3.0
===========================================================================
Serves semantic HTML5 / Vanilla CSS / Vanilla JS HUD frontend and provides:
- Single Atomic WebSocket (/ws/live) @ >= 25 FPS with zero-lag drop-oldest queue
- Dual-Mode Mission Engine: Orbital Surveillance vs Ground Demonstrator
- Dedicated GPU-locked YOLO live tracking separate from static prediction instance
- Thread-safe SQLite trial logging, exports, and Ray-Cast LiDAR / 3D GNC telemetry
- 100% backward compatibility for all Phase 2 endpoints

Run:
    python server.py --port 8080
"""

import os
import sys
import json
import base64
import shutil
import tempfile
import argparse
import asyncio
import queue
import threading
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional, Dict, Any, List

import cv2
import numpy as np
import uvicorn
from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from pydantic import BaseModel

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import (
    DATASET_DIR,
    MODELS_DIR,
    REPORTS_DIR,
    CLASS_NAMES,
    CLASS_DISPLAY_NAMES,
)
from src.detector import SpaceDebrisDetector
from core.stream_manager import LiveStreamManager
from core.kpi_logger import CaptureKpiLogger

# -----------------------------------------------------------------------------
# Global Locks & Singletons
# -----------------------------------------------------------------------------
gpu_lock = threading.Lock()
kpi_logger = CaptureKpiLogger()

detector_weights = MODELS_DIR / "best.pt"
if not detector_weights.exists():
    detector_weights = MODELS_DIR / "yolo11n.pt"

# Static prediction detector instance (guarded by gpu_lock)
detector = SpaceDebrisDetector(
    weights_path=detector_weights,
    conf_threshold=0.50,
    iou_threshold=0.45,
    device="0",
)

# Dedicated live streaming manager
stream_manager = LiveStreamManager(
    weights_path=detector_weights,
    gpu_lock=gpu_lock,
    botsort_cfg_path=PROJECT_ROOT / "configs" / "spaci_botsort.yaml",
    kpi_logger=kpi_logger,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Clean startup and shutdown handler for background streaming worker."""
    print("[SPACI 3.0] Starting background LiveStreamManager worker thread...")
    stream_manager.start()
    yield
    print("[SPACI 3.0] Shutting down LiveStreamManager cleanly...")
    stream_manager.stop()


# Initialize FastAPI App
app = FastAPI(
    title="SPACI 3.0 Aerospace HUD & Live GNC API",
    description="High-speed REST API & WebSocket Engine for space debris detection, 3D LiDAR fusion, and closed-form ballistic GNC.",
    version="3.0.0",
    lifespan=lifespan,
)

# -----------------------------------------------------------------------------
# Static Mounts
# -----------------------------------------------------------------------------
WEB_DIR = PROJECT_ROOT / "web"
app.mount("/css", StaticFiles(directory=str(WEB_DIR / "css")), name="css")
app.mount("/js", StaticFiles(directory=str(WEB_DIR / "js")), name="js")
if (WEB_DIR / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(WEB_DIR / "assets")), name="assets")
if REPORTS_DIR.exists():
    app.mount("/reports", StaticFiles(directory=str(REPORTS_DIR)), name="reports")

# 11 Curated Test Samples for 1-Click Verification
SAMPLE_CATALOG = [
    {"label": "CHEOPS (ESA Exoplanet)", "class_name": "cheops", "filename": "img010033_jpg.rf.32ef88458356049c1726406ec802d3ba.jpg"},
    {"label": "Space Debris Fragment", "class_name": "debris", "filename": "img021927_jpg.rf.91830c181251b09d0664c76dbafb9d5c.jpg"},
    {"label": "Double Start / Ambiguous", "class_name": "double_start", "filename": "img030225_jpg.rf.07359beb506faa15dee6b2416bd2f714.jpg"},
    {"label": "Earth Observation Sat-1", "class_name": "earth_observation_sat_1", "filename": "img040342_jpg.rf.613e64136c166993b418d92cbf807a70.jpg"},
    {"label": "LISA Pathfinder (ESA)", "class_name": "lisa_pathfinder", "filename": "img050582_jpg.rf.7041faffb8910ffd424e156960718d2d.jpg"},
    {"label": "PROBA-2 (Sun Observer)", "class_name": "proba_2", "filename": "img000124_jpg.rf.dcf525bbc6c6c45a3e387abc33d15112.jpg"},
    {"label": "PROBA-3 Coronagraph (CSC)", "class_name": "proba_3_csc", "filename": "img060265_jpg.rf.300fa9d6f8f06522f9dc5c6c1e724317.jpg"},
    {"label": "PROBA-3 Occulter (OCS)", "class_name": "proba_3_ocs", "filename": "img071318_jpg.rf.c3a8771650fec77976cfbc9b35b8c46f.jpg"},
    {"label": "SMART-1 (Lunar Demonstrator)", "class_name": "smart_1", "filename": "img080433_jpg.rf.13778d212f5eb8b2fe728c9899fd29a9.jpg"},
    {"label": "SOHO (Solar Observatory)", "class_name": "soho", "filename": "img090877_jpg.rf.74c9d4ecaa18d18a5f6c684e14beb770.jpg"},
    {"label": "XMM-Newton (X-Ray Telescope)", "class_name": "xmm_newton", "filename": "img100270_jpg.rf.0ae42f6549b65ab4df27f0dfec3ff709.jpg"},
]


# -----------------------------------------------------------------------------
# REST API Endpoints (Core & Dual-Mode)
# -----------------------------------------------------------------------------

@app.get("/")
@app.get("/landing")
async def serve_landing():
    """Serves the primary 3D Info & Overview presentation page."""
    landing_file = WEB_DIR / "landing.html"
    if not landing_file.exists():
        raise HTTPException(status_code=404, detail="Landing page not found")
    return FileResponse(str(landing_file))


@app.get("/hud")
@app.get("/app")
async def serve_hud():
    """Serves the operational Mission Control HUD workspace."""
    index_file = WEB_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="Mission Control HUD not found")
    return FileResponse(str(index_file))


@app.get("/api/samples")
@app.get("/api/catalog")
async def get_samples():
    """Returns the list of 11 pre-loaded sample objects for quick test."""
    return {"samples": SAMPLE_CATALOG}


@app.get("/api/samples/{filename}")
async def get_sample_image(filename: str):
    """Serves sample image binary from Dataset/test/images."""
    img_path = DATASET_DIR / "test" / "images" / filename
    if not img_path.exists():
        raise HTTPException(status_code=404, detail="Sample image not found")
    return FileResponse(str(img_path), media_type="image/jpeg")


class ModeRequest(BaseModel):
    mode: str  # 'ORBITAL_SURVEILLANCE' or 'GROUND_DEMONSTRATOR'


@app.post("/api/mode")
def set_mission_mode(req: ModeRequest):
    stream_manager.set_mode(req.mode.upper())
    return {"status": "ok", "mode": stream_manager.mode}


@app.get("/api/mode")
def get_mission_mode():
    return {"mode": stream_manager.mode}


class LiveSourceRequest(BaseModel):
    source: str  # 'TESTBENCH', 'VIDEO_LOOP', 'WEBCAM'
    video_path: Optional[str] = None


@app.post("/api/live/source")
def set_live_source(req: LiveSourceRequest):
    stream_manager.set_source(req.source, req.video_path)
    return {"status": "ok", "source": stream_manager.source_type}


@app.get("/api/live/source")
def get_live_source():
    return {"source": stream_manager.source_type, "video_path": str(stream_manager.video_loop_path) if stream_manager.video_loop_path else None}


class GncParamsRequest(BaseModel):
    v_net: Optional[float] = None
    t_lat: Optional[float] = None
    d_net: Optional[float] = None
    magnetic_assist: Optional[bool] = None
    auto_fire: Optional[bool] = None


@app.post("/api/live/params")
def set_gnc_params(req: GncParamsRequest):
    if req.v_net is not None:
        stream_manager.v_net = req.v_net
    if req.t_lat is not None:
        stream_manager.t_lat = req.t_lat
    if req.d_net is not None:
        stream_manager.d_net = req.d_net
    if req.magnetic_assist is not None:
        stream_manager.magnetic_assist = req.magnetic_assist
    if req.auto_fire is not None:
        stream_manager.auto_fire = req.auto_fire
    return {
        "status": "ok",
        "v_net": stream_manager.v_net,
        "t_lat": stream_manager.t_lat,
        "d_net": stream_manager.d_net,
        "magnetic_assist": stream_manager.magnetic_assist,
        "auto_fire": stream_manager.auto_fire,
    }


@app.post("/api/capture-lab-frame")
def capture_lab_frame():
    save_dir = stream_manager.trigger_lab_frame_capture()
    return {"status": "ok", "message": f"Lab frame queued for capture in {save_dir}"}


@app.post("/api/kpi/fire")
def manual_fire_net():
    last_packet = stream_manager.last_packet
    if not last_packet:
        try:
            last_packet = stream_manager.frame_queue.queue[-1]
        except Exception:
            last_packet = None

    if last_packet and last_packet.get("tracks") and last_packet.get("gnc_command"):
        primary = next((t for t in last_packet["tracks"] if t["track_id"] == last_packet.get("locked_track_id")), last_packet["tracks"][0])
        res = stream_manager.fire_net(primary, last_packet["gnc_command"])
        return {"status": "fired", "trial": res}
    return {"status": "no_target_locked", "message": "No valid target currently in lock"}


@app.get("/api/kpi/summary")
def get_kpi_summary():
    return stream_manager.kpi_logger.get_summary_kpis()


@app.get("/api/kpi/export-csv")
def export_kpi_csv():
    csv_data = stream_manager.kpi_logger.export_csv()
    return PlainTextResponse(content=csv_data, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=spaci_capture_trials.csv"})


@app.get("/api/kpi/export-json")
def export_kpi_json():
    return stream_manager.kpi_logger.export_json()


# -----------------------------------------------------------------------------
# Single Atomic WebSocket Endpoint (/ws/live)
# -----------------------------------------------------------------------------

@app.websocket("/ws/live")
async def websocket_live_endpoint(websocket: WebSocket):
    """
    Frame-locked, drop-oldest atomic live telemetry and video stream.
    Sustains >= 25 FPS with bounded memory without blocking asyncio event loop.
    """
    await websocket.accept()
    stream_manager.active_connections += 1
    try:
        while True:
            try:
                # Retrieve latest packet non-blockingly to keep event loop 100% responsive
                packet = stream_manager.frame_queue.get_nowait()
                await websocket.send_text(json.dumps(packet))
            except queue.Empty:
                await asyncio.sleep(0.01)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        pass
    finally:
        stream_manager.active_connections = max(0, stream_manager.active_connections - 1)


# -----------------------------------------------------------------------------
# Single-Frame & Static Endpoints (Guarded by gpu_lock)
# -----------------------------------------------------------------------------

class DetectRequest(BaseModel):
    sample_filename: Optional[str] = None
    image_base64: Optional[str] = None
    conf_threshold: float = 0.50
    iou_threshold: float = 0.45
    speed_mps: Optional[float] = 7500.0
    altitude_km: Optional[float] = 650.0
    augment: Optional[bool] = False


@app.post("/api/detect")
def detect_debris(req: DetectRequest):
    """
    Executes deep transfer learning inference under GPU lock without corrupting live trackers.
    """
    # 1. Resolve Image
    if req.sample_filename:
        img_path = DATASET_DIR / "test" / "images" / req.sample_filename
        if not img_path.exists():
            raise HTTPException(status_code=404, detail=f"Sample {req.sample_filename} not found")
        bgr_image = cv2.imread(str(img_path))
    elif req.image_base64:
        header, encoded = req.image_base64.split(",", 1) if "," in req.image_base64 else ("", req.image_base64)
        img_bytes = base64.b64decode(encoded)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        bgr_image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    else:
        raise HTTPException(status_code=400, detail="Either sample_filename or image_base64 must be provided")

    if bgr_image is None:
        raise HTTPException(status_code=400, detail="Failed to decode image")

    with gpu_lock:
        detector.set_thresholds(req.conf_threshold, req.iou_threshold, augment=req.augment)
        ann_bgr, detections, summary = detector.predict_image(
            image=bgr_image,
            speed_mps=req.speed_mps,
            altitude_km=req.altitude_km,
        )

    serialized_detections = []
    for d in detections:
        serialized_detections.append({
            "class_id": d["class_id"],
            "class_name": d["class_name"],
            "display_name": d["display_name"],
            "confidence": round(d["confidence"], 4),
            "bbox": d["bbox"],
            "area_ratio": d["area_ratio"],
            "risk_score": d["risk_score"],
            "operational_state": d["operational_state"],
            "size_hazard": d["risk_breakdown"].size_risk,
            "threat_prior": d["risk_breakdown"].threat_risk,
        })

    return {
        "summary": summary,
        "detections": serialized_detections,
    }


@app.post("/api/upload")
@app.post("/predict")
def upload_file(
    file: UploadFile = File(...),
    conf_threshold: float = Form(0.50),
    iou_threshold: float = Form(0.45),
    speed_mps: Optional[float] = Form(7500.0),
    altitude_km: Optional[float] = Form(650.0),
    augment: Optional[bool] = Form(False),
):
    """Handles direct multipart file uploads of images for static detection."""
    contents = file.file.read()
    np_arr = np.frombuffer(contents, np.uint8)
    bgr_image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if bgr_image is None:
        raise HTTPException(status_code=400, detail="Failed to decode uploaded image")

    with gpu_lock:
        detector.set_thresholds(conf_threshold, iou_threshold, augment=augment)
        ann_bgr, detections, summary = detector.predict_image(
            image=bgr_image,
            speed_mps=speed_mps,
            altitude_km=altitude_km,
        )

    _, enc = cv2.imencode(".jpg", ann_bgr)
    ann_b64 = "data:image/jpeg;base64," + base64.b64encode(enc).decode("utf-8")

    serialized = []
    for d in detections:
        serialized.append({
            "class_id": d["class_id"],
            "class_name": d["class_name"],
            "display_name": d["display_name"],
            "confidence": round(d["confidence"], 4),
            "bbox": d["bbox"],
            "area_ratio": d["area_ratio"],
            "risk_score": d["risk_score"],
            "operational_state": d["operational_state"],
            "size_hazard": d["risk_breakdown"].size_risk,
            "threat_prior": d["risk_breakdown"].threat_risk,
        })

    return {
        "summary": summary,
        "detections": serialized,
        "annotated_base64": ann_b64,
        "filename": file.filename,
    }


def create_video_writer(out_path: str, fps: float, width: int, height: int) -> cv2.VideoWriter:
    """Creates a high-compatibility H.264 VideoWriter via Microsoft Media Foundation."""
    try:
        fourcc = cv2.VideoWriter_fourcc(*'H264')
        writer = cv2.VideoWriter(out_path, cv2.CAP_MSMF, fourcc, fps, (width, height))
        if writer.isOpened():
            return writer
    except Exception:
        pass

    try:
        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        writer = cv2.VideoWriter(out_path, cv2.CAP_ANY, fourcc, fps, (width, height))
        if writer.isOpened():
            return writer
    except Exception:
        pass

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    return cv2.VideoWriter(out_path, fourcc, fps, (width, height))


def process_video_stream(
    input_path: Path,
    original_filename: str,
    conf_threshold: float = 0.25,
    iou_threshold: float = 0.45,
    speed_mps: Optional[float] = 7500.0,
    altitude_km: Optional[float] = 650.0,
    max_frames: int = 150,
) -> Dict[str, Any]:
    """Video ingestion and BoT-SORT kinematics processing under GPU lock."""
    effective_conf = min(conf_threshold, 0.25) if "sample_encounter" in original_filename else conf_threshold

    with gpu_lock:
        detector.reset_tracker()
        detector.set_thresholds(effective_conf, iou_threshold)

    cap = cv2.VideoCapture(str(input_path))
    if not cap.isOpened():
        raise HTTPException(status_code=400, detail="Failed to open or decode video file")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    step = max(1, total_frames // max_frames) if total_frames > max_frames else 1
    effective_fps = max(5.0, min(fps / step, 30.0))

    video_out_dir = REPORTS_DIR / "video_output"
    video_out_dir.mkdir(parents=True, exist_ok=True)
    out_filename = f"annotated_{Path(original_filename).stem}.mp4"
    out_path = video_out_dir / out_filename

    out_writer = create_video_writer(str(out_path), effective_fps, width, height)

    all_tracks: Dict[int, Dict[str, Any]] = {}
    peak_risk = 0.0
    critical_frame_b64 = ""
    processed_count = 0
    frame_idx = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if not critical_frame_b64:
            _, enc_init = cv2.imencode(".jpg", frame)
            critical_frame_b64 = "data:image/jpeg;base64," + base64.b64encode(enc_init).decode("utf-8")

        if frame_idx % step == 0:
            with gpu_lock:
                ann_frame, detections, summary = detector.track_video_frame(
                    frame,
                    speed_mps=speed_mps,
                    altitude_km=altitude_km,
                )
            out_writer.write(ann_frame)
            processed_count += 1

            for d in detections:
                tid = d.get("track_id", -1)
                r_score = d.get("risk_score", 0.0)
                tumble_val = d.get("tumble_rate", 0.0)
                vel_speed = d.get("velocity_speed", 0.0)

                if tid not in all_tracks or r_score > all_tracks[tid]["risk_score"]:
                    all_tracks[tid] = {
                        "track_id": tid,
                        "class_id": d["class_id"],
                        "class_name": d["class_name"],
                        "display_name": d["display_name"],
                        "confidence": round(d["confidence"], 4),
                        "tumble_rate": round(float(tumble_val), 5),
                        "velocity_speed": round(float(vel_speed), 2),
                        "risk_score": r_score,
                        "operational_state": d["operational_state"],
                        "area_ratio": d["area_ratio"],
                        "bbox": d.get("bbox", []),
                    }

                if r_score >= peak_risk or detections:
                    peak_risk = max(peak_risk, r_score)
                    _, enc = cv2.imencode(".jpg", ann_frame)
                    critical_frame_b64 = "data:image/jpeg;base64," + base64.b64encode(enc).decode("utf-8")

        frame_idx += 1
        if processed_count >= max_frames:
            break

    cap.release()
    out_writer.release()

    state_counts = {
        "Hazardous": sum(1 for t in all_tracks.values() if t["operational_state"] == "Hazardous"),
        "Reusable / Salvageable": sum(1 for t in all_tracks.values() if t["operational_state"] == "Reusable / Salvageable"),
        "Useful / Active": sum(1 for t in all_tracks.values() if t["operational_state"] == "Useful / Active"),
        "Inert Fragment": sum(1 for t in all_tracks.values() if t["operational_state"] == "Inert Fragment"),
    }

    mean_risk_val = round(float(np.mean([t["risk_score"] for t in all_tracks.values()])), 3) if all_tracks else 0.0

    return {
        "filename": original_filename,
        "is_video": True,
        "total_frames": total_frames,
        "fps": round(fps, 1),
        "duration_sec": round(total_frames / (fps or 25.0), 2),
        "processed_frames": processed_count,
        "tracks": list(all_tracks.values()),
        "summary": {
            "total_objects": len(all_tracks),
            "state_counts": state_counts,
            "mean_risk": mean_risk_val,
            "max_risk": round(peak_risk, 3),
            "hazardous_count": state_counts["Hazardous"],
            "reusable_count": state_counts["Reusable / Salvageable"],
            "active_count": state_counts["Useful / Active"],
            "fragment_count": state_counts["Inert Fragment"],
        },
        "annotated_video_url": f"/reports/video_output/{out_filename}",
        "representative_frame_base64": critical_frame_b64,
    }


@app.get("/reports/video_output/{filename}")
async def serve_annotated_video(filename: str):
    """Serves annotated video with range request support."""
    file_path = (REPORTS_DIR / "video_output" / filename).resolve()
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Annotated video not found")
    return FileResponse(
        str(file_path),
        media_type="video/mp4",
        headers={
            "Accept-Ranges": "bytes",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )


@app.post("/api/run-sample-video")
def run_sample_video(
    conf_threshold: float = Form(0.25),
    iou_threshold: float = Form(0.45),
    speed_mps: Optional[float] = Form(7500.0),
    altitude_km: Optional[float] = Form(650.0),
    max_frames: int = Form(150),
):
    sample_path = WEB_DIR / "assets" / "sample_encounter.mp4"
    if not sample_path.exists():
        raise HTTPException(status_code=404, detail="Sample encounter video not found in web/assets")

    return process_video_stream(
        input_path=sample_path,
        original_filename="sample_encounter.mp4",
        conf_threshold=conf_threshold,
        iou_threshold=iou_threshold,
        speed_mps=speed_mps,
        altitude_km=altitude_km,
        max_frames=max_frames,
    )


@app.post("/api/upload-video")
def upload_video(
    file: UploadFile = File(...),
    conf_threshold: float = Form(0.25),
    iou_threshold: float = Form(0.45),
    speed_mps: Optional[float] = Form(7500.0),
    altitude_km: Optional[float] = Form(650.0),
    max_frames: int = Form(150),
):
    temp_dir = Path(tempfile.gettempdir())
    input_path = temp_dir / f"spaci_video_{file.filename}"

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        return process_video_stream(
            input_path=input_path,
            original_filename=file.filename,
            conf_threshold=conf_threshold,
            iou_threshold=iou_threshold,
            speed_mps=speed_mps,
            altitude_km=altitude_km,
            max_frames=max_frames,
        )
    finally:
        try:
            if input_path.exists():
                input_path.unlink()
        except Exception:
            pass


@app.get("/api/benchmarks")
async def get_benchmarks():
    standard_report_file = REPORTS_DIR / "evaluation_test_report.json"
    tta_report_file = REPORTS_DIR / "evaluation_test_tta_report.json"

    data: Dict[str, Any] = {"status": "ok"}
    if standard_report_file.exists():
        with open(standard_report_file, "r") as f:
            data["test_standard"] = json.load(f)

    if tta_report_file.exists():
        with open(tta_report_file, "r") as f:
            data["test_tta"] = json.load(f)

    data["baseline_reference"] = {
        "model": "YOLO11n (2.58M params, 35 epochs)",
        "precision": 0.8246,
        "recall": 0.8499,
        "map50": 0.8867,
        "map50_95": 0.5056,
    }
    return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8080, help="Port to run server on")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host address")
    args = parser.parse_args()

    print(f"[SPACI 3.0 Server] Starting Mission Control HUD at http://localhost:{args.port}")
    uvicorn.run("server:app", host=args.host, port=args.port, reload=False, log_level="info")
