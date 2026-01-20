import os, re
from pathlib import Path
from openai import OpenAI
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from dotenv import load_dotenv
from unstructured.partition.auto import partition 


from shared import (
    overlap_chunks,
    sentence_chunks,
    paragraph_chunks,
)

load_dotenv()


# =============================================================================
# Setup
# =============================================================================
def read_document_with_metadata(file_path: str) -> dict:
    elements = partition(filename=file_path)
    
    return {
        "filename": Path(file_path).name,
        "elements": [
            {
                "text": str(el),
                "page": el.metadata.page_number if hasattr(el, 'metadata') and hasattr(el.metadata, 'page_number') else None
            }
            for el in elements
        ]
    }

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

def auto_select_chunker(text: str) -> list[str]:
    """
    Auto-select chunking strategy based on text structure.
    
    Logic:
    1. Very small docs (<500 chars) → sentence chunks
    2. Has paragraph structure → paragraph chunks
    3. Small docs without structure → sentence chunks  
    4. Large dense text → overlap chunks for context
    """

    
    char_count = len(text)
    
    # Count paragraphs using regex (handles \n\n or \n \n)
    pattern = r'\n\s*\n'
    paragraphs = [p.strip() for p in re.split(pattern, text) if p.strip()]
    para_count = len(paragraphs)
    
    # Very small document
    if char_count < 500:
        print(f"  📃 Strategy: Sentence (tiny doc, {char_count} chars)")
        return sentence_chunks(text)
    
    # Check if has clear paragraph structure
    if para_count >= 2:
        avg_para_size = char_count / para_count
        
        # Good paragraph size is 100-3000 chars
        if 100 < avg_para_size < 3000:
            print(f"  📄 Strategy: Paragraph ({para_count} paragraphs, ~{int(avg_para_size)} chars each)")
            return paragraph_chunks(text)
    
    # Small document without clear structure
    if char_count < 1500:
        print(f"  📃 Strategy: Sentence (small doc, {char_count} chars)")
        return sentence_chunks(text)
    
    # Large or dense text - use overlap for context continuity
    print(f"  🔄 Strategy: Overlap (dense text, {char_count} chars)")
    return overlap_chunks(text, chunk_size=500, overlap=50)

# =============================================================================
# Smart Chunking
# =============================================================================

# def auto_select_chunker(text: str) -> list[str]:
#     """
#     Auto-select best chunking strategy based on content.
    
#     Logic:
#     1. Markdown → paragraph chunks (preserves sections)
#     2. High paragraph density → paragraph chunks
#     3. Small docs (<1000 chars) → sentence chunks
#     4. Default → overlap chunks (safe fallback)
#     """
#     paragraphs = text.count('\n\n')
#     char_count = len(text)
    
#     # Check for Markdown patterns
#     is_markdown = (
#         text.startswith('#') or 
#         '\n# ' in text or 
#         '\n## ' in text or
#         '\n### ' in text or
#         '\n- ' in text or      # Bullet lists
#         '\n* ' in text or      # Alternate bullets
#         '\n```' in text        # Code blocks
#     )

#     if is_markdown:
#         print("  📝 Strategy: Markdown/Paragraph Splitting")
#         return paragraph_chunks(text)
        
#     if char_count > 0 and paragraphs > (char_count / 1000): 
#         print("  📄 Strategy: Paragraph Chunking")
#         return paragraph_chunks(text)
    
#     if char_count < 1000:
#         print("  📃 Strategy: Sentence Chunks (small doc)")
#         return sentence_chunks(text)

#     print("  🔄 Strategy: Overlap Chunks (general purpose)")
#     return overlap_chunks(text, chunk_size=500, overlap=50)


# def chunk_text(text: str, strategy: str = "auto", **kwargs) -> list[str]:
#     """
#     Chunk text with specified or auto strategy.
    
#     Args:
#         text: Text to chunk
#         strategy: "auto", "paragraph", "sentence", "overlap", "fixed"
#         **kwargs: chunk_size, overlap for relevant strategies
    
#     Returns:
#         List of text chunks
#     """
#     if strategy == "auto":
#         chunks = auto_select_chunker(text)
#     elif strategy == "paragraph":
#         print("  📄 Strategy: Paragraph Chunking")
#         chunks = paragraph_chunks(text)
#     elif strategy == "sentence":
#         print("  📃 Strategy: Sentence Chunking")
#         chunks = sentence_chunks(text)
#     elif strategy == "overlap":
#         chunk_size = kwargs.get("chunk_size", 500)
#         overlap = kwargs.get("overlap", 50)
#         print(f"  🔄 Strategy: Overlap Chunks ({chunk_size}/{overlap})")
#         chunks = overlap_chunks(text, chunk_size=chunk_size, overlap=overlap)
#     elif strategy == "fixed":
#         chunk_size = kwargs.get("chunk_size", 100)
#         print(f"  📏 Strategy: Fixed Size ({chunk_size} words)")
#         chunks = fixed_size_chunks(text, chunk_size=chunk_size)
#     else:
#         raise ValueError(f"Unknown strategy: {strategy}")
    
#     # Filter empty chunks
#     chunks = [c.strip() for c in chunks if c.strip()]
    
#     # Filter very small chunks (less than 10 characters)
#     chunks = [c for c in chunks if len(c) >= 10]
    
#     return chunks


# =============================================================================
# Document Ingestion with Metadata
# =============================================================================

def ingest_file(
    file_path: str, 
    collection, 
    strategy: str = "auto",
    **chunk_kwargs
) -> int:
    """
    Ingest a single file with metadata.
    
    Returns number of chunks added.
    """
    path = Path(file_path)
    filename = path.name
    
    print(f"\n📄 Processing: {filename}")
    
    # Read document using unstructured
    try:
        text = read_document(file_path)
    except Exception as e:
        print(f"  ❌ Failed to read: {e}")
        return 0
    
    if not text or not text.strip():
        print(f"  ⚠️  Empty document, skipping")
        return 0
    
    # Chunk the text
    chunks = chunk_text(text, strategy, **chunk_kwargs)
    
    if not chunks:
        print(f"  ⚠️  No chunks created, skipping")
        return 0
    
    # Create unique IDs using filename to avoid collisions
    file_id = path.stem.replace(" ", "_").replace("-", "_")[:20]
    
    # Check for existing chunks from this file and remove them
    try:
        existing = collection.get(where={"source": filename})
        if existing and existing["ids"]:
            collection.delete(ids=existing["ids"])
            print(f"  🔄 Replaced {len(existing['ids'])} existing chunks")
    except Exception:
        pass  # Collection might be empty
    
    ids = [f"{file_id}_chunk_{i}" for i in range(len(chunks))]
    
    metadatas = [
        {
            "source": filename,
            "file_path": str(path.absolute()),
            "file_type": path.suffix.lower(),
            "chunk_index": i,
            "total_chunks": len(chunks),
            "char_count": len(chunks[i]),
        }
        for i in range(len(chunks))
    ]
    
    # Add to collection
    collection.add(
        documents=chunks,
        ids=ids,
        metadatas=metadatas
    )
    
    print(f"  ✅ Added {len(chunks)} chunks")
    return len(chunks)


def ingest_folder(
    folder_path: str, 
    collection, 
    strategy: str = "auto",
    recursive: bool = False,
    **chunk_kwargs
) -> dict:
    """
    Ingest all supported files from a folder.
    
    Returns stats dict.
    """
    folder = Path(folder_path)
    
    if not folder.exists():
        raise FileNotFoundError(f"Folder not found: {folder_path}")
    
    # Supported extensions (unstructured handles these)
    supported = {
        ".txt", ".pdf", ".docx", ".doc", ".md", 
        ".html", ".htm", ".pptx", ".xlsx", ".csv", 
        ".json", ".eml", ".msg", ".rtf", ".odt"
    }
    
    stats = {
        "files_processed": 0,
        "files_failed": 0,
        "total_chunks": 0,
        "by_type": {}
    }
    
    print(f"\n{'='*60}")
    print(f"📂 Ingesting folder: {folder}")
    print(f"{'='*60}")
    
    # Get files
    pattern = "**/*" if recursive else "*"
    files = [f for f in folder.glob(pattern) if f.is_file() and f.suffix.lower() in supported]
    
    if not files:
        print(f"⚠️  No supported files found in {folder}")
        print(f"   Supported types: {', '.join(sorted(supported))}")
        return stats
    
    print(f"Found {len(files)} files to process")
    
    for file_path in sorted(files):
        chunks_added = ingest_file(str(file_path), collection, strategy, **chunk_kwargs)
        
        if chunks_added > 0:
            stats["files_processed"] += 1
            stats["total_chunks"] += chunks_added
            
            ext = file_path.suffix.lower()
            stats["by_type"][ext] = stats["by_type"].get(ext, 0) + 1
        else:
            stats["files_failed"] += 1
    
    print(f"\n{'='*60}")
    print(f"📊 Ingestion Complete")
    print(f"{'='*60}")
    print(f"  ✅ Files processed: {stats['files_processed']}")
    print(f"  ❌ Files failed: {stats['files_failed']}")
    print(f"  📦 Total chunks: {stats['total_chunks']}")
    if stats["by_type"]:
        print(f"  📁 By type: {stats['by_type']}")
    
    return stats


# =============================================================================
# Retrieval with Source Tracking
# =============================================================================

def retrieve(
    query: str, 
    collection, 
    n_results: int = 5,
    filter_source: str = None
) -> list[dict]:
    """
    Retrieve relevant chunks with metadata.
    
    Args:
        query: Search query
        collection: ChromaDB collection
        n_results: Number of results to return
        filter_source: Optional filename to filter by
    
    Returns:
        List of {content, source, chunk_index, distance, metadata}
    """
    # Build where clause if filtering
    where = {"source": filter_source} if filter_source else None
    
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
        where=where
    )
    
    # Handle empty results
    if not results["documents"] or not results["documents"][0]:
        return []
    
    retrieved = []
    
    for i in range(len(results["documents"][0])):
        retrieved.append({
            "content": results["documents"][0][i],
            "source": results["metadatas"][0][i]["source"],
            "chunk_index": results["metadatas"][0][i]["chunk_index"],
            "total_chunks": results["metadatas"][0][i].get("total_chunks", "?"),
            "distance": results["distances"][0][i],
            "metadata": results["metadatas"][0][i]
        })
    
    return retrieved


def format_context_with_sources(retrieved: list[dict]) -> str:
    """Format retrieved chunks with source labels for the prompt."""
    
    if not retrieved:
        return "No relevant context found."
    
    context_parts = []
    
    for i, item in enumerate(retrieved, 1):
        source = item["source"]
        chunk_idx = item["chunk_index"]
        total = item["total_chunks"]
        content = item["content"]
        
        header = f"[Source {i}: {source} (chunk {chunk_idx + 1}/{total})]"
        context_parts.append(f"{header}\n{content}")
    
    return "\n\n---\n\n".join(context_parts)


# =============================================================================
# Answer Generation with Citations
# =============================================================================

def generate_answer(
    query: str, 
    collection, 
    n_results: int = 5,
    model: str = "gpt-4o-mini"
) -> dict:
    """
    Generate answer with source citations.
    
    Returns:
        {
            answer: str,
            sources: list[str],
            retrieved: list[dict],
            confidence: float,
            tokens_used: int
        }
    """
    client = OpenAI()
    
    # Retrieve relevant chunks
    retrieved = retrieve(query, collection, n_results)
    
    if not retrieved:
        return {
            "answer": "I don't have any relevant information in the loaded documents to answer this question.",
            "sources": [],
            "retrieved": [],
            "confidence": 0.0,
            "tokens_used": 0
        }
    
    # Format context with sources
    context = format_context_with_sources(retrieved)
    
    # Build prompt
    system_prompt = """You are a helpful assistant that answers questions based ONLY on the provided context.

IMPORTANT RULES:
1. ONLY use information from the provided sources - never use outside knowledge
2. Cite sources using [Source N] format when you use information from them
3. If the context doesn't contain enough information, say "I don't have sufficient information about this in the provided documents."
4. Be accurate and concise
5. If sources conflict, mention the discrepancy
6. Never make up or infer information not explicitly in the sources"""

    user_prompt = f"""Context from documents:

{context}

---

Question: {query}

Provide an answer based ONLY on the context above. Cite your sources using [Source N] format."""

    # Generate response
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.1  # Low temperature for factual answers
    )
    
    answer = response.choices[0].message.content
    
    # Calculate confidence based on relevance (lower distance = more relevant)
    # ChromaDB distance: 0 = identical, higher = less similar
    avg_distance = sum(r["distance"] for r in retrieved) / len(retrieved)
    min_distance = min(r["distance"] for r in retrieved)
    
    # Convert to confidence (rough heuristic)
    # Distance of 0.5 or less is usually good, 1.0+ is poor
    confidence = max(0, min(1, 1 - (avg_distance / 2)))
    
    # Boost confidence if best match is very close
    if min_distance < 0.3:
        confidence = min(1, confidence + 0.1)
    
    # List unique sources
    sources_used = list(dict.fromkeys(r["source"] for r in retrieved))  # Preserves order
    
    return {
        "answer": answer,
        "sources": sources_used,
        "retrieved": retrieved,
        "confidence": confidence,
        "tokens_used": response.usage.total_tokens
    }


def query(
    question: str, 
    collection, 
    n_results: int = 5,
    verbose: bool = True
) -> dict:
    """
    Main query function - retrieve and generate answer.
    """
    result = generate_answer(question, collection, n_results)
    
    if verbose:
        print(f"\n{'─'*60}")
        print(f"❓ Question: {question}")
        print(f"{'─'*60}")
        print(f"\n💡 Answer:\n{result['answer']}")
        print(f"\n📚 Sources: {', '.join(result['sources']) if result['sources'] else 'None'}")
        print(f"📊 Confidence: {result['confidence']:.0%}")
        print(f"🔤 Tokens: {result['tokens_used']}")
    
    return result


# =============================================================================
# Testing
# =============================================================================

def test_with_questions(collection, questions: list[str] = None) -> list[dict]:
    """
    Run test questions and return results.
    
    If no questions provided, uses defaults.
    """
    
    if questions is None:
        questions = [
            "What is this document about?",
            "What are the main topics covered?",
            "Summarize the key points.",
            "What conclusions are drawn?",
            "Tell me about something not mentioned in the documents.",
        ]
    
    print(f"\n{'='*60}")
    print("📋 TESTING RAG PIPELINE")
    print(f"{'='*60}")
    
    # Check collection status
    count = collection.count()
    print(f"📦 Collection has {count} chunks")
    
    if count == 0:
        print("⚠️  No documents loaded. Please ingest files first.")
        return []
    
    results = []
    
    for i, q in enumerate(questions, 1):
        print(f"\n{'─'*60}")
        print(f"Q{i}: {q}")
        print('─'*60)
        
        result = query(q, collection, verbose=False)
        
        # Truncate long answers for display
        answer = result["answer"]
        if len(answer) > 400:
            display_answer = answer[:400] + "..."
        else:
            display_answer = answer
        
        print(f"\nAnswer: {display_answer}")
        print(f"\nSources: {', '.join(result['sources']) if result['sources'] else 'None'}")
        print(f"Confidence: {result['confidence']:.0%}")
        
        results.append({
            "question": q,
            "answer": result["answer"],
            "sources": result["sources"],
            "confidence": result["confidence"]
        })
    
    # Summary
    print(f"\n{'='*60}")
    print("📈 TEST SUMMARY")
    print(f"{'='*60}")
    
    avg_conf = sum(r["confidence"] for r in results) / len(results) if results else 0
    answered = sum(1 for r in results if r["confidence"] > 0.3)
    
    print(f"  Questions: {len(results)}")
    print(f"  Answered well (>30% conf): {answered}/{len(results)}")
    print(f"  Average confidence: {avg_conf:.0%}")
    
    return results


def get_collection_stats(collection) -> dict:
    """Get stats about what's in the collection."""
    
    count = collection.count()
    
    if count == 0:
        return {"total_chunks": 0, "sources": [], "by_type": {}}
    
    # Get all metadata
    all_data = collection.get(include=["metadatas"])
    
    sources = set()
    by_type = {}
    
    for meta in all_data["metadatas"]:
        sources.add(meta.get("source", "unknown"))
        file_type = meta.get("file_type", "unknown")
        by_type[file_type] = by_type.get(file_type, 0) + 1
    
    return {
        "total_chunks": count,
        "sources": sorted(sources),
        "by_type": by_type
    }


# =============================================================================
# Main
# =============================================================================

def main():
    """Interactive demo of the Advanced RAG Pipeline."""
    
    print("🚀 Advanced RAG Pipeline")
    print("=" * 60)
    
    # Initialize
    collection = get_collection("advanced_rag")
    
    # Check existing data
    stats = get_collection_stats(collection)
    if stats["total_chunks"] > 0:
        print(f"\n📦 Existing collection found:")
        print(f"   Chunks: {stats['total_chunks']}")
        print(f"   Sources: {', '.join(stats['sources'][:5])}")
        
        choice = input("\nUse existing data? (y/n): ").strip().lower()
        if choice != 'y':
            # Clear and reingest
            collection = get_collection("advanced_rag_new")
    
    # Ingest if empty
    if collection.count() == 0:
        folder_path = input("\nEnter folder path to ingest: ").strip()
        
        if folder_path and Path(folder_path).exists():
            ingest_folder(folder_path, collection, strategy="auto")
        else:
            print(f"⚠️  Folder not found: {folder_path}")
            return
    
    # Interactive loop
    print(f"\n{'='*60}")
    print("💬 Ready for questions!")
    print("   Commands: 'test' | 'stats' | 'quit'")
    print(f"{'='*60}")
    
    while True:
        question = input("\n❓ Question: ").strip()
        
        if not question:
            continue
        
        if question.lower() == 'quit':
            print("👋 Goodbye!")
            break
        
        if question.lower() == 'test':
            custom = input("Enter test questions (comma-separated) or press Enter for defaults: ").strip()
            if custom:
                questions = [q.strip() for q in custom.split(",")]
            else:
                questions = None
            test_with_questions(collection, questions)
            continue
        
        if question.lower() == 'stats':
            stats = get_collection_stats(collection)
            print(f"\n📊 Collection Stats:")
            print(f"   Total chunks: {stats['total_chunks']}")
            print(f"   Sources ({len(stats['sources'])}): {', '.join(stats['sources'])}")
            print(f"   By type: {stats['by_type']}")
            continue
        
        query(question, collection)


if __name__ == "__main__":
    main()