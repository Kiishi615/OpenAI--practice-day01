import openai
import os, sys
from dotenv import load_dotenv

load_dotenv()

try:
    api_key=os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("API key missing")
    

    client=openai.Client(api_key=api_key)

except Exception as e:
    print(f"some error:{e}")
    client= None
    sys.exit(1)


messages=[{"role":"system", "content":"You are a diva"}]

while True:
    user_input=input("\nYou: ")
    if user_input=="quit":
        with open("chat_log.txt","w")as f:
            f.write(str(messages))
        break

    messages.append({"role":"user", "content": user_input})

    response=client.chat.completions.create(
        model="gpt-5-nano",
        messages=messages
    )

    reply=response.choices[0].message.content
    print("\nAI: ", reply)
    messages.append({"role":"assistant", "content":reply})
    

