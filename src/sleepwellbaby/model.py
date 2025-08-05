from typing import Any, Dict, List, Tuple

import joblib
import numpy as np
from sklearn.base import BaseEstimator

from sleepwellbaby.eligibility import check_eligibility
from sleepwellbaby.preprocess import pipeline

from . import package_root


def load_model() -> Tuple[BaseEstimator, Dict[str, Any]]:
    """Load model files."""

    with open(package_root / "output" / "models" / "classifier.bz2", mode="rb") as f:
        model: BaseEstimator = joblib.load(f)
    with open(
        package_root / "output" / "models" / "trained_support_obj.pkl", mode="rb"
    ) as f:
        model_support_dict: Dict[str, Any] = joblib.load(f)
    return model, model_support_dict


def process_prediction(
    pred_proba: np.ndarray, classes: List[str]
) -> Tuple[str, Dict[str, float]]:
    """
    Process predicted probabilities.

    Parameters
    ----------
    pred_proba : np.ndarray
        Predicted probabilities per class, shape (1, n_classes).
    classes : list of str
        Class labels.

    Returns
    -------
    tuple
        prediction : str
            Predicted class label (readable).
        proba_dict : dict of str to float
            Dictionary mapping readable class labels to their probabilities.
    """
    pred = return_y_pred(pred_proba, classes)

    pred_label = pred[0]
    proba_dict = {k: v for k, v in zip(classes, pred_proba[0])}

    return pred_label, proba_dict


def return_y_pred(
    probas: np.ndarray, classes: List[str], wake_label: str = None, wake_thresh: float = None
) -> List[str]:
    """
    Return predictions.

    If provided, predict `wake_label` based on threshold,
    and remaining labels based on highest probability.

    Parameters
    ----------
    probas : np.ndarray
        Probabilities per class, shape (n_samples, n_classes).
    classes : list of str
        Names of classes.
    wake_label : str, optional
        Class that corresponds to Wake. Defaults to None.
    wake_thresh : float, optional
        Threshold to predict `wake_label`. Defaults to None.

    Returns
    -------
    list of str
        Predicted classes.
    """
    if (wake_label is None and wake_thresh is not None) or (
        wake_label is not None and wake_thresh is None
    ):
        raise Exception("wake_label and wake_thresh should be provided in conjunction")
    if wake_label:
        if wake_label not in classes:
            raise Exception("wake_label is expected to be in classes")
        W_mask = np.array([i == wake_label for i in classes])
        # Calculate what would be the prediction when disregarding wake_label
        y_pred = [classes[i] for i in probas[:, ~W_mask].argmax(axis=1)]
        # Predict Wake wherever probability exceeds threshold
        y_pred = np.where(probas.T[W_mask][0] > wake_thresh, wake_label, y_pred)
    else:
        y_pred = [classes[i] for i in probas.argmax(axis=1)]
    return y_pred


def get_prediction(payload, model=None, model_support_dict=None):
    if (model is None) | (model_support_dict is None):
        model, model_support_dict = load_model()

    eligible = check_eligibility(payload)

    if eligible:
        df = pipeline(payload, model_support_dict)
        pred_proba = model.predict_proba(df)
        pred, proba_dict = process_prediction(pred_proba, model.classes_)
    else:
        pred = "ineligible"
        proba_dict = {"AS": -1, "QS": -1, "W": -1}
    return pred, proba_dict
