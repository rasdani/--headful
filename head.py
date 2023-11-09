from openai import OpenAI
import instructor
from enum import Enum
from pydantic import BaseModel, validator
from urllib.parse import urlparse
from typing import Union
from dotenv import load_dotenv

load_dotenv()
client = instructor.patch(OpenAI())
# MODEL = "gpt-4-1106-preview"
# MODEL = "gpt-4"
MODEL = "gpt-3.5-turbo-1106"

class FunctionName(Enum):
    VISIT_WEBSITE = 'visit_website'
    EXECUTE_BROWSER_ACTION = 'execute_browser_action'

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
        raise ValueError(f"Error: function {function_call.function_name} does not exist")
    return driver

tools = [
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
    }
]

# Create Assistant
assistant = client.beta.assistants.create(
    name="Web Browser Assistant",
    instructions="You are the operator of a web browser. Translate user requests into calls of the provided browser functions.",
    tools=tools,
    model=MODEL,
)

# Create Thread
thread = client.beta.threads.create()

# Add a message to the thread
user_message = "Visit google"
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content=user_message,
)
thread_messages = client.beta.threads.messages.list(thread_id=thread.id)
# print(f"{thread.data=}")

# Run the Assistant
run = client.beta.threads.runs.create(
  thread_id=thread.id,
  assistant_id=assistant.id,
#   instructions="Please address the user as Jane Doe. The user has a premium account."
)

# Retrive run and check its status
run = client.beta.threads.runs.retrieve(
  thread_id=thread.id,
  run_id=run.id,
)
print(f"{run.status=}")

# Retrieve Assistant's response
messages = client.beta.threads.messages.list(
  thread_id=thread.id
)
print(f"{messages=}")

# Optionally inspect the run steps
run_steps = client.beta.threads.runs.steps.list(
    thread_id=thread.id,
    run_id=run.id
)
print(f"{run_steps=}")

# Retriece run to get function call ids
# Retrive run and check its status
run = client.beta.threads.runs.retrieve(
  thread_id=thread.id,
  run_id=run.id,
)
tool_calls = run.required_action.submit_tool_outputs.tool_calls
print(f"{tool_calls=}")
# call_ids = [call.tool_call_id for call in tool_calls]

### excute function

# Submit function call outputs
# run = client.beta.threads.runs.submit_tool_outputs(
#   thread_id=thread.id,
#   run_id=run.id,
#   tool_outputs=[
#       {
#         "tool_call_id": call_ids[0],
#         "output": "22C",
#       },
#       {
#         "tool_call_id": call_ids[1],
#         "output": "LA",
#       },
#     ]
# )