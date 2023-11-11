import openai
from dotenv import load_dotenv
import os
from playwright.sync_api import sync_playwright
import json

from drive_browser import WebDriver
from head import visit_website, execute_browser_action, functions, MODEL, execute_function_call, create_assistant, create_thread, add_message_to_thread, create_assistant_run, wait_for_run, get_tool_calls, get_call_ids, submit_tool_outputs, list_messages


load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def main():
    messages = []
    messages.append({"role": "system", "content": "Navigate a web browser with the provided functions."})

    with sync_playwright() as playwright:
        # driver = WebDriver(playwright)
        # driver.start_browser(headless=False)
        user_input = input("Enter your message: ")
        print(f"{user_input=}") 
        name = "Web Browser Assistant"
        instructions="You are the operator of a web browser. Translate user requests into calls of the provided browser functions."
        assistant = create_assistant(name=name, instructions=instructions, tools=tools, model=MODEL)
        thread = create_thread()
        message = "Visit google"
        message_obj = add_message_to_thread(thread, message)
        run = create_assistant_run(thread, assistant)
        run = wait_for_run(run)
        tool_calls = get_tool_calls(run)
        call_ids = get_call_ids(tool_calls)
        run = submit_tool_outputs(thread, run, call_ids, outputs)
        run = wait_for_run(run)
        messages = list_messages(thread)
    print(messages)
        if "function_call" in assistant_message:
            function_call = assistant_message["function_call"]
            execute_function_call(driver, function_call)  # Assuming this function is set up to handle the function call object
        else:
            messages.append(assistant_message)
            print("Assistant's response: ", assistant_message["content"])


if __name__ == "__main__":
    main()
