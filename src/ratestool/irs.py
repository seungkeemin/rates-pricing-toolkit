"""KRW IRS: quarterly curve from CD 91D and par swap rates, then a pay-fixed / receive-CD valuation.

Single-curve setup: the same curve projects CD forwards and discounts. Accrual is fixed at 0.25.
"""

from dataclasses import dataclass

import numpy as np

from .curve import bootstrap_par_curve

ACCRUAL = 0.25


def krw_irs_curve(cd91, mid_swap):
    """DF on 0.25, 0.5, ... from CD 91D (simple) and par swap rates {years: rate}."""
    first = {ACCRUAL: 1.0 / (1.0 + cd91 * ACCRUAL)}
    return bootstrap_par_curve({float(k): v for k, v in mid_swap.items()}, step=ACCRUAL, first_node_df=first)


def forward_rates(df, accrual=ACCRUAL):
    """Simple 3M forwards F_k = (DF_{k-1} / DF_k - 1) / accrual, with DF_0 = 1."""
    prev = np.r_[1.0, df[:-1]]
    return (prev / df - 1.0) / accrual


@dataclass(frozen=True)
class SwapValue:
    fixed_pv: float
    float_pv: float
    value_pay_fixed: float
    fair_rate: float


def value_pay_fixed(df, fixed_rate, notional, accrual=ACCRUAL):
    """PV of both legs of a pay-fixed swap on the given quarterly DFs."""
    fwd = forward_rates(df, accrual)
    fixed_pv = float(np.sum(notional * fixed_rate * accrual * df))
    float_pv = float(np.sum(notional * fwd * accrual * df))
    fair = float((1.0 - df[-1]) / (accrual * df.sum()))
    return SwapValue(fixed_pv, float_pv, float_pv - fixed_pv, fair)
