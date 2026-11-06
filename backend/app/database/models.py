from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class PlateRecord(Base):
    """
    Model representing a recognized license plate log in PostgreSQL / SQLite.
    """
    __tablename__ = "plate_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    plate_number = Column(String(32), index=True, nullable=False)
    raw_text = Column(String(64), nullable=True)
    confidence = Column(Float, nullable=False, default=0.0)
    
    state_code = Column(String(8), nullable=True, index=True)
    state_name = Column(String(64), nullable=True)
    rto_district = Column(String(128), nullable=True)
    
    detection_mode = Column(String(32), nullable=False, default="Upload")  # Upload, Snapshot, Live Stream, Video Upload
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    full_image_path = Column(Text, nullable=True)
    crop_image_path = Column(Text, nullable=True)
    is_valid_format = Column(Boolean, default=False)
    is_hsrp = Column(Boolean, default=False, nullable=True)
    hsrp_status = Column(String(64), default="Standard Non-HSRP", nullable=True)
    notes = Column(Text, nullable=True)

    def to_dict(self):
        # Extract relative URL for serving static crops
        crop_name = ""
        if self.crop_image_path and str(self.crop_image_path).strip() not in ("None", "null", ""):
            crop_name = str(self.crop_image_path).replace("\\", "/").split("/")[-1]

        full_name = ""
        if self.full_image_path and str(self.full_image_path).strip() not in ("None", "null", ""):
            full_name = str(self.full_image_path).replace("\\", "/").split("/")[-1]

        is_hsrp_val = bool(self.is_hsrp) if self.is_hsrp is not None else False
        status_val = self.hsrp_status
        if not status_val:
            if is_hsrp_val:
                status_val = "Verified HSRP"
            elif self.is_valid_format:
                status_val = "Standard Non-HSRP"
            else:
                status_val = "Fancy / Non-Standard"

        return {
            "id": self.id,
            "plate_number": self.plate_number,
            "raw_text": self.raw_text,
            "confidence": round(self.confidence * 100, 1),
            "state_code": self.state_code or "Unknown",
            "state_name": self.state_name or "Unknown",
            "rto_district": self.rto_district or "Unknown",
            "detection_mode": self.detection_mode,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.timestamp else "",
            "full_image_url": f"/captures/full_frames/{full_name}" if full_name else None,
            "crop_image_url": f"/captures/cropped_plates/{crop_name}" if crop_name else None,
            "full_image_path": self.full_image_path,
            "crop_image_path": self.crop_image_path,
            "is_valid_format": self.is_valid_format,
            "is_hsrp": is_hsrp_val,
            "hsrp_status": status_val,
            "notes": self.notes,
        }

    def __repr__(self):
        return f"<PlateRecord(id={self.id}, plate='{self.plate_number}', state='{self.state_code}', hsrp='{self.hsrp_status}')>"
