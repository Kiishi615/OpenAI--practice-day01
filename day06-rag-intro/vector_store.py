import openai
import chromadb
import os
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from pathlib import Path
from split_text import Text_handler, split_into_chunks
from dotenv import load_dotenv

load_dotenv()




client=chromadb.Client()

file= input("What file do you want to ask a question?") +".txt"
print(f"Great! Accessing {file}")

openai_ef=OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name="text-embedding-3-small"
)

text=Text_handler(file)
chunks=split_into_chunks(text)

collection= client.create_collection(
    name="Rand_text",
    embedding_function=openai_ef
)

collection.add(
    documents= chunks,
    ids=[f"chunk_{i}" for i in range(len(chunks))]
    
)
question = input("What's your question?")

results=collection.query(
    query_texts=[f"{question}"],
    n_results=3
)

print("Found chunks:",results['documents'][0][0])