# 国产软件存储行为参考

## 核心原则

国产软件（腾讯系、网易系、WPS、百度系）普遍**不遵循 Windows Known Folders API**，喜欢硬编码路径。迁移或清理时必须特殊处理。

---

## 微信（WeChat / 微信PC版）

### 路径结构
- 默认：`C:\Users\<user>\Documents\WeChat Files\`
- 用户可能自定义到 `D:\xwechat_files` 等位置
- 包含三个关键子目录：
  - `wxid_xxxxxxxx` — **电脑微信正在使用的数据库**（聊天记录、图片、文件）
  - `Backup` — **手机微信的打包备份**，电脑微信日常不读取
  - `old_backup` — 旧版备份残留

### Backup vs wxid_... 的本质区别
| | wxid_... | Backup |
|---|---|---|
| 给谁用的 | 电脑微信日常运行 | 手机微信的灾难恢复 |
| 电脑能直接看吗 | ✅ 能，电脑微信直接读取 | ❌ 不能，是加密打包的 |
| 删除后果 | 电脑记录全丢 | 手机坏了/换机时无法恢复旧记录 |
| 大小 | 通常几GB到十几GB | 可能几十GB（累积多次备份） |

### 官方功能逻辑
- **迁移（导出到电脑 / 迁移到电脑）**：手机记录合并进电脑的 `wxid_...` 数据库，电脑可直接查看
- **备份与恢复（备份到电脑）**：手机记录打包成 `Backup` 文件夹，电脑不能看，只有"恢复"时才传回手机

### 操作禁忌
- **绝不能**直接把 `WeChat Files` 文件夹从 C 盘剪切到 D/E 盘，微信会找不到
- **正确做法**：在微信客户端 → 设置 → 文件管理 → 更改存储路径，让微信自己搬
- 换电脑时：复制整个 `WeChat Files` 文件夹到新电脑，或通过微信官方"迁移到另一台电脑"

---

## QQ（PC版）

### 路径结构
- 默认：`C:\Users\<user>\Documents\Tencent Files\<QQ号>\`
- 核心文件：
  - `Msg3.0.db` — 聊天记录主数据库（可能几个GB）
  - `Image` / `Video` / `FileRecv` — 接收的图片、视频、文件
  - `CustomFace` — 自定义表情

### 操作要点
- QQ 的存储路径可在设置里修改（设置 → 文件管理 → 更改目录）
- 直接剪切文件夹会导致记录丢失，必须走官方设置迁移
- `Msg3.0.db` 是单文件数据库，非常容易被锁定

---

## 企业微信

### 路径结构
- 默认：`C:\Users\<user>\Documents\WXWork\`
- 与微信完全独立，互不通数据
- 包含企业聊天记录、文件、微盘缓存

### 操作要点
- 同样支持设置里修改存储路径
- `WXWork` 和 `WeChat Files` 是两个世界，不要混淆

---

## 腾讯系在 ProgramData 的残留

腾讯软件除了在用户目录（Documents/AppData）存放数据外，还在 `C:\ProgramData\Tencent` 和 `C:\ProgramData\NVIDIA Corporation`（部分腾讯游戏/组件）放置全局数据。

### C:\ProgramData\Tencent 常见子项
| 子文件夹 | 大小 | 说明 | 可删？ |
|---------|------|------|--------|
| `WeType` | ~100-400 MB | **微信输入法**全局数据 | 🟢 不用该输入法时可删 |
| `QQPCMgr` | ~100-200 MB | **QQ电脑管家**全局数据 | 🟢 不用电脑管家时可删 |
| `valorant.live` | ~20-50 MB | 无畏契约反作弊/启动数据 | 🟡 如仍玩游戏则保留 |
| `WeChat` | ~0-10 MB | 微信全局配置（非聊天记录） | 🟡 保留 |
| `QQ` | ~0-5 MB | QQ 全局配置 | 🟡 保留 |
| `QQDownload` | 可变 | QQ 下载管理器缓存 | 🟢 可清空 |
| `WemeetUpdateSvc` | ~0-5 MB | 腾讯会议更新服务 | 🟡 保留 |
| `WeMail` | ~0-5 MB | 腾讯邮箱数据 | 🟡 保留 |

### 注意
- `C:\ProgramData\Tencent` 下的数据通常是**全局配置和缓存**，真正的聊天记录和接收文件在用户目录的 `Documents\Tencent Files\` 里
- 删除 ProgramData 下的 Tencent 子项**不会**影响聊天记录，但可能影响输入法词库、电脑管家配置等

---

## 网易云音乐

### 路径结构
- 缓存：`%LOCALAPPDATA%\Netease\CloudMusic\Cache\`
- 下载的音乐：`%LOCALAPPDATA%\Netease\CloudMusic\Library\`
- 更新安装包残留：`%LOCALAPPDATA%\Netease\CloudMusic\update\`

### 可安全清理
- `Cache` 文件夹（可能几GB）— 在线听歌缓存
- `update` 文件夹 — 更新包残留
- `Library` 里的下载音乐需确认后再删

---

## WPS

### 路径结构
- 用户数据：`%APPDATA%\Kingsoft\office6\`
- 崩溃备份：`%APPDATA%\Kingsoft\office6\backup\`
- 临时文件：`%APPDATA%\Kingsoft\office6\temp\`
- 云盘本地缓存：`%USERPROFILE%\Documents\WPSDrive\`

### 可安全清理
- `backup` — 崩溃自动保存的临时文件
- `temp` — 临时文件
- WPS 云盘的下载缓存（如果文件已在云端）

### 注意
- WPS 云盘（WPSDrive）可能占用大量空间，文件可能同时存在本地和云端
- WPS 可能锁定 Documents 下的文件，导致文件夹无法重命名/删除

---

## 百度网盘

### 路径结构
- 安装目录默认：`C:\Users\<user>\AppData\Roaming\baidu\BaiduNetdisk\` 或用户自定义
- **坑点**：百度网盘的"下载目录"和"安装目录"可能混在一起，用户容易把下载的大文件放在安装目录下
- 常见大文件：
  - 下载的安装包（如 Adobe Premiere、游戏安装包）
  - 下载的视频/音乐

### 操作要点
- 优先检查安装目录里是否有用户下载的大文件（.rar, .zip, .exe, .mp4 等）
- 程序本体（.dll, .exe）不要删

---

## 钉钉 / 飞书 / Lark

### 路径结构
- 钉钉：`%LOCALAPPDATA%\DingTalk\` 和 `%USERPROFILE%\Documents\DingTalk\`
- 飞书：`%LOCALAPPDATA%\Feishu\` 和 `%APPDATA%\LarkShell\`
- 缓存通常位于 `%LOCALAPPDATA%` 下的应用文件夹

### 操作要点
- 办公软件的缓存可能包含未下载完的文件或历史文档缓存
- 钉钉/飞书的聊天记录云端同步较多，本地缓存相对不那么重要
- 但仍建议保守清理，只清明确标为 Cache/Temp 的文件夹

---

## Steam / WeGame / Epic

### Steam
- 库文件夹：`steamapps\common\` 里是游戏本体
- `steamapps\downloading\` — 下载中/未完成的游戏
- `steamapps\workshop\` — Steam 创意工坊订阅内容
- `userdata\` — 游戏存档和云同步数据

### WeGame
- 平台数据：`WEGAME\` 目录
- 游戏数据：`WeGameApps\rail_apps\`
- 常见游戏：LOL（英雄联盟）、Valorant（无畏契约）

### 操作要点
- 卸载游戏请走平台（Steam/WeGame）自带卸载，不要直接删文件夹，否则注册表残留
- `downloading` 里的未完成下载可以直接删
- 创意工坊内容如果取消订阅，可以手动清理

---

## 通用识别模式

### 名字带这些的通常是缓存/可删
- `Cache`, `Temp`, `tmp`, `log`, `logs`, `download`, `update`, `backup`

### 名字带这些的通常是核心数据/慎动
- `saves`, `savegames`, `profiles`, `config`, `db`, `database`, `msg`, `record`

### `.dist-info` 和 `.egg-info`
- Python 包的元数据目录，卸载包后可能残留空目录，可以清理

---

## 容易被遗忘的大户（ProgramData）

用户在清理时往往只关注 `AppData` 和 `Documents`，而忽略 `C:\ProgramData`。

### Anaconda
- 路径：`C:\ProgramData\anaconda3`（如果为所有用户安装）
- 大小：通常 **3-8 GB**
- 说明：完整的 Python 发行版，包含 `Lib`、`Library`、`envs`、`pkgs`
- **如已改用其他 Python 环境，可卸载**（用 `Uninstall-Anaconda3.exe /S`，不要直接删文件夹）

### 0install.net
- 路径：`C:\ProgramData\0install.net`
- 大小：通常 **几百 MB**
- 说明：Zero Install 包管理器的全局仓库，常见托管应用如 DeepL
- **如不再使用 0install 管理的应用，可删除**

### NVIDIA / NVIDIA Corporation
- 路径：`C:\ProgramData\NVIDIA` 和 `C:\ProgramData\NVIDIA Corporation`
- 说明：驱动安装缓存、配置文件、ShadowPlay 数据
- **一般不动**，但 `Downloader` 子目录可能包含旧驱动安装包
