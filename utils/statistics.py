# utils/statistics.py

import numpy as np
from typing import List, Tuple

def ci95(arr: List[float]) -> Tuple[float, float]:
    """
    Compute a 95% confidence interval using the 2.5th and 97.5th percentiles.

    Parameters
    ----------
    arr : List[float]
        List of numerical samples (e.g., Monte Carlo outputs).

    Returns
    -------
    Tuple[float, float]
        Lower and upper bounds of the 95% interval.
        Returns (0.0, 0.0) if input is empty.
    """
    if not arr:
        return (0.0, 0.0)
    
    a = np.asarray(arr)
    lower = float(np.percentile(a, 2.5))
    upper = float(np.percentile(a, 97.5))
    return (lower, upper)
