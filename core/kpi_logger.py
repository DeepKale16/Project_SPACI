"""
core/kpi_logger.py - Thread-Safe Capture KPI Logger & SQLite Trial Evaluator
===========================================================================
Persists ground capture trials with explicit fidelity tags:
  - GROUND_TRUTH_SIM vs ESTIMATED_TRACK
Evaluates 3D miss distance, Ferrous/Magnetic Assist margins, and
generates live summary stats and CSV/JSON mission payloads.
"""

import os
import json
import sqlite3
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import numpy as np


class CaptureKpiLogger:
    """
    Thread-safe trial evaluator and SQLite logger for SPACI 3.0.
    Database stored in gitignored path: data/spaci_trials.db
    """

    def __init__(self, db_path: Optional[Path | str] = None):
        if db_path is None:
            project_root = Path(__file__).resolve().parent.parent
            data_dir = project_root / "data"
            data_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = data_dir / "spaci_trials.db"
        else:
            self.db_path = Path(db_path)
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        conn.execute("PRAGMA journal_mode=WAL;")
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS capture_trials (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp_ms INTEGER NOT NULL,
                    mode TEXT NOT NULL,
                    target_class TEXT NOT NULL,
                    fidelity TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    deployment_distance_m REAL NOT NULL,
                    miss_error_cm REAL NOT NULL,
                    net_radius_m REAL NOT NULL,
                    capture_success INTEGER NOT NULL,
                    latency_ms REAL NOT NULL,
                    fps REAL NOT NULL,
                    magnetic_assist INTEGER NOT NULL,
                    tumble_rate REAL NOT NULL,
                    abort_reason TEXT
                );
            """)
            conn.commit()

    def log_trial(
        self,
        target_class: str,
        confidence: float,
        deployment_distance_m: float,
        miss_error_m: float,
        net_radius_m: float,
        latency_ms: float = 12.0,
        fps: float = 30.0,
        fidelity: str = "ESTIMATED_TRACK",
        magnetic_assist: bool = False,
        tumble_rate: float = 0.0,
        abort_reason: Optional[str] = None,
        mode: str = "GROUND_DEMONSTRATOR",
    ) -> Dict[str, Any]:
        """
        Evaluates trial outcome with optional ferrous magnetic assist margin.
        If magnetic_assist is True, capture envelope expands by 15% due to magnetic latching.
        """
        eff_radius_m = net_radius_m * 1.15 if magnetic_assist else net_radius_m
        is_success = int(miss_error_m <= eff_radius_m and abort_reason is None)
        miss_error_cm = round(miss_error_m * 100.0, 2)
        timestamp_ms = int(time.time() * 1000)

        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO capture_trials (
                    timestamp_ms, mode, target_class, fidelity, confidence,
                    deployment_distance_m, miss_error_cm, net_radius_m, capture_success,
                    latency_ms, fps, magnetic_assist, tumble_rate, abort_reason
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                timestamp_ms,
                mode,
                target_class,
                fidelity,
                round(confidence, 4),
                round(deployment_distance_m, 3),
                miss_error_cm,
                round(net_radius_m, 3),
                is_success,
                round(latency_ms, 2),
                round(fps, 1),
                int(magnetic_assist),
                round(tumble_rate, 5),
                abort_reason,
            ))
            conn.commit()

        return {
            "timestamp_ms": timestamp_ms,
            "target_class": target_class,
            "capture_success": bool(is_success),
            "miss_error_cm": miss_error_cm,
            "effective_radius_cm": round(eff_radius_m * 100.0, 2),
            "magnetic_assist": magnetic_assist,
            "fidelity": fidelity,
        }

    def get_summary_kpis(self) -> Dict[str, Any]:
        """Calculates SPACI's 3 core KPIs + performance telemetry."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*), AVG(capture_success), AVG(deployment_distance_m), AVG(miss_error_cm), AVG(confidence), AVG(latency_ms), AVG(fps) FROM capture_trials")
            row = cursor.fetchone()

        if not row or row[0] == 0:
            return {
                "total_trials": 0,
                "capture_success_rate_pct": 0.0,
                "mean_deployment_distance_m": 0.0,
                "mean_miss_error_cm": 0.0,
                "mean_detection_confidence_pct": 0.0,
                "mean_latency_ms": 0.0,
                "mean_fps": 0.0,
            }

        total, succ, dist, miss, conf, lat, fps = row
        return {
            "total_trials": total,
            "capture_success_rate_pct": round(float(succ or 0.0) * 100.0, 1),
            "mean_deployment_distance_m": round(float(dist or 0.0), 2),
            "mean_miss_error_cm": round(float(miss or 0.0), 1),
            "mean_detection_confidence_pct": round(float(conf or 0.0) * 100.0, 1),
            "mean_latency_ms": round(float(lat or 0.0), 2),
            "mean_fps": round(float(fps or 0.0), 1),
        }

    def export_csv(self) -> str:
        headers = ["id,timestamp_ms,mode,target_class,fidelity,confidence,deployment_distance_m,miss_error_cm,net_radius_m,capture_success,latency_ms,fps,magnetic_assist,tumble_rate,abort_reason"]
        rows = []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, timestamp_ms, mode, target_class, fidelity, confidence, deployment_distance_m, miss_error_cm, net_radius_m, capture_success, latency_ms, fps, magnetic_assist, tumble_rate, abort_reason FROM capture_trials ORDER BY id ASC")
            for r in cursor.fetchall():
                row_str = ",".join(str(val) if val is not None else "" for val in r)
                rows.append(row_str)

        return "\n".join(headers + rows)

    def export_json(self) -> List[Dict[str, Any]]:
        results = []
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM capture_trials ORDER BY id ASC")
            for r in cursor.fetchall():
                results.append(dict(r))
        return results
