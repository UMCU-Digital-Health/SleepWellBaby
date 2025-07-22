import pytest
import numpy as np

from sleepwellbaby.data import example_payload
from sleepwellbaby.model import load_model, process_prediction
from sleepwellbaby.preprocess import pipeline

def test_pipeline_prediction():
    model, model_support_dict = load_model()
    df = pipeline(example_payload, model_support_dict)
    pred_proba = model.predict_proba(df)
    pred, proba_dict = process_prediction(pred_proba, model.classes_)
    assert isinstance(pred, str)
    assert isinstance(proba_dict, dict)
    assert np.isclose(sum(proba_dict.values()), 1.0)
    assert set(proba_dict.keys()) == set(model.classes_)
    example_payload_prediction = np.array(list(proba_dict.values()), dtype='float64')
    example_payload_expectation = np.array([0.5615941683425135, 
                                            0.20849384661464576,
                                            0.22991198504284074,])
    assert np.isclose(example_payload_prediction, example_payload_expectation).all()