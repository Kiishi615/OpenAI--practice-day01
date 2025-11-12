import openai
import os, sys
from dotenv import load_dotenv
import glob

from refactored_chatbot import *
from file_functions import read_text_file, save_text_file

def main():
    filename=get_user_file()
    client = setup_api()
    messages=[]
    while True:
        user_input =get_user_input()
        user_text=read_text_file(filename)
        if user_input=="quit":
            reply= get_ai_response(client, messages)

            messages.append({"role":"assistant", "content":reply})
            save_chat_log(messages, filename)
            break
        
        messages.append({"role":"user", "content": user_text})

        messages.append({"role":"user", "content": user_input})

        
        reply= get_ai_response(client, messages)

        messages.append({"role":"assistant", "content":reply})

        display_response(reply)

main()