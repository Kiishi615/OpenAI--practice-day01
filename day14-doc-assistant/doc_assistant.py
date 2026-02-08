from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.document_loaders import  UnstructuredFileLoader, DirectoryLoader
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_pinecone import PineconeVectorStore
from langchain_experimental.text_splitter import SemanticChunker
from pathlib import Path
import uuid, os
from dotenv import load_dotenv
load_dotenv()

DOCS_DIR = Path(__file__).parent / "docs"

loader = DirectoryLoader(str(DOCS_DIR),
                        loader_cls= UnstructuredFileLoader,
                        show_progress= True,
                        use_multithreading= True,
                        silent_errors=True)

embedding = OpenAIEmbeddings(model= 'text-embedding-3-small')

parent_store = {}   
all_children = [] 
available_docs = set()

parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap = 200)
child_splitter = SemanticChunker(embeddings= embedding)

for doc in loader.lazy_load():
    source = Path(doc.metadata.get("source", "unknown")).name
    doc.metadata["source"] = source  
    available_docs.add(source)

    
    parent_chunks = parent_splitter.split_documents([doc])

    
    for parent_chunk in parent_chunks:
        
        parent_id = str(uuid.uuid4())

        
        parent_store[parent_id] = {
            "content": parent_chunk.page_content,
            "metadata": parent_chunk.metadata
        }

        
        try:
            child_chunks = child_splitter.split_documents([parent_chunk])
        except Exception as e:
            print(f"Semantic chunking failed for a parent chunk, skipping: {e}")
            continue

        for i, child in enumerate(child_chunks):
            child.metadata["parent_id"] = parent_id
            child.metadata["child_index"] = i
            all_children.append(child)

INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "doc-assistant")

vectorstore = PineconeVectorStore.from_documents(
    all_children,
    embedding,
    index_name=INDEX_NAME
)
while True:
    query = input("""
AI: What your question?
Human:  """)
    results = vectorstore.similarity_search(query, k=6)
    print(f"\n--- Test Search: '{query}' ---")
    for result in results:
        print(f"\n {result.page_content}")