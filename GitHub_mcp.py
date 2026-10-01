#!/usr/bin/env python3
# github_mcp.py - minimal GitHub MCP server (FastMCP + requests)
# tools: whoami, list_repos, list_files, read_file, write_file, search_code, list_issues
import os
import base64
import requests
from fastmcp import FastMCP

TOKEN = os.environ.get("GITHUB_TOKEN", "").strip()
API = "https://api.github.com"
HEADERS = {
    "Authorization": "Bearer " + TOKEN,
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "littlehouse-github-mcp",
}

mcp = FastMCP("github")

def _call(method, path, **kw):
    url = path if path.startswith("http") else API + path
    try:
        r = requests.request(method, url, headers=HEADERS, timeout=30, **kw)
    except Exception as e:
        return {"ok": False, "error": "network: " + str(e)}
    if r.status_code >= 400:
        return {"ok": False, "status": r.status_code, "error": r.text[:500]}
    ctype = r.headers.get("Content-Type", "")
    if "application/json" in ctype:
        return {"ok": True, "data": r.json()}
    return {"ok": True, "data": r.text[:2000]}

@mcp.tool()
def whoami():
    "Show the GitHub account that owns the token."
    return _call("GET", "/user")

@mcp.tool()
def list_repos(limit: int = 20):
    "List repos of the token owner, newest updated first."
    return _call("GET", "/user/repos?per_page=" + str(limit) + "&sort=updated")

@mcp.tool()
def list_files(repo: str, path: str = ""):
    "List files under a path. repo looks like owner/name."
    return _call("GET", "/repos/" + repo + "/contents/" + path)

@mcp.tool()
def read_file(repo: str, path: str, ref: str = ""):
    "Read a text file from a repo and return decoded content."
    q = ("?ref=" + ref) if ref else ""
    r = _call("GET", "/repos/" + repo + "/contents/" + path + q)
    if not r.get("ok"):
        return r
    d = r["data"]
    if isinstance(d, dict) and d.get("content"):
        try:
            txt = base64.b64decode(d["content"]).decode("utf-8", "replace")
        except Exception as e:
            txt = "<decode error: " + str(e) + ">"
        return {"ok": True, "path": d.get("path"), "sha": d.get("sha"),
                "size": d.get("size"), "content": txt}
    return r

@mcp.tool()
def write_file(repo: str, path: str, content: str, message: str, branch: str = "", sha: str = ""):
    "Create or update a file. Pass sha when updating an existing file."
    body = {"message": message,
            "content": base64.b64encode(content.encode("utf-8")).decode("ascii")}
    if branch:
        body["branch"] = branch
    if sha:
        body["sha"] = sha
    return _call("PUT", "/repos/" + repo + "/contents/" + path, json=body)

@mcp.tool()
def search_code(q: str):
    "Search code across GitHub."
    return _call("GET", "/search/code?q=" + q)

@mcp.tool()
def list_issues(repo: str, state: str = "open"):
    "List issues of a repo."
    return _call("GET", "/repos/" + repo + "/issues?state=" + state)

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8010)
