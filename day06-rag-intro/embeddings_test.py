import openai
import numpy as np
import os
from dotenv import load_dotenv

load_dotenv()

client= openai.Client(api_key=os.getenv('OPENAI_API_KEY'))

def get_embedding(text):
    response=client.embeddings.create(
        model="text-embedding-3-small",
        input=text
)
    return response.data[0].embedding

# text1 = "I love pizza"
# text2 = "I adore pizza"
# text3 = "The weather is nice"

# emb1= get_embedding(text1)
# emb2= get_embedding(text2)
# emb3= get_embedding(text3)

# emb1=np.array(emb1)
# emb2=np.array(emb2)
# emb3=np.array(emb3)


# def cosine_similarity(a,b):
#     return np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b))

# print(f"'{text1}' vs '{text2}': {cosine_similarity(emb1, emb2):.3f}")  # High similarity
# print(f"'{text1}' vs '{text3}': {cosine_similarity(emb1, emb3):.3f}")