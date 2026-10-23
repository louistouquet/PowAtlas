# Daily job of the pilot's PC, run by the Windows scheduled task "PowAtlas sync"
# (docs/collecte/installation-pc.md, section 4): bring the GitHub artifacts home,
# then advance the historical backfill by one slice (up to 3 h) per source. GFS, collected on
# this PC only, is thus kept up to date. Output appended to data\pc-daily.log.
$root = Split-Path -Parent $PSScriptRoot
$pa = Join-Path $root '.venv\Scripts\powatlas.exe'
$data = Join-Path $root 'data'
$log = Join-Path $data 'pc-daily.log'
New-Item -ItemType Directory -Force -Path $data | Out-Null
# Python output: line by line and in UTF-8, read as such by this script.
$env:PYTHONUNBUFFERED = '1'
$env:PYTHONUTF8 = '1'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function Write-Log($text) { $text | Out-File -FilePath $log -Append -Encoding utf8 }

# Run at wake-up, the network may not be up yet: an offline backfill would
# spend the 3 attempts of each unit it reaches. Wait up to 10 minutes.
$online = $false
for ($i = 0; $i -lt 10 -and -not $online; $i++) {
    try { [void][System.Net.Dns]::GetHostAddresses('github.com'); $online = $true } catch { Start-Sleep -Seconds 60 }
}
if (-not $online) {
    Write-Log "=== $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') no network after 10 minutes: nothing done"
    exit 1
}

Write-Log "=== $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') sync"
& $pa sync --data $data --env (Join-Path $root '.env') 2>&1 | ForEach-Object { Write-Log "$_" }
Write-Log "sync exit code $LASTEXITCODE"

# A backfill started by hand writes the same files: never run two at once.
if (Get-Process -Name powatlas -ErrorAction SilentlyContinue) {
    Write-Log "backfill skipped: another powatlas process is running"
    exit 0
}

# IFS and AIFS stop at the last winter before the daily collection began
# (2026-04-30); GFS runs up to the last published day (later dates are ignored).
$slices = @(
    @('aifs-single', '2025-02-26', '2026-04-30'),
    @('ifs-0p25', '2024-02-01', '2026-04-30'),
    @('gfs-0p25', '2021-11-01', '2099-12-31')
)
foreach ($s in $slices) {
    Write-Log "=== $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') backfill $($s[0])"
    & $pa backfill --source $s[0] --from $s[1] --to $s[2] --data $data --max-hours 3 2>&1 |
        ForEach-Object { Write-Log "$_" }
    Write-Log "backfill $($s[0]) exit code $LASTEXITCODE"
}
