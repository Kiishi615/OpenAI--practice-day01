from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()


prompt1 = PromptTemplate.from_template(template= "Summarize the input: {input}")
prompt2 = PromptTemplate.from_template(template= "Translate the input to French: {Summary}")
prompt3 = PromptTemplate.from_template(template= "Extract the key words : {French}")


llm = ChatOpenAI(model="gpt-3.5-turbo")

chain1 = prompt1 | llm | StrOutputParser()
chain2 = prompt2 | llm | StrOutputParser()
chain3 = prompt3 | llm | StrOutputParser()

full_chain = chain1 | chain2 | chain3

prompt = input('What do you want me to summarize? \n\n')

final_output = full_chain.invoke({"input" : prompt})


print(final_output)