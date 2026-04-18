---
name: disk-cleanup-master
description: Windows 磁盘空间分析与清理专家。当用户遇到 C 盘满了、磁盘空间不足、需要清理硬盘、分析大文件、整理系统垃圾、迁移用户目录（Documents/Desktop/Downloads）、清理微信/QQ/网易云/WPS 等国产软件缓存、整理 Python 全局 pip 环境、分析 Steam/WeGame 游戏库空间时触发。覆盖 Windows 10/11 系统。核心原则：扫描激进，删除保守，所有删除操作必须经用户确认。
---

# Disk Cleanup Master — Windows 硬盘清理大师

## 核心原则（不可违背）

1. **扫描激进，删除保守**
   - 扫描阶段：大胆遍历、全面排查，不怕多报
   - 删除阶段：每个操作必须向用户展示具体内容、大小、风险，获得明确确认后才执行
2. **红绿灯安全模型**
   - 🟢 绿灯（可安全删除）：Temp、浏览器缓存、pip cache、`__pycache__`、旧安装包残留、应用明确标注的 Cache/Log、WinSxS 旧组件
   - 🟡 黄灯（需用户确认）：游戏存档、微信/QQ 记录、WPS 云盘文件、下载文件夹中的个人文件、ProgramData 里的应用全局数据
   - 🔴 红灯（禁止擅自删除）：Windows 系统目录、Program Files、用户正在使用的项目文件、未备份的数据
3. **国产软件特殊处理**
   - 腾讯系（微信/QQ/企业微信）、网易系、WPS、百度系普遍硬编码路径，不遵循 Windows Known Folders API
   - 绝不能直接剪切/重命名它们的文件夹，必须在软件设置里改路径
   - 详见 `references/chinese-app-special-cases.md`

## 标准工作流程

### Step 1: 全景扫描（激进）
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
# 按关键词搜索文件夹名（深度 6 层，不计算大小，极速）
python scripts/find_folders_by_keyword.py "D:\\" "Call of Duty|COD|Modern Warfare"
```

### Step 2: 分类与风险评估
- 将扫描结果按 🟢🟡🔴 分类
- 对黄灯项标注具体风险（如"微信 Backup 33 GB，删后换手机无法恢复"）
- 对红灯项直接排除，不做任何操作

### Step 3: 向用户呈现报告
- 用表格展示：区域、大小、风险等级、建议操作
- 让用户勾选或明确回复"删哪些"
- **禁止**在未经用户逐条确认的情况下执行批量删除

### Step 4: 执行清理
- 绿灯项：可直接执行，但执行后需汇报结果
- 黄灯项：用户确认一条，执行一条
- 执行前优先使用 `--dry-run` 或预览模式

### Step 5: 验证
- 清理后重新检查磁盘空间
- 对迁移操作（如 Documents 迁移）做写入测试验证路径正确性

## C 盘专项清理指南

### 系统级安全清理（绿灯）
```powershell
# 临时文件
$env:TEMP                    # 用户临时文件
C:\Windows\Temp              # 系统临时文件
C:\Windows\SoftwareDistribution\Download  # Windows Update 缓存

# 浏览器缓存
$env:LOCALAPPDATA\Microsoft\Edge\User Data\Default\Cache
$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Cache

# 回收站
C:\$Recycle.Bin

# 休眠文件（如用户不用休眠功能）
# powercfg /hibernate off
```

### WinSxS 组件存储清理（高价值绿灯）
WinSxS (`C:\Windows\WinSxS`) 是 Windows 的系统组件仓库，每次更新会保留旧版本以便回滚。长期累积可达 10-20 GB。

**分析可回收空间：**
```powershell
dism /Online /Cleanup-Image /AnalyzeComponentStore
```

**执行清理（安全，推荐）：**
```powershell
dism /Online /Cleanup-Image /StartComponentCleanup
```
- 清理后无法卸载已安装的 Windows 更新（实际影响极小）
- 通常可回收 **几百 MB ~ 数 GB**
- 耗时 3-10 分钟，可后台运行

**更激进的清理（谨慎）：**
```powershell
dism /Online /Cleanup-Image /StartComponentCleanup /ResetBase
```
- 释放更多空间，但彻底无法回滚任何更新
- 仅在磁盘极度紧张时考虑

### Python 全局环境整理
- `pip list --format=freeze` 查看总包数
- `pip list --not-required` 找出用户直接安装的顶层包（通常远少于总包数）
- `pip check` 检查依赖冲突
- `pip cache purge` 清理 pip 下载缓存
- 清理 `site-packages` 中 `~` 开头的损坏安装残留
- 清理所有 `__pycache__` 文件夹：`Get-ChildItem -Path $sitePackages -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force`
- **注意**：修复依赖冲突时可能遇到互斥包（如 pyjwt 版本被两个包同时要求不同范围），需用户决定保留哪个

### AppData 定向扫描
AppData 是 C 盘隐藏大户，通常分为：
- `Local`：程序缓存、运行时数据（可清理空间大）
- `Roaming`：用户配置、聊天记录（谨慎处理）
- `LocalLow`：低权限应用数据（通常不大）

常见大项：
- `Local\Netease\CloudMusic\Cache` — 网易云音乐缓存（可删）
- `Roaming\Kingsoft\office6\backup` — WPS 崩溃备份（可删）
- `Roaming\Tencent` — 微信 PC 版数据（黄灯，见 reference）

### ProgramData 定向扫描
ProgramData 是**容易被忽视的 C 盘大户**，存放应用的全局数据、安装缓存和设备驱动配置。

**分类策略：**

| 类别 | 典型路径 | 风险 | 示例 |
|------|---------|------|------|
| **设备驱动数据** | `NVIDIA`, `NVIDIA Corporation`, `LGHUB`, `ASUS` | 🔴 不动 | 删除后设备可能异常 |
| **应用全局数据** | `Tencent`, `anaconda3`, `0install.net` | 🟡 确认后删 | 不用该应用时可删 |
| **安装缓存** | `Package Cache`, `Microsoft\VisualStudio` | 🟡 谨慎 | 删除后可能无法卸载/修复程序 |
| **系统数据** | `Microsoft\Windows Defender`, `Microsoft\Search` | 🔴 不动 | 系统核心组件 |

**扫描命令：**
```powershell
# 推荐用脚本扫描，避免单条命令超时
python scripts/scan_programdata.py
```

**常见可清理项：**
- `anaconda3` — 如果已改用其他 Python 环境，可卸载（通常 3-8 GB）
- `0install.net` — Zero Install 包管理器数据，不用时可删（通常几百 MB）
- `Tencent\QQPCMgr` — QQ 电脑管家数据（如不用可删）
- `Tencent\WeType` — 微信输入法数据（如不用可删）

## 大应用卸载流程（黄灯 → 绿灯）

对于 ProgramData 或 Program Files 中发现的大应用残留，**不要直接删除文件夹**，应走正规卸载流程：

1. **查注册表找卸载程序**
   ```powershell
   Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*" |
     Where-Object { $_.DisplayName -match "Anaconda" }
   ```

2. **静默卸载（NSIS 安装器）**
   ```powershell
   & "C:\ProgramData\anaconda3\Uninstall-Anaconda3.exe" /S
   ```
   - **注意**：`/S` 启动后可能**立即返回**，不会等待卸载完成
   - 必须轮询检查文件夹是否消失：
   ```powershell
   while (Test-Path "C:\ProgramData\anaconda3") { Start-Sleep -Seconds 10 }
   ```

3. **清理残留**
   - 检查并删除残留文件夹
   - 检查 PATH 环境变量：
   ```powershell
   [Environment]::GetEnvironmentVariable("Path", "User") -split ";" | Select-String "anaconda"
   [Environment]::GetEnvironmentVariable("Path", "Machine") -split ";" | Select-String "anaconda"
   ```

4. **删除顽固文件夹的最后手段：Robocopy Empty Trick**
   当 `Remove-Item -Force` 和 `takeown + icacls` 都失败时：
   ```powershell
   $empty = "C:\temp_empty_$(Get-Random)"
   New-Item -ItemType Directory -Path $empty -Force | Out-Null
   robocopy $empty "C:\ProgramData\0install.net" /MIR /R:1 /W:1 /NP /NFL /NDL
   Remove-Item $empty -Force
   Remove-Item "C:\ProgramData\0install.net" -Force
   ```
   - **原理**：用空文件夹镜像覆盖目标，强制清空内容
   - **警告**：`robocopy /MIR` 会彻底清空目标，方向绝不能反！

## 用户目录迁移

### Windows 标准文件夹（Documents / Desktop / Downloads / Pictures / Videos）
- **正确做法**：右键文件夹 → 属性 → 位置 → 移动
- 这是系统级重定向，程序通过 API 获取路径时会自动指向新位置
- 迁移后旧文件夹如被锁定无法删除，可重启后再处理

### 第三方应用数据
- **错误做法**：直接剪切 AppData 或 Documents 里的应用文件夹到新盘
- **正确做法**：进各软件设置里修改"文件管理/存储位置"，让软件自己迁移
- 例外：Steam 游戏库可在 Steam 设置里添加/迁移库文件夹

## 游戏库存分析

### Steam
- 库文件夹：`steamapps\common\`（游戏本体）
- 未完成下载：`steamapps\downloading\`（可安全删）
- 创意工坊：`steamapps\workshop\`（取消订阅后可手动清理）
- 卸载游戏必须走 Steam 客户端，不要直接删文件夹

### WeGame
- 平台数据：`WEGAME\`
- 游戏数据：`WeGameApps\rail_apps\`
- 常见大游戏：LOL（~40-50 GB）、Valorant（~30 GB）

## 常见陷阱与经验

1. **robocopy /MIR 风险**
   - `/MIR` 等于镜像同步，会删除目标端多余文件，用错方向会清空数据
   - 大目录操作可能超时，但 robocopy 进程会继续在后台运行，导致后续 IO 卡死
   - **处理**：操作后检查残留 `Get-Process robocopy`，必要时强制终止

2. **Robocopy Empty Trick（删除顽固文件夹）**
   - 当文件被锁定、权限不足、`takeown` 也失败时，可用空文件夹 + `/MIR` 强制清空目标
   - **必须**：先创建独立空文件夹作为源，确认目标路径正确后再执行
   - **绝不能**把系统目录（如 `C:\Windows`）作为目标

3. **扫描输出污染**
   - 单条 Shell 命令中并行运行多个 `Get-ChildItem | Format-Table`，输出流可能混淆（如 `NVIDIA Corporation` 的结果里混入 `Tencent` 文件夹）
   - **处理**：一次只扫描一个目录，或用 Python 脚本做统一输出

4. **NSIS 卸载程序异步行为**
   - 带 `/S` 参数的静默卸载程序启动后可能**立即返回**，不会阻塞等待完成
   - **处理**：启动后轮询检查安装目录是否消失，或检查进程列表

5. **文件锁定**
   - 微信、WPS、QQ 等常驻后台软件会锁定自己的数据文件，导致文件夹无法重命名/删除
   - **处理**：先关闭对应进程（包括守护进程），再操作

6. **Unicode 文件名**
   - Windows 中文文件名在 PowerShell/Python 中容易导致编码错误
   - **处理**：Python 脚本中使用 `.encode('ascii', 'replace').decode('ascii')` 安全输出

7. **Measure-Object -Sum 超时**
   - 对包含数十万文件的目录（如微信缓存、游戏资源），`Get-ChildItem -Recurse` 配合 `Measure-Object` 可能超时
   - **处理**：改用 `robocopy $path \NULL /L /S /NJH /NJS /BYTES` 统计，或限制扫描深度

8. **大目录搜索的终极策略（分层 + 关键词）**
   - `Get-ChildItem -Recurse` 和 `robocopy /L /S` 在 Steam 游戏库、整个磁盘扫描时都会超时
   - **处理**：
     1. **粗筛**：用 `os.scandir` 只扫根目录下 >5GB 的文件夹，瞬间完成
     2. **钻取**：对大户用 `tree_size_scanner.py` 层层深入
     3. **定向搜索**：用 `find_folders_by_keyword.py` 做深度受限（≤6 层）的目录名关键词匹配，**不计算大小**，避免超时
     4. 以上三步都找不到，才考虑全盘递归

## 脚本工具清单

- `scripts/tree_size_scanner.py <path> [min_mb] [max_depth]` — **分层钻取扫描**，从根目录层层深入最大文件夹，生成磁盘占用地图
- `scripts/scan_large_folders.py <path>` — 快速扫描指定路径下的大文件夹（深度限制防超时）
- `scripts/scan_programdata.py` — 定向扫描 C:\ProgramData，按安全等级分类输出大文件夹
- `scripts/find_folders_by_keyword.py <path> <pattern>` — 按关键词深度搜索文件夹名（深度 6 层，不计算大小，极速）
- `scripts/find_zombie_packages.py` — 分析全局 pip 环境，列出顶层包和依赖冲突
- `scripts/cleanup_temp.ps1 [-WhatIf]` — 安全清理 Temp、浏览器缓存、pip cache、WinSxS（支持预览模式）
- `scripts/robocopy_wipe.py <target>` — 用 robocopy empty trick 删除顽固文件夹（带路径安全检查）

## 输出模板

向用户汇报时，使用以下表格模板：

| 区域 | 大小 | 风险 | 建议 |
|------|------|------|------|
| ... | ... | 🟢/🟡/🔴 | ... |

清理后报告：

| 盘符 | 清理前可用 | 清理后可用 | 释放空间 |
|------|-----------|-----------|---------|
| ... | ... | ... | ... |
