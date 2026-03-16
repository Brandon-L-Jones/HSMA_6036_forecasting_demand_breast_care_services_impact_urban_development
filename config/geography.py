# config/geography.py

"""
Geography configuration for RDUH Breast Service Demand Forecasting Tool.

These values represent illustrative baseline assumptions for:
- Annual population growth (%)
- Additional housing-related growth (%)
- Baseline daily 2WW referrals (Year 0)
- Age distribution proportions

Replace with:
- ONS Subnational Population Projections (SNPP)
- Local Plan housing allocations
- SUS / RTT baseline referral data

Author: HSMA Project 6036
"""

from typing import Dict, TypedDict


class AgeDistribution(TypedDict):
    u40: float
    a40_49: float
    a50_plus: float


class GeographyConfig(TypedDict):
    growth: float
    housing: float
    baseline_referrals: int
    age: AgeDistribution


def geography_defaults() -> Dict[str, GeographyConfig]:
    """
    Returns baseline geography assumptions for RDUH catchment areas.

    growth  = population growth % per year
    housing = additional % demand growth from development
    baseline_referrals = daily referrals at Year 0
    age proportions must sum approximately to 1.0
    """

    return {

        "Exeter": {
            "growth": 1.3,
            "housing": 0.8,
            "baseline_referrals": 12,
            "age": {"u40": 0.38, "a40_49": 0.32, "a50_plus": 0.30}
        },

        "East Devon": {
            "growth": 0.9,
            "housing": 0.5,
            "baseline_referrals": 9,
            "age": {"u40": 0.34, "a40_49": 0.30, "a50_plus": 0.36}
        },

        "Mid Devon": {
            "growth": 0.8,
            "housing": 0.4,
            "baseline_referrals": 7,
            "age": {"u40": 0.35, "a40_49": 0.29, "a50_plus": 0.36}
        },

        "North Devon": {
            "growth": 0.7,
            "housing": 0.3,
            "baseline_referrals": 8,
            "age": {"u40": 0.33, "a40_49": 0.28, "a50_plus": 0.39}
        },

        "Torbay": {
            "growth": 0.6,
            "housing": 0.3,
            "baseline_referrals": 10,
            "age": {"u40": 0.31, "a40_49": 0.29, "a50_plus": 0.40}
        },

        "Teignbridge": {
            "growth": 0.9,
            "housing": 0.7,
            "baseline_referrals": 9,
            "age": {"u40": 0.36, "a40_49": 0.30, "a50_plus": 0.34}
        },

        "Plymouth": {
            "growth": 0.8,
            "housing": 0.6,
            "baseline_referrals": 11,
            "age": {"u40": 0.40, "a40_49": 0.31, "a50_plus": 0.29}
        },

        "Other": {
            "growth": 1.0,
            "housing": 0.5,
            "baseline_referrals": 10,
            "age": {"u40": 0.40, "a40_49": 0.30, "a50_plus": 0.30}
        },
    }


def get_geography(name: str) -> GeographyConfig:
    """
    Safely retrieve a single geography configuration.
    Raises clear error if not found.
    """
    geos = geography_defaults()
    if name not in geos:
        raise ValueError(f"Geography '{name}' not found in configuration.")
    return geos[name]
