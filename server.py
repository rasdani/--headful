### This webserver will receive the coordinates from the vimium fork and save them in a json file
import json
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import time
import logging


def run_server():
    app = Flask(__name__)
    # app.logger.setLevel(logging.ERROR)
    CORS(app)  # This will enable CORS for all routes

    @app.route("/bboxes", methods=["POST"])
    # @cross_origin()
    def handle_bbox():
        data = request.get_json()
        # print("Coordinates received successfully ", time.time())
        ret = jsonify({"message": "Received data successfully"})
        # print(data)
        with open("coordinates.json", "w") as f:
            json.dump(data, f)
        return ret, 200

    @app.route("/hintString", methods=["POST"])
    # @cross_origin()
    def handle_hint_string():
        data = request.get_json()
        print(data)
        hint_code = data.get('hintString')
        print("Received hint code: ", hint_code)
        return jsonify({"message": "Received hint code successfully"}), 200

    app.run(port=5000)

if __name__ == "__main__":
    run_server()
