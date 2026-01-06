import pandas as pd
import numpy as np
import streamlit as st

from app.core.data import get_historical_data


def build_prices_matrix(symbol_keys, period="7d", interval="5m") -> pd.DataFrame:
    """
    Constructs a time-aligned price matrix (Close).
    Columns = assets (keys), index = UTC datetime.
    """
    price_series = {}

    for k in symbol_keys:
        df = get_historical_data(k, period=period, interval=interval)
        if df is None or df.empty:
            st.warning(f"[Portfolio] No data for {k}.")
            continue
        price_series[k] = df["Close"].rename(k)

    if not price_series:
        return pd.DataFrame()

    prices = pd.concat(price_series.values(), axis=1).sort_index()
    prices = prices.dropna(how="any")
    return prices


def normalize_weights(weights: dict) -> dict:
    """Force weights to sum to 1."""
    w = pd.Series(weights, dtype=float).fillna(0.0)
    s = w.sum()
    if s <= 0:
        w[:] = 1.0 / len(w)
    else:
        w = w / s
    return w.to_dict()


def simulate_portfolio(
    prices: pd.DataFrame,
    weights: dict,
    rebalance: str = "W",
    base: float = 100.0,
) -> pd.DataFrame:
    """
    Simulate a rebalanced portfolio.
    """
    if prices.empty:
        return pd.DataFrame()

    assets = list(prices.columns)
    weights = {a: weights.get(a, 0.0) for a in assets}
    weights = normalize_weights(weights)

    returns = prices.pct_change().fillna(0.0)

    rebalance_dates = set(returns.resample(rebalance).first().index)

    current_w = pd.Series(weights, index=assets)
    port_returns = []

    for t in returns.index:
        if t in rebalance_dates:
            current_w = pd.Series(weights, index=assets)

        r_t = returns.loc[t]
        port_r = float((current_w * r_t).sum())
        port_returns.append(port_r)

        # Weight drift
        current_w = current_w * (1.0 + r_t)
        if current_w.sum() > 0:
            current_w = current_w / current_w.sum()

    out = pd.DataFrame(index=returns.index)
    out["Portfolio_Returns"] = port_returns
    out["Portfolio_Equity"] = base * (1.0 + out["Portfolio_Returns"]).cumprod()
    return out
