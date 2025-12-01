import os
from dotenv import load_dotenv
import openai

def main():
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    client = openai.Client(api_key=api_key)

    messages = [
        {"role": "system", "content": "You are a cowboy"},
        {"role": "user", "content": "Howdy Partner"}
    ]

    response = client.chat.completions.create(
        model="gpt-5-nano",
        messages=messages
    )



    reply = response.choices[0].message.content
    print(reply)

if __name__ == "__main__":
    main()