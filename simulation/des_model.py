# simulation/des_model.py

"""
Discrete Event Simulation (DES) for Breast 2WW pathway.

Simulates:
- Referral arrivals
- Clinic assessment
- Imaging
- Biopsy

Outputs waiting time metrics for capacity planning.
"""

import simpy
import random
import numpy as np
from dataclasses import dataclass
from typing import Dict, List
from utils.helpers import minutes_to_days


# ------------------------------
# Configuration Data Classes
# -----------------------------

@dataclass
class ServiceTimes:
    clinic_mean_mins: float
    imaging_mean_mins: float
    biopsy_mean_mins: float


@dataclass
class PathwayProbs:
    imaging_prob: float
    biopsy_prob: float


@dataclass
class ResourcesConfig:
    clinic_rooms: int
    imaging_slots: int
    biopsy_slots: int


@dataclass
class SimInputs:
    daily_referrals: float
    service_times: ServiceTimes
    pathway_probs: PathwayProbs
    resources: ResourcesConfig
    sim_days: int = 180
    warm_up: int = 30


# -----------------------------
# Core Simulation
# -----------------------------

def run_sim_once(inputs: SimInputs) -> Dict[str, float]:

    env = simpy.Environment()

    # Resources
    clinic = simpy.Resource(env, capacity=inputs.resources.clinic_rooms)
    imaging = simpy.Resource(env, capacity=inputs.resources.imaging_slots)
    biopsy = simpy.Resource(env, capacity=inputs.resources.biopsy_slots)

    wait_times: List[float] = []

    def patient(env):

        arrival_time = env.now

        # --- Clinic ---
        with clinic.request() as req:
            yield req
            yield env.timeout(
                minutes_to_days(
                    random.expovariate(1.0 / inputs.service_times.clinic_mean_mins)
                )
            )

            # --- Imaging ---
            imaging_done = False
            
            if random.random() < inputs.pathway_probs.imaging_prob:
                imaging_done = True
                with imaging.request() as req:
                    yield req
                    yield env.timeout(
                        minutes_to_days(
                            random.expovariate(1.0 / inputs.service_times.imaging_mean_mins)
                        )
                    )
            
            # --- Biopsy ---
            if imaging_done and random.random() < inputs.pathway_probs.biopsy_prob:
                with biopsy.request() as req:
                    yield req
                    yield env.timeout(
                        minutes_to_days(
                            random.expovariate(1.0 / inputs.service_times.biopsy_mean_mins)
                        )
                    )

        total_time = env.now - arrival_time

        if env.now > inputs.warm_up:
            wait_times.append(total_time)

    def arrival_process(env):

        while True:
            yield env.timeout(
                random.expovariate(inputs.daily_referrals)
            )
            env.process(patient(env))

    env.process(arrival_process(env))
    env.run(until=inputs.sim_days)

    if not wait_times:
        return {
            "mean_wait": 0.0,
            "p95_wait": 0.0,
        }

    return {
        "mean_wait": float(np.mean(wait_times)),
        "p95_wait": float(np.percentile(wait_times, 95)),
    }
