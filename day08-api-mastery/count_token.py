import os, sys
from dotenv import load_dotenv
import openai, tiktoken
from pathlib import Path


november_challenge = Path(__file__).parent.parent
sys.path.insert(0, str(november_challenge))

import enable_imports

from refactored_chatbot import  (load_config, setup_api, get_user_input, 
                                get_user_file, save_chat_log,
                                get_ai_response,  display_response)
from dotenv import load_dotenv


# config = load_config()
# client = setup_api()

def num_tokens_from_string(string:str) -> int:
    encoding = tiktoken.encoding_for_model("gpt-5-nano")
    num_tokens = len(encoding.encode(string))
    return num_tokens

def cost_estimate(model_name: str, tokens:int)-> float:
    """
    For the model you provide it tells you the cost of the tokens you input.
    
    """
    
    OPENAI_INPUT_PRICES = {
    "gpt-5.1": 1.25,
    "gpt-5": 1.25,
    "gpt-5-chat": 1.25,
    "gpt-5.1-codex": 1.25,
    "gpt-5-codex": 1.25,
    "gpt-5-mini": 0.25,
    "gpt-5-nano": 0.05,
    "gpt-5-pro": 15.00,
    "gpt-4.1": 2.00,
    "gpt-4.1-mini": 0.40,
    "gpt-4.1-nano": 0.10,
    "gpt-4o": 2.50,
    "gpt-4o-mini": 0.15,
}
    
    if model_name not in OPENAI_INPUT_PRICES:
        raise ValueError(f"Unknown model: {model_name}")
    
    price_per_million= OPENAI_INPUT_PRICES[model_name]
    cost= (tokens/ 1_000_000) * price_per_million

    return cost

def check_token_limit(model_name: str, input_tokens: int) -> bool:
    """
    Returns True if within limit, False if over.
    Raises error if model is unknown.
    """

    MAX_CONTEXT_WINDOW = {
    "gpt-5": 400_000,
    "gpt-5.1": 400_000,
    "gpt-5-mini": 400_000,
    "gpt-5-nano": 400_000,
    "gpt-5-pro": 400_000,
    "gpt-4.1": 1_000_000,
    "gpt-4.1-mini": 1_000_000,
    "gpt-4.1-nano": 1_000_000,
    "gpt-4o": 128_000,          
    "gpt-4o-mini": 128_000,
    }

    if model_name not in MAX_CONTEXT_WINDOW:
        raise ValueError(f"Unknown model: {model_name}")

    max_limit = MAX_CONTEXT_WINDOW[model_name]
    return input_tokens <= max_limit

def assert_token_limit(model_name: str, input_tokens: int):
    """
    """
    MAX_CONTEXT_WINDOW = {
    "gpt-5": 400_000,
    "gpt-5.1": 400_000,
    "gpt-5-mini": 400_000,
    "gpt-5-nano": 400_000,
    "gpt-5-pro": 400_000,
    "gpt-4.1": 1_000_000,
    "gpt-4.1-mini": 1_000_000,
    "gpt-4.1-nano": 1_000_000,
    "gpt-4o": 128_000,          
    "gpt-4o-mini": 128_000,
    }

    if not check_token_limit(model_name, input_tokens):
        max_limit = MAX_CONTEXT_WINDOW[model_name]
        raise ValueError(
            f"Token limit exceeded: {input_tokens} > {max_limit} "
            f"for model '{model_name}'."
        )


if __name__ == "__main__":
    user_input = get_user_input()


    num_tokens = num_tokens_from_string(user_input)
    print(f"\n After encoding, it's {num_tokens} tokens")

    preffered_model = get_user_input()


    cost = cost_estimate(preffered_model, num_tokens)

    assert_token_limit(preffered_model, num_tokens)
    print(cost)



