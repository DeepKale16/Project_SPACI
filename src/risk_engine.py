"""
risk_engine.py - SPACI 2.0 NASA/ESA Calibrated Orbital Risk Assessment Matrix
=============================================================================
Calculates normalized multi-factor collision hazard scores (0.0 to 1.0) and
maps detections into exactly 4 Operational Classification States:
  1. Hazardous
  2. Reusable / Salvageable
  3. Useful / Active
  4. Inert Fragment
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
import numpy as np

from src.config import (
    STATE_HAZARDOUS,
    STATE_REUSABLE,
    STATE_ACTIVE,
    STATE_FRAGMENT,
    ACTIVE_SATELLITE_CLASSES,
    INTACT_OBJECT_CLASSES,
    RiskConfig,
)
from src.taxonomy import get_category_for_class


@dataclass
class RiskBreakdown:
    total_score: float
    operational_state: str
    size_risk: float
    threat_risk: float
    tumble_risk: float
    confidence_penalty: float
    telemetry_adjustment: float
    details: Dict[str, Any]


class RiskEngine:
    """
    Computes rigorous orbital risk metrics grounded in NASA-STD-8719.14C,
    IADC-02-01, and ESA MASTER-8 specifications.
    """

    def __init__(self, config: Optional[RiskConfig] = None):
        self.cfg = config or RiskConfig()

    def compute(
        self,
        class_name: str,
        area_ratio: float,
        confidence: float,
        tumble_rate: float = 0.0,
        is_video: bool = False,
        speed_mps: Optional[float] = None,
        altitude_km: Optional[float] = None,
        object_count: int = 1,
    ) -> RiskBreakdown:
        """
        Calculates multi-factor risk score and operational state.

        Args:
            class_name: Raw YOLO class name.
            area_ratio: Normalized bbox area (w * h / frame_area).
            confidence: Model prediction confidence (0.0 - 1.0).
            tumble_rate: Aspect ratio variance over time (for video tracks).
            is_video: Boolean flag indicating if temporal tracking is available.
            speed_mps: Relative velocity in m/s (optional telemetry).
            altitude_km: Orbital altitude in km (optional telemetry).
            object_count: Number of co-detected objects in FOV.

        Returns:
            RiskBreakdown object with score, operational state, and factor breakdown.
        """
        clean_cls = class_name.lower().strip()
        cat_profile = get_category_for_class(clean_cls)

        # 1. Optical Size Proxy S(r_A)
        # Scaled so that objects occupying >= 6.5% of sensor FOV saturate at 1.0
        size_risk = float(np.clip(np.sqrt(max(0.0, area_ratio)) * self.cfg.k_size, 0.0, 1.0))

        # 2. Inherent Taxonomy Base Threat Prior
        base_threat = cat_profile.default_base_threat

        # 3. Epistemic Uncertainty Margin
        conf_clamped = float(np.clip(confidence, 0.1, 1.0))
        conf_penalty = float(1.0 - conf_clamped * 0.25)

        # 4. Rotational Dynamics / Tumble Hazard
        tumble_hazard = float(np.clip(tumble_rate * self.cfg.tumble_k, 0.0, 1.0)) if is_video else 0.0

        # Weighted combination
        if is_video:
            # Video: Size (35%), Tumble (35%), Threat (20%), Confidence (10%)
            raw_score = (
                0.35 * size_risk +
                0.35 * tumble_hazard +
                0.20 * base_threat +
                0.10 * conf_penalty
            )
        else:
            # Single Frame: Size (55%), Base Threat (30%), Confidence (15%)
            raw_score = (
                0.55 * size_risk +
                0.30 * base_threat +
                0.15 * conf_penalty
            )

        # Field-of-view density penalty (crowding)
        if object_count > 3:
            density_boost = min(0.12, (object_count - 3) * 0.02)
            raw_score = min(1.0, raw_score + density_boost)

        # 5. Telemetry adjustments
        telemetry_adj = 0.0
        if speed_mps is not None:
            # Hypervelocity scaling up to 8,000 m/s (~LEO orbital speed)
            speed_norm = min(1.0, max(0.0, speed_mps / 8000.0))
            raw_score = 0.85 * raw_score + 0.15 * speed_norm
            telemetry_adj += 0.15 * speed_norm

        if altitude_km is not None:
            # Crowded orbital regimes (LEO 400-900 km per ESA MASTER-8)
            if 400.0 <= altitude_km <= 900.0:
                raw_score = min(1.0, raw_score + 0.06)
                telemetry_adj += 0.06

        final_score = round(float(np.clip(raw_score, 0.0, 1.0)), 4)

        # Operational State Assignment
        is_active = clean_cls in ACTIVE_SATELLITE_CLASSES
        is_intact = clean_cls in INTACT_OBJECT_CLASSES

        if final_score > self.cfg.hazardous_threshold:
            operational_state = STATE_HAZARDOUS
        elif is_active and final_score <= self.cfg.hazardous_threshold:
            operational_state = STATE_ACTIVE
        elif is_intact and final_score < self.cfg.reusable_max_risk:
            operational_state = STATE_REUSABLE
        else:
            operational_state = STATE_FRAGMENT

        return RiskBreakdown(
            total_score=final_score,
            operational_state=operational_state,
            size_risk=round(size_risk, 4),
            threat_risk=round(base_threat, 4),
            tumble_risk=round(tumble_hazard, 4),
            confidence_penalty=round(conf_penalty, 4),
            telemetry_adjustment=round(telemetry_adj, 4),
            details={
                "class_name": clean_cls,
                "category": cat_profile.name,
                "area_ratio": round(area_ratio, 6),
                "confidence": round(confidence, 4),
                "is_active_satellite": is_active,
                "is_intact_structure": is_intact,
            },
        )
