from langgraph.graph import StateGraph
from openai import OpenAI
import os
from rag.retriever import retrieve

llm = OpenAI(api_key=os.getenv("GROQ_API_KEY"),
             base_url="https://api.groq.com/openai/v1")

def retrieve_node(state):
    q = state["question"]
    docs = retrieve(q)
    return {"question": q, "docs": docs}

def draft(state):
    q = state["question"]
    docs = state["docs"]

    context = ""
    for i, d in enumerate(docs):
        context += f"[{i+1}] {d['content']}\n"

    prompt = f"""
Use only this context to answer.

Context:
{context}

Question:
{q}

Answer with citations like [1], [2].
"""

    res = llm.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role":"user","content":prompt}]
    )

    return {**state, "draft": res.choices[0].message.content}

def cite(state):
    sources = []
    for i, d in enumerate(state["docs"]):
        sources.append(f"[{i+1}] {d['source_file']} pages {d['pages']}")

    return {**state, "citations": sources}

def final(state):
    return {
        "final": state["draft"] + "\n\nSources:\n" + "\n".join(state["citations"])
    }

graph = StateGraph(dict)
graph.add_node("retrieve", retrieve_node)
graph.add_node("draft", draft)
graph.add_node("cite", cite)
graph.add_node("final", final)

graph.set_entry_point("retrieve")
graph.add_edge("retrieve", "draft")
graph.add_edge("draft", "cite")
graph.add_edge("cite", "final")

app = graph.compile()
