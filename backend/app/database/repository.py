from datetime import datetime
from typing import List, Optional, Dict, Any
import pandas as pd
from sqlalchemy import desc, func
from backend.app.database.connection import get_db
from backend.app.database.models import PlateRecord

class PlateRepository:
    """Repository handling all database operations for license plate logs."""

    @staticmethod
    def create_record(
        plate_number: str,
        confidence: float,
        detection_mode: str,
        raw_text: Optional[str] = None,
        state_code: Optional[str] = None,
        state_name: Optional[str] = None,
        rto_district: Optional[str] = None,
        full_image_path: Optional[str] = None,
        crop_image_path: Optional[str] = None,
        is_valid_format: bool = False,
        is_hsrp: bool = False,
        hsrp_status: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        try:
            with get_db() as db:
                record = PlateRecord(
                    plate_number=plate_number,
                    raw_text=raw_text,
                    confidence=confidence,
                    state_code=state_code,
                    state_name=state_name,
                    rto_district=rto_district,
                    detection_mode=detection_mode,
                    timestamp=datetime.utcnow(),
                    full_image_path=full_image_path,
                    crop_image_path=crop_image_path,
                    is_valid_format=is_valid_format,
                    is_hsrp=is_hsrp,
                    hsrp_status=hsrp_status or ("Verified HSRP" if is_hsrp else ("Standard Non-HSRP" if is_valid_format else "Fancy / Non-Standard")),
                    notes=notes,
                )
                db.add(record)
                db.flush()
                db.refresh(record)
                return record.to_dict()
        except Exception as e:
            print(f"Warning: Database write bypassed ({e})")
            return None

    @staticmethod
    def get_records(
        search: Optional[str] = None,
        state: Optional[str] = None,
        mode: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        try:
            with get_db() as db:
                query = db.query(PlateRecord)

                if search:
                    q = f"%{search.strip()}%"
                    query = query.filter(
                        PlateRecord.plate_number.ilike(q) |
                        PlateRecord.rto_district.ilike(q) |
                        PlateRecord.state_name.ilike(q) |
                        PlateRecord.state_code.ilike(q) |
                        PlateRecord.raw_text.ilike(q)
                    )

                if state and state != "All":
                    query = query.filter(PlateRecord.state_code == state.upper())

                if mode and mode != "All":
                    query = query.filter(PlateRecord.detection_mode == mode)

                records = query.order_by(desc(PlateRecord.timestamp)).offset(offset).limit(limit).all()
                return [r.to_dict() for r in records]
        except Exception as e:
            print(f"Warning: Database read failed ({e})")
            return []

    @staticmethod
    def get_stats() -> Dict[str, Any]:
        try:
            with get_db() as db:
                total_scans = db.query(func.count(PlateRecord.id)).scalar() or 0
                unique_plates = db.query(func.count(func.distinct(PlateRecord.plate_number))).scalar() or 0
                valid_plates = db.query(func.count(PlateRecord.id)).filter(PlateRecord.is_valid_format == True).scalar() or 0
                avg_conf = db.query(func.avg(PlateRecord.confidence)).scalar() or 0.0
                
                return {
                    "total_scans": total_scans,
                    "unique_plates": unique_plates,
                    "valid_plates": valid_plates,
                    "avg_confidence": round(avg_conf * 100, 1),
                }
        except Exception:
            return {
                "total_scans": 0,
                "unique_plates": 0,
                "valid_plates": 0,
                "avg_confidence": 0.0,
            }

    @staticmethod
    def export_csv() -> str:
        try:
            with get_db() as db:
                records = db.query(PlateRecord).order_by(desc(PlateRecord.timestamp)).all()
                data = [r.to_dict() for r in records]
                if not data:
                    df = pd.DataFrame(columns=[
                        "id", "plate_number", "raw_text", "confidence", "state_code", 
                        "state_name", "rto_district", "detection_mode", "timestamp", "is_valid_format",
                        "is_hsrp", "hsrp_status"
                    ])
                else:
                    df = pd.DataFrame(data)
                return df.to_csv(index=False)
        except Exception:
            return ""

    @staticmethod
    def delete_all():
        try:
            with get_db() as db:
                db.query(PlateRecord).delete()
        except Exception:
            pass
