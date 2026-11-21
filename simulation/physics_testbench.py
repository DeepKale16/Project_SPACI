"""
simulation/physics_testbench.py - Deterministic 3D Multi-Object Physics Simulator
=================================================================================
Generates synthetic 640x640 aerospace optical frames with zero external hardware:
- Composites 1-4 moving 3D orbital/ground targets on a starfield canvas
- Calibrated physical mockups (0.35m - 0.85m) at ranges (1.5m - 6.0m)
- In-plane rotation + cyclic foreshortening scale simulating 3D tumble
- Provides true 3D ground truth for Ray-Cast LiDAR and Kalman verification
"""

import math
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import cv2
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEST_IMG_DIR = PROJECT_ROOT / "Dataset" / "test" / "images"

# 11-Class Archetypes & Physical Diameters
TARGET_PRESETS = [
    {"class_name": "debris", "display_name": "Space Debris Fragment", "diam_m": 0.42, "color": (11, 158, 245)},
    {"class_name": "cheops", "display_name": "CHEOPS (ESA Exoplanet)", "diam_m": 0.75, "color": (129, 185, 16)},
    {"class_name": "earth_observation_sat_1", "display_name": "Earth Observation Sat-1", "diam_m": 0.68, "color": (233, 165, 14)},
    {"class_name": "soho", "display_name": "SOHO (Solar Observatory)", "diam_m": 0.82, "color": (129, 185, 16)},
    {"class_name": "lisa_pathfinder", "display_name": "LISA Pathfinder (ESA)", "diam_m": 0.65, "color": (129, 185, 16)},
    {"class_name": "smart_1", "display_name": "SMART-1 (Lunar Demonstrator)", "diam_m": 0.55, "color": (233, 165, 14)},
]


class SimulatedTarget3D:
    """Represents a single 3D target moving along a deterministic trajectory."""

    def __init__(
        self,
        track_id: int,
        preset: Dict[str, Any],
        initial_pos: Tuple[float, float, float],
        velocity: Tuple[float, float, float],
        tumble_omega_rad: float = 1.2,
        template_img: Optional[np.ndarray] = None,
    ):
        self.track_id = track_id
        self.class_name = preset["class_name"]
        self.display_name = preset["display_name"]
        self.diam_m = preset["diam_m"]
        self.color = preset["color"]

        self.pos = np.array(initial_pos, dtype=np.float64)  # [X, Y, Z] in Launcher Frame (+Y up)
        self.vel = np.array(velocity, dtype=np.float64)      # [vx, vy, vz]
        self.tumble_omega = tumble_omega_rad
        self.angle_rad = 0.0
        self.template_img = template_img

    def step(self, dt: float):
        self.pos += self.vel * dt
        self.angle_rad += self.tumble_omega * dt

        # Bounce or loop within lab boundaries
        # X: [-1.8, 1.8], Y: [-0.6, 1.2], Z: [1.5, 6.0]
        if self.pos[0] < -1.8 or self.pos[0] > 1.8:
            self.vel[0] *= -1.0
        if self.pos[1] < -0.6 or self.pos[1] > 1.2:
            self.vel[1] *= -1.0
        if self.pos[2] < 1.6 or self.pos[2] > 5.8:
            self.vel[2] *= -1.0


class PhysicsTestbench:
    """
    Complete Standalone 3D Physics Testbench.
    Zero external dependencies; runs 100% in software.
    """

    def __init__(
        self,
        width: int = 640,
        height: int = 640,
        fx: float = 554.3,
        fy: float = 554.3,
        num_targets: int = 2,
    ):
        self.width = width
        self.height = height
        self.fx = fx
        self.fy = fy
        self.cx = width / 2.0
        self.cy = height / 2.0

        self.targets: List[SimulatedTarget3D] = []
        self._load_templates()
        self.reset(num_targets)

    def _load_templates(self):
        """Preloads real sample images from the dataset as textures."""
        self.templates = {}
        if TEST_IMG_DIR.exists():
            for img_p in list(TEST_IMG_DIR.glob("*.jpg"))[:12]:
                im = cv2.imread(str(img_p))
                if im is not None:
                    # Crop center 300x300
                    h, w = im.shape[:2]
                    ch, cw = h // 2, w // 2
                    crop = im[max(0, ch - 150):min(h, ch + 150), max(0, cw - 150):min(w, cw + 150)]
                    self.templates[len(self.templates)] = crop

    def reset(self, num_targets: int = 2, scenario: str = "default"):
        """Resets targets to a clean, deterministic state."""
        self.targets = []
        templates_list = list(self.templates.values())

        if scenario == "lateral_pass":
            # Fast crossing target
            p = TARGET_PRESETS[0]
            tmpl = templates_list[0] if templates_list else None
            self.targets.append(SimulatedTarget3D(1, p, (-1.2, 0.1, 3.2), (0.8, 0.05, -0.1), 2.5, tmpl))
        elif scenario == "radial_approach":
            # Rapid incoming debris
            p = TARGET_PRESETS[0]
            tmpl = templates_list[0] if templates_list else None
            self.targets.append(SimulatedTarget3D(1, p, (0.05, 0.1, 5.5), (0.02, -0.05, -1.2), 3.2, tmpl))
        else:
            # Default multi-target mix (e.g. 1 debris + 1 satellite)
            for i in range(min(num_targets, len(TARGET_PRESETS))):
                preset = TARGET_PRESETS[i % len(TARGET_PRESETS)]
                init_x = -0.8 + (i * 1.2)
                init_y = 0.1 + (i * 0.15)
                init_z = 2.4 + (i * 1.2)
                vx = 0.35 * (1 if i % 2 == 0 else -1)
                vy = 0.08 * (1 if i % 2 == 0 else -1)
                vz = -0.15 * (i + 1)
                omega = 1.0 + (i * 1.8)
                tmpl = templates_list[i % len(templates_list)] if templates_list else None
                self.targets.append(SimulatedTarget3D(i + 1, preset, (init_x, init_y, init_z), (vx, vy, vz), omega, tmpl))

    def step(self, dt: float = 0.033) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
        """
        Advances the 3D physics simulation by dt seconds and renders the 640x640 frame.
        Returns:
            (frame_bgr, gt_target_records)
        """
        # 1. Base synthetic deep-space starfield canvas
        frame = np.full((self.height, self.width, 3), 4, dtype=np.uint8)

        # Deterministic starfield background
        np.random.seed(42)
        star_xs = np.random.randint(0, self.width, 90)
        star_ys = np.random.randint(0, self.height, 90)
        star_bright = np.random.randint(120, 240, 90)
        for sx, sy, sb in zip(star_xs, star_ys, star_bright):
            frame[sy, sx] = [sb, sb, sb]

        gt_records = []

        # Sort targets by depth Z (back to front) for correct occlusion
        sorted_targets = sorted(self.targets, key=lambda t: t.pos[2], reverse=True)

        for tgt in sorted_targets:
            tgt.step(dt)
            X, Y, Z = tgt.pos
            if Z <= 0.1:
                continue

            # Pinhole projection: Launcher Frame (+Y up) -> Image Plane (v down)
            u = self.fx * (X / Z) + self.cx
            v = self.cy - self.fy * (Y / Z)

            # Metric scale -> pixel dimensions (sweet spot 45px - 240px)
            base_size_px = max(24.0, (tgt.diam_m * self.fx) / Z)

            # 3D Foreshortening simulation: cyclic aspect ratio variation
            # scale = 0.4 + 0.6 * |cos(omega * t)|
            foreshorten = 0.45 + 0.55 * abs(math.cos(tgt.angle_rad))
            w_px = max(20.0, base_size_px)
            h_px = max(16.0, base_size_px * foreshorten)

            # Bounding box coordinates clamped to frame
            x1 = int(round(u - w_px / 2.0))
            y1 = int(round(v - h_px / 2.0))
            x2 = int(round(u + w_px / 2.0))
            y2 = int(round(v + h_px / 2.0))

            x1_c = max(0, min(self.width - 1, x1))
            y1_c = max(0, min(self.height - 1, y1))
            x2_c = max(0, min(self.width - 1, x2))
            y2_c = max(0, min(self.height - 1, y2))

            # Composite mockup texture or shaded 3D ellipsoid
            if (x2_c > x1_c) and (y2_c > y1_c):
                bw = x2_c - x1_c
                bh = y2_c - y1_c

                if tgt.template_img is not None:
                    # Resize and rotate template
                    patch = cv2.resize(tgt.template_img, (bw, bh))
                    # In-plane rotation
                    center = (bw // 2, bh // 2)
                    rot_mat = cv2.getRotationMatrix2D(center, math.degrees(tgt.angle_rad), 1.0)
                    rot_patch = cv2.warpAffine(patch, rot_mat, (bw, bh), borderMode=cv2.BORDER_REFLECT)
                    frame[y1_c:y2_c, x1_c:x2_c] = rot_patch
                else:
                    # Shaded fallback sphere
                    cv2.ellipse(
                        frame,
                        (int(u), int(v)),
                        (int(bw // 2), int(bh // 2)),
                        math.degrees(tgt.angle_rad),
                        0,
                        360,
                        tgt.color,
                        -1,
                    )

            # Ground truth record for LiDAR & GNC verification
            gt_records.append({
                "track_id": tgt.track_id,
                "class_name": tgt.class_name,
                "display_name": tgt.display_name,
                "pos_xyz": (float(X), float(Y), float(Z)),
                "vel_xyz": (float(tgt.vel[0]), float(tgt.vel[1]), float(tgt.vel[2])),
                "bbox_2d": [float(x1_c), float(y1_c), float(x2_c), float(y2_c)],
                "z_m": float(Z),
                "diam_m": float(tgt.diam_m),
                "angle_rad": float(tgt.angle_rad),
            })

        return frame, gt_records
