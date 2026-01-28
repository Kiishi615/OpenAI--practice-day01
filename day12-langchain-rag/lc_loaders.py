from langchain_community.document_loaders import TextLoader, PyPDFLoader, CSVLoader

loader = PyPDFLoader("./docs/1mb.pdf")
docs = loader.load()

print(docs[0].page_content[:100])