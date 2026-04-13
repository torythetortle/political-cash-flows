"""Parse and merge FEC pipe-delimited flat files."""

import re
from pathlib import Path

import pandas as pd

from .config import (
    RAW_DIR, PROCESSED_DIR,
    OPPEXP_COLUMNS, COMMITTEE_COLUMNS, CANDIDATE_COLUMNS,
    DEM_CODES, REP_CODES, PURPOSE_CATEGORIES,
)


def load_oppexp_for_cycle(cycle: int) -> pd.DataFrame | None:
    """Load operating expenditures for a given cycle."""
    raw_dir = RAW_DIR / f"operating_expenditures_{cycle}"
    if not raw_dir.exists():
        print(f"  Skipping {cycle} (not downloaded)")
        return None

    txt_files = list(raw_dir.glob("*.txt"))
    if not txt_files:
        return None

    print(f"  Parsing {cycle} operating expenditures ({txt_files[0].name})...")
    df = pd.read_csv(
        txt_files[0],
        sep="|",
        header=None,
        names=OPPEXP_COLUMNS,
        encoding="latin-1",
        low_memory=False,
        on_bad_lines="skip",
    )
    df["cycle"] = cycle
    return df


def load_committee_master(cycle: int) -> pd.DataFrame | None:
    """Load committee master for a given cycle."""
    raw_dir = RAW_DIR / f"committee_master_{cycle}"
    if not raw_dir.exists():
        # Fall back to old path (pre-multi-cycle)
        raw_dir = RAW_DIR / "committee_master"
    if not raw_dir.exists():
        return None

    txt_files = list(raw_dir.glob("*.txt"))
    if not txt_files:
        return None

    print(f"  Parsing {cycle} committee master...")
    return pd.read_csv(
        txt_files[0],
        sep="|",
        header=None,
        names=COMMITTEE_COLUMNS,
        encoding="latin-1",
        low_memory=False,
        on_bad_lines="skip",
    )


def load_candidate_master(cycle: int) -> pd.DataFrame | None:
    """Load candidate master for a given cycle."""
    raw_dir = RAW_DIR / f"candidate_master_{cycle}"
    if not raw_dir.exists():
        raw_dir = RAW_DIR / "candidate_master"
    if not raw_dir.exists():
        return None

    txt_files = list(raw_dir.glob("*.txt"))
    if not txt_files:
        return None

    print(f"  Parsing {cycle} candidate master...")
    df = pd.read_csv(
        txt_files[0],
        sep="|",
        header=None,
        names=CANDIDATE_COLUMNS,
        encoding="latin-1",
        low_memory=False,
        on_bad_lines="skip",
    )
    return df


def normalize_party(party_code: str) -> str | None:
    """Map party affiliation codes to DEM/REP or None."""
    if pd.isna(party_code):
        return None
    code = str(party_code).strip().upper()
    if code in DEM_CODES:
        return "DEM"
    if code in REP_CODES:
        return "REP"
    return None


def categorize_purpose(purpose_text: str) -> str:
    """Map free-text purpose to a standard category."""
    if pd.isna(purpose_text):
        return "Other"
    text = str(purpose_text).upper().strip()
    for keyword, category in PURPOSE_CATEGORIES.items():
        if keyword in text:
            return category
    return "Other"


def parse_date(dt_str: str) -> str | None:
    """Parse FEC date format (MM/DD/YYYY) to YYYY-MM."""
    if pd.isna(dt_str):
        return None
    dt = str(dt_str).strip()
    match = re.match(r"(\d{2})/\d{2}/(\d{4})", dt)
    if match:
        return f"{match.group(2)}-{match.group(1)}"
    return None


def parse_and_merge() -> pd.DataFrame:
    """Parse FEC files across cycles, merge with committee + candidate data."""
    print("Parsing FEC data...")

    all_dfs = []
    all_candidates = []

    for cycle in [2020, 2022, 2024]:
        df = load_oppexp_for_cycle(cycle)
        if df is None:
            continue

        cm = load_committee_master(cycle)
        if cm is None:
            # Use 2024 committee master as fallback
            cm = load_committee_master(2024)

        cn = load_candidate_master(cycle)
        if cn is not None:
            all_candidates.append(cn)

        # Ensure cmte_id is string
        df["cmte_id"] = df["cmte_id"].astype(str).str.strip()
        cm["cmte_id"] = cm["cmte_id"].astype(str).str.strip()

        # Merge committee info (party + candidate linkage)
        df = df.merge(
            cm[["cmte_id", "cmte_nm", "cmte_pty_affiliation", "cand_id"]],
            on="cmte_id",
            how="left",
        )

        # Normalize party
        df["party"] = df["cmte_pty_affiliation"].apply(normalize_party)
        df = df[df["party"].notna()].copy()

        # Clean transaction amounts
        df["transaction_amt"] = pd.to_numeric(df["transaction_amt"], errors="coerce")
        df = df[df["transaction_amt"] > 0]

        # Clean vendor name and address
        for col in ["name", "city", "state", "zip_code"]:
            df[col] = df[col].astype(str).str.strip()

        df = df[
            (df["name"] != "nan")
            & (df["city"] != "nan")
            & (df["state"] != "nan")
            & (df["state"].str.len() == 2)
        ]

        # Categorize purpose
        df["purpose_category"] = df["purpose"].apply(categorize_purpose)

        # Parse month
        df["month"] = df["transaction_dt"].apply(parse_date)

        all_dfs.append(df)
        print(f"  {cycle}: {len(df):,} records")

    df = pd.concat(all_dfs, ignore_index=True)

    # Build candidate lookup (combine all cycles)
    if all_candidates:
        candidates = pd.concat(all_candidates, ignore_index=True).drop_duplicates(subset=["cand_id"])
        candidates["cand_id"] = candidates["cand_id"].astype(str).str.strip()
        df["cand_id"] = df["cand_id"].astype(str).str.strip()

        # Merge candidate name and office
        df = df.merge(
            candidates[["cand_id", "cand_name", "cand_office", "cand_office_st", "cand_election_yr"]],
            on="cand_id",
            how="left",
        )
    else:
        df["cand_name"] = None
        df["cand_office"] = None
        df["cand_office_st"] = None
        df["cand_election_yr"] = None

    # Save
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PROCESSED_DIR / "expenditures_merged.parquet"
    df.to_parquet(out_path, index=False)
    print(f"\n  Total: {len(df):,} records across all cycles")
    print(f"  Saved to {out_path}\n")

    return df
