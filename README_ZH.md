# Disk Cleanup Master

中文 | [English](README.md)


## 概览

Windows 磁盘空间分析与清理 Agent Skill，按“扫描激进、删除保守”原则处理大文件、缓存和常见软件占用。

## 主要能力

- 扫描磁盘占用、缓存、游戏库和锁定目录。
- 删除前保留确认边界。
- 面向 Windows 10/11 排障与清理。

## 使用方式

按 README 和 SKILL.md 中的脚本说明运行扫描，再按风险分级确认清理。

## 状态

该仓库仍按当前 README 的说明维护或使用。

## 注意事项

该工具默认保守，不应静默删除用户数据。

## 命令与配置参考

以下代码块从主 README 保留；命令、路径和配置键不翻译，复制时请以实际环境为准。

```powershell
# Scan ProgramData
python scripts/scan_programdata.py

# Clean temp files
powershell -ExecutionPolicy Bypass -File scripts/cleanup_temp.ps1
```

## 详细技术说明

主 README 保留了原始技术细节、历史说明、完整命令和文件结构。本文件作为中文版本维护核心说明；需要逐项核对命令时，请参照主 README 的代码块和路径。
