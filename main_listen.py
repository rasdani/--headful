import time
from time import sleep
from dotenv import load_dotenv
import os
from playwright.sync_api import sync_playwright

from drive_browser import WebDriver

def setup():
    screenshot_dir = f"browser-recordings/{time.time()}/screenshots"
    os.makedirs(screenshot_dir, exist_ok=True)
    return screenshot_dir

def take_screenshot_on_navigation(driver, event, screenshot_dir):
    driver.take_screenshot(screenshot_dir)
    print("SCREENSHOT TAKEN")

def main():
    screenshot_dir = setup()
    playwright = None
    context = None
    path_to_extension = "./vimium"
    args = [
        f"--disable-extensions-except={path_to_extension}",
        f"--load-extension={path_to_extension}",
    ]
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
        page = context.pages[1]
        # page.on("framenavigated", lambda event: take_screenshot_on_navigation(driver, event, screenshot_dir))
        while True:
            sleep(2)
            print(f"{context.pages}")
            # page.wait_for_load_state("networkidle")
            while not page.wait_for_event("framenavigated"):
                sleep(2)
                print("WAITING...")

            screenshot_path = f"{screenshot_dir}/{time.time()}.png"
            driver.take_screenshot(screenshot_path)
            print("SCREENSHOT TAKEN")

            # page.on("framenavigated", lambda event: take_screenshot_on_navigation(page, event, screenshot_dir))


            # with open('vimium_triggered.txt', 'r') as f:
            #     flag = f.read().strip()
            # if flag == 'True':
            #     driver.take_screenshot(f"{screenshot_dir}")
            #     with open('vimium_triggered.txt', 'w') as f:
            #         f.write('False')    # Reset the flag
            # user_input = input("Enter your message: ")
            # if user_input == "x":
            #     break
            # if user_input == "s":
            #     driver.take_screenshot()
            #     continue

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
