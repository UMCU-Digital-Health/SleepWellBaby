
<!-- Adapted from hugging face template: https://github.com/huggingface/huggingface_hub/blob/main/src/huggingface_hub/templates/modelcard_template.md -->

# Model Card for SleepWellBaby

The model predicts the sleep stage of preterm infants based on vital signs collected by a bedside monitor

## Model Details

### Model Description

This model uses vital parameter data samppled at $0.4$ Hz from the preceding eight minutes to predict the sleep stage (`active sleep`, `quiet sleep` or `wake`). It can be used for continuous (every minute) monitoring of sleep stages.

- **Developed by:** Thom Sentner et al.
- **Model type:** Random Forest Classifier (multiclass)
- **License:** MIT

### Model Sources
- **Paper:** https://doi.org/10.1093/sleep/zsac143


## Uses
This software is *for research use only*

### Direct Use
The Sleep Well Baby algorithm is intended to monitor sleep as a vital sign. It was developed for preterm infants on the neonatal intensive care unit (NICU) with postmenstrual ages $[28, 34)$ weeks.

Foreseeable primary users of the model include healthcare workers (e.g. nurses and neonatologists) and sleep researchers.

### Out-of-Scope Use
The software is not suitable for use in clinical management.

## Bias, Risks, and Limitations
This model may reflect biases present in the training data, such as times at which sleep stages were observed and the circumstances under which sleep stages were observed (e.g. patient conditions, noise in the ward). Predictions should be interpreted with caution.


### Recommendations
Users should be made aware of the risks, biases and limitations of the model. In particular, 
* This model has not been cleared as a medical device and cannot be used safely for patient management. 
* The model was trained on an imperfect golden standard for sleep stages, namely human observations
* The model is not a perfect, neither in terms of discrimination or calibration

## How to Get Started with the Model
See [`notebooks/example.ipynb`](../notebooks/example.ipynb) for a complete example of how to use the model.

## Training Details

### Training Data

The model was trained to predict observed sleep stages (by human annotators) based on vital parameters from the bedside monitor. See [dataset card](dataset_card.md) for details.

### Training Procedure 

For model training a grouped nested cross-validation (`splits=4`) procedure was used, where grouping took place on patient level. Patients where oversampled in the inner loop to equalize the amount of training data per patient.


#### Training Hyperparameters
Random search was used to find the best hyperparameters (indicated in italics)
* `Class weight`: *balanced*
* `Number of estimators`: *250*
* `Max depth`: 2, 3, *5*, 20, 50
* `Min samples split`: 2%, 4.2%, 8.3%, 16.7%, *33.3%*
* `Min samples leaf`: 1, 0.4%, *3%*, 6%
* `Max features`: 5%, *10%*, 20%, 40%

## Evaluation

The model was evaluated on the training data using pooled results from the outer loop as well as on a separate validation dataset.

### Testing Data, Factors & Metrics

#### Testing Data
See [dataset card](dataset_card.md).

#### Metrics
- Balanced accuracy Wake
- Sensitivity Wake
- Specificity Wake
- F1 score (macroaveraged)
- F1 score Wake
- AUROC (macro-averaged)
- AUROC Active Sleep
- AUROC Quiet Sleep
- AUROC Wake
- Cohen’s kappa
- Cohen’s kappa Active Sleep
- Cohen’s kappa Quiet Sleep
- Cohen’s kappa Wake
- Brier Active Sleep
- Brier Quiet Sleep
- Brier Wake

### Results

The model achieved a macro-averaged AUROC of 0.76 (0.69-0.82) on the training data and 0.70 (0.61–0.78) on the validation data. Confidence intervals were determined using bootstrapping. 

Calibration of the model has Brier scores of the order $\sim 0.2$.


## Model Examination

Contributions to individual predictions were examined using Shapley values

## Environmental Impact
The model can be trained locally on CPUs. The environmental impact is low.

## Technical Specifications

### Model Architecture and Objective
The model is a multiclass classifier trained on tabular data using `imbalanced-learn` (based on `scikit-learn`).

### Compute Infrastructure
Trained on a local machine used for development by the AI for Health team at UMC Utrecht.

#### Hardware
The model can be trained on a standard laptop or desktop with sufficient RAM and CPU power. For larger datasets, a machine with more resources may be required.

#### Software
See [pyproject.toml](../pyproject.toml) files for the software dependencies required to run the model.

## Citation

```
@article{10.1093/sleep/zsac143,
    author = {Sentner, Thom and Wang, Xiaowan and de Groot, Eline R and van Schaijk, Lieke and Tataranno, Maria Luisa and Vijlbrief, Daniel C and Benders, Manon J N L and Bartels, Richard and Dudink, Jeroen},
    title = {The Sleep Well Baby project: an automated real-time sleep–wake state prediction algorithm in preterm infants},
    journal = {Sleep},
    volume = {45},
    number = {10},
    pages = {zsac143},
    year = {2022},
    month = {06},
    issn = {0161-8105},
    doi = {10.1093/sleep/zsac143},
    url = {https://doi.org/10.1093/sleep/zsac143},
    eprint = {https://academic.oup.com/sleep/article-pdf/45/10/zsac143/45986688/zsac143.pdf},
}
```

If the model artefact has a [DOI](https://www.doi.org/), please provide it here.

## Glossary

* **AS**: active sleep
* **IS**: intermediate sleep
* **QS**: quiet sleep
* **W**: wake

## Model Card Authors
* Richard Bartels

## Model Card Contact

* r.t.bartels-6@umcutrecht.nl
