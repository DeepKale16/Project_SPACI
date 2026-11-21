"""
tests/test_gnc_quartic.py - Unit Tests for Closed-Form Quartic Ballistic GNC
============================================================================
Verifies:
- Quartic residual < 10^-6 m (exact root)
- +Y up gravity compensation (aim point elevates above target)
- ABORT_UNREACHABLE when target is physically unreachable
- Bidirectional 2D <-> 3D projection round-trip accuracy
- 6-condition Go/No-Go gate decisions
"""

import pytest
import numpy as np
from core.tracking_control import QuarticBallisticSolver, TetheredNetSafetyGate, NetCanopyModel
from core.sensor_fusion import SensorFusionEngine


def test_quartic_exact_residual_lateral():
    """Verify quartic solver computes exact intercept with residual < 10^-6 m."""
    solver = QuarticBallisticSolver(g=9.81)
    pos_p0 = (0.5, 0.2, 3.5)
    vel_v = (-0.6, 0.05, -0.2)
    v_net = 9.0
    t_lat = 0.08

    sol = solver.solve_intercept(pos_p0, vel_v, v_net=v_net, t_lat=t_lat)
    assert sol is not None, "Quartic solver should find valid real intercept"
    assert sol["tf_s"] > 0.0
    assert sol["residual_m"] < 1e-6, f"Residual {sol['residual_m']} exceeds 10^-6 m tolerance"


def test_gravity_compensation_aims_upward():
    """Verify +Y up gravity compensation aims strictly above the target."""
    solver = QuarticBallisticSolver(g=9.81)
    pos_p0 = (0.0, 0.0, 4.0)
    vel_v = (0.0, 0.0, 0.0)  # Stationary target

    sol = solver.solve_intercept(pos_p0, vel_v, v_net=9.0, t_lat=0.0)
    assert sol is not None
    # Aim Y must be higher than target Y to compensate for gravity
    y_tgt = sol["pos_target_intercept"][1]
    y_aim = sol["pos_aim_point"][1]
    assert y_aim > y_tgt, f"Aim point Y ({y_aim}) must be elevated above target Y ({y_tgt})"
    assert sol["tilt_deg"] > 0.0, "Gimbal tilt must be positive (aiming up)"


def test_unreachable_target_returns_none():
    """Verify target beyond ballistic reach returns None (ABORT_UNREACHABLE)."""
    solver = QuarticBallisticSolver(g=9.81)
    # Target at 50 meters with 9 m/s net is physically impossible
    pos_p0 = (0.0, 0.0, 50.0)
    vel_v = (0.0, 0.0, 5.0)  # Moving away

    sol = solver.solve_intercept(pos_p0, vel_v, v_net=9.0, t_lat=0.08)
    assert sol is None, "Distant receding target must have no real intercept solution"


def test_2d_3d_bidirectional_roundtrip_projection():
    """Verify 2D pixel -> 3D Launcher Frame -> 2D pixel round-trip matches exactly."""
    fusion = SensorFusionEngine(fx=554.3, fy=554.3, cx=320.0, cy=320.0)
    orig_u, orig_v = 450.0, 180.0
    z_m = 3.25

    # 1. 2D -> 3D
    X, Y, Z = fusion.pixel_to_launcher(orig_u, orig_v, z_m)
    assert Z == z_m
    assert X > 0.0  # u > cx -> +X (right)
    assert Y > 0.0  # v < cy -> +Y (up)

    # 2. 3D -> 2D
    u_proj, v_proj, in_front = fusion.launcher_to_pixel(X, Y, Z)
    assert in_front is True
    assert abs(u_proj - orig_u) < 1e-4, f"Projected u {u_proj} != {orig_u}"
    assert abs(v_proj - orig_v) < 1e-4, f"Projected v {v_proj} != {orig_v}"


def test_safety_gate_all_six_conditions():
    """Verify TetheredNetSafetyGate evaluates all 6 Go/No-Go conditions correctly."""
    gate = TetheredNetSafetyGate(max_net_diameter_m=1.2, v_net_mps=9.0)

    # 1. Optimal conditions -> FIRE_READY
    verdict_ready = gate.evaluate_safety(
        track_id=1,
        pos_xyz=(0.1, 0.1, 3.0),
        vel_xyz=(-0.1, 0.0, -0.1),
        tumble_variance=0.012,
        obj_diam_m=0.40,
        kalman_sigma_pos=0.08,
    )
    assert verdict_ready["state"] == "FIRE_READY"
    assert verdict_ready["fire_cmd"] is True

    # 2. Excessive Tumble -> ABORT_UNSAFE
    verdict_tumble = gate.evaluate_safety(
        track_id=1,
        pos_xyz=(0.1, 0.1, 3.0),
        vel_xyz=(-0.1, 0.0, -0.1),
        tumble_variance=0.085,  # Exceeds 0.045
        obj_diam_m=0.40,
        kalman_sigma_pos=0.08,
    )
    assert verdict_tumble["state"] == "ABORT_UNSAFE"
    assert verdict_tumble["fire_cmd"] is False

    # 3. Oversized Target -> ABORT_UNSAFE
    verdict_oversize = gate.evaluate_safety(
        track_id=1,
        pos_xyz=(0.1, 0.1, 3.0),
        vel_xyz=(-0.1, 0.0, -0.1),
        tumble_variance=0.010,
        obj_diam_m=1.80,  # Exceeds net aperture
        kalman_sigma_pos=0.08,
    )
    assert verdict_oversize["state"] == "ABORT_UNSAFE"

    # 4. Out of range corridor (Z = 7.0m, reachable but outside 1.5-6.5m envelope) -> ABORT_OUT_OF_ENVELOPE
    verdict_range = gate.evaluate_safety(
        track_id=1,
        pos_xyz=(0.0, 0.0, 7.0),
        vel_xyz=(0.0, 0.0, 0.0),
        tumble_variance=0.010,
        obj_diam_m=0.40,
        kalman_sigma_pos=0.08,
    )
    assert verdict_range["state"] == "ABORT_OUT_OF_ENVELOPE"

    # 5. Gimbal pan angle exceeded (+-75 deg limit, Pan=77.3 deg) -> ABORT_OUT_OF_ENVELOPE
    verdict_gimbal = gate.evaluate_safety(
        track_id=1,
        pos_xyz=(8.0, 0.0, 1.8),
        vel_xyz=(0.0, 0.0, 0.0),
        tumble_variance=0.010,
        obj_diam_m=0.40,
        kalman_sigma_pos=0.08,
    )
    assert verdict_gimbal["state"] == "ABORT_OUT_OF_ENVELOPE"

    # 6. Kalman unconverged -> TRACKING
    verdict_kalman = gate.evaluate_safety(
        track_id=1,
        pos_xyz=(0.1, 0.1, 3.0),
        vel_xyz=(-0.1, 0.0, -0.1),
        tumble_variance=0.010,
        obj_diam_m=0.40,
        kalman_sigma_pos=0.35,  # >= 0.15 m
    )
    assert verdict_kalman["state"] == "TRACKING"
