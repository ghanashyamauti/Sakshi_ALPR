"""
Runner script for Sakshi ALPR India Backend Server
Run: python run_backend.py
"""
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Apply global PyTorch compatibility patch before any other imports
import backend.app.patch_torch  # noqa: F401

import uvicorn
from backend.app.config import HOST, PORT, APP_NAME

if __name__ == "__main__":
    print(f"==================================================")
    print(f"  Starting {APP_NAME}")
    print(f"  Listening on: http://{HOST}:{PORT}")
    print(f"  Swagger Docs: http://{HOST}:{PORT}/docs")
    print(f"==================================================")
    uvicorn.run(
        "backend.app.main:app",
        host=HOST,
        port=PORT,
        reload=False
    )
