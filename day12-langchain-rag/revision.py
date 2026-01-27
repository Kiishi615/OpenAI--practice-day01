from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()

prompt1 = PromptTemplate.from_template(template= "Summarize the user input : {input}" )
prompt2 = PromptTemplate.from_template(template= "Translate the user input to french : {summary}" )
prompt3 = PromptTemplate.from_template(template= "Extract the keywords the user input : {French}" )

llm = ChatOpenAI()

chain1 = prompt1 | llm | StrOutputParser()
chain2 = prompt2 | llm | StrOutputParser()
chain3 = prompt3 | llm | StrOutputParser()

overall_chain = chain1 | chain2 | chain3

prompt = input("Nigga what's you gats to say?:  \n\n")

response = overall_chain.invoke({"input": prompt})

print(f"AI: {response}")
