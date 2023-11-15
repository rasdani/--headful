import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
from io import BytesIO
import base64
import os
import time


app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes


@app.route("/", methods=["POST"])
def handle_post():
    data = request.get_json()
    # Do something with the data here
    # print(data)
    print("Coordinates received successfully ", time.time())
    data_json = jsonify({"message": "Received data successfully"})
    with open("coordinates.json", "w") as f:
        json.dump(data, f)
    return data_json, 200

@app.route("/save_image", methods=["POST"])
def save_image():
    data = request.get_json()
    image_data = data['image'].split(',')[1]  # Remove the "data:image/png;base64," part
    image = Image.open(BytesIO(base64.b64decode(image_data)))
    if not os.path.exists('bbox-images'):
        os.makedirs('bbox-images')
    image.save(os.path.join('bbox-images', f'image_{data["index"]}.png'))
    return jsonify({"message": "Image saved successfully"}), 200


if __name__ == "__main__":
    app.run(port=5000)
