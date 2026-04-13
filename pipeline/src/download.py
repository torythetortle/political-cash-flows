"""Download FEC bulk data files."""

import zipfile
import io
from pathlib import Path

import httpx
from tqdm import tqdm

from .config import FEC_FILES, RAW_DIR


def download_file(url: str, dest_dir: Path, skip_if_exists: bool = True) -> Path:
    """Download and extract a zip file from the FEC."""
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Check if already downloaded
    if skip_if_exists and any(dest_dir.iterdir()):
        print(f"  Skipping {dest_dir.name} (already exists)")
        return dest_dir

    print(f"  Downloading {url}...")
    with httpx.Client(follow_redirects=True, timeout=120) as client:
        with client.stream("GET", url) as response:
            response.raise_for_status()
            total = int(response.headers.get("content-length", 0))
            chunks = []
            with tqdm(total=total, unit="B", unit_scale=True, desc=dest_dir.name) as pbar:
                for chunk in response.iter_bytes(chunk_size=8192):
                    chunks.append(chunk)
                    pbar.update(len(chunk))

    data = b"".join(chunks)
    z = zipfile.ZipFile(io.BytesIO(data))
    z.extractall(dest_dir)
    print(f"  Extracted to {dest_dir}")
    return dest_dir


def download_all(skip_if_exists: bool = True) -> None:
    """Download all FEC bulk data files."""
    print("Downloading FEC bulk data files...")
    for name, url in FEC_FILES.items():
        dest = RAW_DIR / name
        try:
            download_file(url, dest, skip_if_exists)
        except httpx.HTTPStatusError as e:
            print(f"  Warning: {name} failed ({e.response.status_code}), skipping")
        except Exception as e:
            print(f"  Warning: {name} failed ({e}), skipping")
    print("All downloads complete.\n")
