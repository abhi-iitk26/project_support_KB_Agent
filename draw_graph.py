from graph.agent_graph import app

graph = app.get_graph()

# Generate PNG bytes
png_bytes = graph.draw_mermaid_png()

# Save to file
with open("support_kb_architecture.png", "wb") as f:
    f.write(png_bytes)

print("Graph saved as support_kb_architecture.png")
