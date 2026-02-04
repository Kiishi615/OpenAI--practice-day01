from langchain_anthropic import ChatAnthropic
from langchain_community.document_loaders import  PyPDFLoader
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os
load_dotenv()


loader = PyPDFLoader(file_path= r"./books/Antifragile (Nassim Nicholas Taleb) (Z-Library).pdf")
doc = loader.load()



embedding = OpenAIEmbeddings(model= 'text-embedding-3-small')

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap = 200)

chunks = splitter.split_documents(doc)

vector_store = Chroma.from_documents(documents=chunks, embedding= embedding)

llm = ChatAnthropic(model ="claude-3-haiku-20240307", temperature=0.2)

retriever = vector_store.as_retriever()

prompt = ChatPromptTemplate.from_template("""
    Answer the question with the Context, if you don't know say you don't know
    Context : {context},
    question : {question}
    """
)

chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

response = chain.invoke(("What is Antifragility"))

print(response)

