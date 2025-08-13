
import numpy as np
from sklearn.base import BaseEstimator

from sleepwellbaby.data import get_example_payload
from sleepwellbaby.model import (
    get_prediction,
    load_model,
    process_prediction,
    return_y_pred,
)


def test_load_model_returns_expected_types():
    model, model_support = load_model()
    assert isinstance(model, BaseEstimator)
    assert isinstance(model_support, dict)

def test_return_y_pred():
    probas = np.array([[0.2, 0.3, 0.4], [0.2, 0.4, 0.3], [0.4, 0.3, 0.2]])
    classes = ["AS", "QS", "W"]

    # Without W_threshold
    preds = return_y_pred(probas, classes)
    assert preds[0] == "W"
    assert preds[1] == "QS"
    assert preds[2] == "AS"

    # With W_threshold
    preds = return_y_pred(probas,
                          classes,
                          wake_label="W",
                          wake_thresh=0.25)
    assert preds[0] == "W"
    assert preds[1] == "W"
    assert preds[2] == "AS"

    # invalid wake_label
    try:
        return_y_pred(np.array([0.1, 0.1, 0.8]), classes, wake_label="INVALID", wake_thresh=0.5)
    except Exception as e:
        assert "wake_label is expected to be in classes" in str(e)

    # Inclomplete argument (only label or threshold provided)
    probas = np.array([[0.1, 0.7, 0.2]])

    # Only W label provided
    try:
        return_y_pred(probas, classes, wake_label="W")
    except Exception as e:
        assert "wake_label and wake_thresh should be provided in conjunction" in str(e)

    # Only W threshold provided
    try:
        return_y_pred(probas, classes, wake_thresh=0.3)
    except Exception as e:
        assert "wake_label and wake_thresh should be provided in conjunction" in str(e)

def test_process_prediction():
    probas = np.array([[0.1, 0.7, 0.2]])
    classes = ["AS", "QS", "W"]
    pred_label, proba_dict = process_prediction(probas, classes)
    assert pred_label == "QS"
    assert isinstance(proba_dict, dict)
    assert set(proba_dict.keys()) == set(classes)

def test_get_prediction():
    example_payload = get_example_payload()
    model, model_support_dict = load_model()
    pred, proba_dict = get_prediction(example_payload, model, model_support_dict)
    assert isinstance(pred, str)
    assert isinstance(proba_dict, dict)
    assert np.isclose(sum(proba_dict.values()), 1.0)
    assert set(proba_dict.keys()) == set(model.classes_)
    example_payload_prediction = np.array(list(proba_dict.values()), dtype='float64')
    example_payload_expectation = np.array([0.5615941683425135,
                                            0.20849384661464576,
                                            0.22991198504284074,])
    assert np.isclose(example_payload_expectation, example_payload_prediction).all()
