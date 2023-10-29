from time import sleep
from playwright.sync_api import sync_playwright, Playwright

class WebDriver:
    def __init__(self, playwright: Playwright):
        self.playwright = playwright
        self.browser = None
        self.context = None
        self.page = None

    def start_browser(self, headless=False, browser_type="chromium"):
        browser_launcher = getattr(self.playwright, browser_type, None)
        if not browser_launcher:
            raise ValueError(f"Invalid browser type: {browser_type}")
        self.browser = browser_launcher.launch(headless=headless, args=["--start-maximized"])
        self.context = self.browser.new_context()
        self.page = self.context.new_page()

    def navigate_to(self, url):
        if self.page:
            self.page.goto(url)

    def click_coordinates(self, x_coord, y_coord):
        if self.page:
            self.page.mouse.click(x_coord, y_coord)

    def enter_text(self, text):
        if self.page:
            self.page.keyboard.type(text)

    def press_enter(self):
        if self.page:
            self.page.keyboard.press('Enter')

    def take_screenshot(self, screenshot_path="screenshot.png"):
        if self.page:
            self.page.screenshot(path=screenshot_path)

    def close_browser(self):
        if self.browser:
            self.browser.close()

# Example Usage:
if __name__ == "__main__":
    with sync_playwright() as playwright:
        driver = WebDriver(playwright)
        driver.start_browser(headless=False)
        # URL = "https://www.startpage.com/"
        # URL = "https://google.com/"
        URL = "https://github.com/rasdani"
        driver.navigate_to(URL)
        sleep(5)
        # driver.click_coordinates(650, 270)
        # driver.enter_text("Hello World")
        # driver.click_coordinates(880, 270)
        # driver.press_enter()
        # sleep(5)
        # driver.take_screenshot("example_screenshot.png")
        driver.take_screenshot("github_screenshot.png")
        driver.close_browser()
