"""Configuration constants for the FEC data pipeline."""

from pathlib import Path

# Paths
ROOT_DIR = Path(__file__).parent.parent.parent
RAW_DIR = ROOT_DIR / "data" / "raw"
PROCESSED_DIR = ROOT_DIR / "data" / "processed"
EXPORTS_DIR = ROOT_DIR / "data" / "exports"
STATIC_DIR = ROOT_DIR / "web" / "static" / "data"

# FEC bulk data URLs — multi-cycle
FEC_BASE = "https://www.fec.gov/files/bulk-downloads"
FEC_FILES = {
    # 2024
    "operating_expenditures_2024": f"{FEC_BASE}/2024/oppexp24.zip",
    "pac_disbursements_2024": f"{FEC_BASE}/2024/pas224.zip",
    "committee_master_2024": f"{FEC_BASE}/2024/cm24.zip",
    "candidate_master_2024": f"{FEC_BASE}/2024/cn24.zip",
    # 2022
    "operating_expenditures_2022": f"{FEC_BASE}/2022/oppexp22.zip",
    "committee_master_2022": f"{FEC_BASE}/2022/cm22.zip",
    "candidate_master_2022": f"{FEC_BASE}/2022/cn22.zip",
    # 2020
    "operating_expenditures_2020": f"{FEC_BASE}/2020/oppexp20.zip",
    "committee_master_2020": f"{FEC_BASE}/2020/cm20.zip",
    "candidate_master_2020": f"{FEC_BASE}/2020/cn20.zip",
}

CANDIDATE_COLUMNS = [
    "cand_id", "cand_name", "cand_pty_affiliation", "cand_election_yr",
    "cand_office_st", "cand_office", "cand_office_district", "cand_ici",
    "cand_status", "cand_pcc", "cand_st1", "cand_st2",
    "cand_city", "cand_st", "cand_zip",
]

# Purpose text → category mapping
PURPOSE_CATEGORIES = {
    "MEDIA": "Media & Advertising",
    "ADVERTIS": "Media & Advertising",
    "TV": "Media & Advertising",
    "RADIO": "Media & Advertising",
    "DIGITAL AD": "Media & Advertising",
    "ONLINE AD": "Media & Advertising",
    "BROADCAST": "Media & Advertising",
    "DIRECT MAIL": "Direct Mail",
    "MAIL": "Direct Mail",
    "PRINTING": "Direct Mail",
    "POSTAGE": "Direct Mail",
    "CONSULT": "Consulting",
    "STRATEG": "Consulting",
    "POLLING": "Polling & Research",
    "RESEARCH": "Polling & Research",
    "SURVEY": "Polling & Research",
    "DATA": "Data & Analytics",
    "ANALYTICS": "Data & Analytics",
    "VOTER FILE": "Data & Analytics",
    "FUNDRAIS": "Fundraising",
    "DONOR": "Fundraising",
    "CONTRIBUT": "Fundraising",
    "SALARY": "Payroll & Staff",
    "PAYROLL": "Payroll & Staff",
    "STAFF": "Payroll & Staff",
    "TRAVEL": "Travel",
    "AIRFARE": "Travel",
    "LODGING": "Travel",
    "HOTEL": "Travel",
    "EVENT": "Events",
    "CATERING": "Events",
    "VENUE": "Events",
    "LEGAL": "Legal & Compliance",
    "COMPLIANCE": "Legal & Compliance",
    "LAWYER": "Legal & Compliance",
    "ATTORNEY": "Legal & Compliance",
    "SOFTWARE": "Technology",
    "WEBSITE": "Technology",
    "WEB": "Technology",
    "TECH": "Technology",
    "PHONE": "Field & Phones",
    "CANVASS": "Field & Phones",
    "FIELD": "Field & Phones",
    "DOOR": "Field & Phones",
    "RENT": "Overhead",
    "OFFICE": "Overhead",
    "UTILIT": "Overhead",
    "INSURANCE": "Overhead",
    "BANK": "Fees & Processing",
    "CREDIT CARD": "Fees & Processing",
    "MERCHANT": "Fees & Processing",
    "PROCESSING": "Fees & Processing",
    "FEE": "Fees & Processing",
}

# Census Geocoding API
CENSUS_GEOCODER_URL = "https://geocoding.geo.census.gov/geocoder/locations/address"
CENSUS_BATCH_URL = "https://geocoding.geo.census.gov/geocoder/locations/addressbatch"

# Column schemas for FEC pipe-delimited files (no headers)
OPPEXP_COLUMNS = [
    "cmte_id", "amndt_ind", "rpt_yr", "rpt_tp",
    "image_num", "line_num", "form_tp_cd", "sched_tp_cd",
    "name", "city", "state", "zip_code", "transaction_dt",
    "transaction_amt", "election_tp", "purpose",
    "category", "category_desc",
    "memo_cd", "memo_text", "entity_tp", "sub_id",
    "file_num", "tran_id", "back_ref_tran_id", "unused",
]

COMMITTEE_COLUMNS = [
    "cmte_id", "cmte_nm", "tres_nm", "cmte_st1",
    "cmte_st2", "cmte_city", "cmte_st", "cmte_zip",
    "cmte_dsgn", "cmte_tp", "cmte_pty_affiliation",
    "cmte_filing_freq", "org_tp", "connected_org_nm", "cand_id",
]

# Party codes that map to DEM/REP
DEM_CODES = {"DEM", "DFL"}
REP_CODES = {"REP"}

# Focus cities for deep-dive exports
FOCUS_CITIES = {
    "Philadelphia": {"state": "PA", "lat": 39.9526, "lng": -75.1652},
    "Atlanta": {"state": "GA", "lat": 33.7490, "lng": -84.3880},
    "Phoenix": {"state": "AZ", "lat": 33.4484, "lng": -112.0740},
    "Detroit": {"state": "MI", "lat": 42.3314, "lng": -83.0458},
    "Las Vegas": {"state": "NV", "lat": 36.1699, "lng": -115.1398},
    "Milwaukee": {"state": "WI", "lat": 43.0389, "lng": -87.9065},
}
