from graph.react_graph import app

while True:
    q = input("\nAsk ReAct Agent (type 'quit'): ")
    if q.lower() == "quit":
        break

    result = app.invoke({"question": q})
    print("\n", result["final"])
