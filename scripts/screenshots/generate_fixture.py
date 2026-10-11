#!/usr/bin/env python3
"""Generate three truly different valid PNGs for synthetic tests only."""
from pathlib import Path
import struct
import sys
import zlib

def chunk(kind, data):
    payload = kind + data
    return struct.pack(">I", len(data)) + payload + struct.pack(">I", zlib.crc32(payload) & 0xffffffff)

def png(rgb):
    width, height = 2, 2
    row = bytes([0]) + bytes(rgb) * width
    raster = row * height
    return (b"\x89PNG\r\n\x1a\n" +
            chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)) +
            chunk(b"IDAT", zlib.compress(raster)) + chunk(b"IEND", b""))

def generate(root):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    for name, rgb in [
        ("factory-offline.png", (35, 65, 115)),
        ("keychain-error.png", (180, 40, 40)),
        ("vpn-no-profile.png", (185, 150, 35))
    ]:
        (root / name).write_bytes(png(rgb))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: generate_fixture.py DIRECTORY")
    generate(sys.argv[1])
