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

## 对应技术覆盖

### 核心原则

该 skill 的原则是“扫描激进、删除保守”：可以尽量完整地发现大文件、缓存和系统垃圾，但删除、迁移或禁用操作必须由用户确认。

### 脚本范围

脚本面向 Windows 磁盘清理场景，覆盖系统缓存、用户目录、常见国产软件缓存、开发环境缓存和大型应用目录分析。

### 使用流程

1. 先扫描磁盘占用和候选清理项。
2. 生成清理建议和风险说明。
3. 用户确认后再执行删除、迁移或禁用。
4. 对高风险操作保留回滚或恢复说明。

### 参考

英文 README 中的 scripts、usage 和 references 对应本中文说明中的脚本范围、执行流程和安全边界。
