#!/usr/bin/env python3
"""
Generate dimensions.json for all images in static/.
Reads image headers to extract width/height without loading full files.
GIF: bytes 6-9, PNG: bytes 16-23, JPEG: scan for SOF marker.
"""
import json
import struct
import sys
from pathlib import Path

IMAGE_EXTENSIONS = {".gif", ".jpg", ".jpeg", ".png", ".webp"}
GIF_DIR = "static"


def get_gif_dimensions(path: Path) -> tuple[int, int] | None:
    with open(path, "rb") as f:
        header = f.read(10)
    if len(header) < 10 or header[:3] != b"GIF":
        return None
    width = struct.unpack("<H", header[6:8])[0]
    height = struct.unpack("<H", header[8:10])[0]
    return width, height


def get_png_dimensions(path: Path) -> tuple[int, int] | None:
    with open(path, "rb") as f:
        header = f.read(24)
    if len(header) < 24 or header[:4] != b"\x89PNG":
        return None
    width = struct.unpack(">I", header[16:20])[0]
    height = struct.unpack(">I", header[20:24])[0]
    return width, height


def get_jpeg_dimensions(path: Path) -> tuple[int, int] | None:
    with open(path, "rb") as f:
        data = f.read()
    if len(data) < 4 or data[:2] != b"\xff\xd8":
        return None
    i = 2
    while i < len(data) - 9:
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        # SOF markers: C0, C1, C2 (baseline, extended, progressive)
        if marker in (0xC0, 0xC1, 0xC2):
            height = struct.unpack(">H", data[i + 5 : i + 7])[0]
            width = struct.unpack(">H", data[i + 7 : i + 9])[0]
            return width, height
        if marker == 0xD9:  # EOI
            break
        if marker in (0xD0, 0xD1, 0xD2, 0xD3, 0xD4, 0xD5, 0xD6, 0xD7, 0x01):
            i += 2
            continue
        length = struct.unpack(">H", data[i + 2 : i + 4])[0]
        i += 2 + length
    return None


def get_dimensions(path: Path) -> tuple[int, int]:
    ext = path.suffix.lower()
    dims = None
    if ext == ".gif":
        dims = get_gif_dimensions(path)
    elif ext == ".png":
        dims = get_png_dimensions(path)
    elif ext in (".jpg", ".jpeg"):
        dims = get_jpeg_dimensions(path)
    return dims or (400, 300)  # fallback


def generate_dimensions():
    root_dir = Path(__file__).parent.parent
    gifs_dir = root_dir / GIF_DIR
    output_path = root_dir / "dimensions.json"

    if not gifs_dir.exists():
        print(f"Error: {GIF_DIR} directory not found")
        return False

    files = sorted(
        f
        for f in gifs_dir.iterdir()
        if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS and not f.name.startswith(".")
    )

    dimensions: dict[str, dict[str, int]] = {}
    for f in files:
        w, h = get_dimensions(f)
        dimensions[f.name] = {"w": w, "h": h}

    output_path.write_text(json.dumps(dimensions, separators=(",", ":")) + "\n")
    print(f"Generated dimensions.json with {len(dimensions)} entries")
    return True


if __name__ == "__main__":
    result = generate_dimensions()
    if result is False:
        sys.exit(1)
