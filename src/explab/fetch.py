"""Fetch and integrity gate (U4).

Downloads the exploratory file from its OSF endpoint, verifies the
SHA-256 against the OSF-published value recorded in data/README.md,
and reports row and test counts. Counts rows and test IDs only; it
reads no outcome column. The confirmatory file is never requested.
"""

import csv
import hashlib
import json
import urllib.request
from pathlib import Path

URL = "https://osf.io/download/3vqmp/"
FILENAME = "upworthy-archive-exploratory-packages-03.12.2020.csv"
EXPECTED_SHA256 = "8368313b060f4015a0c6fb34e6d788163cee29554144aba9390b14922eb9d8ce"
EXPECTED_SIZE = 14_260_949
DOCUMENTED_PACKAGES = 22_666
DOCUMENTED_TESTS = 4_873

RAW_DIR = Path("data/raw")
RESULTS = Path("results")


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    dest = RAW_DIR / FILENAME
    if not dest.exists():
        req = urllib.request.Request(URL, headers={"User-Agent": "explab-fetch/1.0"})
        with urllib.request.urlopen(req) as resp, open(dest, "wb") as f:
            while True:
                chunk = resp.read(1 << 20)
                if not chunk:
                    break
                f.write(chunk)
    digest = sha256_of(dest)
    test_ids = set()
    rows = 0
    with open(dest, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        id_col = "clickability_test_id"
        for row in reader:
            rows += 1
            test_ids.add(row[id_col])
    out = {
        "file": FILENAME,
        "download_url": URL,
        "size_bytes": dest.stat().st_size,
        "expected_size_bytes": EXPECTED_SIZE,
        "sha256": digest,
        "expected_sha256": EXPECTED_SHA256,
        "sha256_match": digest == EXPECTED_SHA256,
        "packages_rows": rows,
        "documented_packages": DOCUMENTED_PACKAGES,
        "packages_match_documented": rows == DOCUMENTED_PACKAGES,
        "tests": len(test_ids),
        "documented_tests": DOCUMENTED_TESTS,
        "tests_match_documented": len(test_ids) == DOCUMENTED_TESTS,
    }
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "fetch.json").write_text(
        json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(out, indent=1, sort_keys=True))
    if not out["sha256_match"]:
        raise SystemExit("SHA-256 mismatch: refusing to continue")
    return out


if __name__ == "__main__":
    run()
