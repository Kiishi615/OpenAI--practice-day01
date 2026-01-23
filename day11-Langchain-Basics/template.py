# from langchain_core.prompts import PromptTemplate

# TEMPLATE = '''
# System:
# {instruction}

# Human: {prompt}
# '''

# prompt_template = PromptTemplate.from_template(template= TEMPLATE)

# def summarize (prompt:str)->str:
#     response = prompt_template.invoke({'instruction': '''The chatbot
# should summarize whatever the user sends''',
# 'prompt': prompt })
#     return response.text

from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI  # or another LLM provider
from dotenv import load_dotenv

load_dotenv()

TEMPLATE = '''
System:
{instruction}

H: {prompt}
'''

prompt_template = PromptTemplate.from_template(template=TEMPLATE)

# Create an LLM instance
llm = ChatOpenAI(model="gpt-3.5-turbo")  # or use ChatAnthropic, etc.

# Chain the prompt with the LLM
chain = prompt_template | llm

def summarize(prompt: str) -> str:
    response = chain.invoke({
        'instruction': 'The chatbot should summarize whatever the user sends',
        'prompt': prompt
    })
    return response.content  # .content for chat models

def translate(prompt: str) -> str:
    response = chain.invoke({
        'instruction': 'The chatbot should translate to french whatever the user sends',
        'prompt': prompt
    })
    return response.content  #

def QA(prompt: str) -> str:
    response = chain.invoke({
        'instruction': 'The chatbot should answer every question whatever the user sends',
        'prompt': prompt
    })
    return response.content  #

def classify(prompt: str) -> str:
    response = chain.invoke({
        'instruction': 'The chatbot should classify into categories whatever the user sends',
        'prompt': prompt
    })
    return response.content  #

prompt = input('What do you want me to summarize? \n')

print(f"\n {summarize(prompt)}")