"""Exclusion and split integrity tests."""

import hashlib
import json
from pathlib import Path

import pandas as pd

from explab.data import apply_exclusions

ROOT = Path(__file__).resolve().parent.parent


def _frame(rows):
    return pd.DataFrame(
        rows,
        columns=["clickability_test_id", "created_at", "impressions", "clicks", "headline"],
    )


def test_window_and_zero_impression_exclusions():
    df = _frame(
        [
            ["t_in", "2013-08-01", 100, 2, "A?"],
            ["t_in", "2013-08-01", 100, 1, "B"],
            ["t_out", "2015-02-01", 100, 2, "A?"],
            ["t_out", "2015-02-01", 0, 0, "B"],
            ["t_out", "2015-02-01", 100, 1, "C"],
        ]
    )
    df["created_at"] = pd.to_datetime(df["created_at"])
    kept, counts = apply_exclusions(df)
    assert counts["tests_total"] == 2
    assert counts["tests_dropped_window"] == 1
    assert counts["rows_dropped_zero_impressions"] == 1
    assert set(kept["clickability_test_id"]) == {"t_out"}
    assert counts["rows_kept"] == 2


def test_split_lock_integrity():
    record = json.loads((ROOT / "prereg" / "split.json").read_text(encoding="utf-8"))
    dev = record["development_ids"]
    locked = record["locked_ids"]
    assert len(dev) == 974
    assert len(locked) == 3899
    assert not set(dev) & set(locked)

    def digest(ids):
        payload = ("\n".join(ids) + "\n").encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    assert digest(dev) == record["development_ids_sha256"]
    assert digest(locked) == record["locked_ids_sha256"]
    prereg_hash = (ROOT / "prereg" / "hash.txt").read_text(encoding="utf-8").strip()
    actual = hashlib.sha256((ROOT / "prereg" / "PREREG.md").read_bytes()).hexdigest()
    assert prereg_hash == actual
