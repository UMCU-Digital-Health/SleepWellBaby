
import pytest

import numpy as np
import pandas as pd

from sleepwellbaby.eligibility import age_eligibility, data_eligibility, reference_eligibility



def test_data_eligibility():
    # All values are positive, so eligibility should be True
    payload1 = {'param_X': {"values": np.ones(192)}}
    assert data_eligibility(payload1) is True

    # 50% missing
    payload2 = {'param_X': {"values": np.ravel(np.c_[[np.ones(96), np.ones(96)*-1]].T)}}  # 1 and -1 interchange
    assert data_eligibility(payload2) is True

    # >50% missing
    values = np.ravel(np.c_[[np.ones(96), np.ones(96)*-1]].T)
    values[0] = -1
    payload3 = {'param_X': {"values": values}}  # 1 and -1 interchange, 97x -1
    assert data_eligibility(payload3) is False

    # Oldes 35s missing
    payload4 = {'param_X': {"values": np.concatenate([np.ones(14)*-1, np.ones(178)])}}
    assert data_eligibility(payload4) is True

    # newest 35s missing, less than 50% completeness in 60s windows so False
    payload5 = {'param_X': {"values": np.concatenate([np.ones(178), np.ones(14)*-1])}}
    assert data_eligibility(payload5) is False

def test_age_eligibility():
    # Observation date before birth date
    payload = {
        "birth_date": "2024-01-02",
        "gestation_period": 196,  # 28 weeks
        "observation_date": "2024-01-01"
    }
    with pytest.raises(ValueError, match="Observation date cannot be before birth date."):
        age_eligibility(payload)

    # PMA exactly at lower bound (28), should be eligible
    payload = {
        "birth_date": "2024-01-01",
        "gestation_period": 196,  # 28 weeks
        "observation_date": "2024-01-01"
    }
    assert age_eligibility(payload) is True

    # PMA below lower bound (27.9), should be ineligible
    payload = {
        "birth_date": "2024-01-01",
        "gestation_period": 195,
        "observation_date": "2024-01-01"
    }
    assert age_eligibility(payload) is False

    # PMA at upper bound (34), should be ineligible
    payload = {
        "birth_date": "2024-01-01",
        "gestation_period": 238,  # 34 weeks
        "observation_date": "2024-01-01"
    }
    assert age_eligibility(payload) is False

    # PMA just below upper bound (34), should be eligible
    payload = {
        "birth_date": "2024-01-01",
        "gestation_period": 237,  # 34 weeks
        "observation_date": "2024-01-01"
    }
    assert age_eligibility(payload) is True

    # PMA 33+6, with GA=33, should be eligible
    payload = {
        "birth_date": "2024-01-01",
        "gestation_period": 231,
        "observation_date": "2024-01-07"
    }
    assert age_eligibility(payload) is True

    # PMA 34, with GA=33, should be ineligible
    payload = {
        "birth_date": "2024-01-01",
        "gestation_period": 231,
        "observation_date": "2024-01-08"
    }
    assert age_eligibility(payload) is False

    # observation date is none, set to today
    payload = {
        "birth_date": "2024-01-01",
        "gestation_period": 231,
        "observation_date": None
    }
    assert age_eligibility(payload) is False

    payload = {
        "birth_date": pd.Timestamp.today(),
        "gestation_period": 231,
        "observation_date": None
    }
    assert age_eligibility(payload) is True 


def test_reference_eligibility():

    # All reference values within valid ranges for param_HR (at boundaries)
    payload = {
        "param_HR": {
            "ref2h_mean": 100,
            "ref24h_mean": 220,
            "ref2h_std": 1,
            "ref24h_std": 25
        }
    }
    assert reference_eligibility(payload) is True

    # Mean below min for param_HR
    payload = {
        "param_HR": {
            "ref2h_mean": 99,  # min is 100
            "ref24h_mean": 110, # At max, should be
            "ref2h_std": 10,
            "ref24h_std": 15
        }
    }
    assert reference_eligibility(payload) is False

    # Mean above max for param_HR
    payload = {
        "param_HR": {
            "ref2h_mean": 110,  
            "ref24h_mean": 221, # max is 220
            "ref2h_std": 10,
            "ref24h_std": 15
        }
    }
    assert reference_eligibility(payload) is False

    # Std below min for param_HR
    payload = {
        "param_HR": {
            "ref2h_mean": 120,
            "ref24h_mean": 110,
            "ref2h_std": 0,  # min is 0, lower bound not included
            "ref24h_std": 15
        }
    }
    assert reference_eligibility(payload) is False

    # Std above max for param_HR
    payload = {
        "param_HR": {
            "ref2h_mean": 120,
            "ref24h_mean": 110,
            "ref2h_std": 10,
            "ref24h_std": 26  # max is 25
        }
    }
    assert reference_eligibility(payload) is False

    # All parameter eligible, and obsolete key (should be ignored)
    payload = {
        "param_HR": {
            "ref2h_mean": 120,
            "ref24h_mean": 110,
            "ref2h_std": 10,
            "ref24h_std": 15
        },
        "param_RR": {
            "ref2h_mean": 70,
            "ref24h_mean": 70,
            "ref2h_std": 10,
            "ref24h_std": 10, 
        },
        "param_OS": {
            "ref2h_mean": 95,
            "ref24h_mean": 97,
            "ref2h_std": 5,
            "ref24h_std": 7
        },
        "other_key": {
            "ref2h_mean": 0,
            "ref24h_mean": 0,
            "ref2h_std": 0,
            "ref24h_std": 0
        }
    }
    assert reference_eligibility(payload) is True

    # One parameter out of bounds
    payload["param_RR"]["ref2h_mean"] = 19  # min is 20
    assert reference_eligibility(payload) is False