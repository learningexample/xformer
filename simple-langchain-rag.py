import os
import requests
from tqdm import tqdm
import chromadb
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import LlamaCpp
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA

# Step 1: Define Model Path and URL
MODEL_DIR = "models"
MODEL_FILENAME = "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_FILENAME)
MODEL_URL = "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"

# Step 2: Download Model If Missing
def download_model():
    os.makedirs(MODEL_DIR, exist_ok=True)  # Ensure the directory exists
    print(f" Downloading {MODEL_FILENAME} (~800MB)...")

    response = requests.get(MODEL_URL, stream=True)
    total_size = int(response.headers.get("content-length", 0))

    with open(MODEL_PATH, "wb") as file, tqdm(
        desc="Downloading",
        total=total_size,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1MB chunks
            if chunk:
                file.write(chunk)
                bar.update(len(chunk))

    print(" Model downloaded successfully!")

# Check if the model exists, otherwise download it
if not os.path.exists(MODEL_PATH):
    download_model()

# Step 3: Load and Process All PDFs from "contents/" Folder
pdf_folder = "contents"
all_documents = []

for filename in os.listdir(pdf_folder):
    if filename.endswith(".pdf"):
        pdf_path = os.path.join(pdf_folder, filename)
        print(f" Processing {filename}...")
        loader = PyPDFLoader(pdf_path)
        all_documents.extend(loader.load())

# Step 4: Split Text into Chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
docs = text_splitter.split_documents(all_documents)

# Step 5: Create Embeddings (Using a Small Model)
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Step 6: Store in Local Vector Database (ChromaDB)
db = Chroma.from_documents(docs, embedding=embedding_model, persist_directory="chroma_db")
db.persist()

#  Step 7: Load the TinyLlama Model
print(f" Loading model from: {MODEL_PATH}")
llm = LlamaCpp(model_path=MODEL_PATH, n_ctx=2048, temperature=0.5, verbose=True)

# Step 8: Create Retrieval-Based Q&A Chain
retriever = db.as_retriever()
qa_chain = RetrievalQA.from_chain_type(llm, retriever=retriever)

# Step 9: Ask a Question
question = "What are the key points in the documents?"
response = qa_chain.run(question)

#  Step 10: Print the Answer
print("\n💡 Answer:\n", response)
