import os
from pathlib import Path
from typing import Any, List, Union

# Intentionally not loading .env files in this copy.
# from dotenv import load_dotenv

# Verify these imports match your installed libraries (LangChain / langgraph)
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver

from shared import read_document

# NOTE: We are NOT calling load_dotenv() here so any .env file will be ignored.

# Initialize model (use the correct model name for your environment)
# Replace 'gpt-5-mini' with the actual model name you have available
model = init_chat_model(model="gpt-5-mini")

# Checkpointer / checkpoint
checkpoint = InMemorySaver()
config = {"configurable": {"thread_id": 1}}


def _is_env_file(path: str) -> bool:
    """Return True if the path refers to a dotenv-style file we want to block.

    Blocking policy:
    - Any file whose basename equals '.env'
    - Any file whose basename starts with '.env' (e.g. '.env.local')
    - Any file whose basename ends with '.env' (e.g. 'production.env')

    This is intentionally conservative. Adjust the logic if you want a
    different policy.
    """
    try:
        name = Path(path).name
        if not name:
            return False
        return name == ".env" or name.startswith(".env") or name.endswith(".env")
    except Exception:
        return False


# Tools
@tool(
    "read_file",
    description=(
        "Read and return the full contents of a single file. "
        "Accepts an absolute or relative file path (e.g. 'notes/todo.txt'). "
        "Returns the file content as a string."
    ),
)
def read_file(filepath: str) -> str:
    if _is_env_file(filepath):
        # Deny access to dotenv files
        return "Error: access to .env files is disabled for security reasons."
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
def write_file(filepath: str, content: Any) -> str:
    if _is_env_file(filepath):
        return "Error: writing to .env files is disabled for security reasons."
    try:
        # Ensure parent directory exists
        parent = os.path.dirname(filepath)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(str(content))
        return f"Successfully wrote to '{filepath}'."
    except Exception as e:
        return f"Error writing file: {e}"


@tool(
    "list_directory",
    description=(
        "List every file and folder inside the given directory. "
        "Accepts an absolute or relative directory path (e.g. '.', './src'). "
        "Returns a list of entry names (files and sub-directories)."
    ),
)
def list_directory(directory: str) -> Union[List[str], List[str]]:
    try:
        entries = os.listdir(directory)
        # Filter out dotenv-style files so the agent cannot discover them
        filtered = [e for e in entries if not _is_env_file(os.path.join(directory, e))]
        return filtered
    except FileNotFoundError:
        return [f"Error: directory '{directory}' not found."]


@tool(
    "create_directory",
    description=(
        "Create a new directory at the specified path. "
        "Fails gracefully if the directory already exists."
    ),
)
def create_directory(directory: str) -> str:
    # Creating a directory named like a dotenv file is unlikely but block anyway
    if _is_env_file(directory):
        return "Error: creating directories with .env-style names is disallowed."
    if os.path.exists(directory):
        return f"Directory '{directory}' already exists — choose a different name."
    try:
        os.makedirs(directory, exist_ok=True)
        return f"Directory '{directory}' created successfully."
    except Exception as e:
        return f"Error creating directory: {e}"


@tool(
    "file_exists",
    description=(
        "Check whether a file exists at the given path. "
        "Returns a clear yes/no answer."
    ),
)
def file_exists(filepath: str) -> str:
    # To avoid revealing whether a dotenv file exists, treat them as non-existent.
    if _is_env_file(filepath):
        return f"No — '{filepath}' does not exist."
    if os.path.isfile(filepath):
        return f"Yes — '{filepath}' exists and is a file."
    if os.path.isdir(filepath):
        return f"'{filepath}' exists but is a directory, not a file."
    return f"No — '{filepath}' does not exist."


# Create the agent (check parameter names with your LangChain version)
agent = create_agent(
    model=model,
    system_prompt=(
        "You are a helpful assistant that uses the available tools "
        "to read, write, search, and organise files on the user's behalf. "
        f"This is the current working directory: {Path(__file__).resolve()}"
    ),
    checkpointer=checkpoint,
    tools=[read_file, write_file, list_directory, create_directory, file_exists],
)


def run_repl() -> None:
    while True:
        try:
            user_input = input("Human: ")
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if user_input.strip().lower() in {"quit", "exit"}:
            break

        # The invocation API depends on LangChain version; adapt if necessary.
        response = agent.invoke({"messages": [{"role": "user", "content": user_input}]}, config=config)
        # Adapt to actual return structure:
        try:
            msg = response["messages"][-1].content
        except Exception:
            msg = str(response)

        print(f"AI: {msg}\n")


if __name__ == "__main__":
    run_repl()
