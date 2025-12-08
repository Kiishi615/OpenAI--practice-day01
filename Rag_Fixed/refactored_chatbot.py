import openai
import os, sys
from dotenv import load_dotenv
import json
from pathlib import Path


def load_config():
        current_dir = Path(__file__).parent
        config_path = current_dir / 'config.json'
        

        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
        except FileNotFoundError:
            print("WARNING: 'config.json' not found. Using an empty config.")
            config = {} # Use an empty dict as a safe fallback
        except json.JSONDecodeError:
            print("WARNING: 'config.json' is corrupted. Using an empty config.")
            config = {} # Also a safe fallback
        return config
def setup_api():
    load_dotenv()
    try:
        api_key=os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("API key missing")
        client=openai.Client(api_key=api_key)
        

    except Exception as e:
        print(f"some error:{e}")
        client= None

    return client
def get_user_input():
    return input("\nYou: ").strip()

def get_user_file():
    return input("\nWhat file do you want: ").strip()

def save_chat_log(messages, filename):
    with open(f"{filename}_processed.txt","w")as f:
        for msg in messages:
            f.write(f"{msg['role']}: {msg['content']}\n")
            f.write("-" * 50 + "\n")


def get_ai_response(client, messages, config):
    
    response=client.chat.completions.create(
        **config,
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
            save_chat_log(messages, filename='words')
            break
        messages.append({"role":"user", "content": user_input})
        
        reply= get_ai_response(client, messages, config)

        messages.append({"role":"assistant", "content":reply})
        

        display_response(reply)
        
if __name__=="__main__":
    config=load_config()

    main()





