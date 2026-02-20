import numexpr
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

model = init_chat_model(model='gpt-5.2')

config = {'configurable' : {'thread_id' : 1}}
checkpointer = InMemorySaver()


@tool('calculator', description=(
    "Evaluate a mathematical expression using numexpr syntax. "
    "Supports: +, -, *, /, **, % and "
    "functions: sqrt, abs, sin, cos, tan, log, log10, exp. "
    "Examples: '10**2', 'sqrt(400)', 'sin(3.14159)', 'log10(1000)'"
))
def calculator(expression: str):
    try:
        result = numexpr.evaluate(expression).item()
        return str(result)
    except Exception as e:
        print(f"Error: not allowed {e}")



@tool('temperature_converter', description=(
        "Converts temperature from 'Fahrenheit' to 'Celsius' and vice versa"
        "curr_unit must be exactly 'fahrenheit' or 'celsius' (lowercase, full word)."))
def temp_converter(curr_unit: str, temp: float)-> float:
    curr_unit = curr_unit.lower()
    if curr_unit == "fahrenheit":
        temperature = (temp-32) * 5/9
    if curr_unit == "celsius":
        temperature = (temp* 9/5) + 32
    return temperature



@tool('distance_converter', description="Converts distance from 'Kilometer' to 'Miles' and vice versa")
def distance_converter(curr_unit: str, distance: float)-> float:
    curr_unit = curr_unit.lower()
    if curr_unit == "kilometer":
        converted_distance = distance *0.621371
    if curr_unit == "miles":
        converted_distance = distance / 0.621371
    return converted_distance


@tool('weight_converter', description="Converts distance from 'Kilograms' to 'Pounds' and vice versa")
def weight_converter(curr_unit: str, weight: float)-> float:
    curr_unit = curr_unit.lower()
    if curr_unit == "kilogram":
        converted_weight = weight *2.20462
    if curr_unit == "pounds":
        converted_weight = weight /2.20462
    return converted_weight 

agent = create_agent(
    model= model,
    tools= [calculator, distance_converter, temp_converter],
    system_prompt=(
    "You are a helpful math and conversion assistant.\n\n"
    "You have the following tools:\n"
    "- **calculator**: For math expressions using numexpr syntax. "
    "Use ** for exponents, sqrt() for square roots, "
    "sin/cos/tan for trig, log for natural log, log10 for base-10 log.\n"
    "- **temperature_converter**: For converting between Fahrenheit and Celsius.\n"
    "- **distance_converter**: For converting between Kilometers and Miles.\n\n"
    "Always use the appropriate tool — never calculate or convert in your head."
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