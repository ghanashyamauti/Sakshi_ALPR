"""
Indian State & Comprehensive RTO District Mapping Dictionary
Covers all 36 States and Union Territories + Bharat Series.
"""
from typing import Tuple, Optional, Dict

# All 36 Official Indian States & Union Territories
STATE_CODES: Dict[str, str] = {
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

# Detailed Maharashtra (MH) RTOs
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
    "17": "Shrirampur (Ahmednagar North)",
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

# Detailed Delhi (DL) RTOs
DELHI_RTO = {
    "01": "North Delhi (Mall Road)",
    "02": "New Delhi (Tilak Marg)",
    "03": "South Delhi (Sheikh Sarai)",
    "04": "West Delhi 1 (Janakpuri)",
    "05": "North East Delhi (Loni Road)",
    "06": "Central Delhi (Sarai Kale Khan)",
    "07": "East Delhi 1 (Mayur Vihar)",
    "08": "North West Delhi 1 (Wazirpur)",
    "09": "South West Delhi 1 (Palam / Janakpuri)",
    "10": "West Delhi 2 (Raja Garden)",
    "11": "North West Delhi 2 (Rohini)",
    "12": "South West Delhi 2 (Vasant Vihar)",
    "13": "East Delhi 2 (Surajmal Vihar)",
    "14": "South Delhi 2 (Dwarka)",
}

# Detailed Gujarat (GJ) RTOs
GUJARAT_RTO = {
    "01": "Ahmedabad City",
    "02": "Mehsana",
    "03": "Rajkot",
    "04": "Bhavnagar",
    "05": "Surat City",
    "06": "Vadodara City",
    "07": "Kheda (Nadiad)",
    "08": "Banaskantha (Palanpur)",
    "09": "Sabarkantha (Himmatnagar)",
    "10": "Jamnagar",
    "11": "Junagadh",
    "12": "Kutch (Bhuj)",
    "13": "Surendranagar",
    "14": "Amreli",
    "15": "Valsad",
    "16": "Bharuch",
    "17": "Panchmahal (Godhra)",
    "18": "Gandhinagar",
    "19": "Bardoli",
    "20": "Dahod",
    "21": "Navsari",
    "22": "Narmada (Rajpipla)",
    "23": "Anand",
    "24": "Patan",
    "25": "Porbandar",
    "26": "Vyara (Tapi)",
    "27": "Ahmedabad East (Vastral)",
    "28": "Surat Rural (Pal)",
    "29": "Vadodara Rural (Dharampuri)",
}

# Detailed Karnataka (KA) RTOs
KARNATAKA_RTO = {
    "01": "Bangalore Central (Koramangala)",
    "02": "Bangalore West (Rajajinagar)",
    "03": "Bangalore East (Indiranagar)",
    "04": "Bangalore North (Yeshwanthpur)",
    "05": "Bangalore South (Jayanagar)",
    "06": "Tumakuru",
    "07": "Kolar",
    "08": "KGF",
    "09": "Mysuru City (West)",
    "10": "Chamrajnagar",
    "11": "Mandya",
    "12": "Madikeri (Kodagu)",
    "13": "Hassan",
    "14": "Shivamogga",
    "15": "Sagara",
    "16": "Chitradurga",
    "17": "Davangere",
    "18": "Chikkamagaluru",
    "19": "Mangaluru",
    "20": "Udupi",
    "21": "Puttur",
    "22": "Belagavi",
    "25": "Dharwad / Hubballi",
    "41": "Bangalore West (Gnanabharathi)",
    "50": "Bangalore North (Yelahanka)",
    "51": "Bangalore South (Electronics City)",
    "53": "Bangalore East (K.R. Puram)",
}

# Detailed Uttar Pradesh (UP) RTOs
UTTAR_PRADESH_RTO = {
    "14": "Ghaziabad",
    "15": "Meerut",
    "16": "Gautam Buddha Nagar (Noida)",
    "17": "Baghpat",
    "32": "Lucknow",
    "70": "Prayagraj (Allahabad)",
    "78": "Kanpur Nagar",
    "80": "Agra",
    "65": "Varanasi",
    "53": "Gorakhpur",
    "11": "Saharanpur",
    "12": "Muzaffarnagar",
    "13": "Bulandshahr",
    "21": "Moradabad",
    "25": "Bareilly",
    "42": "Ayodhya (Faizabad)",
    "93": "Jhansi",
}

# Detailed Haryana (HR) RTOs
HARYANA_RTO = {
    "01": "Ambala",
    "02": "Jagadhri (Yamunanagar)",
    "03": "Panchkula",
    "05": "Karnal",
    "06": "Panipat",
    "07": "Kurukshetra",
    "08": "Kaithal",
    "10": "Sonipat",
    "12": "Rohtak",
    "20": "Hisar",
    "26": "Gurugram North",
    "51": "Faridabad",
    "55": "Gurugram South",
    "98": "Badshahpur (Gurugram)",
}

STATE_RTO_MAPS = {
    "MH": MAHARASHTRA_RTO,
    "DL": DELHI_RTO,
    "GJ": GUJARAT_RTO,
    "KA": KARNATAKA_RTO,
    "UP": UTTAR_PRADESH_RTO,
    "HR": HARYANA_RTO,
}

def get_rto_details(clean_plate: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Given an alphanumeric license plate (e.g., 'MH17BB1105'),
    returns (state_code, state_name, rto_district).
    """
    if not clean_plate or len(clean_plate) < 2:
        return None, None, None

    # Check for Bharat Series
    if "BH" in clean_plate[:4]:
        return "BH", "Bharat Series (Pan-India)", "Defence / Central Government / All-India"

    state_code = clean_plate[:2].upper()
    state_name = STATE_CODES.get(state_code, f"State ({state_code})")

    # Extract RTO number
    remaining = clean_plate[2:]
    digits = "".join([c for c in remaining if c.isdigit()])
    rto_num = digits[:2].zfill(2) if len(digits) >= 1 else "01"

    rto_district = None
    if state_code in STATE_RTO_MAPS:
        state_map = STATE_RTO_MAPS[state_code]
        rto_district = state_map.get(rto_num, f"{state_name} (RTO-{rto_num})")
    else:
        rto_district = f"{state_name} (RTO-{rto_num})"

    return state_code, state_name, rto_district
