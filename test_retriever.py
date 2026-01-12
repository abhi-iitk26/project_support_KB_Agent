from rag.retriever import retrieve

res = retrieve("refund policy")
for r in res:
    print("----")
    print(r["content"][:200])
