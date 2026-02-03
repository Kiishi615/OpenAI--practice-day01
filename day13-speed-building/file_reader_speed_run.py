from unstructured.partition.auto import partition
import openai
from dotenv import load_dotenv
load_dotenv()

elements = partition("1mb.pdf")
text = []
for element in elements:
    text.append(element.text)



messages = [
            {"role": "system", "content": f"""
                You are a RAG bot. Answer any question asked with my provided context {text}. If nothing similar exists, your only response is: 'I don't know.'
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