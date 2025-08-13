# Sleep Well Baby: sleep stage prediction

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fgithub.com%2FUMCU-Digital-Health%2FSleepWellBaby%2Fblob%2Fmain%2Fpyproject.toml)
[![Unit test](https://github.com/UMCU-Digital-Health/SleepWellBaby/actions/workflows/unit_test.yml/badge.svg)](https://github.com/UMCU-Digital-Health/SleepWellBaby/actions/workflows/unit_test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<img src="https://cdn.worldvectorlogo.com/logos/umc-utrecht-1.svg" alt="UMCU Logo" width="200"/>

Author: Richard Bartels
Email: r.t.bartels-6@umcutrecht.nl

## Introduction
This repository contains code to run the sleep-well baby model that can classify sleep stages in 
preterm infants based on vital signs. It only contains code for model inference, not for training.

**Important**: *this software is for research use only and not intended for clinical or diagnostic purposes. Use at your own risk.*

## Getting started



### Installation

> **⚠️ Warning:**  
> This software only runs on `Python 3.8` because the model file was produced using that version.

The easiest way to install the `sleepwellbaby` package is to 
to use the package manager [uv](https://docs.astral.sh/uv/), a modern Python package manager that simplifies dependency management and ensures reproducibility:

```bash
uv sync --frozen
```

### Starterkit
An example of how to run this code can be found in [notebooks/example.ipynb](notebooks/example.ipynb)

## Documentation
Dataset and model information can be found in the [dataset card](docs/dataset_card.md) and [model card](docs/model_card.md), respectively.

## Citation instructions
Reference should be made to the sleep-well baby paper when using this software.


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
