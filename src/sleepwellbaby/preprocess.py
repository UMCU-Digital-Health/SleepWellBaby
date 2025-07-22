import re
import warnings

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing._data import _handle_zeros_in_scale
from tsfresh.feature_extraction import MinimalFCParameters, extract_features

TIME_COL = "time_unix_epoch"
PR_N_COL = "parameter_name"
PR_V_COL = "parameter_value"
PT_COL = "patient"
lookback_windows = [60, 120, 240, 480]

class StandardScalerWithoutFit(StandardScaler):
    def __init__(self, mean, scale):
        super().__init__(copy=True, with_mean=True, with_std=True) 

        self.mean_ = mean
        self.scale_ = _handle_zeros_in_scale(scale)
        self.n_features_in_ = 1

def dict_to_df(data: dict) -> pd.DataFrame:
    """Extract vital parameters from payload (json) to dataframe."""

    to_df = {}
    for k, v in data.items():
        if "param_" not in k:
            continue
        to_df[k.split("param_")[1]] = v["values"]
    df = pd.DataFrame(to_df)
    # TODO: move comment
    # NANs (coded as 0 or -1) are implicitely removed at normalization,
    # as scale_and_correct only considers values of > 0.
    return df

def rescale(
    v, ref24h_mean: float, ref24h_std: float
):
    """Scales values based on mean and standard deviation of past 24h.

    Args:
        v array-like: parameter values
        ref24h_mean (float): mean of ref24h values of patient
        ref24h_std (float): std of ref24h values of patient

    Returns:
        array-like: scaled parameter values
    """
    # TODO add check that estimates whether scale isn't variance by accident?
    # Remove 0s before scaling
    v = v.astype(np.float)
    v[v <= 1e-10] = np.nan  # convert 0 and -1 to nan

    scaler = StandardScalerWithoutFit(ref24h_mean, ref24h_std)
    return scaler.transform(v.reshape(-1, 1))

def ref24h_correction(df: pd.DataFrame, data: dict):
    """Scales and corrects data based on ref24h and ref2h values.

    Args:
        df (pd.DataFrame): containing vital parameter values
        data (dict): payload containing median values for ref24h and ref2h of each parameter

    Returns:
        pd.DataFrame: containing median-corrected parameter values
    """
    for x in df.columns:
        if x == 'OS':
            continue
        elif x in ['HR', 'RR']:
            values = data[f"param_{x}"]
            df[x] = rescale(
                v=df[x].values,
                ref24h_mean=values["ref24h_mean"],
                ref24h_std=values["ref24h_std"],
        )
    return df

def calculate_features(df_windows, n_jobs=0):
    """Calculate features for provided window-dataframe

    Args:
        df_windows (pd.DataFrame): containing columns:
            "id": tuple(group id, time of window)
            `pr_n_col`: parameter name of value
            `pr_v_col`: parameter value of row
            `time_col`: time of row
        n_jobs (int, optional): n_jobs during extract_features. Defaults to 0.

    Returns:
        pd.DataFrame: calculated features
    """
    warnings.simplefilter("ignore")
    to_calculate = {
        **{k: v for k, v in MinimalFCParameters().items() if k != "standard_deviation"},
        "linear_trend": [
            {"attr": i} for i in ["pvalue", "rvalue", "intercept", "slope"]
        ],
    }

    # Duplicate df_windows for each past to calculate features on
    past_dfs = []
    for far_past in lookback_windows:
        df_i = df_windows.copy()
        # add window/past indicator to parameter name (e.g. HR__0_60)
        df_i[PR_N_COL] = df_i[PR_N_COL] + "__0_" + str(far_past)
        # remove rows from df_i where time of row falls outside of window
        mask = ([i[1] for i in df_i["id"]] - df_i[TIME_COL]) < far_past
        df_i = df_i[mask]
        past_dfs.append(df_i)
    df_windows = pd.concat(past_dfs)

    df_features = extract_features(
        df_windows,
        column_id="id",
        column_sort=TIME_COL,
        column_kind=PR_N_COL,
        column_value=PR_V_COL,
        n_jobs=n_jobs,
        default_fc_parameters=to_calculate,
    )
    for col in [i for i in df_features.columns if re.search("__length$", i)]:
        # Filter out rows that do not have enough measurements
        # to support feature calculation (i.e. too short length)
        # Criterium = minimally 50% coverage in all of the windows
        far_past = int(col.split("_")[3])
        df_features = df_features[df_features[col] >= int(far_past / 2.5 * 0.5)]
        # Drop length column
        df_features = df_features.drop(columns=[col])
    # Drop sum_values columns, as these are a derivative of __mean for our complete data
    df_features = df_features.drop(
        columns=[i for i in df_features.columns if re.search("__sum_values$", i)]
    )

    # unpack id
    df_features[[PT_COL, TIME_COL]] = [list(i) for i in df_features.index]
    return df_features


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
    df["id"] = [(1, int(max(lookback_windows))) for _ in range(df.shape[0])]
    # Calculate features
    df = calculate_features(df)
    return df

def pipeline(payload, model_support_dict):
    """Preprocess data to df to predict on

    Args:
        data (dict): containing parameter values, ref2h metrics and ref24h metrics

    Returns:
        pd.DataFrame: containing features
    """
    return (
        dict_to_df(payload)
        .pipe(ref24h_correction, payload)
        .pipe(convert_to_features)
        .reindex(columns=model_support_dict["Xcol"])
    )