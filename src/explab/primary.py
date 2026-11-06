"""Primary analysis: within-test pooled log odds ratio (frozen plan).

Plan: prereg/PREREG.md section 6. Per test, clicks and impressions are
summed by label group into one 2 by 2 table. Per-test log odds ratios
(0.5 continuity correction on all four cells when any cell is 0) are
pooled with a DerSimonian and Laird random-effects meta-analysis.
The verdict rule, including the 190-test floor, is frozen.

This is the only script that ever analyses the locked split.
"""

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from .data import (
    DEFAULT_DATA,
    DEFAULT_SPLIT,
    apply_exclusions,
    load_raw,
    load_split,
    restrict_to_split,
    round4,
)
from .label import add_labels

Z95 = 1.959964
Z90 = 1.644854
LOG_095 = math.log(0.95)
LOG_105 = math.log(1.05)
LOG_090 = math.log(0.90)
LOG_110 = math.log(1.10)
N_FLOOR = 190

RESULTS = Path("results")


def per_test_table(df, id_col="clickability_test_id"):
    """df: labelled package rows (exclusions applied).
    Returns a DataFrame with one row per eligible test and its 2 by 2
    counts, plus a count of tests dropped by the negative-nonclicks
    integrity guard. id_col lets the causal bootstrap treat each
    resampled cluster as its own test."""
    grouped = (
        df.groupby([id_col, "is_question"])
        .agg(clicks=("clicks", "sum"), impressions=("impressions", "sum"))
        .reset_index()
    )
    q = grouped[grouped["is_question"]].set_index(id_col)
    nq = grouped[~grouped["is_question"]].set_index(id_col)
    common = q.index.intersection(nq.index)
    table = pd.DataFrame(
        {
            "clicks_q": q.loc[common, "clicks"].astype(float),
            "impressions_q": q.loc[common, "impressions"].astype(float),
            "clicks_nq": nq.loc[common, "clicks"].astype(float),
            "impressions_nq": nq.loc[common, "impressions"].astype(float),
        }
    )
    table["nonclicks_q"] = table["impressions_q"] - table["clicks_q"]
    table["nonclicks_nq"] = table["impressions_nq"] - table["clicks_nq"]
    bad = (table["nonclicks_q"] < 0) | (table["nonclicks_nq"] < 0)
    n_bad = int(bad.sum())
    table = table[~bad]
    return table, n_bad


def log_or_per_test(table):
    """Add logor and var columns; apply the 0.5 correction per test."""
    t = table.copy()
    cells = ["clicks_q", "nonclicks_q", "clicks_nq", "nonclicks_nq"]
    zero = (t[cells] == 0).any(axis=1)
    t["continuity_corrected"] = zero
    for c in cells:
        t[c] = t[c] + np.where(zero, 0.5, 0.0)
    t["logor"] = np.log(
        (t["clicks_q"] * t["nonclicks_nq"]) / (t["nonclicks_q"] * t["clicks_nq"])
    )
    t["var"] = (
        1 / t["clicks_q"]
        + 1 / t["nonclicks_q"]
        + 1 / t["clicks_nq"]
        + 1 / t["nonclicks_nq"]
    )
    return t


def pool_dl(logors, variances):
    """DerSimonian and Laird random-effects pooling."""
    y = np.asarray(logors, dtype=float)
    v = np.asarray(variances, dtype=float)
    k = len(y)
    w = 1.0 / v
    y_fe = float(np.sum(w * y) / np.sum(w))
    q_stat = float(np.sum(w * (y - y_fe) ** 2))
    dfree = k - 1
    c = float(np.sum(w) - np.sum(w**2) / np.sum(w))
    tau2 = max(0.0, (q_stat - dfree) / c) if c > 0 else 0.0
    w_re = 1.0 / (v + tau2)
    est = float(np.sum(w_re * y) / np.sum(w_re))
    se = float(math.sqrt(1.0 / np.sum(w_re)))
    i2 = max(0.0, (q_stat - dfree) / q_stat) * 100 if q_stat > 0 else 0.0
    return {
        "n_tests": int(k),
        "log_or": est,
        "se": se,
        "ci95": (est - Z95 * se, est + Z95 * se),
        "ci90": (est - Z90 * se, est + Z90 * se),
        "tau": math.sqrt(tau2),
        "tau2": tau2,
        "i2_percent": i2,
        "q_stat": q_stat,
    }


def verdict_rule(n_tests, ci95, ci90):
    """The frozen verdict rule of PREREG.md section 6, in order."""
    lo95, hi95 = ci95
    lo90, hi90 = ci90
    if n_tests < N_FLOOR:
        if hi95 < LOG_090 or lo95 > LOG_110:
            return "CONFIRMED", "floor_cap_large_effect"
        return "INCONCLUSIVE", "floor_cap_below_190_tests"
    if lo95 > 0 or hi95 < 0:
        return "CONFIRMED", "ci95_excludes_0"
    if lo90 > LOG_095 and hi90 < LOG_105:
        return "REFUTED", "ci90_inside_sesoi_band"
    return "INCONCLUSIVE", "neither_rule_fired"


def analyse(df_labelled, id_col="clickability_test_id"):
    """Full primary estimator on labelled, exclusion-applied rows."""
    table, n_bad = per_test_table(df_labelled, id_col=id_col)
    t = log_or_per_test(table)
    pooled = pool_dl(t["logor"].to_numpy(), t["var"].to_numpy())
    verdict, branch = verdict_rule(pooled["n_tests"], pooled["ci95"], pooled["ci90"])
    out = {
        "n_tests": pooled["n_tests"],
        "tests_dropped_negative_nonclicks": n_bad,
        "tests_continuity_corrected": int(t["continuity_corrected"].sum()),
        "log_or": round4(pooled["log_or"]),
        "odds_ratio": round4(math.exp(pooled["log_or"])),
        "se": round4(pooled["se"]),
        "ci95_log_or": [round4(pooled["ci95"][0]), round4(pooled["ci95"][1])],
        "ci90_log_or": [round4(pooled["ci90"][0]), round4(pooled["ci90"][1])],
        "ci95_odds_ratio": [
            round4(math.exp(pooled["ci95"][0])),
            round4(math.exp(pooled["ci95"][1])),
        ],
        "tau": round4(pooled["tau"]),
        "tau2": round4(pooled["tau2"]),
        "i2_percent": round4(pooled["i2_percent"]),
        "verdict": verdict,
        "verdict_branch": branch,
    }
    return out, t


def run(split_name, data_path=DEFAULT_DATA, split_path=DEFAULT_SPLIT):
    if split_name not in ("dev", "locked"):
        raise ValueError("split_name must be 'dev' or 'locked'")
    df = load_raw(data_path)
    kept, counts = apply_exclusions(df)
    split = load_split(split_path)
    key = "development" if split_name == "dev" else "locked"
    part = add_labels(restrict_to_split(kept, split[key]))
    out, per_test = analyse(part)
    out = {"split": split_name, "exclusion_counts_full_file": counts, **out}
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / f"primary_{split_name}.json").write_text(
        json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8"
    )
    per_test_out = per_test.reset_index()[
        [
            "clickability_test_id",
            "clicks_q",
            "impressions_q",
            "clicks_nq",
            "impressions_nq",
            "logor",
            "var",
            "continuity_corrected",
        ]
    ].copy()
    for col in ("logor", "var"):
        per_test_out[col] = per_test_out[col].round(6)
    per_test_out.to_csv(RESULTS / f"per_test_{split_name}.csv", index=False)
    print(json.dumps(out, indent=1, sort_keys=True))
    return out


if __name__ == "__main__":
    import sys

    name = sys.argv[1] if len(sys.argv) > 1 else "dev"
    if name not in ("dev", "locked"):
        raise SystemExit("usage: python -m explab.primary [dev|locked]")
    run(name)
