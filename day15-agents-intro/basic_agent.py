from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from rich import inspect

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

agent = create_agent(
    model= llm,
    tools= [calculate_age, reverse_string]
)
if __name__ == "__main__":
    while True:
        user_input = input("Human: ")
        if user_input.lower() in ("quit", "exit"):
            print("AI: Goodbye")
            break
        try:
            response = agent.invoke({
                'messages':[
                    {"role": "user", "content": user_input}
                ]
            })
            print(f"AI: {response['messages'][-1].content}\n")
        except Exception as e:
            print(f"Something went wrong: {e}")
            print("Try again.\n")

