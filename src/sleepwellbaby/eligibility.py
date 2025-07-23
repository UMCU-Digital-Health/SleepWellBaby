import numpy as np
import pandas as pd

from sleepwellbaby.model import get_prediction
from sleepwellbaby.preprocess import lookback_windows, vitals_freq


pma_range = [28, 34]  # weeks, lo <= PMA < hi

def data_eligibility(payload: dict) -> bool:
    """
    Checks if data completeness is sufficient for eligibility.

    For each parameter in the payload, verifies that no more than 50% of values are missing
    (missing values are coded as 0 or -1) in all lookback windows.

    Args:
        payload (dict): Dictionary containing parameter values.

    Returns:
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


def age_eligibility(payload: dict, observation_date: str = None) -> bool:
    """Check eligibililty based on postmenstrual age on the date of observation."""
    birth_date = pd.to_datetime(payload["birth_date"], format="%Y-%m-%d")
    chronological_age = birth_date - pd.DateOffset(
        days=payload["gestation_period"]
    )
    
    if observation_date is None:
        observation_date = pd.Timestamp.today()
    else:
        observation_date = pd.to_datetime(observation_date, format="%Y-%m-%d")
        if observation_date < birth_date:
            raise ValueError("Observation date cannot be before birth date.")


    pma = (observation_date - chronological_age).days / 7
    
    return (pma_range[0] <= pma) & (pma < pma_range[1])




def reference_eligibility(data):
    """Eligibility check of reference values"""

    def check_requirements(values, keys, requirements):
        """[summary]

        Args:
            values (dict): values to be checked against requirements
            keys (list): keys of `values` which values need to be checked
            requirements (dict): specifying the min and max allowed values

        Returns:
            bool: Whether key-value pairs conformed to requirements
        """
        if requirements.get("exclusiveMin", False):
            if any(values[i] <= requirements["min"] for i in keys):
                return False
        else:
            if any(values[i] < requirements["min"] for i in keys):
                return False
        if requirements.get("exclusiveMax", False):
            if any(values[i] >= requirements["max"] for i in keys):
                return False
        else:
            if any(values[i] > requirements["max"] for i in keys):
                return False
        return True

    for k, v in data.items():
        if not k.startswith("param_"):
            continue
        mean_median_check = check_requirements(
            values=v,
            keys=["ref2h_mean", "ref2h_median", "ref24h_mean", "ref24h_median"],
            requirements=v_mean_median[k],
        )
        std_check = check_requirements(
            values=v, keys=["ref2h_std", "ref24h_std"], requirements=v_std[k]
        )
        if not (mean_median_check and std_check):
            return False
    return True


def check_eligibility(data):
    """Eligibility check of gestational age and data completeness

    Args:
        data (dict): containing parameter values

    Returns:
        bool: if patient is eligible based on data received
    """
    age_elig = age_eligibility(data)
    data_elig = data_eligibility(data)
    ref_elig = reference_eligibility(data)

    logs.log_lists["age"].append(age_elig)
    logs.log_lists["missing_data"].append(data_elig)
    logs.log_lists["reference_data"].append(ref_elig)

    return age_elig & data_elig & ref_elig

def process(payload, model=None, model_support_dict=None):
    """Preprocess and predict on data

    Args:
        data (dict): containing parameter values, ref2h metrics and ref24h metrics

    Returns:
        tuple: prediction, labeled probabilities
    """
    if not check_eligibility(payload):
        return False

    pred, proba_dict = get_prediction(payload, model, model_support_dict)
    return pred, proba_dict