# SPACI 3.0: REST & WebSocket API Specification

FastAPI Server running locally on `http://localhost:8080`.

---

## 1. Real-Time Telemetry Stream

### `GET /ws/live` (WebSocket)
Frame-locked, drop-oldest atomic live telemetry and video stream.

#### Frame Packet Schema (JSON)
```json
{
  "frame_id": 829,
  "timestamp_ms": 1795272699953,
  "fps": 28.5,
  "latency_ms": 18.2,
  "mode": "GROUND_DEMONSTRATOR",
  "source": "TESTBENCH",
  "depth_source": "SIMULATED_RAYCAST_LIDAR",
  "frame_b64": "data:image/jpeg;base64,...",
  "tracks": [
    {
      "track_id": 1,
      "class_id": 1,
      "class_name": "debris",
      "confidence": 0.88,
      "bbox": [180, 210, 290, 320],
      "pos_xyz": [-0.15, 0.05, 3.2],
      "vel_xyz": [0.08, -0.02, -0.45],
      "tumble_variance": 0.0142,
      "estimated_diameter_m": 0.42
    }
  ],
  "locked_track_id": 1,
  "gnc_command": {
    "state": "FIRE_READY",
    "track_id": 1,
    "intercept_pos": [-0.12, 0.04, 3.02],
    "aim_pos": [-0.12, 0.65, 3.02],
    "pan_deg": -2.3,
    "tilt_deg": 12.1,
    "t_flight_s": 0.38,
    "net_open_pct": 82.5,
    "safety_status": "GO"
  },
  "radar_state": {
    "targets": [
      { "track_id": 1, "class_name": "debris", "x_m": -0.15, "y_m": 0.05, "z_m": 3.2 }
    ],
    "net_arc_3d": [
      [0.0, 0.0, 0.0],
      [-0.03, 0.16, 0.75],
      [-0.12, 0.04, 3.02]
    ],
    "launcher_fov_cone": { "max_range_m": 7.0, "hfov_deg": 60.0 }
  }
}
```

---

## 2. Mission Control REST Endpoints

### `GET /api/mode`
Returns active mission mode.
- **Response:** `{"mode": "GROUND_DEMONSTRATOR"}`

### `POST /api/mode`
Switches operating mode.
- **Body:** `{"mode": "ORBITAL_SURVEILLANCE"}` or `{"mode": "GROUND_DEMONSTRATOR"}`
- **Response:** `{"status": "ok", "mode": "ORBITAL_SURVEILLANCE"}`

### `GET /api/live/source`
Returns active video/simulation feed.
- **Response:** `{"source": "TESTBENCH", "video_path": null}`

### `POST /api/live/source`
Selects stream input source.
- **Body:** `{"source": "TESTBENCH"}` | `{"source": "VIDEO_LOOP", "video_path": "web/assets/sample_encounter.mp4"}` | `{"source": "WEBCAM"}`
- **Response:** `{"status": "ok", "source": "TESTBENCH"}`

### `POST /api/live/params`
Configures live GNC and launcher hardware parameters.
- **Body:**
  ```json
  {
    "v_net": 9.5,
    "t_lat": 0.02,
    "d_net": 1.2,
    "magnetic_assist": true,
    "auto_fire": false
  }
  ```

### `POST /api/capture-lab-frame`
Triggers saving the current webcam/testbench frame to `data/lab_frames/` with timestamped annotation.

---

## 3. Net Capture KPI & Logging Endpoints

### `POST /api/kpi/fire`
Manually commands net launch against currently locked target.
- **Response:**
  ```json
  {
    "status": "fired",
    "trial": {
      "timestamp_ms": 1795272699953,
      "target_class": "debris",
      "capture_success": true,
      "miss_error_cm": 4.86,
      "effective_radius_cm": 60.0,
      "magnetic_assist": true,
      "fidelity": "GROUND_TRUTH_SIM"
    }
  }
  ```

### `GET /api/kpi/summary`
Returns aggregate KPI performance.
- **Response:**
  ```json
  {
    "total_trials": 24,
    "capture_success_rate_pct": 75.0,
    "mean_deployment_distance_m": 3.42,
    "mean_miss_error_cm": 6.12,
    "mean_detection_confidence_pct": 88.4,
    "mean_latency_ms": 18.2,
    "mean_fps": 28.5
  }
  ```

### `GET /api/kpi/export-csv`
Downloads `spaci_capture_trials.csv` attachment.

### `GET /api/kpi/export-json`
Returns full trial records as a JSON array.

---

## 4. SPACI 2.0 Backward-Compatible Endpoints

### `GET /api/catalog` (or `/api/samples`)
Returns 11 pre-loaded curated test images for 1-click inspection.

### `POST /api/detect`
Performs static image detection under GPU lock:
```json
{
  "sample_filename": "img010033_jpg.rf.32ef88458356049c1726406ec802d3ba.jpg",
  "conf_threshold": 0.50,
  "iou_threshold": 0.45,
  "speed_mps": 7500.0,
  "altitude_km": 650.0
}
```

### `POST /api/upload` (or `/predict`)
Direct multipart file upload of image for visual detection and NASA/ESA risk classification.
