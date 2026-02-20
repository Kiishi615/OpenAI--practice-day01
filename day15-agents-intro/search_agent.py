from dataclasses import dataclass

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langchain_community.retrievers import WikipediaRetriever
from langchain_community.tools import DuckDuckGoSearchResults
from langgraph.checkpoint.memory import InMemorySaver
from rich import inspect

load_dotenv()

model = init_chat_model(model='gpt-5.2')

search = DuckDuckGoSearchResults(output_format='list')

retriever = WikipediaRetriever(top_k_results=4, lang="en", doc_content_chars_max=2500)

config = {'configurable' : {'thread_id' : 1}}
checkpointer = InMemorySaver()

@tool ('search_web', description=(
    "Search the internet using DuckDuckGo for current events, "
    "recent news, real-time information, or topics not likely "
    "found in encyclopedias."
))
def search_web(question: str):
    try:
        result = search.invoke(question)
        return result
    except Exception as e:
        return f"Error searching the web: {e}"

@tool ('search_wiki', description=(
    "Search Wikipedia for well-established facts, historical events, "
    "scientific concepts, biographies, or topics that need detailed, "
    "encyclopedic explanations."
))
def search_wiki(question: str):
    try:
        docs = retriever.invoke(question)
        
        result = "\n\n".join(doc.page_content for doc in docs)
        
        return result
    except Exception as e:
        return f"Error searching Wikipedia: {e}"


agent = create_agent(
    model= model,
    tools= [search_web, search_wiki],
    system_prompt= ("You are a helpful research assistant. "
    "Use search_wiki for well-established facts, science, history, and biographies. "
    "Use search_web for current events, recent news, and real-time information. "
    "If neither tool returns useful results, say 'I don't know'. "
    "Always cite which source you used."),
    checkpointer= checkpointer
)

if __name__ == "__main__":
    while True:
        user_input =input('Human: ')
        if user_input.lower() in ("quit", "exit"):
            print("AI: Goodbye")
            break
        try:
            response =agent.invoke(
                {
                'messages' : [{'role': 'user', 'content': user_input}]
                },
                config= config

            )
            print(f"AI: {response['messages'][-1].content}\n")
        except Exception as e:
            print(f"Something went wrong: {e}")
            print("Try again.\n")

# print(response)
# inspect(response, help=True)


# print(docs[0].page_content[:400])