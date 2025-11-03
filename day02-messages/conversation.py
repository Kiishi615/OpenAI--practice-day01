import openai
import os
from dotenv import load_dotenv

load_dotenv()


messages=[]

messages.append({"role":"user","content":"What is 2+2"})
messages.append({"role":"assistant","content":"4"})
messages.append({"role":"user","content":"What is 3+3"})



client=openai.Client(api_key=os.getenv("OPENAI_API_KEY"))

response=client.chat.completions.create(
    model="gpt-5-nano",
    messages= messages
)

print(response.choices[0].message.content)