"""
app.py - Root Entry Point for SPACI 2.0 Web Application
========================================================
Runs the high-performance FastAPI Mission Control HUD web server.
Usage:
    python app.py [--port 8080] [--host 0.0.0.0]
"""

import sys
import argparse
from pathlib import Path
import uvicorn

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from server import app

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SPACI 2.0 Mission Control HUD")
    parser.add_argument("--port", type=int, default=8080, help="Port to run server on")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host address")
    args = parser.parse_args()

    print(f"[SPACI 2.0] Mission Control HUD active at: http://localhost:{args.port}")
    uvicorn.run("server:app", host=args.host, port=args.port, reload=False, log_level="info")

