#!/usr/bin/env python3
"""
Generate GIF table for README.md
Scans the static directory and creates a markdown table with name and GIF preview.
"""
import hashlib
import sys
from pathlib import Path

IMAGE_EXTENSIONS = {".gif", ".jpg", ".jpeg", ".png", ".webp"}
GIF_DIR = "static"
TABLE_MARKER = "## GIF Collection"


def check_for_duplicate_images(gifs_dir: Path) -> bool:
    gif_files = [
        f
        for f in gifs_dir.iterdir()
        if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS and not f.name.startswith(".")
    ]

    if not gif_files:
        return True

    hash_map: dict[str, list[str]] = {}
    for gif_file in gif_files:
        md5_hash = hashlib.md5()
        with open(gif_file, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                md5_hash.update(chunk)
        file_hash = md5_hash.hexdigest()
        hash_map.setdefault(file_hash, []).append(gif_file.name)

    duplicates_found = False
    for file_hash, files in hash_map.items():
        if len(files) > 1:
            if not duplicates_found:
                print("Duplicate images detected!")
                duplicates_found = True
            print(f"   Hash {file_hash[:8]}... has {len(files)} copies:")
            for filename in files:
                print(f"     - {filename}")

    if duplicates_found:
        print("\nPlease remove duplicate images before committing.")
    return not duplicates_found


def generate_gif_table(gifs_dir: Path) -> str:
    gif_files = sorted(
        [
            f
            for f in gifs_dir.iterdir()
            if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS and not f.name.startswith(".")
        ]
    )

    if not gif_files:
        return ""

    table = f"\n{TABLE_MARKER}\n\n"
    table += "| Name | Preview |\n"
    table += "|------|:-------:|\n"

    for gif_file in gif_files:
        name = gif_file.stem
        gif_path = f"{GIF_DIR}/{gif_file.name}"
        table += f'| `{name}` | <img src="{gif_path}" alt="{name}" width="120"> |\n'

    return table


def update_readme() -> bool:
    root_dir = Path(__file__).parent.parent
    gifs_dir = root_dir / GIF_DIR
    readme_path = root_dir / "README.md"

    if not gifs_dir.exists():
        print(f"Error: {GIF_DIR} directory not found")
        return False

    if not check_for_duplicate_images(gifs_dir):
        return False

    if not readme_path.exists():
        print("Error: README.md not found")
        return False

    gif_count = len(
        [
            f
            for f in gifs_dir.iterdir()
            if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS and not f.name.startswith(".")
        ]
    )

    content = readme_path.read_text()
    new_table = generate_gif_table(gifs_dir)

    if TABLE_MARKER in content:
        start_idx = content.find(TABLE_MARKER)
        next_section_idx = content.find("\n##", start_idx + len(TABLE_MARKER))
        if next_section_idx == -1:
            new_content = content[:start_idx] + new_table
        else:
            new_content = content[:start_idx] + new_table + "\n" + content[next_section_idx:]
    else:
        new_content = content.rstrip() + "\n" + new_table

    readme_path.write_text(new_content)

    table_row_count = new_table.count("| `")
    if table_row_count != gif_count:
        print(f"Warning: Mismatch! {gif_count} files but {table_row_count} rows in table")
        return False

    print(f"Updated README.md with {gif_count} GIFs")
    return True


if __name__ == "__main__":
    result = update_readme()
    if result is False:
        sys.exit(1)
