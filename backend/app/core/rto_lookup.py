"""
Indian State & RTO District Mapping Dictionary
Specialized for accurate regional identification including Maharashtra (MH) districts.
"""
from typing import Tuple, Optional

# Indian State & Union Territory Codes
STATE_CODES = {
    "AN": "Andaman and Nicobar Islands",
    "AP": "Andhra Pradesh",
    "AR": "Arunachal Pradesh",
    "AS": "Assam",
    "BR": "Bihar",
    "CH": "Chandigarh",
    "CG": "Chhattisgarh",
    "DD": "Daman and Diu",
    "DL": "Delhi",
    "DN": "Dadra and Nagar Haveli",
    "GA": "Goa",
    "GJ": "Gujarat",
    "HR": "Haryana",
    "HP": "Himachal Pradesh",
    "JH": "Jharkhand",
    "JK": "Jammu and Kashmir",
    "KA": "Karnataka",
    "KL": "Kerala",
    "LA": "Ladakh",
    "LD": "Lakshadweep",
    "MP": "Madhya Pradesh",
    "MH": "Maharashtra",
    "MN": "Manipur",
    "ML": "Meghalaya",
    "MZ": "Mizoram",
    "NL": "Nagaland",
    "OD": "Odisha",
    "PB": "Punjab",
    "PY": "Puducherry",
    "RJ": "Rajasthan",
    "SK": "Sikkim",
    "TN": "Tamil Nadu",
    "TS": "Telangana",
    "TR": "Tripura",
    "UP": "Uttar Pradesh",
    "UK": "Uttarakhand",
    "UA": "Uttarakhand",
    "WB": "West Bengal",
    "BH": "Bharat Series (Pan-India)",
}

# Detailed Maharashtra (MH) RTO Districts
MAHARASHTRA_RTO = {
    "01": "Mumbai South (Tardeo)",
    "02": "Mumbai West (Andheri)",
    "03": "Mumbai East (Wadala)",
    "04": "Thane",
    "05": "Kalyan",
    "06": "Raigad (Pen)",
    "07": "Sindhudurg",
    "08": "Ratnagiri",
    "09": "Kolhapur",
    "10": "Sangli",
    "11": "Satara",
    "12": "Pune City",
    "13": "Solapur",
    "14": "Pimpri-Chinchwad (PCMC)",
    "15": "Nashik City",
    "16": "Ahmednagar (Parner / Rahuri / Sangamner)",
    "17": "Shrirampur (Ahmednagar)",
    "18": "Dhule",
    "19": "Jalgaon",
    "20": "Chhatrapati Sambhajinagar (Aurangabad)",
    "21": "Jalna",
    "22": "Parbhani",
    "23": "Beed",
    "24": "Latur",
    "25": "Dharashiv (Osmanabad)",
    "26": "Nanded",
    "27": "Amravati",
    "28": "Buldhana",
    "29": "Yavatmal",
    "30": "Akola",
    "31": "Nagpur Urban",
    "32": "Wardha",
    "33": "Gadchiroli",
    "34": "Chandrapur",
    "35": "Gondia",
    "36": "Bhandara",
    "37": "Washim",
    "38": "Hingoli",
    "39": "Nandurbar",
    "40": "Nagpur Rural",
    "41": "Malegaon (Nashik)",
    "42": "Baramati (Pune)",
    "43": "Navi Mumbai (Vashi)",
    "44": "Ambejogai (Beed)",
    "45": "Akluj (Solapur)",
    "46": "Panvel (Navi Mumbai / Raigad)",
    "47": "Mumbai North (Borivali)",
    "48": "Vasai-Virar (Palghar)",
    "49": "Nagpur East",
    "50": "Karad (Satara)",
}

def get_rto_details(clean_plate: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Given a clean alphanumeric license plate (e.g., 'MH16AB1234' or 'DL01CA1111'),
    returns (state_code, state_name, rto_district).
    """
    if not clean_plate or len(clean_plate) < 2:
        return None, None, None

    # Check for Bharat Series
    if "BH" in clean_plate[:4]:
        return "BH", "Bharat Series (Pan-India)", "Defence / Central Government / All-India"

    state_code = clean_plate[:2].upper()
    state_name = STATE_CODES.get(state_code, "Other / Unknown State")

    rto_district = None
    if state_code == "MH":
        remaining = clean_plate[2:]
        digits = "".join([c for c in remaining if c.isdigit()])
        if len(digits) >= 2:
            rto_num = digits[:2].zfill(2)
            rto_district = MAHARASHTRA_RTO.get(rto_num, f"Maharashtra RTO ({rto_num})")
        elif len(digits) == 1:
            rto_num = digits[:1].zfill(2)
            rto_district = MAHARASHTRA_RTO.get(rto_num, f"Maharashtra RTO ({rto_num})")
        else:
            rto_district = "Maharashtra (RTO Unspecified)"
    else:
        remaining = clean_plate[2:]
        digits = "".join([c for c in remaining if c.isdigit()])
        if digits:
            rto_district = f"{state_name} (RTO-{digits[:2]})"
        else:
            rto_district = state_name

    return state_code, state_name, rto_district

