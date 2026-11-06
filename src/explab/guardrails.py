"""Data guardrails (frozen, PREREG.md section 9). Integrity only.

G1: exclusion counts on the full exploratory file. Under Amendment A1
the window exclusion count is the problem-exclusion count.
G2/G3: one statistic with two readings. Per eligible test, the log
ratio of impressions per package (question group over non-question
group), pooled with the primary machinery. As a balance check (G2) it
should be near 0 under randomization. As a placebo (G3), impressions
per package is a quantity the headline text cannot cause inside a
randomized test. Computed on the development split only: the locked
split is touched by primary.py alone.
"""

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from .data import DEFAULT_DATA, DEFAULT_SPLIT, apply_exclusions, load_raw, load_split, restrict_to_split, round4
from .label import add_labels
from .primary import pool_dl

RESULTS = Path("results")


def balance_statistic(df_labelled):
    """Pooled log ratio of impressions per package, question vs not."""
    grp = (
        df_labelled.groupby(["clickability_test_id", "is_question"])
        .agg(impressions=("impressions", "sum"), packages=("impressions", "size"))
        .reset_index()
    )
    q = grp[grp["is_question"]].set_index("clickability_test_id")
    nq = grp[~grp["is_question"]].set_index("clickability_test_id")
    common = q.index.intersection(nq.index)
    imp_q = q.loc[common, "impressions"].astype(float)
    imp_nq = nq.loc[common, "impressions"].astype(float)
    per_q = imp_q / q.loc[common, "packages"].astype(float)
    per_nq = imp_nq / nq.loc[common, "packages"].astype(float)
    y = np.log(per_q / per_nq)
    var = 1.0 / imp_q + 1.0 / imp_nq
    pooled = pool_dl(y.to_numpy(), var.to_numpy())
    return {
        "n_tests": pooled["n_tests"],
        "log_ratio_impressions_per_package": round4(pooled["log_or"]),
        "ci95": [round4(pooled["ci95"][0]), round4(pooled["ci95"][1])],
        "tau": round4(pooled["tau"]),
    }


def run(data_path=DEFAULT_DATA, split_path=DEFAULT_SPLIT):
    df = load_raw(data_path)
    kept, counts = apply_exclusions(df)
    split = load_split(split_path)
    dev = add_labels(restrict_to_split(kept, split["development"]))
    bal = balance_statistic(dev)
    out = {
        "g1_exclusion_counts_full_file": counts,
        "g1_note": "Window exclusion count is the problem-exclusion count under Amendment A1.",
        "g2_balance_check_dev": bal,
        "g3_placebo_dev": bal,
        "g3_note": "G2 and G3 are the same statistic under two readings (PREREG section 9).",
    }
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "guardrails.json").write_text(
        json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(out, indent=1, sort_keys=True))
    return out


if __name__ == "__main__":
    run()
