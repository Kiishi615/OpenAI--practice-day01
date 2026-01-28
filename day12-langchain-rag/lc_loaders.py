from langchain_community.document_loaders import TextLoader, PyPDFLoader, CSVLoader

loader = PyPDFLoader("./docs/1mb.pdf")
doc = loader.load()

print(doc[0].page_content[:100])


