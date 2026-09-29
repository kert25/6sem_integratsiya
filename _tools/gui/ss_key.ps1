# ss_key.ps1 - send keys to the FOREGROUND window (activate by -App titleLike first)
# usage: powershell -File ss_key.ps1 "<SendKeys>" [-App Postman] [-Sleep ms]
param(
    [string]$Keys,
    [string]$App = "",
    [int]$Sleep = 300
)
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class F {
    [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int cmd);
}
"@
$null = [F]::SetProcessDPIAware()
if ($App) {
    $proc = Get-Process | Where-Object { $_.MainWindowHandle -ne 0 -and $_.MainWindowTitle -like "*$App*" } | Select-Object -First 1
    if ($proc) {
        $null = [F]::ShowWindow($proc.MainWindowHandle, 9)  # SW_RESTORE
        $null = [F]::SetForegroundWindow($proc.MainWindowHandle)
        Start-Sleep -Milliseconds $Sleep
    }
}
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.SendKeys]::SendWait($Keys)
Write-Output "sent: $Keys"
