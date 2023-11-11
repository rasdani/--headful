import pyaudio
import wave
import webrtcvad
import openai
from dotenv import load_dotenv
import os
from playwright.sync_api import sync_playwright
import json

from drive_browser import WebDriver
from head import chat_completion_request, functions

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def visit_website(driver, url):
    driver.navigate_to(url)
    return "Success"


def execute_browser_action(driver, action):
    page = driver.page
    if action == "go_back":
        page.go_back()
    elif action == "go_forward":
        page.go_forward()
    elif action == "new_tab":
        page.context().new_page()
    else:
        return f"Unknown action: {action}"
    return "Success"


def execute_function_call(driver, function_call):
    if function_call["name"] == "visit_website":
        url = json.loads(function_call["arguments"])["url"]
        results = visit_website(driver, url)
    elif function_call["name"] == "execute_browser_action":
        action = json.loads(function_call["arguments"])["action"]
        results = execute_browser_action(driver, action)
    else:
        results = f"Error: function {function_call['name']} does not exist"
    return results


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

    recording = False
    frames = []  # List to hold audio frames
    silence_frames = 0  # Counter for silent frames
    # silence_threshold = 30  # Silence threshold in number of framesh
    silence_threshold = 90  # Silence threshold in number of framesh

    messages = []
    messages.append(
        {
            "role": "system",
            "content": "Navigate a web browser with the provided functions.",
        }
    )

    try:
        with sync_playwright() as playwright:
            driver = WebDriver(playwright)
            driver.start_browser(headless=False)
            print("Speak into the microphone...")
            while True:
                buffer = stream.read(160, exception_on_overflow=False)
                is_speech = vad.is_speech(buffer, sample_rate=16000)

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
                            # transcript = openai.Audio.transcribe("whisper-1", audio_file)
                            # user_input = transcript['text']
                            user_input = input("Enter your message: ")
                            print(f"{user_input=}")
                            frames = []
                            messages.append({"role": "user", "content": user_input})
                            print(f"{messages=}")
                            print(f"{functions=}")
                            chat_response = chat_completion_request(
                                messages=messages,
                                functions=functions,
                            )
                            print(f"{chat_response=}")
                            # assistant_message = chat_response.json()["choices"][0]["message"]
                            assistant_message = chat_response["choices"][0]["message"]
                            if "function_call" in assistant_message:
                                function_call = assistant_message["function_call"]
                                execute_function_call(
                                    driver, function_call
                                )  # Assuming this function is set up to handle the function call object
                            else:
                                messages.append(assistant_message)
                                print(
                                    "Assistant's response: ",
                                    assistant_message["content"],
                                )
                                # Reset the frames list for the next recording
                        else:
                            # Optionally, keep recording silence for a smoother transition
                            frames.append(buffer)

    except KeyboardInterrupt:
        # driver.close_browser()
        pass  # Exit on Ctrl+C

    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
        # audio_file= open("recording.wav", "rb")
        # transcript = openai.Audio.transcribe("whisper-1", audio_file)
        # print(transcript)
        # driver.close_browser()


if __name__ == "__main__":
    main()
