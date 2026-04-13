"""Aggregate spending data for frontend consumption."""

import pandas as pd

from .config import PROCESSED_DIR


def aggregate_by_state(df: pd.DataFrame) -> dict:
    """Aggregate total spend by state and party."""
    print("Aggregating by state...")

    state_party = df.groupby(["state", "party"])["transaction_amt"].sum().unstack(fill_value=0)

    state_spend = {}
    for state in state_party.index:
        row = state_party.loc[state]
        dem = float(row.get("DEM", 0))
        rep = float(row.get("REP", 0))
        vendor_count = int(df[df["state"] == state]["vendor_id"].nunique())
        state_spend[state] = {
            "dem_spend": dem,
            "rep_spend": rep,
            "total_spend": dem + rep,
            "vendor_count": vendor_count,
        }

    print(f"  {len(state_spend)} states\n")
    return state_spend


def aggregate_top_vendors(df: pd.DataFrame, n: int = 50) -> list[dict]:
    """Get top vendors by total spend with enriched data."""
    print(f"Aggregating top {n} vendors...")

    df_agg = df.copy()
    df_agg["dem_amt"] = df_agg["transaction_amt"].where(df_agg["party"] == "DEM", 0)
    df_agg["rep_amt"] = df_agg["transaction_amt"].where(df_agg["party"] == "REP", 0)

    vendor_agg = df_agg.groupby(["vendor_id", "canonical_name", "city", "state"]).agg(
        total_spend=("transaction_amt", "sum"),
        dem_spend=("dem_amt", "sum"),
        rep_spend=("rep_amt", "sum"),
    ).reset_index()

    vendor_agg = vendor_agg.sort_values("total_spend", ascending=False).head(n)

    result = []
    for _, row in vendor_agg.iterrows():
        total = max(row["total_spend"], 1)

        # Get top purpose category for this vendor
        vendor_rows = df[df["vendor_id"] == row["vendor_id"]]
        purpose_counts = vendor_rows["purpose_category"].value_counts()
        top_purpose = purpose_counts.index[0] if len(purpose_counts) > 0 else "Other"

        # Get cycles this vendor appears in
        cycles = sorted(vendor_rows["cycle"].dropna().unique().tolist())

        result.append({
            "vendor_id": row["vendor_id"],
            "canonical_name": row["canonical_name"],
            "total_spend": float(row["total_spend"]),
            "dem_pct": round(float(row["dem_spend"]) / total * 100, 1),
            "rep_pct": round(float(row["rep_spend"]) / total * 100, 1),
            "cycles": [int(c) for c in cycles],
            "category": top_purpose,
            "city": row["city"],
            "state": row["state"],
        })

    if result:
        print(f"  Top vendor: {result[0]['canonical_name']} ({result[0]['total_spend']:,.0f})\n")
    return result


def aggregate_vendor_cycles(df: pd.DataFrame) -> list[dict]:
    """Build real cycle-over-cycle spend data for repeat vendors."""
    print("Building vendor cycle data...")

    # Get total spend per vendor per cycle
    cycle_spend = df.groupby(["vendor_id", "canonical_name", "cycle", "party"]).agg(
        spend=("transaction_amt", "sum"),
    ).reset_index()

    # Get dominant party per vendor
    vendor_party = df.groupby(["vendor_id", "party"])["transaction_amt"].sum().reset_index()
    dominant = vendor_party.loc[
        vendor_party.groupby("vendor_id")["transaction_amt"].idxmax()
    ][["vendor_id", "party"]].rename(columns={"party": "dominant_party"})

    # Get vendors that appear in multiple cycles
    vendor_cycles = cycle_spend.groupby("vendor_id")["cycle"].nunique().reset_index()
    vendor_cycles.columns = ["vendor_id", "n_cycles"]
    multi_cycle = vendor_cycles[vendor_cycles["n_cycles"] >= 2]["vendor_id"].tolist()

    if not multi_cycle:
        # If no multi-cycle vendors, take top single-cycle vendors
        multi_cycle = df.groupby("vendor_id")["transaction_amt"].sum().nlargest(30).index.tolist()

    # Build output
    vendor_totals = df.groupby(["vendor_id", "canonical_name"])["transaction_amt"].sum().reset_index()
    vendor_totals = vendor_totals[vendor_totals["vendor_id"].isin(multi_cycle)]
    vendor_totals = vendor_totals.merge(dominant, on="vendor_id", how="left")
    vendor_totals = vendor_totals.sort_values("transaction_amt", ascending=False).head(30)

    result = []
    for _, row in vendor_totals.iterrows():
        v_cycles = cycle_spend[cycle_spend["vendor_id"] == row["vendor_id"]]
        cycles_dict = {}
        for _, cr in v_cycles.groupby("cycle")["spend"].sum().items():
            pass
        # Simpler approach
        v_by_cycle = df[df["vendor_id"] == row["vendor_id"]].groupby("cycle")["transaction_amt"].sum()
        cycles_dict = {str(int(k)): float(v) for k, v in v_by_cycle.items()}

        # Top purpose
        v_rows = df[df["vendor_id"] == row["vendor_id"]]
        top_purpose = v_rows["purpose_category"].value_counts().index[0] if len(v_rows) > 0 else "Other"

        result.append({
            "vendor_id": row["vendor_id"],
            "canonical_name": row["canonical_name"],
            "dominant_party": row.get("dominant_party", "DEM"),
            "category": top_purpose,
            "cycles": cycles_dict,
        })

    print(f"  {len(result)} vendors with cycle data\n")
    return result


def aggregate_vendor_details(df: pd.DataFrame) -> dict:
    """Build detailed per-vendor data: monthly timeline, purpose breakdown, top committees."""
    print("Building vendor detail data...")

    # Get top 500 vendors by spend
    top_vendors = df.groupby("vendor_id")["transaction_amt"].sum().nlargest(500).index.tolist()
    vdf = df[df["vendor_id"].isin(top_vendors)]

    details = {}
    for vid in top_vendors:
        v = vdf[vdf["vendor_id"] == vid]

        # Monthly spending timeline
        monthly = v.groupby("month")["transaction_amt"].sum()
        timeline = {str(k): round(float(v)) for k, v in monthly.items() if pd.notna(k)}

        # Purpose breakdown
        purpose = v.groupby("purpose_category")["transaction_amt"].sum().sort_values(ascending=False)
        purpose_breakdown = {str(k): round(float(v)) for k, v in purpose.items()}

        # Top committees that paid this vendor
        committees = v.groupby(["cmte_id", "cmte_nm", "party"]).agg(
            spend=("transaction_amt", "sum")
        ).reset_index().sort_values("spend", ascending=False).head(10)
        top_committees = [
            {
                "name": row["cmte_nm"],
                "party": row["party"],
                "spend": round(float(row["spend"])),
            }
            for _, row in committees.iterrows()
        ]

        # Linked candidates
        cand_spend = v[v["cand_name"].notna()].groupby(
            ["cand_id", "cand_name", "cand_office", "cand_office_st"]
        )["transaction_amt"].sum().reset_index().sort_values("transaction_amt", ascending=False).head(5)
        candidates = [
            {
                "id": row["cand_id"],
                "name": row["cand_name"],
                "office": row["cand_office"],
                "state": row["cand_office_st"],
                "spend": round(float(row["transaction_amt"])),
            }
            for _, row in cand_spend.iterrows()
        ]

        details[vid] = {
            "timeline": timeline,
            "purpose": purpose_breakdown,
            "committees": top_committees,
            "candidates": candidates,
        }

    print(f"  Built details for {len(details)} vendors\n")
    return details
