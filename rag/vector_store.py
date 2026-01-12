import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "ml_book_kb"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Load same embedding model
embedder = SentenceTransformer(MODEL_NAME)

# Connect to persistent Chroma DB
client = chromadb.Client(
    Settings(
        persist_directory=CHROMA_PATH,
        is_persistent=True,
        anonymized_telemetry=False
    )
)

# Load your collection
collection = client.get_collection(COLLECTION_NAME)
