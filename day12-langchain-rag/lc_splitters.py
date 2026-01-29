from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter, CharacterTextSplitter, TokenTextSplitter

loader = PyPDFLoader("./docs/12mb.pdf")
doc = loader.load()


# print(doc[0].page_content[:100])

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 1000,
    chunk_overlap = 100,
    add_start_index = True
)

chunks1 = text_splitter.split_documents(doc)

print(f"RecursiveCharacterTextSplitter:  {chunks1[0].page_content}\n\n")


text_splitter = CharacterTextSplitter(
    separator= "\n\n",
    chunk_size = 1000,
    chunk_overlap = 100,
    length_function = len
)

chunks2 = text_splitter.split_documents(doc)
print(f"CharacterTextSplitter:  {chunks2[0].page_content}\n\n")

text_splitter = TokenTextSplitter(
    chunk_size = 1000,
    chunk_overlap = 100
)

chunks3 = text_splitter.split_documents(doc)
print(f"TokenTextSplitter:  {chunks3[0].page_content}\n\n")

