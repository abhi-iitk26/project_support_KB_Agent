from graph.agent_graph import app

while True:
    q = input("Ask Support KB: ")
    if q.lower() == "quit":
        break

    out = app.invoke({"question": q})
    print(out["final"])
