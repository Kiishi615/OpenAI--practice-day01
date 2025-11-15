from pathlib import Path
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

# with open("Sample Documents/Stars_Explode.txt", "r") as f:
#     text=f.read()

folder=Path('Sample Documents')
file='Stars_Explode.txt'
file_location=folder/file
text =file_location.read_text()

split=split_into_chunks(text)
print(split)


# print(os.path.exists(r"Sample Documents/Stars_Explode.txt"))