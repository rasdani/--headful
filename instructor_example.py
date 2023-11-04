import os
from typing_extensions import Annotated
from enum import Enum
from pydantic import BaseModel, BeforeValidator, validator
from instructor import llm_validator, patch
import openai
from dotenv import load_dotenv
from typing import Optional, Union
from urllib.parse import urlparse

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
    }
]

# class Functions(BaseModel):
#     functions: list[Function] 

# class FunctionCall(BaseModel):
#     function: Function
#     arguments: str


class Function(BaseModel):
    name: str
    # parameters: dict
    arguments: str

class VisitWebsiteArgs(BaseModel):
    url: str

    @validator('url')
    def check_url(cls, v):
        parsed = urlparse(v)
        if not all([parsed.scheme, parsed.netloc]):
            raise ValueError('Invalid URL')
        return v


class BrowserAction(Enum):
    GO_BACK = 'go_back'
    GO_FORWARD = 'go_forward'
    NEW_TAB = 'new_tab'

class ExecuteBrowserActionArgs(BaseModel):
    action: BrowserAction

class FunctionCall(BaseModel):
    function: Function
    arguments: Union[VisitWebsiteArgs, ExecuteBrowserActionArgs, None]

while True:
    user_input = input("Enter your message: ")
    messages.append({"role": "user", "content": user_input})    
    qa: FunctionCall = openai.ChatCompletion.create(
        model=GPT_MODEL,
        temperature=0,
        response_model=FunctionCall,
        messages=messages,
        functions=functions,
        max_retries=1,
    )
    print(f"{qa=}")
