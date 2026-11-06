"""Power module (no outcome data). Reproduces the research pack's
calculations C1 to C4 from their published inputs, from code.

Inputs (estimates from published totals, labelled as estimates):
- C1: baseline CTR = 5.7M clicks / 370M impressions (Robertson et al.
  2023 totals, both rounded).
- C2: mean arm size = 538,272,878 assignments / 150,817 arms
  (Matias et al. 2021 totals).

C3: two-proportion sample size, pooled-variance form:
  n = (z_a * sqrt(2 pbar (1-pbar)) + z_b * sqrt(p1(1-p1) + p2(1-p2)))^2
      / (p2 - p1)^2
with alpha 0.05 two-sided and power 0.80. Rounded to the nearest
integer, this reproduces the pack's table exactly.

C4: tests needed for the pooled analysis. One test contributes one
question arm and one non-question arm at the mean arm size; per-test
variance of the log odds ratio is 2 * (1/clicks + 1/nonclicks).
Pooled standard error with between-test SD tau over k tests is
sqrt((var + tau^2) / k); k is the smallest integer giving 80 percent
power at the 5 percent relative odds ratio effect.
"""

import json
import math
from pathlib import Path

from scipy.optimize import brentq
from scipy.stats import norm

RESULTS = Path("results")
Z_A = float(norm.ppf(0.975))
Z_B = float(norm.ppf(0.80))

BASELINE_CLICKS = 5_700_000
BASELINE_IMPRESSIONS = 370_000_000
TOTAL_ASSIGNMENTS = 538_272_878
TOTAL_ARMS = 150_817

PACK_C3 = {5: 411183, 10: 105261, 20: 27546, 50: 4996}
PACK_C4 = {0.0: 118, 0.05: 126, 0.10: 150, 0.15: 190}
PACK_MDE = 60.3


def baseline_ctr():
    return BASELINE_CLICKS / BASELINE_IMPRESSIONS


def mean_arm_size():
    return TOTAL_ASSIGNMENTS / TOTAL_ARMS


def n_per_arm(p1, rel_lift):
    p2 = p1 * (1 + rel_lift)
    pbar = (p1 + p2) / 2
    num = (
        Z_A * math.sqrt(2 * pbar * (1 - pbar))
        + Z_B * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))
    ) ** 2
    return num / (p2 - p1) ** 2


def min_detectable_effect(p1, n_arm):
    f = lambda rel: n_per_arm(p1, rel) - n_arm
    return brentq(f, 1e-6, 5.0)


def tests_needed(tau):
    p1 = baseline_ctr()
    n_arm = round(mean_arm_size())
    clicks = p1 * n_arm
    var = 2 * (1 / clicks + 1 / (n_arm - clicks))
    p2 = p1 * 1.05
    delta = math.log((p2 / (1 - p2)) / (p1 / (1 - p1)))
    pooled_var_needed = (delta / (Z_A + Z_B)) ** 2
    return math.ceil((var + tau**2) / pooled_var_needed), var, delta


def run():
    p1 = baseline_ctr()
    arm = mean_arm_size()
    c3 = {}
    for rel_pct, target in PACK_C3.items():
        value = n_per_arm(p1, rel_pct / 100)
        c3[str(rel_pct)] = {
            "n_per_arm": round(value),
            "pack_value": target,
            "matches_pack": round(value) == target,
        }
    mde = min_detectable_effect(p1, round(arm)) * 100
    c4 = {}
    var = delta = None
    for tau, target in PACK_C4.items():
        k, var, delta = tests_needed(tau)
        c4[str(tau)] = {"tests_needed": k, "pack_value": target, "matches_pack": k == target}
    out = {
        "inputs_labelled_estimates": True,
        "c1_baseline_ctr_percent": round(p1 * 100, 4),
        "c2_mean_arm_size": round(arm, 1),
        "c2_mean_arm_size_rounded": round(arm),
        "c3_n_per_arm_by_relative_lift_percent": c3,
        "c3_min_detectable_effect_percent_at_mean_arm": round(mde, 1),
        "c3_min_detectable_effect_pack": PACK_MDE,
        "c4_per_test_log_or_variance": round(var, 6),
        "c4_target_log_or": round(delta, 4),
        "c4_tests_needed_by_tau": c4,
        "formula": "pooled-variance two-proportion z, alpha 0.05 two-sided, power 0.80",
    }
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "power.json").write_text(
        json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(out, indent=1, sort_keys=True))
    return out


if __name__ == "__main__":
    run()
