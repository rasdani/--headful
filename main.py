import openai
from dotenv import load_dotenv
import os
from playwright.sync_api import sync_playwright
import json

from drive_browser import WebDriver
from head import function_call_request, execute_function_call


load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def main():
    messages = []
    messages.append(
        {
            "role": "system",
            "content": "Navigate a web browser with the provided functions. If the user wants to click on a specific webpage element, pass the request on",
        }
    )
    playwright = None
    context = None
    path_to_extension = "./vimium"
    args = [
        f"--disable-extensions-except={path_to_extension}",
        f"--load-extension={path_to_extension}",
    ]
    viewport_size = None
    try:
        playwright = sync_playwright().start()
        iPhone = playwright.devices["iPhone 12"]
        viewport_size = iPhone["viewport"]
        context = playwright.chromium.launch_persistent_context(
            "./browser-data",
            headless=False,
            args=args,
            user_agent=iPhone["user_agent"],
        )
        driver = WebDriver(
            playwright=playwright, context=context, viewport_size=viewport_size
        )
        while True:
            user_input = input("Enter your message: ")
            if user_input == "x":
                break
            if user_input == "s":
                driver.take_screenshot()
                continue
            messages.append({"role": "user", "content": user_input})
            func_call = function_call_request(messages)
            print(f"{func_call=}")
            driver, response = execute_function_call(driver, func_call)
            print(f"{response=}")
            messages = []

    except KeyboardInterrupt:
        print("Exiting...")
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Exiting...")

    finally:
        if context:
            print("Cleaning up context...")
            context.close()
        if playwright:
            print("Stopping playwright...")
            playwright.stop()
        print("Done.")


if __name__ == "__main__":
    main()
