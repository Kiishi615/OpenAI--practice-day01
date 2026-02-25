import json
import os
import logging
import time
import functools
import traceback
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

# ---------------------------------------------------------------------------
# Logging Setup
# ---------------------------------------------------------------------------
LOG_DIR = Path("chat_logs")
LOG_DIR.mkdir(exist_ok=True)

logger = logging.getLogger("robust_agent")
logger.setLevel(logging.DEBUG)

# File handler — captures everything WARNING+ to a persistent log
file_handler = logging.FileHandler(LOG_DIR / "agent_errors.log", encoding="utf-8")
file_handler.setLevel(logging.WARNING)
file_handler.setFormatter(
    logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s")
)

# Console handler — shows WARNING+ in the terminal
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)
console_handler.setFormatter(
    logging.Formatter("%(levelname)s: %(message)s")
)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

# ---------------------------------------------------------------------------
# Retry Decorator
# ---------------------------------------------------------------------------

def retry(max_retries: int = 3, backoff_base: int = 2, fallback=None):
    """Retry a function up to *max_retries* times with exponential back-off.

    Args:
        max_retries:  Number of retry attempts after the first failure.
        backoff_base: Base for the exponential delay (seconds).
        fallback:     Optional callable(exception) → str invoked when every
                      retry is exhausted. If None, a generic error string is
                      returned.

    Usage::

        @retry(max_retries=3, fallback=lambda e: "service down")
        def my_tool(arg):
            ...
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, max_retries + 2):  # attempt 1 = original call
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    last_exception = exc
                    if attempt <= max_retries:
                        delay = backoff_base ** attempt
                        logger.warning(
                            "Tool '%s' failed (attempt %d/%d): %s — "
                            "retrying in %ds…",
                            func.__name__, attempt, max_retries + 1,
                            exc, delay,
                        )
                        time.sleep(delay)
                    else:
                        logger.error(
                            "Tool '%s' exhausted all %d attempts. "
                            "Last error: %s",
                            func.__name__, max_retries + 1, exc,
                        )

            # All retries exhausted — use fallback or generic message
            if fallback is not None:
                return fallback(last_exception)
            return (
                f"Error: tool '{func.__name__}' failed after "
                f"{max_retries + 1} attempts. Last error: {last_exception}"
            )

        return wrapper

    return decorator

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

model = init_chat_model(model='gpt-5-mini')

checkpoint = InMemorySaver()
config = {'configurable': {'thread_id': 1}}
chat_id = "953499438"
bot_token = os.getenv("TELEGRAM_API_KEY")

with open("nigerian_stocks.json", "r") as f:
    NIGERIAN_STOCKS = json.load(f)


def security_check(filepath):
    blocked_files = [".env", "secrets.json", "config.yml", f"{Path(__file__)}"]
    resolved = Path(filepath).resolve()
    if resolved.name in blocked_files:
        return "ERROR: Access to sensitive files is denied."


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@tool(
    "send_telegram_message",
    description=(
        "Sends a text message to the user's Telegram chat."
    ),
)
def send_telegram_message(content) -> str | None:
    """Send *content* to the configured Telegram chat.

    Args:
        content: The message text to send.

    Returns:
        A confirmation or error string so the agent knows what happened.
    """

    @retry(
        max_retries=3,
        fallback=lambda e: (
            "Telegram unavailable — message NOT sent. "
            f"Error: {e}"
        ),
    )
    def _send(text):
        url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
        payload = {'chat_id': chat_id, 'text': text}
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
        return "Message sent successfully!"

    return _send(content)


@tool(
    "search_the_internet",
    description=(
        "Search the internet using Tavily for current events, "
        "recent news, real-time information, or topics "
    ),
)
def search_the_internet(query) -> str | None:

    @retry(
        max_retries=3,
        fallback=lambda e: (
            "Internet search unavailable — please try again later. "
            f"Error: {e}"
        ),
    )
    def _search(q):
        tavily_client = TavilyClient()
        response = tavily_client.search(
            query=q,
            max_results=3,
            search_depth='fast',
        )
        data = ""
        for i in response['results']:
            data += "".join(i['content'])
        return data

    return _search(query)


@tool(
    "lookup_nigerian_ticker",
    description=(
        "Search for a Nigerian stock by company name or symbol. "
        "Returns the correct TradingView ticker. "
        "ALWAYS call this BEFORE search_stock_price."
    ),
)
def lookup_nigerian_ticker(search_term: str) -> str:
    """Local JSON lookup — no network needed, no retry required."""
    try:
        term = search_term.lower()
        for stock in NIGERIAN_STOCKS:
            if term in stock["name"].lower() or term in stock["description"].lower():
                return f"Ticker: {stock['ticker']}  |  Company: {stock['description']}"
        return f"No stock found matching '{search_term}'. Ask the user to clarify."
    except Exception as exc:
        logger.error("lookup_nigerian_ticker failed: %s", exc)
        return f"Error looking up ticker: {exc}"


@tool(
    "search_stock_price",
    description=(
        "Get the current price for an exact TradingView ticker (e.g. 'NSENG:UBA'). "
        "If you don't know the exact ticker, call lookup_nigerian_ticker first."
    ),
)
def search_stock_price(ticker: str) -> str:

    @retry(
        max_retries=2,
        fallback=lambda e: (
            f"Stock data for '{ticker}' temporarily unavailable. "
            f"Error: {e}"
        ),
    )
    def _fetch(t):
        cols = ["name", "description", "close", "change", "high", "low", "volume"]
        _, df = (
            Query()
            .select(*cols)
            .set_markets("nigeria")
            .set_tickers(t)
            .get_scanner_data()
        )
        if df.empty:
            return f"No data for '{t}'. Use lookup_nigerian_ticker first."
        return df.to_string(index=False)

    return _fetch(ticker)


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------
# Main Loop — resilient against unexpected errors
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logger.info("Robust agent started.")

    while True:
        try:
            user_input = input('Human: ')
            if user_input.lower() == "quit":
                print("Goodbye!")
                break

            response = agent.invoke(
                {'messages': [{'role': 'user', 'content': user_input}]},
                config=config,
            )
            print(f"AI: {response['messages'][-1].content}\n")

        except KeyboardInterrupt:
            print("\nSession interrupted. Goodbye!")
            logger.info("Session ended by KeyboardInterrupt.")
            break

        except Exception as exc:
            logger.error(
                "Unhandled error in agent loop:\n%s",
                traceback.format_exc(),
            )
            print(
                f"\n⚠️  Something went wrong: {exc}\n"
                "The error has been logged. You can keep chatting.\n"
            )