import pandas as pd
import pytest

from sleepwellbaby.data import compute_reference_values, generate_mock_signalbase_data
from sleepwellbaby.utils import get_swb_predictions


def test_get_swb_predictions():

    # Generate mock data with 1Hz frequency
    for freq in ['S', '2s500ms']:
        df = generate_mock_signalbase_data(freq=freq).sort_values(by='datetime').set_index('datetime')
        df = compute_reference_values(df, freq=1)

        # Select two timestamps 1min apart
        # Get indices of times at which you want to get an SWB value (we only compute it at whole minutes)
        t_range_swb = pd.date_range(start=df.index.min().round(freq='min'), end=df.index.max().round(freq='min'), freq='1min')[-10:-8]

        df_pred, columns = get_swb_predictions(df, t_range_swb, birth_date='2000-01-01', gestation_period=210, freq=freq)

        assert isinstance(df_pred, pd.DataFrame)
        assert isinstance(columns, list)
        assert all(col in df_pred.columns for col in columns)
        assert df_pred.loc[t_range_swb[0]].notnull().any()
        assert df_pred.loc[t_range_swb[1]].notnull().any()

        # Check that valueerror is raised if too many elements are missing from the list
        if freq == 'S':
            with pytest.raises(ValueError, match="of the timestamps missing from DataFrame index"):
                get_swb_predictions(df, t_range_swb, freq='2s500ms', birth_date='2000-01-01', gestation_period=210)
            # No valueerror when threshold is set to 1
            try:
                df_pred, columns = get_swb_predictions(df, t_range_swb, freq='2s500ms', birth_date='2000-01-01', gestation_period=210, missing_index_threshold=1)
            except ValueError:
                pytest.fail("ValueError was raised when missing_index_threshold=1")
        if freq == '2s500ms':
            with pytest.raises(ValueError, match="of the timestamps missing from DataFrame index"):
                get_swb_predictions(df, t_range_swb, birth_date='2000-01-01', gestation_period=210, freq='S')
            try:
                df_pred, columns = get_swb_predictions(df, t_range_swb,birth_date='2000-01-01', gestation_period=210, freq='S', missing_index_threshold=1)
            except ValueError:
                pytest.fail("ValueError was raised when missing_index_threshold=1")
