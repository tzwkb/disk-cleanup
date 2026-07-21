#!/usr/bin/env python3
"""
Fast folder name search by keyword regex (cross-platform: Windows + macOS).
Scans directory names up to a limited depth (default 6) without calculating sizes.
Much faster than recursive size scanning; designed for finding specific apps/games
in large drives (e.g. Steam libraries, cracked game folders) without timeouts.
"""
import os
import re
import sys

DEFAULT_MAX_DEPTH = 6


def search(path: str, pattern: re.Pattern, max_depth: int, current_depth: int = 0):
    """Yield paths whose directory name matches the pattern."""
    if current_depth > max_depth:
        return
    try:
        with os.scandir(path) as it:
            for entry in it:
                if not entry.is_dir(follow_symlinks=False):
                    continue
                name = entry.name
                if pattern.search(name):
                    yield entry.path
                if current_depth < max_depth:
                    yield from search(entry.path, pattern, max_depth, current_depth + 1)
    except PermissionError:
        pass
    except OSError:
        pass


def main():
    if len(sys.argv) < 3:
        print("Usage: python find_folders_by_keyword.py <path> <regex_pattern> [max_depth]")
        print("")
        print("Examples (Windows):")
        print('  python find_folders_by_keyword.py "D:\\\\" "Call of Duty|COD|Modern Warfare"')
        print('  python find_folders_by_keyword.py "C:\\\\" "anaconda|python" 4')
        print("Examples (macOS):")
        print('  python find_folders_by_keyword.py ~/Library "Steam|UTM|docker|xinWeChat" 6')
        print('  python find_folders_by_keyword.py ~/Library "Claude|Codex|kimi" 4')
        sys.exit(1)

    target = sys.argv[1]
    raw_pattern = sys.argv[2]
    max_depth = int(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_MAX_DEPTH

    try:
        compiled = re.compile(raw_pattern, re.IGNORECASE)
    except re.error as e:
        print(f"Invalid regex: {e}")
        sys.exit(1)

    print(f"Searching: {target}")
    print(f"Pattern:   {raw_pattern}")
    print(f"Max depth: {max_depth}")
    print("-" * 70)

    count = 0
    for match_path in search(target, compiled, max_depth):
        safe = match_path.encode("ascii", "replace").decode("ascii")
        print(safe)
        count += 1

    print("-" * 70)
    print(f"Found {count} matching folder(s)")


if __name__ == "__main__":
    main()
