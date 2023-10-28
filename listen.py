import pyaudio
import wave
import numpy as np
import librosa
import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
# Configure audio recording parameters
chunk = 1024  # Record in chunks of 1024 samples
sample_format = pyaudio.paInt16  # 16 bits per sample
channels = 1
fs = 16000  # Record at 16000 samples per second
duration = 5
num_chunks = int(fs / chunk * duration)

p = pyaudio.PyAudio()

print('Recording...')

frames = []
stream = p.open(format=sample_format, channels=channels, rate=fs, frames_per_buffer=chunk, input=True)

# while True:
#     data = stream.read(chunk)
#     frames.append(data)
#     audio_data = np.frombuffer(data, dtype=np.int16)
#     non_silent_intervals = librosa.effects.split(y=audio_data, top_db=30)  # Adjust top_db as needed
#     if len(non_silent_intervals) == 0:
#         break

for _ in range(num_chunks):
    data = stream.read(chunk)
    frames.append(data)

print('Finished recording.')

# Stop and close the stream
stream.stop_stream()
stream.close()

# Terminate the PortAudio interface
p.terminate()

# Save the recorded data as a WAV file
filename = 'output.wav'
wf = wave.open(filename, 'wb')
wf.setnchannels(channels)
wf.setsampwidth(p.get_sample_size(sample_format))
wf.setframerate(fs)
wf.writeframes(b''.join(frames))
wf.close()

# Note: you need to be using OpenAI Python v0.27.0 for the code below to work
audio_file= open("output.wav", "rb")
transcript = openai.Audio.transcribe("whisper-1", audio_file)
print(transcript)