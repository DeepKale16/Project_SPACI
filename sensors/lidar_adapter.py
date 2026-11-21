"""
sensors/lidar_adapter.py - Depth Sensing Abstraction for SPACI 3.0
==================================================================
Abstract DepthProvider interface and implementations:
- SimulatedLidarProvider: True ray-cast LiDAR against 3D ground-truth silhouettes with 8.0m wall clutter
- MonocularProxyProvider: Range estimation proxy for plain video/webcam
- SerialLidarProvider: Non-blocking stub ready for future UART/UDP physical hardware
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Any
import numpy as np


@dataclass
class DepthReading:
    """Standardized depth reading payload."""
    z_m: float
    std_m: float
    num_points: int
    depth_source: str  # 'RAYCAST_LIDAR', 'MONOCULAR_PROXY', 'HARDWARE_LIDAR'
    raw_points_3d: np.ndarray = field(default_factory=lambda: np.zeros((0, 3), dtype=np.float32))


class DepthProvider(ABC):
    """Abstract Base Class for depth sensing (Hardware abstraction)."""

    @abstractmethod
    def get_depth_for_box(
        self,
        bbox_xyxy: List[float],
        frame_shape: Tuple[int, int] = (640, 640),
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> DepthReading:
        """Computes depth reading for a detected 2D bounding box."""
        pass


class SimulatedLidarProvider(DepthProvider):
    """
    True multi-object 3D Ray-Casting LiDAR Simulator.
    Casts 25-40 rays uniformly across the 2D bounding box against ground-truth 3D silhouettes.
    Rays that hit an object return true object Z + N(0, 0.02^2) m noise (5% dropout).
    Rays that miss (box corners, background, false positives) hit the lab wall at 8.0 m.
    """

    def __init__(self, num_rays: int = 36, wall_distance_m: float = 8.0, noise_std_m: float = 0.02, dropout_rate: float = 0.05):
        self.num_rays = num_rays
        self.wall_distance_m = wall_distance_m
        self.noise_std_m = noise_std_m
        self.dropout_rate = dropout_rate

    def get_depth_for_box(
        self,
        bbox_xyxy: List[float],
        frame_shape: Tuple[int, int] = (640, 640),
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> DepthReading:
        x1, y1, x2, y2 = bbox_xyxy
        w = max(1.0, x2 - x1)
        h = max(1.0, y2 - y1)

        gt_targets = (extra_context or {}).get("gt_targets", [])
        fx = (extra_context or {}).get("fx", 554.3)
        fy = (extra_context or {}).get("fy", 554.3)
        cx = (extra_context or {}).get("cx", frame_shape[1] / 2.0)
        cy = (extra_context or {}).get("cy", frame_shape[0] / 2.0)

        grid_n = int(np.ceil(np.sqrt(self.num_rays)))
        xs = np.linspace(x1 + 0.1 * w, x2 - 0.1 * w, grid_n)
        ys = np.linspace(y1 + 0.1 * h, y2 - 0.1 * h, grid_n)

        pts_3d = []
        for qy in ys:
            for qx in xs:
                if np.random.rand() < self.dropout_rate:
                    continue  # sensor dropout

                hit_z = None
                # Check intersection against 3D ground-truth silhouettes
                for tgt in gt_targets:
                    t_x1, t_y1, t_x2, t_y2 = tgt.get("bbox_2d", [0, 0, 0, 0])
                    if t_x1 <= qx <= t_x2 and t_y1 <= qy <= t_y2:
                        true_z = tgt.get("z_m", 3.0)
                        hit_z = true_z + float(np.random.normal(0.0, self.noise_std_m))
                        break

                if hit_z is None:
                    # Ray missed foreground target -> hits background wall
                    hit_z = self.wall_distance_m + float(np.random.normal(0.0, 0.05))

                ray_x = (qx - cx) * hit_z / fx
                ray_y = -(qy - cy) * hit_z / fy
                pts_3d.append([ray_x, ray_y, hit_z])

        if not pts_3d:
            pts_3d = [[0.0, 0.0, self.wall_distance_m]]

        pts_arr = np.array(pts_3d, dtype=np.float32)
        raw_z = pts_arr[:, 2]

        return DepthReading(
            z_m=float(np.median(raw_z)),
            std_m=float(np.std(raw_z)),
            num_points=len(pts_arr),
            depth_source="RAYCAST_LIDAR",
            raw_points_3d=pts_arr,
        )


class MonocularProxyProvider(DepthProvider):
    """
    Monocular Relative Range Proxy for regular uploaded videos or webcams without LiDAR.
    Explicitly tags depth_source='MONOCULAR_PROXY' to avoid circular size-depth assumptions.
    """

    def __init__(self, ref_distance_m: float = 3.5):
        self.ref_distance_m = ref_distance_m

    def get_depth_for_box(
        self,
        bbox_xyxy: List[float],
        frame_shape: Tuple[int, int] = (640, 640),
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> DepthReading:
        x1, y1, x2, y2 = bbox_xyxy
        w = max(1.0, x2 - x1)
        h = max(1.0, y2 - y1)
        area_ratio = (w * h) / (frame_shape[0] * frame_shape[1])

        # Monocular geometric proxy based on apparent angular size
        est_z = self.ref_distance_m * (0.15 / np.sqrt(max(0.001, area_ratio)))
        est_z = float(np.clip(est_z, 0.5, 12.0))

        return DepthReading(
            z_m=round(est_z, 3),
            std_m=0.35,
            num_points=1,
            depth_source="MONOCULAR_PROXY",
            raw_points_3d=np.array([[0.0, 0.0, est_z]], dtype=np.float32),
        )


class SerialLidarProvider(DepthProvider):
    """
    Hardware-Ready non-blocking UART/UDP serial adapter.
    Operates safely in software mode if no physical serial port is attached.
    """

    def __init__(self, port: str = "COM3", baud: int = 115200):
        self.port = port
        self.baud = baud
        self.connected = False

    def get_depth_for_box(
        self,
        bbox_xyxy: List[float],
        frame_shape: Tuple[int, int] = (640, 640),
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> DepthReading:
        # Fallback to software monocular proxy when physical LiDAR is not plugged in
        proxy = MonocularProxyProvider()
        res = proxy.get_depth_for_box(bbox_xyxy, frame_shape, extra_context)
        res.depth_source = "SERIAL_LIDAR_MOCK"
        return res
