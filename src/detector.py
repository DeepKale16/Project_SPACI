"""
detector.py - SPACI 2.0 Unified Space Debris Detection & Kinematic Analyzer
===========================================================================
Integrates Ultralytics YOLO inference with DebrisTracker and RiskEngine.
Handles single images, video streams, and batch directories.
"""

from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import cv2
import numpy as np
from ultralytics import YOLO

from src.config import (
    MODELS_DIR,
    CLASS_NAMES,
    CLASS_DISPLAY_NAMES,
    STATE_COLORS_BGR,
    STATE_COLORS_HEX,
    OPERATIONAL_STATES,
)
from src.taxonomy import get_category_for_class, get_display_name
from src.tracker import DebrisTracker
from src.risk_engine import RiskEngine, RiskBreakdown


class SpaceDebrisDetector:
    """
    High-performance detector and operational hazard analyzer.
    """

    def __init__(
        self,
        weights_path: Optional[str | Path] = None,
        conf_threshold: float = 0.25,
        iou_threshold: float = 0.45,
        device: str = "0",
        augment: bool = False,
    ):
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        self.device = device
        self.augment = augment

        if weights_path is None:
            candidate_best = MODELS_DIR / "best.pt"
            candidate_base = MODELS_DIR / "yolo11n.pt"
            if candidate_best.exists():
                self.weights_path = candidate_best
            elif candidate_base.exists():
                self.weights_path = candidate_base
            else:
                self.weights_path = "yolo11n.pt"
        else:
            self.weights_path = Path(weights_path)

        self.model = YOLO(str(self.weights_path))
        self.risk_engine = RiskEngine()
        self.tracker = DebrisTracker()

    def reset_tracker(self):
        """Resets tracker states between video files."""
        self.tracker.reset()

    def set_thresholds(self, conf: float, iou: float, augment: Optional[bool] = None):
        self.conf_threshold = conf
        self.iou_threshold = iou
        if augment is not None:
            self.augment = augment

    def predict_image(
        self,
        image: np.ndarray,
        speed_mps: Optional[float] = None,
        altitude_km: Optional[float] = None,
        augment: Optional[bool] = None,
    ) -> Tuple[np.ndarray, List[Dict[str, Any]], Dict[str, Any]]:
        """
        Runs object detection on a single image and assesses orbital risk.

        Args:
            image: BGR numpy array from cv2.imread or OpenCV.
            speed_mps: Optional relative velocity telemetry.
            altitude_km: Optional orbital altitude telemetry.
            augment: Optional override for Test-Time Augmentation (TTA).

        Returns:
            Tuple of (annotated_bgr_image, detection_records, summary_stats).
        """
        h_img, w_img = image.shape[:2]
        frame_area = float(w_img * h_img)

        use_tta = self.augment if augment is None else augment

        results = self.model.predict(
            source=image,
            conf=self.conf_threshold,
            iou=self.iou_threshold,
            device=self.device,
            verbose=False,
            augment=use_tta,
        )

        detections = []
        raw_boxes = results[0].boxes

        num_objects = len(raw_boxes) if raw_boxes is not None else 0

        if raw_boxes is not None and num_objects > 0:
            for box in raw_boxes:
                cls_id = int(box.cls[0].item())
                conf = float(box.conf[0].item())
                xyxy = box.xyxy[0].cpu().numpy().tolist()
                x1, y1, x2, y2 = xyxy

                w_box = max(1.0, x2 - x1)
                h_box = max(1.0, y2 - y1)
                box_area = w_box * h_box
                area_ratio = box_area / frame_area

                cls_name = self.model.names.get(cls_id, f"class_{cls_id}")

                # Risk calculation
                risk: RiskBreakdown = self.risk_engine.compute(
                    class_name=cls_name,
                    area_ratio=area_ratio,
                    confidence=conf,
                    tumble_rate=0.0,
                    is_video=False,
                    speed_mps=speed_mps,
                    altitude_km=altitude_km,
                    object_count=num_objects,
                )

                detections.append({
                    "class_id": cls_id,
                    "class_name": cls_name,
                    "display_name": get_display_name(cls_name),
                    "confidence": conf,
                    "bbox": [round(c, 2) for c in xyxy],
                    "area_ratio": round(area_ratio, 6),
                    "risk_score": risk.total_score,
                    "operational_state": risk.operational_state,
                    "risk_breakdown": risk,
                })

        # Draw overlays
        annotated = self.render_annotations(image.copy(), detections, is_video=False)

        summary = self._build_summary(detections)
        return annotated, detections, summary

    def track_video_frame(
        self,
        frame: np.ndarray,
        speed_mps: Optional[float] = None,
        altitude_km: Optional[float] = None,
    ) -> Tuple[np.ndarray, List[Dict[str, Any]], Dict[str, Any]]:
        """
        Runs BoT-SORT / ByteTrack tracking on a video frame, updating tumbling
        estimates across temporal observations.
        """
        h_img, w_img = frame.shape[:2]
        frame_area = float(w_img * h_img)

        try:
            results = self.model.track(
                source=frame,
                conf=self.conf_threshold,
                iou=self.iou_threshold,
                device=self.device,
                persist=True,
                tracker="bytetrack.yaml",
                verbose=False,
            )
        except Exception:
            results = self.model.predict(
                source=frame,
                conf=self.conf_threshold,
                iou=self.iou_threshold,
                device=self.device,
                verbose=False,
            )

        detections = []
        raw_boxes = results[0].boxes
        num_objects = len(raw_boxes) if raw_boxes is not None else 0

        if raw_boxes is not None and num_objects > 0:
            for box in raw_boxes:
                cls_id = int(box.cls[0].item())
                conf = float(box.conf[0].item())
                xyxy = box.xyxy[0].cpu().numpy().tolist()
                x1, y1, x2, y2 = xyxy

                w_box = max(1.0, x2 - x1)
                h_box = max(1.0, y2 - y1)
                box_area = w_box * h_box
                area_ratio = box_area / frame_area

                cls_name = self.model.names.get(cls_id, f"class_{cls_id}")
                track_id = int(box.id[0].item()) if (box.id is not None and box.id.numel() > 0) else -1

                detections.append({
                    "track_id": track_id,
                    "class_id": cls_id,
                    "class_name": cls_name,
                    "display_name": get_display_name(cls_name),
                    "confidence": conf,
                    "bbox": [round(c, 2) for c in xyxy],
                    "area_ratio": round(area_ratio, 6),
                })

            # Update tracker history
            self.tracker.update(detections)

            # Compute risk with tumble rate
            for det in detections:
                tid = det["track_id"]
                track_hist = self.tracker.get_track(tid)
                tumble_rate = track_hist.get_tumble_rate() if track_hist else 0.0
                vel_dx, vel_dy, vel_mag = track_hist.get_velocity_vector() if track_hist else (0.0, 0.0, 0.0)

                risk: RiskBreakdown = self.risk_engine.compute(
                    class_name=det["class_name"],
                    area_ratio=det["area_ratio"],
                    confidence=det["confidence"],
                    tumble_rate=tumble_rate,
                    is_video=True,
                    speed_mps=speed_mps,
                    altitude_km=altitude_km,
                    object_count=num_objects,
                )

                det["tumble_rate"] = tumble_rate
                det["velocity_vector"] = (vel_dx, vel_dy)
                det["velocity_speed"] = vel_mag
                det["risk_score"] = risk.total_score
                det["operational_state"] = risk.operational_state
                det["risk_breakdown"] = risk

        annotated = self.render_annotations(
            frame.copy(),
            detections,
            is_video=True,
            speed_mps=speed_mps,
            altitude_km=altitude_km,
        )
        summary = self._build_summary(detections)
        return annotated, detections, summary

    def render_annotations(
        self,
        image: np.ndarray,
        detections: List[Dict[str, Any]],
        is_video: bool = False,
        speed_mps: Optional[float] = None,
        altitude_km: Optional[float] = None,
    ) -> np.ndarray:
        """
        Renders aesthetic cyberpunk/aerospace HUD overlays on the frame.
        """
        h_img, w_img = image.shape[:2]

        # Draw Persistent HUD Flight Telemetry Header on video frames
        if is_video:
            vel_str = f"{speed_mps:.0f} m/s" if speed_mps is not None else "7500 m/s"
            alt_str = f"{altitude_km:.0f} km" if altitude_km is not None else "650 km"
            hud_hdr = f"SPACI 2.0 HUD // FOV: {w_img}x{h_img} // VEL: {vel_str} // ALT: {alt_str}"
            cv2.rectangle(image, (12, 12), (min(w_img - 12, 490), 38), (10, 16, 30), -1)
            cv2.rectangle(image, (12, 12), (min(w_img - 12, 490), 38), (56, 189, 248), 1)
            cv2.putText(image, hud_hdr, (20, 29), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (56, 189, 248), 1, cv2.LINE_AA)

            tgt_color = (68, 68, 239) if any(d.get("operational_state") == "Hazardous" for d in detections) else (16, 185, 129)
            status_text = f"TARGET ACQUISITION: {len(detections)} OBJECTS IN SENSOR FOV"
            cv2.rectangle(image, (12, 42), (min(w_img - 12, 380), 66), (10, 16, 30), -1)
            cv2.rectangle(image, (12, 42), (min(w_img - 12, 380), 66), tgt_color, 1)
            cv2.putText(image, status_text, (20, 58), cv2.FONT_HERSHEY_SIMPLEX, 0.38, tgt_color, 1, cv2.LINE_AA)
        for det in detections:
            x1, y1, x2, y2 = map(int, det["bbox"])
            state = det["operational_state"]
            color = STATE_COLORS_BGR.get(state, (0, 255, 255))
            score = det["risk_score"]
            name = det["display_name"]
            conf = det["confidence"]

            # Main bounding box
            cv2.rectangle(image, (x1, y1), (x2, y2), color, 2, cv2.LINE_AA)

            # Corner accents
            corner_len = min(18, max(5, int((x2 - x1) * 0.2)))
            thick = 3
            # Top-left
            cv2.line(image, (x1, y1), (x1 + corner_len, y1), color, thick)
            cv2.line(image, (x1, y1), (x1, y1 + corner_len), color, thick)
            # Top-right
            cv2.line(image, (x2, y1), (x2 - corner_len, y1), color, thick)
            cv2.line(image, (x2, y1), (x2, y1 + corner_len), color, thick)
            # Bottom-left
            cv2.line(image, (x1, y2), (x1 + corner_len, y2), color, thick)
            cv2.line(image, (x1, y2), (x1, y2 - corner_len), color, thick)
            # Bottom-right
            cv2.line(image, (x2, y2), (x2 - corner_len, y2), color, thick)
            cv2.line(image, (x2, y2), (x2, y2 - corner_len), color, thick)

            # Label text
            tid_str = f"#{det['track_id']} " if is_video and det.get("track_id", -1) != -1 else ""
            label_text = f"{tid_str}{name} | {state.upper()}"
            sub_text = f"Conf: {conf * 100:.1f}% | Risk: {score:.2f}"
            if is_video and "tumble_rate" in det:
                sub_text += f" | Tumble: {det['tumble_rate']:.3f}"

            # Label banner
            (tw1, th1), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.48, 1)
            (tw2, th2), _ = cv2.getTextSize(sub_text, cv2.FONT_HERSHEY_SIMPLEX, 0.42, 1)
            banner_w = max(tw1, tw2) + 14
            banner_h = th1 + th2 + 16

            y_banner_top = max(0, y1 - banner_h)
            cv2.rectangle(image, (x1, y_banner_top), (x1 + banner_w, y_banner_top + banner_h), (15, 23, 42), -1)
            cv2.rectangle(image, (x1, y_banner_top), (x1 + banner_w, y_banner_top + banner_h), color, 1)

            cv2.putText(image, label_text, (x1 + 6, y_banner_top + th1 + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.48, color, 1, cv2.LINE_AA)
            cv2.putText(image, sub_text, (x1 + 6, y_banner_top + th1 + th2 + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (203, 213, 225), 1, cv2.LINE_AA)

            # Draw trajectory trail for video tracking
            if is_video and "track_id" in det:
                track = self.tracker.get_track(det["track_id"])
                if track and len(track.positions) > 1:
                    pts = np.array(list(track.positions), dtype=np.int32).reshape((-1, 1, 2))
                    cv2.polylines(image, [pts], False, color, 2, cv2.LINE_AA)

        return image

    def _build_summary(self, detections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregates detection metrics into an operational status report."""
        state_counts = {s: 0 for s in OPERATIONAL_STATES}
        for det in detections:
            st = det["operational_state"]
            if st in state_counts:
                state_counts[st] += 1

        total = len(detections)
        scores = [d["risk_score"] for d in detections]
        mean_risk = float(np.mean(scores)) if scores else 0.0
        max_risk = float(np.max(scores)) if scores else 0.0

        return {
            "total_objects": total,
            "state_counts": state_counts,
            "mean_risk": round(mean_risk, 3),
            "max_risk": round(max_risk, 3),
            "hazardous_count": state_counts["Hazardous"],
            "reusable_count": state_counts["Reusable / Salvageable"],
            "active_count": state_counts["Useful / Active"],
            "fragment_count": state_counts["Inert Fragment"],
        }
