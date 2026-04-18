# Disk Cleanup Master

A safety-first Windows disk cleanup toolkit implementing an aggressive-scan, conservative-delete workflow. Built for real-world scenarios including Chinese software quirks, massive Steam libraries, and stubborn locked folders.

[中文说明](#中文说明)

---

## Philosophy

**Scan aggressive, delete conservative.**

- 🟢 **Green** — Safe to delete: temp files, browser caches, pip cache, `__pycache__`, WinSxS old components, app-labeled Cache/Log folders.
- 🟡 **Yellow** — Confirm with user: game saves, WeChat/QQ logs, WPS cloud files, downloads, ProgramData app data.
- 🔴 **Red** — Never touch: Windows system directories, Program Files, active project files, un-backed-up data.

## Features

| Feature | Description |
|---------|-------------|
| **Layered Tree Scanning** | Drill down from root into largest folders, avoid timeouts on massive directories |
| **ProgramData Audit** | Scan and classify `C:\ProgramData` by safety level (driver data / app data / system data) |
| **WinSxS Cleanup** | Safe DISM-based component store cleanup |
| **Python Environment Health** | Find zombie pip packages and dependency conflicts |
| **Robocopy Wipe** | Delete stubborn locked folders when `takeown` fails |
| **Chinese Software Special Cases** | Documented quirks for WeChat, QQ, WPS, NetEase, BaiduNetdisk |

## Script Inventory

| Script | Purpose | Usage |
|--------|---------|-------|
| `tree_size_scanner.py` | Layered drill-down size scanner | `python tree_size_scanner.py "C:\\" 500 4` |
| `scan_large_folders.py` | Top-level folder size scan with depth limit | `python scan_large_folders.py "C:\\"` |
| `scan_programdata.py` | ProgramData audit with safety classification | `python scan_programdata.py` |
| `find_folders_by_keyword.py` | Fast keyword search for apps/games | `python find_folders_by_keyword.py "D:\\" "Call of Duty|COD"` |
| `find_zombie_packages.py` | Pip orphan package analyzer | `python find_zombie_packages.py` |
| `cleanup_temp.ps1` | Safe temp/cache cleaner with `-WhatIf` preview | `powershell -File cleanup_temp.ps1 -WhatIf` |
| `robocopy_wipe.py` | Delete stubborn folders via empty-folder mirror | `python robocopy_wipe.py "C:\Path\To\Target"` |

## Quick Start

```powershell
# 1. C-drive overview (shows folders > 500 MB, depth 4)
python scripts/tree_size_scanner.py "C:\\" 500 4

# 2. Find forgotten large apps in ProgramData
python scripts/scan_programdata.py

# 3. Preview temp cleanup (no files deleted)
powershell -File scripts/cleanup_temp.ps1 -WhatIf

# 4. Find pip dependency conflicts
python scripts/find_zombie_packages.py
```

## Safety Warnings

1. **Never use `robocopy /MIR` backwards.** The wipe script creates an empty folder as source and mirrors it *to* the target. Reversing source/destination will destroy data.
2. **Tencent apps (WeChat/QQ) use hardcoded paths.** Do NOT move their folders manually. Change paths inside each app's settings dialog.
3. **NSIS uninstallers (`/S`) return immediately.** Poll for folder disappearance after silent uninstalls.
4. **Scan output pollution.** Running multiple `Get-ChildItem | Format-Table` in one shell call can mix outputs. Use Python scripts for unified reporting.

## References

- `references/chinese-app-special-cases.md` — Storage quirks for WeChat, QQ, WPS, NetEase, BaiduNetdisk, Steam/WeGame

## Requirements

- Windows 10/11
- Python 3.8+ (for scanner scripts)
- PowerShell 5.1+ (for `.ps1` scripts)

## License

MIT License — see [LICENSE](LICENSE).

---

## 中文说明

**Disk Cleanup Master** 是一个 Windows 磁盘清理工具集，核心原则是"扫描激进，删除保守"。

### 核心特性

- **分层钻取扫描**：从根目录层层深入最大文件夹，快速定位空间占用源头，避免在大目录上超时
- **ProgramData 专项审计**：扫描 `C:\ProgramData` 并按安全等级分类（设备驱动/应用数据/系统数据）
- **WinSxS 组件清理**：使用 DISM 安全清理 Windows 组件存储
- **Python 环境健康检查**：识别 pip 僵尸包和依赖冲突
- **顽固文件夹删除**：当 `takeown`/`icacls` 失败时，使用 robocopy empty trick 强制清空
- **国产软件特殊处理**：记录微信、QQ、WPS、网易云、百度网盘等国产软件的存储路径硬编码行为

### 安全模型

| 等级 | 可删除项 |
|------|---------|
| 🟢 绿灯 | Temp、浏览器缓存、pip cache、`__pycache__`、WinSxS 旧组件、应用标注的 Cache/Log |
| 🟡 黄灯 | 游戏存档、微信/QQ 记录、WPS 云盘文件、下载文件夹、ProgramData 应用数据 |
| 🔴 红灯 | Windows 系统目录、Program Files、用户正在使用的项目文件、未备份的数据 |

### 快速开始

```powershell
# 1. C 盘全景扫描（显示 >500MB 文件夹，深入 4 层）
python scripts/tree_size_scanner.py "C:\\" 500 4

# 2. ProgramData 审计
python scripts/scan_programdata.py

# 3. 预览临时文件清理（不删除任何文件）
powershell -File scripts/cleanup_temp.ps1 -WhatIf

# 4. 检查 pip 依赖冲突
python scripts/find_zombie_packages.py
```

### 重要警告

1. **切勿反向使用 `robocopy /MIR`**。wipe 脚本创建空文件夹作为源，镜像到目标。源和目标颠倒会清空数据。
2. **腾讯系软件（微信/QQ）使用硬编码路径**。切勿手动移动其文件夹，必须在各应用设置中修改存储路径。
3. **NSIS 静默卸载程序（`/S`）启动后立即返回**。需要在启动后轮询检查安装目录是否消失。
4. **扫描输出污染**。在单条 shell 命令中并行运行多个 `Get-ChildItem | Format-Table` 会导致输出混淆。使用 Python 脚本做统一输出。
