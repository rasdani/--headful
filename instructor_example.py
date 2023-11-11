import os
import json
from typing_extensions import Annotated
from enum import Enum
from pydantic import BaseModel, BeforeValidator, validator
from instructor import llm_validator, patch
import openai
from dotenv import load_dotenv
from typing import Optional, Union
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
from drive_browser import WebDriver

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
patch()

GPT_MODEL = "gpt-3.5-turbo-0613"
system_message = "Use function_call to translate user requests into proper calls of the provided browser functions."
messages = [
    {
        "role": "system",
        "content": system_message,
    },
]
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
    },
]


def visit_website(driver, url):
    driver.navigate_to(url)
    return driver


class FunctionName(Enum):
    VISIT_WEBSITE = "visit_website"
    EXECUTE_BROWSER_ACTION = "execute_browser_action"


class VisitWebsiteArgs(BaseModel):
    url: str

    @validator("url")
    def check_url(cls, v):
        parsed = urlparse(v)
        if not all([parsed.scheme, parsed.netloc]):
            raise ValueError("Invalid URL")
        return v


class BrowserAction(Enum):
    GO_BACK = "go_back"
    GO_FORWARD = "go_forward"
    NEW_TAB = "new_tab"


class ExecuteBrowserActionArgs(BaseModel):
    action: BrowserAction


class FunctionCall(BaseModel):
    function_name: FunctionName
    arguments: Union[VisitWebsiteArgs, ExecuteBrowserActionArgs, None]


def execute_browser_action(driver, action: BrowserAction):
    page = driver.page
    if action == BrowserAction.GO_BACK:
        page.go_back()
    elif action == BrowserAction.GO_FORWARD:
        page.go_forward()
    elif action == BrowserAction.NEW_TAB:
        new_page = page.context.new_page()
        driver.page = new_page
    else:
        raise ValueError(f"Unknown action: {action.action}")
    return driver


def execute_function_call(driver, function_call: FunctionCall):
    if function_call.function_name == FunctionName.VISIT_WEBSITE:
        url = function_call.arguments.url
        driver = visit_website(driver, url)
    elif function_call.function_name == FunctionName.EXECUTE_BROWSER_ACTION:
        action = function_call.arguments.action
        driver = execute_browser_action(driver, action)
    else:
        raise ValueError(
            f"Error: function {function_call.function_name} does not exist"
        )
    return driver


try:
    with sync_playwright() as playwright:
        driver = WebDriver(playwright)
        driver.start_browser(headless=False)
        while True:
            user_input = input("Enter your message: ")
            messages.append({"role": "user", "content": user_input})
            func_call: FunctionCall = openai.ChatCompletion.create(
                model=GPT_MODEL,
                temperature=0,
                response_model=FunctionCall,
                messages=messages,
                functions=functions,
                max_retries=1,
            )
            print(f"{messages=}")
            print(f"{func_call=}")

            driver = execute_function_call(driver, func_call)
            messages = []

except KeyboardInterrupt:
    pass

# finally:
# driver.close_browser()
