import sys
from pathlib import Path

# Setup import paths for project modules
november_challenge = Path(__file__).parent.parent
sys.path.insert(0, str(november_challenge))
import enable_imports

from count_token import num_tokens_from_string
from refactored_chatbot import (
    setup_api,
    get_user_input,
    load_config,
    get_ai_response,
    display_response,
)


def calculate_cost(input_tokens:int , output_tokens: int, model_name:str) -> float:
    TOKEN_PRICES = {
    "gpt-5.1": {"input": 1.25, "output": 10.00},
    "gpt-5": {"input": 1.25, "output": 10.00},
    "gpt-5-chat": {"input": 1.25, "output": 10.00},
    "gpt-5.1-codex": {"input": 1.25, "output": 10.00},
    "gpt-5-codex": {"input": 1.25, "output": 10.00},
    "gpt-5-mini": {"input": 0.25, "output": 2.00},
    "gpt-5-nano": {"input": 0.05, "output": 0.40},
    "gpt-5-pro": {"input": 15.00, "output": 120.00},
    "gpt-4.1": {"input": 2.00, "output": 8.00},
    "gpt-4.1-mini": {"input": 0.40, "output": 1.60},
    "gpt-4.1-nano": {"input": 0.10, "output": 0.40},
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    }

    if model_name not in TOKEN_PRICES:
        raise ValueError(f"Unknown model: {model_name}")
    
    price_per_million= TOKEN_PRICES[model_name]["input"]
    input_cost= (input_tokens/ 1_000_000) * price_per_million

    price_per_million= TOKEN_PRICES[model_name]["output"]
    output_cost= (output_tokens/ 1_000_000) * price_per_million

    cost = input_cost + output_cost

    return cost

    # Return cost in dollars
    
def track_conversation_cost(messages) -> float: 
    running_total = 0
    input_content = ""
    output_content = ""

    for msg in messages:
        if msg["role"] in ["user", "system", "developer"]:
            input_content += " " + msg["content"]
        if msg["role"] in ["assistant"]:
            output_content += " " + msg["content"]
    input_tokens = num_tokens_from_string(input_content)
    output_tokens = num_tokens_from_string(output_content)

    running_total = calculate_cost(input_tokens, output_tokens, model)
    return running_total
    # Track running total  


if __name__ == "__main__":
    config = load_config()
    client = setup_api()

    messages=[{"role":"system", "content":"You are a diva"}]


    model = "gpt-4.1-nano"

    while True:
        user_input=get_user_input()
        if user_input=="quit":
            messages.append({"role":"user", "content": user_input})
            break
        messages.append({"role":"user", "content": user_input})

        reply= get_ai_response(client, messages, config)

        messages.append({"role":"assistant", "content":reply})

        display_response(reply)
        print(f"Cost so far : ${track_conversation_cost(messages)}")




