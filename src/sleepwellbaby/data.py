import json
from datetime import date

import importlib_resources


def replace_today_placeholder(d: dict) -> dict:
    """Fill out current date placeholder in a dictionary.

    This function recursively searches through the input dictionary and replaces any value equal to
    '@today' with the current date in 'YYYY-MM-DD' format.

    Parameters
    ----------
    d : dict
        Input dictionary to process.

    Returns
    -------
    dict
        Dictionary with all '@today' values replaced by the current date.
    """
    for k, v in d.items():
        if isinstance(v, dict):
            d[k] = replace_today_placeholder(d[k])
        if v == "@today":
            d[k] = date.today().strftime(r"%Y-%m-%d")
    return d


# Note: there is no outlier detection on the values list
def get_example_payload():
    """
    Loads and returns the example payload from the 'example_payload.json' file located in the 'templates' directory of the 'sleepwellbaby' package.

    Returns:
      dict: The parsed JSON payload as a Python dictionary.

    Raises:
      FileNotFoundError: If the 'example_payload.json' file does not exist.
      json.JSONDecodeError: If the file contents are not valid JSON.
    """
    my_resources = importlib_resources.files("sleepwellbaby")
    data_bytes = my_resources.joinpath("templates", "example_payload.json").read_bytes()
    payload = json.loads(
        data_bytes.decode("utf-8"), object_hook=replace_today_placeholder
    )
    return payload
