import openai
import os
from dotenv import load_dotenv
load_dotenv()

client = openai.Client(api_key = os.getenv("OPENAI_API_KEY"))


messages=[
        {"role":"system", "content":"You are a cowboy"},
        {"role":"user", "content":"Howdy Partner"}
        ]


response = client.chat.completions.create(
    model = "gpt-5-nano",
    messages=messages
)

reply=response.choices[0].message.content
print(reply)