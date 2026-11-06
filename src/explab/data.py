"""Data loading, frozen exclusions, and split membership.

Exclusions are frozen in prereg/PREREG.md section 7, as amended by
Amendment A1:
- E1/E2: tests whose first package was created in the window
  2013-06-25 to 2014-01-10 are dropped (the archive team's problem
  window; Author Correction, DOI 10.1038/s41597-024-03600-w).
- E3: rows with impressions equal to 0 are dropped before aggregation.
"""

import json
from pathlib import Path

import pandas as pd

WINDOW_START = pd.Timestamp("2013-06-25")
WINDOW_END = pd.Timestamp("2014-01-10")

DEFAULT_DATA = "data/raw/upworthy-archive-exploratory-packages-03.12.2020.csv"
DEFAULT_SPLIT = "prereg/split.json"


def load_raw(path=DEFAULT_DATA):
    df = pd.read_csv(path, dtype={"clickability_test_id": str})
    df["created_at"] = pd.to_datetime(df["created_at"])
    return df


def test_dates(df):
    """First package creation date per test (E2 test date)."""
    return df.groupby("clickability_test_id")["created_at"].min()


def apply_exclusions(df):
    """Return (kept_df, counts). Counts are integrity facts, not results."""
    counts = {
        "rows_total": int(len(df)),
        "tests_total": int(df["clickability_test_id"].nunique()),
    }
    first_date = test_dates(df)
    window_tests = set(
        first_date[(first_date >= WINDOW_START) & (first_date <= WINDOW_END)].index
    )
    counts["tests_dropped_window"] = int(len(window_tests))
    in_window = df["clickability_test_id"].isin(window_tests)
    counts["rows_dropped_window"] = int(in_window.sum())
    kept = df[~in_window]
    zero = kept["impressions"] == 0
    counts["rows_dropped_zero_impressions"] = int(zero.sum())
    kept = kept[~zero]
    counts["rows_kept"] = int(len(kept))
    counts["tests_kept"] = int(kept["clickability_test_id"].nunique())
    return kept, counts


def load_split(path=DEFAULT_SPLIT):
    record = json.loads(Path(path).read_text(encoding="utf-8"))
    return {
        "development": set(record["development_ids"]),
        "locked": set(record["locked_ids"]),
        "record": record,
    }


def restrict_to_split(df, split_ids):
    return df[df["clickability_test_id"].isin(split_ids)]


def round4(x):
    return round(float(x), 4)
