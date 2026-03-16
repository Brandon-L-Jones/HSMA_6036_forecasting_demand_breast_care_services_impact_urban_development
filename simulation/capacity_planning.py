# simulation/capacity_planning.py

"""
Capacity planning module.

Searches for minimum resource configuration required
to meet a performance target under stochastic simulation.

Used for strategic workforce planning.
"""

from typing import Dict, Any
from simulation.monte_carlo import run_mc
from simulation.des_model import SimInputs, ResourcesConfig
from copy import deepcopy


def safe_capacity_search(
    base_inputs: SimInputs,
    base_resources: ResourcesConfig,
    target_wait_days: float = 14.0,
    max_iterations: int = 20,
    step_size: int = 1,
    runs: int = 30,
) -> Dict[str, Any]:

    current_resources = deepcopy(base_resources)
    iteration = 0

    while iteration < max_iterations:

        test_inputs = SimInputs(
            daily_referrals=base_inputs.daily_referrals,
            service_times=base_inputs.service_times,
            pathway_probs=base_inputs.pathway_probs,
            resources=current_resources,
            sim_days=base_inputs.sim_days,
            warm_up=base_inputs.warm_up,
        )

        results = run_mc(test_inputs, n_runs=runs)

        mean_wait = results["mean_wait"]["mean"]

        if mean_wait <= target_wait_days:
            return {
                "required_resources": current_resources,
                "achieved_wait": mean_wait,
                "iterations": iteration,
            }

        # Increase capacity
        current_resources = ResourcesConfig(
            clinic_rooms=max(1, current_resources.clinic_rooms + step_size),
            imaging_slots=max(1, current_resources.imaging_slots + step_size),
            biopsy_slots=max(1, current_resources.biopsy_slots + step_size),
        )

        iteration += 1

    return {
        "required_resources": current_resources,
        "achieved_wait": mean_wait,
        "iterations": iteration,
        "warning": "Target not achieved within max_iterations",
    }



# def safe_capacity_search(
#     base_inputs: SimInputs,
#     base_resources: ResourcesConfig,
#     target_wait_days: float = 14.0,
#     max_iterations: int = 20,
#     step_size: int = 1,
#     runs: int = 30,
# ) -> Dict[str, Any]:
#     """
#     Incrementally increases capacity until the mean waiting time
#     falls below the target threshold.

#     Parameters:
#     - base_inputs: Simulation inputs
#     - base_resources: Starting resource configuration
#     - target_wait_days: Target mean wait threshold (e.g. 14 days)
#     - max_iterations: Safety cap on search
#     - step_size: Increment in staff per iteration
#     - runs: Monte Carlo replications

#     Returns:
#     Dictionary containing:
#     - required_resources
#     - achieved_wait
#     - iterations
#     """

#     current_resources = base_resources
#     iteration = 0

#     while iteration < max_iterations:

#         # Update simulation inputs with current resources
#         test_inputs = SimInputs(
#             daily_referrals=base_inputs.daily_referrals,
#             service_times=base_inputs.service_times,
#             pathway_probs=base_inputs.pathway_probs,
#             resources=current_resources,
#             sim_days=base_inputs.sim_days,
#             warm_up=base_inputs.warm_up,
#         )

#         results = run_mc(test_inputs, n_runs=runs)

#         mean_wait = results["mean_wait"]["mean"]

#         if mean_wait <= target_wait_days:
#             return {
#                 "required_resources": current_resources,
#                 "achieved_wait": mean_wait,
#                 "iterations": iteration,
#             }

#         # Increase capacity (example: increase clinic slots)
#         current_resources = ResourcesConfig(
#             clinic_rooms=current_resources.clinic_rooms + step_size,
#             imaging_slots=current_resources.imaging_slots + step_size,
#             biopsy_slots=current_resources.biopsy_slots + step_size,
#         )

#         iteration += 1

#     # If target not met
#     return {
#         "required_resources": current_resources,
#         "achieved_wait": mean_wait,
#         "iterations": iteration,
#         "warning": "Target not achieved within max_iterations",
#     }
