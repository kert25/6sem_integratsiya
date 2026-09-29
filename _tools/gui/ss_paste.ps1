# ss_paste.ps1 - put text on clipboard and Ctrl+V into foreground window (-App to activate first)
# usage: powershell -File ss_paste.ps1 "<text>" [-App Postman] [-Enter] [-Sleep ms]
param(
    [string]$Text,
    [string]$App = "",
    [switch]$Enter,
    [int]$Sleep = 300
)
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class F2 {
    [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int cmd);
}
"@
$null = [F2]::SetProcessDPIAware()
if ($App) {
    $proc = Get-Process | Where-Object { $_.MainWindowHandle -ne 0 -and $_.MainWindowTitle -like "*$App*" } | Select-Object -First 1
    if ($proc) {
        $null = [F2]::ShowWindow($proc.MainWindowHandle, 9)
        $null = [F2]::SetForegroundWindow($proc.MainWindowHandle)
        Start-Sleep -Milliseconds $Sleep
    }
}
Add-Type -AssemblyName System.Windows.Forms
Set-Clipboard -Value $Text
Start-Sleep -Milliseconds 200
[System.Windows.Forms.SendKeys]::SendWait("^v")
if ($Enter) {
    Start-Sleep -Milliseconds 400
    [System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
}
Write-Output "pasted ($($Text.Length) chars)"
