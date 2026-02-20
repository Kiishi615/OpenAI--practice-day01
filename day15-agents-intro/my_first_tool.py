from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool

load_dotenv()

llm = init_chat_model(model= "gpt-4o-mini")

@tool
def calculate_age(birth_year:int) -> int:
    "Calculate age from the birth year"
    try:
        return 2026 - birth_year
    except Exception as e:
        return f"Error calculating age: {e}"

@tool
def reverse_string(text: str)-> str:
    "Reverse any string"
    try:
        return text[::-1]
    except Exception as e:
        return f"Error reversing string: {e}"


