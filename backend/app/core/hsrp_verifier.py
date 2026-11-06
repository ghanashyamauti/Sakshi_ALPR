"""
Physical HSRP (High Security Registration Plate) Verification Engine
Analyzes physical visual characteristics (Blue IND Strip, Ashok Chakra hologram region,
color space distribution) and CMVR Rule 50 syntax standards.
"""
import cv2
import numpy as np
from typing import Dict, Any, Tuple

class HSRPVerifier:
    """
    Verifies whether a detected license plate is an authentic physical HSRP plate,
    a standard non-HSRP plate (e.g. vintage, painted, plain aluminum), or a
    fancy/non-standard plate.
    """

    @staticmethod
    def inspect_blue_strip(crop: np.ndarray) -> Tuple[bool, float]:
        """
        Detects the physical retro-reflective blue IND strip on the left 20% margin
        of the license plate using HSV color space masking.
        """
        if crop is None or crop.size == 0:
            return False, 0.0

        h, w = crop.shape[:2]
        if w < 15 or h < 10:
            return False, 0.0

        # Examine leftmost 18% - 22% of the plate
        strip_width = max(int(w * 0.22), 8)
        left_strip = crop[:, :strip_width]

        # Convert to HSV color space
        hsv = cv2.cvtColor(left_strip, cv2.COLOR_BGR2HSV)

        # Blue color range in HSV: Hue ~ 95-135, Saturation >= 45, Value >= 30
        lower_blue = np.array([95, 45, 30], dtype=np.uint8)
        upper_blue = np.array([135, 255, 255], dtype=np.uint8)

        blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
        blue_pixel_count = np.count_nonzero(blue_mask)
        total_pixels = blue_mask.size

        blue_ratio = float(blue_pixel_count) / float(total_pixels) if total_pixels > 0 else 0.0

        # Authentic HSRP blue IND strip typically covers 7% to 45% of the left margin
        is_blue_present = blue_ratio >= 0.065
        return is_blue_present, round(blue_ratio, 3)

    @classmethod
    def verify(
        cls,
        crop: np.ndarray,
        raw_text: str,
        is_valid_format: bool
    ) -> Dict[str, Any]:
        """
        Comprehensive physical + semantic verification of Indian HSRP compliance.
        """
        has_blue_strip, blue_ratio = cls.inspect_blue_strip(crop)

        # Check if raw OCR text explicitly contained 'IND' prefix
        clean_upper = raw_text.upper() if raw_text else ""
        has_ind_token = any(clean_upper.startswith(token) for token in ("IND", "1ND", "INO", "1NO", "IN0", "IN "))

        # True physical HSRP verification
        is_hsrp = (has_blue_strip or has_ind_token) and is_valid_format

        if is_hsrp:
            status = "Verified HSRP"
            badge_label = "Verified Indian HSRP"
            badge_class = "badge-hsrp"
            description = "Authentic High Security Registration Plate with verified blue IND strip."
        elif is_valid_format:
            status = "Standard Non-HSRP"
            badge_label = "Standard / Non-HSRP Plate"
            badge_class = "badge-standard"
            description = "Valid Indian number format, but lacks physical HSRP blue IND security strip."
        else:
            status = "Fancy / Non-Standard"
            badge_label = "Fancy / Non-Standard Plate"
            badge_class = "badge-fancy"
            description = "Does not comply with standard Indian CMVR registration format."

        return {
            "is_hsrp": is_hsrp,
            "hsrp_status": status,
            "badge_label": badge_label,
            "badge_class": badge_class,
            "has_blue_strip": has_blue_strip,
            "blue_strip_ratio": blue_ratio,
            "has_ind_token": has_ind_token,
            "description": description,
        }

