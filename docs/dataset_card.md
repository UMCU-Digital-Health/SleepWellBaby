## Dataset Description

- **Paper:** Sentner et al., The Sleep Well Baby project: an automated real-time sleep–
wake state prediction algorithm in preterm infants. SLEEP, 2022, https://doi.org/10.1093/sleep/zsac143
- **Point of Contact:** [Richard Bartels](r.t.bartels-6@umcutrecht.nl)

Based on the dataset card template from huggingface, which can be found [here](https://github.com/huggingface/datasets/blob/main/templates/README_guide.md#table-of-contents).

### Dataset Summary
The dataset contains behavarious sleep-wake state classifications according to the [BeSSPI scheme](https://doi.org/10.1016/j.sleep.2022.01.020) together with vital parameter data for 46 preterm infants in the age range $[28, 34)$ postmenstrual weeks.


### Supported Tasks and Leaderboards
- `Classification`: The dataset can be used to train a model for classifying sleep states of preterm infants at the neonatal intensive care unit. Success on this task is typically measured by achieving a high (macro-averaged) AUC score. The performance of the best model is currently around $0.7$.


### Languages

The dataset is in English.

## Dataset Structure

### Data Instances

The input data 

Provide an JSON-formatted example and brief description of a typical instance in the dataset. If available, provide a link to further examples.

#### Sleep stage annotations
This dataset contains sleep stage annotations recorded in an Excel file using a long format. Each row represents a time point during the observation period. The columns include:
- Time: Minutes elapsed since the start of the observations.
- Sleep state: The observed sleep stage, which can be one of the following categories:
  - AS: Active Sleep
  - IS: Indeterminate Sleep
  - QS: Quiet Sleep
  - W: Wake
- Observed behaviour: baby behaviour used for classification
- Comments: optional field with potential disturbances such as sounds, interventions etc.
- Confidence score: -1, 0 or 1 to indicate confidence in the observation.

Additionally, each file contains  patient characteristics
- NICU ward
- Bed location
- Type of crib
- respiratory support
- Postmenstrual age
- Gender

#### Vital parameter data
Vital parameter data was extracted using *BedBase* and exported using *SignalBase* (University Medical Center Utrecht). The data came in `.tsv` format and was structured in long format with a timestamp and a parameter value. A separate file was extracted for each vital parameter, including heart rate, pulse rate, respiratory rate, oxygen saturation, arterial blood pressure (mean, diastolic and systolic), perfusion index.  The data frequency is $0.4$ or $1$ Hz depending on the BedBase version.

#### Input data for inference

Input data for inference is structured as follows:

```json
{
  "observation_date": null,
  "birth_date": "@today",
  "gestation_period": 210,
  "param_HR": {
    "ref2h_mean": 100.0,
    "ref2h_std": 10.0,
    "ref24h_mean": 100.0,
    "ref24h_std": 10.0,
    "values": [88.0, 108.0, 92.0, 91.0, 89.0, 76.0, 101.0, 107.0, 98.0, 101.0, 110.0, 121.0, 89.0, 82.0, 105.0, 102.0, 94.0, 96.0, 110.0, 112.0, 98.0, 100.0, 95.0, 86.0, 88.0, 94.0, 99.0, 99.0, 120.0, 101.0, 104.0, 89.0, 86.0, 96.0, 105.0, 116.0, 114.0, 93.0, 91.0, 98.0, 96.0, 110.0, 95.0, 89.0, 103.0, 88.0, 91.0, 99.0, 94.0, 84.0, 102.0, 108.0, 108.0, 106.0, 103.0, 98.0, 109.0, 104.0, 94.0, 91.0, 106.0, 94.0, 119.0, 106.0, 102.0, 91.0, 91.0, 100.0, 85.0, 103.0, 93.0, 94.0, 106.0, 114.0, 97.0, 98.0, 95.0, 102.0, 99.0, 97.0, 100.0, 95.0, 99.0, 96.0, 106.0, 102.0, 85.0, 109.0, 84.0, 93.0, 119.0, 113.0, 112.0, 98.0, 89.0, 100.0, 94.0, 112.0, 93.0, 86.0, 105.0, 83.0, 90.0, 109.0, 93.0, 95.0, 99.0, 95.0, 93.0, 108.0, 104.0, 103.0, 106.0, 101.0, 92.0, 120.0, 95.0, 107.0, 86.0, 111.0, 120.0, 95.0, 98.0, 79.0, 113.0, 102.0, 100.0, 90.0, 101.0, 101.0, 100.0, 108.0, 115.0, 88.0, 94.0, 91.0, 102.0, 93.0, 102.0, 95.0, 91.0, 99.0, 103.0, 95.0, 99.0, 96.0, 97.0, 99.0, 113.0, 102.0, 119.0, 95.0, 99.0, 110.0, 91.0, 95.0, 105.0, 85.0, 96.0, 107.0, 101.0, 103.0, 106.0, 101.0, 93.0, 123.0, 107.0, 100.0, 122.0, 106.0, 110.0, 109.0, 80.0, 88.0, 102.0, 101.0, 107.0, 88.0, 108.0, 94.0, 92.0, 105.0, 101.0, 99.0, 98.0, 102.0, 91.0, 118.0, 92.0, 117.0, 97.0, 91.0]
  },
  "param_RR": {
    "ref2h_mean": 90.0,
    "ref2h_std": 10.0,
    "ref24h_mean": 90.0,
    "ref24h_std": 10.0,
    "values": [106.0, 93.0, 88.0, 89.0, 106.0, 92.0, 99.0, 94.0, 99.0, 83.0, 115.0, 99.0, 93.0, 92.0, 104.0, 97.0, 117.0, 113.0, 87.0, 74.0, 103.0, 86.0, 92.0, 104.0, 97.0, 99.0, 100.0, 97.0, 91.0, 116.0, 98.0, 94.0, 113.0, 98.0, 113.0, 95.0, 117.0, 99.0, 93.0, 96.0, 87.0, 96.0, 101.0, 102.0, 126.0, 122.0, 96.0, 103.0, 91.0, 114.0, 93.0, 95.0, 95.0, 94.0, 104.0, 104.0, 95.0, 95.0, 100.0, 104.0, 100.0, 93.0, 97.0, 98.0, 93.0, 106.0, 103.0, 113.0, 113.0, 101.0, 92.0, 93.0, 100.0, 108.0, 110.0, 102.0, 89.0, 120.0, 102.0, 107.0, 99.0, 94.0, 107.0, 98.0, 100.0, 106.0, 116.0, 93.0, 115.0, 89.0, 123.0, 108.0, 109.0, 94.0, 103.0, 92.0, 95.0, 108.0, 85.0, 100.0, 89.0, 89.0, 85.0, 109.0, 95.0, 101.0, 99.0, 92.0, 102.0, 108.0, 102.0, 110.0, 101.0, 99.0, 124.0, 111.0, 95.0, 92.0, 120.0, 95.0, 105.0, 94.0, 105.0, 94.0, 94.0, 99.0, 101.0, 87.0, 94.0, 90.0, 96.0, 85.0, 85.0, 108.0, 102.0, 100.0, 104.0, 96.0, 111.0, 108.0, 89.0, 105.0, 91.0, 83.0, 95.0, 93.0, 121.0, 100.0, 103.0, 106.0, 96.0, 115.0, 97.0, 107.0, 88.0, 101.0, 102.0, 100.0, 95.0, 103.0, 95.0, 92.0, 102.0, 101.0, 101.0, 87.0, 119.0, 96.0, 107.0, 112.0, 102.0, 88.0, 116.0, 105.0, 121.0, 88.0, 107.0, 110.0, 105.0, 101.0, 115.0, 112.0, 99.0, 115.0, 92.0, 91.0, 82.0, 92.0, 98.0, 112.0, 98.0, 109.0]
  },
  "param_OS": {
    "ref2h_mean": 100.0,
    "ref2h_std": 10.0,
    "ref24h_mean": 100.0,
    "ref24h_std": 10.0,
    "values": [103.0, 108.0, 104.0, 101.0, 102.0, 104.0, 105.0, 95.0, 83.0, 90.0, 98.0, 83.0, 100.0, 84.0, 104.0, 95.0, 82.0, 105.0, 102.0, 95.0, 113.0, 91.0, 111.0, 94.0, 97.0, 99.0, 111.0, 96.0, 103.0, 104.0, 118.0, 121.0, 83.0, 94.0, 108.0, 99.0, 98.0, 101.0, 101.0, 78.0, 91.0, 107.0, 99.0, 94.0, 81.0, 104.0, 106.0, 103.0, 107.0, 86.0, 86.0, 101.0, 102.0, 101.0, 92.0, 103.0, 108.0, 96.0, 84.0, 116.0, 110.0, 94.0, 91.0, 89.0, 90.0, 100.0, 102.0, 89.0, 92.0, 96.0, 97.0, 95.0, 93.0, 84.0, 97.0, 92.0, 99.0, 81.0, 104.0, 112.0, 100.0, 104.0, 118.0, 94.0, 98.0, 109.0, 108.0, 107.0, 95.0, 81.0, 102.0, 92.0, 102.0, 96.0, 84.0, 89.0, 100.0, 97.0, 105.0, 97.0, 99.0, 101.0, 109.0, 78.0, 105.0, 95.0, 109.0, 86.0, 104.0, 97.0, 82.0, 83.0, 99.0, 105.0, 94.0, 97.0, 85.0, 91.0, 80.0, 78.0, 117.0, 94.0, 105.0, 93.0, 82.0, 103.0, 96.0, 101.0, 94.0, 87.0, 105.0, 109.0, 105.0, 119.0, 106.0, 116.0, 89.0, 110.0, 109.0, 89.0, 90.0, 103.0, 109.0, 94.0, 103.0, 94.0, 95.0, 114.0, 105.0, 103.0, 78.0, 107.0, 91.0, 103.0, 85.0, 92.0, 86.0, 93.0, 103.0, 100.0, 121.0, 109.0, 110.0, 87.0, 109.0, 101.0, 108.0, 119.0, 74.0, 112.0, 94.0, 105.0, 108.0, 104.0, 104.0, 92.0, 104.0, 88.0, 100.0, 71.0, 89.0, 98.0, 103.0, 115.0, 101.0, 95.0, 108.0, 103.0, 103.0, 96.0, 91.0, 111.0]
  }
}
```

### Data Fields

List and describe the fields present in the dataset. Mention their data type, and whether they are used as input or output in any of the tasks the dataset currently supports. If the data has span indices, describe their attributes, such as whether they are at the character level or word level, whether they are contiguous or not, etc. If the datasets contains example IDs, state whether they have an inherent meaning, such as a mapping to other datasets or pointing to relationships between data points.

- `example_field`: description of `example_field`

Note that the descriptions can be initialized with the **Show Markdown Data Fields** output of the [Datasets Tagging app](https://huggingface.co/spaces/huggingface/datasets-tagging), you will then only need to refine the generated descriptions.

### Data Splits
The dataset consists of training ($N = 37$) and a validation set ($N = 9$).

For model training a grouped nested cross-validation procedure was used, where grouping took place on patient id.

## Dataset Creation

### Curation Rationale

What need motivated the creation of this dataset? What are some of the reasons underlying the major choices involved in putting it together?

### Source Data

This section describes the source data (e.g. news text and headlines, social media posts, translated sentences,...)

#### Initial Data Collection and Normalization

Describe the data collection process. Describe any criteria for data selection or filtering. List any key words or search terms used. If possible, include runtime information for the collection process.

If data was collected from other pre-existing datasets, link to source here and to their [Hugging Face version](https://huggingface.co/datasets/dataset_name).

If the data was modified or normalized after being collected (e.g. if the data is word-tokenized), describe the process and the tools used.

#### Who are the source language producers?

State whether the data was produced by humans or machine generated. Describe the people or systems who originally created the data.

If available, include self-reported demographic or identity information for the source data creators, but avoid inferring this information. Instead state that this information is unknown. See [Larson 2017](https://www.aclweb.org/anthology/W17-1601.pdf) for using identity categories as a variables, particularly gender.

Describe the conditions under which the data was created (for example, if the producers were crowdworkers, state what platform was used, or if the data was found, what website the data was found on). If compensation was provided, include that information here.

Describe other people represented or mentioned in the data. Where possible, link to references for the information.

### Annotations

For details regarding the annotation process of sleep states see:

```
@article{DEGROOT2022167,
title = {Creating an optimal observational sleep stage classification system for very and extremely preterm infants},
journal = {Sleep Medicine},
volume = {90},
pages = {167-175},
year = {2022},
issn = {1389-9457},
doi = {https://doi.org/10.1016/j.sleep.2022.01.020},
url = {https://www.sciencedirect.com/science/article/pii/S1389945722000272},
author = {E.R. {de Groot} and A. Bik and C. Sam and X. Wang and R.A. Shellhaas and T. Austin and M.L. Tataranno and M.J.N.L. Benders and A. {van den Hoogen} and J. Dudink},
keywords = {Preterm infants, Sleep-wake stages, Behavioral observation, Neonatal intensive care},
}
```

#### Annotation process
Sleep stages were annotated via the current golden standard, observational sleep stage classification. Sleep stages of subjects were typically recorded over one to three hours periods in which a sleep stage was annotated every minute based on the past minute of observations. This observational classification can be performed either directly or through video recordings.

The typical interrater agreement between two human annotators is $\kappa = 0.8$.

#### Who are the annotators?

Sleep stages were annotated by humans trained in the BeSSPI protocol.

Typical annotators are research interns or PhD students. For new researchers an interrater agreement was determined (Cohen's $\kappa$).

### Personal and Sensitive Information
This data contains personal information from the electronic-health record, including patient characteristics such as birth date, gestational age, gender, birth weight, delivery method, plurality and APGAR scores. In addition, it contains vital parameter data from the bedside monitor. Researchers only have access to pseudonomyzed data, where all subjects received a pseudo ID.

## Considerations for Using the Data

### Social Impact of Dataset
This dataset can help by providing more insight into the sleep-wake pattern of preterm infants. Moreover, it can support in the development of a automated sleep-wake classifiers that could potentially enable the use of sleep as a vital sign.

### Discussion of Biases

Sleep observations with a confidence score of $-1$ were excluded for model development.

The patient population consists only of patients from NICU of the Wilhelmina's Children Hospital (WKZ). Since this is a single (academic) hospital in the Netherlands, this patient population will not be representative of all hospitals. In addition, practices in this particular NICU that can affect sleep-wake cycles might be different at other hospitals. Finally, all data was collected during the daytime and results derived from it could be less accurate during nighttime.

### Other Known Limitations

-

## Additional Information

### Dataset Curators

This dataset was collected by the team of Jeroen Dudink.

### Licensing Information

This dataset is not meant to be shared and has no license.

### Citation Information

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

### Contributions

Thanks to [@richardbartels](https://github.com/richardbartels) for adding this dataset.