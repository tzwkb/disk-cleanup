# Safe Windows Temp Cleanup
# This script cleans known-safe temporary/cache locations.
# Preview mode: set $WhatIf = $true to see what would be deleted without removing anything.

param([switch]$WhatIf, [switch]$IncludeWinSxS)

$totalFreed = 0
$actions = @()

function Remove-SafePath($path, $label) {
    if (-not (Test-Path $path)) { return }
    $sz = 0
    try {
        $sz = (Get-ChildItem $path -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
    } catch {}
    
    if ($sz -gt 0) {
        $actions += [PSCustomObject]@{ Label = $label; Path = $path; SizeMB = [math]::Round($sz/1MB,1) }
        if (-not $WhatIf) {
            Get-ChildItem $path -Force -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
        }
        $script:totalFreed += $sz
    }
}

# 1. User Temp
Remove-SafePath $env:TEMP "User Temp"

# 2. Windows Temp
Remove-SafePath "C:\Windows\Temp" "Windows Temp"

# 3. Edge Cache
Remove-SafePath "$env:LOCALAPPDATA\Microsoft\Edge\User Data\Default\Cache" "Edge Cache"

# 4. Chrome Cache
Remove-SafePath "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Cache" "Chrome Cache"

# 5. Pip Cache
$pipCache = & python -m pip cache dir 2>$null
if ($pipCache -and (Test-Path $pipCache)) {
    $sz = (Get-ChildItem $pipCache -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
    if ($sz -gt 0) {
        $actions += [PSCustomObject]@{ Label = "Pip Cache"; Path = $pipCache; SizeMB = [math]::Round($sz/1MB,1) }
        if (-not $WhatIf) {
            & python -m pip cache purge 2>$null | Out-Null
        }
        $totalFreed += $sz
    }
}

# 6. Windows Update Download Cache (if any)
Remove-SafePath "C:\Windows\SoftwareDistribution\Download" "Windows Update Cache"

# 7. WinSxS Component Store Cleanup (optional, requires admin but safe)
if ($IncludeWinSxS) {
    Write-Host "Analyzing WinSxS component store..." -ForegroundColor Cyan
    $analysis = dism /Online /Cleanup-Image /AnalyzeComponentStore 2>$null
    $reclaimLine = $analysis | Select-String "Component Store Cleanup Recommended"
    if ($reclaimLine -match "Yes") {
        $actions += [PSCustomObject]@{ Label = "WinSxS Analysis"; Path = "C:\Windows\WinSxS"; SizeMB = 0; Note = "Cleanup recommended by DISM" }
        if (-not $WhatIf) {
            Write-Host "Starting WinSxS cleanup (this may take 5-10 minutes)..." -ForegroundColor Yellow
            dism /Online /Cleanup-Image /StartComponentCleanup | Out-Null
            $actions += [PSCustomObject]@{ Label = "WinSxS Cleanup"; Path = "C:\Windows\WinSxS"; SizeMB = 0; Note = "Completed" }
        }
    } else {
        $actions += [PSCustomObject]@{ Label = "WinSxS Analysis"; Path = "C:\Windows\WinSxS"; SizeMB = 0; Note = "Cleanup not recommended currently" }
    }
}

# Report
if ($WhatIf) {
    Write-Host "PREVIEW MODE - No files were deleted." -ForegroundColor Yellow
} else {
    Write-Host "CLEANUP COMPLETE" -ForegroundColor Green
}

if ($actions.Count -gt 0) {
    $actions | Format-Table -AutoSize
    Write-Host "Total temp/cache freed: $([math]::Round($totalFreed/1MB,1)) MB"
} else {
    Write-Host "Nothing to clean."
}
