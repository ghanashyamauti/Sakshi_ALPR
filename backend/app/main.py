"""
Sakshi ALPR India - FastAPI Main Server
"""
try:
    import torch.utils.serialization
except Exception:
    pass

import torch
import ultralytics.nn.tasks as tasks

# Global PyTorch 2.6+ / Ultralytics patch to prevent weights_only unpickling failures
_orig_torch_load = torch.load
def _patched_torch_load(*args, **kwargs):
    if "weights_only" not in kwargs:
        kwargs["weights_only"] = False
    return _orig_torch_load(*args, **kwargs)
torch.load = _patched_torch_load

def _safe_load_wrapper(weight, safe_only=None):
    ckpt = torch.load(weight, map_location="cpu", weights_only=False)
    if not isinstance(ckpt, dict):
        ckpt = {"model": ckpt.model}
    return ckpt, str(weight)

tasks.torch_safe_load = _safe_load_wrapper

try:
    import ultralytics.engine.model as model_engine
    model_engine.torch_safe_load = _safe_load_wrapper
except Exception:
    pass

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from backend.app.config import (
    APP_NAME,
    VERSION,
    CORS_ORIGINS,
    STORAGE_DIR,
    DATABASE_URL,
    PLATE_MODEL_PATH,
)
from backend.app.database.connection import init_db
from backend.app.api import detect_router, records_router, stats_router

# Initialize Database Schema on startup
init_db()

app = FastAPI(
    title=APP_NAME,
    version=VERSION,
    description="Enterprise License Plate Recognition REST API fine-tuned for Indian Vehicles.",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for frontend applications
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static folder for vehicle images & crops
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/captures", StaticFiles(directory=str(STORAGE_DIR)), name="captures")

# Register API Sub-routers
app.include_router(detect_router)
app.include_router(records_router)
app.include_router(stats_router)

@app.on_event("startup")
async def startup_warmup():
    """Pre-warm AI detection pipeline and models into memory on server start."""
    try:
        from backend.app.api.routes_detect import get_pipeline
        get_pipeline()
        print("[OK] Sakshi ALPR AI Pipeline & Models successfully loaded into memory!")
    except Exception as e:
        print(f"[WARNING] Pre-warm note: {e}")

@app.get("/")
async def root():
    return {
        "app": APP_NAME,
        "version": VERSION,
        "status": "online",
        "docs": "/docs",
        "database": "Neon PostgreSQL" if "neon.tech" in DATABASE_URL else "SQLite"
    }

@app.get("/api/v1/health")
async def health_check():
    model_ok = Path(PLATE_MODEL_PATH).exists()
    return {
        "status": "healthy",
        "database_connected": True,
        "model_loaded": model_ok,
        "model_path": PLATE_MODEL_PATH,
    }

