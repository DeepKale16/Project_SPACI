"""
tests/test_testbench.py - Unit Tests for Standalone 3D Physics Testbench
========================================================================
Verifies:
- 3D Physics Testbench generates 640x640 3-channel optical frames
- Targets move and maintain realistic depths within bounds
- 3D tumbling produces dynamic aspect-ratio variance
"""

import pytest
import numpy as np
from simulation.physics_testbench import PhysicsTestbench


def test_testbench_frame_generation():
    """Verify testbench produces 640x640 BGR frames and structured ground-truth targets."""
    bench = PhysicsTestbench(width=640, height=640, num_targets=2)
    frame, gt_targets = bench.step(0.033)

    assert frame.shape == (640, 640, 3)
    assert len(gt_targets) >= 1
    t0 = gt_targets[0]
    assert "pos_xyz" in t0
    assert "bbox_2d" in t0
    assert 1.5 <= t0["z_m"] <= 6.5


def test_testbench_tumbling_aspect_ratio_fluctuation():
    """Verify in-plane rotation + foreshortening causes aspect ratio to vary over time."""
    bench = PhysicsTestbench(num_targets=1)
    aspect_ratios = []

    for _ in range(25):
        _, gt_targets = bench.step(0.04)
        if gt_targets:
            b = gt_targets[0]["bbox_2d"]
            w = max(1.0, b[2] - b[0])
            h = max(1.0, b[3] - b[1])
            aspect_ratios.append(w / h)

    # Standard deviation of aspect ratios should be > 0.05 due to simulated 3D tumbling
    assert np.std(aspect_ratios) > 0.05, f"Tumble variance too low: {np.std(aspect_ratios)}"
