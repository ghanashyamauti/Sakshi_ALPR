import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Base backend directory
BACKEND_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BACKEND_DIR.parent

# Load backend/.env
load_dotenv(BACKEND_DIR / ".env")

# Database URL (Neon PostgreSQL or SQLite fallback)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/alpr.db")

# Server Config
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# CORS origins
cors_raw = os.getenv("CORS_ORIGINS", '["*"]')
try:
    CORS_ORIGINS = json.loads(cors_raw)
except Exception:
    CORS_ORIGINS = ["*"]

# Model paths
PLATE_MODEL_PATH = os.getenv("PLATE_MODEL_PATH", str(BACKEND_DIR / "models" / "license_plate_detector.pt"))
if not Path(PLATE_MODEL_PATH).is_absolute():
    PLATE_MODEL_PATH = str((BACKEND_DIR / PLATE_MODEL_PATH).resolve())

EASYOCR_MODEL_DIR = os.getenv("EASYOCR_MODEL_DIR", str(BACKEND_DIR / "models" / "easyocr"))
if not Path(EASYOCR_MODEL_DIR).is_absolute():
    EASYOCR_MODEL_DIR = str((BACKEND_DIR / EASYOCR_MODEL_DIR).resolve())

CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.30"))
OCR_CONFIDENCE_THRESHOLD = float(os.getenv("OCR_CONFIDENCE_THRESHOLD", "0.35"))

# Storage paths
SAVE_DETECTIONS = os.getenv("SAVE_DETECTIONS", "True").lower() in ("true", "1", "yes")
STORAGE_DIR = BACKEND_DIR / os.getenv("STORAGE_DIR", "data")
FULL_FRAMES_DIR = STORAGE_DIR / "full_frames"
CROPPED_PLATES_DIR = STORAGE_DIR / "cropped_plates"
SAMPLES_DIR = BACKEND_DIR / "data" / "samples"

# Ensure directories exist
FULL_FRAMES_DIR.mkdir(parents=True, exist_ok=True)
CROPPED_PLATES_DIR.mkdir(parents=True, exist_ok=True)

# Application metadata
APP_NAME = os.getenv("APP_NAME", "Sakshi ALPR India API")
VERSION = os.getenv("VERSION", "2.0.0")

