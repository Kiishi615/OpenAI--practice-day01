import requests, os
from dotenv import load_dotenv

load_dotenv()


API_KEY = os.getenv("WEATHER_API_KEY")
city = input("What City's weather do you wanna find out about:  ")

url = "https://api.weatherapi.com/v1/current.json"

params = {
    "key": API_KEY,
    "q": city,
    "aqi": "no"
}

response = requests.get(url, params=params, timeout=10)
data = response.json()

# with open(f"{city}_weather_report.txt", "w") as f:
#     f.write(str(data))
if data['error']:
    print("An error occured")
else:
    print(f"Current temperature of {city} is {data['current']['temp_c']}")
    print(f"Current weather condition of {city} is {data['current']['condition']['text']}")

