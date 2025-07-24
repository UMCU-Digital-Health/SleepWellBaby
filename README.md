# SleepWellBaby

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Author: Richard Bartels
Email: r.t.bartels-6@umcutrecht.nl

## Installation

To install the sleepwellbaby package use:

```{bash}
uv sync
```

You can then activate the environment using

```{bash}
source .venv/bin/activate
```

This will also install the nbstripout package, which will strip out the output of notebooks when committing to git.
The nbstripout package should be installed automatically when running this cookiecutter template, to check if it is installed run:

```{bash}
nbstripout --status
```

If it is not installed, you can install it manually by running:

```{bash}
nbstripout --install
```

## Deploying to PositConnect

To deploy to PositConnect install rsconnect (`pip install rsconnect-python`) and run (in case of a dash app):
```{bash}
rsconnect deploy dash --server https://rsc.ds.umcutrecht.nl/ --api-key <(user specific key)> --entrypoint run.app:app .
```

## Documentation
Dataset and model information can be found in the [dataset card](docs/dataset_card.md) and [model card](docs/model_card.md), respectively.

e

## Citation instructions
Reference should be made to the sleep-well baby paper when using this software.

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

## TODO:
* add model card
* add dataset card
* add example for signalbase and generic
* add license
* fix test environment on github "ValueError: node array from the pickle has an incompatible dtype:" from unpickling
