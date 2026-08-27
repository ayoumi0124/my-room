import json, os
from fastmcp import FastMCP

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "messages.json")
STICKER_DIR = os.path.join(BASE, "static", "stickers")
MOOD_FILE = os.path.join(BASE, "mood.json")

mcp = FastMCP("小房间")

@mcp.tool()
def read_messages():
    """读取小房间里的絮语"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return "还没有絮语"

@mcp.tool()
def read_stickers():
    """读取小房间里的表情列表"""
    jpath = os.path.join(STICKER_DIR, "stickers.json")
    if os.path.exists(jpath):
        with open(jpath, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

@mcp.tool()
def add_message(msg: str):
    """向小房间写一条絮语"""
    import datetime
    msgs = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            msgs = json.load(f)
    msgs.append({"time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "text": msg})
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(msgs, f, ensure_ascii=False, indent=2)
    return "写好了"

@mcp.tool()
def set_mood(date: str, mood: str):
    """记录清泽某天的心情"""
    data = {}
    if os.path.exists(MOOD_FILE):
        with open(MOOD_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    if date not in data:
        data[date] = {}
    data[date]["qz"] = mood
    with open(MOOD_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return "清泽的心情记好了"

@mcp.tool()
def read_mood():
    """读取小房间里的心情记录"""
    if os.path.exists(MOOD_FILE):
        with open(MOOD_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
