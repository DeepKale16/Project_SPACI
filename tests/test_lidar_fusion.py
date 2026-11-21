"""
tests/test_lidar_fusion.py - Unit Tests for Ray-Cast LiDAR & MAD/IQR Outlier Rejection
======================================================================================
Verifies:
- Ray-cast LiDAR produces multi-point point clouds
- MAD/IQR outlier rejection discards 8.0 m wall clutter
- Non-circular physical diameter estimation matches metric ground truth
"""

import pytest
import numpy as np
from sensors.lidar_adapter import SimulatedLidarProvider
from core.sensor_fusion import SensorFusionEngine


def test_raycast_lidar_wall_clutter_rejection():
    """Verify MAD/IQR filter successfully separates 3.0 m target from 8.0 m wall clutter."""
    fusion = SensorFusionEngine(wall_distance_m=8.0)

    # Synthetic ray cluster: 25 rays hit target at 3.0m, 11 rays hit wall at 8.0m
    target_pts = np.random.normal(3.0, 0.02, 25)
    wall_pts = np.random.normal(8.0, 0.04, 11)
    all_z = np.concatenate([target_pts, wall_pts])
    points_3d = np.zeros((len(all_z), 3), dtype=np.float32)
    points_3d[:, 2] = all_z

    fused_z, std_z, num_inliers = fusion.filter_lidar_outliers(points_3d)

    # Fused Z should be close to 3.0m, NOT influenced by 8.0m wall
    assert abs(fused_z - 3.0) < 0.10, f"Fused Z {fused_z} affected by wall clutter"
    assert num_inliers >= 20, f"Expected >=20 inliers, got {num_inliers}"


def test_simulated_lidar_adapter():
    """Verify SimulatedLidarProvider queries ground-truth silhouettes."""
    lidar = SimulatedLidarProvider(num_rays=36, wall_distance_m=8.0)
    bbox = [280, 280, 360, 360]
    gt_targets = [{
        "bbox_2d": [270, 270, 370, 370],
        "z_m": 2.85,
    }]

    reading = lidar.get_depth_for_box(bbox, extra_context={"gt_targets": gt_targets})
    assert reading.depth_source == "RAYCAST_LIDAR"
    assert reading.num_points > 20
    assert abs(reading.z_m - 2.85) < 0.15, f"Reading Z {reading.z_m} differs from GT 2.85m"


def test_physical_diameter_estimation():
    """Verify pinhole back-projection correctly calculates metric diameter."""
    fusion = SensorFusionEngine(fx=554.3, fy=554.3)
    # Target of 0.60 m at 3.0 m should project to w_px = (0.60 * 554.3) / 3.0 = 110.86 px
    w_px = 110.86
    h_px = 90.0
    bbox = [100.0, 100.0, 100.0 + w_px, 100.0 + h_px]
    fused_z = 3.0

    w_m, h_m = fusion.estimate_physical_diameter(bbox, fused_z)
    assert abs(w_m - 0.60) < 0.01, f"Estimated width {w_m} != 0.60 m"
