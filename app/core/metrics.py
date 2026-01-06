# app/core/metrics.py
import pandas as pd
import numpy as np


def max_drawdown(equity: pd.Series) -> float:
    """
    Max drawdown in % from an equity curve.
    """
    equity = equity.dropna()
    if equity.empty:
        return float("nan")
    running_max = equity.cummax()
    dd = (equity - running_max) / running_max
    return float(dd.min() * 100.0)


def annualized_vol(returns: pd.Series, periods_per_year: int = 252) -> float:
    """
    Annualized volatility in %.
    """
    returns = returns.dropna()
    if returns.empty:
        return float("nan")
    return float(returns.std() * np.sqrt(periods_per_year) * 100.0)


def annualized_return(returns: pd.Series, periods_per_year: int = 252) -> float:
    """
    Annualized return in % using geometric compounding.
    """
    returns = returns.dropna()
    if returns.empty:
        return float("nan")
    compounded = (1.0 + returns).prod()
    n = len(returns)
    if n == 0:
        return float("nan")
    return float((compounded ** (periods_per_year / n) - 1.0) * 100.0)


def sharpe_ratio(returns: pd.Series, rf_annual: float = 0.0, periods_per_year: int = 252) -> float:
    """
    Sharpe ratio (annualized). rf_annual in decimal (e.g. 0.02 for 2%).
    """
    returns = returns.dropna()
    if returns.empty:
        return float("nan")
    rf_per_period = rf_annual / periods_per_year
    excess = returns - rf_per_period
    vol = excess.std()
    if vol == 0 or np.isnan(vol):
        return float("nan")
    return float((excess.mean() / vol) * np.sqrt(periods_per_year))


def corr_matrix(returns_df: pd.DataFrame) -> pd.DataFrame:
    """
    Correlation matrix of returns.
    """
    if returns_df is None or returns_df.empty:
        return pd.DataFrame()
    return returns_df.corr()
