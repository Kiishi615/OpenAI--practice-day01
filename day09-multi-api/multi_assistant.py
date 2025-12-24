from ai_weather_bot import get_weather
from news_api import get_news

from shared import (load_config, setup_api,
                    get_user_input, get_ai_response,
                    display_response)


config=load_config()
client= setup_api()

messages=[{"role":"system", "content":"You are a helpful assistant"}]


while True:
    temp_messages=[{"role":"system", 
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
    """}]
    
    user_input=get_user_input()
    if user_input=="quit":
        break
    temp_messages.append({"role":"user", "content": user_input})
    messages.append({"role":"user", "content": user_input})

    action= get_ai_response(client, temp_messages, config)

    if action == "weather":
        city = input("What City's weather are you interested in?: ")
        data = get_weather(city)

        messages= [{"role" : "system", "content": "You are a helpful weather assistant that helps describe the weather nicely"},
                {"role" : "system", "content": f"{data}"}
                ]

            
        reply= get_ai_response(client, messages, config)


        

        display_response(reply)

    if action == "news":
        get_news()

    if action == "chat":
        reply= get_ai_response(client, messages, config)

        messages.append({"role":"assistant", "content":reply})
        

        display_response(reply)




