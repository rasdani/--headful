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
    # home_dir = os.getenv("HOME")
    # path_to_extension = os.path.join(home_dir, "git/vimium")
    path_to_extension = "./vimium"
    args = [
        f"--disable-extensions-except={path_to_extension}",
        f"--load-extension={path_to_extension}",
        # "--window-size=960,800",
    ]
    # viewport_size = {"width": 960, "height": 800}
    # viewport_size = {"width": 960, "height": 670}
    # viewport_size = {"width": 1280, "height": 720}
    # screen_size = {"width": 960, "height": 800}
    viewport_size = None
    # with sync_playwright() as playwright:
    try:
        playwright = sync_playwright().start()
        # context = playwright.chromium.launch(headless=False, args=args)
        # context = playwright.firefox.launch(headless=False, args=args)
        iPhone = playwright.devices["iPhone 12"]
        viewport_size = iPhone["viewport"]
        context = playwright.chromium.launch_persistent_context(
            "./browser-data",
            headless=False,
            args=args,
            # screen=screen_size,
            # device_scale_factor=1.5,
            user_agent=iPhone["user_agent"],
        )
        # context.pages[0].close()  # Close the initial page
        driver = WebDriver(
            playwright=playwright,
            context=context, 
            viewport_size=viewport_size
        )
        # try mobile
        # browser = playwright.chromium.launch(headless=False, args=args)
        # context = browser.new_context(**iPhone)
        # context = browser.new_context(user_agent=iPhone["user_agent"])
        # driver = WebDriver(
        #     playwright=playwright, context=context, 
        #     # viewport_size=iPhone["viewport"]
        # )
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
