from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
load_dotenv()

embeddings = OpenAIEmbeddings(model = "text-embedding-3-small")

vector_store = Chroma(
    collection_name = "lc_vectorstore"
)

vector_store.add_texts(
    texts=[
        "Langchain is awesome",
        "Langchain is slow",
        "Python is great for beginners",
        "React is a frontend framework"
    ],
    metadatas=[
    
        {"source": "twitter", "sentiment": "positive", "topic": "langchain"},
        {"source": "reddit", "sentiment": "negative", "topic": "langchain"},
        {"source": "blog", "sentiment": "positive", "topic": "python"},
        {"source": "docs", "sentiment": "neutral", "topic": "react"}
    ]
)


results = vector_store.similarity_search("How bad is langchain?", k= 2, filter={"sentiment": "negative"})
for r in results:
    print(f"{r.page_content}  |   {r.metadata}" )