"""
test_detector.py - Unit Tests for SpaceDebrisDetector & Pipeline Integration
"""

import unittest
import numpy as np
from src.detector import SpaceDebrisDetector
from src.config import MODELS_DIR


class TestDetector(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Initialize detector
        cls.detector = SpaceDebrisDetector(
            weights_path=MODELS_DIR / "yolo11n.pt",
            conf_threshold=0.1,
            device="0",
        )

    def test_detector_initialization(self):
        self.assertIsNotNone(self.detector.model)
        self.assertIsNotNone(self.detector.risk_engine)

    def test_dummy_image_inference(self):
        # 640x640 blank image
        dummy_frame = np.zeros((640, 640, 3), dtype=np.uint8)
        annotated, detections, summary = self.detector.predict_image(dummy_frame)

        self.assertEqual(annotated.shape, (640, 640, 3))
        self.assertIsInstance(detections, list)
        self.assertIn("total_objects", summary)
        self.assertIn("hazardous_count", summary)


if __name__ == "__main__":
    unittest.main()
