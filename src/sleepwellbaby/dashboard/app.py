import datetime
import json

# import flask_monitoringdashboard as dashboard
from flask import Flask, request
from flask_restx import Api, Resource
from flask_restx.fields import Nested
from jsonschema import FormatChecker
from werkzeug.exceptions import MethodNotAllowed

from sleepwellbaby import version
from sleepwellbaby.dashboard.data_structures import (
    args_pred_other,
    args_pred_pr,
    response_pred,
)
from sleepwellbaby.model import get_prediction, load_model

model, model_support_dict = load_model()


app = Flask(__name__)

# Allow dates not to strictly adhere to ISO8601
# https://github.com/noirbizarre/flask-restplus/issues/603#issuecomment-472367498
format_checker = FormatChecker()


# fmt: on
@format_checker.checks("date", ValueError)  # noqa: E302
def lenient_date_check(value):
    """Check if input value is valid date"""
    datetime.datetime.strptime(value, "%Y-%m-%d")
    return True


api = Api(
    app,
    version=version,
    title="SWB API",
    description="API to request SleepWellBaby predictions",
    # https://github.com/python-restx/flask-restx/issues/344
    format_checker=format_checker,
)

# Predict endpoint
models_in_pred_pr = {
    k: api.model(f"payload_predict_{k}", v) for k, v in args_pred_pr.items()
}
args_pred = {
    **args_pred_other,
    **{k: Nested(v, required=True) for k, v in models_in_pred_pr.items()},
}
model_in_pred = api.model("payload_predict", args_pred)
model_out_pred = api.model("response_predict", response_pred)


@api.route(
    "/predict",
    doc={
        "description": "Will return a prediction from "
        "the SleepWellBaby algorithm if baby is eligible"
    },
)
class DoPrediction(Resource):
    @api.expect(model_in_pred, validate=True)
    @api.marshal_with(model_out_pred, description="Data received successfully")
    @api.doc(responses={400: "Input data not as expected"})
    def post(self):
        """Request a prediction for query data"""
        data = request.get_json()
        prediction, pred_proba = get_prediction(data, model, model_support_dict)
        result = {
            "prediction": prediction,
            "AS": pred_proba["AS"],
            "QS": pred_proba["QS"],
            "W": pred_proba["W"],
        }

        return result, 200


@app.after_request
def inject_api_version(response):
    """Ensure api_version is appended to HTTP codes 400 and 500 of API endpoints"""
    api_endpoints = [i for i in api.endpoints if i != "specs"]
    api_urls = [
        rule.rule for rule in app.url_map.iter_rules() if rule.endpoint in api_endpoints
    ]
    if request.path in api_urls:
        data = response.get_json()
        if "api_version" not in data:
            data["api_version"] = version
            response.set_data(json.dumps(data))
    return response


@api.errorhandler(MethodNotAllowed)
def method_not_allowed(error):
    """Improve informativeness of MethodNotAllowed message response"""
    return {
        "message": error.description,
        "valid_methods": error.valid_methods,
        "requested_method": request.method,
    }, 405


if __name__ == "__main__":
    app.run()
