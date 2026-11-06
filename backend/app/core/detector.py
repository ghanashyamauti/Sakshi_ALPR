"""
YOLOv8 License Plate Detector Module
Supports high-resolution multi-scale inference for detecting both large vehicle plates
and small, distant, or moving bike/scooter plates.
"""
import backend.app.patch_torch  # noqa: F401
import os
from typing import List, Dict, Any, Optional
import numpy as np

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
        padding: int = 5,
        imgsz: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Runs YOLOv8 detection with dynamic multi-scale resolution.
        Higher imgsz preserves small motorcycle plates on 1080p/720p inputs.
        """
        if image is None or image.size == 0:
            return []

        h, w = image.shape[:2]
        
        if imgsz is not None:
            target_imgsz = imgsz
        else:
            max_dim = max(h, w)
            if max_dim >= 1080:
                target_imgsz = 1024
            elif max_dim >= 720:
                target_imgsz = 800
            else:
                target_imgsz = 640

        try:
            results = self.model(image, conf=confidence_threshold, imgsz=target_imgsz, verbose=False)
        except Exception:
            # Fallback to standard 640 if memory limit reached
            results = self.model(image, conf=confidence_threshold, imgsz=640, verbose=False)

        detections = []

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
                if crop.size == 0 or crop.shape[0] < 5 or crop.shape[1] < 5:
                    continue

                detections.append({
                    "bbox": [int(x1), int(y1), int(x2), int(y2)],
                    "padded_bbox": [int(x1_pad), int(y1_pad), int(x2_pad), int(y2_pad)],
                    "confidence": conf,
                    "crop": crop,
                    "class_name": cls_name
                })

        return detections
