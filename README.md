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

## TODO:
* add model card
* add dataset card
* add example for signalbase and generic
* add license
* fix test environment on github "ValueError: node array from the pickle has an incompatible dtype:" from unpickling
