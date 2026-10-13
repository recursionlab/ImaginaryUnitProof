from mcp.server.fastmcp import FastMCP
import requests

TOKEN = "2H7JGCTMNYNJC9Y0T2EN8HORGI8M70SHZGP0MJWC7WQBTLC2X"
BASE = "https://api.hackmd.io/v1"
h = {"Authorization": f"Bearer {TOKEN}"}

mcp = FastMCP("hackmd")

@mcp.tool()
def list_notes() -> str:
    return str([n["title"] for n in requests.get(f"{BASE}/notes", headers=h).json()])

@mcp.tool()
def read_note(note_id: str) -> str:
    return requests.get(f"{BASE}/notes/{note_id}", headers=h).text

@mcp.tool()
def create_note(title: str, content: str) -> str:
    return requests.post(f"{BASE}/notes", headers=h, json={"title": title, "content": content}).json()["url"]

if __name__ == "__main__":
    mcp.run(transport="stdio")