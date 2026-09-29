# ss_click.ps1 - click at absolute screen coords (DPI-aware)
# usage: powershell -File ss_click.ps1 X Y [-Dbl]
param([int]$X, [int]$Y, [switch]$Dbl)
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class M {
    [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern void mouse_event(uint f, uint dx, uint dy, uint data, UIntPtr extra);
}
"@
$null = [M]::SetProcessDPIAware()
$null = [M]::SetCursorPos($X, $Y)
Start-Sleep -Milliseconds 120
$null = [M]::mouse_event(0x0002, 0, 0, 0, [UIntPtr]::Zero)  # LEFTDOWN
Start-Sleep -Milliseconds 60
$null = [M]::mouse_event(0x0004, 0, 0, 0, [UIntPtr]::Zero)  # LEFTUP
if ($Dbl) {
    Start-Sleep -Milliseconds 80
    $null = [M]::mouse_event(0x0002, 0, 0, 0, [UIntPtr]::Zero)
    Start-Sleep -Milliseconds 60
    $null = [M]::mouse_event(0x0004, 0, 0, 0, [UIntPtr]::Zero)
}
Write-Output "clicked $X,$Y"
