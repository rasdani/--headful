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
# MODEL = "gpt-4-1106-preview"
# MODEL = "gpt-4"
MODEL = "gpt-3.5-turbo-1106"
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
    },
]


def create_assistant(**kwargs):
    assistant = client.beta.assistants.create(**kwargs)
    return assistant


def create_thread():
    thread = client.beta.threads.create()
    return thread


def add_message_to_thread(thread, message):
    message_obj = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=message,
    )
    return message_obj


def list_messages(thread):
    thread_messages = client.beta.threads.messages.list(thread_id=thread.id)
    return thread_messages


def create_assistant_run(thread, assistant):
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )
    run = wait_for_run(thread, run)
    return run


def get_run(thread, run):
    run = client.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id,
    )
    return run


def update_run(thread, run):
    run = client.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id,
    )
    return run


def get_run_steps(thread, run):
    run_steps = client.beta.threads.runs.steps.list(thread_id=thread.id, run_id=run.id)
    return run_steps


def wait_for_run(thread, run):
    status = run.status
    print(f"{status}")
    while status in ["in_progress", "queued"]:
        sleep(1)
        run = update_run(thread, run)
        status = run.status
        print(f"{status}")
    print(f"{status}")
    return run


def get_tool_calls(run):
    tool_calls = run.required_action.submit_tool_outputs.tool_calls
    return tool_calls


def get_call_ids(tool_calls):
    return [call.id for call in tool_calls]


def submit_tool_outputs(thread, run, call_ids, outputs):
    tool_outputs = [
        {"tool_call_id": call_id, "output": output}
        for call_id, output in zip(call_ids, outputs)
    ]
    run = client.beta.threads.runs.submit_tool_outputs(
        thread_id=thread.id,
        run_id=run.id,
        tool_outputs=tool_outputs,
    )
    run = wait_for_run(thread, run)
    return run


def setup_chat(assistant_name, instructions, tools, model):
    assistant = create_assistant(
        name=assistant_name, instructions=instructions, tools=tools, model=model
    )
    thread = create_thread()
    return assistant, thread

def get_tool_call_ids(run):
    tool_calls = get_tool_calls(run)
    call_ids = get_call_ids(tool_calls)
    return call_ids

if __name__ == "__main__":
    name = "Web Browser Assistant"
    instructions = "You are the operator of a web browser. Translate user requests into calls of the provided browser functions."
    assistant = create_assistant(
        name=name, instructions=instructions, tools=tools, model=MODEL
    )
    thread = create_thread()
    message = "Visit google"
    message_obj = add_message_to_thread(thread, message)
    run = create_assistant_run(thread, assistant)
    run = wait_for_run(thread, run)
    tool_calls = get_tool_calls(run)
    call_ids = get_call_ids(tool_calls)
    outputs = ["Success"]
    run = submit_tool_outputs(thread, run, call_ids, outputs)
    run = wait_for_run(thread, run)
    messages = list_messages(thread)
    print(messages)
