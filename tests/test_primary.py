"""Unit tests for the primary estimator and the frozen verdict rule."""

import math

import numpy as np
import pandas as pd

from explab.primary import log_or_per_test, pool_dl, verdict_rule


def test_log_or_known_value():
    table = pd.DataFrame(
        {
            "clicks_q": [10.0],
            "impressions_q": [100.0],
            "clicks_nq": [5.0],
            "impressions_nq": [100.0],
            "nonclicks_q": [90.0],
            "nonclicks_nq": [95.0],
        }
    )
    out = log_or_per_test(table)
    expected = math.log((10 * 95) / (90 * 5))
    assert abs(out["logor"].iloc[0] - expected) < 1e-12
    assert not out["continuity_corrected"].iloc[0]


def test_continuity_correction_flagged():
    table = pd.DataFrame(
        {
            "clicks_q": [0.0],
            "impressions_q": [100.0],
            "clicks_nq": [5.0],
            "impressions_nq": [100.0],
            "nonclicks_q": [100.0],
            "nonclicks_nq": [95.0],
        }
    )
    out = log_or_per_test(table)
    assert out["continuity_corrected"].iloc[0]
    assert np.isfinite(out["logor"].iloc[0])


def test_pool_dl_no_heterogeneity():
    pooled = pool_dl([0.2, 0.2, 0.2], [0.01, 0.01, 0.01])
    assert abs(pooled["log_or"] - 0.2) < 1e-9
    assert pooled["tau2"] == 0.0


def test_verdict_rule_branches():
    assert verdict_rule(500, (0.1, 0.3), (0.12, 0.28))[0] == "CONFIRMED"
    assert verdict_rule(500, (-0.02, 0.02), (-0.01, 0.01))[0] == "REFUTED"
    assert verdict_rule(500, (-0.2, 0.2), (-0.15, 0.15))[0] == "INCONCLUSIVE"
    # Below the floor: capped unless the effect is large.
    assert verdict_rule(100, (0.01, 0.05), (0.015, 0.045))[0] == "INCONCLUSIVE"
    assert verdict_rule(100, (0.2, 0.5), (0.25, 0.45))[0] == "CONFIRMED"
