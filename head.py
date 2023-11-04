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
# GPT_MODEL = "gpt-3.5-turbo-0613"
GPT_MODEL = "gpt-3.5-turbo"
# GPT_MODEL = "gpt-4"


# @retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
# def chat_completion_request(messages, functions=None, function_call=None, model=GPT_MODEL):
#     print(f"{model=}")
#     headers = {
#         "Content-Type": "application/json",
#         "Authorization": "Bearer " + openai.api_key,
#     }
#     # json_data = {"model": model, "messages": messages}
#     json_data = {"model": model, "temperature": 0, "messages": messages}
#     if functions is not None:
#         json_data.update({"functions": functions})
#     if function_call is not None:
#         json_data.update({"function_call": function_call})
#     try:
#         response = requests.post(
#             "https://api.openai.com/v1/chat/completions",
#             headers=headers,
#             json=json_data,
#         )
#         print(f"{response.status_code=}")
#         return response
#     except Exception as e:
#         print("Unable to generate ChatCompletion response")
#         print(f"Exception: {e}")
#         return e

def chat_completion_request(messages, functions=None, function_call="auto", model=GPT_MODEL):
    print(f"{model=}")
    try:
        completion = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        functions=functions,
        function_call=function_call,
        temperature=0,
        )
        return completion
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e

functions = [
    {
        "name": "visit_website",
        "description": "Use this function to visit a website requested by the user.",
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
    },
    {
        "name": "execute_browser_action",
        # "description": "Execute a given action in the browser",
        "description": "Use this function to go back, go forward, or open a new tab",
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "The action to be performed in the browser. Can be 'go_back', 'go_forward', or 'new_tab'.",
                },
            },
            "required": ["action"],
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
# system_message = "Navigate a web browser with the provided functions."
# system_message = "You are the operator of a web browser. Your objective is to understand user requests and translate them into proper calls of the provided browser functions."
system_message = "Use function_call to translate user requests into proper calls of the provided browser functions."
# system_message = """
# You are a helpful assistant. 
# Respond to the following prompt by using function_call and then summarize actions. 
# Ask for clarification if a user request is ambiguous.
# """
# system_message = """
# You are a the operator of web browser. 
# Respond to the following prompt by using function_call to call the provided functions with proper arguments. 
# Don not talk, just execute the function calls. You are an operator, not a conversation partner.
# """
messages.append({"role": "system", "content": system_message})
# messages.append({"role": "user", "content": "Hi, who are the top 5 artists by number of tracks?"})

if __name__ == "__main__":
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
        if "function_call" in assistant_message:
            function_call = assistant_message["function_call"]
            execute_function_call(function_call)  # Assuming this function is set up to handle the function call object
        else:
            messages.append(assistant_message)
            print("Assistant's response: ", assistant_message["content"])
