import openai
import os, sys
from dotenv import load_dotenv
import glob


load_dotenv()

try:
    api_key=api_key=os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("API key missing")
    

    client=openai.Client(api_key=api_key)

except Exception as e:
    print(f"some error:{e}")
    client= None
    sys.exit(1)


folder_path = os.getcwd()
print(folder_path)
files =glob.glob(os.path.join(folder_path, '*.txt'))

files = [f for f in files if '_processed' not in os.path.basename(f)]

for file in files:
    filename = os.path.basename(file)
    name, ext = os.path.splitext(filename)
    new_filename = f"{name}_processed{ext}"


    with open(file) as f:
        user_text = f.read()
        messages=[{"role":"user", "content": user_text},
                  {"role":"user", "content": "summarise this in bullet points"}]
        response=client.chat.completions.create(
            model="gpt-5-nano",
            messages=messages
        )


        with open(new_filename,"w")as f:
            f.write(str(response.choices[0].message.content))
        

