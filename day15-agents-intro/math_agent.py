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
        return f"Error evaluating expression '{expression}': {e}"



@tool('temperature_converter', description=(
        "Converts temperature from 'Fahrenheit' to 'Celsius' and vice versa"
        "curr_unit must be exactly 'fahrenheit' or 'celsius' (lowercase, full word)."))
def temp_converter(curr_unit: str, temp: float)-> float:
    try:
        curr_unit = curr_unit.lower()
        if curr_unit == "fahrenheit":
            return (temp-32) * 5/9
        elif curr_unit == "celsius":
            return (temp* 9/5) + 32
        else:
            return f"Error: curr_unit must be 'fahrenheit' or 'celsius', got '{curr_unit}'"
    except Exception as e:
        return f"Error converting temperature: {e}"



@tool('distance_converter', description=("Converts distance from 'Kilometer' to 'Miles' and vice versa"
        "curr_unit must be exactly 'kilometer' or 'miles' (lowercase, full word)."))
                                        
def distance_converter(curr_unit: str, distance: float)-> float:
    try:
        curr_unit = curr_unit.lower()
        if curr_unit == "kilometer":
            return distance * 0.621371
        elif curr_unit == "miles":
            return distance / 0.621371
        else:
            return f"Error: curr_unit must be 'kilometer' or 'miles', got '{curr_unit}'"
    except Exception as e:
        return f"Error converting distance: {e}"


@tool('weight_converter', description=("Converts distance from 'Kilograms' to 'Pounds' and vice versa"
        "curr_unit must be exactly 'kilograms' or 'pounds' (lowercase, full word)."))
                                    
def weight_converter(curr_unit: str, weight: float)-> float:
    try:
        curr_unit = curr_unit.lower()
        if curr_unit == "kilograms":
            return weight * 2.20462
        elif curr_unit == "pounds":
            return weight / 2.20462
        else:
            return f"Error: curr_unit must be 'kilograms' or 'pounds', got '{curr_unit}'"
    except Exception as e:
        return f"Error converting weight: {e}" 

agent = create_agent(
    model= model,
    tools= [calculator, distance_converter, temp_converter, weight_converter],
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

if __name__ == "__main__":
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