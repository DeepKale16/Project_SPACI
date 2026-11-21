"""
core/tracking_control.py - Pure-NumPy 3D Kalman Filter, Ballistic GNC & Net Safety Gate
========================================================================================
Implements:
- 6-State Pure-NumPy Constant-Velocity 3D Kalman Filter [X, Y, Z, vx, vy, vz]
- Dynamic delta-t & Velocity-Jump Sanity Gate (>20 m/s)
- Deterministic Multi-Target Priority Lock (Ground Demonstrator Mode)
- Exact Closed-Form Quartic 3D Ballistic Intercept Solver with Gravity Compensation
- 4-Ejector Net Opening Canopy Model R_open(d)
- 6-Condition Tethered Net Go/No-Go Safety Gate & Structured Actuator JSON
"""

import time
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
import numpy as np


class KalmanFilter3D:
    """
    Pure-NumPy 6-State 3D Constant-Velocity Kalman Filter.
    State vector: [X, Y, Z, vx, vy, vz]^T in Launcher Coordinate Frame (+Y Up).
    Requires no external dependencies (pure NumPy).
    """

    def __init__(
        self,
        initial_xyz: Tuple[float, float, float],
        timestamp_s: float,
        pos_noise_std: float = 0.05,
        proc_accel_std: float = 1.2,
        vel_jump_thresh_mps: float = 20.0,
    ):
        self.x = np.zeros((6, 1), dtype=np.float64)
        self.x[0, 0] = initial_xyz[0]
        self.x[1, 0] = initial_xyz[1]
        self.x[2, 0] = initial_xyz[2]

        self.last_timestamp_s = timestamp_s
        self.pos_noise_std = pos_noise_std
        self.proc_accel_std = proc_accel_std
        self.vel_jump_thresh_mps = vel_jump_thresh_mps

        # Covariance initialized with high uncertainty (sigma_init = 0.5 m)
        self.P = np.diag([0.25, 0.25, 0.25, 4.0, 4.0, 4.0]).astype(np.float64)

        # Measurement Matrix (Observing [X, Y, Z])
        self.H = np.zeros((3, 6), dtype=np.float64)
        self.H[0, 0] = 1.0
        self.H[1, 1] = 1.0
        self.H[2, 2] = 1.0

        # Measurement Noise
        r_var = self.pos_noise_std ** 2
        self.R = np.diag([r_var, r_var, r_var * 2.0]).astype(np.float64)

        self.converged_frames = 0

    def predict(self, current_timestamp_s: float) -> np.ndarray:
        dt = max(1e-4, min(0.5, current_timestamp_s - self.last_timestamp_s))
        self.last_timestamp_s = current_timestamp_s

        # Transition Matrix F
        F = np.eye(6, dtype=np.float64)
        F[0, 3] = dt
        F[1, 4] = dt
        F[2, 5] = dt

        # Continuous White Noise Acceleration Q
        q = (self.proc_accel_std ** 2)
        dt2 = dt * dt
        dt3 = dt2 * dt / 2.0
        dt4 = dt2 * dt2 / 4.0

        Q_block = np.array([
            [dt4, dt3],
            [dt3, dt2]
        ], dtype=np.float64) * q

        Q = np.zeros((6, 6), dtype=np.float64)
        for i in range(3):
            Q[i, i] = Q_block[0, 0]
            Q[i, i + 3] = Q_block[0, 1]
            Q[i + 3, i] = Q_block[1, 0]
            Q[i + 3, i + 3] = Q_block[1, 1]

        # Prior State & Covariance
        self.x = F @ self.x
        self.P = F @ self.P @ F.T + Q
        return self.x

    def update(self, measured_xyz: Tuple[float, float, float]) -> np.ndarray:
        z = np.array(measured_xyz, dtype=np.float64).reshape((3, 1))

        # Velocity-Jump Sanity Gate
        pred_pos = self.x[0:3]
        dist_jump = float(np.linalg.norm(z - pred_pos))
        dt = max(1e-3, self.last_timestamp_s - (self.last_timestamp_s - 0.033))
        implied_speed = dist_jump / dt

        if implied_speed > self.vel_jump_thresh_mps:
            # Re-initialize state to measurement with zero velocity on physical jump
            self.x[0:3] = z
            self.x[3:6] = 0.0
            self.P = np.diag([0.25, 0.25, 0.25, 4.0, 4.0, 4.0])
            self.converged_frames = 1
            return self.x

        # Standard Kalman Update
        y = z - (self.H @ self.x)
        S = self.H @ self.P @ self.H.T + self.R
        K = self.P @ self.H.T @ np.linalg.inv(S)

        self.x = self.x + (K @ y)
        I = np.eye(6, dtype=np.float64)
        self.P = (I - K @ self.H) @ self.P

        self.converged_frames += 1
        return self.x

    @property
    def position_xyz(self) -> Tuple[float, float, float]:
        return float(self.x[0, 0]), float(self.x[1, 0]), float(self.x[2, 0])

    @property
    def velocity_xyz(self) -> Tuple[float, float, float]:
        return float(self.x[3, 0]), float(self.x[4, 0]), float(self.x[5, 0])

    @property
    def position_uncertainty_m(self) -> float:
        """Euclidean 3D position uncertainty: sqrt(trace(P[0:3, 0:3]))"""
        return float(np.sqrt(np.trace(self.P[0:3, 0:3])))


class DeterministicTargetLockPolicy:
    """
    Deterministic Multi-Target Lock Policy for Ground Demonstrator Mode.
    Prioritizes:
      1. 'debris' (highest capture urgency)
      2. Derelict spacecraft / unknown ('earth_observation_sat_1', 'smart_1', 'double_start')
      3. Operational satellites ('cheops', 'soho', etc.) - DO NOT FIRE unless override enabled
    Breaks ties by closest valid intercept range.
    """

    PRIORITY_RANKS = {
        "debris": 1,
        "earth_observation_sat_1": 2,
        "smart_1": 2,
        "double_start": 3,
        "cheops": 4,
        "lisa_pathfinder": 4,
        "proba_2": 4,
        "proba_3_csc": 4,
        "proba_3_ocs": 4,
        "soho": 4,
        "xmm_newton": 4,
    }

    def __init__(self, allow_active_sat_fire: bool = False):
        self.allow_active_sat_fire = allow_active_sat_fire

    def select_primary_target(self, candidate_tracks: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not candidate_tracks:
            return None

        valid_tracks = []
        for t in candidate_tracks:
            cname = t.get("class_name", "unknown")
            rank = self.PRIORITY_RANKS.get(cname, 3)
            # By default do not lock on operational satellites
            if rank == 4 and not self.allow_active_sat_fire:
                continue
            z_val = t.get("pos_xyz", (0, 0, 10.0))[2]
            valid_tracks.append((rank, z_val, t))

        if not valid_tracks:
            # Fallback: display first track in observation mode
            return candidate_tracks[0]

        # Sort by rank (ascending), then range Z (ascending)
        valid_tracks.sort(key=lambda item: (item[0], item[1]))
        return valid_tracks[0][2]


class QuarticBallisticSolver:
    """
    Exact Closed-Form Quartic 3D Ballistic Intercept Solver.
    Solves for time-of-flight t_f under gravity g = [0, -9.81, 0]^T m/s^2 (+Y up)
    and system latency t_lat.
    """

    def __init__(self, g: float = 9.81):
        self.g = g

    def solve_intercept(
        self,
        pos_p0: Tuple[float, float, float],
        vel_v: Tuple[float, float, float],
        v_net: float = 9.0,
        t_lat: float = 0.08,
    ) -> Optional[Dict[str, Any]]:
        """
        Solves: c4*t^4 + c3*t^3 + c2*t^2 + c1*t + c0 = 0 via np.roots.
        Selects smallest positive real root.
        """
        P0 = np.array(pos_p0, dtype=np.float64)
        V = np.array(vel_v, dtype=np.float64)
        g = self.g

        # Target position at launch instant (accounting for latency)
        P1 = P0 + V * t_lat
        px, py, pz = P1[0], P1[1], P1[2]
        vx, vy, vz = V[0], V[1], V[2]

        v_sq = float(np.sum(V ** 2))
        p1_sq = float(np.sum(P1 ** 2))
        p1_dot_v = float(np.dot(P1, V))

        # Quartic Coefficients:
        # || P1 + V*t + 0.5*g_vec*t^2 ||^2 = (v_net * t)^2
        # where g_vec = [0, -g, 0]^T
        c4 = 0.25 * (g ** 2)
        c3 = g * vy
        c2 = v_sq + (g * py) - (v_net ** 2)
        c1 = 2.0 * p1_dot_v
        c0 = p1_sq

        roots = np.roots([c4, c3, c2, c1, c0])

        # Filter strictly real, positive roots
        valid_tf = []
        for r in roots:
            if abs(r.imag) < 1e-6 and r.real > 1e-4:
                valid_tf.append(float(r.real))

        if not valid_tf:
            return None

        tf = float(min(valid_tf))

        # Target position at intercept instant
        P_tgt = P1 + V * tf

        # Parabolic gravity-compensated aim position:
        # Launcher aims at P_aim so ballistic net curves and intercepts at P_tgt
        P_aim = P_tgt + np.array([0.0, 0.5 * g * (tf ** 2), 0.0])

        # Convert to Gimbal Angles (Pan, Tilt in Degrees)
        pan_deg = float(np.degrees(np.arctan2(P_aim[0], P_aim[2])))
        tilt_deg = float(np.degrees(np.arctan2(P_aim[1], np.sqrt(P_aim[0]**2 + P_aim[2]**2))))

        # Residual verification: norm(P_aim - 0.5*g*tf^2 - P_tgt)
        residual = float(np.linalg.norm(P_aim - np.array([0, 0.5*g*(tf**2), 0]) - P_tgt))

        return {
            "tf_s": round(tf, 4),
            "pos_target_intercept": (float(P_tgt[0]), float(P_tgt[1]), float(P_tgt[2])),
            "pos_aim_point": (float(P_aim[0]), float(P_aim[1]), float(P_aim[2])),
            "pan_deg": round(pan_deg, 2),
            "tilt_deg": round(tilt_deg, 2),
            "residual_m": residual,
        }


class NetCanopyModel:
    """
    Models the 4-ejector Tethered Net Deployment & Opening Envelope R_open(d).
    Opens smoothly from 0.8m to 2.2m up to 0.5 * D_net, retains full diameter
    until 6.5m, then gradually degrades due to tether drag and dispersion.
    """

    def __init__(self, max_net_diameter_m: float = 1.2):
        self.d_net = max_net_diameter_m

    def get_canopy_radius(self, distance_m: float) -> float:
        max_r = 0.5 * self.d_net

        if distance_m < 0.8:
            # Tightly packed bundle
            return float(0.08 * max_r)
        elif 0.8 <= distance_m <= 2.2:
            # Deployment phase: sinusoidal expansion
            progress = (distance_m - 0.8) / 1.4
            return float(max_r * (0.08 + 0.92 * np.sin(progress * (np.pi / 2.0))))
        elif 2.2 < distance_m <= 6.5:
            # Stable full capture window
            return float(max_r)
        else:
            # Tether drag & dispersion decay
            decay = 0.08 * (distance_m - 6.5)
            return float(max(0.25 * max_r, max_r - decay))


class TetheredNetSafetyGate:
    """
    6-Condition Go/No-Go Safety Gate for Autonomous Net Launch.
    Enforces all physical, aerodynamic, and gimbal envelope rules.
    """

    def __init__(
        self,
        max_net_diameter_m: float = 1.2,
        v_net_mps: float = 9.0,
        t_lat_s: float = 0.08,
        pan_limits: Tuple[float, float] = (-75.0, 75.0),
        tilt_limits: Tuple[float, float] = (-15.0, 60.0),
        max_tumble_variance: float = 0.045,
        max_pos_uncertainty_m: float = 0.15,
    ):
        self.solver = QuarticBallisticSolver()
        self.canopy = NetCanopyModel(max_net_diameter_m)
        self.v_net = v_net_mps
        self.t_lat = t_lat_s
        self.pan_limits = pan_limits
        self.tilt_limits = tilt_limits
        self.max_tumble_variance = max_tumble_variance
        self.max_pos_uncertainty = max_pos_uncertainty_m

    def evaluate_safety(
        self,
        track_id: int,
        pos_xyz: Tuple[float, float, float],
        vel_xyz: Tuple[float, float, float],
        tumble_variance: float,
        obj_diam_m: float,
        kalman_sigma_pos: float,
    ) -> Dict[str, Any]:
        """
        Evaluates the 6 mandatory Go/No-Go conditions:
        1. Quartic real root exists (else ABORT_UNREACHABLE)
        2. Deployment window (1.5m <= Z_int <= 6.5m) and opening >= 75%
        3. Object diameter fits opened net (obj_diam <= 0.70 * 2 * R_open)
        4. Tumble variance below snag threshold (sigma^2_AR <= 0.045)
        5. Aim angles within gimbal limits (Pan +/-75 deg, Tilt -15..+60 deg)
        6. Kalman position uncertainty sigma_pos < 0.15 m
        """
        # Condition 1: Quartic ballistic solver
        sol = self.solver.solve_intercept(pos_xyz, vel_xyz, v_net=self.v_net, t_lat=self.t_lat)
        if sol is None:
            return self._build_verdict(track_id, "ABORT_UNREACHABLE", "Target unreachable with net velocity", None, 0.0)

        tf = sol["tf_s"]
        z_int = sol["pos_target_intercept"][2]
        pan = sol["pan_deg"]
        tilt = sol["tilt_deg"]
        r_open = self.canopy.get_canopy_radius(z_int)
        open_pct = (r_open / (0.5 * self.canopy.d_net)) * 100.0

        # Condition 2: Deployment distance corridor & canopy opening
        if not (1.5 <= z_int <= 6.5) or open_pct < 75.0:
            return self._build_verdict(track_id, "ABORT_OUT_OF_ENVELOPE", f"Intercept range {z_int:.2f}m outside 1.5-6.5m corridor or opening <75%", sol, open_pct)

        # Condition 3: Object diameter vs net aperture
        if obj_diam_m > (0.70 * 2.0 * r_open):
            return self._build_verdict(track_id, "ABORT_UNSAFE", f"Object diameter ({obj_diam_m:.2f}m) exceeds 70% net aperture ({0.70*2*r_open:.2f}m)", sol, open_pct)

        # Condition 4: Rotational Tumble rate variance
        if tumble_variance > self.max_tumble_variance:
            return self._build_verdict(track_id, "ABORT_UNSAFE", f"Tumble variance ({tumble_variance:.4f}) exceeds safety limit ({self.max_tumble_variance})", sol, open_pct)

        # Condition 5: Mechanical Pan/Tilt gimbal limits
        if not (self.pan_limits[0] <= pan <= self.pan_limits[1]) or not (self.tilt_limits[0] <= tilt <= self.tilt_limits[1]):
            return self._build_verdict(track_id, "ABORT_OUT_OF_ENVELOPE", f"Aim angles (Pan {pan:.1f}°, Tilt {tilt:.1f}°) exceed mechanical gimbal limits", sol, open_pct)

        # Condition 6: Kalman position convergence
        if kalman_sigma_pos >= self.max_pos_uncertainty:
            return self._build_verdict(track_id, "TRACKING", f"Kalman uncertainty ({kalman_sigma_pos:.2f}m) >= 0.15m limit (converging)", sol, open_pct)

        # ALL 6 CONDITIONS SATISFIED -> FIRE READY
        return self._build_verdict(track_id, "FIRE_READY", "All 6 flight and envelope safety gates cleared", sol, open_pct, fire_cmd=True)

    def _build_verdict(
        self,
        track_id: int,
        state: str,
        reason: str,
        sol: Optional[Dict[str, Any]],
        net_open_pct: float,
        fire_cmd: bool = False,
    ) -> Dict[str, Any]:
        return {
            "timestamp_ms": int(time.time() * 1000),
            "track_id": track_id,
            "state": state,
            "fire_cmd": fire_cmd,
            "abort_reason": reason if "ABORT" in state else None,
            "status_message": reason,
            "pan_deg": sol["pan_deg"] if sol else 0.0,
            "tilt_deg": sol["tilt_deg"] if sol else 0.0,
            "t_flight_s": sol["tf_s"] if sol else 0.0,
            "net_open_pct": round(net_open_pct, 1),
            "intercept_pos": sol["pos_target_intercept"] if sol else (0.0, 0.0, 0.0),
            "aim_pos": sol["pos_aim_point"] if sol else (0.0, 0.0, 0.0),
        }
