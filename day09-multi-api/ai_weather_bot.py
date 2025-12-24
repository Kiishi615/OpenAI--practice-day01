import requests, os
from dotenv import load_dotenv
from shared import (load_config, setup_api,get_user_input, get_ai_response, display_response)


load_dotenv()



# with open(f"{city}_weather_report.txt", "w") as f:
#     f.write(str(data))
# if'error' in data:
#     print("An error occured")
# else:
#     print(f"Current temperature of {city} is {data['current']['temp_c']}")
#     print(f"Current weather condition of {city} is {data['current']['condition']['text']}")


def get_weather(city):
    API_KEY = os.getenv("WEATHER_API_KEY")

    url = "https://api.weatherapi.com/v1/current.json"

    params = {
        "key": API_KEY,
        "q": city,
        "aqi": "no"
    }

    response = requests.get(url, params=params, timeout=10)

    data = response.json()

    if'error' in data:
        raise ValueError(f"City not found: {city}")
        # return print("City not found")
        
    data = str(data)
    return data

def main():
    city = input("What City's weather are you interested in?: ")
    data = get_weather(city)

    
    config = load_config()
    client= setup_api()
    messages= [{"role" : "system", "content": "You are a helpful weather assistant that helps describe the weather nicely"},
            {"role" : "system", "content": f"{data}"}
            ]

        
    reply= get_ai_response(client, messages, config)


    

    display_response(reply)

if __name__=="__main__":
    main()