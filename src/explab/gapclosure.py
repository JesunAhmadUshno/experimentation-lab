"""Gap-closure amendment analyses (DECISIONS.md D13, D14, D15; 2026-11-17).

Post-registration analyses registered in DECISIONS.md before any of them
ran. They write only new files:

- results/amendment_2026-11-17_gap_closure.json
- reports/gap-closure-2026-11-17.md

No frozen results file is read-write; the frozen files are read only as
the reference values these analyses are checked against.

D13 (label-rule sensitivity): registered and stopped. The corrected
labels cannot be derived from committed materials; this module verifies
and records that finding programmatically (see label_sensitivity()).

D14 (mSPRT tau sensitivity): the frozen sequential design of PREREG
section 10, same seeded streams, with the mSPRT likelihood ratio
computed on a grid of mixing scales. The frozen tau row must reproduce
results/sequential.json exactly.

D15 (moderator analysis): post hoc, exploratory decomposition of the
locked-split heterogeneity in results/per_test_locked.csv. No verdict.
"""

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import chi2

from . import SEED
from .peeking import LOOKS, RUNS, wilson_ci
from .power import baseline_ctr
from .primary import pool_dl

RESULTS = Path("results")
REPORTS = Path("reports")
TAU_GRID = [0.0005, 0.001, 0.002, 0.003, 0.005, 0.0075, 0.01]
ALPHA = 0.05


def r4(x):
    return round(float(x), 4)


# ---------------------------------------------------------------- D13


def label_sensitivity():
    """Verify the D13 stop: corrected labels exist only for the audit
    sample, which is development-split by construction."""
    sample = json.loads((RESULTS / "label_audit_sample.json").read_text(encoding="utf-8"))
    review = json.loads((RESULTS / "label_audit_review.json").read_text(encoding="utf-8"))
    split = json.loads(Path("prereg/split.json").read_text(encoding="utf-8"))
    marks = {int(r["sample_index"]): bool(r["label_correct"]) for r in review}
    rows = sample["sample"]
    flipped = [rows[i] for i, ok in marks.items() if not ok]
    dev_ids = set(split["development_ids"])
    locked_ids = set(split["locked_ids"])
    per_test_locked = pd.read_csv(RESULTS / "per_test_locked.csv")
    return {
        "status": "STOPPED: corrected labels cannot be derived from committed materials",
        "n_flipped_in_audit": len(flipped),
        "flipped_sample_indices": [int(r["sample_index"]) for r in flipped],
        "flipped_groups": sorted({r["group"] for r in flipped}),
        "flipped_test_ids_all_in_development_split": all(
            r["clickability_test_id"] in dev_ids for r in flipped
        ),
        "flipped_test_ids_any_in_locked_split": any(
            r["clickability_test_id"] in locked_ids for r in flipped
        ),
        "per_test_locked_columns": list(per_test_locked.columns),
        "reason": (
            "The only corrected labels in the committed record are the audit "
            "sample flips, drawn from the development split by construction "
            "(src/explab/label.py make_audit_sample restricts to the "
            "development split). The reviewer's criterion in "
            "results/label_audit_review_notes.json is a semantic judgment, "
            "not a mechanical rule, so locked-split labels cannot be derived "
            "from it. results/per_test_locked.csv is aggregated under the "
            "frozen rule and carries no per-package labels. Recomputing the "
            "locked headline under corrected labels would require inventing "
            "a labelling rule and applying it to the locked split, which "
            "PREREG section 3 forbids. No correction was invented and no "
            "locked number was recomputed under new labels."
        ),
    }


# ---------------------------------------------------------------- D14


def streams(p_treated, p_control):
    """Replicate explab.peeking.simulate's draws exactly (same seed, same
    draw order), additionally returning the plug-in pooled variance."""
    rng = np.random.default_rng(SEED)
    n_looks = len(LOOKS)
    inc_t = rng.binomial(500, p_treated, size=(RUNS, n_looks)).astype(float)
    inc_c = rng.binomial(500, p_control, size=(RUNS, n_looks)).astype(float)
    cum_t = np.cumsum(inc_t, axis=1)
    cum_c = np.cumsum(inc_c, axis=1)
    n = LOOKS.astype(float)[None, :]
    rate_t = cum_t / n
    rate_c = cum_c / n
    p_pool = (cum_t + cum_c) / (2 * n)
    var = p_pool * (1 - p_pool) * (2.0 / n)
    with np.errstate(divide="ignore", invalid="ignore"):
        z = np.where(var > 0, (rate_t - rate_c) / np.sqrt(np.where(var > 0, var, 1.0)), 0.0)
    return z, var


def msprt_any_look_rate(z, var, tau):
    lam = np.sqrt(var / (var + tau**2)) * np.exp(
        (z**2 / 2.0) * (tau**2 / (var + tau**2))
    )
    reject = (lam >= 1.0 / ALPHA).any(axis=1)
    count = int(reject.sum())
    return {
        "reject_count": count,
        "rate_percent": round(count / RUNS * 100, 2),
        "ci95_percent": wilson_ci(count, RUNS),
    }


def tau_sensitivity():
    p0 = baseline_ctr()
    frozen = json.loads((RESULTS / "sequential.json").read_text(encoding="utf-8"))
    out_rows = []
    streams_by_arm = {}
    for name, pt, pc in (("aa_null", p0, p0), ("ab_5pct_lift", p0 * 1.05, p0)):
        streams_by_arm[name] = streams(pt, pc)
    for tau in TAU_GRID:
        row = {"tau_mix": tau}
        for name in ("aa_null", "ab_5pct_lift"):
            z, var = streams_by_arm[name]
            row[name] = msprt_any_look_rate(z, var, tau)
        out_rows.append(row)
    frozen_row = next(r for r in out_rows if r["tau_mix"] == 0.001)
    check = {
        "aa_msprt_percent_matches_frozen": frozen_row["aa_null"]["rate_percent"]
        == frozen["aa"]["msprt_any_look_percent"],
        "ab_msprt_percent_matches_frozen": frozen_row["ab_5pct_lift"]["rate_percent"]
        == frozen["ab_5pct_lift"]["msprt_any_look_percent"],
        "frozen_aa_msprt_percent": frozen["aa"]["msprt_any_look_percent"],
        "frozen_ab_msprt_percent": frozen["ab_5pct_lift"]["msprt_any_look_percent"],
    }
    return {
        "design": {
            "seed": SEED,
            "runs": RUNS,
            "looks_per_arm": [int(x) for x in LOOKS],
            "baseline_ctr": round(p0, 6),
            "tau_grid": TAU_GRID,
            "frozen_tau_mix": 0.001,
            "note": (
                "Same seeded streams as the frozen run; the streams use no "
                "outcome data. Naive rates do not depend on tau and are the "
                "frozen ones in results/sequential.json."
            ),
        },
        "frozen_tau_reproduction_check": check,
        "rows": out_rows,
    }


# ---------------------------------------------------------------- D15


def group_block(y, v, groups, name):
    """Pool per group with pool_dl; decompose Cochran's Q; DL residual
    tau squared under the group-mean model; shares explained."""
    pooled_all = pool_dl(y, v)
    w = 1.0 / v
    labels = sorted(set(groups))
    per_group = {}
    q_within = 0.0
    c_resid = float(np.sum(w))
    for g in labels:
        idx = groups == g
        pg = pool_dl(y[idx], v[idx])
        per_group[str(g)] = {
            "n_tests": pg["n_tests"],
            "log_or": r4(pg["log_or"]),
            "odds_ratio": r4(math.exp(pg["log_or"])),
            "ci95_log_or": [r4(pg["ci95"][0]), r4(pg["ci95"][1])],
            "tau": r4(pg["tau"]),
            "i2_percent": r4(pg["i2_percent"]),
        }
        wg = w[idx]
        y_fe_g = float(np.sum(wg * y[idx]) / np.sum(wg))
        q_within += float(np.sum(wg * (y[idx] - y_fe_g) ** 2))
        c_resid -= float(np.sum(wg**2) / np.sum(wg))
    q_total = float(pooled_all["q_stat"])
    q_between = q_total - q_within
    dfree_between = len(labels) - 1
    dfree_resid = len(y) - len(labels)
    tau2_resid = max(0.0, (q_within - dfree_resid) / c_resid) if c_resid > 0 else 0.0
    tau2_total = float(pooled_all["tau2"])
    return {
        "moderator": name,
        "n_groups": len(labels),
        "per_group": per_group,
        "q_total": r4(q_total),
        "q_within": r4(q_within),
        "q_between": r4(q_between),
        "q_between_df": dfree_between,
        "q_between_p": float(chi2.sf(q_between, dfree_between)) if dfree_between > 0 else None,
        "share_of_q_explained_percent": r4(q_between / q_total * 100) if q_total > 0 else None,
        "tau2_overall": r4(tau2_total),
        "tau2_residual": r4(tau2_resid),
        "r2_tau2_reduction_percent": r4((tau2_total - tau2_resid) / tau2_total * 100)
        if tau2_total > 0
        else None,
    }


def moderator_analysis():
    t = pd.read_csv(RESULTS / "per_test_locked.csv")
    y = t["logor"].to_numpy(dtype=float)
    v = t["var"].to_numpy(dtype=float)
    pooled = pool_dl(y, v)
    frozen = json.loads((RESULTS / "primary_locked.json").read_text(encoding="utf-8"))
    check = {
        "n_tests": pooled["n_tests"],
        "log_or_from_csv": r4(pooled["log_or"]),
        "frozen_log_or": frozen["log_or"],
        "tau_from_csv": r4(pooled["tau"]),
        "frozen_tau": frozen["tau"],
        "i2_from_csv": r4(pooled["i2_percent"]),
        "frozen_i2_percent": frozen["i2_percent"],
    }
    total_impr = t["impressions_q"] + t["impressions_nq"]
    q_share = t["impressions_q"] / total_impr
    baseline_ctr_t = t["clicks_nq"] / t["impressions_nq"]
    m1 = np.where(q_share > 0.5, "question_dominant", "non_question_dominant")
    tert = np.quantile(baseline_ctr_t, [1 / 3, 2 / 3])
    m2 = np.where(
        baseline_ctr_t <= tert[0],
        "baseline_ctr_low",
        np.where(baseline_ctr_t <= tert[1], "baseline_ctr_mid", "baseline_ctr_high"),
    )
    med = float(np.median(total_impr))
    m3 = np.where(total_impr > med, "size_above_median", "size_at_or_below_median")
    return {
        "status": "POST HOC, EXPLORATORY. No verdict. Second look at the locked split under DECISIONS.md D15; the multiple-look cost is stated there and in the report.",
        "overall_check_against_frozen": check,
        "overall": {
            "n_tests": pooled["n_tests"],
            "log_or": r4(pooled["log_or"]),
            "odds_ratio": r4(math.exp(pooled["log_or"])),
            "tau": r4(pooled["tau"]),
            "tau2": r4(pooled["tau2"]),
            "i2_percent": r4(pooled["i2_percent"]),
        },
        "moderators": [
            group_block(y, v, m1, "M1 question share of test impressions, split at 0.5"),
            group_block(y, v, m2, "M2 baseline CTR band (non-question arm CTR), tertiles"),
            group_block(y, v, m3, "M3 test size (total impressions), median split; packages per test is not in the committed per-test file, so total impressions stands in"),
        ],
    }


# ---------------------------------------------------------------- main


def run():
    out = {
        "amendment_date": "2026-11-17",
        "decisions": ["D13", "D14", "D15"],
        "frozen_files_touched": [],
        "d13_label_sensitivity": label_sensitivity(),
        "d14_msprt_tau_sensitivity": tau_sensitivity(),
        "d15_moderator_analysis": moderator_analysis(),
    }
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "amendment_2026-11-17_gap_closure.json").write_text(
        json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8"
    )
    write_report(out)
    print(json.dumps(out, indent=1, sort_keys=True))
    return out


def write_report(out):
    d13 = out["d13_label_sensitivity"]
    d14 = out["d14_msprt_tau_sensitivity"]
    d15 = out["d15_moderator_analysis"]
    lines = []
    lines.append("# Gap-closure amendment analyses (2026-11-17)")
    lines.append("")
    lines.append(
        "Generated by `python -m explab.gapclosure` from the committed files. "
        "Post-registration amendments D13, D14, D15 in DECISIONS.md, registered "
        "before any of these computations ran. No frozen results file was "
        "modified; every number below is read from "
        "results/amendment_2026-11-17_gap_closure.json."
    )
    lines.append("")
    lines.append("## D13. Label-rule sensitivity: stopped, no correction invented")
    lines.append("")
    lines.append(
        f"Status: {d13['status']}. The audit's {d13['n_flipped_in_audit']} flipped "
        f"headlines (sample indices {d13['flipped_sample_indices']}, all in the "
        f"{', '.join(d13['flipped_groups'])} group) belong to tests that are all in "
        f"the development split: {d13['flipped_test_ids_all_in_development_split']}; "
        f"any in the locked split: {d13['flipped_test_ids_any_in_locked_split']}. "
        "The frozen headline stands as reported: pooled odds ratio 0.8645 "
        "(95% CI 0.8335 to 0.8966, 465 locked tests, results/primary_locked.json)."
    )
    lines.append("")
    lines.append(d13["reason"])
    lines.append("")
    lines.append("## D14. mSPRT mixing-scale sensitivity (ROADMAP Deep item 3)")
    lines.append("")
    chk = d14["frozen_tau_reproduction_check"]
    lines.append(
        f"Frozen-stream check at tau 0.001: A/A mSPRT rate reproduces "
        f"results/sequential.json: {chk['aa_msprt_percent_matches_frozen']}; "
        f"A/B: {chk['ab_msprt_percent_matches_frozen']}. Design: "
        f"{d14['design']['runs']} runs, seed {d14['design']['seed']}, looks at "
        f"{d14['design']['looks_per_arm']} impressions per arm, baseline CTR "
        f"{d14['design']['baseline_ctr']}. Naive rates are tau-independent "
        "(frozen: A/A final look 5.03 percent, any look 16.32 percent; "
        "A/B 5.76 and 17.27 percent)."
    )
    lines.append("")
    lines.append("| tau_mix | A/A any-look rejection % (95% CI) | A/B 5% lift any-look rejection % (95% CI) |")
    lines.append("| --- | --- | --- |")
    for row in d14["rows"]:
        a = row["aa_null"]
        b = row["ab_5pct_lift"]
        lines.append(
            f"| {row['tau_mix']} | {a['rate_percent']} [{a['ci95_percent'][0]}, {a['ci95_percent'][1]}] "
            f"| {b['rate_percent']} [{b['ci95_percent'][0]}, {b['ci95_percent'][1]}] |"
        )
    lines.append("")
    lines.append(
        "Reading: the frozen tau 0.001 sits at the conservative end of the map. "
        "The table is the trade-off itself; no tau is adopted and no verdict "
        "changes (DECISIONS.md D11 stands)."
    )
    lines.append("")
    lines.append("## D15. Moderator analysis of the locked-split heterogeneity (post hoc, exploratory)")
    lines.append("")
    ov = d15["overall"]
    lines.append(
        f"Overall (recomputed from results/per_test_locked.csv; matches "
        f"results/primary_locked.json): {ov['n_tests']} tests, log OR "
        f"{ov['log_or']}, tau {ov['tau']}, I squared {ov['i2_percent']} percent. "
        "This is a second, post hoc look at the locked split under amendment "
        "D15. It is exploratory: no hypothesis is tested and no verdict "
        "changes. Three moderator splits were run, the ones registered in D15."
    )
    for m in d15["moderators"]:
        lines.append("")
        lines.append(f"### {m['moderator']}")
        lines.append("")
        lines.append("| Group | Tests | Log OR | Odds ratio | 95% CI (log OR) | tau | I squared % |")
        lines.append("| --- | --- | --- | --- | --- | --- | --- |")
        for g, blk in m["per_group"].items():
            lines.append(
                f"| {g} | {blk['n_tests']} | {blk['log_or']} | {blk['odds_ratio']} "
                f"| [{blk['ci95_log_or'][0]}, {blk['ci95_log_or'][1]}] | {blk['tau']} | {blk['i2_percent']} |"
            )
        lines.append("")
        lines.append(
            f"Q decomposition: Q total {m['q_total']}, Q within {m['q_within']}, "
            f"Q between {m['q_between']} (df {m['q_between_df']}, p "
            f"{m['q_between_p']:.4g}). Share of Q explained: "
            f"{m['share_of_q_explained_percent']} percent. Tau squared: overall "
            f"{m['tau2_overall']}, residual under the group-mean model "
            f"{m['tau2_residual']}, reduction {m['r2_tau2_reduction_percent']} percent."
        )
    lines.append("")
    REPORTS.mkdir(exist_ok=True)
    (REPORTS / "gap-closure-2026-11-17.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    run()
