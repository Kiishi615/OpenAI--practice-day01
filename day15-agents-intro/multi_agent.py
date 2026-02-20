from basic_agent import calculate_age, reverse_string
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
# from langchain.tools import tool
from langchain_community.retrievers import WikipediaRetriever
from langchain_community.tools import DuckDuckGoSearchResults
from langgraph.checkpoint.memory import InMemorySaver
from math_agent import (calculator, distance_converter, temp_converter,
                        weight_converter)
# from rich import inspect
from search_agent import search_web, search_wiki

load_dotenv()

model = init_chat_model("claude-haiku-4-5")

config = {'configurable' : {'thread_id' : 1}}
checkpointer = InMemorySaver()


agent = create_agent(
    model= model,
    tools= [calculator, distance_converter, temp_converter, weight_converter, search_web, search_wiki, reverse_string, calculate_age],
    system_prompt=(
        "You are a helpful all-purpose assistant with access to the following tools:\n\n"
        
        "**Math:**\n"
        "- **calculator**: Evaluate math expressions using numexpr syntax. "
        "Use ** for exponents, sqrt() for square roots, "
        "sin/cos/tan for trig, log for natural log, log10 for base-10 log.\n\n"
        
        "**Conversions:**\n"
        "- **temperature_converter**: Convert between Fahrenheit and Celsius.\n"
        "- **distance_converter**: Convert between Kilometers and Miles.\n"
        "- **weight_converter**: Convert between Kilograms and Pounds.\n\n"
        
        "**Research:**\n"
        "- **search_web**: Search DuckDuckGo for current events, recent news, and real-time information.\n"
        "- **search_wiki**: Search Wikipedia for established facts, history, science, and biographies.\n\n"
        
        "**Utilities:**\n"
        "- **calculate_age**: Calculate someone's age from their birth year.\n"
        "- **reverse_string**: Reverse any string.\n\n"
        
        "Always use the appropriate tool — never calculate, convert, or guess in your head. "
        "If using research tools, cite which source you used. "
        "After using a tool, explain the result clearly to the user."
    ),
    checkpointer= checkpointer
)

while True:
    user_input =input('Human: ')
    if user_input.lower() in ("quit", "exit"):
        print("AI: Goodbye")
        break
    try:
        response =agent.invoke(
            {
            'messages' : [{'role': 'user', 'content': user_input}]
            },
            config= config

        )
        print(f"AI: {response['messages'][-1].content}\n")
        
    except Exception as e:
        print(f"Something went wrong: {e}")
        print("Try again.\n")
        # inspect(response, help=True)

