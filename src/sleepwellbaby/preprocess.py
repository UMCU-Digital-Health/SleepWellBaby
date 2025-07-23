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
minimum_coverage_features = 0.5  # minimum percentage of data completeness in lookback window
vitals_freq = 0.4  # Frequency of vital parameter data, Hz
lookback_windows = [60, 120, 240, 480]  # lookback windows in seconds

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
    # NANs (coded as 0 or -1) are implicitely removed in the rescale function
    return df

def rescale(
    v: np.ndarray, ref24h_mean: float, ref24h_std: float
) -> np.ndarray:
    """
    Scale values based on the mean and standard deviation of the past 24 hours.

    Parameters
    ----------
    v : np.ndarray
        Array of parameter values.
    ref24h_mean : float
        Mean of ref24h values of the patient.
    ref24h_std : float
        Standard deviation of ref24h values of the patient.

    Returns
    -------
    np.ndarray
        Scaled parameter values.
    """
    v = v.astype(float)
    v[v <= 1e-10] = np.nan  # convert 0 and -1 to nan

    scaler = StandardScalerWithoutFit(ref24h_mean, ref24h_std)
    return scaler.transform(v.reshape(-1, 1))

def ref24h_correction(df: pd.DataFrame, data: dict) -> pd.DataFrame:
    """
    Scales and corrects data based on ref24h and ref2h values.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing vital parameter values.
    data : dict
        Payload containing median values for ref24h and ref2h of each parameter.

    Returns
    -------
    pd.DataFrame
        DataFrame containing scaled parameter values based on personal reference values.
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

def calculate_features(
    df_windows: pd.DataFrame, n_jobs: int = 0
) -> pd.DataFrame:
    """
    Calculate features for provided window-dataframe.

    Parameters
    ----------
    df_windows : pd.DataFrame
        DataFrame containing columns:
            "id": tuple (group id, time of window), used for groupby
            PR_N_COL: parameter name of value
            PR_V_COL: parameter value of row
            TIME_COL: time of row
    n_jobs : int, optional
        Number of jobs to run in parallel during extract_features. Defaults to 0.

    Returns
    -------
    pd.DataFrame
        DataFrame with calculated features.
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

        # add window lookback indicator to parameter name (e.g. HR__0_60)
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
        # Only filter if there are any rows left after filtering, otherwise keep all
        mask = df_features[col] >= int(far_past * vitals_freq * minimum_coverage_features)
        if mask.any():
            df_features = df_features[mask]
        # Drop length column
        df_features = df_features.drop(columns=[col])

    # Drop sum_values columns, as these are a derivative of __mean for our complete data
    df_features = df_features.drop(
        columns=[i for i in df_features.columns if re.search("__sum_values$", i)]
    )

    # unpack id
    df_features[[PT_COL, TIME_COL]] = [list(i) for i in df_features.index]
    df_features = df_features.reset_index(drop=True)

    # If the dataframe is empty after filtering, return a single row of NaNs with correct columns
    if df_features.shape[0] == 0:
        nan_row = pd.DataFrame(
            [[np.nan] * len(df_features.columns)],
            columns=df_features.columns
        )
        return nan_row

    return df_features


def convert_to_features(df):
    """
    Calculates features from parameter values.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing rescaled parameter values.

    Returns
    -------
    pd.DataFrame
        DataFrame containing extracted features.
    """
    # Stack dataframe
    df.columns = pd.MultiIndex.from_tuples([(PR_V_COL, c) for c in df.columns])
    df = df.stack().reset_index()
    df = df.rename(columns={"level_0": TIME_COL, "level_1": PR_N_COL})
    # Add a timestamp to each row, assumes last value in value lists to be newest
    df[TIME_COL] = df[TIME_COL] / vitals_freq + 1./vitals_freq
    # Add ids as expected by `calculate_features`
    df["id"] = [(1, int(max(lookback_windows))) for _ in range(df.shape[0])]
    # Calculate features
    df = calculate_features(df)
    return df

def pipeline(
    payload: dict, 
    model_support_dict: dict
) -> pd.DataFrame:
    """
    Preprocess data to DataFrame to predict on.

    Parameters
    ----------
    payload : dict
        Dictionary containing parameter values, ref2h metrics, and ref24h metrics.
    model_support_dict : dict
        Dictionary containing model meta information, including names of feature columns.

    Returns
    -------
    pd.DataFrame
        DataFrame containing extracted features, ready for prediction.
    """
    return (
        dict_to_df(payload)
        .pipe(ref24h_correction, payload)
        .pipe(convert_to_features)
        .reindex(columns=model_support_dict["Xcol"])
    )