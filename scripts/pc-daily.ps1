# Daily job of the pilot's PC, run by the Windows scheduled task "PowAtlas sync"
# (docs/collecte/installation-pc.md, section 4): bring the GitHub artifacts home,
# then advance the historical backfill by one slice per source. GFS, collected on
# this PC only, is thus kept up to date. Output appended to data\pc-daily.log.
$root = Split-Path -Parent $PSScriptRoot
$pa = Join-Path $root '.venv\Scripts\powatlas.exe'
$data = Join-Path $root 'data'
$log = Join-Path $data 'pc-daily.log'
New-Item -ItemType Directory -Force -Path $data | Out-Null

function Write-Log($text) { $text | Out-File -FilePath $log -Append -Encoding utf8 }

Write-Log "=== $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') sync"
& $pa sync --data $data --env (Join-Path $root '.env') 2>&1 | ForEach-Object { Write-Log "$_" }

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
    & $pa backfill --source $s[0] --from $s[1] --to $s[2] --data $data --max-hours 1 2>&1 |
        ForEach-Object { Write-Log "$_" }
}
