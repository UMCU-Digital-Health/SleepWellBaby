import joblib
import numpy as np

from . import package_root


def load_model():
    """Loads model files

    Returns:
        tuple: processed files TODO: correct
    """

    with open(package_root / "output" / "models" / "trained_model.bz2", mode="rb") as f:
        model = joblib.load(f)

    return model

def process_prediction(pred_proba, classes):
    """Process predicted probabilities

    Args:
        pred_proba (array-like): predicted probabilities per class
        classes (list-like): class labels

    Returns:
        tuple: prediction, labeled probabilities
    """
    pred = return_y_pred(pred_proba, classes)
    readable_pred = {
        "AS": "active_sleep",
        "QS": "quiet_sleep",
        "W": "wake",
    }
    pred = readable_pred[pred[0]]
    # for i in readable_pred.values():
    #     logs.log_lists[i].append(pred == i)
    proba_dict = {readable_pred[k]: v for k, v in zip(classes, *pred_proba)}
    return pred, proba_dict

def return_y_pred(probas, classes, W_label=None, W_thresh=None):
    """Return predictions

    If provided, predict `W_label` based on threshold,
    and remaining labels based on highest probability

    Args:
        probas (array-like): probabilities per class
        classes (list of str): names of classes
        W_label (str): class that corresponds to Wake, defaults to None
        W_thresh (float): threshold to predict `W_label`, defaults to None

    Returns:
        list of str: predicted classes
    """
    if (W_label is None and W_thresh is not None) or (
        W_label is not None and W_thresh is None
    ):
        raise Exception("W_label and W_tresh should be provided in conjunction")
    if W_label:
        if W_label not in classes:
            raise Exception("W_label is expected to be in classes")
        W_mask = np.array([i == W_label for i in classes])
        # Calculate what would be the prediction when disregarding W_label
        y_pred = [classes[i] for i in probas[:, ~W_mask].argmax(axis=1)]
        # Predict Wake wherever probability exceeds threshold
        y_pred = np.where(probas.T[W_mask][0] > W_thresh, W_label, y_pred)
    else:
        y_pred = [classes[i] for i in probas.argmax(axis=1)]
    return y_pred