# forecast/demand_model.py

"""
Demand model for RDUH Breast 2WW forecasting.

This module defines the deterministic demand growth mechanism.
It applies:

1. Population growth
2. Housing growth
3. Referral behaviour inflation
4. Age-weighted demand scaling

Growth is compounded annually.
"""

from dataclasses import dataclass


@dataclass
class DemandParams:
    # Baseline (Year 0)
    baseline_daily: float  # baseline daily referrals

    # Growth assumptions (% per year)
    growth: float
    housing: float
    referral_inflation: float

    # Age distribution (must sum approx 1.0)
    age_u40: float
    age_40_49: float
    age_50_plus: float

    # Relative demand weights (modifiable if required)
    w_u40: float = 0.5
    w_40_49: float = 1.0
    w_50_plus: float = 1.5

    def __post_init__(self):
        """Basic validation to improve model safety."""
        age_sum = self.age_u40 + self.age_40_49 + self.age_50_plus

        if not 0.95 <= age_sum <= 1.05:
            raise ValueError(
                f"Age proportions must sum to ~1.0. Currently: {age_sum:.3f}"
            )

        if self.baseline_daily < 0:
            raise ValueError("Baseline daily demand cannot be negative.")

    # -----------------------------
    # Core Model Components
    # -----------------------------

    def age_weight(self) -> float:
        """
        Computes weighted demand multiplier based on age mix.
        Higher age groups generate greater diagnostic demand.
        """
        return (
            self.age_u40 * self.w_u40
            + self.age_40_49 * self.w_40_49
            + self.age_50_plus * self.w_50_plus
        )

    def annual_growth_factor(self) -> float:
        """
        Combined annual multiplicative growth factor.
        Includes population + housing + referral behaviour.
        """
        g_total = (self.growth + self.housing) / 100.0
        r_infl = self.referral_inflation / 100.0

        # Multiplicative compounding
        return (1.0 + g_total) * (1.0 + r_infl)

    def daily_demand_at_year(self, y: float) -> float:
        """
        Returns projected daily demand at year y.
        Growth is compounded annually.
        """
        factor = self.annual_growth_factor() ** y
        return self.baseline_daily * self.age_weight() * factor

    def annual_demand_at_year(self, y: float) -> float:
        """
        Returns projected annual demand at year y.
        """
        return self.daily_demand_at_year(y) * 365.0
