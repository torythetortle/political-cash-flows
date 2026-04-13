#!/usr/bin/env python3
"""
CLI entrypoint for the FEC data pipeline.

Usage:
    python -m pipeline.src.run_pipeline          # full pipeline
    python -m pipeline.src.run_pipeline --step download
    python -m pipeline.src.run_pipeline --step parse
    python -m pipeline.src.run_pipeline --step deduplicate
    python -m pipeline.src.run_pipeline --step geocode
    python -m pipeline.src.run_pipeline --step export
"""

import sys
import click

# Allow running as `python pipeline/src/run_pipeline.py` or `python -m pipeline.src.run_pipeline`
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent.parent.parent))

from pipeline.src.download import download_all
from pipeline.src.parse import parse_and_merge
from pipeline.src.deduplicate import deduplicate_vendors
from pipeline.src.geocode import geocode_vendors
from pipeline.src.aggregate import aggregate_by_state, aggregate_top_vendors, aggregate_vendor_cycles, aggregate_vendor_details
from pipeline.src.export import export_all
from pipeline.src.config import PROCESSED_DIR

import pandas as pd


@click.command()
@click.option("--step", type=click.Choice(["download", "parse", "deduplicate", "geocode", "aggregate", "export", "all"]), default="all", help="Run a specific pipeline step")
@click.option("--max-geocode", default=2000, help="Max addresses to geocode per run")
@click.option("--skip-download", is_flag=True, help="Skip the download step")
def main(step: str, max_geocode: int, skip_download: bool):
    """Run the FEC data pipeline."""
    print("=" * 60)
    print("  Political Cash Flows — FEC Data Pipeline")
    print("=" * 60 + "\n")

    if step in ("download", "all") and not skip_download:
        download_all()

    if step in ("parse", "all"):
        df = parse_and_merge()
    elif step not in ("download",):
        # Load from saved parquet
        parquet = PROCESSED_DIR / "expenditures_merged.parquet"
        if not parquet.exists():
            print(f"Error: {parquet} not found. Run 'parse' step first.")
            sys.exit(1)
        df = pd.read_parquet(parquet)

    if step in ("deduplicate", "all"):
        df = deduplicate_vendors(df)
    elif step not in ("download", "parse"):
        parquet = PROCESSED_DIR / "expenditures_deduplicated.parquet"
        if parquet.exists():
            df = pd.read_parquet(parquet)

    if step in ("geocode", "all"):
        df = geocode_vendors(df, max_geocode=max_geocode)
    elif step not in ("download", "parse", "deduplicate"):
        parquet = PROCESSED_DIR / "expenditures_geocoded.parquet"
        if parquet.exists():
            df = pd.read_parquet(parquet)

    if step in ("aggregate", "export", "all"):
        state_spend = aggregate_by_state(df)
        top_vendors = aggregate_top_vendors(df)
        vendor_cycles = aggregate_vendor_cycles(df)
        vendor_details = aggregate_vendor_details(df)

    if step in ("export", "all"):
        export_all(df, state_spend, top_vendors, vendor_cycles, vendor_details)

    print("Pipeline complete.")


if __name__ == "__main__":
    main()
