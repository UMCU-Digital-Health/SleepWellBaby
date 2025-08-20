import matplotlib.pyplot as plt
import numpy as np
import shap
import sklearn


def get_shap_values(model, X):
    if isinstance(model, sklearn.calibration.CalibratedClassifierCV):
        # https://github.com/slundberg/shap/issues/899
        shap_values_list = []
        for calibrated_classifier in model.calibrated_classifiers_:
            explainer = shap.TreeExplainer(calibrated_classifier.base_estimator)
            shap_values = explainer.shap_values(X)
            shap_values_list.append(shap_values)
        if isinstance(shap_values_list[0], list):
            # multiclass
            # zip to get list of classes instead of list of folds
            shap_values_list = list(zip(*shap_values_list))
            for idx, i in enumerate(shap_values_list):
                shap_values[idx] = np.array(i).sum(axis=0) / len(i)

    return shap_values

def dot_plot(shap_values, X, class_names):
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
        plt.title({"AS": "Active sleep", "QS": "Quiet sleep", "W": "Wake"}[class_names[i]])
        plt.xticks(fontsize=8)
        plt.yticks(fontsize=6)
        ax.xaxis.label.set_size(8)
        plt.tight_layout()
        figs.append(f)
        plt.close()
    return figs
