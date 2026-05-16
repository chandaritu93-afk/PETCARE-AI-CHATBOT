import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import re

def load_pdfs(folder):
    if not os.path.exists(folder):
        print(f"Folder not found: {folder}")
        return []

    documents = []

    for file in os.listdir(folder):
        if file.endswith(".pdf"):
            filepath = os.path.join(folder, file)
            try:
                loader = PyPDFLoader(filepath)
                docs = loader.load()
                documents.extend(docs)
                print(f"Loaded: {file} ({len(docs)} pages)")
            except Exception as e:
                print(f"Error loading {file}: {e}")

    if not documents:
        print("No PDFs found!")
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=200,
    )

    chunks = splitter.split_documents(documents)
    print(f"Total chunks: {len(chunks)}")

    return chunks
import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(model_name="NeuML/pubmedbert-base-embeddings")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FAISS_DIR = os.path.join(BASE_DIR, "..", "faiss_index")


def create_faiss_index(documents):
    if not documents:
        return None

    db = FAISS.from_documents(documents, embeddings)
    os.makedirs(FAISS_DIR, exist_ok=True)
    db.save_local(FAISS_DIR)
    print("FAISS index saved!")
    return db
import os
import pdfplumber

def read_all_pdfs(folder_path):
    import os
    import pdfplumber

    all_text = ""

    for file in os.listdir(folder_path):
        if file.endswith(".pdf"):
            pdf_path = os.path.join(folder_path, file)

            try:
                with pdfplumber.open(pdf_path) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            all_text += text + "\n"
            except:
                print(f"Skipped {file}")

    return all_text
from typing import List
import requests

# 🔹 TEXT CHUNKING
def chunk_text(text: str, chunk_size: int = 500) -> List[str]:
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

# 🔹 REMOVE DUPLICATES
def remove_duplicates(chunks: List[str]) -> List[str]:
    return list(set(chunks))

# 🔹 THRESHOLD FILTER
def filter_chunks(chunks, min_length=50):
    return [str(c) for c in chunks if len(str(c)) > min_length]
if os.path.exists(FAISS_DIR):
    db = FAISS.load_local(FAISS_DIR, embeddings, allow_dangerous_deserialization=True)
    print("FAISS loaded")
else:
    db = None
    print("FAISS not found")
def extract_keywords(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9 ]', '', text)

    stopwords = {
        "the", "is", "are", "a", "an", "of",
        "to", "and", "in", "for", "on"
    }

    words = text.split()

    keywords = [w for w in words if w not in stopwords]

    return keywords


def retrieve_docs(query: str, k: int = 4):
    keywords = extract_keywords(query)
    boosted_query = " ".join(keywords)
    results = []

    # -------- FAISS --------
    if db is not None:

        docs_with_scores = db.similarity_search_with_score(boosted_query, k=10)

        docs = []

        for doc, score in docs_with_scores:
            if score < 0.7:
                docs.append(doc)

        for d in docs:
            src = d.metadata.get("source", "unknown")
            page = d.metadata.get("page", None)
            pdf_name = os.path.basename(src)

            if page is not None:
                citation = f"[{pdf_name}, Page {page + 1}]"
            else:
                citation = f"[{pdf_name}]"

            results.append(d.page_content + "\n" + citation)

    # -------- PUBMED --------
    pubmed = fetch_pubmed(query)
    if pubmed:
        results.append("🧬 PubMed:\n" + pubmed)

    # -------- EUROPE PMC --------
    epmc = fetch_europe_pmc(query)
    if epmc:
        results.append("📄 Europe PMC:\n" + epmc)

    # -------- OPENFDA --------
    fda = fetch_openfda(query)
    if fda:
        results.append("💊 OpenFDA:\n" + fda)

    # -------- REMOVE DUPLICATES --------
    results = list(set(results))

    return results
def fetch_europe_pmc(query):
    try:
        url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={query}&format=json&pageSize=1"
        res = requests.get(url).json()

        result = res["resultList"]["result"][0]
        title = result.get("title", "")
        abstract = result.get("abstractText", "")

        return f"{title}\n{abstract[:200]}"
    except:
        return ""
def fetch_openfda(query):
    try:
        url = f"https://api.fda.gov/drug/label.json?search={query}&limit=1"
        res = requests.get(url).json()

        result = res["results"][0]
        purpose = result.get("purpose", [""])[0]

        return f"Medicine Info: {purpose}"
    except:
        return ""


# -------- PUBMED --------
def fetch_pubmed(query):
    try:
        url = f"https://pubmed.ncbi.nlm.nih.gov/?term={query}"
        return f"Search PubMed: {url}"
    except Exception as e:
        print("PubMed error:", e)
        return ""