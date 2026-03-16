# simulation/monte_carlo.py

"""
Monte Carlo wrapper for DES.

Runs multiple stochastic replications of the pathway simulation
and computes confidence intervals for key metrics.
"""

from typing import Dict, List
import numpy as np
from simulation.des_model import run_sim_once, SimInputs
from utils.statistics import ci95


def run_mc(inputs: SimInputs, n_runs: int = 50) -> Dict[str, Dict[str, float]]:
    """
    Run Monte Carlo simulation.

    Args:
        inputs (SimInputs): Simulation inputs
        n_runs (int): Number of stochastic replications

    Returns:
        Dict with metrics and 95% CIs
    """

    mean_waits: List[float] = []
    p95_waits: List[float] = []
  

    for i in range(n_runs):
        result = run_sim_once(inputs)
        mean_waits.append(result["mean_wait"])
        p95_waits.append(result["p95_wait"])


    summary = {
        "mean_wait": {
            "mean": float(np.mean(mean_waits)),
            "ci95_low": ci95(mean_waits)[0],
            "ci95_high": ci95(mean_waits)[1],
        },
        "p95_wait": {
            "mean": float(np.mean(p95_waits)),
            "ci95_low": ci95(p95_waits)[0],
            "ci95_high": ci95(p95_waits)[1],
        },
    }


    return summary
