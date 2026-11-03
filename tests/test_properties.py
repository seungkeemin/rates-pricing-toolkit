"""Checks that do not depend on the Excel file."""

import numpy as np

from ratestool import bootstrap_par_curve, daily_vol_bp, forward_rates, krw_irs_curve, value_pay_fixed


def test_bootstrap_reprices_every_par_quote(inputs):
    k = inputs["krw_irs"]
    grid, df = krw_irs_curve(k["cd91"], k["mid_swap"])
    for years, rate in k["mid_swap"].items():
        n = int(float(years) / 0.25)
        np.testing.assert_allclose((1 - df[n - 1]) / (0.25 * df[:n].sum()), rate, atol=1e-12)


def test_swap_at_fair_rate_is_worth_zero(inputs):
    k = inputs["krw_irs"]
    _, df = krw_irs_curve(k["cd91"], k["mid_swap"])
    fair = value_pay_fixed(df, 0.0, 1.0).fair_rate
    assert abs(value_pay_fixed(df, fair, k["notional"]).value_pay_fixed) < 1e-3   # KRW on 100bn notional


def test_single_curve_float_leg_equals_one_minus_df(inputs):
    k = inputs["krw_irs"]
    _, df = krw_irs_curve(k["cd91"], k["mid_swap"])
    np.testing.assert_allclose(value_pay_fixed(df, 0.0, 1.0).float_pv, 1 - df[-1], atol=1e-14)


def test_flat_par_curve_gives_flat_forwards():
    grid, df = bootstrap_par_curve({1.0: 0.03, 2.0: 0.03, 3.0: 0.03}, step=0.25)
    np.testing.assert_allclose(forward_rates(df), 0.03, atol=1e-10)


def test_daily_vol_is_sample_std_of_bp_changes():
    np.testing.assert_allclose(daily_vol_bp([3.00, 3.01, 2.99]), np.std([1.0, -2.0], ddof=1))
