from pathlib import Path


def split_into_chunks(text, chunk_size=100):
    #Split text into word-based chunks for vector embeddings


    words=text.split()
    chunks=[]
    current_chunk= []

    for word in words:
        current_chunk.append(word)
        if len(current_chunk)==chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk=[]
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks

def text_handler(file_path):
    try:
        with open(f"{file_path}", "r", encoding="utf-8") as f:
            text=f.read()
        return text
    except FileNotFoundError:
        print(f"File not in '{file_path}'")
        
    except Exception as e:
        print(f"Some Error occured: {e}")
        

if __name__=="__main__":
    print(text_handler("Stars_Explode.txt"))

    folder=Path('Sample Documents')
    file='Stars_Explode.txt'
    file_path=folder/file
    text =text_handler(file_path)

    split=split_into_chunks(text)
    print(split)


    # print(os.path.exists(r"Sample Documents/Stars_Explode.txt"))