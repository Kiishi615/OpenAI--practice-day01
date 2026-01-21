import chromadb
import os
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from shared.split_text import text_handler, split_into_chunks
from dotenv import load_dotenv

load_dotenv()

def initialize_chroma_collection(collection_name):
    client=chromadb.Client()
    
    openai_ef=OpenAIEmbeddingFunction(
        api_key=os.getenv("OPENAI_API_KEY"),
        model_name="text-embedding-3-small"
    )
    collection= client.create_collection(
        name=f"{collection_name}",
        embedding_function=openai_ef
    )

    return collection

def ingest_document(file, collection):
    text=text_handler(file)
    chunks=split_into_chunks(text)
    collection.add(
        documents= chunks,
        ids=[f"chunk_{i}" for i in range(len(chunks))]
    )
    return collection



def query_database(question, collection, n_results=3):
    results=collection.query(
        query_texts=[f"{question}"],
        n_results=n_results
    )
    return results['documents'][0]
    


def main():
    empty_collection =initialize_chroma_collection("Randos")
    full_collection =ingest_document(file, empty_collection)
    answers= query_database(question, full_collection)
    print(answers)

if __name__ == "__main__":
    main()









