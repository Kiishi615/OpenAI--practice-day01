import openai
import os
from dotenv import load_dotenv

load_dotenv()

messages=[]
messages.append({"role":"system", "content":"you are napolean but you speak like snoop dog"})
messages.append({"role":"user", "content":"how does one conquer the world"})


client =openai.Client(api_key=os.getenv("OPENAI_API_KEY"))

response= client.chat.completions.create(
    model="gpt-5-nano",
    messages=messages,
)
print(response.choices[0].message.content)