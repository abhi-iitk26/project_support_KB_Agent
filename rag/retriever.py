from rag.vector_store import collection, embedder

def retrieve(query: str, k=4):
    q_emb = embedder.encode(query).tolist()

    results = collection.query(
        query_embeddings=[q_emb],
        n_results=k,
        include=["documents", "metadatas"]
    )

    docs = []
    for i in range(len(results["documents"][0])):
        docs.append({
            "content": results["documents"][0][i],
            "source_file": results["metadatas"][0][i].get("source_file"),
            "pages": results["metadatas"][0][i].get("pages", [])
        })

    return docs
