"""US Treasury zero curve from par yields (semi-annual coupons, continuous-compounding zero rates)."""

import numpy as np

from .curve import bootstrap_par_curve, zero_rate_cc

TENOR_YEARS = {"6M": 0.5, "1Y": 1.0, "2Y": 2.0, "3Y": 3.0, "5Y": 5.0, "7Y": 7.0, "10Y": 10.0}


def ust_zero_curve(par_yield_pct):
    """Bootstrap DFs on a half-year grid out to 10Y.

    6M and 1Y are bills: DF = exp(-y T) with the quoted yield.
    2Y..10Y are par coupon bonds: (y/2) * sum DF(0.5..T) + DF(T) = 1, log-linear DF in between.
    Returns (t, df, zero_pct).
    """
    y = {TENOR_YEARS[k]: v / 100.0 for k, v in par_yield_pct.items() if k in TENOR_YEARS}
    short = {t: float(np.exp(-y[t] * t)) for t in (0.5, 1.0)}
    coupon_bonds = {t: r for t, r in y.items() if t > 1.0}
    t, df = bootstrap_par_curve(coupon_bonds, step=0.5, first_node_df=short)
    return t, df, zero_rate_cc(t, df) * 100.0
