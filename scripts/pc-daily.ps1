# Daily job of the pilot's PC, run by the Windows scheduled task "PowAtlas sync"
# (docs/collecte/installation-pc.md, section 4): bring the GitHub artifacts home, collect the
# observations that only answer this PC (Arpa Piemonte, file manual copies of data\pc-collect),
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

# Manual copies (powatlas collect --out data\pc-collect), if any, filed first: an older copy
# of today must not replace the one collect-pc makes next.
Write-Log "=== $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') store and collect-pc"
& $pa store --from (Join-Path $data 'pc-collect') --data $data 2>&1 | ForEach-Object { Write-Log "$_" }
Write-Log "store exit code $LASTEXITCODE"
# Observation sources of task "pc" (catalogue): today's unit straight into the archive.
& $pa collect-pc --data $data 2>&1 | ForEach-Object { Write-Log "$_" }
Write-Log "collect-pc exit code $LASTEXITCODE"

# A backfill started by hand writes the same files: never run two at once.
if (Get-Process -Name powatlas -ErrorAction SilentlyContinue) {
    Write-Log "backfill skipped: another powatlas process is running"
    exit 0
}

# Periods come from the catalogue (settings.backfill): IFS and AIFS stop at the
# last winter before the daily collection began, GFS runs up to the last published day.
foreach ($source in @('aifs-single', 'ifs-0p25', 'gfs-0p25')) {
    Write-Log "=== $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') backfill $source"
    & $pa backfill --source $source --data $data --max-hours 3 2>&1 | ForEach-Object { Write-Log "$_" }
    Write-Log "backfill $source exit code $LASTEXITCODE"
}
Write-Log "=== $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') progress"
& $pa progress --data $data 2>&1 | ForEach-Object { Write-Log "$_" }
