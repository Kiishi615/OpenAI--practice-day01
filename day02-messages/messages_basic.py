import openai
import os
from dotenv import load_dotenv

load_dotenv()

messages = []
messages.append({"role":"system", "content": "You are helpful"})
messages.append({"role":"system", "content": "Hi there"})

print("message count:", len(messages))
print("first message :", messages[0])
print("second message :", messages[1])

