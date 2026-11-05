"""
Optical Character Recognition (OCR) Engine
"""
from typing import Tuple, Optional, List
import numpy as np
import cv2
import easyocr
from backend.app.config import OCR_CONFIDENCE_THRESHOLD, EASYOCR_MODEL_DIR

class LicensePlateOCR:
    _instance: Optional["LicensePlateOCR"] = None

    def __init__(self, use_gpu: bool = False):
        model_dir = EASYOCR_MODEL_DIR
        self.reader = easyocr.Reader(
            ['en'],
            gpu=use_gpu,
            model_storage_directory=model_dir,
            user_network_directory=model_dir,
            verbose=False
        )

    @classmethod
    def get_instance(cls, use_gpu: bool = False) -> "LicensePlateOCR":
        if cls._instance is None:
            cls._instance = cls(use_gpu=use_gpu)
        return cls._instance

    @staticmethod
    def preprocess_plate(crop: np.ndarray) -> np.ndarray:
        if crop is None or crop.size == 0:
            return crop

        h, w = crop.shape[:2]
        if h < 60:
            scale = 80.0 / max(h, 1)
            crop = cv2.resize(crop, (int(w * scale), 80), interpolation=cv2.INTER_CUBIC)

        if len(crop.shape) == 3:
            gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        else:
            gray = crop

        filtered = cv2.bilateralFilter(gray, 9, 75, 75)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(filtered)
        return enhanced

    def read_text(
        self,
        crop: np.ndarray,
        confidence_threshold: float = OCR_CONFIDENCE_THRESHOLD
    ) -> Tuple[str, float, np.ndarray]:
        if crop is None or crop.size == 0:
            return "", 0.0, crop

        preprocessed = self.preprocess_plate(crop)
        
        results = self.reader.readtext(
            preprocessed,
            allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
            detail=1,
            paragraph=False
        )

        if not results:
            results = self.reader.readtext(
                crop,
                allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
                detail=1,
                paragraph=False
            )

        if not results:
            return "", 0.0, preprocessed

        sorted_results = sorted(results, key=lambda r: (r[0][0][1] // 25, r[0][0][0]))

        extracted_words: List[str] = []
        confidences: List[float] = []

        for bbox, text, conf in sorted_results:
            clean = text.strip()
            if clean and conf >= confidence_threshold:
                extracted_words.append(clean)
                confidences.append(float(conf))

        raw_text = "".join(extracted_words)
        mean_conf = float(np.mean(confidences)) if confidences else 0.0

        return raw_text, mean_conf, preprocessed

