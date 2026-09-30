"""Delta-normal VaR of a rate position."""

import numpy as np
from scipy.stats import norm


def daily_vol_bp(yields_pct):
    """Sample standard deviation of daily yield changes in bp."""
    dy_bp = np.diff(np.asarray(yields_pct, dtype=float)) * 100.0
    return float(np.std(dy_bp, ddof=1))


def delta_normal_var(dv01, vol_bp, confidence=0.99, holding_days=1):
    """VaR = DV01 * sigma_bp * z_alpha * sqrt(h)."""
    return float(dv01 * vol_bp * norm.ppf(confidence) * np.sqrt(holding_days))
