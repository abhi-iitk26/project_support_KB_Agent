from fastmcp import FastMCP
from tools import search_docs

mcp = FastMCP("Support KB Agent")

@mcp.tool()
def search(query: str):
    return search_docs(query)

if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=3333)