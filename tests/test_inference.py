"""
test_inference.py - Unit Test for End-to-End Image Detection and Risk Calculation
"""

import unittest
from pathlib import Path
import cv2

from src.config import DATASET_DIR, MODELS_DIR
from src.detector import SpaceDebrisDetector


class TestEndToEndInference(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.detector = SpaceDebrisDetector(
            weights_path=MODELS_DIR / "yolo11n.pt",
            conf_threshold=0.05,
            device="0",
        )

    def test_inference_on_sample_image(self):
        test_img_dir = DATASET_DIR / "test" / "images"
        first_img = next(test_img_dir.glob("*.jpg"))
        bgr = cv2.imread(str(first_img))

        self.assertIsNotNone(bgr, f"Failed to load image: {first_img}")
        annotated, detections, summary = self.detector.predict_image(bgr)

        self.assertEqual(annotated.shape, bgr.shape)
        self.assertIn("total_objects", summary)
        self.assertIn("mean_risk", summary)
        self.assertIn("state_counts", summary)


if __name__ == "__main__":
    unittest.main()
