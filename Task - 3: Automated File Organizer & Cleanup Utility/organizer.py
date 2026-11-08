"""
Automated File Organizer & Cleanup Utility
------------------------------------------
Sorts files in a directory (e.g. Downloads) into category subfolders
based on file extension. Handles naming collisions and permission errors.

Usage:
    python organizer.py                  # organizes ~/Downloads
    python organizer.py "C:/path/to/dir" # organizes a custom folder
    python organizer.py --dry-run        # preview only, moves nothing
"""

import argparse
import os
import shutil
from collections import Counter
from pathlib import Path

# Extension -> category folder mapping
EXTENSION_MAP = {
    # Documents
    ".pdf": "Documents", ".doc": "Documents", ".docx": "Documents",
    ".txt": "Documents", ".xls": "Documents", ".xlsx": "Documents",
    ".ppt": "Documents", ".pptx": "Documents", ".csv": "Documents",
    # Images
    ".jpg": "Images", ".jpeg": "Images", ".png": "Images",
    ".gif": "Images", ".bmp": "Images", ".svg": "Images", ".webp": "Images",
    # Videos
    ".mp4": "Videos", ".mkv": "Videos", ".avi": "Videos",
    ".mov": "Videos", ".wmv": "Videos",
    # Archives
    ".zip": "Archives", ".rar": "Archives", ".7z": "Archives",
    ".tar": "Archives", ".gz": "Archives",
    # Code
    ".py": "Code", ".js": "Code", ".html": "Code", ".css": "Code",
    ".java": "Code", ".cpp": "Code", ".c": "Code", ".json": "Code",
}

DEFAULT_CATEGORY = "Others"


def get_category(filename: str) -> str:
    """Return the category folder for a file based on its extension."""
    ext = os.path.splitext(filename)[1].lower()
    return EXTENSION_MAP.get(ext, DEFAULT_CATEGORY)


def unique_destination(dest_dir: str, filename: str) -> str:
    """Return a path that doesn't collide, e.g. report.pdf -> report_1.pdf."""
    base, ext = os.path.splitext(filename)
    candidate = os.path.join(dest_dir, filename)
    counter = 1
    while os.path.exists(candidate):
        candidate = os.path.join(dest_dir, f"{base}_{counter}{ext}")
        counter += 1
    return candidate


def organize(target_dir: str, dry_run: bool = False) -> dict:
    """Organize files in target_dir. Returns a stats dictionary."""
    stats = {"moved": Counter(), "skipped": 0, "errors": []}
    script_name = os.path.basename(__file__)

    with os.scandir(target_dir) as entries:
        files = [e for e in entries if e.is_file() and e.name != script_name]

    for entry in files:
        category = get_category(entry.name)
        dest_dir = os.path.join(target_dir, category)

        try:
            if not dry_run:
                os.makedirs(dest_dir, exist_ok=True)
            dest_path = unique_destination(dest_dir, entry.name)

            if dry_run:
                print(f"[DRY RUN] {entry.name} -> {category}/")
            else:
                shutil.move(entry.path, dest_path)
                print(f"Moved: {entry.name} -> {category}/{os.path.basename(dest_path)}")
            stats["moved"][category] += 1

        except PermissionError:
            msg = f"Permission denied: {entry.name}"
            print(f"[ERROR] {msg}")
            stats["errors"].append(msg)
        except FileExistsError:
            msg = f"File already exists: {entry.name}"
            print(f"[ERROR] {msg}")
            stats["errors"].append(msg)
        except OSError as exc:
            msg = f"Could not move {entry.name}: {exc}"
            print(f"[ERROR] {msg}")
            stats["errors"].append(msg)

    return stats


def print_summary(stats: dict, dry_run: bool) -> None:
    """Print a formatted execution summary."""
    total = sum(stats["moved"].values())
    label = "Files that would be moved" if dry_run else "Total files relocated"
    print("\n" + "=" * 40)
    print("        EXECUTION SUMMARY")
    print("=" * 40)
    for category, count in sorted(stats["moved"].items()):
        print(f"  {category:<12} : {count}")
    print("-" * 40)
    print(f"  {label}: {total}")
    print(f"  Errors encountered   : {len(stats['errors'])}")
    print("=" * 40)


def main() -> None:
    parser = argparse.ArgumentParser(description="Automated File Organizer")
    parser.add_argument(
        "directory", nargs="?", default=str(Path.home() / "Downloads"),
        help="Directory to organize (default: ~/Downloads)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would happen without moving any files",
    )
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"Error: '{args.directory}' is not a valid directory.")
        return

    print(f"Organizing: {args.directory}\n")
    stats = organize(args.directory, dry_run=args.dry_run)
    print_summary(stats, args.dry_run)


if __name__ == "__main__":
    main()
