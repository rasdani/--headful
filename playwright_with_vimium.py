import os
from playwright.sync_api import sync_playwright

def run(playwright):
    chromium = playwright.chromium
    # Path to the extension
    home_dir = os.getenv("HOME")
    path_to_extension = os.path.join(home_dir, 'git/vimium')
    # Launching browser with a persistent context
    browser_context = chromium.launch_persistent_context(
        './user-data-dir',
        headless=False,  # Extensions are not supported in headless mode
        args=[
            f'--disable-extensions-except={path_to_extension}',
            f'--load-extension={path_to_extension}',
        ]
    )
    page = browser_context.new_page()
    page.goto('https://github.com')
    # page.screenshot(path='screenshot_before.png')
    page.keyboard.press('f')
    page.screenshot(path='screenshot_after.png')
    # Interact with the background page or the popup of the extension
    # ...

    input('Press Enter to exit...')
    browser_context.close()

with sync_playwright() as playwright:
    run(playwright)
