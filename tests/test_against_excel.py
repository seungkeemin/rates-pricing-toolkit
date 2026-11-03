"""Python results must match the Excel answers to 6 decimal places.

Excel's Solver stops with price residuals around 1e-6 per 100 face, so bootstrapped DFs agree to
about 1e-8 rather than to machine precision. KRW amounts are compared relative to their size.
"""

import datetime as dt

import numpy as np

from ratestool import bond_risk, delta_normal_var, forward_rates, krw_irs_curve, ust_zero_curve, value_pay_fixed


def test_ust_zero_curve(inputs, excel):
    t, df, zero = ust_zero_curve(inputs["ust"]["par_yield_pct"])
    e = excel["ust"]
    np.testing.assert_allclose(df[0], e["df_0_5"], atol=1e-6)
    np.testing.assert_allclose(t[1:], e["t"])
    np.testing.assert_allclose(df[1:], e["df"], atol=1e-6)
    np.testing.assert_allclose(zero[1:], e["zero_pct"], atol=1e-6)


def test_krw_irs_curve_and_valuation(inputs, excel):
    k, e = inputs["krw_irs"], excel["krw_irs"]
    grid, df = krw_irs_curve(k["cd91"], k["mid_swap"])
    np.testing.assert_allclose(grid, np.arange(1, 21) * 0.25)
    np.testing.assert_allclose(df, e["df"], atol=1e-6)
    np.testing.assert_allclose(forward_rates(df), e["fwd"], atol=1e-6)

    v = value_pay_fixed(df, k["fixed_rate"], k["notional"])
    np.testing.assert_allclose(v.fair_rate, e["fair_rate"], atol=1e-6)
    np.testing.assert_allclose([v.fixed_pv, v.float_pv], [e["fixed_pv"], e["float_pv"]], rtol=1e-6)
    np.testing.assert_allclose(v.value_pay_fixed, e["value_pay_fixed"], rtol=1e-4)


def test_ktb_risk_and_var(inputs, excel):
    b, e = inputs["ktb"], excel["ktb"]
    r = bond_risk(dt.date.fromisoformat(b["settlement"]), dt.date.fromisoformat(b["maturity"]),
                  b["coupon_pct"], b["ytm_pct"], b["freq"], b["par"], b["notional"])
    for name in ("dirty", "accrued", "clean", "macaulay", "modified", "convexity"):
        np.testing.assert_allclose(getattr(r, name), e[name], atol=1e-6, err_msg=name)
    np.testing.assert_allclose([r.dollar_duration, r.dv01], [e["dollar_duration"], e["dv01"]], rtol=1e-9)

    var = delta_normal_var(r.dv01, b["daily_vol_bp"], b["confidence"], b["holding_days"])
    np.testing.assert_allclose(var, e["var"], rtol=1e-9)
    np.testing.assert_allclose(var / (b["notional"] / b["par"] * r.dirty), e["var_ratio"], atol=1e-9)


def test_daily_vol_from_yield_series_matches_excel_stdev(inputs):
    import csv
    from pathlib import Path

    from ratestool import daily_vol_bp

    path = Path(__file__).parent / "fixtures" / "ktb_yields.csv"
    ys = [float(r["yield_pct"]) for r in csv.DictReader(path.open(encoding="utf-8"))]
    assert len(ys) == inputs["ktb"]["n_yield_obs"]
    np.testing.assert_allclose(daily_vol_bp(ys), inputs["ktb"]["daily_vol_bp"], rtol=1e-12)
