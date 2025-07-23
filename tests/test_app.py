import pytest

import json
from sleepwellbaby.dashboard.app import app
from sleepwellbaby.data import get_example_payload


def test_predict_endpoint_returns_ineligible(monkeypatch):

    # Patch process to return None (ineligible)
    def fake_process(data):
        return "ineligible", {"AS": -1, "QS": -1, "W": -1}
    import sleepwellbaby.model
    monkeypatch.setattr(sleepwellbaby.model, "get_prediction", fake_process)

    client = app.test_client()
    payload = {
        # Minimal valid payload structure, adjust keys as needed
        "other_arg": "2023-01-01",
        "pr": {"some_key": 1}
    }
    # payload = get_example_payload()

    response = client.post("/predict", data=json.dumps(payload), content_type="application/json")
    assert response.status_code == 200  # Ensure endpoint returns HTTP 200 OK
    data = response.get_json()
    assert(isinstance(data, dict))
    assert data["prediction"] == 'ineligible'
    assert data["AS"] == -1
    assert data["QS"] == -1
    assert data["W"] == -1
    assert "api_version" in data

def test_predict_endpoint_returns_prediction(monkeypatch):

    # Patch process to return a prediction and probabilities
    def fake_process(data):
        return "AS", {"AS": 0.7, "QS": 0.2, "W": 0.1}
    monkeypatch.setattr("sleepwellbaby.model.get_prediction", fake_process)

    client = app.test_client()
    payload = {
        # Minimal valid payload structure, adjust keys as needed
        "other_arg": "2023-01-01",
        "pr": {"some_key": 1}
    }
    response = client.post("/predict", data=json.dumps(payload), content_type="application/json")
    assert response.status_code == 200
    data = response.get_json()
    assert data["prediction"] == "AS"
    assert data["AS"] == 0.7
    assert data["QS"] == 0.2
    assert data["W"] == 0.1
    assert "api_version" in data

def test_predict_endpoint_invalid_method():

    client = app.test_client()
    response = client.get("/predict")
    assert response.status_code == 405
    data = response.get_json()
    assert "message" in data
    assert "valid_methods" in data
    assert "requested_method" in data