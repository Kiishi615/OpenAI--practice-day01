import sys, os
from pathlib import Path
import time
import asyncio
from openai import AsyncOpenAI, RateLimitError
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(funcName)s - %(message)s'
)
# File handler
file_handler = logging.FileHandler('app.log', mode='a')
file_handler.setFormatter(formatter)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)


# Setup import paths for project modules
november_challenge = Path(__file__).parent.parent
sys.path.insert(0, str(november_challenge))
import enable_imports


from refactored_chatbot import  (load_config, setup_api)

from openai import RateLimitError, APIConnectionError
def call_with_retry():
    logging.info("Application started")
    for attempt in range(5):
        try:
            client = setup_api()
            logger.info("client initialised successfully")
            return client
        except (RateLimitError, APIConnectionError) as e:
            logger.warning(f"You're hitting rate limits: {e}")
            wait = 2 ** attempt
            logger.warning(f"Attempt {attempt} failed. Waiting {wait}s...")
            time.sleep(wait)
        
        except Exception as e:
            logger.error(f"Some error : {e} happened")
    logger.error("All retry attempts exhausted")
    return None

def response_with_retry(client, messages, config):
    for attempt in range(5):
        try:
            response=client.chat.completions.create(
                **config,
                messages=messages
            )

            reply=response.choices[0].message.content
            return reply
        except (RateLimitError, APIConnectionError) as e:
            logger.warning(f"You're hitting rate limits: {e}")
            wait = 2 ** attempt
            logger.warning(f"Attempt {attempt} failed. Waiting {wait}s...")
            time.sleep(wait)
    
        except Exception as e:
            logger.error(f"Some error : {e} happened")
            return None
def spam_api():
    client = setup_api()
    config = load_config()
    
    for i in range(1000):
        print(f"Request {i}")
        messages = [{"role": "user", "content": "I'm gonna ragebait you so hard"}]  # Simple, fixed message
        
        # Use your retry function here
        reply = response_with_retry(client, messages, config)



def setup_async_api():
    load_dotenv()
    config = load_config()
    # Assuming your load_config returns a dict with api_key, or you set it via env vars
    # You might need to adjust how you get the key depending on your config structure
    return AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY")) 

async def single_request(client, index):
    """Sends one request but doesn't wait for others to finish."""
    try:
        print(f"Firing request {index}...")
        
        # We use 'await' here, which lets Python switch to sending other requests 
        # while this one is travelling across the internet.
        response = await client.chat.completions.create(
            model="gpt-4.1-nano", # Use a cheap model for testing!
            messages=[{"role": "user", "content": "Say hi."}],
            max_tokens=5
        )
        print(f"Request {index} Success!")
        
    except RateLimitError:
        print(f"!!! RATE LIMIT HIT on Request {index} !!!")
    except Exception as e:
        print(f"Request {index} failed with: {e}")

async def spam_api_concurrently():
    client = setup_async_api()
    
    number_of_requests = 451 
    
    tasks = []
    for i in range(number_of_requests):
        tasks.append(single_request(client, i))

    print(f"Starting {number_of_requests} simultaneous requests...")
    
    # 3. asyncio.gather launches them all at roughly the same time
    await asyncio.gather(*tasks)
    
    await client.close()
if __name__ == "__main__":
    client = call_with_retry()
    response_with_retry(client, messages, config)