import os, re
from pathlib import Path
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from shared import (load_config, setup_api, get_user_input, 
                    save_chat_log, get_ai_response,  display_response)
from dotenv import load_dotenv
from unstructured.partition.auto import partition 



load_dotenv()


def read_document_with_metadata(file_path: str) -> dict:
    """Read document, return elements with page tracking."""
    elements = partition(filename=file_path)
    path = Path(file_path)
    
    parsed = []
    for el in elements:
        text = str(el).strip()
        if not text:
            continue
        
        page = None
        if hasattr(el, 'metadata') and hasattr(el.metadata, 'page_number'):
            page = el.metadata.page_number
        
        parsed.append({"text": text, "page": page})
    
    return {
        "filename": path.name,
        "elements": parsed
    }

def chunk_with_metadata(doc: dict, strategy: str = "auto", chunk_size: int = 500, overlap: int = 50) -> list[dict]:
    """
    Chunk document while preserving page numbers.
    
    Returns:
        [
            {"text": "...", "page": 1, "source": "doc.pdf"},
            {"text": "...", "page": 2, "source": "doc.pdf"},
            ...
        ]
    """
    elements = doc["elements"]
    filename = doc["filename"]
    
    if not elements:
        return []
    
    # Get full text to decide strategy
    full_text = '\n\n'.join([el["text"] for el in elements])
    char_count = len(full_text)
    
    # Decide strategy
    if strategy == "auto":
        if char_count < 500:
            strategy = "sentence"
        elif len(elements) >= 2:
            avg_size = char_count / len(elements)
            if 100 < avg_size < 3000:
                strategy = "element"  # Each element is already a good chunk
            else:
                strategy = "overlap"
        elif char_count < 1500:
            strategy = "sentence"
        else:
            strategy = "overlap"
    
    print(f"  📄 Strategy: {strategy}")
    
    # Strategy: Element (each unstructured element becomes a chunk)
    if strategy == "element":
        return [
            {
                "text": el["text"],
                "page": el["page"],
                "source": filename
            }
            for el in elements if el["text"].strip()
        ]
    
    # Strategy: Sentence (split each element into sentences, keep page)
    if strategy == "sentence":
        import nltk
        chunks = []
        for el in elements:
            sentences = nltk.sent_tokenize(el["text"])
            for sent in sentences:
                if sent.strip():
                    chunks.append({
                        "text": sent.strip(),
                        "page": el["page"],
                        "source": filename
                    })
        return chunks
    
    # Strategy: Overlap (combine elements until chunk_size, track pages)
    if strategy == "overlap":
        chunks = []
        current_text = ""
        current_pages = set()
        
        for el in elements:
            # Would adding this element exceed chunk size?
            if len(current_text) + len(el["text"]) > chunk_size and current_text:
                # Save current chunk
                pages = sorted([p for p in current_pages if p])
                chunks.append({
                    "text": current_text.strip(),
                    "page": pages[0] if len(pages) == 1 else pages,  # Single page or list
                    "source": filename
                })
                
                # Start new chunk with overlap
                words = current_text.split()
                overlap_text = ' '.join(words[-overlap:]) if len(words) > overlap else current_text
                current_text = overlap_text + "\n\n" + el["text"]
                current_pages = {el["page"]}
            else:
                current_text += ("\n\n" if current_text else "") + el["text"]
                current_pages.add(el["page"])
        
        # Don't forget last chunk
        if current_text.strip():
            pages = sorted([p for p in current_pages if p])
            chunks.append({
                "text": current_text.strip(),
                "page": pages[0] if len(pages) == 1 else pages,
                "source": filename
            })
        
        return chunks
    
    # Strategy: Paragraph (elements are already paragraphs from unstructured)
    return [
        {
            "text": el["text"],
            "page": el["page"],
            "source": filename
        }
        for el in elements if el["text"].strip()
    ]

def get_collection(collection_name: str = "rag_documents"):
    """Initialize ChromaDB with OpenAI embeddings."""
    client = chromadb.Client()
    
    openai_ef = OpenAIEmbeddingFunction(
        api_key=os.getenv("OPENAI_API_KEY"),
        model_name="text-embedding-3-small"
    )
    
    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=openai_ef
    )
    
    return collection

def ingest_chunks(collection, chunks):
    collection.add(
    documents=[c["text"] for c in chunks],
    ids=[f"chunk_{i}" for i in range(len(chunks))],
    metadatas=[
        {
            "source": c["source"],
            "page": c["page"] if isinstance(c["page"], int) else str(c["page"])
        }
        for c in chunks
    ]
)
    return collection

def query_rag(question: str, collection, n_results: int = 10) -> list[dict]:
    """
    Query and return relevant chunks with metadata.
    
    Returns:
        [
            {"text": str, "source": str, "page": int},
            ...
        ]
    """
    results = collection.query(
        query_texts=[question],
        n_results=n_results,
        include=["documents", "metadatas"]
    )
    
    if not results["documents"][0]:
        return []
    
    chunks = []
    for i in range(len(results["documents"][0])):
        text = results["documents"][0][i]
        source = results["metadatas"][0][i].get("source", "Unknown")
        page = results["metadatas"][0][i].get("page")
        
        if page:
            chunks.append(f"[{source}, Page {page}]\n{text}")
        else:
            chunks.append(f"[{source}]\n{text}")
    
    return chunks

def rewrite_query(messages:list[dict], current_query:str, client) ->str:
    recent_history = messages[-6:]

    rewriter_prompt = [
        {"role": "system", "content": """You are a query rewriter for a document search system.

Your job: Turn the user's latest question into a standalone search query.

Rules:
1. Include the FULL topic from conversation context
2. For follow-ups like "what else", "more", "continue" - repeat the original topic
3. Only output the search query, nothing else

Examples:
- User asks "What skills do grade 8 workers need?" then "What else?"
→ "What additional skills do grade 8 workers need?"

- User asks "Tell me about safety" then "Any more details?"
→ "More details about safety requirements and procedures"
"""}
    ]

    rewriter_prompt.extend(recent_history)
    rewriter_prompt.append({"role": "user", "content": current_query})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=rewriter_prompt,
        temperature=0,
        max_tokens=100
    )

    return response.choices[0].message.content


def main():
    config = load_config()
    client = setup_api()
    messages=[{"role":"system", "content":"""You are a helpful assistant that answers 
                questions based on the provided context from the document. 
                If the context doesn't contain the answer, say you don't know."""}]

    folder = Path('documents')

    file = input("What file do you want to ask a question about? (include extension): ").strip()
    file_path = folder / file

    # Check file exists
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return

    print(f"\n✅ Loading {file}...")

    # Step 1: Read document
    doc = read_document_with_metadata(str(file_path))
    print(f"   Found {len(doc['elements'])} elements")

    # Step 2: Chunk it
    chunks = chunk_with_metadata(doc, strategy="auto")
    print(f"   Created {len(chunks)} chunks")

    # Step 3: Ingest into collection
    collection = get_collection("DEFAULT_COLLECTION_NAME")
    collection = ingest_chunks(collection, chunks)
    print(f"   ✅ Ready to query!\n")

    while True:
        user_input = get_user_input()
        if user_input.lower() == "quit":
            print("Saving chat log...")
            save_name = input("Enter filename to save log: ")
            save_chat_log(messages, save_name)
            break
        
        rewritten_query = rewrite_query(messages, user_input, client)
        context = query_rag(rewritten_query, collection, n_results=5)
        context = " ".join(context)

        temp_messages = [
            {"role": "system", "content": f"""Answer based on this context only:
                {context}
                
                If the context doesn't answer the question, respond with: I don't have
                information about that in the document"""}
        ]

        for msg in messages[-8:]:
            temp_messages.append(msg)
        
        temp_messages.append({"role": "user", "content": user_input})

        reply = get_ai_response(client, temp_messages, config)

        messages.append({"role": "user", "content": user_input})
        messages.append({"role": "assistant", "content": reply})

        display_response(reply)


if __name__ == "__main__":
    main()