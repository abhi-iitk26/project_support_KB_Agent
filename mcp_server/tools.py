import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from rag.retriever import retrieve

def search_docs(query: str):
    return retrieve(query)
