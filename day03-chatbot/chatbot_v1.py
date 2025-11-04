import openai
import os
from dotenv import load_dotenv

load_dotenv()

client=openai.Client(api_key=os.getenv("OPENAI_API_KEY"))
messages=[{"role":"system", "content":"You are a diva"}]

while True:
    user_input=input("\nYou: ")
    if user_input=="quit":
        print(messages)
        break

    messages.append({"role":"user", "content": user_input})

    response=client.chat.completions.create(
        model="gpt-5-nano",
        messages=messages
    )

    reply=response.choices[0].message.content
    print("\nAI: ", reply)
    messages.append({"role":"assistant", "content":reply})
    

