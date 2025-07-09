import numpy as np
import pandas as pd

from src.api import logs, model, model_support
from src.api.data_structures import v_mean_median, v_std
from src.utils.config_helpers import config_minmax_week
from src.utils.constants import PR_N_COL, PR_V_COL, TIME_COL
from src.utils.model.predictions import return_y_pred
from src.utils.preprocess.features import calculate_features, feature_pasts
from src.utils.preprocess.normalization import scale_and_correct


def data_eligibility(data):
    """Eligibility check of data completeness"""
    # Test if there are max 50% nan (defined as -1 or 0) for all time windows for all
    # series of values.
    # NANs (coded as 0 or -1) are implicitely removed at normalization,
    # as scale_and_correct only considers values of > 0.
    def relative_n_nans(v):
        return np.mean([(i <= 0) for i in v])

    values = [v["values"] for k, v in data.items() if "param_" in k]
    for past in feature_pasts:
        n_values = int(past / 2.5)
        # Assumes last value in value lists to be newest
        data_elig = all(relative_n_nans(pr[-n_values:]) <= 0.5 for pr in values)
        if not data_elig:
            return False
    return True


def age_eligibility(data):
    """Eligibility check of gestational age"""
    time_lmp = pd.to_datetime(data["birth_date"], format="%Y-%m-%d") - pd.DateOffset(
        days=data["gestation_period"]
    )
    current_gest_age = (pd.Timestamp.today() - time_lmp).days / 7
    age_elig = config_minmax_week(current_gest_age)
    return age_elig


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


def params_to_df(data):
    """Processes received data to dataframe

    Args:
        data (dict): containing parameter values

    Returns:
        pd.DataFrame: processed data, with a column for each parameter
    """
    to_df = {}
    for k, v in data.items():
        if "param_" not in k:
            continue
        to_df[k.split("param_")[1]] = v["values"]
    df = pd.DataFrame(to_df)
    # NANs (coded as 0 or -1) are implicitely removed at normalization,
    # as scale_and_correct only considers values of > 0.
    return df


def ref24h_correction(df, data):
    """Scales and corrects data based on ref24h and ref2h values

    Args:
        df (pd.DataFrame): containing parameter values
        data (dict): containing median values for ref24h and ref2h of each parameter

    Returns:
        pd.DataFrame: containing median-corrected parameter values
    """
    for pr in df.columns:
        pr_values = data[f"param_{pr}"]
        median_ratio = pr_values["ref24h_median"] / pr_values["ref2h_median"]
        df[pr] = scale_and_correct(
            v=df[pr],
            pr=pr,
            ref24h_mean=pr_values["ref24h_mean"],
            ref24h_std=pr_values["ref24h_std"],
            mode_ratio=None,
            median_ratio=median_ratio,
            train_pt=False,
        )
    return df


def convert_to_features(df):
    """Calculates features from parameter values

    Args:
        df (pd.DataFrame): containing median-corrected parameter values

    Returns:
        pd.DataFrame: containing features
    """
    # Stack dataframe
    df.columns = pd.MultiIndex.from_tuples([(PR_V_COL, c) for c in df.columns])
    df = df.stack().reset_index()
    df = df.rename(columns={"level_0": TIME_COL, "level_1": PR_N_COL})
    # Add a timestamp to each row, assumes last value in value lists to be newest
    df[TIME_COL] = df[TIME_COL] * 2.5 + 2.5
    # Add ids as expected by `calculate_features`
    df["id"] = [(1, int(max(feature_pasts))) for _ in range(df.shape[0])]
    # Calculate features
    df = calculate_features(df)
    return df


def process_prediction(pred_proba, classes):
    """Process predicted probabilities

    Args:
        pred_proba (array-like): predicted probabilities per class
        classes (list-like): class labels

    Returns:
        tuple: prediction, labeled probabilities
    """
    pred = return_y_pred(pred_proba, classes)
    readable_pred = {
        "AS": "active_sleep",
        "QS": "quiet_sleep",
        "W": "wake",
    }
    pred = readable_pred[pred[0]]
    for i in readable_pred.values():
        logs.log_lists[i].append(pred == i)
    proba_dict = {readable_pred[k]: v for k, v in zip(classes, *pred_proba)}
    return pred, proba_dict


def preprocess(data):
    """Preprocess data to df to predict on

    Args:
        data (dict): containing parameter values, ref2h metrics and ref24h metrics

    Returns:
        pd.DataFrame: containing features
    """
    return (
        params_to_df(data)
        .pipe(ref24h_correction, data)
        .pipe(convert_to_features)
        .reindex(columns=model_support["Xcol"])
    )


def process(data):
    """Preprocess and predict on data

    Args:
        data (dict): containing parameter values, ref2h metrics and ref24h metrics

    Returns:
        tuple: prediction, labeled probabilities
    """
    if not check_eligibility(data):
        return False

    df = preprocess(data)
    pred_proba = model.predict_proba(df)
    pred, proba_dict = process_prediction(pred_proba, model["classifier"].classes_)
    return pred, proba_dict
