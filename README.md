# Disk Cleanup Master

<!-- bilingual-readme:start -->

## 双语说明 / Bilingual Documentation

> 本节提供整篇 README 的中英双语维护说明；下方保留原始详细说明、命令、路径和配置示例。
> This section provides bilingual maintenance notes for the full README; the original detailed notes, commands, paths, and configuration examples are preserved below.

### 中文

**概览**：Windows 磁盘空间分析与清理 Agent Skill，按“扫描激进、删除保守”原则处理大文件、缓存和常见软件占用。

**主要能力**：
- 扫描磁盘占用、缓存、游戏库和锁定目录。
- 删除前保留确认边界。
- 面向 Windows 10/11 排障与清理。

**使用方式**：按 README 和 SKILL.md 中的脚本说明运行扫描，再按风险分级确认清理。

**状态**：该仓库仍按当前 README 的说明维护或使用。

**注意事项**：该工具默认保守，不应静默删除用户数据。

### English

**Overview**: Windows disk space analysis and cleanup Agent Skill using an aggressive-scan, conservative-delete workflow.

**Key capabilities**:
- Scans disk usage, caches, game libraries, and locked folders.
- Keeps confirmation boundaries before deletion.
- Targets Windows 10/11 troubleshooting and cleanup.

**Usage**: Run scans according to README/SKILL.md scripts, then confirm cleanup by risk level.

**Status**: This repository is maintained or used according to the current README notes.

**Notes**: The tool is conservative by default and should not silently delete user data.

<!-- bilingual-readme:end -->

**Agent Skill** — Windows 磁盘空间分析与清理工具，按“扫描激进、删除保守”原则定位大文件、缓存、系统垃圾和常见软件占用，并保留确认与回滚边界。

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