"""
tracker.py - Multi-Object Kinematics & Rotational Tumble Tracker for SPACI 2.0
=============================================================================
Maintains temporal object track histories, aspect ratio fluctuations (Tumble
Rate estimation via ESA Clean Space ADR criteria), and velocity vectors.
"""

from collections import deque
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
import numpy as np


@dataclass
class TrackHistory:
    track_id: int
    class_name: str
    positions: deque = field(default_factory=lambda: deque(maxlen=30))
    aspect_ratios: deque = field(default_factory=lambda: deque(maxlen=30))
    areas: deque = field(default_factory=lambda: deque(maxlen=30))
    confidences: deque = field(default_factory=lambda: deque(maxlen=30))

    def update(self, bbox: List[float], conf: float, class_name: str):
        self.class_name = class_name
        x1, y1, x2, y2 = bbox
        w = max(1.0, x2 - x1)
        h = max(1.0, y2 - y1)
        cx = (x1 + x2) / 2.0
        cy = (y1 + y2) / 2.0

        self.positions.append((cx, cy))
        self.aspect_ratios.append(w / h)
        self.areas.append(w * h)
        self.confidences.append(conf)

    def get_tumble_rate(self) -> float:
        """
        Calculates tumble rate proxy using rolling variance of aspect ratio:
        sigma^2(AR) = (1 / N-1) sum((AR_i - mean(AR))^2)
        """
        if len(self.aspect_ratios) < 2:
            return 0.0
        ar_array = np.array(self.aspect_ratios)
        variance = float(np.var(ar_array))
        return round(variance, 5)

    def get_velocity_vector(self) -> Tuple[float, float, float]:
        """
        Computes velocity vector (dx, dy) and magnitude in pixels per frame.
        """
        if len(self.positions) < 2:
            return 0.0, 0.0, 0.0
        p_now = self.positions[-1]
        p_prev = self.positions[-2]
        dx = p_now[0] - p_prev[0]
        dy = p_now[1] - p_prev[1]
        speed = float(np.sqrt(dx**2 + dy**2))
        return round(dx, 2), round(dy, 2), round(speed, 2)


class DebrisTracker:
    """
    Manages track states across consecutive video frames with fallback ID assignment.
    """

    def __init__(self, history_len: int = 30):
        self.history_len = history_len
        self.tracks: Dict[int, TrackHistory] = {}
        self.next_id: int = 1

    def reset(self):
        """Clears all track histories for a fresh video stream."""
        self.tracks.clear()
        self.next_id = 1

    def update(self, detections: List[dict]) -> Dict[int, TrackHistory]:
        """
        Updates internal track records with current frame detections.
        Ensures every detection has a unique, consistent positive track ID.

        Args:
            detections: List of dicts with 'track_id', 'bbox' [x1, y1, x2, y2],
                        'confidence', 'class_name'.

        Returns:
            Dictionary of active TrackHistory objects.
        """
        for det in detections:
            tid = det.get("track_id")

            # Fallback ID assignment if YOLO tracker returns -1 or None
            if tid is None or tid <= 0:
                det_bbox = det.get("bbox", [0, 0, 0, 0])
                cx = (det_bbox[0] + det_bbox[2]) / 2.0
                cy = (det_bbox[1] + det_bbox[3]) / 2.0

                matched_id = None
                min_dist = float("inf")
                for existing_id, history in self.tracks.items():
                    if history.positions:
                        last_x, last_y = history.positions[-1]
                        dist = np.sqrt((cx - last_x)**2 + (cy - last_y)**2)
                        # Match if within 85 pixels and same class
                        if dist < 85.0 and dist < min_dist and history.class_name == det["class_name"]:
                            min_dist = dist
                            matched_id = existing_id

                if matched_id is not None:
                    tid = matched_id
                else:
                    tid = self.next_id
                    self.next_id += 1

                det["track_id"] = tid

            if tid not in self.tracks:
                self.tracks[tid] = TrackHistory(
                    track_id=tid,
                    class_name=det["class_name"],
                    positions=deque(maxlen=self.history_len),
                    aspect_ratios=deque(maxlen=self.history_len),
                    areas=deque(maxlen=self.history_len),
                    confidences=deque(maxlen=self.history_len),
                )
            self.tracks[tid].update(det["bbox"], det["confidence"], det["class_name"])

        return self.tracks

    def get_track(self, track_id: int) -> Optional[TrackHistory]:
        return self.tracks.get(track_id)

    def clear(self):
        self.tracks.clear()
