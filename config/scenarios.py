# config/scenarios.py

"""
Scenario presets for RDUH Breast Service Demand Forecasting Tool.

These scenarios modify baseline geography assumptions.

Definitions:
- referral_inflation: additional annual % change in referral behaviour
- growth_delta: adjustment to baseline population growth %
- housing_delta: adjustment to baseline housing-driven growth %

These are illustrative scenario stress-tests and not formal forecasts.
"""

from typing import Dict, TypedDict


class ScenarioConfig(TypedDict):
    referral_inflation: float
    growth_delta: float
    housing_delta: float


def scenario_presets() -> Dict[str, ScenarioConfig]:
    """
    Returns predefined demand growth scenarios.
    Values are percentage point adjustments.
    """

    return {

        "Baseline": {
            "referral_inflation": 0.5,
            "growth_delta": 0.0,
            "housing_delta": 0.0
        },

        "High Growth": {
            "referral_inflation": 1.2,
            "growth_delta": 0.6,
            "housing_delta": 0.5
        },

        "Low Growth": {
            "referral_inflation": 0.2,
            "growth_delta": -0.3,
            "housing_delta": -0.2
        },

        "Best Case (Demand Controlled)": {
            "referral_inflation": 0.0,
            "growth_delta": -0.5,
            "housing_delta": -0.4
        },

        "Worst Case (System Pressure)": {
            "referral_inflation": 1.8,
            "growth_delta": 1.0,
            "housing_delta": 0.8
        },
    }


def get_scenario(name: str) -> ScenarioConfig:
    """
    Safely retrieve a scenario configuration.
    Raises a clear error if not found.
    """
    scenarios = scenario_presets()
    if name not in scenarios:
        raise ValueError(f"Scenario '{name}' not found.")
    return scenarios[name]
