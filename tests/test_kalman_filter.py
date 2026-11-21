"""
tests/test_kalman_filter.py - Unit Tests for Pure-NumPy 3D Kalman & Target Lock Policy
=====================================================================================
Verifies:
- 3D Constant-Velocity Kalman converges position uncertainty < 0.15 m
- Velocity-jump gate triggers on >20 m/s physical discontinuities
- Target Lock Policy deterministically prioritizes debris over satellites
"""

import pytest
import numpy as np
from core.tracking_control import KalmanFilter3D, DeterministicTargetLockPolicy


def test_kalman_filter_convergence():
    """Verify 3D Kalman Filter converges position uncertainty below 0.15m over 10 steps."""
    t0 = 0.0
    kf = KalmanFilter3D(initial_xyz=(0.0, 0.0, 3.0), timestamp_s=t0)
    assert kf.position_uncertainty_m > 0.4, "Initial uncertainty must be high (~0.5m)"

    # True trajectory: moving at (0.2, 0.0, -0.1) m/s
    true_vx, true_vy, true_vz = 0.2, 0.0, -0.1
    for step in range(1, 12):
        t = t0 + step * 0.033
        true_x = 0.0 + true_vx * (step * 0.033)
        true_y = 0.0 + true_vy * (step * 0.033)
        true_z = 3.0 + true_vz * (step * 0.033)

        kf.predict(t)
        # Measure with small noise
        meas = (true_x + float(np.random.normal(0, 0.01)),
                true_y + float(np.random.normal(0, 0.01)),
                true_z + float(np.random.normal(0, 0.02)))
        kf.update(meas)

    # Uncertainty should converge below 0.15 m
    assert kf.position_uncertainty_m < 0.15, f"Uncertainty {kf.position_uncertainty_m} did not converge < 0.15m"


def test_kalman_velocity_jump_gate():
    """Verify sudden physical teleportation (>20 m/s jump) triggers the reset gate."""
    kf = KalmanFilter3D(initial_xyz=(0.0, 0.0, 3.0), timestamp_s=0.0)
    kf.predict(0.033)
    # Jump by 5 meters in 33 ms -> ~150 m/s jump
    kf.update((5.0, 0.0, 3.0))

    # Gate resets velocity to 0 and reinitializes covariance
    assert kf.position_uncertainty_m > 0.4
    assert kf.converged_frames == 1


def test_target_lock_policy_priority():
    """Verify lock policy prioritizes 'debris' over operational satellites."""
    policy = DeterministicTargetLockPolicy(allow_active_sat_fire=False)

    candidates = [
        {"track_id": 10, "class_name": "cheops", "pos_xyz": (0.0, 0.0, 2.0)},      # Closer active sat
        {"track_id": 20, "class_name": "debris", "pos_xyz": (0.2, 0.1, 3.5)},      # Further debris fragment
    ]

    primary = policy.select_primary_target(candidates)
    assert primary is not None
    assert primary["class_name"] == "debris", "Debris must take precedence over active satellite"
    assert primary["track_id"] == 20
