import chromadb
import os, numpy as np
import seaborn as sns, matplotlib.pyplot as plt
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from chromadb.api.types import EmbeddingFunction
from shared import text_handler, paragraph_chunks, sentence_chunks, overlap_chunks
from dotenv import load_dotenv

def similarity_heatmap(texts:str, collection, labels =None)->None:
    if labels is None:
        labels = [f"Text {i+1}" for i in range (len(texts))]

    embeddings = collection._embedding_function(texts)
    embeddings = np.array(embeddings)

    norm = np.linalg.norm(embeddings,axis=1,keepdims=True)
    similarity_matrix = np.dot(embeddings,embeddings.T)/ (norm * norm.T)

    plt.figure(figsize=(8,6))
    sns.heatmap(
        similarity_matrix,
        annot=True,
        cmap="Blues",
        xticklabels=labels,
        yticklabels=labels,
        fmt=".3f"
        cbar_kws={'label': 'Cosine Similarity'}
    )
    plt.title("Text Similarity Matrix")
    plt.tight_layout()
    plt.show()