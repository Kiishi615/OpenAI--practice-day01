import openai
import os, sys
from dotenv import load_dotenv

load_dotenv()

api_key=os.getenv("OPENAI_API_KEY")
client=openai.Client(api_key=api_key)

def call_openai(message):
    messages=[{'role':'user', 'content':message}]
    response=client.chat.completions.create(
        model="gpt-5-nano",
        messages=messages
    )
    return response.choices[0].message.content

def call_with_system(user_msg, system_msg):
    # Build messages
    messages=[{'role':'system', 'content':system_msg}, 
            {'role':'user', 'content':user_msg} ]
    # Call API
    response=client.chat.completions.create(
        model="gpt-5-nano",
        messages=messages
    )
    return response.choices[0].message.content

if __name__=="__main__":
    print("Testing call_openai()...")
    response1 = call_openai("Tell me a joke")
    print("Response:", response1)
    print("\n" + "-"*50 + "\n")
    
    print("Testing call_with_system()...")
    response2 = call_with_system( 
        "Tell me a joke",
        "You are a comedian who tells only dad jokes"
        
    )
    print("Response:", response2)