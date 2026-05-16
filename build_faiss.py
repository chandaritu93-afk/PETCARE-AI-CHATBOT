import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ragcore import load_pdfs
from ragcore  import create_faiss_index

PDF_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "pdfs")

print("Loading PDFs...")

chunks = load_pdfs(PDF_FOLDER)

if chunks:
    print(f"Found {len(chunks)} chunks")
    create_faiss_index(chunks)
    print("DONE!")
else:
    print("No PDFs found in data/pdfs folder")