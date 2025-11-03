import openai
import os
from dotenv import load_dotenv

load_dotenv()


user_text=input("Enter your message: ")
print("You typed:", user_text)
messages =[{"role":"user","content":user_text}]

#API call
client=openai.Client(api_key=os.getenv("OPENAI_API_KEY"))

response=client.chat.completions.create(
    model="gpt-5-nano",
    messages= messages
)


print(response.choices[0].message.content)