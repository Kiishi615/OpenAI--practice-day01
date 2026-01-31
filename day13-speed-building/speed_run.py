import openai
from dotenv import load_dotenv
load_dotenv()

messages = [
            {"role": "system", "content": """
                                            You are the Vengeance of Gotham. You speak in short, punchy sentences. 
                                            Your world is one of shadows, grit, and tireless duty. 
                                            You are weary but resolute. Avoid humor. You are the Night.

                                            """
            }]

while True:
    
    user_input = input("\nHuman: ").strip()
    if user_input.lower() == "stop":
        break
    else:
        messages.append({"role": "user", "content": user_input })

        response = openai.chat.completions.create(
            model = "gpt-5-nano",
            messages= messages
        )
        messages.append({"role": "assistant", "content": f"{response.choices[0].message.content}" })

    print(f"\nAI: {response.choices[0].message.content}")