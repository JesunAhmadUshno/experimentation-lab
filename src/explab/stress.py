"""Assumption stress tests (U9, development split only).

(a) Placebo outcome: the guardrails balance statistic (impressions per
package), which the headline text cannot cause inside a randomized
test.
(b) Negative control: the primary estimator applied to the label
"headline starts with the word The", a feature with no registered
hypothesis and no plausible direct path to clicks beyond style
correlation.
(c) Sensitivity: for the IPW observational estimate, the E-value on
the risk ratio scale, and the bias (in log odds units, and as an odds
ratio factor) that an unmeasured confounder would need to contribute
to explain the full gap to the randomized benchmark.
"""

import json
import math
from pathlib import Path

from .data import DEFAULT_DATA, DEFAULT_SPLIT, apply_exclusions, load_raw, load_split, restrict_to_split, round4
from .guardrails import balance_statistic
from .label import add_labels
from .primary import analyse

RESULTS = Path("results")


def starts_with_the(headline):
    if not isinstance(headline, str):
        return False
    return headline.strip().lower().startswith("the ")


def run(data_path=DEFAULT_DATA, split_path=DEFAULT_SPLIT):
    df = load_raw(data_path)
    kept, _ = apply_exclusions(df)
    split = load_split(split_path)
    dev = add_labels(restrict_to_split(kept, split["development"]))

    placebo = balance_statistic(dev)

    neg = dev.copy()
    neg["is_question"] = neg["headline"].map(starts_with_the)
    neg_out, _ = analyse(neg)

    causal = json.loads((RESULTS / "causal.json").read_text(encoding="utf-8"))
    mu_t = causal["ipw"]["mu_question"]
    mu_c = causal["ipw"]["mu_nonquestion"]
    rr = mu_t / mu_c
    rr_for_evalue = rr if rr >= 1 else 1.0 / rr
    e_value = rr_for_evalue + math.sqrt(rr_for_evalue * (rr_for_evalue - 1))
    gap = causal["ipw"]["gap_to_benchmark"]

    out = {
        "split": "dev",
        "placebo_impressions_per_package": placebo,
        "negative_control_starts_with_the": {
            "n_tests": neg_out["n_tests"],
            "log_or": neg_out["log_or"],
            "ci95_log_or": neg_out["ci95_log_or"],
        },
        "sensitivity_ipw": {
            "risk_ratio": round4(rr),
            "e_value": round4(e_value),
            "bias_to_explain_full_gap_log_or": round4(abs(gap)),
            "bias_to_explain_full_gap_or_factor": round4(math.exp(abs(gap))),
        },
    }
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "stress.json").write_text(
        json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(out, indent=1, sort_keys=True))
    return out


if __name__ == "__main__":
    run()
