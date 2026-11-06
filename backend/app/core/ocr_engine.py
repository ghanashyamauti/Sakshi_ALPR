"""
Optical Character Recognition (OCR) Engine
High-precision multi-pass OCR for Indian vehicle and motorcycle number plates.
Supports standard single-line plates and two-line square motorcycle/scooter plates.
Optimized for low-latency CPU inference without redundant passes.
"""
import cv2
import numpy as np
import easyocr
import gc
from typing import Tuple, Optional, List
import backend.app.patch_torch  # noqa: F401
from backend.app.config import EASYOCR_MODEL_DIR

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
    def enhance_crop(crop: np.ndarray, target_height: int = 140) -> Tuple[np.ndarray, np.ndarray]:
        """
        Upscales plate crop to optimal resolution and produces two enhanced versions:
        1. Resized high-detail color crop
        2. Sharpened unsharp-masked crop for thin font strokes
        """
        if crop is None or crop.size == 0:
            return crop, crop

        h, w = crop.shape[:2]
        scale = max(target_height / max(h, 1), 1.0)
        new_w = int(w * scale)
        resized = cv2.resize(crop, (new_w, target_height), interpolation=cv2.INTER_CUBIC)

        # Grayscale & Sharpening
        if len(resized.shape) == 3:
            gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        else:
            gray = resized.copy()

        kernel = np.array([[-1, -1, -1],
                           [-1,  9, -1],
                           [-1, -1, -1]])
        sharpened = cv2.filter2D(gray, -1, kernel)

        return resized, sharpened

    def _ocr_single(self, img: np.ndarray) -> Tuple[str, float]:
        """Runs EasyOCR on a single image and returns concatenated text and mean confidence."""
        try:
            results = self.reader.readtext(
                img,
                allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
                detail=1,
                paragraph=False,
                text_threshold=0.25,
                link_threshold=0.40,
                low_text=0.25
            )
            if not results:
                return "", 0.0

            # Sort row-major (top-to-bottom, left-to-right)
            sorted_res = sorted(results, key=lambda r: (r[0][0][1] // 28, r[0][0][0]))
            words = [r[1].strip() for r in sorted_res if r[1].strip()]
            confs = [float(r[2]) for r in sorted_res if r[1].strip()]
            
            combined = "".join(words)
            mean_conf = float(np.mean(confs)) if confs else 0.0
            return combined, mean_conf
        except Exception:
            return "", 0.0

    def read_text(
        self,
        crop: np.ndarray,
        confidence_threshold: float = 0.20
    ) -> Tuple[str, float, np.ndarray]:
        if crop is None or crop.size == 0:
            return "", 0.0, crop

        from backend.app.core.postprocessor import IndianPlatePostProcessor

        h, w = crop.shape[:2]
        aspect_ratio = float(w) / float(max(h, 1))

        resized, sharpened = self.enhance_crop(crop)

        # 1. Primary pass on resized crop
        text1, conf1 = self._ocr_single(resized)
        if text1:
            _, _, is_valid = IndianPlatePostProcessor.process(text1)
            if is_valid:
                gc.collect()
                return text1, max(conf1, 0.75), resized

        # 2. Secondary pass on sharpened crop
        text2, conf2 = self._ocr_single(sharpened)
        if text2:
            _, _, is_valid = IndianPlatePostProcessor.process(text2)
            if is_valid:
                gc.collect()
                return text2, max(conf2, 0.75), resized

        # 3. Two-line bike plate pass if aspect ratio < 2.3
        if aspect_ratio < 2.3 and h >= 30:
            top_half = crop[:int(h * 0.55), :]
            bot_half = crop[int(h * 0.45):, :]

            top_resized, _ = self.enhance_crop(top_half, target_height=100)
            bot_resized, _ = self.enhance_crop(bot_half, target_height=100)

            top_text, top_conf = self._ocr_single(top_resized)
            bot_text, bot_conf = self._ocr_single(bot_resized)

            if top_text and bot_text:
                combined_bike = top_text + bot_text
                _, _, is_valid = IndianPlatePostProcessor.process(combined_bike)
                if is_valid:
                    gc.collect()
                    return combined_bike, max((top_conf + bot_conf) / 2.0, 0.75), resized

        # 4. Fallback: Return whichever candidate had more characters without re-running OCR
        best_candidate = text1 if len(text1) >= len(text2) else text2
        best_conf = conf1 if len(text1) >= len(text2) else conf2
        
        gc.collect()
        if len(best_candidate) >= 4:
            return best_candidate, best_conf, resized

        return "", 0.0, resized
