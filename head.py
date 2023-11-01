import json
import requests
import os
import openai
from dotenv import load_dotenv
from tenacity import retry, wait_random_exponential, stop_after_attempt
from playwright.sync_api import sync_playwright, Playwright
from drive_browser import WebDriver


load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
GPT_MODEL = "gpt-3.5-turbo-0613"


@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
def chat_completion_request(messages, functions=None, function_call=None, model=GPT_MODEL):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + openai.api_key,
    }
    json_data = {"model": model, "messages": messages}
    if functions is not None:
        json_data.update({"functions": functions})
    if function_call is not None:
        json_data.update({"function_call": function_call})
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=json_data,
        )
        print(f"{response.status_code=}")
        return response
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e

functions = [
    {
        "name": "visit_website",
        "description": "Visit a given website",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL to enter into the browser",
                },
            },
            "required": ["url"],
        },
    }
]

def visit_website(url):
    with sync_playwright() as playwright:
        driver = WebDriver(playwright)
        driver.start_browser(headless=False)
        driver.navigate_to(url)
    return "Success"

def execute_function_call(function_call):
    if function_call["name"] == "visit_website":
        url = json.loads(function_call["arguments"])["url"]
        results = visit_website(url)
    else:
        results = f"Error: function {function_call['name']} does not exist"
    return results



messages = []
messages.append({"role": "system", "content": "Navigate a web browser with the provided functions."})
# messages.append({"role": "user", "content": "Hi, who are the top 5 artists by number of tracks?"})

while True:
    user_input = input("Enter your message: ")
    if user_input.lower() == "quit":
        break
    messages.append({"role": "user", "content": user_input})
    chat_response = chat_completion_request(
        messages,
        functions=functions,
    )
    print(f"{chat_response=}")
    print(f"{chat_response.text=}")
    assistant_message = chat_response.json()["choices"][0]["message"]
    assistant_message = chat_response.json()["choices"][0]["message"]
    if "function_call" in assistant_message:
        function_call = assistant_message["function_call"]
        execute_function_call(function_call)  # Assuming this function is set up to handle the function call object
    else:
        messages.append(assistant_message)
        print("Assistant's response: ", assistant_message["content"])
