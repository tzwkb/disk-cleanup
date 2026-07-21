#!/usr/bin/env python3
"""
Layered directory size scanner (cross-platform: Windows + macOS).
Recursively drills down from a root path, always following the largest folders
first, to locate space consumers fast. Skips OS system-critical paths.
Read-only — never deletes.
"""
import os
import sys
from pathlib import Path

IS_MAC = sys.platform == "darwin"

# Paths that are never worth drilling into for cleanup purposes (union of both OSes)
SKIP_PATHS = {
    # Windows
    "c:/windows",
    "c:/windows/system32",
    "c:/windows/syswow64",
    "c:/windows/winsxs",
    "c:/program files",
    "c:/program files (x86)",
    "c:/programdata/microsoft",
    "c:/$recycle.bin",
    "c:/system volume information",
    "c:/recovery",
    "c:/boot",
    "c:/users/asus/appdata/roaming/microsoft",
    "c:/users/asus/appdata/local/microsoft",
    "c:/users/asus/appdata/local/packages",
    # macOS
    "/System",
    "/Library",
    "/Volumes",
    "/private/var",
    "/private/tmp",
    "/cores",
    "/opt",
    "/usr",
    "/bin",
    "/sbin",
    "/etc",
    "/dev",
    "/proc",
    "/net",
    "/home",
    "/tmp",
    "/var",
}

# Paths where we stop drilling but still report size (known app roots)
STOP_DRILL_PATHS = {
    # Windows
    "c:/programdata/nvidia",
    "c:/programdata/nvidia corporation",
    "c:/programdata/lghub",
    "c:/programdata/asus",
    "c:/programdata/microsoft/windows defender",
    "c:/users/asus/appdata/roaming/tencent",
    "c:/users/asus/appdata/local/tencent",
    # macOS
    "/System/Volumes/Data/Users",
}


def normalize(p: str) -> str:
    return os.path.normpath(os.path.abspath(p)).lower().replace("\\", "/")


def should_skip(path: str) -> bool:
    np = normalize(path)
    for sp in SKIP_PATHS:
        if np == sp or np.startswith(sp + "/"):
            return True
    return False


def should_stop_drill(path: str) -> bool:
    np = normalize(path)
    for sp in STOP_DRILL_PATHS:
        if np == sp or np.startswith(sp + "/"):
            return True
    return False


def get_dir_size(path: str) -> int:
    total = 0
    try:
        for root, dirs, files in os.walk(path):
            for f in files:
                try:
                    total += os.path.getsize(os.path.join(root, f))
                except OSError:
                    pass
            # Remove symlinks from dirs to prevent infinite loops
            dirs[:] = [d for d in dirs if not os.path.islink(os.path.join(root, d))]
    except PermissionError:
        pass
    except OSError:
        pass
    return total


def scan_layer(path: str, depth: int = 0, max_depth: int = 5, min_mb: float = 100.0):
    """Recursively scan, printing only folders above threshold, drilling into largest first."""
    if depth > max_depth:
        return
    if should_skip(path):
        return

    stop_here = should_stop_drill(path)

    try:
        entries = []
        with os.scandir(path) as it:
            for entry in it:
                if not entry.is_dir(follow_symlinks=False):
                    continue
                name = entry.name
                if name.startswith("$") and depth == 0:
                    continue
                # on macOS, skip system hidden dirs at the top level
                if IS_MAC and depth == 0 and name.startswith("."):
                    continue
                entries.append((entry.path, name))
    except PermissionError:
        return
    except OSError:
        return

    if not entries:
        return

    sized = []
    for full_path, name in entries:
        if should_skip(full_path):
            continue
        sz = get_dir_size(full_path)
        if sz >= min_mb * 1024 * 1024:
            sized.append((full_path, name, sz))

    sized.sort(key=lambda x: x[2], reverse=True)

    indent = "  " * depth
    for full_path, name, sz in sized:
        gb = sz / (1024 ** 3)
        mb = sz / (1024 ** 2)
        size_str = f"{gb:.2f} GB" if gb >= 1.0 else f"{mb:.0f} MB"
        safe_name = name.encode("ascii", "replace").decode("ascii")

        marker = ""
        np = normalize(full_path)
        if "anaconda" in np or "0install" in np:
            marker = " [CLEANABLE if unused]"
        elif "cache" in np or "temp" in np or "backup" in np:
            marker = " [LIKELY CLEANABLE]"
        elif "download" in np:
            marker = " [CHECK FOR OLD FILES]"
        elif any(k in np for k in ("steam", "xcode", "android", "docker", "utm", "xinwechat")):
            marker = " [APP DATA — macOS: scan-only]"

        print(f"{indent}{safe_name:<50} {size_str:>10}{marker}")

        if not stop_here and not should_skip(full_path):
            scan_layer(full_path, depth + 1, max_depth, min_mb)


def main():
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        target = "C:\\" if not IS_MAC else os.path.expanduser("~")
    min_mb = float(sys.argv[2]) if len(sys.argv) > 2 else 100.0
    max_depth = int(sys.argv[3]) if len(sys.argv) > 3 else 5

    print(f"Scanning: {target}")
    print(f"Threshold: {min_mb} MB | Max depth: {max_depth}")
    print("=" * 80)

    total = get_dir_size(target)
    print(f"{'ROOT':<50} {total / (1024**3):>6.2f} GB")
    print("")

    scan_layer(target, depth=0, max_depth=max_depth, min_mb=min_mb)
    print("=" * 80)


if __name__ == "__main__":
    main()
