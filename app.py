from flask import Flask, request, jsonify
import json, os, datetime

app = Flask(__name__)
BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "messages.json")
STICKER_DIR = os.path.join(BASE, "static", "stickers")
STICKERS_JSON = os.path.join(STICKER_DIR, "stickers.json")
MOOD_FILE = os.path.join(BASE, "mood.json")

os.makedirs(STICKER_DIR, exist_ok=True)

def load_msgs():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_msg(msg):
    msgs = load_msgs()
    msgs.append({"time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "text": msg})
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(msgs, f, ensure_ascii=False, indent=2)

def load_moods():
    if os.path.exists(MOOD_FILE):
        with open(MOOD_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

@app.route("/")
def home():
    return open(os.path.join(BASE, "index.html"), encoding="utf-8").read()

@app.route("/save")
def save():
    msg = request.args.get("msg", "")
    if msg:
        save_msg(msg)
        return "ok"
    return "empty"

@app.route("/messages")
def messages():
    return jsonify(load_msgs())

@app.route("/stickers")
def stickers():
    if os.path.exists(STICKERS_JSON):
        with open(STICKERS_JSON, "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    files = [f for f in os.listdir(STICKER_DIR) if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp")) and f != "stickers.json"]
    return jsonify(files)

@app.route("/upload", methods=["POST"])
def upload():
    f = request.files.get("file")
    if not f or f.filename == "":
        return "no file", 400
    tag = request.form.get("tag", "")
    f.save(os.path.join(STICKER_DIR, f.filename))
    data = []
    if os.path.exists(STICKERS_JSON):
        with open(STICKERS_JSON, "r", encoding="utf-8") as jf:
            data = json.load(jf)
    data.append({"file": f.filename, "tag": tag})
    with open(STICKERS_JSON, "w", encoding="utf-8") as jf:
        json.dump(data, jf, ensure_ascii=False, indent=2)
    return "ok"

@app.route("/delete_sticker")
def delete_sticker():
    name = request.args.get("file", "")
    if not name:
        return "empty", 400
    fp = os.path.join(STICKER_DIR, name)
    if os.path.exists(fp):
        os.remove(fp)
    if os.path.exists(STICKERS_JSON):
        with open(STICKERS_JSON, "r", encoding="utf-8") as jf:
            data = json.load(jf)
        data = [d for d in data if d.get("file") != name]
        with open(STICKERS_JSON, "w", encoding="utf-8") as jf:
            json.dump(data, jf, ensure_ascii=False, indent=2)
    return "ok"

@app.route("/mood")
def mood():
    return jsonify(load_moods())

@app.route("/mood_set")
def mood_set():
    date = request.args.get("date", "")
    me = request.args.get("me", "")
    qz = request.args.get("qz", "")
    moods = load_moods()
    if date not in moods:
        moods[date] = {}
    if me:
        moods[date]["me"] = me
    if qz:
        moods[date]["qz"] = qz
    with open(MOOD_FILE, "w", encoding="utf-8") as f:
        json.dump(moods, f, ensure_ascii=False, indent=2)
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
