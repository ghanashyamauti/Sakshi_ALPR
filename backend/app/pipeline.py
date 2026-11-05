"""
End-to-End ALPR Master Pipeline for Backend
"""
import time
import uuid
import base64
from typing import Dict, Any, List, Optional
import numpy as np
import cv2
from PIL import Image
import io

from backend.app.config import (
    SAVE_DETECTIONS,
    FULL_FRAMES_DIR,
    CROPPED_PLATES_DIR,
    CONFIDENCE_THRESHOLD,
)
from backend.app.core.detector import LicensePlateDetector
from backend.app.core.ocr_engine import LicensePlateOCR
from backend.app.core.postprocessor import IndianPlatePostProcessor
from backend.app.core.rto_lookup import get_rto_details
from backend.app.database.repository import PlateRepository

class ALPRPipeline:
    def __init__(self, use_gpu: bool = False):
        self.detector = LicensePlateDetector.get_instance()
        self.ocr = LicensePlateOCR.get_instance(use_gpu=use_gpu)
        self.live_stream_cache: Dict[str, float] = {}
        self.cache_ttl_seconds = 10.0

    def annotate_frame(
        self,
        frame: np.ndarray,
        detections: List[Dict[str, Any]]
    ) -> np.ndarray:
        annotated = frame.copy()

        for item in detections:
            x1, y1, x2, y2 = item["bbox"]
            display_text = item.get("plate_number") or item.get("raw_text") or "Plate"
            state_code = item.get("state_code", "")
            conf = item.get("confidence", 0.0)
            is_valid = item.get("is_valid", False)

            color = (0, 200, 0) if is_valid else (255, 165, 0)
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)

            badge_text = f"{display_text} ({int(conf * 100)}%)"
            if state_code:
                badge_text = f"[{state_code}] {badge_text}"

            font = cv2.FONT_HERSHEY_SIMPLEX
            scale = 0.65
            thickness = 2
            (tw, th), _ = cv2.getTextSize(badge_text, font, scale, thickness)

            badge_y1 = max(0, y1 - th - 12)
            badge_y2 = y1
            badge_x1 = x1
            badge_x2 = min(annotated.shape[1], x1 + tw + 14)

            cv2.rectangle(annotated, (badge_x1, badge_y1), (badge_x2, badge_y2), color, -1)
            cv2.putText(annotated, badge_text, (badge_x1 + 6, badge_y2 - 6), font, scale, (0, 0, 0), thickness, cv2.LINE_AA)

        return annotated

    def process_image(
        self,
        image_input: Any,
        detection_mode: str = "Upload",
        save_to_db: bool = True,
        is_live_stream: bool = False,
    ) -> Dict[str, Any]:
        if isinstance(image_input, bytes):
            nparr = np.frombuffer(image_input, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        elif isinstance(image_input, str):
            image = cv2.imread(image_input)
        elif isinstance(image_input, Image.Image):
            image = cv2.cvtColor(np.array(image_input), cv2.COLOR_RGB2BGR)
        elif isinstance(image_input, np.ndarray):
            image = image_input.copy()
        else:
            raise TypeError("Unsupported image input format.")

        if image is None:
            raise ValueError("Invalid image: could not be decoded.")

        detections = self.detector.detect(image, confidence_threshold=CONFIDENCE_THRESHOLD)
        processed_plates = []
        now_epoch = time.time()

        for det in detections:
            crop = det["crop"]
            det_conf = det["confidence"]
            bbox = det["bbox"]

            if crop is None or crop.size == 0:
                continue

            raw_text, ocr_conf, _ = self.ocr.read_text(crop)
            if not raw_text:
                continue

            clean_plate, display_plate, is_valid = IndianPlatePostProcessor.process(raw_text)
            if len(clean_plate) < 4:
                continue

            state_code, state_name, rto_district = get_rto_details(clean_plate)
            overall_conf = float((det_conf * 0.4) + (ocr_conf * 0.6))

            should_save_to_db = save_to_db
            if is_live_stream:
                last_seen = self.live_stream_cache.get(clean_plate, 0.0)
                if (now_epoch - last_seen) < self.cache_ttl_seconds:
                    should_save_to_db = False
                else:
                    self.live_stream_cache[clean_plate] = now_epoch

            full_frame_path = None
            crop_path = None
            crop_url = None
            full_image_url = None

            if SAVE_DETECTIONS and should_save_to_db:
                file_uuid = uuid.uuid4().hex[:10]
                crop_filename = f"crop_{clean_plate}_{file_uuid}.jpg"
                full_filename = f"full_{clean_plate}_{file_uuid}.jpg"

                crop_dest = CROPPED_PLATES_DIR / crop_filename
                full_dest = FULL_FRAMES_DIR / full_filename

                cv2.imwrite(str(crop_dest), crop)
                cv2.imwrite(str(full_dest), image)

                crop_path = str(crop_dest)
                full_frame_path = str(full_dest)
                crop_url = f"/captures/cropped_plates/{crop_filename}"
                full_image_url = f"/captures/full_frames/{full_filename}"

            db_record = None
            if should_save_to_db:
                db_record = PlateRepository.create_record(
                    plate_number=display_plate,
                    raw_text=raw_text,
                    confidence=overall_conf,
                    state_code=state_code,
                    state_name=state_name,
                    rto_district=rto_district,
                    detection_mode=detection_mode,
                    full_image_path=full_frame_path,
                    crop_image_path=crop_path,
                    is_valid_format=is_valid,
                )

            # Base64 crop preview
            _, crop_buf = cv2.imencode('.jpg', crop)
            crop_b64 = base64.b64encode(crop_buf).decode('utf-8')

            processed_plates.append({
                "plate_number": display_plate,
                "clean_plate": clean_plate,
                "raw_text": raw_text,
                "confidence": round(overall_conf * 100, 1),
                "state_code": state_code or "Unknown",
                "state_name": state_name or "Unknown",
                "rto_district": rto_district or "Unknown",
                "is_valid": is_valid,
                "bbox": bbox,
                "crop_base64": f"data:image/jpeg;base64,{crop_b64}",
                "crop_url": crop_url,
                "full_image_url": full_image_url,
                "db_record": db_record,
            })

        annotated_image = self.annotate_frame(image, processed_plates)
        _, ann_buf = cv2.imencode('.jpg', annotated_image)
        ann_b64 = base64.b64encode(ann_buf).decode('utf-8')

        return {
            "annotated_image_base64": f"data:image/jpeg;base64,{ann_b64}",
            "plates": processed_plates,
            "count": len(processed_plates),
        }

    def process_video(
        self,
        video_path: str,
        frame_interval: int = 5,
        max_duration_sec: int = 90
    ) -> Dict[str, Any]:
        """
        Processes a full uploaded video to identify all vehicle & bike license plates.
        Extracts unique plates across the video and saves them to the database.
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration_sec = total_frames / fps if total_frames > 0 else 0

        unique_plates: Dict[str, Dict[str, Any]] = {}
        frame_count = 0
        processed_frames = 0
        max_frames_to_process = int(fps * max_duration_sec)

        while cap.isOpened() and frame_count < max_frames_to_process:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            if frame_count % frame_interval != 0:
                continue

            processed_frames += 1
            current_time_sec = frame_count / fps
            timestamp_str = f"{int(current_time_sec // 60):02d}:{int(current_time_sec % 60):02d}"

            # Detect plates in current frame
            detections = self.detector.detect(frame, confidence_threshold=CONFIDENCE_THRESHOLD)

            for det in detections:
                crop = det["crop"]
                det_conf = det["confidence"]
                if crop is None or crop.size == 0:
                    continue

                raw_text, ocr_conf, _ = self.ocr.read_text(crop)
                if not raw_text:
                    continue

                clean_plate, display_plate, is_valid = IndianPlatePostProcessor.process(raw_text)
                if len(clean_plate) < 4:
                    continue

                state_code, state_name, rto_district = get_rto_details(clean_plate)
                overall_conf = float((det_conf * 0.4) + (ocr_conf * 0.6))

                # Update or insert if higher confidence
                existing = unique_plates.get(clean_plate)
                if not existing or overall_conf > existing["confidence_raw"]:
                    _, crop_buf = cv2.imencode('.jpg', crop)
                    crop_b64 = base64.b64encode(crop_buf).decode('utf-8')

                    unique_plates[clean_plate] = {
                        "plate_number": display_plate,
                        "clean_plate": clean_plate,
                        "raw_text": raw_text,
                        "confidence": round(overall_conf * 100, 1),
                        "confidence_raw": overall_conf,
                        "state_code": state_code or "Unknown",
                        "state_name": state_name or "Unknown",
                        "rto_district": rto_district or "Unknown",
                        "is_valid": is_valid,
                        "timestamp_in_video": timestamp_str,
                        "crop_base64": f"data:image/jpeg;base64,{crop_b64}",
                    }

        cap.release()

        # Save all unique detected plates to Neon PostgreSQL database
        saved_plates = []
        for plate_data in unique_plates.values():
            db_record = PlateRepository.create_record(
                plate_number=plate_data["plate_number"],
                raw_text=plate_data["raw_text"],
                confidence=plate_data["confidence_raw"],
                state_code=plate_data["state_code"],
                state_name=plate_data["state_name"],
                rto_district=plate_data["rto_district"],
                detection_mode="Video Upload",
                is_valid_format=plate_data["is_valid"],
                notes=f"Found in video at {plate_data['timestamp_in_video']}"
            )
            plate_data["db_record"] = db_record
            saved_plates.append(plate_data)

        return {
            "duration_seconds": round(duration_sec, 1),
            "total_frames": total_frames,
            "processed_frames": processed_frames,
            "unique_plates_count": len(saved_plates),
            "plates": saved_plates,
        }

