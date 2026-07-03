# Disk Cleanup Master

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Agent Skill](https://img.shields.io/badge/Agent%20Skill-Codex-blue.svg)](SKILL.md)
[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)

[English](README.md) | 中文

## 概览

Windows 磁盘空间分析与清理 Agent Skill，按“扫描激进、删除保守”原则处理大文件、缓存和常见软件占用。

## 主要能力

- 扫描磁盘占用、缓存、游戏库和锁定目录。
- 删除前保留确认边界。
- 面向 Windows 10/11 排障与清理。

## 使用方式

按 README 和 SKILL.md 中的脚本说明运行扫描，再按风险分级确认清理。

## 注意事项

该工具默认保守，不应静默删除用户数据。

## 命令与配置参考

以下命令、路径和配置键保持原样，复制时请以实际环境为准。

```powershell
# Scan ProgramData
python scripts/scan_programdata.py

# Clean temp files
powershell -ExecutionPolicy Bypass -File scripts/cleanup_temp.ps1
```
