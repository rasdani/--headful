import pyaudio
import webrtcvad


def main():
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=160)
    vad = webrtcvad.Vad(1)  # Set aggressiveness mode, an integer between 0 and 3.

    print("Speak into the microphone...")

    while True:
        frames = stream.read(160, exception_on_overflow=False)
        is_speech = vad.is_speech(frames, sample_rate=16000)

        if is_speech:
            print("Detected speech")
        else:
            print("No speech detected")

    stream.stop_stream()
    stream.close()
    p.terminate()

if __name__ == "__main__":
    main()
