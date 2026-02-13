import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.document_loaders import UnstructuredFileLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from langchain_experimental.text_splitter import SemanticChunker
import uuid, os, json, asyncio, time
from dotenv import load_dotenv

load_dotenv()


# _______ Logging Setup _______

def setup_logging(level=logging.INFO, log_dir="logs"):
    Path(log_dir).mkdir(exist_ok=True)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.handlers = []

    # File — captures everything
    file_handler = RotatingFileHandler(
        Path(log_dir) / "doc_assistant.log",
        maxBytes=10_000_000,
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)s | %(funcName)s | %(message)s"
    ))

    # Console — clean, info only
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

setup_logging()
log = logging.getLogger("doc_assistant")


# _______ Config _______

DOCS_DIR = Path(__file__).parent / "docs"
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "doc-assistant")
MAX_RECENT_PAIRS = 3

# _______ Shared Tools _______

embedding = OpenAIEmbeddings(model="text-embedding-3-small")
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)


# _______ Ingest _______

async def ingest():
    log.info("Starting ingest")
    start_time = time.time()

    loader = DirectoryLoader(
        str(DOCS_DIR),
        loader_cls=UnstructuredFileLoader,
        show_progress=True,
        use_multithreading=True,
        silent_errors=True
    )

    parent_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200
    )

    child_splitter = SemanticChunker(
        embeddings=embedding,
        breakpoint_threshold_type="percentile",
        breakpoint_threshold_amount=85,
        min_chunk_size=50
    )

    parent_store = {}
    all_children = []
    available_docs = set()

    for doc in loader.lazy_load():
        source = Path(doc.metadata.get("source", "unknown")).name
        doc.metadata["source"] = source
        available_docs.add(source)

        doc_start = time.time()
        doc_children = 0

        parent_chunks = parent_splitter.split_documents([doc])
        log.debug(f"{source}: {len(parent_chunks)} parent chunks created")

        for parent_chunk in parent_chunks:
            parent_id = str(uuid.uuid4())

            parent_store[parent_id] = {
                "content": parent_chunk.page_content,
                "metadata": parent_chunk.metadata
            }

            try:
                child_chunks = child_splitter.split_documents([parent_chunk])
            except Exception as e:
                log.warning(f"Semantic chunking failed for parent {parent_id[:8]}: {e}")
                continue

            for i, child in enumerate(child_chunks):
                child.metadata["parent_id"] = parent_id
                child.metadata["child_index"] = i
                all_children.append(child)
                doc_children += 1

        doc_time = time.time() - doc_start
        log.info(f"✅ {source}: {len(parent_chunks)} parents, {doc_children} children, {doc_time:.1f}s")

    log.info(f"Total parents: {len(parent_store)}")
    log.info(f"Total children: {len(all_children)}")

    if not all_children:
        log.error("No children created. Nothing to upload.")
        return parent_store, available_docs

    # Clear old vectors
    pc = Pinecone()
    index = pc.Index(INDEX_NAME)
    index.delete(delete_all=True)
    log.info("Cleared old vectors from Pinecone")

    # Async upload
    log.info("Uploading to Pinecone...")
    upload_start = time.time()

    BATCH_SIZE = 100
    batches = [all_children[i:i + BATCH_SIZE] for i in range(0, len(all_children), BATCH_SIZE)]

    async def upload_batch(batch, batch_num):
        batch_start = time.time()
        await PineconeVectorStore.afrom_documents(
            batch,
            embedding,
            index_name=INDEX_NAME
        )
        batch_time = time.time() - batch_start
        log.debug(f"Batch {batch_num + 1}/{len(batches)}: {len(batch)} chunks in {batch_time:.1f}s")

    CONCURRENT_LIMIT = 5
    for i in range(0, len(batches), CONCURRENT_LIMIT):
        concurrent_batches = batches[i:i + CONCURRENT_LIMIT]
        tasks = [
            upload_batch(batch, i + j)
            for j, batch in enumerate(concurrent_batches)
        ]
        await asyncio.gather(*tasks)

    upload_time = time.time() - upload_start
    total_time = time.time() - start_time
    log.info(f"Upload complete: {len(all_children)} chunks in {upload_time:.1f}s")
    log.info(f"Total ingest time: {total_time:.1f}s")

    # Save parent store
    with open("parent_store.json", "w") as f:
        json.dump(parent_store, f)
    log.info(f"Saved parent_store.json ({len(parent_store)} parents)")

    # Log summary stats
    sizes = [len(c.page_content) for c in all_children]
    log.info(f"Chunk stats: min={min(sizes)}, max={max(sizes)}, avg={sum(sizes)//len(sizes)}, median={sorted(sizes)[len(sizes)//2]}")

    return parent_store, available_docs


# _______ Chat _______

async def chat(parent_store):
    log.info(f"Starting chat with {len(parent_store)} parents")

    vectorstore = PineconeVectorStore.from_existing_index(
        index_name=INDEX_NAME,
        embedding=embedding
    )

    # ── Prompts ──
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

    # ── Chains ──
    reformulation_chain = reformulation_prompt | llm | StrOutputParser()
    answer_chain = answer_prompt | llm | StrOutputParser()
    summary_chain = summary_prompt | llm | StrOutputParser()

    # ── Memory ──
    summary = ""
    recent_messages = []
    turn_count = 0

    print("\n✅ Document Assistant Ready")
    print("Commands: 'quit' to exit, 'clear' to reset memory, 'debug' to see memory\n")

    while True:
        query = input("Human: ")

        if not query.strip():
            continue
        if query.lower() in ["quit", "exit", "q"]:
            log.info(f"Chat ended after {turn_count} turns")
            break
        if query.lower() == "clear":
            summary = ""
            recent_messages = []
            turn_count = 0
            log.info("Memory cleared by user")
            print("🗑️ Memory cleared.\n")
            continue
        if query.lower() == "debug":
            print(f"\nSummary: {summary or '(empty)'}")
            print(f"Recent: {len(recent_messages)} messages")
            for msg in recent_messages:
                print(f"  {msg['role']}: {msg['content'][:80]}...")
            print()
            continue

        turn_count += 1
        turn_start = time.time()

        log.info(f"Turn {turn_count}: \"{query[:80]}\"")

        # ── Format recent messages ──
        recent_str = ""
        if recent_messages:
            recent_str = "\n".join(
                f"{'Human' if m['role'] == 'human' else 'AI'}: {m['content']}"
                for m in recent_messages
            )

        # ── Step 1: Reformulate ──
        reform_start = time.time()
        if summary or recent_messages:
            search_query = await reformulation_chain.ainvoke({
                "question": query,
                "summary": summary or "No previous conversation.",
                "recent_messages": recent_str or "No recent messages.",
            })
        else:
            search_query = query
        reform_time = time.time() - reform_start
        log.debug(f"Reformulated in {reform_time:.2f}s: \"{search_query[:80]}\"")

        # ── Step 2: Search children ──
        search_start = time.time()
        child_results = vectorstore.similarity_search(search_query, k=10)
        search_time = time.time() - search_start
        log.debug(f"Search returned {len(child_results)} children in {search_time:.2f}s")

        # ── Step 3: Get parents ──
        parent_ids = []
        seen_pids = set()
        for child in child_results:
            pid = child.metadata.get("parent_id")
            if pid and pid not in seen_pids:
                parent_ids.append(pid)
                seen_pids.add(pid)

        parent_texts = []
        missing_parents = 0
        for pid in parent_ids:
            if pid in parent_store:
                parent_texts.append(parent_store[pid]["content"])
            else:
                missing_parents += 1
                log.warning(f"Parent {pid[:8]} not found in parent_store")

        if missing_parents:
            log.warning(f"{missing_parents} parents not found in store")

        context = "\n\n---\n\n".join(parent_texts) if parent_texts else "No relevant context found."
        context_tokens = len(context) // 4  # rough estimate

        log.debug(f"Context: {len(parent_texts)} parents, ~{context_tokens} tokens")

        # ── Step 4: Generate answer ──
        answer_start = time.time()
        answer = await answer_chain.ainvoke({
            "context": context,
            "question": query,
            "summary": summary or "No previous conversation.",
            "recent_messages": recent_str or "No recent messages.",
        })
        answer_time = time.time() - answer_start
        log.debug(f"Answer generated in {answer_time:.2f}s ({len(answer)} chars)")

        # ── Step 5: Display ──
        total_time = time.time() - turn_start
        print(f"\nAI: {answer}")
        print(f"  🔍 Searched: \"{search_query}\"")
        print(f"  📄 Parents: {len(parent_texts)} | ⏱️ {total_time:.1f}s")

        # ── Step 6: Update memory ──
        recent_messages.append({"role": "human", "content": query})
        recent_messages.append({"role": "ai", "content": answer})

        # ── Step 7: Summarize if needed ──
        if len(recent_messages) > MAX_RECENT_PAIRS * 2:
            summarize_start = time.time()

            to_summarize = recent_messages[:-(MAX_RECENT_PAIRS * 2)]
            to_keep = recent_messages[-(MAX_RECENT_PAIRS * 2):]

            new_messages_str = "\n".join(
                f"{'Human' if m['role'] == 'human' else 'AI'}: {m['content']}"
                for m in to_summarize
            )

            summary = await summary_chain.ainvoke({
                "old_summary": summary or "No previous summary.",
                "new_messages": new_messages_str,
            })

            recent_messages = to_keep
            summarize_time = time.time() - summarize_start
            log.info(f"Memory summarized in {summarize_time:.2f}s. Summary: {len(summary)} chars. Recent: {len(recent_messages)} msgs.")
            print(f"  📝 Memory summarized.")

        # ── Log turn summary ──
        log.info(f"Turn {turn_count} complete: reform={reform_time:.2f}s search={search_time:.2f}s answer={answer_time:.2f}s total={total_time:.2f}s parents={len(parent_texts)}")

        print()


# _______ Main _______

if __name__ == "__main__":
    with open("parent_store.json", "r") as f:
                parent_store = json.load(f)
    print(f"📂 Loaded {len(parent_store)} parents")
    asyncio.run(chat(parent_store))