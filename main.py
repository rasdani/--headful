import openai
from dotenv import load_dotenv
import os
from playwright.sync_api import sync_playwright
import json

from drive_browser import WebDriver
from head import chat_completion_request, execute_function_call


load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def main():
    messages = []
    messages.append(
        {
            "role": "system",
            "content": "Navigate a web browser with the provided functions.",
        }
    )
    with sync_playwright() as playwright:
        # driver = WebDriver(playwright)
        # driver.start_browser(headless=False)
        while True:
            user_input = input("Enter your message: ")
            messages.append({"role": "user", "content": user_input})
            func_call = chat_completion_request(messages)
            print(f"{messages=}")
            print(f"{func_call=}")

            # driver = execute_function_call(driver, func_call)
            messages = []
            print(messages)
            # if "function_call" in assistant_message:
            #     function_call = assistant_message["function_call"]
            #     execute_function_call(driver, function_call)  # Assuming this function is set up to handle the function call object
            # else:
            #     messages.append(assistant_message)
            #     print("Assistant's response: ", assistant_message["content"])
            # if "function_call" in assistant_message:
            #     function_call = assistant_message["function_call"]
            #     execute_function_call(driver, function_call)  # Assuming this function is set up to handle the function call object
            # else:
            #     messages.append(assistant_message)
            #     print("Assistant's response: ", assistant_message["content"])


if __name__ == "__main__":
    main()
