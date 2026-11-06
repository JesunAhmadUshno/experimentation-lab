"""Peeking simulation (pack C5) and the mSPRT sequential module (U7).

Design (frozen, PREREG.md section 10): Bernoulli streams at the
archive baseline CTR in both arms (A/A) and with a 5 percent relative
lift in the treated arm (A/B). Looks every 500 impressions per arm up
to 3,500 per arm (7 looks). 200,000 runs, seed 20261106.

Naive: two-proportion pooled z test at each look; reject if any look
has p < 0.05 (peeking) or only the final look does (fixed horizon).

mSPRT (Johari, Pekelis and Walsh): on the difference-in-proportions
scale with plug-in pooled variance V and mixing SD TAU_MIX = 0.001,
    Lambda = sqrt(V / (V + TAU_MIX^2))
             * exp( z^2 / 2 * TAU_MIX^2 / (V + TAU_MIX^2) )
Reject when Lambda first reaches 1 / 0.05 = 20. Always-valid
p-value: min over looks so far of 1 / max Lambda so far.
"""

import json
import math
from pathlib import Path

import numpy as np
from scipy.stats import norm

from . import SEED
from .power import baseline_ctr

RESULTS = Path("results")
RUNS = 200_000
LOOKS = np.arange(500, 3501, 500)
TAU_MIX = 0.001
ALPHA = 0.05


def simulate(p_treated, p_control):
    """Return z statistics and mSPRT lambdas, shape (RUNS, n_looks)."""
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
    lam = np.sqrt(var / (var + TAU_MIX**2)) * np.exp(
        (z**2 / 2.0) * (TAU_MIX**2 / (var + TAU_MIX**2))
    )
    return z, lam


def wilson_ci(successes, n, z=1.959964):
    if n == 0:
        return [None, None]
    p = successes / n
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    half = (z / denom) * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    return [round((centre - half) * 100, 2), round((centre + half) * 100, 2)]


def rate_block(z, lam):
    pvals = 2 * norm.sf(np.abs(z))
    final_reject = pvals[:, -1] < ALPHA
    any_reject = (pvals < ALPHA).any(axis=1)
    msprt_reject = (lam >= 1.0 / ALPHA).any(axis=1)
    return {
        "naive_final_look_type1_or_power_percent": round(final_reject.mean() * 100, 2),
        "naive_final_look_ci95_percent": wilson_ci(int(final_reject.sum()), RUNS),
        "naive_any_look_percent": round(any_reject.mean() * 100, 2),
        "naive_any_look_ci95_percent": wilson_ci(int(any_reject.sum()), RUNS),
        "msprt_any_look_percent": round(msprt_reject.mean() * 100, 2),
        "msprt_any_look_ci95_percent": wilson_ci(int(msprt_reject.sum()), RUNS),
    }


def run():
    p0 = baseline_ctr()
    z_aa, lam_aa = simulate(p0, p0)
    aa = rate_block(z_aa, lam_aa)
    z_ab, lam_ab = simulate(p0 * 1.05, p0)
    ab = rate_block(z_ab, lam_ab)
    out = {
        "seed": SEED,
        "runs": RUNS,
        "looks_per_arm": [int(x) for x in LOOKS],
        "baseline_ctr": round(p0, 6),
        "tau_mix": TAU_MIX,
        "pack_c5_reference": {
            "final_look_percent": 5.03,
            "final_look_ci95_percent": [4.93, 5.12],
            "any_look_percent": 16.32,
            "any_look_ci95_percent": [16.16, 16.48],
        },
        "aa": aa,
        "ab_5pct_lift": ab,
    }
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "sequential.json").write_text(
        json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(out, indent=1, sort_keys=True))
    return out


if __name__ == "__main__":
    run()
