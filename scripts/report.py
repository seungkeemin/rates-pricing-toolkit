"""Print every result next to the Excel answer and draw the UST curve figure.

    python scripts/report.py
"""

import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ratestool import bond_risk, delta_normal_var, forward_rates, krw_irs_curve, ust_zero_curve, value_pay_fixed  # noqa: E402

I = json.loads((ROOT / "tests/fixtures/inputs.json").read_text(encoding="utf-8"))
E = json.loads((ROOT / "tests/fixtures/excel_expected.json").read_text(encoding="utf-8"))


def row(label, py, xl, fmt="{:.6f}"):
    print(f"{label:<28}{fmt.format(py):>22}{fmt.format(xl):>22}{py - xl:>14.2e}")


print(f"{'':<28}{'Python':>22}{'Excel':>22}{'diff':>14}")
t, df, zero = ust_zero_curve(I["ust"]["par_yield_pct"])
for T in (2.0, 5.0, 10.0):
    i = list(t).index(T)
    row(f"UST zero {T:g}Y (%)", zero[i], E["ust"]["zero_pct"][i - 1])

k = I["krw_irs"]
grid, dfk = krw_irs_curve(k["cd91"], k["mid_swap"])
v = value_pay_fixed(dfk, k["fixed_rate"], k["notional"])
row("KRW 5Y fair swap rate", v.fair_rate, E["krw_irs"]["fair_rate"], "{:.8f}")
row("fixed leg PV (KRW)", v.fixed_pv, E["krw_irs"]["fixed_pv"], "{:,.0f}")
row("floating leg PV (KRW)", v.float_pv, E["krw_irs"]["float_pv"], "{:,.0f}")
row("pay-fixed value (KRW)", v.value_pay_fixed, E["krw_irs"]["value_pay_fixed"], "{:,.0f}")

b = I["ktb"]
r = bond_risk(dt.date.fromisoformat(b["settlement"]), dt.date.fromisoformat(b["maturity"]),
              b["coupon_pct"], b["ytm_pct"], b["freq"], b["par"], b["notional"])
for name in ("dirty", "clean", "macaulay", "modified", "convexity"):
    row(f"KTB {name}", getattr(r, name), E["ktb"][name])
row("KTB DV01 (KRW)", r.dv01, E["ktb"]["dv01"], "{:,.2f}")
var = delta_normal_var(r.dv01, b["daily_vol_bp"], b["confidence"], b["holding_days"])
row("1-day 99% VaR (KRW)", var, E["ktb"]["var"], "{:,.0f}")

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ImportError:
    sys.exit(0)
par = {0.5: 3.98, 1: 4.04, 2: 4.23, 3: 4.30, 5: 4.38, 7: 4.52, 10: 4.68}
fig, ax1 = plt.subplots(figsize=(8, 4.2))
ax1.plot(list(par), list(par.values()), "o", color="gray", label="par yield (quote)")
ax1.plot(t, zero, "-", color="C0", label="zero rate (bootstrapped, cc)")
ax1.set_xlabel("maturity (years)"); ax1.set_ylabel("%"); ax1.grid(alpha=0.3)
ax2 = ax1.twinx()
ax2.plot(t, df, "--", color="C1", label="discount factor")
ax2.set_ylabel("DF")
h1, l1 = ax1.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
ax1.legend(h1 + h2, l1 + l2, loc="center right", fontsize=8)
ax1.set_title(f"US Treasury curve, {I['ust']['as_of']}")
fig.tight_layout()
(ROOT / "figures").mkdir(exist_ok=True)
fig.savefig(ROOT / "figures" / "ust_curve.png", dpi=130)
