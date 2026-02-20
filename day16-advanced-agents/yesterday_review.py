from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from rich import inspect

load_dotenv()

model = init_chat_model(model='gpt-5-mini')

checkpoint = InMemorySaver()
config = {'configurable' : {'thread_id' : 1}}

@tool('calculate_age', description="Calculate age")
def calculate_age(year: int):
    return 2026- year

agent = create_agent(
    model= model,
    system_prompt= 'You are helpful assistant that uses the tools available to you',
    checkpointer=checkpoint,
    tools= [calculate_age]
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

        # inspect(response, help= True)


        print(f"AI: {response['messages'][-1].content}\n")