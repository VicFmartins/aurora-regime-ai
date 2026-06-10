"""Return calculations for Aurora market features."""

from __future__ import annotations

import numpy as np
import pandas as pd


def compute_returns(
    prices: pd.DataFrame,
    method: str = "simple",
) -> pd.DataFrame:
    """Compute returns from prices without applying any forward-looking shift.

    The one-period shift used to avoid look-ahead bias is intentionally applied only
    inside ``build_feature_set`` after all raw indicators are computed.
    """
    if method == "simple":
        return prices.pct_change()
    if method == "log":
        return compute_log_returns(prices)
    raise ValueError("Metodo de retorno invalido. Use 'simple' ou 'log'.")


def compute_log_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Compute log returns from prices without applying any forward-looking shift.

    The one-period shift used to avoid look-ahead bias is intentionally applied only
    inside ``build_feature_set`` after all raw indicators are computed.
    """
    return np.log(prices / prices.shift(1))
