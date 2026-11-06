"""Known-answer tests for the power module (pack C3 and C4 values)."""

from explab import power as power_module
from explab.power import baseline_ctr, mean_arm_size, n_per_arm

needed_for_tau = power_module.tests_needed


def test_baseline_inputs():
    assert abs(baseline_ctr() - 0.0154054) < 1e-6
    assert round(mean_arm_size()) == 3569


def test_c3_table_reproduced():
    p1 = baseline_ctr()
    assert round(n_per_arm(p1, 0.05)) == 411183
    assert round(n_per_arm(p1, 0.10)) == 105261
    assert round(n_per_arm(p1, 0.20)) == 27546
    assert round(n_per_arm(p1, 0.50)) == 4996


def test_c4_table_reproduced():
    assert needed_for_tau(0.0)[0] == 118
    assert needed_for_tau(0.05)[0] == 126
    assert needed_for_tau(0.10)[0] == 150
    assert needed_for_tau(0.15)[0] == 190
