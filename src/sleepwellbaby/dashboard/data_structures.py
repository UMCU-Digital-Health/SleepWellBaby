from itertools import product

from flask_restx.fields import Date, Float, Integer, List, String

from sleepwellbaby import version
from sleepwellbaby.data import get_example_payload


def make_required_and_add_example(d, exmpl_data):
    """Makes flask_restx fields required, and adds examples from provided data

    Parameters
    ----------
        d (dict): dict of flask_restx.fields
        exmpl_data (dict): dict of examples, similarly keyed as `d`

    Returns
    -------
        dict: dict of flask_restx.fields, with added examples and required set to True
    """
    for k in d.keys():
        if isinstance(d[k], dict):
            d[k] = make_required_and_add_example(d[k], exmpl_data[k])
        else:
            d[k].required = True
            d[k].example = exmpl_data[k]
    return d


possible_pred_values = ["active_sleep", "quiet_sleep", "wake", "ineligible"]

coverage_req = {"description": "Should be based on max 50% missing values"}

v_values = {"cls_or_instance": Float(min=-1), "min_items": 192, "max_items": 192}

args_vitals = {
    k: {
        **{
            "_".join(i): Float(**coverage_req)
            for i in product(["ref2h", "ref24h"], ["mean", "std"])
        },
        "values": List(**v_values),
    }
    for k in ["param_HR", "param_RR", "param_OS"]
}

example_payload = get_example_payload()
args_vitals = make_required_and_add_example(args_vitals, example_payload)
args_patient_characteristics = {
    "birth_date": Date(),
    "gestation_period": Integer(),
    "observation_date": Date(nullable=True),
}
args_patient_characteristics = make_required_and_add_example(args_patient_characteristics, example_payload)

response_pred = {
    "prediction": String(enum=possible_pred_values),
    "AS": Float(min=-1, max=1),
    "QS": Float(min=-1, max=1),
    "W": Float(min=-1, max=1),
    "api_version": String(default=version),
}
