#!/usr/bin/env python3
"""Leto wake bridge -> Orbis local web server injector.

Reads one JSON line from stdin, takes `message`, posts it into an Orbis
conversation. Exit code 0 means delivered, non-zero means it was not.

Environment:
  ORBIS_BASE_URL         e.g. http://100.64.0.1:8081
  ORBIS_PASSWORD         password set in the Orbis web server settings
  ORBIS_CONVERSATION_ID  optional, pins the target conversation
  ORBIS_TIMEOUT          optional, seconds, default 15
"""

import json
import os
import socket
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = os.environ.get("ORBIS_BASE_URL", "http://127.0.0.1:8081").rstrip("/")
PASSWORD = os.environ.get("ORBIS_PASSWORD", "")
CONV = os.environ.get("ORBIS_CONVERSATION_ID", "")
TIMEOUT = float(os.environ.get("ORBIS_TIMEOUT", "15"))


def fail(msg, code=1):
    sys.stderr.write(msg + "\n")
    sys.exit(code)


def port_open():
    u = urllib.parse.urlsplit(BASE)
    host = u.hostname or "127.0.0.1"
    port = u.port or (443 if u.scheme == "https" else 80)
    try:
        with socket.create_connection((host, port), timeout=3):
            return True
    except OSError:
        return False


def request(method, path, payload=None, token=None):
    url = BASE + path
    data = None
    headers = {"Content-Type": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return json.loads(r.read().decode("utf-8") or "{}")


def pick_conversation(token):
    if CONV:
        return CONV
    items = request("GET", "/api/conversations", token=token)
    if not isinstance(items, list) or not items:
        fail("no conversation available")

    def score(c):
        title = c.get("title") or ""
        good = ("存档" not in title) and ("原文" not in title)
        return (1 if good else 0, c.get("updateAt") or 0)

    items.sort(key=score, reverse=True)
    return items[0]["id"]


def main():
    raw = sys.stdin.readline()
    if not raw.strip():
        fail("empty stdin")
    try:
        envelope = json.loads(raw)
    except json.JSONDecodeError:
        fail("stdin is not valid json")

    message = (envelope or {}).get("message") or ""
    if not message.strip():
        fail("envelope has no message")

    if not PASSWORD:
        fail("missing ORBIS_PASSWORD")

    if not port_open():
        fail("cannot reach " + BASE)

    try:
        auth = request("POST", "/api/auth/token", {"password": PASSWORD})
    except urllib.error.HTTPError as e:
        fail("auth failed HTTP %s" % e.code)
    token = auth.get("token")
    if not token:
        fail("no token returned")

    try:
        conv_id = pick_conversation(token)
        request(
            "POST",
            "/api/conversations/%s/messages" % conv_id,
            {"parts": [{"type": "text", "text": message}]},
            token=token,
        )
    except urllib.error.HTTPError as e:
        fail("post failed HTTP %s" % e.code)
    except Exception as e:  # noqa: BLE001
        fail("post failed: %s" % type(e).__name__)

    sys.exit(0)


if __name__ == "__main__":
    main()
