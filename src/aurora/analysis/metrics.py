"""Pure performance metrics for strategy and benchmark evaluation."""

from __future__ import annotations

import numpy as np
import pandas as pd


def compute_cumulative_return(returns: pd.Series) -> float:
    """Compute cumulative return from a return series."""
    clean_returns = _clean_returns(returns)
    if clean_returns.empty:
        return float("nan")
    return float((1.0 + clean_returns).prod() - 1.0)


def compute_annualized_return(
    returns: pd.Series,
    periods_per_year: int = 12,
) -> float:
    """Compute annualized return using the geometric mean."""
    clean_returns = _clean_returns(returns)
    if clean_returns.empty:
        return float("nan")

    total_growth = float((1.0 + clean_returns).prod())
    num_periods = clean_returns.shape[0]
    return float(total_growth ** (periods_per_year / num_periods) - 1.0)


def compute_annualized_volatility(
    returns: pd.Series,
    periods_per_year: int = 12,
) -> float:
    """Compute annualized volatility from return dispersion."""
    clean_returns = _clean_returns(returns)
    if clean_returns.empty:
        return float("nan")
    return float(clean_returns.std(ddof=0) * np.sqrt(periods_per_year))


def compute_sharpe_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.0,
    periods_per_year: int = 12,
) -> float:
    """Compute the annualized Sharpe ratio with optional annual risk-free rate."""
    clean_returns = _clean_returns(returns)
    if clean_returns.empty:
        return float("nan")

    periodic_risk_free = (1.0 + risk_free_rate) ** (1.0 / periods_per_year) - 1.0
    excess_returns = clean_returns - periodic_risk_free
    volatility = excess_returns.std(ddof=0)
    if volatility == 0.0:
        return float("nan")
    return float(excess_returns.mean() / volatility * np.sqrt(periods_per_year))


def compute_max_drawdown(returns: pd.Series) -> float:
    """Compute maximum drawdown from a return series."""
    clean_returns = _clean_returns(returns)
    if clean_returns.empty:
        return float("nan")

    equity_curve = (1.0 + clean_returns).cumprod()
    running_peak = equity_curve.cummax()
    drawdown = equity_curve.div(running_peak).sub(1.0)
    return float(drawdown.min())


def compute_calmar_ratio(
    returns: pd.Series,
    periods_per_year: int = 12,
) -> float:
    """Compute the Calmar ratio as annualized return over absolute max drawdown."""
    annualized_return = compute_annualized_return(returns, periods_per_year=periods_per_year)
    max_drawdown = compute_max_drawdown(returns)
    if pd.isna(annualized_return) or pd.isna(max_drawdown) or max_drawdown == 0.0:
        return float("nan")
    return float(annualized_return / abs(max_drawdown))


def compute_hit_rate(returns: pd.Series) -> float:
    """Compute hit rate as the fraction of positive return periods."""
    clean_returns = _clean_returns(returns)
    if clean_returns.empty:
        return float("nan")
    return float((clean_returns > 0.0).mean())


def compute_best_period_return(returns: pd.Series) -> float:
    """Return the best observed period return."""
    clean_returns = _clean_returns(returns)
    if clean_returns.empty:
        return float("nan")
    return float(clean_returns.max())


def compute_worst_period_return(returns: pd.Series) -> float:
    """Return the worst observed period return."""
    clean_returns = _clean_returns(returns)
    if clean_returns.empty:
        return float("nan")
    return float(clean_returns.min())


def _clean_returns(returns: pd.Series) -> pd.Series:
    clean_returns = returns.copy()
    clean_returns = pd.to_numeric(clean_returns, errors="coerce")
    clean_returns = clean_returns.dropna()
    return clean_returns
