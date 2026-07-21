#!/usr/bin/env python3
"""
Analyze global pip environment for zombie packages and conflicts.
"""
import subprocess
import sys


def run_pip(args):
    result = subprocess.run([sys.executable, "-m", "pip"] + args, capture_output=True, text=True)
    lines = [l for l in result.stdout.strip().split("\n") if l and not l.startswith("WARNING")]
    return lines


def main():
    print("=== Pip Environment Analysis ===\n")

    # 1. Total packages
    all_pkgs = run_pip(["list", "--format=freeze"])
    print(f"Total installed packages: {len(all_pkgs)}")

    # 2. Top-level (not-required) packages
    top_pkgs = run_pip(["list", "--not-required", "--format=freeze"])
    print(f"Top-level (directly installed) packages: {len(top_pkgs)}")
    print(f"Indirect dependencies: {len(all_pkgs) - len(top_pkgs)}\n")

    # 3. Dependency conflicts
    print("=== Dependency Check ===")
    check = subprocess.run([sys.executable, "-m", "pip", "check"], capture_output=True, text=True)
    if check.returncode == 0 and "No broken requirements" in check.stdout:
        print("No dependency conflicts found.")
    else:
        for line in check.stdout.strip().split("\n"):
            if line and not line.startswith("WARNING"):
                print(f"  CONFLICT: {line}")
    print()

    # 4. Show top-level packages by category hint
    print("=== Top-Level Packages (review these for uninstall candidates) ===")
    for line in top_pkgs:
        print(f"  {line}")


if __name__ == "__main__":
    main()
