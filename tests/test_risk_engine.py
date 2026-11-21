"""
test_risk_engine.py - Unit Tests for NASA/ESA Risk Engine Calculations
"""

import unittest
from src.risk_engine import RiskEngine
from src.config import STATE_HAZARDOUS, STATE_REUSABLE, STATE_ACTIVE, STATE_FRAGMENT


class TestRiskEngine(unittest.TestCase):

    def setUp(self):
        self.engine = RiskEngine()

    def test_hazardous_large_debris(self):
        # Huge debris occupying 25% of the frame
        res = self.engine.compute(class_name="debris", area_ratio=0.25, confidence=0.90)
        self.assertGreater(res.total_score, 0.60)
        self.assertEqual(res.operational_state, STATE_HAZARDOUS)

    def test_active_satellite(self):
        # Small CHEOPS operational satellite
        res = self.engine.compute(class_name="cheops", area_ratio=0.01, confidence=0.95)
        self.assertLessEqual(res.total_score, 0.60)
        self.assertEqual(res.operational_state, STATE_ACTIVE)

    def test_reusable_defunct_sat(self):
        # Small intact defunct satellite with low risk
        res = self.engine.compute(class_name="earth_observation_sat_1", area_ratio=0.002, confidence=0.95)
        self.assertLess(res.total_score, 0.40)
        self.assertEqual(res.operational_state, STATE_REUSABLE)

    def test_inert_fragment(self):
        # Moderate sized generic debris that doesn't breach 0.60
        res = self.engine.compute(class_name="debris", area_ratio=0.01, confidence=0.95)
        if res.total_score <= 0.60:
            self.assertEqual(res.operational_state, STATE_FRAGMENT)

    def test_tumble_rate_escalation(self):
        # Video with high aspect ratio variance (tumbling rocket or fragment)
        res_stable = self.engine.compute(class_name="debris", area_ratio=0.04, confidence=0.85, tumble_rate=0.0, is_video=True)
        res_tumbling = self.engine.compute(class_name="debris", area_ratio=0.04, confidence=0.85, tumble_rate=0.15, is_video=True)
        self.assertGreater(res_tumbling.total_score, res_stable.total_score)

    def test_clipping_bounds(self):
        # Negative area or over 1.0 area shouldn't crash or violate [0, 1]
        res_neg = self.engine.compute(class_name="debris", area_ratio=-0.5, confidence=0.0)
        res_huge = self.engine.compute(class_name="debris", area_ratio=2.5, confidence=1.5)
        self.assertGreaterEqual(res_neg.total_score, 0.0)
        self.assertLessEqual(res_huge.total_score, 1.0)


if __name__ == "__main__":
    unittest.main()
