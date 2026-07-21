# Disk Cleanup Master

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Agent Skill](https://img.shields.io/badge/Agent%20Skill-Codex-blue.svg)](SKILL.md)
[![PowerShell](https://img.shields.io/badge/PowerShell-scripts-5391FE.svg)](https://learn.microsoft.com/powershell/)
[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)

English | [中文](README_ZH.md)


**Agent Skill** — Safety-first Windows disk cleanup and space-analysis toolkit with aggressive scanning, conservative deletion, cache diagnostics, and confirmation-first cleanup guardrails.


Safety-first disk cleanup toolkit implementing an **aggressive-scan, conservative-delete** workflow. Cross-platform: full scan-and-confirm-delete on Windows; **read-only scan on macOS — it never auto-deletes, even when explicitly authorized** (the user runs the suggested commands themselves).

## Philosophy

> **macOS:** strictly read-only. This skill reports findings and suggested commands but **never runs any `rm` / trash / move operation**, even if the user says "go". Deletion is entirely manual.

| Level | Action | Examples |
|-------|--------|----------|
| 🟢 **Green** | Safe to delete | Temp files, browser cache, pip cache, `__pycache__`, WinSxS old components |
| 🟡 **Yellow** | Confirm with user | Game saves, WeChat/QQ logs, WPS cloud files, downloads |
| 🔴 **Red** | Never touch | Windows system directories, Program Files, active projects |

## Scripts

| Script | Purpose |
|--------|---------|
| `tree_size_scanner.py` | Layered tree scanning of large folders (cross-platform) |
| `scan_programdata.py` | Audit `C:\ProgramData` by safety level (Windows) |
| `cleanup_temp.ps1` | Safe temp file cleanup (Windows) |
| `scan_large_folders.py` | Identify space hogs (cross-platform) |
| `find_zombie_packages.py` | Detect orphaned pip packages (cross-platform) |
| `robocopy_wipe.py` | Wipe locked folders when `takeown` fails (Windows) |
| `find_folders_by_keyword.py` | Locate folders by name pattern (cross-platform) |
| `disk_overview.py` | Per-volume free space overview (macOS, read-only) |
| `scan_library.py` | Audit `~/Library` by safety level (macOS, read-only) |

## Usage

Run individual scripts as needed:

```powershell
# Scan ProgramData
python scripts/scan_programdata.py

# Clean temp files
powershell -ExecutionPolicy Bypass -File scripts/cleanup_temp.ps1
```

## References

- `references/chinese-app-special-cases.md` — Documented quirks for WeChat, QQ, WPS, NetEase, BaiduNetdisk

## License

[MIT](LICENSE)
