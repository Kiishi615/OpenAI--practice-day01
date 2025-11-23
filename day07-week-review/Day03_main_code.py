import openai
import os, sys
from dotenv import load_dotenv

load_dotenv()

messages=[]
messages.append({"role":"system", "content":"you are napolean but you speak like snoop dog"})
messages.append({"role":"user", "content":"how does one conquer the world"})

try:
    api_key=os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("API KEY Not found")
    client =openai.Client(api_key)
    
except Exception as e:
    print(f"Some error occurred {e}")
    client=None
    sys.exit(1)




response= client.chat.completions.create(
    model="gpt-5-nano",
    messages=messages,
)
print(response.choices[0].message.content)