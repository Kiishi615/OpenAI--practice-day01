from PyPDF2 import PdfReader
from pathlib import Path

count_pdf = 0
count_txt = 0
pdfs = {}
txts = {}
folder = Path('documents')
documents = list(folder.iterdir())

# print(len(documents))

for doc in documents:

    if doc.suffix.lower() == ".pdf":
        count_pdf +=1
        pdfs[f"pdf_{count_pdf}"]= PdfReader(doc)
        # print(f"\n {pdfs}")
    if doc.suffix == ".txt":
        count_txt +=1
        with open(doc, encoding="utf-8") as f:
            txts[f"txt_{count_txt}"] = f.read()

for txt in txts:
    print(txt)
