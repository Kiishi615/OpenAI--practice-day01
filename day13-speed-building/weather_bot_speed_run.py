import requests, os, openai
from dotenv import load_dotenv
load_dotenv()

url = "https://api.weatherapi.com/v1/current.json"
API_KEY = os.getenv("WEATHER_API_KEY")

params = {
    "key" : API_KEY,
    "q" : input("""AI: Enter a Place
Human:  """ ),
    "aqi" : "no"
}

response = requests.get(url, params=params, timeout=10)

data = response.json()

current_weather_data= data["current"]

current_weather_data = str(current_weather_data)

messages = [
            {"role": "system", "content": f"""
            You are a weather monitor. 
            Answer based on the weather data I provided {current_weather_data}.
            Make the weather clear
            If nothing similar exists, your only response is: 'I don't know.'
                                            """
            }]

while True:
    
    user_input = input("\nHuman: ").strip()
    if user_input.lower() == "stop":
        break
    else:
        messages.append({"role": "user", "content": user_input })

        response = openai.chat.completions.create(
            model = "gpt-5-nano",
            messages= messages
        )
        messages.append({"role": "assistant", "content": f"{response.choices[0].message.content}" })

    print(f"\nAI: {response.choices[0].message.content}")


