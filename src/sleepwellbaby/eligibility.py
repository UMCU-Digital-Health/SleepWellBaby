import numpy as np
import pandas as pd

from sleepwellbaby import logger
from sleepwellbaby.preprocess import lookback_windows, vitals_freq

pma_range = [28, 34]  # weeks, lo <= PMA < hi
reference_ranges = {
    "param_HR": {
        "mean": {"min": 100, "max": 220},
        "std": {
            "min": 0,
            "max": 25,
        },
    },
    "param_RR": {
        "mean": {"min": 20, "max": 90},
        "std": {
            "min": 0,
            "max": 30,
        },
    },
    "param_OS": {"mean": {"min": 85, "max": 100}, "std": {"min": 0, "max": 10}},
}


def data_eligibility(payload: dict) -> bool:
    """
    Checks if data completeness is sufficient for eligibility.

    For each parameter in the payload, verifies that no more than 50% of values are missing
    (missing values are coded as 0 or -1) in all lookback windows.

    Parameters
    ----------
        payload (dict): Dictionary containing parameter values.

    Returns
    -------
        bool: True if data completeness is sufficient, False otherwise.
    """

    def relative_n_nans(v: list) -> float:
        return np.mean([(i <= 0) for i in v])

    values = [v["values"] for k, v in payload.items() if "param_" in k]
    for past in lookback_windows:
        n_values = int(past * vitals_freq)
        # Assumes last value in value lists to be newest
        data_elig = all(relative_n_nans(pr[-n_values:]) <= 0.5 for pr in values)
        if not data_elig:
            return False
    return True


def age_eligibility(payload: dict) -> bool:
    """Check eligibililty based on postmenstrual age on the date of observation."""
    birth_date = pd.to_datetime(payload["birth_date"], format="%Y-%m-%d")
    observation_date = payload["observation_date"]
    chronological_age = birth_date - pd.DateOffset(days=payload["gestation_period"])

    if observation_date is None:
        observation_date = pd.Timestamp.today()
    else:
        observation_date = pd.to_datetime(observation_date, format="%Y-%m-%d")
        if observation_date < birth_date:
            raise ValueError("Observation date cannot be before birth date.")

    pma = (observation_date - chronological_age).days / 7

    return (pma_range[0] <= pma) & (pma < pma_range[1])


def reference_eligibility(payload: dict) -> bool:
    """Eligibility check of reference values"""

    keys_mean = ["ref2h_mean", "ref24h_mean"]
    keys_std = ["ref2h_std", "ref24h_std"]
    for k, v in payload.items():
        if not k.startswith("param_"):
            continue
        for stat, stat_range in reference_ranges[k].items():
            if stat == "std":
                # lower bound not included, upper include
                if any(v[i] <= stat_range["min"] for i in keys_std):
                    return False
                if any(v[i] > stat_range["max"] for i in keys_std):
                    return False
            elif stat == "mean":
                # lower and upper bound included
                if any(v[i] < stat_range["min"] for i in keys_mean):
                    return False
                if any(v[i] > stat_range["max"] for i in keys_mean):
                    return False
    return True


def check_eligibility(payload: dict) -> bool:
    """
    Checks eligibility based on gestational age and data completeness.

    Parameters
    ----------
    payload : dict
        Dictionary containing parameter values.

    Returns
    -------
    bool
        True if patient is eligible based on data received, False otherwise.
    """
    age_elig = age_eligibility(payload)
    if not age_elig:
        logger.info("Patient does not meet PMA criteria")
    data_elig = data_eligibility(payload)
    if not data_elig:
        logger.info("Data completeness criteria not met")
    ref_elig = reference_eligibility(payload)
    if not ref_elig:
        logger.info("Reference values out of bounds")

    return age_elig & data_elig & ref_elig
