# ss_scroll.ps1 - scroll N notches at screen position (negative = down)
# usage: powershell -File ss_scroll.ps1 X Y [-Notches 3] [-Up]
param([int]$X, [int]$Y, [int]$Notches = 3, [switch]$Up)
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class S {
    [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern void mouse_event(uint f, uint dx, uint dy, uint data, UIntPtr extra);
}
"@
$null = [S]::SetProcessDPIAware()
$null = [S]::SetCursorPos($X, $Y)
Start-Sleep -Milliseconds 100
$delta = if ($Up) { $Notches * 120 } else { -$Notches * 120 }
$null = [S]::mouse_event(0x0800, 0, 0, $delta, [UIntPtr]::Zero)
Write-Output "scrolled at $X,$Y delta=$delta"
