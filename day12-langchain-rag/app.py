"""
RAG Chatbot with Streamlit
==========================

FLOW:
1. User uploads a PDF
2. We process it (load → chunk → embed → store)
3. We build the RAG chain
4. User chats with the document
5. Conversation history is maintained

STREAMLIT CONCEPT:
- Streamlit re-runs the ENTIRE script on every interaction
- To persist data between reruns, we use st.session_state
- Think of session_state as a dictionary that survives reruns
"""

import streamlit as st
import tempfile
import os

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

from langchain_classic.chains.retrieval import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain 
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from dotenv import load_dotenv

load_dotenv()


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║ SECTION 1: CONFIGURATION                                                  ║
# ║ All settings in one place - easy to modify                                ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

CONFIG = {
    # Document processing
    "chunk_size": 500,
    "chunk_overlap": 50,
    
    # Models
    "embedding_model": "text-embedding-3-small",
    "llm_model": "gpt-4o",
    "llm_temperature": 0.2,
    
    # Retrieval
    "retriever_k": 4,
}

# Page config (must be first Streamlit command)
st.set_page_config(
    page_title="Chat with PDF",
    page_icon="📄",
    layout="centered",
)


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║ SECTION 2: SESSION STATE INITIALIZATION                                   ║
# ║ These variables persist across Streamlit reruns                           ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

# Initialize session state variables if they don't exist
if "messages" not in st.session_state:
    # Chat messages for display: [{"role": "user/assistant", "content": "..."}]
    st.session_state.messages = []

if "chat_history" not in st.session_state:
    # LangChain history object for the chain
    st.session_state.chat_history = ChatMessageHistory()

if "rag_chain" not in st.session_state:
    # The RAG chain (None until document is processed)
    st.session_state.rag_chain = None

if "document_processed" not in st.session_state:
    # Flag to track if we've processed a document
    st.session_state.document_processed = False

if "current_file_name" not in st.session_state:
    # Track which file is currently loaded
    st.session_state.current_file_name = None


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║ SECTION 3: DOCUMENT PROCESSING FUNCTIONS                                  ║
# ║ PDF → Pages → Chunks → Vector Store → Retriever                           ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

def save_uploaded_file(uploaded_file) -> str:
    """
    Save uploaded file to a temporary location.
    
    Input:  uploaded_file (Streamlit UploadedFile object)
    Output: path to saved file (str)
    
    WHY: PyPDFLoader needs a file path, but Streamlit gives us bytes.
            So we save to a temp file first.
    """
    # Create temp directory if it doesn't exist
    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, uploaded_file.name)
    
    # Write the uploaded bytes to the temp file
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return temp_path


def load_and_chunk_pdf(file_path: str) -> list:
    """
    Load PDF and split into chunks.
    
    Input:  file_path (str)
    Output: chunks (List[Document])
    
    FLOW: PDF file → Pages (List[Document]) → Chunks (List[Document])
    """
    # Load PDF into pages
    loader = PyPDFLoader(file_path)
    pages = loader.load()
    
    # Split pages into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CONFIG["chunk_size"],
        chunk_overlap=CONFIG["chunk_overlap"],
        add_start_index=True,
    )
    chunks = splitter.split_documents(pages)
    
    return chunks


def create_vector_store(chunks: list) -> Chroma:
    """
    Create embeddings and store in vector database.
    
    Input:  chunks (List[Document])
    Output: vector_store (Chroma)
    
    FLOW: Chunks → Embeddings (via OpenAI) → Stored in ChromaDB
    """
    embeddings = OpenAIEmbeddings(model=CONFIG["embedding_model"])
    
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name="uploaded_document",
    )
    
    return vector_store


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║ SECTION 4: CHAIN BUILDING FUNCTIONS                                       ║
# ║ Vector Store → Retriever → Prompt → LLM → Chain                           ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

def create_prompt() -> ChatPromptTemplate:
    """
    Create the prompt template.
    
    PLACEHOLDERS:
    - {context}      : Retrieved documents (filled by create_retrieval_chain)
    - {chat_history} : Previous messages (we pass this in invoke)
    - {input}        : User's question (we pass this in invoke)
    """
    system_prompt = """You are a helpful assistant that answers questions based on the provided document.

Use the following pieces of retrieved context to answer the question.
If you don't know the answer or it's not in the context, say so honestly.
Be concise but thorough.

Context:
{context}"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ])
    
    return prompt


def create_rag_chain(vector_store: Chroma):
    """
    Build the complete RAG chain.
    
    Input:  vector_store (Chroma)
    Output: rag_chain (Runnable)
    
    CHAIN FLOW:
    {"input", "chat_history"} 
        → retriever adds "context"
        → prompt formats everything
        → LLM generates answer
        → returns {"input", "chat_history", "context", "answer"}
    """
    # Create LLM
    llm = ChatOpenAI(
        model=CONFIG["llm_model"],
        temperature=CONFIG["llm_temperature"],
    )
    
    # Create prompt
    prompt = create_prompt()
    
    # Create retriever from vector store
    retriever = vector_store.as_retriever(
        search_kwargs={"k": CONFIG["retriever_k"]}
    )
    
    # Build chain: prompt + LLM (handles document stuffing)
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    
    # Build chain: retriever + QA chain (handles retrieval + adds context)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    
    return rag_chain


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║ SECTION 5: PROCESS DOCUMENT (Combines all processing steps)               ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

def process_document(uploaded_file) -> bool:
    """
    Full pipeline: Upload → Save → Load → Chunk → Embed → Store → Chain
    
    Input:  uploaded_file (Streamlit UploadedFile)
    Output: success (bool)
    
    Side effects: Updates st.session_state with the new chain
    """
    try:
        with st.spinner("Processing document..."):
            # Step 1: Save uploaded file temporarily
            status = st.status("Processing your document...", expanded=True)
            
            status.write("📁 Saving file...")
            file_path = save_uploaded_file(uploaded_file)
            
            # Step 2: Load and chunk
            status.write("📄 Loading and splitting PDF...")
            chunks = load_and_chunk_pdf(file_path)
            status.write(f"   Created {len(chunks)} chunks")
            
            # Step 3: Create vector store
            status.write("🧮 Creating embeddings...")
            vector_store = create_vector_store(chunks)
            
            # Step 4: Create RAG chain
            status.write("🔗 Building RAG chain...")
            rag_chain = create_rag_chain(vector_store)
            
            # Step 5: Update session state
            st.session_state.rag_chain = rag_chain
            st.session_state.document_processed = True
            st.session_state.current_file_name = uploaded_file.name
            
            # Clear previous chat when new document is loaded
            st.session_state.messages = []
            st.session_state.chat_history = ChatMessageHistory()
            
            status.update(label="✅ Document processed!", state="complete")
            
            # Cleanup temp file
            os.remove(file_path)
            
        return True
        
    except Exception as e:
        st.error(f"Error processing document: {str(e)}")
        return False


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║ SECTION 6: CHAT FUNCTION                                                  ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

def get_response(user_input: str) -> str:
    """
    Send user input through the RAG chain and get response.
    
    Input:  user_input (str)
    Output: answer (str)
    
    Side effects: Updates chat_history in session_state
    
    INVOKE INPUT:  {"input": str, "chat_history": List[Message]}
    INVOKE OUTPUT: {"input": str, "chat_history": [...], "context": [...], "answer": str}
    """
    response = st.session_state.rag_chain.invoke({
        "input": user_input,
        "chat_history": st.session_state.chat_history.messages,
    })
    
    # Update LangChain history (for context in future questions)
    st.session_state.chat_history.add_user_message(user_input)
    st.session_state.chat_history.add_ai_message(response["answer"])
    
    return response["answer"]


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║ SECTION 7: STREAMLIT UI                                                   ║
# ║ This is what the user sees and interacts with                             ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

# ──────────────────────────────────────────────────────────────────────────────
# Header
# ──────────────────────────────────────────────────────────────────────────────
st.title("📄 Chat with PDF")
st.caption("Upload a PDF and ask questions about it")


# ──────────────────────────────────────────────────────────────────────────────
# Sidebar: File Upload & Settings
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("📁 Document")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Upload a PDF",
        type=["pdf"],
        help="Select a PDF file to chat with"
    )
    
    # Process button
    if uploaded_file is not None:
        # Check if this is a new file
        is_new_file = (uploaded_file.name != st.session_state.current_file_name)
        
        if is_new_file:
            if st.button("📥 Process Document", type="primary", use_container_width=True):
                process_document(uploaded_file)
        else:
            st.success(f"✅ {uploaded_file.name} is loaded")
    
    # Show current status
    st.divider()
    
    if st.session_state.document_processed:
        st.success(f"**Loaded:** {st.session_state.current_file_name}")
        
        # Clear chat button
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.chat_history = ChatMessageHistory()
            st.rerun()
    else:
        st.info("👆 Upload a PDF to get started")
    
    # Settings expander
    with st.expander("⚙️ Settings"):
        st.write(f"**Chunk size:** {CONFIG['chunk_size']}")
        st.write(f"**Chunk overlap:** {CONFIG['chunk_overlap']}")
        st.write(f"**LLM:** {CONFIG['llm_model']}")
        st.write(f"**Retriever K:** {CONFIG['retriever_k']}")


# ──────────────────────────────────────────────────────────────────────────────
# Main Chat Area
# ──────────────────────────────────────────────────────────────────────────────

# Show chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask a question about your document..."):
    
    # Check if document is processed
    if not st.session_state.document_processed:
        st.warning("⚠️ Please upload and process a document first!")
    else:
        # Add user message to display
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = get_response(prompt)
            st.markdown(response)
        
        # Add assistant message to display
        st.session_state.messages.append({"role": "assistant", "content": response})


# ──────────────────────────────────────────────────────────────────────────────
# Footer
# ──────────────────────────────────────────────────────────────────────────────
if not st.session_state.document_processed:
    st.markdown("---")
    st.markdown(
        """
        ### How to use:
        1. **Upload** a PDF document using the sidebar
        2. **Click** "Process Document" to analyze it
        3. **Ask** questions in the chat box below
        
        The chatbot will remember your conversation and use context from previous messages.
        """
    )