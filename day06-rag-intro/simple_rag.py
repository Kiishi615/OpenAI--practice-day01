import openai
import chromadb
import os, sys
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from pathlib import Path
from vector_store import initialize_chroma_collection, ingest_document, query_database

november_challenge = Path(__file__).parent.parent
sys.path.insert(0, str(november_challenge))

import enable_imports
from refactored_chatbot import *
from dotenv import load_dotenv

load_dotenv()





def main():
    client= setup_api()
    messages=[{"role":"system", "content":"You are a RAG assistant"}]

    file2= input("What file do you want to ask a question?") +".txt"
    print(f"\n Great! Accessing {file2}")
        
    empty_collection =initialize_chroma_collection("Randos")
    full_collection =ingest_document(file2, empty_collection)


    while True:

        user_input=get_user_input()
        if user_input=="quit":
            messages.append({"role":"user", "content": user_input})
            save_chat_log(messages, filename='words')
            break

        messages.append({"role":"user", "content": user_input})
        answers= query_database(user_input, full_collection)
        answers= " ".join(answers)
        messages.append({"role":"user", "content": answers})

        


        reply= get_ai_response(client, messages)

        messages.append({"role":"assistant", "content":reply})
        

        display_response(reply)



    


    


    


if __name__ == "__main__":
    main()










