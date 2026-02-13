from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.document_loaders import  UnstructuredFileLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
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

parent_splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000, 
    chunk_overlap = 200
)

child_splitter = SemanticChunker(
    embeddings= embedding,
    breakpoint_threshold_type= "percentile",
    breakpoint_threshold_amount= 85,
    min_chunk_size= 50
)

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
pc = Pinecone()
INDEX_NAME = pc.Index(INDEX_NAME)

llm = ChatGoogleGenerativeAI(model="gemini-3-flash-preview", temperature = 0.3)

vectorstore = PineconeVectorStore.from_documents(
    all_children,
    embedding,
    index_name=INDEX_NAME
)

# _______ Memory Stuff _______

summary = ""
recent_messages = []



# _______ Prompt def _______
reformulation_prompt = ChatPromptTemplate.from_messages([
    ("system", """Rewrite the user's latest message as a standalone question that can be understood WITHOUT any conversation history. Resolve all pronouns. Do NOT answer the question, only rewrite it. If it's already standalone, return it as-is."""),
    ("human", """Conversation summary: {summary}

Recent messages:
{recent_messages}

User's latest message: {question}

Standalone question:""")
])
answer_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a knowledgeable document assistant. Answer questions based ONLY on the provided context. If the context doesn't contain enough information, say "I couldn't find information about that in your document." Be conversational but accurate. Do not make things up."""),
    ("human", """Context from the document:
---
{context}
---

Conversation so far: {summary}

Recent messages:
{recent_messages}

Question: {question}

Answer:""")
])
summary_prompt = ChatPromptTemplate.from_messages([
    ("system", "Summarize this conversation concisely. Capture key topics and facts. Keep it under 200 words."),
    ("human", """Previous summary: {old_summary}

New messages:
{new_messages}

Updated summary:""")
])


# _______ Chain Stuff _______
reformulation_chain = reformulation_prompt | llm | StrOutputParser()
answer_chain = answer_prompt | llm | StrOutputParser()
summary_chain = summary_prompt | llm | StrOutputParser()


question = input("What's your question pretty boy? ")
query = reformulation_chain.invoke(
    {"question" : question},
)
