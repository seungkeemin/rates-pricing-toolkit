"""Discount curves from par quotes, with log-linear DF interpolation between bootstrapped nodes."""

import numpy as np
from scipy.optimize import brentq


def loglinear_df(t, t_nodes, df_nodes):
    """DF at t by linear interpolation of ln DF between nodes (t inside the node range)."""
    return np.exp(np.interp(t, t_nodes, np.log(df_nodes)))


def bootstrap_par_curve(par_rates, step, first_node_df=None, face=1.0):
    """Bootstrap DFs on a regular grid of `step` years from par rates.

    par_rates: {maturity: par rate (decimal)} for the bootstrapped nodes, ascending.
    first_node_df: optional {t: DF} fixed before bootstrapping (short end from money-market rates).
    Each new node T is solved so that a par bond paying rate * step every period prices at face:
        rate * step * sum DF(t_k) + DF(T) = 1,
    with DFs between the previous node and T log-linear in the unknown DF(T).
    Returns (grid, df) on step, 2*step, ..., max maturity.
    """
    maturities = sorted(par_rates)
    grid = np.round(np.arange(step, maturities[-1] + step / 2, step), 10)
    t_nodes, df_nodes = [0.0], [1.0]
    for t, df in sorted((first_node_df or {}).items()):
        t_nodes.append(t)
        df_nodes.append(df)

    for T in maturities:
        if T <= t_nodes[-1]:
            continue
        rate = par_rates[T]
        pay = grid[grid <= T + 1e-12]

        def gap(df_T):
            dfs = loglinear_df(pay, t_nodes + [T], df_nodes + [df_T])
            return rate * step * dfs.sum() + dfs[-1] - 1.0

        df_T = brentq(gap, 1e-6, 1.0, xtol=1e-15)
        t_nodes.append(T)
        df_nodes.append(df_T)
    return grid, loglinear_df(grid, t_nodes, df_nodes)


def zero_rate_cc(t, df):
    """Continuously compounded zero rate."""
    return -np.log(df) / t
