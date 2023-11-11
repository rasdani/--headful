import os
from dotenv import load_dotenv
import base64
import requests

load_dotenv()
# OpenAI API Key
api_key = os.getenv("OPENAI_API_KEY")


# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


# Path to your image
# message = "The little Github logo in this screenshot is annotated with a small yellow lable. What letter is on the label?"


def see(image_path, user_request):
    base64_image = encode_image(image_path)
    message = """This is a screenshot of a web page. The clickable elements of the page are annotated with small yellow labels containing a code of one or two letters. \
        Now follows a user request. Interpret which element the user wants to click on and return the corresponding letter code. \
        Respond by citing the letter code only!
    USER REQUEST: {user_request}"""
    message = message.format(user_request=user_request)

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": message},
                    {
                        "type": "image_url",
                        "image_url": {
                            # "url": f"data:image/jpeg;base64,{base64_image}"
                            "url": f"data:image/png;base64,{base64_image}"
                        },
                    },
                ],
            }
        ],
        "max_tokens": 300,
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
    )
    response_json = response.json()
    response_message = response_json["choices"][0]["message"]["content"]
    print(response_message)
    return response_message


if __name__ == "__main__":
    image_path = "screenshot_after.png"
    while True:
        user_request = input("User request: ")
        see(image_path, user_request)
