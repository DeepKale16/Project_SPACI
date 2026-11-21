"""
test_dataset.py - Unit Tests for Dataset Integrity & Configuration
"""

import unittest
from pathlib import Path
import yaml
from PIL import Image

from src.config import DATASET_DIR, DATA_YAML_PATH, CLASS_NAMES


class TestDataset(unittest.TestCase):

    def test_dataset_dir_exists(self):
        self.assertTrue(DATASET_DIR.exists(), "Dataset directory does not exist")

    def test_yaml_config(self):
        self.assertTrue(DATA_YAML_PATH.exists(), "data.yaml does not exist")
        with open(DATA_YAML_PATH) as f:
            cfg = yaml.safe_load(f)
        self.assertEqual(cfg.get("nc"), 11)
        self.assertIn("names", cfg)

    def test_split_directories(self):
        for split in ["train", "valid", "test"]:
            img_dir = DATASET_DIR / split / "images"
            lbl_dir = DATASET_DIR / split / "labels"
            self.assertTrue(img_dir.exists(), f"{split}/images missing")
            self.assertTrue(lbl_dir.exists(), f"{split}/labels missing")

            imgs = list(img_dir.glob("*.*"))
            lbls = list(lbl_dir.glob("*.txt"))
            self.assertGreater(len(imgs), 0, f"No images in {split}")
            self.assertEqual(len(imgs), len(lbls), f"Count mismatch in {split}")

    def test_sample_image_readable(self):
        test_img_dir = DATASET_DIR / "test" / "images"
        first_img = next(test_img_dir.glob("*.jpg"))
        with Image.open(first_img) as im:
            self.assertEqual(im.size, (640, 640))
            self.assertEqual(im.mode, "RGB")


if __name__ == "__main__":
    unittest.main()
