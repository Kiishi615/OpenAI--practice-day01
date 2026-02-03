import requests
import openai
from newsapi.newsapi_client import NewsApiClient 
from dotenv import load_dotenv
load_dotenv()

r = requests.get('https://www.python.org')

# Init
newsapi = NewsApiClient(api_key='0545393d67ba4a48a39b79634c44c897')
z = input("""
        AI: What do you want to know about? One keyword only e.g Trump
        Human: """)
# /v2/top-headlines
top_headlines = newsapi.get_top_headlines(q=f"{z}",
                                            
                                            language='en',
                                            )

# print (top_headlines["articles"])
news = []
for i in range (len(top_headlines["articles"])):

    news.append(top_headlines["articles"][i]["content"])





messages = [
            {"role": "system", "content": f"""
                You are a news monitor. Match the news to my provided context {news}. If nothing similar exists, your only response is: 'I don't know.'
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

