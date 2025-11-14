import os
def split_into_chunks(text, chunk_size=100):
    words=text.split()
    chunks=[]
    current_chunk= []

    for word in words:
        current_chunk.append(word)
        if len(current_chunk)>=chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk=[]
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks

with open("Sample Documents/Stars_Explode.txt", "r") as f:
    text=f.read()
split=split_into_chunks(text)
print(split)


# print(os.path.exists(r"Sample Documents/Stars_Explode.txt"))