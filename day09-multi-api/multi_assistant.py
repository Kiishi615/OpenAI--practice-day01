import logging, sys
from ai_weather_bot import get_weather
from news_api import get_news
from shared import (setup_logging, load_config, setup_api,
                    get_user_input, response_with_retry,
                    display_response)
from pathlib import Path

log_file = setup_logging()
logger = logging.getLogger(__name__)
logger.info("="*60)
logger.info(f"{Path(sys.argv[0]).stem} STARTED")
logger.info(f"Logging to : {log_file}")
logger.info("="*60)





try:
    config=load_config()
    client= setup_api()
    logger.info("Configuration loaded and API initialized")
except Exception as e:
    logger.critical(f"Failed to initialize: {e} ")
    sys.exit(1)


def classify_intent(client, user_input, config):
    """
    classifies user intent into weather, news or chat
    """
    logger.debug(f"Classifying intent for: {user_input}")
    classification_prompt=[{"role":"system", 
        "content": """
        "You are an intent classification engine. Your only job is to route user inputs to the correct API.

    Analyze the user's message and output exactly one of the following three labels:
    
    1. 'weather'
    - TRIGGER: Requests for current temperature, conditions, or future forecasts.
    - EXCLUDE: Historical weather events (e.g., "Did it snow in 1990?") or metaphors.
    
    2. 'news'
    - TRIGGER: Requests for current events, politics, sports, finance, or specific past events (including disasters like hurricanes or floods).
    - PRIORITY: If a query involves a weather event that caused damage or is a major news story (e.g., "hurricane damage report"), classify as 'news'.

    3. 'chat'
    - TRIGGER: Greetings, philosophical questions, personal statements, jokes, or metaphors (e.g., "political climate").
    - NOTE: If the user expresses a feeling about the weather but doesn't ask for data (e.g., "I hope it rains"), classify as 'chat'.

    CRITICAL INSTRUCTION: Reply with the single label only. Do not add punctuation or explanation.
    """},
    {"role": "user", "content": user_input}
    ]

    reply= response_with_retry(client, classification_prompt, config)
    intent= reply.strip().lower()
    logger.info(f"Intent classified as : {intent}")
    return intent

def location_extractor(client, user_input, config):
    """Extract Location from user_input for weather"""
    logger.debug(f"Extracting Location for: {user_input}")

    extraction_prompt = [{
        "role": "system",
        "content": "Extract the location from this weather query. If no location mentioned, reply with 'none'. Reply with just the location name."
    },
        {"role": "user", "content": user_input}
    ]

    reply= response_with_retry(client, extraction_prompt, config)
    location = reply.strip()
    logger.info(f"Extracted location: {location}")
    return reply

def extract_topic(client, user_input, config):
    logger.debug(f"Extracting the topic for: {user_input}")

    """Extract news topic from query"""
    extraction_prompt = [{
        "role": "system",
        "content": "Extract the news topic from this query. If general news, reply 'general'. Reply with just the topic."
    }, {
        "role": "user",
        "content": user_input
    }]
    
    topic = response_with_retry(client, extraction_prompt, config).strip()
    logger.info(f"Extracted topic: {topic}")
    return topic

messages=[{"role":"system", "content":"You are a helpful assistant"}]
query_count = 0

logger.info("Ready for user input")

while True:
    try:
        user_input=get_user_input()
        query_count += 1
        logger.info(f"Query #{query_count}: {user_input}")

        if user_input.lower()=="quit":
            logger.info("User requested quit")
            break
        messages.append({"role":"user", "content": user_input})

        action= classify_intent(client, user_input, config)

        if action == "weather":
            logger.info("Processing weather request")
            location = location_extractor(client, user_input, config)
            if location.lower() == "none":
                location = input("What city's weather are you interested in? ")
                logger.info(f"User inputed location: {location}")
            logger.info(f"fetching weather for: {location}")
            weather_data = get_weather(location)

            weather_prompt = messages +[{"role" : "system", "content": f"weather data for {location}: {weather_data}. Describe the weather nicely"}
            ]

            reply= response_with_retry(client, weather_prompt, config)
            messages.append({"role": "assistant", "content": reply})
            display_response(reply)
            logger.info("Weather response delivered")

        elif action == "news":
            logger.info("Processing news request")
            topic = extract_topic(client, user_input, config)
            get_news(topic)

        else:
            logger.info("Processing chat request")
            reply= response_with_retry(client, messages, config)
            messages.append({"role":"assistant", "content":reply})
            display_response(reply)
            logger.info("Chat response delivered")

    except KeyboardInterrupt:
        logger.warning("Interrupted by user (Ctrl+C)")
        break
    except Exception as e:
        logger.error(f"Error in the main loop: {e}", exc_info=True)
        print(f"Sorry, an error occured: {e}")

logger.info(f"Session Ended. Total queries: {query_count}")
logger.info("="*60)



