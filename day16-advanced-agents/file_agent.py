import os
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver

from shared import read_document

# from rich import inspect

load_dotenv()

model = init_chat_model(model='gpt-5-mini')

checkpoint = InMemorySaver()
config = {'configurable' : {'thread_id' : 1}}

def security_check(filepath):
    blocked_files = [".env", "secrets.json", "config.yml", f"{Path(__file__)}"]
    resolved = Path(filepath).resolve()
    if resolved.name in blocked_files:
        return "ERROR: Access to sensitive files is denied."
    

@tool(
    "read_file",
    description=(
        "Read and return the full contents of a single file. "
        "Accepts an absolute or relative file path (e.g. 'notes/todo.txt'). "
        "Returns the file content as a string."
    ),
)
def read_file(filepath:str)-> str:
    result = security_check(filepath)
    if result:
        return result
    return read_document(filepath)

@tool(
    "write_file", 
    description=(
        "Create or overwrite a file with the provided content. "
        "Accepts a filename including its extension (e.g. 'report.txt', 'data.csv'). "
        "The file is written with UTF-8 encoding. "
        "Returns a success confirmation or an error message."
    ),
)
def write_file(filepath:str, content:Any):
    result = security_check(filepath)
    if result:
        return result
    try:
        with open(filepath, 'w',encoding='utf-8') as f:
            f.write(str(content))
        return f"Successfully wrote to '{filepath}'."
    except Exception as e:
        return(f"Error writing file: {e}")

@tool(
    "list_directory",
    description=(
        "List every file and folder inside the given directory. "
        "Accepts an absolute or relative directory path (e.g. '.', './src'). "
        "Returns a list of entry names (files and sub-directories)."
    ),
)
def list_directory(directory:str ):
    try:
        return os.listdir(directory)
    except FileNotFoundError:
        return [f"Error: directory '{directory}' not found."]


@tool(
    "create_directory",
    description=(
        "Create a new directory at the specified path. "
        "Fails gracefully if the directory already exists. "
        "Accepts an absolute or relative path (e.g. 'logs', 'output/reports')."
    ),
)
def create_directory(directory: str) -> str:  
    """Create a new folder; report if it already exists."""
    if os.path.exists(directory):
        return f"Directory '{directory}' already exists — choose a different name."
    try:
        os.makedirs(directory)  
        return f"Directory '{directory}' created successfully."
    except Exception as e:
        return f"Error creating directory: {e}"


@tool(
    "file_exists",
    description=(
        "Check whether a file exists at the given path. "
        "Returns a clear yes/no answer. "
        "Useful before reading or writing to avoid errors."
    ),
)
def file_exists(filepath: str) -> str:  
    """Return whether a specific file exists."""
    if os.path.isfile(filepath):
        return f"Yes — '{filepath}' exists and is a file."
    elif os.path.isdir(filepath):
        return f"'{filepath}' exists but is a directory, not a file."
    else:
        return f"No — '{filepath}' does not exist."


agent = create_agent(
    model= model,
    system_prompt= "You are a helpful assistant that uses the available tools "
                    "to read, write, search, and organise files on the user's behalf."
                    f"This is the current working directory: {Path(__file__)}",
    checkpointer=checkpoint,
    tools=[read_file, write_file, list_directory, create_directory, file_exists],
    
)

while True:
    user_input = input('Human: ')
    if user_input.lower() == "quit":
        break
    else:
        response = agent.invoke({
            'messages': [{'role': 'user', 'content': user_input}]
        }, 
        config= config
        )
        print(f"AI: {response['messages'][-1].content}\n")  
        