### instructor has way better undocumented features now
from time import sleep
from openai import OpenAI
import instructor
from enum import Enum
from pydantic import BaseModel, validator
from urllib.parse import urlparse
from typing import Union
from dotenv import load_dotenv

load_dotenv()
client = instructor.patch(OpenAI())
GPT_MODEL = "gpt-4-1106-preview"
# MODEL = "gpt-4"
# GPT_MODEL = "gpt-3.5-turbo-1106"
# MODEL = "gpt-3.5-turbo"


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


def visit_website(driver, url):
    driver.navigate_to(url)
    return driver


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


functions = [
    {
        "type": "function",
        "function": {
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
    },
    {
        "type": "function",
        "function": {
            "name": "execute_browser_action",
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
    },
]

def chat_completion_request(messages, functions=functions, model=GPT_MODEL):
    try:
        func_call: FunctionCall = client.chat.completions.create(
            model=model,
            temperature=0,
            response_model=FunctionCall,
            messages=messages,
            functions=functions,
            max_retries=2,
        )
        return func_call
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e
