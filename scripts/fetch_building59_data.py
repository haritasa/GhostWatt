#!/usr/bin/env python3
"""Download the public Building 59 dataset into GhostWatt's default data path.

The Dryad archive contains 2.3+ GB uncompressed. By default this script extracts
only the four CSVs GhostWatt currently uses. Pass --full to extract all archive
members after download.
"""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

DRYAD_DOWNLOAD_URL = "https://datadryad.org/api/v2/datasets/doi%3A10.7941%2FD1N33Q/download"
ARCHIVE_DATA_DIR = "Bldg59_clean data"
REQUIRED_FILES = ("ele.csv", "occ.csv", "wifi.csv", "site_weather.csv")
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DESTINATION = PROJECT_ROOT / "data" / "raw" / "Building_59" / ARCHIVE_DATA_DIR


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download and prepare the public Building 59 data for GhostWatt.")
    parser.add_argument("--destination", type=Path, default=DEFAULT_DESTINATION, help=f"Data destination (default: {DEFAULT_DESTINATION})")
    parser.add_argument("--archive", type=Path, help="Use an already-downloaded Building_59.zip instead of downloading it.")
    parser.add_argument("--full", action="store_true", help="Extract all data files instead of only GhostWatt's four required CSVs.")
    parser.add_argument("--force", action="store_true", help="Replace an existing destination after confirmation by this explicit flag.")
    return parser.parse_args()


def download_archive(destination: Path) -> None:
    print(f"Downloading public Building 59 archive from Dryad to {destination}…")
    request = urllib.request.Request(DRYAD_DOWNLOAD_URL, headers={"User-Agent": "GhostWatt dataset setup"})
    with urllib.request.urlopen(request, timeout=60) as response, destination.open("wb") as output:
        total = response.headers.get("Content-Length")
        written = 0
        while chunk := response.read(1024 * 1024):
            output.write(chunk)
            written += len(chunk)
            if total:
                print(f"\rDownloaded {written / 1024 / 1024:.0f} MB of {int(total) / 1024 / 1024:.0f} MB", end="", flush=True)
    print()


def extract_archive(archive: Path, destination: Path, full: bool) -> None:
    with zipfile.ZipFile(archive) as zip_file:
        members = zip_file.infolist()
        required_members = {f"{ARCHIVE_DATA_DIR}/{name}" for name in REQUIRED_FILES}
        archive_names = {member.filename for member in members}
        missing = required_members.difference(archive_names)
        if missing:
            raise RuntimeError(f"Archive is missing required files: {', '.join(sorted(missing))}")
        selected = members if full else [member for member in members if member.filename in required_members]
        with tempfile.TemporaryDirectory(prefix="ghostwatt-building59-") as temporary:
            staging = Path(temporary)
            for member in selected:
                target = staging / member.filename
                # Never allow a malicious archive member to write outside staging.
                if not target.resolve().is_relative_to(staging.resolve()):
                    raise RuntimeError(f"Unsafe archive member: {member.filename}")
                if member.is_dir():
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                with zip_file.open(member) as source, target.open("wb") as output:
                    shutil.copyfileobj(source, output)
            extracted_dir = staging / ARCHIVE_DATA_DIR
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(extracted_dir), str(destination))


def validate(destination: Path) -> None:
    missing = [name for name in REQUIRED_FILES if not (destination / name).is_file()]
    if missing:
        raise RuntimeError(f"Setup finished without required files: {', '.join(missing)}")


def main() -> int:
    args = parse_args()
    destination = args.destination.expanduser().resolve()
    if destination.exists():
        if not args.force:
            print(f"Destination already exists: {destination}\nUse --force to replace it.", file=sys.stderr)
            return 2
        shutil.rmtree(destination)

    temporary_archive: Path | None = None
    try:
        if args.archive:
            archive = args.archive.expanduser().resolve()
            if not archive.is_file():
                raise RuntimeError(f"Archive not found: {archive}")
        else:
            temporary_dir = Path(tempfile.mkdtemp(prefix="ghostwatt-download-"))
            temporary_archive = temporary_dir / "Building_59.zip"
            download_archive(temporary_archive)
            archive = temporary_archive
        extract_archive(archive, destination, args.full)
        validate(destination)
    except (OSError, RuntimeError, urllib.error.URLError, zipfile.BadZipFile) as error:
        print(f"Dataset setup failed: {error}", file=sys.stderr)
        if destination.exists():
            shutil.rmtree(destination)
        return 1
    finally:
        if temporary_archive:
            shutil.rmtree(temporary_archive.parent, ignore_errors=True)

    print(f"Building 59 data is ready at:\n  {destination}")
    print("Start GhostWatt and use Import with a blank path, or paste this path into the Import dialog.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
