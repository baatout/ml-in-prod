import logging
import dill
import pandas as pd
from flask import Flask, request
from werkzeug.exceptions import BadRequest

application = Flask(__name__)

logger = logging.getLogger(__name__)
logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S")


def build_model(model_path):
    with open(model_path, "rb") as f:
        mdl = dill.load(f)
    return mdl


def launch_model(mdl, request):
    try:
        features_as_dict = request.get_json()
        features_as_df = pd.io.json.json_normalize(features_as_dict)

        logger.info("Predicting {}".format(features_as_df))
        binary_predictions = mdl.predict(features_as_df)

        detected_zones = str(binary_predictions[0]) + '\n'
        logger.info("Predicted {}".format(detected_zones))
    except Exception as e:
        logger.exception("Error in pipeline")
        raise BadRequest(description=getattr(e, 'message', repr(e)))

    return detected_zones


@application.route("/predict", methods=["POST"])
def handle_predict_request():
    global model
    return launch_model(model, request)


if __name__ == "__main__":
    try:
        model = build_model("pipeline.pk")
        application.run()
    except KeyboardInterrupt:
        logger.exception("Shutting down")
    except Exception:
        logger.exception("Error in initialization chain")
