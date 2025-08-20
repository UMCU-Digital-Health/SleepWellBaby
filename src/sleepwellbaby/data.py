import datetime
import json
import warnings

import importlib_resources
import numpy as np
import pandas as pd


def replace_today_placeholder(d: dict) -> dict:
    """Fill out current date placeholder in a dictionary.

    This function recursively searches through the input dictionary and replaces any value equal to
    '@today' with the current date in 'YYYY-MM-DD' format.

    Parameters
    ----------
    d : dict
        Input dictionary to process.

    Returns
    -------
    dict
        Dictionary with all '@today' values replaced by the current date.
    """
    for k, v in d.items():
        if isinstance(v, dict):
            d[k] = replace_today_placeholder(d[k])
        if v == "@today":
            d[k] = datetime.date.today().strftime(r"%Y-%m-%d")
    return d


def get_example_payload():
    """
    Loads and returns the example payload from the 'example_payload.json' file located in the 'templates' directory of the 'sleepwellbaby' package.

    Returns
    -------
      dict: The parsed JSON payload as a Python dictionary.

    Raises
    ------
      FileNotFoundError: If the 'example_payload.json' file does not exist.
      json.JSONDecodeError: If the file contents are not valid JSON.
    """
    # my_resources = importlib_resources.files("sleepwellbaby")
    # data_bytes = my_resources.joinpath("templates", "example_payload.json").read_bytes()
    # payload = json.loads(
    #     data_bytes.decode("utf-8"), object_hook=replace_today_placeholder
    # )
    # return payload
    resource_path = importlib_resources.files("sleepwellbaby").joinpath("templates", "example_payload.json")

    with resource_path.open("r", encoding="utf-8") as f:
        payload = json.load(f, object_hook=replace_today_placeholder)
    return payload


def generate_mock_signalbase_data(duration: int = 48, freq: str = 'S') -> pd.DataFrame:
    """
    Generates a mock DataFrame simulating SignalBase data for a given duration in hours.

    Parameters
    ----------
    duration : int, optional
        Duration in hours for which to generate data. Default is 48.
    freq : str, optional
        Frequency of the generated timestamps. Options are:
            - 'S': 1-second intervals (default)
            - '2s500ms': 2.5-second intervals

    Returns
    -------
    pandas.DataFrame
        DataFrame containing the following columns:
            - 'datetime': Timestamps at 1-second intervals.
            - 'HR': Simulated heart rate values (mean=150, std=20).
            - 'RESP': Simulated respiration rate values (mean=50, std=15).
            - 'SpO2': Simulated oxygen saturation values (random integers between 85 and 99).
            - 'ID': Constant identifier value (1).
    """

    if freq not in ['S', '2s500ms']:
        raise ValueError(f"freq must be 'S' or '2s500ms', got {freq}.")

    periods = duration*60*60
    if freq == '2s500ms':
        periods = int(periods / 2.5)

    df = pd.DataFrame({
        'datetime': pd.date_range(start='2000-01-01', periods=periods, freq=freq)
    })
    df['HR'] = np.random.normal(150, scale=20, size=periods)
    df['RESP'] = np.random.normal(50, scale=15, size=periods)
    df['SpO2'] = np.random.choice(range(85, 100), size=periods)
    df['ID'] = 1
    return df

def compute_reference_values(
    df: pd.DataFrame,
    freq: float = 1,
    tolerance_2: float = 0.10,
    tolerance_24: float = 0.05
) -> pd.DataFrame:
    """
    Computes rolling mean and standard deviation for heart rate (HR), respiration rate (RESP),
    and oxygen saturation (SpO2) over 2-hour and 24-hour windows.

    Parameters
    ----------
        df (pd.DataFrame): Input DataFrame containing columns 'HR', 'RESP', and 'SpO2'.
        freq (int, optional): Sampling frequency in Hz (default is 1).
        tolerance_2 (float, optional): Minimum fraction of expected samples required for 2-hour window (default is 0.10, similar to BedBase implementation).
        tolerance_24 (float, optional): Minimum fraction of expected samples required for 24-hour window (default is 0.05, similar to BedBase implementation).

    Returns
    -------
        pd.DataFrame: DataFrame with additional columns for rolling mean and standard deviation:
            - 'HR_2h_mean', 'RESP_2h_mean', 'SpO2_2h_mean'
            - 'HR_2h_std', 'RESP_2h_std', 'SpO2_2h_std'
            - 'HR_24h_mean', 'RESP_24h_mean', 'SpO2_24h_mean'
            - 'HR_24h_std', 'RESP_24h_std', 'SpO2_24h_std'
    """

    # 2 hours
    df[['HR_2h_mean', 'RESP_2h_mean', 'SpO2_2h_mean']] = df[['HR', 'RESP', 'SpO2']].rolling(window=pd.Timedelta(2, 'h'), min_periods=int(freq*tolerance_2*2*60*60)).mean()
    df[['HR_2h_std', 'RESP_2h_std', 'SpO2_2h_std']] = df[['HR', 'RESP', 'SpO2']].rolling(window=pd.Timedelta(2, 'h'), min_periods=int(freq*tolerance_2*2*60*60)).std()

    # 24 hours
    df[['HR_24h_mean', 'RESP_24h_mean', 'SpO2_24h_mean']] = df[['HR', 'RESP', 'SpO2']].rolling(window=pd.Timedelta(24, 'h'), min_periods=int(freq*tolerance_24*24*60*60)).mean()
    df[['HR_24h_std', 'RESP_24h_std', 'SpO2_24h_std']] = df[['HR', 'RESP', 'SpO2']].rolling(window=pd.Timedelta(24, 'h'), min_periods=int(freq*tolerance_24*24*60*60)).std()

    return df

def convert_to_payload(
    df: pd.DataFrame,
    birth_date: str = None,
    gestation_period: int = None
) -> dict:
    """
    Converts a DataFrame containing physiological measurements into a structured payload dictionary.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame with 192 rows, indexed by datetime or containing a 'datetime' column.
        Must contain columns: 'HR', 'RESP', 'SpO2', 'HR_2h_mean', 'HR_2h_std', 'HR_24h_mean', 'HR_24h_std',
        'RESP_2h_mean', 'RESP_2h_std', 'RESP_24h_mean', 'RESP_24h_std',
        'SpO2_2h_mean', 'SpO2_2h_std', 'SpO2_24h_mean', 'SpO2_24h_std'.
    birth_date : str, optional
        Birth date in 'YYYY-MM-DD' format. If None, defaults to today's date.
    gestation_period : int, optional
        Gestation period in days. If None, defaults to 210.

    Returns
    -------
    payload : dict
        Dictionary containing birth date, gestation period, observation date, and structured parameters
        for heart rate (HR), respiration rate (RESP), and oxygen saturation (SpO2), including reference
        means, standard deviations, and value lists (missing values filled with -1).

    Raises
    ------
    AssertionError
        If the DataFrame does not have exactly 192 rows or its index is not monotonic increasing.
    """
    if birth_date is None:
        warnings.warn("birth_date is not specified. Setting to today's date.", UserWarning, stacklevel=2)
        birth_date = datetime.datetime.today().strftime('%Y-%m-%d')
    if gestation_period is None:
        gestation_period = 210


    if len(df) != 192:
        raise ValueError(f"DataFrame must have exactly 192 rows, got {len(df)}.")
    # Ensure index is DatetimeIndex or set it from 'datetime' column if available
    if not isinstance(df.index, pd.DatetimeIndex):
        if 'datetime' in df.columns:
            df = df.set_index('datetime')
        else:
            raise ValueError("DataFrame must have a DatetimeIndex or a 'datetime' column.")
    if not df.index.is_monotonic_increasing:
        raise ValueError("DataFrame index must be monotonic increasing.")

    row = df.iloc[-1]

    if isinstance(row.name, datetime.datetime):
        observation_date = str(row.name.date())
    elif "datetime" in row.keys():
        if isinstance(row['datetime'], datetime.datetime):
            observation_date = str(row['datetime'].date())
    else:
        # set to today
        observation_date = datetime.datetime.today().strftime('%Y-%m-%d')

    payload = {
    "birth_date": birth_date,
    "gestation_period": gestation_period,
    "observation_date": observation_date,
    "param_HR": {
        "ref2h_mean": row['HR_2h_mean'],
        "ref2h_std": row['HR_2h_std'],
        "ref24h_mean": row['HR_24h_mean'],
        "ref24h_std": row['HR_24h_std'],
        "values": df['HR'].fillna(-1).values.tolist()
    },
    "param_RR": {
        "ref2h_mean": row['RESP_2h_mean'],
        "ref2h_std": row['RESP_2h_std'],
        "ref24h_mean": row['RESP_24h_mean'],
        "ref24h_std": row['RESP_24h_std'],
        "values": df['RESP'].fillna(-1).values.tolist()
    },
    "param_OS": {
        "ref2h_mean": row['SpO2_2h_mean'],
        "ref2h_std": row['SpO2_2h_std'],
        "ref24h_mean": row['SpO2_24h_mean'],
        "ref24h_std": row['SpO2_24h_std'],
        "values": df['SpO2'].fillna(-1).values.tolist()
        }
    }
    return payload
