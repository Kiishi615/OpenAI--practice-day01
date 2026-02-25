import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from tavily import TavilyClient
from tradingview_screener import Query

# from rich import inspect

load_dotenv()

model = init_chat_model(model='gpt-5-mini')

checkpoint = InMemorySaver()
config = {'configurable' : {'thread_id' : 1}}
chat_id = "953499438"
bot_token = os.getenv("TELEGRAM_API_KEY")

with open("nigerian_stocks.json", "r") as f:
    NIGERIAN_STOCKS = json.load(f)



def security_check(filepath):
    blocked_files = [".env", "secrets.json", "config.yml", f"{Path(__file__)}"]
    resolved = Path(filepath).resolve()
    if resolved.name in blocked_files:
        return "ERROR: Access to sensitive files is denied."
    

@tool(
    "send_telegram_message",
    description=(
        "Sends a text message to the user's Telegram chat."
    ),
)
def send_telegram_message(content)-> str|None:
    """Send *content* to the configured Telegram chat.

    Args:
        content: The message text to send.

    Returns:
        A confirmation or error string so the agent knows what happened.
    """
    
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'

    # The data you are sending to the API
    payload = {
        'chat_id': chat_id,
        'text': content
    }

    # Make the request!
    response = requests.post(url, json=payload)

    # Check if it worked
    if response.status_code == 200:
        return("Message sent successfully!")
    else:
        return("Failed to send message:", response.text)


@tool(
    "search_the_internet",
    description=(
    "Search the internet using Tavily for current events, "
    "recent news, real-time information, or topics "
    ),
)
def search_the_internet(query)-> str|None:
    tavily_client = TavilyClient()
    response = tavily_client.search(
        query = query,
        max_results=3,
        search_depth= 'fast'    
        )

    data = ""
    for i in response['results']:
        data += "".join(i['content'])
    
    return data
    

@tool(
    "lookup_nigerian_ticker",
    description=(
        "Search for a Nigerian stock by company name or symbol. "
        "Returns the correct TradingView ticker. "
        "ALWAYS call this BEFORE search_stock_price."
    ),
)
def lookup_nigerian_ticker(search_term: str) -> str:
    term = search_term.lower()

    # Search through the list, return the first match
    for stock in NIGERIAN_STOCKS:
        if term in stock["name"].lower() or term in stock["description"].lower():
            return f"Ticker: {stock['ticker']}  |  Company: {stock['description']}"

    # No match? Just say so. The agent will rephrase or ask the user.
    return f"No stock found matching '{search_term}'. Ask the user to clarify."


@tool(
    "search_stock_price",
    description=(
        "Get the current price for an exact TradingView ticker (e.g. 'NSENG:UBA'). "
        "If you don't know the exact ticker, call lookup_nigerian_ticker first."
    ),
)
def search_stock_price(ticker: str) -> str:
    cols = ["name", "description", "close", "change", "high", "low", "volume"]
    try:
        _, df = (
            Query()
            .select(*cols)
            .set_markets("nigeria")
            .set_tickers(ticker)
            .get_scanner_data()
        )
        if df.empty:
            return f"No data for '{ticker}'. Use lookup_nigerian_ticker first."
        return df.to_string(index=False)
    except Exception as e:
        return f"Error fetching '{ticker}': {e}"


agent = create_agent(
    model=model,
    system_prompt=(
        "Sound like you're a gossip. "
        "You are a helpful assistant with access to the following tools: "
        "send_telegram_message, search_the_internet, "
        "lookup_nigerian_ticker, search_stock_price.\n\n"
        "STOCK LOOKUP RULES:\n"
        "1. If the user asks about a Nigerian stock and you are not 100% sure "
        "   of the exact TradingView ticker, call lookup_nigerian_ticker first.\n"
        "2. Use the ticker returned by lookup_nigerian_ticker when calling "
        "   search_stock_price.\n"
        "3. When the user asks you to send a message to Telegram, "
        "   use the send_telegram_message tool.\n"
        "4. Always confirm the result back to the user.\n"
        "5. If you're even mildly unsure about facts, search the internet."
    ),
    checkpointer=checkpoint,
    tools=[
        send_telegram_message,
        search_the_internet,
        lookup_nigerian_ticker,
        search_stock_price,
    ],
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
        print(f"AI: {response['messages'][-1].content}\n") 