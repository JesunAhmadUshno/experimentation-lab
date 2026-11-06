"""Unit tests for causal-arm components on synthetic data."""

import numpy as np

from explab.causal import fit_logistic, greedy_match, smd


def test_fit_logistic_recovers_direction():
    rng = np.random.default_rng(7)
    n = 4000
    x = rng.normal(size=n)
    eta = -0.5 + 1.2 * x
    p = 1 / (1 + np.exp(-eta))
    y = (rng.random(n) < p).astype(float)
    X = np.column_stack([np.ones(n), x])
    beta = fit_logistic(X, y)
    assert beta[1] > 0.8
    assert abs(beta[0] + 0.5) < 0.25


def test_smd_zero_for_identical():
    x = np.arange(50, dtype=float)
    assert abs(smd(x, x)) < 1e-9


def test_greedy_match_pairs_nearest():
    logit_t = np.array([0.0, 2.0])
    logit_c = np.array([0.05, -1.0, 2.1])
    pairs = greedy_match(logit_t, logit_c, caliper=0.5)
    assert sorted(pairs) == [(0, 0), (1, 2)]
