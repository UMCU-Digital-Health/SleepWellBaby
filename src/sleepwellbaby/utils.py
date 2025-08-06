from typing import Iterable, List, Tuple

import pandas as pd
from tqdm import tqdm

from sleepwellbaby.data import convert_to_payload
from sleepwellbaby.model import get_prediction, load_model


# Helper function to get predictions
def get_swb_predictions(
    df: pd.DataFrame,
    indices: Iterable[pd.Timestamp],
    freq: str = 'S',
    missing_index_threshold: float = 0.1
) -> Tuple[pd.DataFrame, List[str]]:
    """
    Generate SleepWellBaby (SWB) predictions for specified timestamps in a DataFrame.

    For each timestamp in `indices`, this function extracts a window of data from the DataFrame,
    prepares the input payload, and uses a pre-trained model to predict sleep states and their probabilities.
    If required reference columns contain missing values, the prediction is marked as 'ineligible'.

    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame containing time-indexed data with feature columns, including those with 'mean' or 'std' in their names.
    indices : iterable of pandas.Timestamp
        List or array of timestamps at which to compute SWB predictions.
    freq : str, optional
        Frequency of the generated timestamps. Options are:
            - 'S': 1-second intervals (default)
            - '2s500ms': 2.5-second intervals
    missing_index_threshold : float, optional
        Maximum allowed fraction of missing timestamps in the window for a prediction to be attempted.
        If the fraction of missing timestamps exceeds this threshold, a ValueError is raised.
        Default is 0.1 (i.e., 10%).

    Returns
    -------
    df : pandas.DataFrame
        The input DataFrame with additional columns for predictions and class probabilities at the specified indices.
    columns : list of str
        List of class probability column names (e.g., ['AS', 'QS', 'W']).

    Notes
    -----
    - Predictions are computed for each timestamp using a window of the previous 8 minutes, sampled every 2.5 seconds.
    - If any required reference columns are missing for a timestamp, the prediction is set to 'ineligible' and probabilities to -1.
    - If more than `missing_index_threshold` fraction of timestamps are missing from the DataFrame index for a given window, a ValueError is raised.
    """
    model, model_support_dict = load_model()
    ref_columns = [c for c in df.columns if ('mean' in c) or ('std' in c)]
    for ix, t in enumerate(tqdm(indices, desc="Calculating SWB")):
        # Get the right timestamps for SWB, one every 2.5 seconds
        # For 1Hz data we round so we do not have to interpolate

        timestamps = pd.date_range(t - pd.Timedelta(8, 'm'), t, freq='2500ms', inclusive='right')
        if freq == 'S':
            timestamps = timestamps.round('1s')
        missing_timestamps = [ts for ts in timestamps if ts not in df.index]
        if len(missing_timestamps) / len(timestamps) > missing_index_threshold:
            raise ValueError(f"More than {missing_index_threshold*100}% of the timestamps missing from DataFrame index: n = {len(missing_timestamps)}")

        temp = df.reindex(index=timestamps)  # sets rows with missing indices to nan
        row = temp.iloc[-1]
        assert row.name == t

        # Check if reference values are defined
        if row[ref_columns].isna().any():
            pred = 'ineligible'
            proba_dict = {'AS': -1, 'QS': -1, 'W': -1}
        else:
            payload = convert_to_payload(temp, birth_date='2000-01-01')
            pred, proba_dict = get_prediction(payload, model, model_support_dict)
        columns =list(proba_dict.keys())
        if ix == 0:
            df.loc[:, 'prediction'] = None
            df.loc[:, columns] = None
        df.loc[t, 'prediction'] = pred
        df.loc[t, columns] = pd.DataFrame(proba_dict, index=[0,]).iloc[0]
    return df, columns
