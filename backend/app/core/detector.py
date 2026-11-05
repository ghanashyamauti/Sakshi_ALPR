"""
YOLOv8 License Plate Detector Module
"""
import os
from typing import List, Dict, Any, Optional
import numpy as np
import torch
import ultralytics.nn.tasks as tasks

# PyTorch 2.6+ / Ultralytics patch: Ensures custom model checkpoints load cleanly
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

from ultralytics import YOLO
from backend.app.config import PLATE_MODEL_PATH, CONFIDENCE_THRESHOLD

class LicensePlateDetector:
    _instance: Optional["LicensePlateDetector"] = None

    def __init__(self, model_path: Optional[str] = None):
        path = model_path or PLATE_MODEL_PATH
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found at: {path}")
        
        self.model = YOLO(path)
        self.names = self.model.names

    @classmethod
    def get_instance(cls, model_path: Optional[str] = None) -> "LicensePlateDetector":
        if cls._instance is None:
            cls._instance = cls(model_path)
        return cls._instance

    def detect(
        self,
        image: np.ndarray,
        confidence_threshold: float = CONFIDENCE_THRESHOLD,
        padding: int = 5
    ) -> List[Dict[str, Any]]:
        results = self.model(image, conf=confidence_threshold, verbose=False)
        detections = []
        h, w = image.shape[:2]

        for result in results:
            boxes = result.boxes
            if boxes is None or len(boxes) == 0:
                continue

            for box in boxes:
                conf = float(box.conf[0].cpu().numpy())
                cls_id = int(box.cls[0].cpu().numpy())
                cls_name = self.names.get(cls_id, "License_Plate")

                coords = box.xyxy[0].cpu().numpy().astype(int)
                x1, y1, x2, y2 = coords

                x1_pad = max(0, x1 - padding)
                y1_pad = max(0, y1 - padding)
                x2_pad = min(w, x2 + padding)
                y2_pad = min(h, y2 + padding)

                crop = image[y1_pad:y2_pad, x1_pad:x2_pad]

                detections.append({
                    "bbox": [int(x1), int(y1), int(x2), int(y2)],
                    "padded_bbox": [int(x1_pad), int(y1_pad), int(x2_pad), int(y2_pad)],
                    "confidence": conf,
                    "crop": crop,
                    "class_name": cls_name
                })

        return detections

