import openai
from dotenv import load_dotenv
import os
from playwright.sync_api import sync_playwright
import json

from drive_browser import WebDriver
from head import (
    get_tool_calls,
    create_assistant_run,
    get_tool_call_ids,
    visit_website,
    execute_browser_action,
    tools,
    MODEL,
    execute_function_call,
    add_message_to_thread,
    wait_for_run,
    submit_tool_outputs,
    list_messages,
    setup_chat,
)


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
    name = "Web Browser Assistant"
    instructions = "You are the operator of a web browser. Translate user requests into calls of the provided browser functions."
    assistant, thread = setup_chat(name, instructions, tools, MODEL)

    with sync_playwright() as playwright:
        # driver = WebDriver(playwright)
        # driver.start_browser(headless=False)
        # user_input = input("Enter your message: ")
        # print(f"{user_input=}")
        message = "Visit google"
        message_obj = add_message_to_thread(thread, message)
        run = create_assistant_run(thread, assistant)
        tool_calls = get_tool_calls(run)
        call_ids = get_tool_call_ids(run)
        outputs = ["Success"]
        run = submit_tool_outputs(thread, run, call_ids, outputs)
        messages = list_messages(thread)
        print(messages)
        # if "function_call" in assistant_message:
        #     function_call = assistant_message["function_call"]
        #     execute_function_call(driver, function_call)  # Assuming this function is set up to handle the function call object
        # else:
        #     messages.append(assistant_message)
        #     print("Assistant's response: ", assistant_message["content"])


if __name__ == "__main__":
    main()
