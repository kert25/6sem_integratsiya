# job_status.ps1 - progress of a background job: RUNNING/EXITED + elapsed + tail of its log
# usage: powershell -File job_status.ps1 -Id <pid> -Log <file> [-Tail 3]
# Elapsed is counted from the log file creation time. Log is read as UTF-8 (PYTHONUTF8 output).
# Poll loop pattern (agent, every 30 s): powershell -File _tools\gui\job_status.ps1 -Id <pid> -Log <log>
param(
    [Parameter(Mandatory = $true)][int]$Id,
    [string]$Log = "",
    [int]$Tail = 3
)
$ErrorActionPreference = "Stop"

$proc = Get-Process -Id $Id -ErrorAction SilentlyContinue
if ($proc) { $state = "RUNNING" } else { $state = "EXITED" }
$line = "$state | pid $Id"

if ($Log -and (Test-Path -LiteralPath $Log)) {
    $f = Get-Item -LiteralPath $Log
    $secs = [int]((Get-Date) - $f.CreationTime).TotalSeconds
    $line += " | ${secs}s"
    foreach ($t in @(Get-Content -LiteralPath $Log -Tail $Tail -Encoding UTF8)) {
        if ($t.Trim()) { $line += "`n  | " + $t.Trim() }
    }
} else {
    $line += " | no log"
}

Write-Output $line
