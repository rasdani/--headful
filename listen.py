import pyaudio
import wave
import webrtcvad
import openai
from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def main():
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=16000,
        input=True,
        frames_per_buffer=160,
    )
    vad = webrtcvad.Vad(3)  # Set aggressiveness mode, an integer between 0 and 3.

    print("Speak into the microphone...")

    recording = False
    frames = []  # List to hold audio frames
    silence_frames = 0  # Counter for silent frames
    # silence_threshold = 30  # Silence threshold in number of framesh
    silence_threshold = 90  # Silence threshold in number of framesh

    try:
        while True:
            buffer = stream.read(160, exception_on_overflow=False)
            is_speech = vad.is_speech(buffer, sample_rate=16000)
            is_speech = True

            if is_speech:
                if not recording:
                    print("Detected speech, start recording...")
                    recording = True
                    silence_frames = 0  # Reset silence frame counter

                frames.append(buffer)
            else:
                if recording:
                    silence_frames += 1

                    # If silence duration exceeds a threshold, stop recording
                    if (
                        silence_frames > silence_threshold
                    ):  # For example, stop recording after 1 second of silence
                        print("Speech ended, stop recording.")
                        recording = False
                        silence_frames = 0

                        # Save the recorded audio
                        filename = "recording.wav"
                        wf = wave.open(filename, "wb")
                        wf.setnchannels(1)
                        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
                        wf.setframerate(16000)
                        wf.writeframes(b"".join(frames))
                        wf.close()
                        audio_file = open(
                            "recording.wav", "rb"
                        )  # TODO: skip writing to disk
                        transcript = openai.Audio.transcribe("whisper-1", audio_file)
                        print(transcript)

                        # Reset the frames list for the next recording
                        frames = []
                    else:
                        # Optionally, keep recording silence for a smoother transition
                        frames.append(buffer)

    except KeyboardInterrupt:
        pass  # Exit on Ctrl+C

    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
        # audio_file= open("recording.wav", "rb")
        # transcript = openai.Audio.transcribe("whisper-1", audio_file)
        # print(transcript)


if __name__ == "__main__":
    main()
