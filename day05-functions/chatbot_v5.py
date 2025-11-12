import openai
import os, sys
from dotenv import load_dotenv



def setup_api():
    load_dotenv()
    try:
        api_key=api_key=os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("API key missing")
        client=openai.Client(api_key=api_key)
        return client

    except Exception as e:
        print(f"some error:{e}")
        client= None
        sys.exit(1)

def get_user_input():
    return input("\nYou: ")

def save_chat_log():
    with open("chat_log.txt","w")as f:
        f.write(str(messages))
            
def get_ai_response(client, messages):
    response=client.chat.completions.create(
        model="gpt-5-nano",
        messages=messages
    )

    reply=response.choices[0].message.content
    return reply

def display_response(reply):
    print("\nAI: ", reply)


def main():
    client= setup_api()
    messages=[{"role":"system", "content":"You are a diva"}]

    
    while True:
        user_input=get_user_input()
        if user_input=="quit":
            messages.append({"role":"user", "content": user_input})
            break
        messages.append({"role":"user", "content": user_input})
        
        reply= get_ai_response(client, messages)

        messages.append({"role":"assistant", "content":reply})

        display_response(reply)
        
main()





