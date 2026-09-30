"""Fixed-coupon bond price, duration, DV01 and convexity from YTM (KTB conventions used in the assignment)."""

import datetime as dt
from dataclasses import dataclass

import numpy as np


def add_months(d, months):
    """Same day-of-month `months` later (EDATE); coupon dates here fall on the 10th, so no month-end rolling."""
    y, m = divmod(d.month - 1 + months, 12)
    return dt.date(d.year + y, m + 1, d.day)


def coupon_schedule(settlement, maturity, freq):
    """Coupon dates after settlement, stepping back from maturity by 12/freq months."""
    step = 12 // freq
    dates, d = [], maturity
    while d > settlement:
        dates.append(d)
        d = add_months(d, -step)
    return sorted(dates), d          # d is the last coupon date on or before settlement


@dataclass(frozen=True)
class BondRisk:
    dirty: float
    accrued: float
    clean: float
    macaulay: float
    modified: float
    dollar_duration: float
    dv01: float
    convexity: float


def bond_risk(settlement, maturity, coupon_pct, ytm_pct, freq, par, notional):
    """Price and risk measures, discounting each flow at (1 + y/m)^(m t) with t = days/365."""
    dates, last = coupon_schedule(settlement, maturity, freq)
    t = np.array([(d - settlement).days / 365.0 for d in dates])
    cpn = par * coupon_pct / 100.0 / freq
    cf = np.full(len(dates), cpn)
    cf[-1] += par
    y = ytm_pct / 100.0
    pv = cf / (1.0 + y / freq) ** (freq * t)

    dirty = pv.sum()
    nxt = dates[0]
    accrued = cpn * (settlement - last).days / (nxt - last).days
    macaulay = np.sum(pv * t) / dirty
    modified = macaulay / (1.0 + y / freq)
    dollar_duration = modified * notional / par * dirty
    convexity = np.sum(pv * t * (t + 1.0 / freq)) / (dirty * (1.0 + y / freq) ** 2)
    return BondRisk(dirty, accrued, dirty - accrued, macaulay, modified, dollar_duration,
                    dollar_duration * 1e-4, convexity)
