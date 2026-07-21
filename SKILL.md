---
name: disk-cleanup-master
description: 跨平台磁盘空间分析与清理专家（Windows + macOS）。当用户遇到 C 盘 / 磁盘空间不足、需要清理硬盘、分析大文件、整理系统垃圾、迁移用户目录、清理微信/QQ/网易云/WPS 等国产软件缓存、整理 Python 全局 pip 环境、分析 Steam/WeGame 游戏库空间时触发。覆盖 Windows 10/11 与 macOS（Intel / Apple Silicon，APFS）。核心原则：扫描激进，删除保守；macOS 下仅做只读扫描、不执行删除。
---

# Disk Cleanup Master — 跨平台磁盘清理大师（Windows + macOS）

> **平台说明**：脚本自动识别系统（`sys.platform`）。Windows 保留完整「扫描 + 确认后删除」能力；**macOS 下本技能只做只读扫描与报告，绝不执行删除**，删除决策完全交给用户。

## 核心原则（不可违背）

1. **扫描激进，删除保守**
   - 扫描阶段：大胆遍历、全面排查，不怕多报
   - 删除阶段：每个操作必须向用户展示具体内容、大小、风险，获得明确确认后才执行
   - **macOS 例外（硬性）**：macOS 下本技能**永远不执行删除 / 移动 / 清空回收站**。即使用户说「go / 跑 / 可以」，macOS 路径也只输出「路径 + 大小 + 风险 + 建议命令」，**由用户复制命令自行在终端执行**。删除动作绝不经由本技能触发。
2. **红绿灯安全模型**
   - 🟢 绿灯（可安全删除）：Temp、浏览器缓存、pip cache、`__pycache__`、旧安装包残留、应用明确标注的 Cache/Log、WinSxS 旧组件
   - 🟡 黄灯（需用户确认）：游戏存档、微信/QQ 记录、WPS 云盘文件、下载文件夹中的个人文件、ProgramData / `~/Library/Containers` 里的应用全局数据
   - 🔴 红灯（禁止擅自删除）：系统目录、Program Files / `/System`、用户正在使用的项目文件、未备份的数据
3. **国产软件特殊处理**
   - 腾讯系（微信/QQ/企业微信）、网易系、WPS、百度系普遍硬编码路径，不遵循系统 Known Folders API
   - 绝不能直接剪切/重命名它们的文件夹，必须在软件设置里改路径
   - Windows 详见 `references/chinese-app-special-cases.md`（含 macOS 章节）

---

## 一、Windows 工作流

### 标准工作流程

#### Step 1: 全景扫描（激进）
- 用 `Get-PSDrive` 获取各盘空间概览
- **用 `scripts/tree_size_scanner.py` 做分层钻取扫描** — 从根目录开始，按大小排序，层层深入最大文件夹，快速定位空间消耗源头
- 对 AppData、Documents、**ProgramData** 等重灾区做定向扫描
- **目标**：5 分钟内给出磁盘占用地图

**分层钻取扫描策略：**
```powershell
# C 盘全景（显示 >500MB 的文件夹，深入 4 层）
python scripts/tree_size_scanner.py "C:\\" 500 4
# D/E 盘快速定位大户
python scripts/tree_size_scanner.py "D:\\" 5000 3
```
- 先扫根目录，找到最大的几个文件夹
- 再对最大的文件夹单独深入扫描
- 系统目录（Windows、Program Files）自动跳过，防止误操作

**搜索特定应用/游戏（非平台安装）：**
```powershell
python scripts/find_folders_by_keyword.py "D:\\" "Call of Duty|COD|Modern Warfare"
```

#### Step 2: 分类与风险评估
- 将扫描结果按 🟢🟡🔴 分类
- 对黄灯项标注具体风险（如"微信 Backup 33 GB，删后换手机无法恢复"）
- 对红灯项直接排除，不做任何操作

#### Step 3: 向用户呈现报告
- 用表格展示：区域、大小、风险等级、建议操作
- 让用户勾选或明确回复"删哪些"
- **禁止**在未经用户逐条确认的情况下执行批量删除

#### Step 4: 执行清理
- 绿灯项：可直接执行，但执行后需汇报结果
- 黄灯项：用户确认一条，执行一条
- 执行前优先使用 `--dry-run` 或预览模式

#### Step 5: 验证
- 清理后重新检查磁盘空间
- 对迁移操作（如 Documents 迁移）做写入测试验证路径正确性

### C 盘专项清理指南

#### 系统级安全清理（绿灯）
```powershell
$env:TEMP                    # 用户临时文件
C:\Windows\Temp              # 系统临时文件
C:\Windows\SoftwareDistribution\Download  # Windows Update 缓存
$env:LOCALAPPDATA\Microsoft\Edge\User Data\Default\Cache
$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Cache
C:\$Recycle.Bin
```

#### WinSxS 组件存储清理（高价值绿灯）
```powershell
dism /Online /Cleanup-Image /AnalyzeComponentStore
dism /Online /Cleanup-Image /StartComponentCleanup
```

#### Python 全局环境整理
```powershell
pip list --format=freeze
pip list --not-required
pip check
pip cache purge
```

#### AppData 定向扫描
- `Local\Netease\CloudMusic\Cache` — 网易云音乐缓存（可删）
- `Roaming\Kingsoft\office6\backup` — WPS 崩溃备份（可删）
- `Roaming\Tencent` — 微信 PC 版数据（黄灯）

#### ProgramData 定向扫描
```powershell
python scripts/scan_programdata.py
```

### 大应用卸载流程（黄灯 → 绿灯）
走正规卸载流程，不要直接删除文件夹（详见原技能说明）。

### 游戏库存分析
Steam / WeGame 库文件夹分析与安全清理（见 `references/chinese-app-special-cases.md`）。

### Windows 常见陷阱与经验
1. **robocopy /MIR 风险**：方向绝不能反
2. **NSIS 卸载程序异步行为**：`/S` 后立即返回，需轮询目录是否消失
3. **扫描输出污染**：一次只扫描一个目录
4. **文件锁定**：微信/WPS/QQ 常驻后台会锁文件，先关进程
5. **Unicode 文件名**：Python 脚本统一做 ASCII 安全化
6. **Measure-Object -Sum 超时**：改用 `robocopy /L /S` 或限制深度
7. **大目录搜索终极策略**：粗筛 + 钻取 + 关键词，避免全盘递归

### Windows 脚本工具清单
- `scripts/tree_size_scanner.py <path> [min_mb] [max_depth]` — 分层钻取扫描，跳过系统目录
- `scripts/scan_large_folders.py <path>` — 快速扫描指定路径下的大文件夹（深度限制防超时）
- `scripts/scan_programdata.py` — 定向扫描 C:\ProgramData，按安全等级分类
- `scripts/find_folders_by_keyword.py <path> <pattern>` — 按关键词深度搜索文件夹名
- `scripts/find_zombie_packages.py` — 分析全局 pip 环境，列出顶层包和依赖冲突
- `scripts/cleanup_temp.ps1 [-WhatIf]` — 安全清理 Temp / 浏览器缓存 / pip cache / WinSxS（支持预览）
- `scripts/robocopy_wipe.py <target>` — 用 robocopy empty trick 删除顽固文件夹（带路径安全检查）

---

## 二、macOS 支持（只读扫描，不删除）

> macOS 下本技能**只扫描、只报告**，不执行任何 `rm` / 清空回收站 / 移动操作。
> 所有「清理建议」仅以「路径 + 大小 + 风险 + 建议命令」形式输出，**由用户复制命令自行在终端执行**。即使用户显式授权，本技能在 macOS 下也不代执行删除——删除完全由用户手动完成。

### macOS 磁盘地图要点
- 用户数据实际所在卷：`/System/Volumes/Data`（用 `df -h /System/Volumes/Data` 看可用空间）
- 最大户通常在 `~/Library`：`Caches` / `Application Support` / `Containers` / `Logs` / `Developer`
- 腾讯/字节/网易等 App 沙盒：`~/Library/Containers/<bundle-id>`（清缓存走 App 内，勿直接删容器）
- 开发缓存：`~/.npm`、`~/.cache`、`~/.gradle`、`~/.rustup`、`~/Library/Caches/Homebrew`

### macOS 只读扫描流程
```bash
# 1) 磁盘整体概览
python scripts/disk_overview.py
# 2) 用户主目录顶层
du -sh ~/Documents ~/Downloads ~/Desktop ~/Movies ~/Music ~/Pictures ~/Library
# 3) ~/Library 钻取（最大户在这里）
python scripts/scan_library.py
# 4) 开发工具缓存
du -sh ~/.npm ~/.cache ~/.gradle ~/.rustup ~/Library/Caches/Homebrew
python scripts/find_zombie_packages.py
# 5) 定向搜索特定 App / 游戏
python scripts/find_folders_by_keyword.py ~/Library "Steam|UTM|docker|xinWeChat" 6
# 6) 分层钻取任意大目录（自动跳过系统目录，跨平台脚本）
python scripts/tree_size_scanner.py ~/Library/Application\ Support 500 3
```

### macOS 红绿灯（仅标注，不执行）
- 🟢 绿灯（可再生）：`~/Library/Caches`、`~/.cache`、`~/.npm`、`~/Library/Logs`、`/private/var/folders`、Homebrew/pip/playwright 缓存
- 🟡 黄灯（需确认）：`~/Library/Containers`（微信/QQ/UTM/Docker）、`~/Library/Application Support`（Steam/Claude）、`~/Downloads`、回收站 `~/.Trash`、Docker/UTM 镜像
- 🔴 红灯（勿碰）：`~/Documents`、`~/Desktop`、`~/Pictures`、`~/Movies`、`/System`、`/Library` 系统级、正在用的项目代码

### macOS 脚本工具清单（全部只读）
- `scripts/disk_overview.py` — 各挂载卷可用空间（macOS `df`）
- `scripts/scan_library.py` — 定向扫描 `~/Library`，按安全等级分类（macOS 版「ProgramData 审计」）
- 跨平台脚本在 macOS 同样可用：`tree_size_scanner.py`、`scan_large_folders.py`、`find_folders_by_keyword.py`、`find_zombie_packages.py`

### macOS 常见陷阱（仅提示，不处理）
1. **APFS 共享块**：很多缓存块是克隆/共享块，删除后不一定释放唯一空间；报告时要区分「可再生缓存」与「真实数据」
2. **回收站锁定标志**：回收站文件可能带 `uchg`（锁定）标志，`rm -rf ~/.Trash/*` 会**静默跳过**——删除阶段（用户另行授权时）需先 `chflags -R nouchg ~/.Trash`
3. **`du` 超时**：对 Steam 库/微信缓存（数十万文件）用 `os.scandir` 分层 + 限制深度，脚本已内置深度限制
4. **权限**：`~/Library/Caches`、`~/Library/Logs` 部分子项受 SIP/TCC 保护，`PermissionError` 被忽略，不影响整体地图

---

## 输出模板

| 区域 | 大小 | 风险 | 建议 |
|------|------|------|------|
| ... | ... | 🟢/🟡/🔴 | ... |

清理后报告（Windows 执行删除后回填；macOS 仅用户自行删除后回填）：

| 盘符/卷 | 清理前可用 | 清理后可用 | 释放空间 |
|---------|-----------|-----------|---------|
| ... | ... | ... | ... |
