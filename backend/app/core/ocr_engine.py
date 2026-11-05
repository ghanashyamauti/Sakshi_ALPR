"""
Optical Character Recognition (OCR) Engine
High-precision multi-pass OCR for Indian vehicle and bike number plates.
"""
import cv2
import numpy as np
import easyocr
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

    def read_text(
        self,
        crop: np.ndarray,
        confidence_threshold: float = 0.20
    ) -> Tuple[str, float, np.ndarray]:
        if crop is None or crop.size == 0:
            return "", 0.0, crop

        resized, sharpened = self.enhance_crop(crop)

        from backend.app.core.postprocessor import IndianPlatePostProcessor

        # Check raw resized first, then sharpened
        for img_variant in (resized, sharpened):
            try:
                results = self.reader.readtext(
                    img_variant,
                    allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
                    detail=1,
                    paragraph=False,
                    text_threshold=0.20,
                    link_threshold=0.35,
                    low_text=0.20
                )
            except Exception:
                continue

            if not results:
                continue

            # Sort tokens horizontally and vertically (row-major)
            sorted_results = sorted(results, key=lambda r: (r[0][0][1] // 30, r[0][0][0]))

            words = []
            confs = []
            for _, text, conf in sorted_results:
                clean = text.strip()
                if clean:
                    words.append(clean)
                    confs.append(float(conf))

            combined_text = "".join(words)
            avg_conf = float(np.mean(confs)) if confs else 0.0

            # If this variant yields a valid Indian plate format, accept immediately!
            _, _, is_valid = IndianPlatePostProcessor.process(combined_text)
            if is_valid:
                import gc
                gc.collect()
                return combined_text, max(avg_conf, 0.75), resized

        # Fallback if neither variant was immediately valid: return whatever was found
        try:
            results = self.reader.readtext(resized, allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', paragraph=False)
            if results:
                text = "".join([r[1].strip() for r in results])
                conf = float(np.mean([r[2] for r in results]))
                import gc
                gc.collect()
                return text, conf, resized
        except Exception:
            pass

        import gc
        gc.collect()
        return "", 0.0, resized
