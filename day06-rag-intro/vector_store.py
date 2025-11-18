import chromadb
from split_text import *

client=chromadb.Client()


collection= client.create_collection(name="Rand_text")
text=Text_handler("Stars_Explode.txt")
chunks=split_into_chunks(text)


collection.add(
    documents= chunks,
    ids=[f"chunk_{i}" for i in range(len(chunks))]
    
)

results=collection.query(
    query_texts=["How do trigger a supernovae?"],
    n_results=1
)

print("Found chunks:",results['documents'])

