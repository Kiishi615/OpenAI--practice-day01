from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_classic.chains.retrieval import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain 
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from dotenv import load_dotenv
load_dotenv()


system_prompt = ("""You are an assistant for question-answering tasks.
    Use the following pieces of retrieved context to answer the question.
    If you don't know the answer, say so.

    Context:
    {context}""")

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ]
)

chat_history = ChatMessageHistory()

llm = ChatOpenAI(temperature=0.2, model="gpt-5.2", streaming=True)

# loader = DirectoryLoader(
#     "./docs",
#     glob="**/*.pdf",
#     loader_cls=PyPDFLoader,
#     show_progress=True  
# )

loader = PyPDFLoader("./docs/2601.20452v1.pdf")
doc = loader.load()



# print(doc[0].page_content[:100])

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 500,
    chunk_overlap = 50,
    add_start_index = True
)



embeddings = OpenAIEmbeddings(model = "text-embedding-3-small")

vector_store = Chroma(
    collection_name = "lc_vectorstore",
    embedding_function= embeddings
)

chunks = text_splitter.split_documents(doc)


# for doc in loader.lazy_load():
#     chunks = text_splitter.split_documents([doc])


#     vector_store.add_documents(
#         documents= chunks
#     )

vector_store.add_documents(documents=chunks)

question_answer_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(vector_store.as_retriever(), question_answer_chain)


while True:
    user_input = input("\nYou: ").strip()
    if user_input.lower() == "break":
        break
    elif user_input.lower() == "clear":
        chat_history.clear()
        print("Chat History cleared")
    else: 
        response = rag_chain.invoke({
            "input": user_input,
            "chat_history": chat_history.messages
            })
        chat_history.add_user_message(user_input)
        chat_history.add_ai_message(response["answer"])
        print(f"\nAssistant: {response["answer"]}")


