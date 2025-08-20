from typing import Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
import sklearn


def get_shap_values(
    model: sklearn.calibration.CalibratedClassifierCV,
    X: Union[pd.DataFrame, np.ndarray]
) -> np.ndarray:
    """
    Compute averaged SHAP values for a CalibratedClassifierCV model.

    This function calculates SHAP values for each calibrated classifier in the
    provided CalibratedClassifierCV model and averages them across all folds.
    Supports both binary and multiclass classification models.

    Parameters
    ----------
    model : sklearn.calibration.CalibratedClassifierCV
        A fitted CalibratedClassifierCV model from scikit-learn.
    X : np.ndarray or pd.DataFrame
        Feature matrix of shape (n_samples, n_features) for which to compute SHAP values.

    Returns
    -------
    averaged_shap_values : np.ndarray
        Averaged SHAP values. For binary classification, shape is (n_samples, n_features).
        For multiclass classification, shape is (n_classes, n_samples, n_features).

    Raises
    ------
    NotImplementedError
        If the provided model is not an instance of CalibratedClassifierCV.

    References
    ----------
    - https://github.com/slundberg/shap/issues/899 on how to deal with calibrated classifiers
    """
    if isinstance(model, sklearn.calibration.CalibratedClassifierCV):
        pass
    else:
        raise NotImplementedError("Only sklearn.calibration.CalibratedClassifierCV models are supported.")

    shap_values_list = []

    # Get shap values per calibrated classifier
    for calibrated_classifier in model.calibrated_classifiers_:
        explainer = shap.TreeExplainer(calibrated_classifier.base_estimator)

        # In older versions of shap, for multiclass models the below returns list of:
        # (# samples x # features) with the length of the list being n_classes
        shap_values = explainer.shap_values(X)
        shap_values_list.append(shap_values)
    if isinstance(shap_values_list[0], list):
        # multiclass models

        # zip to get list of classes instead of list of folds
        # Go from shape [a,b,c,d] to [b,a,c,d]
        shap_values_list = list(zip(*shap_values_list))
        averaged_shap_values = [None] * len(shap_values_list)

        # Sum of folds / calibrated classifiers
        for idx, i in enumerate(shap_values_list):
            averaged_shap_values[idx] = np.array(i).sum(axis=0) / len(i)
    else:
        # For binary models
        averaged_shap_values = np.array(shap_values_list).sum(axis=0) / len(shap_values_list)

    return averaged_shap_values

def dot_plot(shap_values, X, class_names):
    def dot_plot(
        shap_values: list,
        X,
        class_names: list[str]
    ) -> list:
        """
        Generates dot summary plots for SHAP values for each class and returns the matplotlib figures.

        Parameters
        ----------
        shap_values : list
            A list of SHAP values arrays, one for each class.
        X : array-like
            The feature matrix used for SHAP summary plots.
        class_names : list of str
            List of class names corresponding to each set of SHAP values.

        Returns
        -------
        figs : list of matplotlib.figure.Figure
            List of matplotlib figure objects containing the dot summary plots for each class.
        """
    figs = []
    for i in range(len(class_names)):
        f, ax = plt.subplots()

        shap.summary_plot(
            shap_values=shap_values[i],
            features=X,
            plot_type='dot',
            class_names=class_names[i],
            max_display=10,
            show=False,
            color=None,
            color_bar=True,
        )
        ax.set_title({"AS": "Active sleep", "QS": "Quiet sleep", "W": "Wake"}[class_names[i]])
        ax.tick_params(axis='x', labelsize=8)
        ax.tick_params(axis='y', labelsize=6)
        ax.xaxis.label.set_size(8)
        f.tight_layout()
        plt.close(f)
        figs.append(f)
    return figs
