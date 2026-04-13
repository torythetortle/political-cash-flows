"""Export processed data to JSON/GeoJSON for the frontend."""

import json
from pathlib import Path

import pandas as pd

from .config import EXPORTS_DIR, STATIC_DIR


def export_vendor_geojson(df: pd.DataFrame, output_dir: Path) -> None:
    """Export vendor locations as GeoJSON FeatureCollection."""
    geo_df = df[df["lat"].notna() & df["lng"].notna()].copy()

    # Vectorized party split (much faster than apply)
    geo_df["dem_amt"] = geo_df["transaction_amt"].where(geo_df["party"] == "DEM", 0)
    geo_df["rep_amt"] = geo_df["transaction_amt"].where(geo_df["party"] == "REP", 0)

    # Aggregate by vendor identity (not by lat/lng which has jitter)
    vendor_agg = geo_df.groupby(
        ["vendor_id", "canonical_name", "city", "state"]
    ).agg(
        total_spend=("transaction_amt", "sum"),
        dem_spend=("dem_amt", "sum"),
        rep_spend=("rep_amt", "sum"),
        lat=("lat", "first"),
        lng=("lng", "first"),
    ).reset_index()

    # Get top purpose category per vendor
    purpose_top = geo_df.groupby("vendor_id")["purpose_category"].agg(
        lambda x: x.value_counts().index[0] if len(x) > 0 else "Other"
    ).reset_index()
    purpose_top.columns = ["vendor_id", "top_purpose"]
    vendor_agg = vendor_agg.merge(purpose_top, on="vendor_id", how="left")
    vendor_agg["top_purpose"] = vendor_agg["top_purpose"].fillna("Other")

    # Get cycles per vendor
    cycles_per = geo_df.groupby("vendor_id")["cycle"].apply(
        lambda x: sorted(x.dropna().unique().tolist())
    ).reset_index()
    cycles_per.columns = ["vendor_id", "cycles"]
    vendor_agg = vendor_agg.merge(cycles_per, on="vendor_id", how="left")

    # Filter to vendors with meaningful spend (> $1000)
    vendor_agg = vendor_agg[vendor_agg["total_spend"] >= 1000]

    features = []
    for _, row in vendor_agg.iterrows():
        dominant = "DEM" if row["dem_spend"] > row["rep_spend"] else "REP"
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [round(row["lng"], 5), round(row["lat"], 5)],
            },
            "properties": {
                "vendor_id": row["vendor_id"],
                "canonical_name": row["canonical_name"],
                "total_spend": round(float(row["total_spend"])),
                "dem_spend": round(float(row["dem_spend"])),
                "rep_spend": round(float(row["rep_spend"])),
                "dominant_party": dominant,
                "cycles": [int(c) for c in row.get("cycles", [2024])] if isinstance(row.get("cycles"), list) else [2024],
                "category": row.get("top_purpose", "Other"),
                "city": row["city"],
                "state": row["state"],
            },
        })

    geojson = {"type": "FeatureCollection", "features": features}

    out_path = output_dir / "vendors_map.geojson"
    with open(out_path, "w") as f:
        json.dump(geojson, f, separators=(",", ":"))
    print(f"  Wrote {len(features):,} vendor features to {out_path}")


def export_state_spend(state_spend: dict, output_dir: Path) -> None:
    """Export state-level spending as JSON."""
    out_path = output_dir / "state_spend.json"
    with open(out_path, "w") as f:
        json.dump(state_spend, f, indent=2)
    print(f"  Wrote state spend to {out_path}")


def export_top_vendors(top_vendors: list[dict], output_dir: Path) -> None:
    """Export ranked vendor list as JSON."""
    out_path = output_dir / "top_vendors.json"
    with open(out_path, "w") as f:
        json.dump(top_vendors, f, indent=2)
    print(f"  Wrote {len(top_vendors)} top vendors to {out_path}")


def export_vendor_cycles(vendor_cycles: list[dict], output_dir: Path) -> None:
    """Export vendor cycle data as JSON."""
    out_path = output_dir / "vendor_cycles.json"
    with open(out_path, "w") as f:
        json.dump(vendor_cycles, f, indent=2)
    print(f"  Wrote {len(vendor_cycles)} vendor cycle entries to {out_path}")


def export_vendor_details(vendor_details: dict, output_dir: Path) -> None:
    """Export enriched vendor detail data (timeline, purpose, committees)."""
    out_path = output_dir / "vendor_details.json"
    with open(out_path, "w") as f:
        json.dump(vendor_details, f, separators=(",", ":"))
    print(f"  Wrote details for {len(vendor_details)} vendors to {out_path}")


def export_city_deep_dive(df: pd.DataFrame, city: str, state: str, output_dir: Path) -> None:
    """Export filtered GeoJSON for a city deep-dive."""
    city_df = df[(df["city"].str.upper() == city.upper()) & (df["state"] == state)].copy()
    city_df = city_df[city_df["lat"].notna() & city_df["lng"].notna()]

    # Aggregate by vendor
    city_df["dem_amt"] = city_df["transaction_amt"].where(city_df["party"] == "DEM", 0)
    city_df["rep_amt"] = city_df["transaction_amt"].where(city_df["party"] == "REP", 0)

    city_agg = city_df.groupby(["vendor_id", "canonical_name"]).agg(
        total_spend=("transaction_amt", "sum"),
        dem_spend=("dem_amt", "sum"),
        rep_spend=("rep_amt", "sum"),
        lat=("lat", "first"),
        lng=("lng", "first"),
    ).reset_index()
    city_agg = city_agg[city_agg["total_spend"] >= 500]

    features = []
    for _, row in city_agg.iterrows():
        dominant = "DEM" if row["dem_spend"] > row["rep_spend"] else "REP"
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [round(row["lng"], 5), round(row["lat"], 5)],
            },
            "properties": {
                "vendor_id": row["vendor_id"],
                "canonical_name": row["canonical_name"],
                "total_spend": round(float(row["total_spend"])),
                "dominant_party": dominant,
                "city": city,
                "state": state,
            },
        })

    geojson = {"type": "FeatureCollection", "features": features}
    filename = f"{city.lower().replace(' ', '_')}_vendors.geojson"
    out_path = output_dir / filename
    with open(out_path, "w") as f:
        json.dump(geojson, f, separators=(",", ":"))
    print(f"  Wrote {len(features):,} {city} vendor features to {out_path}")


def export_all(
    df: pd.DataFrame,
    state_spend: dict,
    top_vendors: list[dict],
    vendor_cycles: list[dict],
    vendor_details: dict | None = None,
) -> None:
    """Export all data artifacts to both exports/ and web/static/data/."""
    print("Exporting data for frontend...")

    for output_dir in [EXPORTS_DIR, STATIC_DIR]:
        output_dir.mkdir(parents=True, exist_ok=True)

        export_vendor_geojson(df, output_dir)
        export_state_spend(state_spend, output_dir)
        export_top_vendors(top_vendors, output_dir)
        export_vendor_cycles(vendor_cycles, output_dir)
        export_city_deep_dive(df, "Philadelphia", "PA", output_dir)
        if vendor_details:
            export_vendor_details(vendor_details, output_dir)

    print("\nExport complete.\n")
