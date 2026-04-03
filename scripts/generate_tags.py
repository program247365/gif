#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "openai>=1.0",
#   "pillow>=10.0",
# ]
# ///
"""
Generate tags.json for all GIFs using GPT-4o vision.

Extracts frames from each GIF and asks GPT-4o to identify:
- Characters/people (e.g., "Ron Swanson", "Batman")
- TV show/movie/source (e.g., "Parks and Recreation", "Wayne's World")
- Emotions/reactions (e.g., "frustrated", "excited")
- Scene description and actions
- Any overlay text visible in the GIF

Setup:
  1. Create an OpenAI API key at https://platform.openai.com/api-keys
  2. When creating the key, use "Restricted" permissions:
     - Set "Chat completions (/v1/chat/completions)" to "Full"
     - Everything else can stay "None"
  3. Export the key: export OPENAI_API_KEY="sk-..."

Usage:
  uv run scripts/generate_tags.py              # Tag untagged GIFs only
  uv run scripts/generate_tags.py --all        # Re-tag everything
  uv run scripts/generate_tags.py --file foo.gif  # Tag a specific file

Cost: ~$0.50-1.00 for all 236 GIFs (GPT-4o with low-detail images).
"""
import argparse
import base64
import json
import sys
from io import BytesIO
from pathlib import Path

from openai import OpenAI
from PIL import Image

IMAGE_EXTENSIONS = {".gif", ".jpg", ".jpeg", ".png", ".webp"}
GIF_DIR = "static"
TAGS_FILE = "tags.json"

SYSTEM_PROMPT = """You are a GIF/meme tagging assistant. Given frames from an animated GIF or image, produce descriptive tags for search.

Return JSON with these fields:
- "characters": array of character/person names if recognizable (e.g., "Ron Swanson", "Batman", "Will Ferrell"). Use the character name if it's a fictional role, actor name if it's the person themselves.
- "source": array of show/movie/game names (e.g., "Parks and Recreation", "Wayne's World", "The Office")
- "emotions": array of emotions/reactions depicted (e.g., "frustrated", "excited", "confused", "smug", "angry")
- "actions": array of what's happening (e.g., "table flip", "typing", "dancing", "facepalm", "money rain")
- "text": any overlay text visible in the image (e.g., "Deal with it", "I have no idea what I'm doing")
- "description": one short sentence describing the GIF

Be thorough. Include alternate names (e.g., both "Ron Swanson" and "Nick Offerman"). If you can't identify someone, describe them ("bearded man", "orange cat"). Always return valid JSON."""


def extract_frames(path: Path, max_frames: int = 3) -> list[str]:
    """Extract evenly-spaced frames from a GIF as base64 PNGs."""
    img = Image.open(path)

    # For non-animated images, just return the single frame
    n_frames = getattr(img, "n_frames", 1)
    if n_frames <= 1:
        buf = BytesIO()
        img.convert("RGB").save(buf, format="PNG")
        return [base64.b64encode(buf.getvalue()).decode()]

    # Pick evenly spaced frames
    indices = [0]
    if n_frames > 2:
        indices.append(n_frames // 2)
    indices.append(min(n_frames - 1, n_frames - 1))

    # Deduplicate
    indices = sorted(set(indices))[:max_frames]

    frames = []
    for idx in indices:
        img.seek(idx)
        buf = BytesIO()
        img.convert("RGB").save(buf, format="PNG")
        frames.append(base64.b64encode(buf.getvalue()).decode())

    return frames


def tag_gif(client: OpenAI, path: Path, filename: str) -> dict:
    """Send frames to GPT-4o and get structured tags."""
    frames = extract_frames(path)

    content: list[dict] = [
        {
            "type": "text",
            "text": f'Filename: "{filename}". Analyze these {len(frames)} frame(s) and return tags as JSON.',
        }
    ]

    for frame_b64 in frames:
        content.append(
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{frame_b64}",
                    "detail": "low",
                },
            }
        )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": content},
        ],
        response_format={"type": "json_object"},
        max_tokens=500,
    )

    text = response.choices[0].message.content or "{}"
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        print(f"  Warning: Could not parse JSON for {filename}")
        return {"description": text}


def main():
    parser = argparse.ArgumentParser(description="Generate tags for GIFs using GPT-4o")
    parser.add_argument("--all", action="store_true", help="Re-tag all GIFs")
    parser.add_argument("--file", type=str, help="Tag a specific file")
    args = parser.parse_args()

    root_dir = Path(__file__).parent.parent
    gifs_dir = root_dir / GIF_DIR
    tags_path = root_dir / TAGS_FILE

    if not gifs_dir.exists():
        print(f"Error: {GIF_DIR} directory not found")
        sys.exit(1)

    # Load existing tags
    existing: dict[str, dict] = {}
    if tags_path.exists() and not args.all:
        existing = json.loads(tags_path.read_text())

    # Get files to process
    if args.file:
        files = [gifs_dir / args.file]
        if not files[0].exists():
            print(f"Error: {args.file} not found")
            sys.exit(1)
    else:
        files = sorted(
            f
            for f in gifs_dir.iterdir()
            if f.is_file()
            and f.suffix.lower() in IMAGE_EXTENSIONS
            and not f.name.startswith(".")
        )

    # Filter to untagged files (unless --all)
    if not args.all and not args.file:
        files = [f for f in files if f.name not in existing]

    if not files:
        print("All GIFs already tagged. Use --all to re-tag.")
        return

    print(f"Tagging {len(files)} GIFs...")

    client = OpenAI()
    tags = dict(existing)

    for i, path in enumerate(files):
        print(f"  [{i + 1}/{len(files)}] {path.name}...", end=" ", flush=True)
        try:
            result = tag_gif(client, path, path.name)
            tags[path.name] = result
            desc = result.get("description", "")[:60]
            print(f"OK - {desc}")
        except Exception as e:
            print(f"FAILED - {e}")
            continue

    # Write tags sorted by filename
    sorted_tags = dict(sorted(tags.items()))
    tags_path.write_text(json.dumps(sorted_tags, indent=2) + "\n")
    print(f"\nWrote {len(sorted_tags)} entries to {TAGS_FILE}")


if __name__ == "__main__":
    main()
