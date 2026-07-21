# Disk Cleanup Master

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Agent Skill](https://img.shields.io/badge/Agent%20Skill-Codex-blue.svg)](SKILL.md)
[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)

[English](README.md) | 中文

## 概览

跨平台磁盘空间分析与清理 Agent Skill（Windows + macOS），按“扫描激进、删除保守”原则处理大文件、缓存和常见软件占用。Windows 下支持确认后删除；**macOS 下仅做只读扫描与报告，绝不执行删除——即使用户说“go / 跑 / 可以”也不代执行，删除命令由用户自行复制在终端运行**。

## 主要能力

- 扫描磁盘占用、缓存、游戏库和锁定目录。
- 删除前保留确认边界（Windows）。
- 面向 Windows 10/11 排障与清理，以及 macOS 空间分析（只读）。

## 使用方式

按 README 和 SKILL.md 中的脚本说明运行扫描，再按风险分级确认清理（macOS 仅报告）。

## 注意事项

该工具默认保守，不应静默删除用户数据。macOS 上更严格：本技能只读扫描，**任何删除（含清空回收站 / 移动）都不由本技能触发，即使用户授权也只输出建议命令，由用户手动执行**。

## 命令与配置参考

以下命令、路径和配置键保持原样，复制时请以实际环境为准。

```powershell
# Scan ProgramData (Windows)
python scripts/scan_programdata.py

# Clean temp files (Windows)
powershell -ExecutionPolicy Bypass -File scripts/cleanup_temp.ps1
```

macOS 只读扫描：

```bash
# 磁盘概览 + ~/Library 钻取（只读）
python scripts/disk_overview.py
python scripts/scan_library.py
```

## macOS 支持（追加）

- 脚本自动识别系统：Windows 保留完整能力，macOS 仅只读。
- macOS 专用只读脚本：`disk_overview.py`（各卷可用空间）、`scan_library.py`（~/Library 安全分级）。
- 跨平台脚本 `tree_size_scanner.py` / `scan_large_folders.py` / `find_folders_by_keyword.py` 在 macOS 同样可用。
- macOS 陷阱：APFS 共享块（删缓存未必释放空间）、回收站 `uchg` 锁定标志（`rm` 会静默跳过）。详见 SKILL.md「macOS 支持」章节。

## 对应技术覆盖

### 核心原则

该 skill 的原则是“扫描激进、删除保守”：可以尽量完整地发现大文件、缓存和系统垃圾，但删除、迁移或禁用操作必须由用户确认（macOS 下不执行删除）。

### 脚本范围

脚本覆盖 Windows 与 macOS 磁盘清理场景，含系统缓存、用户目录、常见国产软件缓存、开发环境缓存和大型应用目录分析。

### 使用流程

1. 先扫描磁盘占用和候选清理项。
2. 生成清理建议和风险说明。
3. 用户确认后再执行删除、迁移或禁用（仅 Windows；macOS 止步于报告）。
4. 对高风险操作保留回滚或恢复说明。

### 参考

英文 README 中的 scripts、usage 和 references 对应本中文说明中的脚本范围、执行流程和安全边界。
