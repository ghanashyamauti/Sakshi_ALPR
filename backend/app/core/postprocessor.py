"""
Indian License Plate Post-Processor & Validation Engine
Handles OCR error correction, IND stripe stripping, and standard formatting.
"""
import re
from typing import Tuple

# Character correction dictionaries
CHAR_TO_DIGIT = {
    'O': '0', 'D': '0', 'Q': '0',
    'I': '1', 'L': '1', 'T': '1',
    'Z': '2',
    'E': '3',
    'A': '4',
    'S': '5',
    'G': '6', 'B': '8',
}

DIGIT_TO_CHAR = {
    '0': 'O',
    '1': 'I',
    '2': 'Z',
    '4': 'A',
    '5': 'S',
    '6': 'G',
    '8': 'B',
}

class IndianPlatePostProcessor:
    """Specialized post-processor for Indian Vehicle Number Plates."""

    STANDARD_PATTERN = re.compile(r"^[A-Z]{2}[0-9]{1,2}[A-Z]{0,3}[0-9]{4}$")
    BH_SERIES_PATTERN = re.compile(r"^[0-9]{2}BH[0-9]{4}[A-Z]{1,2}$")

    @classmethod
    def clean_raw_text(cls, raw_text: str) -> str:
        """Strips noise, whitespace, punctuation, and leading/trailing IND badges."""
        if not raw_text:
            return ""

        cleaned = raw_text.upper()
        cleaned = re.sub(r"[^A-Z0-9]", "", cleaned)

        badges = ("IND", "1ND", "IN0", "1N0", "INO", "1NO", "IN")
        for b in badges:
            if cleaned.startswith(b) and len(cleaned) > len(b) + 4:
                cleaned = cleaned[len(b):]
                break
        for b in badges:
            if cleaned.endswith(b) and len(cleaned) > len(b) + 4:
                cleaned = cleaned[:-len(b)]
                break

        return cleaned

    @classmethod
    def disambiguate_indian_plate(cls, text: str) -> str:
        chars = list(text)
        n = len(chars)

        if n < 6:
            return text

        # Check Bharat Series
        if chars[0].isdigit() or (chars[0] in CHAR_TO_DIGIT and n >= 4 and "".join(chars[2:4]) in ("BH", "8H", "BI")):
            if chars[0] in CHAR_TO_DIGIT: chars[0] = CHAR_TO_DIGIT[chars[0]]
            if chars[1] in CHAR_TO_DIGIT: chars[1] = CHAR_TO_DIGIT[chars[1]]
            chars[2] = 'B'
            chars[3] = 'H'
            return "".join(chars)

        # First 2 positions MUST be letters
        for i in range(min(2, n)):
            if chars[i].isdigit() and chars[i] in DIGIT_TO_CHAR:
                chars[i] = DIGIT_TO_CHAR[chars[i]]

        # Positions 2-3 should be digits
        if n >= 4:
            if chars[2] in CHAR_TO_DIGIT:
                chars[2] = CHAR_TO_DIGIT[chars[2]]
            if n > 3 and chars[3] in CHAR_TO_DIGIT:
                chars[3] = CHAR_TO_DIGIT[chars[3]]

        # Last 4 characters should be digits
        if n >= 8:
            for i in range(n - 4, n):
                if chars[i] in CHAR_TO_DIGIT:
                    chars[i] = CHAR_TO_DIGIT[chars[i]]

        return "".join(chars)

    @classmethod
    def format_plate_display(cls, clean_text: str) -> str:
        if not clean_text:
            return ""

        match = re.match(r"^([A-Z]{2})([0-9]{1,2})([A-Z]{0,3})([0-9]{4})$", clean_text)
        if match:
            state, rto, series, number = match.groups()
            parts = [state, rto]
            if series:
                parts.append(series)
            parts.append(number)
            return " ".join(parts)

        bh_match = re.match(r"^([0-9]{2})(BH)([0-9]{4})([A-Z]{1,2})$", clean_text)
        if bh_match:
            year, bh, num, series = bh_match.groups()
            return f"{year} {bh} {num} {series}"

        return clean_text

    @classmethod
    def process(cls, raw_ocr_text: str) -> Tuple[str, str, bool]:
        cleaned = cls.clean_raw_text(raw_ocr_text)
        disambiguated = cls.disambiguate_indian_plate(cleaned)
        
        # Match standard or Bharat series substring if attached to noise
        embedded_std = re.search(r"([A-Z]{2}[0-9]{1,2}[A-Z]{0,3}[0-9]{4})", disambiguated)
        embedded_bh = re.search(r"([0-9]{2}BH[0-9]{4}[A-Z]{1,2})", disambiguated)

        if embedded_std:
            disambiguated = embedded_std.group(1)
            is_valid = True
        elif embedded_bh:
            disambiguated = embedded_bh.group(1)
            is_valid = True
        else:
            is_valid = bool(
                cls.STANDARD_PATTERN.match(disambiguated) or 
                cls.BH_SERIES_PATTERN.match(disambiguated)
            )

        display = cls.format_plate_display(disambiguated)
        return disambiguated, display, is_valid

