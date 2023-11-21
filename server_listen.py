import json
import threading
from flask import Flask, request, jsonify
from flask_cors import CORS
import pyaudio
import wave
import time

app = Flask(__name__)
CORS(app)  # Adjust CORS according to your needs

class RecordingThread(threading.Thread):
    def __init__(self, filename, max_duration):
        super().__init__()
        self.filename = filename
        self.max_duration = max_duration
        self.do_record = True

    def run(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=160)
        frames = []
        start_time = time.time()
        
        while self.do_record and (time.time() - start_time) < self.max_duration:
            frames.append(stream.read(160, exception_on_overflow=False))

        stream.stop_stream()
        stream.close()
        p.terminate()

        with wave.open(self.filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(16000)
            wf.writeframes(b''.join(frames))

recording_thread = None

@app.route("/bboxes", methods=["POST"])
def handle_bbox():
    global recording_thread
    data = request.get_json()
    print(data)
    with open("coordinates.json", "w") as f:
        json.dump(data, f)
    
    if recording_thread is None or not recording_thread.is_alive():
        recording_thread = RecordingThread('browser_talk.wav', 30)  # 60 seconds max duration
        recording_thread.start()

    return jsonify({"message": "Recording started"}), 200

@app.route("/hintString", methods=["POST"])
def handle_hint_string():
    global recording_thread
    data = request.get_json()
    hint_code = data.get('hintString')
    
    if recording_thread and recording_thread.is_alive():
        recording_thread.do_record = False
        recording_thread.join(5)  # 5 seconds timeout

    return jsonify({"message": "Received hint code successfully", "hintCode": hint_code}), 200

def test_recording(app):
    with app.test_client() as client:
        print("Simulating /bboxes POST request to start recording...")
        bbox_data = {"example": "data"}  # Replace with actual data you expect
        client.post("/bboxes", data=json.dumps(bbox_data), content_type='application/json')

        input("Recording... Press Enter to stop...")

        print("Simulating /hintString POST request to stop recording...")
        hint_string_data = {"hintString": "example"}  # Replace with actual data
        client.post("/hintString", data=json.dumps(hint_string_data), content_type='application/json')


if __name__ == "__main__":
    # app.run(port=5000, threaded=True)
    test_recording(app)
