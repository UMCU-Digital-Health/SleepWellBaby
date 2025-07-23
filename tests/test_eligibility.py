import pytest
import numpy as np

from sleepwellbaby.eligibility import age_eligibility, data_eligibility


def test_data_eligibility_all_values_present():
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

def test_age_eligibility_within_range():

    # Observation date before birth date
    payload = {
        "birth_date": "2024-01-02",
        "gestation_period": 196  # 28 weeks
    }
    observation_date = "2024-01-01"
    with pytest.raises(ValueError, match="Observation date cannot be before birth date."):
        age_eligibility(payload, observation_date)
    
    # PMA exactly at lower bound (28), should be eligible
    payload = {
        "birth_date": "2024-01-01",
        "gestation_period": 196  # 28 weeks
    }
    observation_date = "2024-01-01"
    assert age_eligibility(payload, observation_date) is True

    # PMA below lower bound (27.9), should be ineligible
    payload = {
        "birth_date": "2024-01-01",
        "gestation_period": 195 
    }
    observation_date = "2024-01-01"
    assert age_eligibility(payload, observation_date) is False

    # PMA at upper bound (34), should be ineligible
    payload = {
        "birth_date": "2024-01-01",
        "gestation_period": 238  # 34 weeks
    }
    observation_date = "2024-01-01"
    assert age_eligibility(payload, observation_date) is False

    # PMA just below upper bound (34), should be eligible
    payload = {
        "birth_date": "2024-01-01",
        "gestation_period": 237  # 34 weeks
    }
    observation_date = "2024-01-01"
    assert age_eligibility(payload, observation_date) is True

    # PMA 33+6, with GA=33, should be eligible
    payload = {
        "birth_date": "2024-01-01",
        "gestation_period": 231 
    }
    observation_date = "2024-01-7"
    assert age_eligibility(payload, observation_date) is True

    # PMA 34, with GA=33, should be ineligible
    payload = {
        "birth_date": "2024-01-01",
        "gestation_period": 231 
    }
    observation_date = "2024-01-8"
    assert age_eligibility(payload, observation_date) is False
