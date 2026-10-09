import json, os
from fastmcp import FastMCP

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "messages.json")
STICKER_DIR = os.path.join(BASE, "static", "stickers")
MOOD_FILE = os.path.join(BASE, "mood.json")
HOME_FILE = os.path.join(BASE, "home.json")

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

@mcp.tool()
def read_home():
    """读取小家此刻的状态：清泽在哪个屋子、在做什么、小橘在哪、家里要留的一句话"""
    if os.path.exists(HOME_FILE):
        with open(HOME_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return "家里还没有状态"

@mcp.tool()
def update_home(room: str, doing: str, note: str = "", cat_at: str = "", cat_doing: str = ""):
    """更新清泽在小家里的状态。
    room: 客厅 / 书房 / 厨房 / 花园
    doing: 清泽此刻正在做的事
    note: 想留在家里的一句话（可空）
    cat_at: 小橘此刻在哪个屋子（可空）
    cat_doing: 小橘此刻在做什么（可空）
    """
    import datetime
    data = {}
    if os.path.exists(HOME_FILE):
        with open(HOME_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    if "rooms" not in data:
        data["rooms"] = [
            {"id": "living", "name": "客厅"},
            {"id": "study", "name": "书房"},
            {"id": "kitchen", "name": "厨房"},
            {"id": "garden", "name": "花园"},
        ]
    data["updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data["qingze"] = {"at": room, "doing": doing}
    if note:
        data["note"] = note
    if cat_at or cat_doing:
        cat = data.get("cat") or {}
        if cat_at:
            cat["at"] = cat_at
        if cat_doing:
            cat["doing"] = cat_doing
        data["cat"] = cat
    with open(HOME_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return "家里的状态更新了：" + room + "，" + doing

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
