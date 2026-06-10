"""Monthly backtest engine for Aurora Regime AI."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from aurora.config import ProjectConfig


@dataclass(frozen=True)
class BacktestResult:
    """Structured output of the Aurora backtest engine."""

    portfolio_returns: pd.Series
    equity_curve: pd.Series
    weights_history: pd.DataFrame
    rebalance_log: pd.DataFrame
    metadata: dict[str, Any]


def run_backtest(
    prices: pd.DataFrame,
    target_weights: pd.DataFrame,
    config: ProjectConfig,
) -> BacktestResult:
    """Run a backtest using t-1 signals and apply weights only in the next period.

    The temporal barrier is enforced inside this engine by mapping each target weight
    row dated at ``t`` to the first return observation strictly after ``t``. This
    avoids look-ahead bias even when the target weights were already derived from
    shifted signals upstream.
    """
    normalized_prices = _prepare_prices(prices=prices, config=config)
    normalized_target_weights = _prepare_target_weights(
        target_weights=target_weights,
        config=config,
    )

    asset_returns = normalized_prices.pct_change()
    returns_index = asset_returns.index[1:]

    weights_history, rebalance_log = _build_applied_weights(
        target_weights=normalized_target_weights,
        returns_index=returns_index,
        config=config,
    )

    aligned_asset_returns = asset_returns.loc[weights_history.index]
    gross_portfolio_returns = aligned_asset_returns.mul(weights_history).sum(axis=1)

    transaction_costs = pd.Series(0.0, index=weights_history.index, name="transaction_cost")
    if not rebalance_log.empty:
        transaction_costs.loc[rebalance_log["rebalance_date"]] = rebalance_log[
            "transaction_cost"
        ].to_numpy()

    portfolio_returns = gross_portfolio_returns.sub(transaction_costs, fill_value=0.0)
    portfolio_returns.name = "portfolio_return"

    equity_curve = (1.0 + portfolio_returns).cumprod() * config.initial_capital
    equity_curve.name = "equity_curve"

    metadata = {
        "initial_capital": config.initial_capital,
        "rebalance_frequency": config.rebalance_frequency,
        "transaction_cost_bps": config.transaction_cost_bps,
        "num_rebalances": int(len(rebalance_log)),
        "start_date": str(weights_history.index.min().date())
        if not weights_history.empty
        else None,
        "end_date": str(weights_history.index.max().date()) if not weights_history.empty else None,
    }

    return BacktestResult(
        portfolio_returns=portfolio_returns,
        equity_curve=equity_curve,
        weights_history=weights_history,
        rebalance_log=rebalance_log,
        metadata=metadata,
    )


def _prepare_prices(
    prices: pd.DataFrame,
    config: ProjectConfig,
) -> pd.DataFrame:
    normalized_prices = prices.copy()
    normalized_prices.index = pd.to_datetime(normalized_prices.index)
    normalized_prices = normalized_prices.sort_index()
    normalized_prices = normalized_prices.reindex(columns=list(config.assets))

    if normalized_prices.index.has_duplicates:
        raise ValueError("prices nao pode conter datas duplicadas no indice.")

    return normalized_prices


def _prepare_target_weights(
    target_weights: pd.DataFrame,
    config: ProjectConfig,
) -> pd.DataFrame:
    normalized_weights = target_weights.copy()
    normalized_weights.index = pd.to_datetime(normalized_weights.index)
    normalized_weights = normalized_weights.sort_index()
    normalized_weights = normalized_weights.reindex(columns=list(config.assets))
    normalized_weights = _select_rebalance_targets(
        target_weights=normalized_weights,
        frequency=config.rebalance_frequency,
    )

    if normalized_weights.empty:
        raise ValueError("target_weights nao pode ser vazio para rodar o backtest.")

    if normalized_weights.isna().any().any():
        raise ValueError("target_weights nao pode conter pesos nulos.")

    row_sums = normalized_weights.sum(axis=1)
    if not row_sums.between(1.0 - 1e-9, 1.0 + 1e-9).all():
        raise ValueError("Cada linha de target_weights deve somar 1.0.")

    if (normalized_weights < 0.0).any().any():
        raise ValueError("target_weights nao pode conter pesos negativos.")

    return normalized_weights


def _select_rebalance_targets(
    target_weights: pd.DataFrame,
    frequency: str,
) -> pd.DataFrame:
    if frequency.upper() == "M":
        return target_weights.groupby(target_weights.index.to_period("M")).tail(1)

    return target_weights.groupby(target_weights.index.to_period(frequency)).tail(1)


def _build_applied_weights(
    target_weights: pd.DataFrame,
    returns_index: pd.DatetimeIndex,
    config: ProjectConfig,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    applied_weights = pd.DataFrame(index=returns_index, columns=target_weights.columns, dtype=float)
    previous_weights = pd.Series(0.0, index=target_weights.columns)
    rebalance_rows: list[dict[str, Any]] = []

    for signal_date, target_row in target_weights.iterrows():
        future_dates = returns_index[returns_index > signal_date]
        if len(future_dates) == 0:
            continue

        rebalance_date = future_dates[0]
        current_weights = target_row.astype(float)
        applied_weights.loc[rebalance_date:, current_weights.index] = current_weights.to_numpy()

        turnover = float(current_weights.sub(previous_weights).abs().sum())
        transaction_cost = turnover * (config.transaction_cost_bps / 10_000.0)
        rebalance_rows.append(
            {
                "signal_date": signal_date,
                "rebalance_date": rebalance_date,
                "turnover": turnover,
                "transaction_cost": transaction_cost,
                "weights": current_weights.to_dict(),
            }
        )
        previous_weights = current_weights

    applied_weights = applied_weights.ffill().dropna(how="all")
    rebalance_log = pd.DataFrame(rebalance_rows)
    return applied_weights, rebalance_log
