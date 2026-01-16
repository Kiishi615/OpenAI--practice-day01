import chromadb
import os, numpy as np
import seaborn as sns, matplotlib.pyplot as plt
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from chromadb.api.types import EmbeddingFunction
from shared import text_handler, paragraph_chunks, sentence_chunks, overlap_chunks
from dotenv import load_dotenv

load_dotenv()

def initialize_chroma_collection(collection_name:str):
    client=chromadb.Client()
    
    openai_ef: EmbeddingFunction = OpenAIEmbeddingFunction(
    api_key = os.getenv("OPENAI_API_KEY"),
    model_name = "text-embedding-3-small"
)
    collection = client.get_or_create_collection(
        name = collection_name, 
        embedding_function = openai_ef,
    )

    return collection

def ingest_document(file, collection):
    text=text_handler(file)
    chunks=paragraph_chunks(text)
    collection.add(
        documents= chunks,
        ids=[f"chunk_{i}" for i in range(len(chunks))]
    )
    return collection

def check_similarity(text1: str, text2: str, collection)-> float: 
    ef = collection._embedding_function
    embeddings = ef([text1, text2])
    score = np.dot(embeddings[0], embeddings[1]) / (np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1]))
    return score

def similarity_heatmap(texts:str, collection, labels=None) ->None :
    if labels is None:
        labels = [f"Text {i+1}" for i in range(len(texts))]
    
    embeddings = collection._embedding_function(texts)
    embeddings = np.array(embeddings)
    
    # Cosine similarity matrix
    norm = np.linalg.norm(embeddings, axis=1, keepdims=True)
    similarity_matrix = np.dot(embeddings, embeddings.T) / (norm * norm.T)
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(
        similarity_matrix,
        annot=True,
        cmap="Blues",
        xticklabels=labels,
        yticklabels=labels,
        fmt=".3f",
        cbar_kws={'label': 'Cosine Similarity'}
    )
    plt.title("Text Similarity Matrix")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":

    texts = [
        "The cat sat on the mat",
        "A cat is sitting on the rug",
        "Quantum physics is fascinating",
        "The dog chased the ball"
    ]
    collection = initialize_chroma_collection('Kiishi')
    similarity_heatmap(texts, collection, labels=["A", "B", "C", "D"])