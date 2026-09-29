# ss_ocr.ps1 - screenshot + Windows OCR; prints JSON [{text,x,y},...] in ABSOLUTE screen coords
# usage: powershell -File ss_ocr.ps1 [-Path out.png] [-App windowTitleLike] [-NoSave]
param(
    [string]$Path = "$env:TEMP\opencode\screen.png",
    [string]$App = "",
    [switch]$NoSave
)
$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Storage.StorageFile, Windows.Storage, ContentType = WindowsRuntime]
$null = [Windows.Storage.IStorageFile, Windows.Storage, ContentType = WindowsRuntime]
$null = [Windows.Media.Ocr.OcrEngine, Windows.Media.Ocr, ContentType = WindowsRuntime]
$null = [Windows.Graphics.Imaging.BitmapDecoder, Windows.Graphics.Imaging, ContentType = WindowsRuntime]
$null = [Windows.Globalization.Language, Windows.Globalization, ContentType = WindowsRuntime]

Add-Type @"
using System;
using System.Runtime.InteropServices;
public class U32 {
    [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L; public int T; public int R; public int B; }
}
"@
$null = [U32]::SetProcessDPIAware()

$asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
    $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' })[0]
function Await($WinRtTask, $ResultType) {
    $asTask = $asTaskGeneric.MakeGenericMethod($ResultType)
    $netTask = $asTask.Invoke($null, @($WinRtTask))
    $netTask.Wait(-1) | Out-Null
    $netTask.Result
}

$originX = 0; $originY = 0; $w = 0; $h = 0
if ($App) {
    $proc = Get-Process | Where-Object { $_.MainWindowHandle -ne 0 -and $_.MainWindowTitle -like "*$App*" } | Select-Object -First 1
    if (-not $proc) { Write-Output "[]"; exit 1 }
    $r = New-Object U32+RECT
    $null = [U32]::GetWindowRect($proc.MainWindowHandle, [ref]$r)
    $originX = $r.L; $originY = $r.T; $w = $r.R - $r.L; $h = $r.B - $r.T
} else {
    $vs = [System.Windows.Forms.SystemInformation]::VirtualScreen
    $originX = $vs.X; $originY = $vs.Y; $w = $vs.Width; $h = $vs.Height
}
if ($w -lt 1 -or $h -lt 1) { Write-Output "[]"; exit 1 }

$bmp = New-Object System.Drawing.Bitmap($w, $h)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($originX, $originY, 0, 0, $bmp.Size)
if (-not $NoSave) { $bmp.Save($Path, [System.Drawing.Imaging.ImageFormat]::Png) }
$g.Dispose(); $bmp.Dispose()

$lang = [Windows.Globalization.Language]::new("en-US")
$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage($lang)
if (-not $engine) { $engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages() }
$fs = [System.IO.File]::OpenRead($Path)
$ras = [System.IO.WindowsRuntimeStreamExtensions]::AsRandomAccessStream($fs)
$decoder = Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($ras)) ([Windows.Graphics.Imaging.BitmapDecoder])
$soft = Await ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
$fs.Close()
$ocr = Await ($engine.RecognizeAsync($soft)) ([Windows.Media.Ocr.OcrResult])

$words = @()
foreach ($line in $ocr.Lines) {
    foreach ($word in $line.Words) {
        $rect = $word.BoundingRect
        $words += [pscustomobject]@{
            text = $word.Text
            x    = [int]($originX + $rect.X + $rect.Width / 2)
            y    = [int]($originY + $rect.Y + $rect.Height / 2)
        }
    }
}
Write-Output ($words | ConvertTo-Json -Compress)
