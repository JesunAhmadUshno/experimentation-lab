"""Simulation behaviour tests (seeded, deterministic)."""

from explab.peeking import rate_block, simulate
from explab.power import baseline_ctr


def test_aa_error_rates():
    p0 = baseline_ctr()
    z, lam = simulate(p0, p0)
    block = rate_block(z, lam)
    # Fixed-horizon testing holds its rate; peeking inflates it;
    # mSPRT stays near or below the nominal rate.
    assert 3.5 < block["naive_final_look_type1_or_power_percent"] < 6.5
    assert block["naive_any_look_percent"] > 10.0
    assert block["msprt_any_look_percent"] < 6.5


def test_ab_power_ordering():
    p0 = baseline_ctr()
    z, lam = simulate(p0 * 1.05, p0)
    block = rate_block(z, lam)
    # Peeking is the most powerful and the least honest; mSPRT the least
    # powerful of the three at this small effect.
    assert block["naive_any_look_percent"] > block["naive_final_look_type1_or_power_percent"]
    assert block["msprt_any_look_percent"] < block["naive_any_look_percent"]
