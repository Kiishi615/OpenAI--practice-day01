import requests, os
from dotenv import load_dotenv

load_dotenv()

def get_news(topic):
    API_KEY = os.getenv("NEWS_API_KEY")

    url = ('https://newsapi.org/v2/top-headlines?'
            # 'sources=bbc-news&'
            f"q={topic}&"
            f'apiKey={API_KEY}')


    response = requests.get(url)
    data = response.json()

    if data["totalResults"] == 0:
        print("Nothing here folks")

    else:
        for i in data["articles"]:
            print(f"\n{i["title"]}")
