## utils/helpers.py

def minutes_to_days(mins: float) -> float:
    """
    Convert minutes to model time assuming 8-hour working day.

    This makes 1 model day represent 1 working day (8 hours),
    rather than 24 hours.
    """
    WORKING_MINUTES_PER_DAY = 8 * 60  # 480 minutes
    return max(0.0007, mins / WORKING_MINUTES_PER_DAY)


def clamp01(x: float) -> float:
    """
    Clamp a value between 0 and 1.

    Useful for probabilities or proportions in simulations.
    """
    return max(0.0, min(1.0, x))
