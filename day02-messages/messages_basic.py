import openai
import os
from dotenv import load_dotenv

load_dotenv()

messages = []
messages.append({"role":"system", "content": "You are helpful"})
messages.append({"role":"user", "content": "My name is Mort"})

print("message count:", len(messages))
print("first message :", messages[0])
print("second message :", messages[1])

client =openai.Client(api_key=os.getenv("OPENAI_API_KEY"))
response=client.chat.completions.create(
    model="gpt-5-nano",
    messages=messages

)

print(response.choices[0].message.content)