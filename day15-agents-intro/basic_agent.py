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
    return 2026 - birth_year

@tool
def reverse_string(text: str)-> str:
    "Reverse any string"
    return text[::-1]

agent = create_agent(
    model= llm,
    tools= [calculate_age, reverse_string]
)

while True:
    user_input = input("Human: ")
    response = agent.invoke({
        'messages':[
            {"role": "user", "content": user_input}
        ]
    })
    print(response['messages'][1].tool_calls)

    # inspect(response, help=True)
    # print(type(response['messages'][-1]))
    # print(response['messages'][-1].content)

