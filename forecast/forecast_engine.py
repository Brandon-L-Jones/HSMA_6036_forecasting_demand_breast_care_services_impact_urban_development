# forecast/forecast_engine.py

"""
Forecast engine for RDUH Breast Demand Model.

Generates:
- Central forecast
- Low-growth scenario
- High-growth scenario
- Annual totals
- Year-on-year % change

Used for strategic capacity planning.
"""

import pandas as pd
from copy import deepcopy
from forecast.demand_model import DemandParams


def make_forecast_series(
    params: DemandParams,
    years: int = 20,
    growth_low_delta: float = -0.3,
    growth_high_delta: float = 0.3,
    ref_low_delta: float = -0.2,
    ref_high_delta: float = 0.2,
):
    """
    Generates forecast DataFrame with central, low, and high projections.

    Deltas are percentage point adjustments to baseline assumptions.
    """

    if years <= 0:
        raise ValueError("Years must be > 0")

    ys = list(range(0, years + 1))

    # --- Central Forecast ---
    central_daily = [params.daily_demand_at_year(y) for y in ys]

    # --- Low Scenario ---
    low_params = deepcopy(params)
    low_params.growth += growth_low_delta
    low_params.referral_inflation += ref_low_delta

    low_daily = [low_params.daily_demand_at_year(y) for y in ys]

    # --- High Scenario ---
    high_params = deepcopy(params)
    high_params.growth += growth_high_delta
    high_params.referral_inflation += ref_high_delta

    high_daily = [high_params.daily_demand_at_year(y) for y in ys]

    # --- Build DataFrame ---
    df = pd.DataFrame({
        "Year": ys,
        "Daily_Central": central_daily,
        "Daily_Low": low_daily,
        "Daily_High": high_daily,
    })

    # Annual totals
    df["Annual_Central"] = df["Daily_Central"] * 365.0
    df["Annual_Low"] = df["Daily_Low"] * 365.0
    df["Annual_High"] = df["Daily_High"] * 365.0

    # Year-on-year % change (central only)
    df["YoY_%"] = (
        df["Annual_Central"]
        .pct_change()
        .fillna(0.0)
        * 100.0
    )

    return df
