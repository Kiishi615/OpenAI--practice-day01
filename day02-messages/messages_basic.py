import openai
import os
from dotenv import load_dotenv

load_dotenv()

client=openai.Client(api_key=os.getenv("OPENAI_API_KEY"))
response=client.chat.completions.create(
    model="gpt-5-nano",
    messages=[{"role":"system","content":"Say Hello"}]
)