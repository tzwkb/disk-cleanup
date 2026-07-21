#!/usr/bin/env python3
"""
Scan C:/ProgramData for large folders and classify by safety level.
Helps identify forgotten app installations (Anaconda, 0install, etc.)
and device driver data that should not be touched.
"""
import os
import sys
from pathlib import Path

# Safety classification for known ProgramData folders
# 🟢 safe_to_remove: app data for software no longer used
# 🟡 confirm: app data that may still be in use
# 🔴 do_not_touch: system or device driver data
CLASSIFICATION = {
    # Device drivers / hardware utilities — NEVER touch
    "NVIDIA": ("🔴", "NVIDIA driver data"),
    "NVIDIA Corporation": ("🔴", "NVIDIA driver/config data"),
    "LGHUB": ("🔴", "Logitech G HUB device config"),
    "LGHUBData": ("🔴", "Logitech G HUB data"),
    "ASUS": ("🔴", "ASUS motherboard/software data"),
    "AMD": ("🔴", "AMD driver data"),
    "Intel": ("🔴", "Intel driver data"),
    "Dolby": ("🔴", "Dolby audio driver data"),
    "Realtek": ("🔴", "Realtek audio driver data"),

    # System critical — NEVER touch
    "Microsoft": ("🔴", "Windows system data (Defender, Search, etc.)"),
    "Packages": ("🔴", "Windows app packages"),
    "SoftwareDistribution": ("🔴", "Windows Update data"),
    "USOShared": ("🔴", "Windows Update shared data"),
    "USOPrivate": ("🔴", "Windows Update private data"),
    "Windows Master Store": ("🔴", "Windows master store"),
    "Windows Master Setup": ("🔴", "Windows setup data"),
    "WindowsHolographicDevices": ("🔴", "Windows holographic data"),

    # Installer caches — touch only if desperate
    "Package Cache": ("🟡", "Windows Installer cache (needed for uninstall/repair)"),
    "chocolatey": ("🟡", "Chocolatey package cache"),
    "ChocolateyHttpCache": ("🟡", "Chocolatey HTTP cache"),

    # App global data — safe to remove if app uninstalled
    "anaconda3": ("🟢", "Anaconda Python environment (safe if not using Anaconda)"),
    "conda": ("🟢", "Conda package manager data"),
    "0install.net": ("🟢", "Zero Install package manager data"),
    "Tencent": ("🟡", "Tencent app data (QQ/WeChat/WeType/QQPCMgr) — check subfolders"),
    "Adobe": ("🟡", "Adobe Creative Cloud data"),
    "Steam": ("🟡", "Steam global config"),
    "Battle.net_components": ("🟡", "Battle.net component data"),
    "Epic": ("🟡", "Epic Games data"),
    "Origin": ("🟡", "EA Origin data"),
    "EA Desktop": ("🟡", "EA Desktop data"),
    "Electronic Arts": ("🟡", "Electronic Arts data"),
    "Riot Games": ("🟡", "Riot Games data"),
    "Valorant": ("🟡", "Valorant data"),
    "WPS Cloud Files": ("🟡", "WPS cloud cache"),
    "WPSDrive": ("🟡", "WPS drive cache"),
    "kingsoft": ("🟡", "WPS/Kingsoft data"),
    "NeteaseWinDev": ("🟡", "NetEase developer tools"),
    "Thunder Network": ("🟡", "Xunlei/Thunder download cache"),
    "BaiduNetdisk": ("🟡", "Baidu Netdisk data"),
    "Baidu": ("🟡", "Baidu app data"),
    "360SD": ("🟡", "360 Safe data"),
    "PopCap Games": ("🟡", "PopCap Games data"),
    "Trados": ("🟡", "Trados translation data"),
    "SDL": ("🟡", "SDL software data"),
    "MemoQ": ("🟡", "MemoQ translation data"),
    "SafeNet Sentinel": ("🟡", "SafeNet dongle driver data"),
    "ZeroTier": ("🟡", "ZeroTier VPN data"),
    "obs-studio-hook": ("🟡", "OBS Studio hook data"),
    "Mount and Blade II Bannerlord": ("🟡", "Game data"),
    "Rockstar Games": ("🟡", "Rockstar game data"),
    "Frontier Developments": ("🟡", "Frontier game data"),
    "Battlestate Games": ("🟡", "Battlestate game data"),
    "NetHack": ("🟡", "NetHack game data"),
    "NetHack-cn": ("🟡", "NetHack CN game data"),
    " propagation": ("🟡", "Propagation game data"),
    "Famatech": ("🟡", "Famatech software data"),
    "dtprinter": ("🟡", "Printer driver data"),
    "regid.1991-06.com.microsoft": ("🟡", "Microsoft registration data"),
    "deepscan": ("🟡", "DeepScan software data"),
    "tianxiang": ("🟡", "Tianxiang software data"),
    "xfolder": ("🟡", "XFolder software data"),
    "leigod_person_7002": ("🟡", "Leigod accelerator data"),
    "Whesvc": ("🟡", "Whesvc service data"),
    "Packer": ("🟡", "Packer software data"),
    "shimgen": ("🟡", "Shimgen tool data"),
    "boost_interprocess": ("🟡", "Boost interprocess data"),
    "cef_temp": ("🟡", "CEF temp data"),
    "Alibaba": ("🟡", "Alibaba app data"),
    "Ximalaya SetUp": ("🟡", "Ximalaya setup data"),
    "ABBYY": ("🟡", "ABBYY OCR data"),
    "Oracle": ("🟡", "Oracle Java/data"),
    "Microsoft OneDrive": ("🟡", "OneDrive setup cache"),
    "Microsoft DevDiv": ("🟡", "MS DevDiv data"),
    "Logishrd": ("🟡", "Logitech software data"),
    "Blizzard Entertainment": ("🟡", "Blizzard game data"),
    "AntiCheatExpert": ("🟡", "Anti-cheat system data"),
    "eaanticheat": ("🟡", "EA anti-cheat data"),
    "GameSessionTelemetry": ("🟡", "NVIDIA game telemetry"),
    "GfnRuntimeSdk": ("🟡", "NVIDIA GeForce NOW SDK"),
    "NvTelemetry": ("🟡", "NVIDIA telemetry data"),
    "NvProfileUpdaterPlugin": ("🟡", "NVIDIA profile updater"),
    "NvVAD": ("🟡", "NVIDIA audio driver"),
    "RX": ("🟡", "AMD RX driver data"),
    "ShadowPlay": ("🟡", "NVIDIA ShadowPlay data"),
    "umdlogs": ("🟡", "UMD driver logs"),
    "FrameViewSDK": ("🟡", "NVIDIA FrameView SDK"),
    "DisplayDriverRAS": ("🟡", "NVIDIA display RAS"),
    "CrashDumps": ("🟡", "Crash dump files"),
    "Drs": ("🟡", "NVIDIA driver settings"),
    "Downloader": ("🟡", "NVIDIA downloader cache"),
    "NVIDIA app": ("🟡", "NVIDIA App data"),
    "NVIDIA GeForce Experience": ("🟡", "GeForce Experience data"),
    "nvtopps": ("🟡", "NVIDIA TOPS data"),
    "QQDownload": ("🟡", "QQ Download cache"),
    "QQPCMgr": ("🟢", "QQ PC Manager data (safe if not using)"),
    "WeType": ("🟢", "WeChat Input Method data (safe if not using)"),
    "WeChat": ("🟡", "WeChat PC global data"),
    "QQ": ("🟡", "QQ global data"),
    "TXSSO": ("🟡", "Tencent SSO data"),
    "TSVulFw": ("🟡", "Tencent vulnerability firewall"),
    "qimei": ("🟡", "Tencent QIMEI data"),
    "DeskUpdate": ("🟡", "DeskUpdate tool data"),
    "OD": ("🟡", "Tencent OD data"),
    "WemeetUpdateSvc": ("🟡", "Tencent Meeting update service"),
    "WeMail": ("🟡", "Tencent WeMail data"),
    "wwuni": ("🟡", "Tencent wwuni data"),
    "valorant.live": ("🟡", "Valorant Live data"),
}

# Subfolder classification for Tencent
TENCENT_SUBFOLDERS = {
    "QQPCMgr": ("🟢", "QQ PC Manager"),
    "WeType": ("🟢", "WeChat Input Method"),
    "valorant.live": ("🟡", "Valorant (Tencent anti-cheat)"),
    "WeChat": ("🟡", "WeChat global config"),
    "QQ": ("🟡", "QQ global config"),
    "QQDownload": ("🟡", "QQ Download manager"),
    "WemeetUpdateSvc": ("🟡", "Tencent Meeting"),
    "WeMail": ("🟡", "Tencent Mail"),
}


def get_size(path: str) -> int:
    """Get total size of all files under path."""
    total = 0
    try:
        for root, _dirs, files in os.walk(path):
            for f in files:
                try:
                    total += os.path.getsize(os.path.join(root, f))
                except OSError:
                    pass
    except OSError:
        pass
    return total


def classify(name: str, parent: str = None) -> tuple:
    """Return (emoji, description) for a folder name."""
    if parent and parent.lower() == "tencent":
        if name in TENCENT_SUBFOLDERS:
            return TENCENT_SUBFOLDERS[name]
    if name in CLASSIFICATION:
        return CLASSIFICATION[name]
    return ("🟡", "Unknown — review before deleting")


def main():
    target = r"C:\ProgramData"
    print(f"Scanning: {target}")
    print("=" * 70)

    entries = []
    try:
        for entry in os.scandir(target):
            if not entry.is_dir(follow_symlinks=False):
                continue
            name = entry.name
            if name.startswith("$") or name in {"System Volume Information"}:
                continue
            sz = get_size(entry.path)
            if sz > 10 * 1024 * 1024:  # Only show > 10 MB
                entries.append((name, sz))
    except PermissionError:
        print("Permission denied on some folders.")

    entries.sort(key=lambda x: x[1], reverse=True)

    print("Folder".ljust(40) + "Size".rjust(10) + "Risk".rjust(6) + "  Description")
    print("-" * 70)

    for name, sz in entries:
        emoji, desc = classify(name)
        gb = sz / (1024 ** 3)
        mb = sz / (1024 ** 2)
        size_str = f"{gb:>5.2f} GB" if gb >= 0.5 else f"{mb:>6.0f} MB"
        safe_name = name.encode("ascii", "replace").decode("ascii")[:38]
        safe_emoji = emoji.encode('ascii', 'replace').decode('ascii')
        print(f"{safe_name:<40} {size_str:>10} {safe_emoji:>6}  {desc}")

    # Also scan Tencent subfolders if present
    tencent_path = os.path.join(target, "Tencent")
    if os.path.exists(tencent_path):
        print("\n--- Tencent subfolders ---")
        tencent_entries = []
        try:
            for entry in os.scandir(tencent_path):
                if not entry.is_dir(follow_symlinks=False):
                    continue
                sz = get_size(entry.path)
                if sz > 10 * 1024 * 1024:
                    tencent_entries.append((entry.name, sz))
        except PermissionError:
            pass
        tencent_entries.sort(key=lambda x: x[1], reverse=True)
        for name, sz in tencent_entries:
            emoji, desc = classify(name, parent="Tencent")
            gb = sz / (1024 ** 3)
            mb = sz / (1024 ** 2)
            size_str = f"{gb:>5.2f} GB" if gb >= 0.5 else f"{mb:>6.0f} MB"
            safe_name = name.encode("ascii", "replace").decode("ascii")[:38]
            safe_emoji = emoji.encode('ascii', 'replace').decode('ascii')
        print(f"  {safe_name:<38} {size_str:>10} {safe_emoji:>6}  {desc}")

    print("=" * 70)
    total = sum(x[1] for x in entries)
    print(f"Total scanned: {len(entries)} folders | Sum: {total / (1024**3):.2f} GB")


if __name__ == "__main__":
    main()
