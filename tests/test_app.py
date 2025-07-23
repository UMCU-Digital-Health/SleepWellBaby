import pytest

import json
from sleepwellbaby.dashboard.app import app
from sleepwellbaby.data import get_example_payload


def test_predict_endpoint():
    client = app.test_client()

    # Test using example payload
   
    payload = get_example_payload()
    payload["observation_date"] = payload['birth_date']  # Ensure observation_date is a valid string

    response = client.post("/predict", data=json.dumps(payload), content_type="application/json")
    assert response.status_code == 200  # Ensure endpoint returns HTTP 200 OK
    data = response.get_json()
    assert(isinstance(data, dict))
    assert data["prediction"] in ['AS', 'QS', 'W', 'ineligible']
    assert "api_version" in data

    # Test invalid method
    response = client.get("/predict")
    assert response.status_code == 405
    data = response.get_json()
    assert "message" in data
    assert "valid_methods" in data
    assert "requested_method" in data

