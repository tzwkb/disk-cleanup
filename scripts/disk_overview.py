#!/usr/bin/env python3
"""
macOS disk overview (READ-ONLY — never deletes or modifies anything).

Shows used / available space for every mounted volume via `df -h`,
and highlights the user data volume (/System/Volumes/Data) where
most user space is actually consumed.

No deletion, no mutation — purely informational.
On non-macOS systems it just prints `df -h` output.
"""
import subprocess
import re
import sys


def main():
    try:
        out = subprocess.run(["df", "-h"], capture_output=True, text=True).stdout
    except Exception as e:
        print(f"df failed: {e}")
        return

    lines = out.strip().split("\n")
    if not lines:
        return

    header = lines[0]
    print(header)
    print("-" * len(header))

    data_line = None
    for line in lines[1:]:
        if not line.strip():
            continue
        print(line)
        cols = line.split()
        # exact mount-point match, not substring (avoids matching .../Data/home)
        if len(cols) >= 6 and cols[-1] == "/System/Volumes/Data":
            data_line = line

    if data_line:
        cols = data_line.split()
        if len(cols) >= 5:
            print("")
            print(f"[用户数据卷] 已用 {cols[2]} / 共 {cols[1]} / 可用 {cols[3]} / 占用 {cols[4]}")
            m = re.search(r"(\d+)%", cols[4])
            if m and int(m.group(1)) >= 85:
                print("[警告] 数据卷占用 >= 85%，建议尽快清理。")


if __name__ == "__main__":
    main()
