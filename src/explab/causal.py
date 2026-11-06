"""Causal arm (development split only). PREREG.md section 10.

Cross-test observational contrast of question vs non-question packages,
propensity adjusted (IPW and 1 to 1 matching), against the randomized
within-test benchmark from the primary estimator on the same split.
The gap between adjusted estimate and benchmark, with a cluster
bootstrap interval (2,000 resamples over tests, seed 20261106), is
the result. The observational arm is a methods measurement; it is
never reported as a discovery about headlines.
"""

import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from . import SEED
from .data import DEFAULT_DATA, DEFAULT_SPLIT, apply_exclusions, load_raw, load_split, restrict_to_split, round4
from .features import COVARIATES, build_covariates
from .label import add_labels
from .primary import analyse

RESULTS = Path("results")
REPORTS = Path("reports")
BOOTSTRAP_RUNS = 2000
TRIM_LO, TRIM_HI = 0.01, 0.99
CALIPER_SD = 0.2


def fit_logistic(X, y, l2=1e-6, iters=100):
    """Newton iterations for logistic regression. X includes intercept."""
    beta = np.zeros(X.shape[1])
    Xt = X.T
    for _ in range(iters):
        eta = X @ beta
        p = 1 / (1 + np.exp(-eta))
        w = p * (1 - p)
        grad = Xt @ (y - p) - l2 * beta
        hess = (Xt * w) @ X + l2 * np.eye(X.shape[1])
        step = np.linalg.solve(hess, grad)
        beta = beta + step
        if np.max(np.abs(step)) < 1e-10:
            break
    return beta


def design_matrix(df, means, sds):
    cols = []
    for name in COVARIATES:
        if name == "eyecatcher_reused":
            cols.append(df[name].to_numpy(dtype=float))
        else:
            cols.append((df[name].to_numpy(dtype=float) - means[name]) / sds[name])
    return np.column_stack([np.ones(len(df))] + cols)


def propensity(df, means, sds):
    X = design_matrix(df, means, sds)
    y = df["is_question"].to_numpy(dtype=float)
    beta = fit_logistic(X, y)
    eta = X @ beta
    e = 1 / (1 + np.exp(-eta))
    return e, beta


def log_or_from_totals(clicks_t, imp_t, clicks_c, imp_c):
    return math.log((clicks_t / (imp_t - clicks_t)) / (clicks_c / (imp_c - clicks_c)))


def ipw_estimate(df, e):
    a = df["is_question"].to_numpy(dtype=bool)
    keep = (e >= TRIM_LO) & (e <= TRIM_HI)
    trimmed = int((~keep).sum())
    d = df[keep]
    ek = e[keep]
    ak = a[keep]
    clicks = d["clicks"].to_numpy(dtype=float)
    imp = d["impressions"].to_numpy(dtype=float)
    w_t = np.where(ak, 1.0 / ek, 0.0)
    w_c = np.where(ak, 0.0, 1.0 / (1.0 - ek))
    mu_t = float(np.sum(w_t * clicks) / np.sum(w_t * imp))
    mu_c = float(np.sum(w_c * clicks) / np.sum(w_c * imp))
    return {
        "log_or": math.log((mu_t / (1 - mu_t)) / (mu_c / (1 - mu_c))),
        "mu_question": mu_t,
        "mu_nonquestion": mu_c,
        "n_trimmed": trimmed,
    }


def greedy_match(logit_t, logit_c, caliper):
    """Greedy 1 to 1 nearest-neighbour matching on the logit, without
    replacement, deterministic by construction (DECISIONS.md D12).

    Logits are rounded to 8 decimals. Candidate pairs are all
    (treated, control) pairs inside the caliper, with distances
    computed here in float64. Pairs are considered in one total order:
    distance, then treated row, then control row (numpy lexsort).
    Each pair is assigned if both units are still free. No step
    depends on a search tree's internal ordering or an unstable sort,
    so the matched set is a pure function of the rounded logits."""
    lt = np.round(np.asarray(logit_t, dtype=float), 8)
    lc = np.round(np.asarray(logit_c, dtype=float), 8)
    if len(lt) == 0 or len(lc) == 0:
        return []
    dist = np.abs(lt[:, None] - lc[None, :])
    ti_idx, ci_idx = np.nonzero(dist <= caliper)
    if len(ti_idx) == 0:
        return []
    dists = dist[ti_idx, ci_idx]
    order = np.lexsort((ci_idx, ti_idx, dists))
    used_t = np.zeros(len(lt), dtype=bool)
    used_c = np.zeros(len(lc), dtype=bool)
    pairs = []
    for k in order:
        ti = int(ti_idx[k])
        ci = int(ci_idx[k])
        if not used_t[ti] and not used_c[ci]:
            used_t[ti] = True
            used_c[ci] = True
            pairs.append((ti, ci))
    return pairs


def match_estimate(df, e):
    a = df["is_question"].to_numpy(dtype=bool)
    logit = np.log(e / (1 - e))
    caliper = CALIPER_SD * float(np.std(logit))
    t_idx = np.where(a)[0]
    c_idx = np.where(~a)[0]
    pairs_local = greedy_match(logit[t_idx], logit[c_idx], caliper)
    pairs = [(t_idx[i], c_idx[j]) for i, j in pairs_local]
    if not pairs:
        return {"log_or": None, "n_pairs": 0}
    ti = np.array([p[0] for p in pairs])
    ci = np.array([p[1] for p in pairs])
    clicks = df["clicks"].to_numpy(dtype=float)
    imp = df["impressions"].to_numpy(dtype=float)
    mu_t = float(clicks[ti].sum() / imp[ti].sum())
    mu_c = float(clicks[ci].sum() / imp[ci].sum())
    return {
        "log_or": math.log((mu_t / (1 - mu_t)) / (mu_c / (1 - mu_c))),
        "mu_question": mu_t,
        "mu_nonquestion": mu_c,
        "n_pairs": len(pairs),
        "pair_rows_treated": ti,
        "pair_rows_control": ci,
    }


def smd(x_t, x_c, w_t=None, w_c=None):
    def mean_var(x, w):
        if w is None:
            return float(np.mean(x)), float(np.var(x, ddof=1))
        m = float(np.sum(w * x) / np.sum(w))
        v = float(np.sum(w * (x - m) ** 2) / np.sum(w))
        return m, v

    m_t, v_t = mean_var(x_t, w_t)
    m_c, v_c = mean_var(x_c, w_c)
    denom = math.sqrt((v_t + v_c) / 2)
    return 0.0 if denom == 0 else (m_t - m_c) / denom


def balance_table(df, e, match_pairs):
    a = df["is_question"].to_numpy(dtype=bool)
    w_ipw = np.where(a, 1.0 / e, 1.0 / (1.0 - e))
    table = {}
    for name in COVARIATES:
        x = df[name].to_numpy(dtype=float)
        raw = smd(x[a], x[~a])
        ipw = smd(x[a], x[~a], w_ipw[a], w_ipw[~a])
        if match_pairs is not None and len(match_pairs) > 0:
            ti = np.array([p[0] for p in match_pairs])
            ci = np.array([p[1] for p in match_pairs])
            matched = smd(x[ti], x[ci])
        else:
            matched = None
        table[name] = {
            "smd_raw": round4(raw),
            "smd_ipw": round4(ipw),
            "smd_matched": round4(matched) if matched is not None else None,
        }
    return table


def prepare_dev(data_path=DEFAULT_DATA, split_path=DEFAULT_SPLIT):
    df = load_raw(data_path)
    kept, _ = apply_exclusions(df)
    split = load_split(split_path)
    dev = restrict_to_split(kept, split["development"])
    dev = build_covariates(add_labels(dev)).reset_index(drop=True)
    means = {n: float(dev[n].mean()) for n in COVARIATES if n != "eyecatcher_reused"}
    sds = {
        n: (float(dev[n].std(ddof=1)) or 1.0)
        for n in COVARIATES
        if n != "eyecatcher_reused"
    }
    return dev, means, sds


def run(data_path=DEFAULT_DATA, split_path=DEFAULT_SPLIT):
    dev, means, sds = prepare_dev(data_path, split_path)
    benchmark, _ = analyse(dev)
    e, _beta = propensity(dev, means, sds)
    ipw = ipw_estimate(dev, e)
    match = match_estimate(dev, e)
    pairs = None
    if match["n_pairs"]:
        pairs = list(zip(match.pop("pair_rows_treated"), match.pop("pair_rows_control")))
    else:
        match.pop("pair_rows_treated", None)
        match.pop("pair_rows_control", None)
    balance = balance_table(dev, e, pairs)

    a = dev["is_question"].to_numpy(dtype=bool)
    clicks = dev["clicks"].to_numpy(dtype=float)
    imp = dev["impressions"].to_numpy(dtype=float)
    naive = log_or_from_totals(
        clicks[a].sum(), imp[a].sum(), clicks[~a].sum(), imp[~a].sum()
    )

    # Cluster bootstrap over tests.
    test_ids = dev["clickability_test_id"].to_numpy()
    unique_tests = np.unique(test_ids)
    row_index_by_test = {
        t: np.where(test_ids == t)[0] for t in unique_tests
    }
    rng = np.random.default_rng(SEED)
    gaps_ipw = []
    gaps_match = []
    bench_vals = []
    for _ in range(BOOTSTRAP_RUNS):
        sampled = rng.choice(unique_tests, size=len(unique_tests), replace=True)
        pos = np.concatenate([row_index_by_test[t] for t in sampled])
        boot = dev.iloc[pos].copy()
        boot["boot_id"] = np.repeat(
            np.arange(len(sampled)), [len(row_index_by_test[t]) for t in sampled]
        )
        b_bench, _ = analyse(boot, id_col="boot_id")
        b_e, _ = propensity(boot, means, sds)
        b_ipw = ipw_estimate(boot, b_e)
        b_match = match_estimate(boot, b_e)
        bench_vals.append(b_bench["log_or"])
        gaps_ipw.append(b_ipw["log_or"] - b_bench["log_or"])
        if b_match["log_or"] is not None:
            gaps_match.append(b_match["log_or"] - b_bench["log_or"])

    def pct(vals, lo=2.5, hi=97.5):
        arr = np.sort(np.asarray(vals, dtype=float))
        return [round4(float(np.percentile(arr, lo))), round4(float(np.percentile(arr, hi)))]

    out = {
        "split": "dev",
        "n_packages": int(len(dev)),
        "n_tests": int(len(unique_tests)),
        "benchmark_log_or": benchmark["log_or"],
        "benchmark_ci95_log_or": benchmark["ci95_log_or"],
        "benchmark_bootstrap_ci95_log_or": pct(bench_vals),
        "naive_log_or": round4(naive),
        "ipw": {
            "log_or": round4(ipw["log_or"]),
            "mu_question": round(ipw["mu_question"], 6),
            "mu_nonquestion": round(ipw["mu_nonquestion"], 6),
            "n_trimmed": ipw["n_trimmed"],
            "gap_to_benchmark": round4(ipw["log_or"] - benchmark["log_or"]),
            "gap_bootstrap_ci95": pct(gaps_ipw),
        },
        "matching": {
            "log_or": round4(match["log_or"]) if match["log_or"] is not None else None,
            "mu_question": round(match["mu_question"], 6) if match["log_or"] is not None else None,
            "mu_nonquestion": round(match["mu_nonquestion"], 6) if match["log_or"] is not None else None,
            "n_pairs": match["n_pairs"],
            "gap_to_benchmark": round4(match["log_or"] - benchmark["log_or"]) if match["log_or"] is not None else None,
            "gap_bootstrap_ci95": pct(gaps_match) if gaps_match else None,
            "bootstrap_runs_with_pairs": len(gaps_match),
        },
        "balance": balance,
        "balance_target_abs_smd_below": 0.1,
        "bootstrap_runs": BOOTSTRAP_RUNS,
        "seed": SEED,
    }
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "causal.json").write_text(
        json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8"
    )
    REPORTS.mkdir(exist_ok=True)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(e[a], bins=40, alpha=0.6, label="question packages")
    ax.hist(e[~a], bins=40, alpha=0.6, label="non-question packages")
    ax.set_xlabel("propensity score")
    ax.set_ylabel("packages")
    ax.set_title("Propensity overlap, development split")
    ax.legend()
    fig.tight_layout()
    fig.savefig(REPORTS / "propensity_overlap.png", dpi=120)
    plt.close(fig)
    print(json.dumps(out, indent=1, sort_keys=True))
    return out


if __name__ == "__main__":
    run()
