"""
core/sensor_fusion.py - 3D Multi-Sensor Fusion & Coordinate Kinematics
======================================================================
Implements:
- Launcher Coordinate Frame (+X Right, +Y Up, +Z Forward)
- 2D <-> 3D bidirectional pinhole projection
- Robust MAD / IQR outlier filtering for ray-cast LiDAR (rejects 8.0 m wall clutter)
- Non-circular physical diameter estimation (D_est = w * Z / fx)
"""

from typing import Tuple, List, Optional, Dict, Any
import numpy as np


class SensorFusionEngine:
    """
    Fuses 2D optical detections with 3D LiDAR point clouds or depth readings.
    Enforces the single standard right-handed Launcher Coordinate Frame:
      +X: Right
      +Y: Up (opposing gravity)
      +Z: Forward along optical bore
    """

    def __init__(
        self,
        fx: float = 554.3,
        fy: float = 554.3,
        cx: float = 320.0,
        cy: float = 320.0,
        wall_distance_m: float = 8.0,
    ):
        self.fx = fx
        self.fy = fy
        self.cx = cx
        self.cy = cy
        self.wall_distance_m = wall_distance_m

    def pixel_to_launcher(self, u: float, v: float, z: float) -> Tuple[float, float, float]:
        """
        Transforms 2D image plane coordinates (u, v) and depth Z into
        3D Launcher Coordinate Frame (X, Y, Z) with +Y pointing UP.
        """
        X = (u - self.cx) * z / self.fx
        Y = -(v - self.cy) * z / self.fy
        Z = float(z)
        return float(X), float(Y), Z

    def launcher_to_pixel(self, X: float, Y: float, Z: float) -> Tuple[float, float, bool]:
        """
        Transforms 3D Launcher Frame (X, Y, Z) to 2D image pixel coordinates (u, v).
        Returns (u, v, is_in_front).
        """
        if Z <= 1e-4:
            return float(self.cx), float(self.cy), False

        u = self.fx * (X / Z) + self.cx
        v = self.cy - self.fy * (Y / Z)
        is_in_front = Z > 0
        return float(u), float(v), is_in_front

    def filter_lidar_outliers(self, raw_points_3d: np.ndarray) -> Tuple[float, float, int]:
        """
        Applies Median Absolute Deviation (MAD) / IQR clustering to raw 3D LiDAR points
        to reject background wall clutter (at 8.0m) and extract the true foreground target depth.
        """
        if raw_points_3d is None or len(raw_points_3d) == 0:
            return self.wall_distance_m, 1.0, 0

        z_vals = raw_points_3d[:, 2]

        # 1. Separate foreground points from background wall if target is in foreground
        fg_mask = z_vals < (self.wall_distance_m - 1.0)
        target_z = z_vals[fg_mask] if np.sum(fg_mask) >= 3 else z_vals

        if len(target_z) == 0:
            return float(np.median(z_vals)), float(np.std(z_vals)), len(z_vals)

        # 2. Apply Median Absolute Deviation (MAD) on candidate depth
        med_z = float(np.median(target_z))
        mad = float(np.median(np.abs(target_z - med_z)))
        inlier_mask = np.abs(target_z - med_z) <= max(0.06, 2.5 * mad)
        clean_z = target_z[inlier_mask]

        if len(clean_z) == 0:
            clean_z = target_z

        fused_z = float(np.mean(clean_z))
        std_z = float(np.std(clean_z))
        return round(fused_z, 4), round(std_z, 4), len(clean_z)

    def estimate_physical_diameter(self, bbox_xyxy: List[float], fused_z: float) -> Tuple[float, float]:
        """
        Non-circular physical diameter estimation via pinhole back-projection.
        NEVER derives Z from class priors; calculates metric size directly from fused Z.
        Returns (width_m, height_m).
        """
        x1, y1, x2, y2 = bbox_xyxy
        w_px = max(1.0, x2 - x1)
        h_px = max(1.0, y2 - y1)

        width_m = (w_px * fused_z) / self.fx
        height_m = (h_px * fused_z) / self.fy
        return float(width_m), float(height_m)
