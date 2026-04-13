"""Geocode vendor locations using zip code centroids."""

import csv
import io
import json
from pathlib import Path

import httpx
import pandas as pd
from tqdm import tqdm

from .config import PROCESSED_DIR


ZIP_CACHE_PATH = PROCESSED_DIR / "zip_centroids.json"
ZIP_DATA_URL = "https://gist.githubusercontent.com/erichurst/7882666/raw/5bdc46db47d9515269ab12ed6fb2850377fd869e/US%20Zip%20Codes%20from%202013%20Government%20Data"


def download_zip_centroids() -> dict[str, list[float]]:
    """Download and parse zip code centroid data."""
    if ZIP_CACHE_PATH.exists():
        with open(ZIP_CACHE_PATH) as f:
            return json.load(f)

    print("  Downloading zip code centroid database...")
    r = httpx.get(ZIP_DATA_URL, timeout=30, follow_redirects=True)
    r.raise_for_status()

    centroids: dict[str, list[float]] = {}
    for line in r.text.strip().split("\n"):
        line = line.strip()
        if not line or line.startswith("ZIP"):
            continue
        parts = line.split(",")
        if len(parts) >= 3:
            zipcode = parts[0].strip()
            try:
                lat = float(parts[1].strip())
                lng = float(parts[2].strip())
                centroids[zipcode] = [lat, lng]
            except ValueError:
                continue

    ZIP_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(ZIP_CACHE_PATH, "w") as f:
        json.dump(centroids, f)

    print(f"  Loaded {len(centroids):,} zip code centroids")
    return centroids


def geocode_vendors(df: pd.DataFrame, max_geocode: int = 2000) -> pd.DataFrame:
    """
    Geocode vendor locations using zip code centroids.
    This is fast (no API calls) and provides city-level accuracy.
    """
    print("Geocoding vendor locations via zip codes...")

    centroids = download_zip_centroids()

    # Normalize zip codes to 5 digits
    df["zip5"] = df["zip_code"].astype(str).str.strip().str[:5].str.zfill(5)

    # Look up coordinates
    df["lat"] = df["zip5"].map(lambda z: centroids.get(z, [None, None])[0])
    df["lng"] = df["zip5"].map(lambda z: centroids.get(z, [None, None])[1])

    # Add circular jitter per unique vendor to prevent grid artifacts
    import numpy as np
    np.random.seed(42)
    mask = df["lat"].notna()
    n = mask.sum()
    jitter_scale = 0.004  # ~400m radius
    # Polar coordinates for circular distribution
    angles = np.random.uniform(0, 2 * np.pi, n)
    radii = jitter_scale * np.sqrt(np.random.uniform(0, 1, n))
    df.loc[mask, "lat"] = df.loc[mask, "lat"] + radii * np.cos(angles)
    df.loc[mask, "lng"] = df.loc[mask, "lng"] + radii * np.sin(angles)

    df = df.drop(columns=["zip5"])

    geocoded_count = df["lat"].notna().sum()
    pct = geocoded_count / len(df) * 100 if len(df) > 0 else 0
    print(f"  {geocoded_count:,} / {len(df):,} records have coordinates ({pct:.0f}%)\n")

    out_path = PROCESSED_DIR / "expenditures_geocoded.parquet"
    df.to_parquet(out_path, index=False)
    print(f"  Saved to {out_path}\n")

    return df
