import os
from dotenv import load_dotenv
import base64
import requests
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

LABEL_DESCRIPTION = "small yellow"
LABEL_COLOR = "large red"

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def see(image_path, user_request):
    base64_image = encode_image(image_path)
    message = """This is a screenshot of a web page. The clickable elements of the page are annotated with small yellow labels containing a code of one or two letters. \
        Now follows a user request. Interpret which element the user wants to interact with and return the corresponding letter code. \
        Respond by citing the letter code only!
    USER REQUEST: {user_request}"""
    message = message.format(user_request=user_request)

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    payload = {
        "model": "gpt-4-vision-preview",
        "temperature": 0.0,
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

def see_legacy(image_paths, user_request):
    base64Frames = [encode_image(image_path) for image_path in image_paths]
    message = """\
## Description
These are two screenshots of the same webpage. The first one just shows the webpage, the second one overlays the webpage with {label_description} labels. \
All clickable elements of the page are annotated with these {label_description} labels containing one or two letters. \
## Objective
Now follows a request. Indentify the relevant webpage element by looking at the first screenshot and look up the corresponding annotation label by referencing the second screenshot. \
Respond by citing the letter code only!\
## Request
{user_request}"""
    message = message.format(user_request=user_request, label_description=LABEL_DESCRIPTION)
    PROMPT_MESSAGES = [
        {
            "role": "user",
            "content": [
                message,
                *map(lambda x: {"image": x, "resize": 768}, base64Frames),
            ],
        },
    ]
    params = {
        "model": "gpt-4-vision-preview",
        "temperature": 0.0,
        "messages": PROMPT_MESSAGES,
        # "api_key": api_key,
        # "headers": {"Openai-Version": "2020-11-07"},
        "max_tokens": 200,
    }

    # result = openai.ChatCompletion.create(**params)
    result = client.chat.completions.create(**params)
    response = result.choices[0].message.content
    return response

if __name__ == "__main__":
    image_path = "screenshot_after.png"
    while True:
        user_request = input("User request: ")
        see(image_path, user_request)
