from graph.agent_graph import app

# Extract full compiled LangGraph
graph = app.get_graph()

# Print nodes and edges (for README)
print("\nNodes:")
for n in graph.nodes:
    print(" -", n)

print("\nEdges:")
for e in graph.edges:
    print(f" {e[0]} → {e[1]}")

# Generate PNG
png_bytes = graph.draw_mermaid_png()

with open("support_kb_langgraph.png", "wb") as f:
    f.write(png_bytes)

print("\nSaved: support_kb_langgraph.png")
