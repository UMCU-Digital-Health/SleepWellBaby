import pytest
import json

import pandas as pd

from sleepwellbaby.data import get_example_payload


def test_get_example_payload_success(monkeypatch):
    # Mock importlib_resources.files().joinpath().read_bytes()
    class DummyPath:
        def read_bytes(self):
            # Minimal valid JSON for the payload
            return b'{"observation_date": "2025-05-08"}'
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
    assert payload['observation_date'] == None
    