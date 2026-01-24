from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from dotenv import load_dotenv
load_dotenv()

# Setup
model = ChatAnthropic(model_name= "claude-sonnet-4-20250514")

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a friendly assistant. Be concise."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
])

chain = prompt | model

store = {}
def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

chatbot = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)

# Chat Loop
config = {"configurable": {"session_id": "my_chat"}}

print("Chat with Claude! (type 'quit' to exit)\n")

while True:
    user_input = input("You: ")
    
    if user_input.lower() == 'quit':
        break
    
    response = chatbot.invoke({"input": user_input}, config=config)
    print(f"Claude: {response.content}\n")