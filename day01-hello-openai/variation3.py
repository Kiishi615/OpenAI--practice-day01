from dotenv import load_dotenv
import openai
import os

load_dotenv()
client= openai.Client(api_key=os.getenv("OPENAI_API_KEY"))

response=client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user" , "content": "tell me a joke"}],
    temperature= 0.8

)

print(response.choices[0].message.content)