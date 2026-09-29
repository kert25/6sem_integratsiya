# run_request.ps1 - open request from sidebar by coords, find Send via OCR, click it,
# then OCR again and print URL line + status code + test results.
# usage: powershell -File run_request.ps1 <sidebarX> <sidebarY> <name>
param([int]$SbX, [int]$SbY, [string]$Name)
$ErrorActionPreference = "Continue"
$ocr = { param($path)
    powershell -ExecutionPolicy Bypass -File "$env:TEMP\opencode\ss_ocr.ps1" -App "John's Workspace" -Path $path |
        Out-File "$env:TEMP\opencode\ocr_tmp.json" -Encoding utf8
    (Get-Content "$env:TEMP\opencode\ocr_tmp.json" -Encoding utf8 | ConvertFrom-Json)
}

powershell -ExecutionPolicy Bypass -File "$env:TEMP\opencode\ss_click.ps1" $SbX $SbY | Out-Null
Start-Sleep -Seconds 3
$w = & $ocr "$env:TEMP\opencode\pm_step1.png"
$url = ($w | Where-Object { $_.y -gt 125 -and $_.y -lt 150 -and $_.x -gt 500 -and $_.x -lt 1700 } | ForEach-Object { $_.text }) -join " "
$send = $w | Where-Object { $_.text -eq "Send" -and $_.y -gt 100 -and $_.y -lt 180 } | Select-Object -First 1
if (-not $send) { Write-Output "[$Name] SEND NOT FOUND; url=$url"; exit 1 }
Start-Sleep -Milliseconds 400
powershell -ExecutionPolicy Bypass -File "$env:TEMP\opencode\ss_click.ps1" $send.x $send.y | Out-Null
Start-Sleep -Seconds 8
$w2 = & $ocr "$env:TEMP\opencode\pm_step2_$Name.png"
$code = ($w2 | Where-Object { $_.text -match "^(200|201|204|301|400|401|403|404|405|500)$" -and $_.x -gt 1300 -and $_.y -gt 400 -and $_.y -lt 700 } | ForEach-Object { $_.text }) -join "/"
$tests = ($w2 | Where-Object { $_.text -match "^\d+/\d+$" } | ForEach-Object { $_.text }) -join ","
Write-Output "[$Name] url=$url status=$code tests=$tests"
