import json
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# ---------------------------------------
# CONFIG
# ---------------------------------------

CHUNKS_FILE = "data/semantic_chunks.json"
CHROMA_PATH = "./chroma_db" 
COLLECTION_NAME = "ml_book_kb"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# ---------------------------------------
# Load semantic chunks
# ---------------------------------------

print("📥 Loading semantic chunks...")
with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
    chunks = json.load(f)

print(f"   Loaded {len(chunks)} chunks")

# ---------------------------------------
# Load embedding model
# ---------------------------------------

print("🧠 Loading MiniLM model...")
model = SentenceTransformer(MODEL_NAME)

# ---------------------------------------
# Initialize ChromaDB (PERSISTENT)
# ---------------------------------------

print("📦 Initializing ChromaDB (persistent)...")

client = chromadb.Client(
    Settings(
        persist_directory=CHROMA_PATH,
        is_persistent=True,          # 🔥 CRITICAL FIX
        anonymized_telemetry=False,
    )
)

# ---------------------------------------
# Recreate collection
# ---------------------------------------

try:
    client.delete_collection(COLLECTION_NAME)
    print("♻️ Old collection removed")
except:
    pass

collection = client.create_collection(name=COLLECTION_NAME)

# ---------------------------------------
# Prepare documents + metadata
# ---------------------------------------

documents = []
metadatas = []
ids = []

for i, chunk in enumerate(chunks):
    documents.append(chunk["content"])

    meta = chunk["metadata"].copy()

    # Chroma does NOT allow lists
    if "pages" in meta and isinstance(meta["pages"], list):
        meta["pages"] = ",".join(str(p) for p in meta["pages"])

    metadatas.append(meta)
    ids.append(f"chunk_{i}")

# ---------------------------------------
# Create embeddings
# ---------------------------------------

print("🔢 Creating embeddings...")
embeddings = model.encode(documents, show_progress_bar=True)

# ---------------------------------------
# Store in Chroma
# ---------------------------------------

print("📤 Storing in ChromaDB...")
collection.add(
    documents=documents,
    embeddings=embeddings.tolist(),
    metadatas=metadatas,
    ids=ids,
)

print(f"✅ Stored {len(documents)} chunks in ChromaDB")

# ---------------------------------------
# Inspect stored vectors
# ---------------------------------------

print("\n🔍 Inspecting stored vectors...")

stored = collection.get(include=["documents", "metadatas"])

print(f"Total vectors in DB: {len(stored['documents'])}\n")

for i in range(3):
    print("---------------")
    print("ID:", stored["ids"][i])
    print("CHAPTER:", stored["metadatas"][i]["chapter"])
    print("PAGES:", stored["metadatas"][i]["pages"])
    print("FILENAME:", stored["metadatas"][i]["filename"])
    print("TEXT:", stored["documents"][i][:200], "...")
