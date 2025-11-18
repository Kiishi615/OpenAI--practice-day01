import chromadb
from sentence_transformers import SentenceTransformer


model=SentenceTransformer('all-MiniLM-L6-v2')

sentences=[
    "The dog barked loudly",
    "The puppy made noise", 
    "I love pizza",
    "The cat meowed"

]

embeddings=model.encode(sentences)

print(f"Each sentence becomes {len(embeddings[0])} numbers")
print(f"First few numbers for 'The dog barked loudly': {embeddings[0][:5]}")