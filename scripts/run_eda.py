"""
run_eda.py - Shortcut script to launch dataset audit and generate EDA plots
"""
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.eda import analyze_dataset, generate_eda_visualizations

if __name__ == "__main__":
    print("[SPACI 2.0] Executing Dataset Audit & EDA Pipeline...")
    stats = analyze_dataset()
    generate_eda_visualizations(stats)
    print("[SPACI 2.0] Done! Check reports/ for outputs.")
