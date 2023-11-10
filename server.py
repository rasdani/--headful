import json
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

@app.route('/', methods=['POST'])
def handle_post():
    data = request.get_json()
    # Do something with the data here
    print(data)
    data_json = jsonify({'message': 'Received data successfully'})
    with open('coordinates.json', 'w') as f:
        json.dump(data, f)
    return data_json, 200

if __name__ == '__main__':
    app.run(port=5000)