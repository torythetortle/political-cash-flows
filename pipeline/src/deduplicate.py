"""Fuzzy deduplication of vendor names using rapidfuzz."""

import re
from collections import defaultdict

import pandas as pd
from rapidfuzz import fuzz, process
from tqdm import tqdm

from .config import PROCESSED_DIR


def normalize_vendor_name(name: str) -> str:
    """Normalize vendor name for comparison."""
    name = str(name).upper().strip()
    name = re.sub(r'\b(INC|LLC|LTD|CORP|CO|COMPANY|GROUP|SERVICES?)\b\.?', '', name)
    name = re.sub(r'[.,;:\-\'\"()&/]', ' ', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name


def make_block_key(normalized: str) -> str:
    """Create a blocking key from the first significant word."""
    words = normalized.split()
    if not words:
        return ""
    # Use first word (at least 3 chars) as block key
    for w in words:
        if len(w) >= 3:
            return w[:5]
    return words[0][:5] if words[0] else ""


def deduplicate_vendors(df: pd.DataFrame, threshold: int = 85) -> pd.DataFrame:
    """
    Cluster similar vendor names using blocking + fuzzy matching.

    Strategy: group names by blocking key (first word prefix),
    then fuzzy-match only within blocks. This reduces O(n^2) to O(n*k)
    where k is the average block size.
    """
    print("Deduplicating vendor names...")

    unique_names = df["name"].unique().tolist()
    print(f"  {len(unique_names):,} unique vendor names")

    # Normalize and build blocks
    normalized = {name: normalize_vendor_name(name) for name in unique_names}
    blocks: dict[str, list[str]] = defaultdict(list)
    for name in unique_names:
        key = make_block_key(normalized[name])
        blocks[key].append(name)

    print(f"  {len(blocks):,} blocking groups")

    # Sort by frequency for canonical selection
    name_counts = df["name"].value_counts().to_dict()

    # Cluster within each block
    name_map: dict[str, str] = {}
    total_merged = 0

    for block_key, block_names in tqdm(blocks.items(), desc="  Clustering"):
        if len(block_names) == 1:
            name_map[block_names[0]] = block_names[0]
            continue

        # Sort block by frequency
        block_names.sort(key=lambda n: name_counts.get(n, 0), reverse=True)
        block_norms = [normalized[n] for n in block_names]

        assigned: set[int] = set()

        for i, name in enumerate(block_names):
            if i in assigned:
                continue

            cluster = [name]
            assigned.add(i)

            # Compare against remaining in block
            remaining_idxs = [j for j in range(i + 1, len(block_names)) if j not in assigned]
            if remaining_idxs:
                remaining_norms = [block_norms[j] for j in remaining_idxs]
                matches = process.extract(
                    block_norms[i],
                    remaining_norms,
                    scorer=fuzz.token_sort_ratio,
                    limit=30,
                    score_cutoff=threshold,
                )
                for _, score, idx in matches:
                    original_idx = remaining_idxs[idx]
                    cluster.append(block_names[original_idx])
                    assigned.add(original_idx)

            # Canonical = most frequent
            canonical = cluster[0]
            for member in cluster:
                name_map[member] = canonical
            if len(cluster) > 1:
                total_merged += len(cluster) - 1

    # Apply mapping
    df["canonical_name"] = df["name"].map(name_map)
    df["vendor_id"] = df["canonical_name"].factorize()[0]
    df["vendor_id"] = df["vendor_id"].apply(lambda x: f"V{x:05d}")

    n_clusters = len(set(name_map.values()))
    print(f"  Merged {total_merged:,} names into {n_clusters:,} clusters\n")

    out_path = PROCESSED_DIR / "expenditures_deduplicated.parquet"
    df.to_parquet(out_path, index=False)
    print(f"  Saved to {out_path}\n")

    return df
