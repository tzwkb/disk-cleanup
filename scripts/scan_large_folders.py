#!/usr/bin/env python3
"""
Fast disk space scanner (cross-platform: Windows + macOS).
Scans top-level folders under a given path and reports sizes.
Uses depth-limited recursion to avoid timeouts on huge directories.
"""
import os
import sys
from pathlib import Path

MAX_DEPTH = 2
IS_MAC = sys.platform == "darwin"

# macOS system hidden dirs to skip when scanning from a filesystem root
MACOS_SYSTEM_HIDDEN = {
    ".Spotlight-V100",
    ".fseventsd",
    ".Trashes",
    ".vol",
    ".DocumentRevisions-V100",
    ".TemporaryItems",
    ".PKInstallSandboxManager",
}


def get_size(path: str, current_depth: int = 0) -> int:
    """Estimate directory size with depth limit."""
    total = 0
    try:
        with os.scandir(path) as it:
            for entry in it:
                if entry.is_symlink():
                    continue
                try:
                    if entry.is_file(follow_symlinks=False):
                        total += entry.stat(follow_symlinks=False).st_size
                    elif entry.is_dir(follow_symlinks=False) and current_depth < MAX_DEPTH:
                        total += get_size(entry.path, current_depth + 1)
                except OSError:
                    pass
    except OSError:
        pass
    return total


def main():
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        target = "C:\\" if not IS_MAC else os.path.expanduser("~")
    print(f"Scanning: {target}  (depth limit: {MAX_DEPTH})")
    print("-" * 60)

    p = Path(target)
    if not p.exists():
        print(f"Path not found: {target}")
        return

    folders = []
    for child in p.iterdir():
        if not child.is_dir():
            continue
        name = child.name
        if name.startswith("$") or name == "System Volume Information":
            continue
        if IS_MAC and name in MACOS_SYSTEM_HIDDEN:
            continue
        sz = get_size(str(child))
        folders.append((name, sz))

    folders.sort(key=lambda x: x[1], reverse=True)

    for name, sz in folders[:20]:
        safe_name = name.encode("ascii", "replace").decode("ascii")
        gb = sz / (1024 ** 3)
        mb = sz / (1024 ** 2)
        if gb >= 0.1:
            print(f"{safe_name:<50} {gb:>6.2f} GB")
        else:
            print(f"{safe_name:<50} {mb:>6.1f} MB")

    print("-" * 60)
    total = sum(x[1] for x in folders)
    print(f"Total scanned folders: {len(folders)}  |  Sum: {total / (1024**3):.2f} GB")


if __name__ == "__main__":
    main()
