# shot_window.ps1 - maximize window, bring to front, screenshot via ss_ocr.ps1, then close tab/window
# usage: powershell -File shot_window.ps1 -App "<title>" -Path out.png [-Close tab|window|none] [-WaitSec 2]
#   -Close tab    : activate window + Ctrl+W (default; for Edge tabs; last tab closes the app)
#   -Close window : Stop-Process (for console windows of runs, e.g. titled LR5-pytest)
#   -Close none   : leave window open (exceptional; window overlaps the agent chat in Zed)
# Save path: RELATIVE ASCII path from the caller's workdir (Cyrillic -Path in args gets mangled).
param(
    [Parameter(Mandatory = $true)][string]$App,
    [Parameter(Mandatory = $true)][string]$Path,
    [ValidateSet("tab", "window", "none")]
    [string]$Close = "tab",
    [int]$WaitSec = 2
)
$ErrorActionPreference = "Stop"

Add-Type @"
using System;
using System.Runtime.InteropServices;
public class W32s {
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int cmd);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
}
"@

$proc = Get-Process |
    Where-Object { $_.MainWindowHandle -ne 0 -and $_.MainWindowTitle -like "*$App*" } |
    Select-Object -First 1
if (-not $proc) { Write-Output "ERROR: window not found: $App"; exit 1 }
$hwnd = $proc.MainWindowHandle

# 1) maximize + bring to front + let it repaint
$null = [W32s]::ShowWindow($hwnd, 3)          # SW_MAXIMIZE
$null = [W32s]::SetForegroundWindow($hwnd)
Start-Sleep -Seconds $WaitSec

# 2) screenshot (isolated child run of ss_ocr.ps1)
$ocrScript = Join-Path $PSScriptRoot "ss_ocr.ps1"
$ocr = & powershell -NoProfile -ExecutionPolicy Bypass -File $ocrScript -App $App -Path $Path
if ($LASTEXITCODE -ne 0) { Write-Output "ERROR: ss_ocr failed for: $App"; exit 1 }
$words = 0
try { $words = @($ocr | ConvertFrom-Json).Count } catch { $words = -1 }

# 3) close as requested
if ($Close -eq "tab") {
    $null = [W32s]::SetForegroundWindow($hwnd)
    Start-Sleep -Milliseconds 500
    (New-Object -ComObject WScript.Shell).SendKeys("^w")
    $closeMsg = "tab closed (Ctrl+W)"
} elseif ($Close -eq "window") {
    Stop-Process -Id $proc.Id -Force
    $closeMsg = "window closed (pid $($proc.Id))"
} else {
    $closeMsg = "left open"
}

Write-Output "OK: screenshot saved: $Path (ocr words: $words) | $App | $closeMsg"
