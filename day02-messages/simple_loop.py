import openai
import os
from dotenv import load_dotenv

load_dotenv()
messages =[]
client=openai.Client(api_key=os.getenv("OPENAI_API_KEY"))


while True:
    user_input = input("You: ")
    
    if user_input=="quit":
        print("Goodbye!")
        break
    
    messages.append({"role":"user","content":user_input})

    #Model definition
    response=client.chat.completions.create(
        model="gpt-5-nano",
        messages= messages
    )
 
    

    reply= response.choices[0].message.content
    print("\n AI:", reply)

    messages.append({"role":"assistant","content":reply})




