"""
Detection API Routes
"""
import backend.app.patch_torch  # noqa: F401
import base64
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, File, UploadFile, HTTPException, Body, Form, Query
from pydantic import BaseModel

from backend.app.config import SAMPLES_DIR
from backend.app.pipeline import ALPRPipeline

router = APIRouter(prefix="/api/v1/detect", tags=["Detection"])

# Global pipeline instance
_pipeline: Optional[ALPRPipeline] = None

def get_pipeline() -> ALPRPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = ALPRPipeline(use_gpu=False)
    return _pipeline

class SnapshotPayload(BaseModel):
    image_base64: str
    detection_mode: str = "Live Snapshot"
    engine: str = "ai"

class AIKeyPayload(BaseModel):
    api_key: str

@router.get("/ai-status")
async def get_ai_status():
    """Returns whether Gemini Multimodal Vision AI is enabled."""
    from backend.app.core.vision_ai import GeminiVisionALPR
    return {"ai_enabled": GeminiVisionALPR.get_instance().is_available()}

@router.post("/set-ai-key")
async def set_ai_key(payload: AIKeyPayload):
    """Dynamically activates Gemini Vision AI mode at runtime with provided key."""
    import os
    from backend.app.core.vision_ai import GeminiVisionALPR
    key = payload.api_key.strip()
    os.environ["GEMINI_API_KEY"] = key
    GeminiVisionALPR.get_instance().api_key = key
    return {"success": True, "ai_enabled": GeminiVisionALPR.get_instance().is_available()}

@router.post("/upload")
async def detect_upload(
    file: UploadFile = File(...),
    engine: str = Form("ai")
):
    """Upload a vehicle image file (.jpg, .png) for license plate recognition."""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image.")

    content = await file.read()
    pipeline = get_pipeline()
    try:
        result = pipeline.process_image(
            content,
            detection_mode="Upload",
            save_to_db=True,
            is_live_stream=False,
            engine=engine
        )
        return {
            "success": True,
            "filename": file.filename,
            "plates_detected": result["count"],
            "plates": result["plates"],
            "annotated_image": result["annotated_image_base64"],
            "engine": result.get("engine", "Local YOLOv8 + OCR")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-video")
async def detect_upload_video(
    file: UploadFile = File(...),
    engine: str = Form("ai")
):
    """Upload a vehicle video (.mp4, .avi, .mov) to detect and extract all bike & car license plates."""
    import tempfile
    import os

    suffix = Path(file.filename or "video.mp4").suffix or ".mp4"
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        content = await file.read()
        temp_file.write(content)
        temp_file.flush()
        temp_file.close()

        pipeline = get_pipeline()
        result = pipeline.process_video(temp_file.name, engine=engine)
        return {
            "success": True,
            "filename": file.filename,
            "duration_seconds": result["duration_seconds"],
            "total_frames": result["total_frames"],
            "processed_frames": result["processed_frames"],
            "unique_plates_count": result["unique_plates_count"],
            "plates": result["plates"],
            "engine": result.get("engine", "Local YOLOv8 + OCR")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_file.name):
            try:
                os.unlink(temp_file.name)
            except Exception:
                pass

@router.post("/snapshot")
async def detect_snapshot(payload: SnapshotPayload):
    """Process a live snapshot taken from client webcam."""
    b64_data = payload.image_base64
    if "," in b64_data:
        b64_data = b64_data.split(",")[1]

    try:
        image_bytes = base64.b64decode(b64_data)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 image data.")

    pipeline = get_pipeline()
    try:
        result = pipeline.process_image(
            image_bytes,
            detection_mode=payload.detection_mode,
            save_to_db=True,
            is_live_stream=False
        )
        return {
            "success": True,
            "plates_detected": result["count"],
            "plates": result["plates"],
            "annotated_image": result["annotated_image_base64"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stream-frame")
async def detect_stream_frame(payload: SnapshotPayload):
    """Process real-time video stream frame with intelligent deduplication."""
    b64_data = payload.image_base64
    if "," in b64_data:
        b64_data = b64_data.split(",")[1]

    try:
        image_bytes = base64.b64decode(b64_data)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 image data.")

    pipeline = get_pipeline()
    try:
        result = pipeline.process_image(
            image_bytes,
            detection_mode="Live Stream",
            save_to_db=True,
            is_live_stream=True
        )
        return {
            "success": True,
            "plates_detected": result["count"],
            "plates": result["plates"],
            "annotated_image": result["annotated_image_base64"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/samples")
async def list_samples():
    """List preloaded sample vehicle images for testing."""
    if not SAMPLES_DIR.exists():
        return {"samples": []}
    files = [f.name for f in SAMPLES_DIR.glob("*.jpg")] + [f.name for f in SAMPLES_DIR.glob("*.png")]
    return {"samples": files}

@router.post("/sample/{sample_name}")
async def detect_sample(sample_name: str):
    """Run detection directly on one of the preloaded sample images."""
    sample_path = SAMPLES_DIR / sample_name
    if not sample_path.exists():
        raise HTTPException(status_code=404, detail=f"Sample '{sample_name}' not found.")

    pipeline = get_pipeline()
    try:
        result = pipeline.process_image(
            str(sample_path),
            detection_mode="Upload (Sample)",
            save_to_db=True
        )
        return {
            "success": True,
            "sample_name": sample_name,
            "plates_detected": result["count"],
            "plates": result["plates"],
            "annotated_image": result["annotated_image_base64"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

