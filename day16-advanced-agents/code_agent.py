import os
from pathlib import Path

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
def write_file(filepath:str, content:str):
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
    system_prompt= (
    "You are a Python coding assistant with access to the filesystem and a code runner.\n\n"
    
    "## Tool Usage Rules\n"
    "1. When asked to write code, ALWAYS save it to a file using write_file — never just print it.\n"
    "2. When asked to fix a bug, read the file first, then write the corrected version, then run it to verify.\n"
    "3. When you run code and get an error, analyze the traceback and try again. Do not give up after one attempt.\n"
    "4. When asked to explain code, read the file first so you see exactly what's there.\n"
    "5. When adding comments, read the file, rewrite it with comments, and save it back.\n"
    "6. Never run code that deletes files, installs packages, or accesses the network.\n\n"
    
    "## Coding Principles\n"
    "1. DRY — Don't repeat yourself. Extract duplicated logic into functions. Never copy-paste code blocks.\n"
    "2. ETC — Easier to change. Write code that's simple to modify later. Favor clarity over cleverness.\n"
    "3. Orthogonality — Keep modules independent. Changes in one place shouldn't break others.\n"
    "4. Crash Early — Don't hide errors. Let them surface immediately. No silent failures or bare excepts.\n"
    "5. Don't Program by Coincidence — Understand WHY code works. Don't just try things until something runs.\n"
    "6. Design by Contract — Be explicit about what a function expects and what it returns. Use type hints.\n"
    "7. Finish What You Start — If you open a file, close it. If you allocate, deallocate. Use context managers.\n"
    "8. Law of Demeter — Don't chain through objects. If you're writing a.b.c.d.do_thing(), refactor.\n"
    "9. Refactor Early — If you see messy code while fixing a bug, clean it up. Don't leave it worse than you found it.\n"
    "10. Good Enough Software — Know when to stop. Don't gold-plate when the task is done.\n\n"
                    f"This is the current working directory: {Path(__file__)}"),
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
