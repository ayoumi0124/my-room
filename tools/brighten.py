#!/usr/bin/env python3
# qb.png 亮度三档 · 纯标准库（不依赖 ImageMagick / Pillow）
# 用法: python3 brighten.py [源文件] [输出前缀]
import sys, zlib, struct

SRC = sys.argv[1] if len(sys.argv) > 1 else "/home/admin/room/static/tiles/qb.png"
PRE = sys.argv[2] if len(sys.argv) > 2 else SRC[:-4]

def read_png(path):
    d = open(path, "rb").read()
    if d[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit("不是 PNG 文件: " + path)
    i, w, h, bd, ct, idat = 8, 0, 0, 0, 0, b""
    while i < len(d):
        ln = struct.unpack(">I", d[i:i+4])[0]
        typ = d[i+4:i+8]
        data = d[i+8:i+8+ln]
        if typ == b"IHDR":
            w, h, bd, ct = struct.unpack(">IIBB", data[:10])
        elif typ == b"IDAT":
            idat += data
        elif typ == b"IEND":
            break
        i += 12 + ln
    if bd != 8 or ct != 6:
        raise SystemExit("只支持 8bit RGBA（这张是 bitdepth=%d colortype=%d）" % (bd, ct))
    raw = zlib.decompress(idat)
    stride = w * 4
    out = bytearray(h * stride)
    prev = bytearray(stride)
    pos = 0
    for y in range(h):
        ft = raw[pos]; pos += 1
        line = bytearray(raw[pos:pos + stride]); pos += stride
        if ft == 1:
            for x in range(4, stride):
                line[x] = (line[x] + line[x - 4]) & 255
        elif ft == 2:
            for x in range(stride):
                line[x] = (line[x] + prev[x]) & 255
        elif ft == 3:
            for x in range(stride):
                a = line[x - 4] if x >= 4 else 0
                line[x] = (line[x] + ((a + prev[x]) >> 1)) & 255
        elif ft == 4:
            for x in range(stride):
                a = line[x - 4] if x >= 4 else 0
                b = prev[x]
                c = prev[x - 4] if x >= 4 else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[x] = (line[x] + pr) & 255
        out[y * stride:(y + 1) * stride] = line
        prev = line
    return w, h, out

def write_png(path, w, h, px):
    stride = w * 4
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        raw += px[y * stride:(y + 1) * stride]
    def chunk(t, dd):
        return (struct.pack(">I", len(dd)) + t + dd +
                struct.pack(">I", zlib.crc32(t + dd) & 0xffffffff))
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)
    body = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) +
            chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b""))
    open(path, "wb").write(body)

w, h, px = read_png(SRC)
print("源图 %d x %d" % (w, h))
for tag, gain in (("20", 1.20), ("35", 1.35), ("50", 1.50)):
    buf = bytearray(px)
    for i in range(0, len(buf), 4):
        for k in range(3):
            v = int(buf[i + k] * gain)
            buf[i + k] = 255 if v > 255 else v
    p = "%s_+%s.png" % (PRE, tag)
    write_png(p, w, h, buf)
    print("写出 " + p)
print("好了。浏览器打开 /static/tiles/ 下面那三张，挑一张。")
