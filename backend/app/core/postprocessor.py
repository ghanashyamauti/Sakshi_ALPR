"""
Indian License Plate Post-Processor & Validation Engine
Handles OCR error correction, State code disambiguation, IND stripe stripping, and standard formatting.
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
    'G': '6',
    'B': '8',
}

DIGIT_TO_CHAR = {
    '0': 'O',
    '1': 'I',
    '2': 'Z',
    '3': 'B',
    '4': 'A',
    '5': 'S',
    '6': 'G',
    '8': 'B',
}

# All 36 Official Indian States & Union Territory Codes + BH Series
VALID_STATE_CODES = {
    "AN", "AP", "AR", "AS", "BR", "CH", "CG", "DD", "DL", "DN",
    "GA", "GJ", "HR", "HP", "JH", "JK", "KA", "KL", "LA", "LD",
    "MP", "MH", "MN", "ML", "MZ", "NL", "OD", "PB", "PY", "RJ",
    "SK", "TN", "TS", "TR", "UP", "UK", "UA", "WB", "BH"
}

# Common OCR Misrecognitions for Indian State Codes
STATE_CODE_CORRECTIONS = {
    "MA": "MH",  # Very common: 'H' misread as 'A'
    "M4": "MH",
    "M1": "MH",
    "MI": "MH",
    "MO": "MH",
    "MD": "MH",
    "NH": "MH",
    "D1": "DL",
    "DI": "DL",
    "0L": "DL",
    "OL": "DL",
    "QL": "DL",
    "G1": "GJ",
    "GI": "GJ",
    "CJ": "GJ",
    "6J": "GJ",
    "K1": "KA",
    "KI": "KA",
    "KB": "KA",
    "KO": "KA",
    "K0": "KA",
    "K4": "KA",
    "U9": "UP",
    "VP": "UP",
    "0P": "UP",
    "OP": "UP",
    "H1": "HR",
    "HA": "HR",
    "T5": "TS",
    "TG": "TS",
    "T1": "TN",
    "TM": "TN",
    "P8": "PB",
    "PI": "PB",
    "8R": "BR",
    "B8": "BR",
    "JA": "JH",
    "J1": "JH",
    "C6": "CG",
    "W8": "WB",
    "C1": "CH",
    "C4": "CH",
    "G4": "GA",
    "0D": "OD",
    "OR": "OD",
    "IK": "JK",
}

class IndianPlatePostProcessor:
    """Specialized post-processor for Indian Vehicle & Bike Number Plates."""

    STANDARD_PATTERN = re.compile(r"^[A-Z]{2}[0-9]{1,2}[A-Z]{0,3}[0-9]{1,4}$")
    BH_SERIES_PATTERN = re.compile(r"^[0-9]{2}BH[0-9]{4}[A-Z]{1,2}$")

    @classmethod
    def clean_raw_text(cls, raw_text: str) -> str:
        """Strips noise, whitespace, punctuation, and leading/trailing IND badges."""
        if not raw_text:
            return ""

        cleaned = raw_text.upper()
        cleaned = re.sub(r"[^A-Z0-9]", "", cleaned)

        # Strip embossed HSRP IND badges
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

        if n < 5:
            return text

        # 1. Check Bharat Series (e.g., 22BH1234AA)
        if chars[0].isdigit() or (chars[0] in CHAR_TO_DIGIT and n >= 4 and "".join(chars[2:4]) in ("BH", "8H", "BI")):
            if chars[0] in CHAR_TO_DIGIT: chars[0] = CHAR_TO_DIGIT[chars[0]]
            if chars[1] in CHAR_TO_DIGIT: chars[1] = CHAR_TO_DIGIT[chars[1]]
            chars[2] = 'B'
            chars[3] = 'H'
            return "".join(chars)

        # 2. State Code (Characters 0 and 1) - MUST BE LETTERS
        for i in range(min(2, n)):
            if chars[i].isdigit() and chars[i] in DIGIT_TO_CHAR:
                chars[i] = DIGIT_TO_CHAR[chars[i]]

        state_prefix = "".join(chars[:2])
        if state_prefix not in VALID_STATE_CODES:
            if state_prefix in STATE_CODE_CORRECTIONS:
                corrected_state = STATE_CODE_CORRECTIONS[state_prefix]
                chars[0] = corrected_state[0]
                chars[1] = corrected_state[1]

        # 3. RTO Code (Characters 2 and 3) - MUST BE DIGITS
        if n >= 4:
            if chars[2] in CHAR_TO_DIGIT:
                chars[2] = CHAR_TO_DIGIT[chars[2]]
            if chars[3] in CHAR_TO_DIGIT:
                chars[3] = CHAR_TO_DIGIT[chars[3]]

        # 4. Last 1 to 4 characters - MUST BE DIGITS
        num_digits_at_end = min(4, n - 4)
        for i in range(n - num_digits_at_end, n):
            if chars[i] in CHAR_TO_DIGIT:
                chars[i] = CHAR_TO_DIGIT[chars[i]]

        # 5. Middle Characters (Series letters between RTO and Number) - MUST BE LETTERS
        # e.g. for MH 17 BB 1105 (len 10), chars 4..5 are series 'BB'
        if n >= 8:
            series_end = n - 4
            for i in range(4, series_end):
                if chars[i].isdigit() and chars[i] in DIGIT_TO_CHAR:
                    chars[i] = DIGIT_TO_CHAR[chars[i]]

        return "".join(chars)

    @classmethod
    def format_plate_display(cls, clean_text: str) -> str:
        if not clean_text:
            return ""

        # Match Standard Indian Plate: SS RR TTT NNNN
        match = re.match(r"^([A-Z]{2})([0-9]{1,2})([A-Z]{0,3})([0-9]{1,4})$", clean_text)
        if match:
            state, rto, series, number = match.groups()
            parts = [state, rto]
            if series:
                parts.append(series)
            parts.append(number)
            return " ".join(parts)

        # Match Bharat Series: YY BH NNNN AA
        match_bh = re.match(r"^([0-9]{2})(BH)([0-9]{4})([A-Z]{1,2})$", clean_text)
        if match_bh:
            year, bh, number, series = match_bh.groups()
            return f"{year} {bh} {number} {series}"

        return clean_text

    @classmethod
    def is_valid_plate(cls, text: str) -> bool:
        if not text:
            return False
        return bool(cls.STANDARD_PATTERN.match(text) or cls.BH_SERIES_PATTERN.match(text))

    @classmethod
    def process(cls, raw_text: str) -> Tuple[str, str, bool]:
        """
        End-to-end pipeline:
        raw_text -> clean_plate, display_plate, is_valid
        """
        cleaned = cls.clean_raw_text(raw_text)
        if not cleaned:
            return "", "", False

        disambiguated = cls.disambiguate_indian_plate(cleaned)
        is_valid = cls.is_valid_plate(disambiguated)
        display_format = cls.format_plate_display(disambiguated)

        return disambiguated, display_format, is_valid
