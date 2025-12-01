import openai
import sys, os
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from pathlib import Path
from vector_store import initialize_chroma_collection, ingest_document, query_database

november_challenge = Path(__file__).parent.parent
sys.path.insert(0, str(november_challenge))

import enable_imports
from refactored_chatbot import  (load_config, setup_api, get_user_input, 
                                get_user_file, save_chat_log,
                                get_ai_response,  display_response)
from dotenv import load_dotenv

load_dotenv()


def rewrite_query(messages:list[dict], current_query:str, client) ->str:
    recent_history= messages[-6:]

    rewriter_prompt= [
        {"role": "system", "content": """You are a query rewriter. 
            Turn the user's latest question into a standalone search query 
            that can be understood without any prior conversation. 
            Only output the standalone query, nothing else."""}
    ]

    rewriter_prompt.extend(recent_history)
    rewriter_prompt.append({"role":"user", "content": f"{current_query}"})

    response = client.chat.completions.create(
        model ="gpt-4o-mini",
        messages = rewriter_prompt,
        temperature = 0,
        max_tokens = 100
    )

    reply=response.choices[0].message.content
    return reply



def main():
    config = load_config()
    client = setup_api()
    messages=[{"role":"system", "content":"""You are a helpful assistant that answers 
                questions based on the provided context from the document. 
                If the contex doesn't contain the answer, say you don't know."""}]

    folder=Path('Sample Documents')

    file= input("What file do you want to ask a question?").strip() +".txt"
    file_path=folder/file


    print(f"\n Great! Accessing {file}")

    empty_collection =initialize_chroma_collection("DEFAULT_COLLECTION_NAME")
    full_collection =ingest_document(file_path, empty_collection)


    while True:
        user_input=get_user_input()
        if user_input.lower()=="quit":
            print("Saving chat log...")
            save_name = input("Enter filename to save log: ")
            save_chat_log(messages, save_name)
            break
        
        rewritten_query = rewrite_query(messages, user_input, client)
        context = query_database(rewritten_query, full_collection, n_results=5)
        context= " ".join(context)

        temp_messages = [
            {"role": "system", "content":f"""Answer based on this context only:
                {context}
                
                
                If the context doesn't answer the question, respond with: I don't have
                information about that in the document"""}
        ]

        for msg in messages[-8:]:
            temp_messages.append(msg)
        
        temp_messages.append({"role":"user", "content": user_input})

        reply= get_ai_response(client, temp_messages, config)

        messages.append({"role":"user", "content": user_input})
        messages.append({"role":"assistant", "content":reply})
        

        display_response(reply)

if __name__ == "__main__":


    main()










