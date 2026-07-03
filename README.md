# Disk Cleanup Master

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Agent Skill](https://img.shields.io/badge/Agent%20Skill-Codex-blue.svg)](SKILL.md)
[![PowerShell](https://img.shields.io/badge/PowerShell-scripts-5391FE.svg)](https://learn.microsoft.com/powershell/)
[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)

English | [中文](README_ZH.md)


**Agent Skill** — Safety-first Windows disk cleanup and space-analysis toolkit with aggressive scanning, conservative deletion, cache diagnostics, and confirmation-first cleanup guardrails.

[![PowerShell](https://img.shields.io/badge/PowerShell-5.1+-blue.svg)](https://docs.microsoft.com/powershell/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Safety-first Windows disk cleanup toolkit implementing an **aggressive-scan, conservative-delete** workflow.

## Philosophy

| Level | Action | Examples |
|-------|--------|----------|
| 🟢 **Green** | Safe to delete | Temp files, browser cache, pip cache, `__pycache__`, WinSxS old components |
| 🟡 **Yellow** | Confirm with user | Game saves, WeChat/QQ logs, WPS cloud files, downloads |
| 🔴 **Red** | Never touch | Windows system directories, Program Files, active projects |

## Scripts

| Script | Purpose |
|--------|---------|
| `tree_size_scanner.py` | Layered tree scanning of large folders |
| `scan_programdata.py` | Audit `C:\ProgramData` by safety level |
| `cleanup_temp.ps1` | Safe temp file cleanup |
| `scan_large_folders.py` | Identify space hogs |
| `find_zombie_packages.py` | Detect orphaned pip packages |
| `robocopy_wipe.py` | Wipe locked folders when `takeown` fails |
| `find_folders_by_keyword.py` | Locate folders by name pattern |

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
