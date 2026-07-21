#!/usr/bin/env python3
"""
Scan ~/Library for large folders and classify by macOS safety level (READ-ONLY — never deletes).

macOS equivalent of the Windows "scan_programdata" audit: the real space hogs
on macOS live in ~/Library (Caches / Application Support / Containers / Logs /
Developer). This lists the big folders with a 🟢🟡🔴 risk hint so the agent can
report them without deleting anything.
"""
import os
import sys

HOME = os.path.expanduser("~")
LIB = os.path.join(HOME, "Library")

# (emoji, description) for known top-level ~/Library subfolders
CLASSIFICATION = {
    "Caches": ("🟢", "App 缓存（可再生，删后自动重建）"),
    "Logs": ("🟢", "日志（可再生）"),
    "Cookies": ("🟢", "Cookie 缓存"),
    "Containers": ("🟡", "App 沙盒（微信/QQ/UTM/Docker 等），清缓存走 App 内"),
    "Application Support": ("🟡", "App 数据（Steam/Claude/各 App），删=卸载/丢配置"),
    "Developer": ("🟡", "Xcode / 开发者数据（模拟器、DerivedData）"),
    "Metadata": ("🟡", "Spotlight / 元数据缓存"),
    "Group Containers": ("🟡", "App 组容器"),
    "Daemon Containers": ("🟡", "后台守护进程容器"),
    "Python": ("🟡", "Python 环境"),
    "Biome": ("🟡", "行为预测缓存"),
    "IntelligencePlatform": ("🟡", "Apple 智能平台缓存"),
    "Keychains": ("🔴", "钥匙串（凭证），勿动"),
    "IdentityServices": ("🔴", "账户身份数据"),
    "HomeKit": ("🔴", "HomeKit 数据"),
    "Mail": ("🔴", "邮件数据"),
    "Messages": ("🔴", "信息数据"),
    "Accounts": ("🔴", "账户数据"),
    "Preferences": ("🔴", "系统 / App 偏好设置"),
}

# Friendly labels for heavy bundle ids / app dirs
HEAVY_APPS = {
    "com.tencent.xinWeChat": "微信",
    "com.tencent.WeWorkMac": "企业微信",
    "com.tencent.qq": "QQ",
    "com.tencent.meeting": "腾讯会议",
    "com.utmapp.UTM": "UTM 虚拟机",
    "com.docker.docker": "Docker",
    "com.netease.163music": "网易云音乐",
    "com.kingsoft.wpsoffice.mac": "WPS",
    "com.bytedance.douyin.desktop": "抖音",
    "com.apple.mail": "邮件",
    "com.apple.Safari": "Safari",
    "Steam": "Steam 游戏",
    "Claude": "Claude",
    "Code": "VS Code",
    "Codex": "Codex",
    "kimi-desktop": "Kimi",
    "discord": "Discord",
    "Paradox Interactive": "Paradox 游戏",
    "Sid Meier's Civilization VI": "文明6",
}


def get_size(path: str) -> int:
    total = 0
    try:
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if not os.path.islink(os.path.join(root, d))]
            for f in files:
                try:
                    total += os.path.getsize(os.path.join(root, f))
                except OSError:
                    pass
    except OSError:
        pass
    return total


def fmt(sz: int) -> str:
    gb = sz / (1024 ** 3)
    mb = sz / (1024 ** 2)
    return f"{gb:>5.2f} GB" if gb >= 0.5 else f"{mb:>6.0f} MB"


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else LIB
    print(f"Scanning: {target}")
    print("=" * 80)

    entries = []
    try:
        for entry in os.scandir(target):
            if not entry.is_dir(follow_symlinks=False):
                continue
            name = entry.name
            if name.startswith("."):
                continue
            sz = get_size(entry.path)
            if sz > 10 * 1024 * 1024:  # only folders > 10 MB
                entries.append((name, sz))
    except PermissionError:
        print("Permission denied on some folders (SIP/TCC).")

    entries.sort(key=lambda x: x[1], reverse=True)

    print(f"{'Folder':<42}{'Size':>10}  Risk  Description")
    print("-" * 80)
    for name, sz in entries:
        emoji, desc = CLASSIFICATION.get(name, ("🟡", "未知 — 删除前确认"))
        if name in HEAVY_APPS:
            desc = f"{HEAVY_APPS[name]} 数据"
        safe = name.encode("ascii", "replace").decode("ascii")[:40]
        print(f"{safe:<42}{fmt(sz):>10}  {emoji}   {desc}")

    print("=" * 80)
    total = sum(x[1] for x in entries)
    print(f"Total: {len(entries)} folders | Sum: {total / (1024 ** 3):.2f} GB")


if __name__ == "__main__":
    main()
