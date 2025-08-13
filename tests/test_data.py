from io import BytesIO

import numpy as np
import pandas as pd
import pytest

from sleepwellbaby.data import (
    convert_to_payload,
    generate_mock_signalbase_data,
    get_example_payload,
)


def test_get_example_payload_success(monkeypatch):
    class DummyPath:
        def read_bytes(self):
            # Minimal valid JSON for the payload
            return b'{"observation_date": "2025-05-08"}'
        def open(self, mode='rb', encoding='utf-8'):
            # Simulate opening the resource file
            return BytesIO(self.read_bytes())
    class DummyResources:
        def joinpath(self, *args):
            return DummyPath()
    monkeypatch.setattr("importlib_resources.files", lambda pkg: DummyResources())
    payload = get_example_payload()
    assert isinstance(payload, dict)
    assert payload["observation_date"] == "2025-05-08"

def test_example_payload_dates():
    payload = get_example_payload()
    assert str(payload['birth_date']) == str(pd.Timestamp.today().date())
    assert payload['observation_date'] is None

def make_valid_df(with_datetime_col=False):
    # Non-deterministic tests due to random values; set random seed for reproducibility
    np.random.seed(42)
    # Create a DataFrame with 192 rows and required columns
    idx = pd.date_range("2001-01-01", periods=192, freq="2S500ms")
    data = {
        "HR": np.random.normal(150, 10, 192),
        "RESP": np.random.normal(50, 5, 192),
        "SpO2": np.random.randint(90, 100, 192),
        "HR_2h_mean": np.random.normal(150, 1, 192),
        "HR_2h_std": np.random.normal(5, 0.5, 192),
        "HR_24h_mean": np.random.normal(150, 1, 192),
        "HR_24h_std": np.random.normal(5, 0.5, 192),
        "RESP_2h_mean": np.random.normal(50, 1, 192),
        "RESP_2h_std": np.random.normal(2, 0.2, 192),
        "RESP_24h_mean": np.random.normal(50, 1, 192),
        "RESP_24h_std": np.random.normal(2, 0.2, 192),
        "SpO2_2h_mean": np.random.normal(95, 1, 192),
        "SpO2_2h_std": np.random.normal(1, 0.1, 192),
        "SpO2_24h_mean": np.random.normal(95, 1, 192),
        "SpO2_24h_std": np.random.normal(1, 0.1, 192),
    }
    df = pd.DataFrame(data, index=idx)
    if with_datetime_col:
        df = df.reset_index().rename(columns={"index": "datetime"})
        df["datetime"] = pd.to_datetime(df["datetime"])
        df = df.set_index(pd.Index(range(192)))  # Not monotonic datetime index
    return df

def test_convert_to_payload_basic():
    df = make_valid_df()
    assert len(df) == 192
    payload = convert_to_payload(df, birth_date="2023-01-01", gestation_period=220)
    assert isinstance(payload, dict)
    assert payload["birth_date"] == "2023-01-01"
    assert payload["gestation_period"] == 220
    assert "param_HR" in payload
    assert "param_RR" in payload
    assert "param_OS" in payload
    assert isinstance(payload["param_HR"]["values"], list)
    assert len(payload["param_HR"]["values"]) == 192
    assert isinstance(payload["observation_date"], str)
    # Check that the observation_date matches the last index date
    assert payload["observation_date"] == str(df.index[-1].date())

def test_convert_to_payload_warns_on_missing_birth_date():
    df = make_valid_df()
    # gestation_period is provided, but birth_date is None
    with pytest.warns(UserWarning, match="birth_date is not specified"):
        payload = convert_to_payload(df, birth_date=None, gestation_period=222)
    assert payload["birth_date"] == str(pd.Timestamp.today().date())
    assert payload["gestation_period"] == 222

def test_convert_to_payload_valueerrors():
    df = make_valid_df()
    # 1. DataFrame does not have exactly 192 rows
    with pytest.raises(ValueError, match="DataFrame must have exactly 192 rows"):
        convert_to_payload(df.iloc[:100])

    # 2. DataFrame does not have DatetimeIndex or 'datetime' column
    # Remove index and 'datetime' column
    df_no_datetime = df.reset_index(drop=True)
    with pytest.raises(ValueError, match="DataFrame must have a DatetimeIndex or a 'datetime' column"):
        convert_to_payload(df_no_datetime)

    # 3. DataFrame index is not monotonic increasing
    df_bad = make_valid_df()
    df_bad.index = df_bad.index[::-1]
    with pytest.raises(ValueError, match="DataFrame index must be monotonic increasing."):
        convert_to_payload(df_bad)

def test_generate_mock_signalbase_data():
    # Test default frequency ('S')
    df = generate_mock_signalbase_data(duration=1, freq='S')
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 3600  # 1 hour * 60 min * 60 sec
    assert set(['datetime', 'HR', 'RESP', 'SpO2', 'ID']).issubset(df.columns)
    # Check end time
    expected_end = pd.Timestamp('2000-01-01') + pd.Timedelta(seconds=3599)
    assert df['datetime'].iloc[-1] == expected_end

    # Test 2.5s frequency ('2s500ms')
    df_2 = generate_mock_signalbase_data(duration=1, freq='2s500ms')
    assert len(df_2) == 1440  # 1 hour / 2.5s = 1440 samples
    expected_end_2 = pd.Timestamp('2000-01-01') + pd.Timedelta(seconds=3597.5)
    assert df_2['datetime'].iloc[-1] == expected_end_2

    # Test ValueError for invalid frequency
    with pytest.raises(ValueError, match="freq must be 'S' or '2s500ms'"):
        generate_mock_signalbase_data(duration=1, freq='badfreq')
