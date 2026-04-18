#!/usr/bin/env python3
"""
Delete stubborn folders using the robocopy empty-folder trick.
When Remove-Item -Force and takeown+icacls both fail, mirror an empty
directory over the target to force-empty it, then remove the husk.

SAFETY: This script maintains a blocklist of system paths that must
never be wiped. Always double-check the target path before running.
"""
import os
import sys
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

# Absolute paths that must NEVER be targeted
BLOCKLIST = {
    "c:\\",
    "c:\\windows",
    "c:\\windows\\system32",
    "c:\\program files",
    "c:\\program files (x86)",
    "c:\\programdata",
    "c:\\users",
    "c:\\users\\default",
    "c:\\users\\public",
    "c:\\inetpub",
    "c:\\boot",
    "c:\\recovery",
}


def normalize(p: str) -> str:
    return os.path.normpath(os.path.abspath(p)).lower()


def is_safe(target: str) -> tuple:
    """Return (ok: bool, reason: str)."""
    t = normalize(target)
    if not os.path.exists(target):
        return False, f"Target does not exist: {target}"
    if not os.path.isdir(target):
        return False, f"Target is not a directory: {target}"
    for blocked in BLOCKLIST:
        if t == blocked or t.startswith(blocked + os.sep):
            return False, f"Target is in blocklist or too close to system root: {target}"
    return True, ""


def robocopy_wipe(target: str, retries: int = 3) -> bool:
    """Wipe target directory using robocopy /MIR from an empty folder."""
    empty = tempfile.mkdtemp(prefix="empty_")
    try:
        for attempt in range(1, retries + 1):
            result = subprocess.run(
                ["robocopy", empty, target, "/MIR", "/R:1", "/W:1", "/NP", "/NFL", "/NDL"],
                capture_output=True,
                text=True,
            )
            # After mirroring, try to remove the now-empty husk
            try:
                os.rmdir(target)
                if not os.path.exists(target):
                    return True
            except OSError:
                pass
            if attempt < retries:
                time.sleep(1)
        return False
    finally:
        shutil.rmtree(empty, ignore_errors=True)


def main():
    if len(sys.argv) < 2:
        print("Usage: python robocopy_wipe.py <target_folder>")
        print("")
        print("WARNING: This permanently deletes the target folder and ALL contents.")
        print("Blocked paths (cannot be targeted):")
        for p in sorted(BLOCKLIST):
            print(f"  {p}")
        sys.exit(1)

    target = sys.argv[1]
    ok, reason = is_safe(target)
    if not ok:
        print(f"REFUSED: {reason}")
        sys.exit(1)

    # Show size for user confirmation
    total = 0
    file_count = 0
    for root, _dirs, files in os.walk(target):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(root, f))
                file_count += 1
            except OSError:
                pass

    gb = total / (1024 ** 3)
    mb = total / (1024 ** 2)
    size_str = f"{gb:.2f} GB" if gb >= 0.1 else f"{mb:.1f} MB"

    print(f"Target: {target}")
    print(f"Size:   {size_str}  ({file_count} files)")
    print("")
    confirm = input("Type YES to permanently delete this folder: ")
    if confirm.strip() != "YES":
        print("Cancelled.")
        sys.exit(0)

    print("Wiping with robocopy /MIR ...")
    success = robocopy_wipe(target)
    if success:
        print(f"Deleted: {target}")
    else:
        print(f"FAILED to fully delete: {target}")
        print("Some files may still be locked. Try closing related applications.")
        sys.exit(1)


if __name__ == "__main__":
    main()
