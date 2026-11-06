"""Generate the development / locked split of exploratory test IDs.

This is pre-registration machinery, not analysis code. It reads ONLY the
clickability_test_id column of the exploratory file. It never reads the
clicks or impressions columns.

Rule (frozen in prereg/PREREG.md section 3):
- Take the sorted unique clickability_test_id values.
- Shuffle them with numpy default_rng(seed 20261106).permutation.
- The first floor(0.2 * N) IDs in the shuffled order are the development
  split. The rest are the locked split.
- Write prereg/split.json with both ID lists (sorted ascending) and the
  SHA-256 of each list serialized as the IDs joined by newline characters
  with a trailing newline, UTF-8 encoded.

Usage: python prereg/make_split.py [path-to-exploratory-csv]
Output: prereg/split.json (deterministic; reruns must be byte-identical).
"""

import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 20261106
DEV_FRACTION = 0.2
DEFAULT_CSV = "data/raw/upworthy-archive-exploratory-packages-03.12.2020.csv"
OUT_PATH = Path(__file__).with_name("split.json")


def list_sha256(ids):
    payload = ("\n".join(str(i) for i in ids) + "\n").encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    csv_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CSV
    ids_series = pd.read_csv(
        csv_path, usecols=["clickability_test_id"], dtype=str
    )["clickability_test_id"]
    unique_sorted = sorted(str(i) for i in ids_series.unique())
    n = len(unique_sorted)
    rng = np.random.default_rng(SEED)
    order = rng.permutation(n)
    shuffled = [unique_sorted[i] for i in order]
    n_dev = math.floor(DEV_FRACTION * n)
    dev = sorted(shuffled[:n_dev])
    locked = sorted(shuffled[n_dev:])
    record = {
        "seed": SEED,
        "rule": "sorted unique clickability_test_id, numpy default_rng(seed).permutation, first floor(0.2*N) shuffled IDs are development, rest locked",
        "data_file": Path(csv_path).name,
        "data_file_sha256": file_sha256(csv_path),
        "n_tests_total": n,
        "n_development": len(dev),
        "n_locked": len(locked),
        "development_ids_sha256": list_sha256(dev),
        "locked_ids_sha256": list_sha256(locked),
        "development_ids": dev,
        "locked_ids": locked,
    }
    OUT_PATH.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"tests total={n} development={len(dev)} locked={len(locked)}")
    print(f"development_ids_sha256={record['development_ids_sha256']}")
    print(f"locked_ids_sha256={record['locked_ids_sha256']}")


if __name__ == "__main__":
    main()
