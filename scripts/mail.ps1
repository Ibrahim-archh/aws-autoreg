# =====================================================================
# Просмотр писем и извлечение OTP-кодов из cloudflare_temp_email Worker
#
# Использование:
#   .\scripts\mail.ps1                              — последние 10 писем (любые адреса)
#   .\scripts\mail.ps1 tmpXXX@myrealagent.ru        — письма конкретного адреса
#   .\scripts\mail.ps1 -Last 20                     — последние 20 писем
#   .\scripts\mail.ps1 -Address tmpXXX@... -Last 5  — комбо
# =====================================================================

param(
    [Parameter(Position=0)]
    [string]$Address = "",

    [int]$Last = 10
)

# Берём worker_url и admin_password из config.yaml
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$ConfigPath = Join-Path $ProjectRoot "config\config.yaml"

if (-not (Test-Path $ConfigPath)) {
    Write-Host "config/config.yaml не найден. Запусти сначала setup.ps1" -ForegroundColor Red
    exit 1
}

$cfg = Get-Content $ConfigPath -Raw -Encoding UTF8
$workerUrl = if ($cfg -match 'worker_url:\s*"([^"]+)"') { $Matches[1] }
$adminPwd = if ($cfg -match 'admin_password:\s*"([^"]+)"') { $Matches[1] }

if (-not $workerUrl -or -not $adminPwd) {
    Write-Host "В config.yaml не задан worker_url или admin_password" -ForegroundColor Red
    exit 1
}

# Тянем письма через admin API
$url = "$workerUrl/admin/mails?limit=$Last&offset=0"
try {
    $resp = Invoke-RestMethod -Uri $url -Headers @{ "x-admin-auth" = $adminPwd } -TimeoutSec 15
} catch {
    Write-Host "Запрос упал: $_" -ForegroundColor Red
    exit 1
}

$mails = if ($resp.results) { $resp.results } else { $resp }
if (-not $mails -or $mails.Count -eq 0) {
    Write-Host "Писем нет" -ForegroundColor Yellow
    exit 0
}

# Фильтр по адресу
if ($Address) {
    $mails = $mails | Where-Object { $_.address -eq $Address }
    if (-not $mails) {
        Write-Host "Для $Address писем нет" -ForegroundColor Yellow
        exit 0
    }
}

# Печатаем — новые сверху
foreach ($m in $mails) {
    $raw = $m.raw
    $addr = $m.address
    $created = $m.created_at

    # Subject из заголовка
    $subj = "(no subject)"
    if ($raw -match '(?im)^Subject:\s*(.+)$') {
        $subj = $Matches[1].Trim()
    }

    # From из заголовка
    $from = "(unknown)"
    if ($raw -match '(?im)^From:\s*(.+)$') {
        $from = $Matches[1].Trim()
    }

    # Извлечь 6-значный код (приоритет: рядом с keyword'ом)
    $code = $null
    $keywordPatterns = @(
        '(?i)(?:verification\s+code|code\s+is|your\s+code|builder\s+id|one[- ]?time\s+(?:password|code)|otp)\D{0,80}?(\d{6})\b',
        '(?i)\b(\d{6})\D{0,80}?(?:is\s+your\s+(?:verification|builder|aws|amazon|one[- ]?time)|verification\s+code|builder\s+id|expires?)'
    )
    foreach ($p in $keywordPatterns) {
        if ($raw -match $p) {
            $candidate = $Matches[1]
            if ($candidate -notmatch '^(\d)\1{5}$' -and -not ($candidate -match '^(19|20)\d{4}$')) {
                $code = $candidate
                break
            }
        }
    }
    if (-not $code) {
        $allMatches = [regex]::Matches($raw, '\b(\d{6})\b')
        foreach ($mm in $allMatches) {
            $c = $mm.Groups[1].Value
            if ($c -notmatch '^(\d)\1{5}$' -and -not ($c -match '^(19|20)\d{4}$')) {
                $code = $c
                break
            }
        }
    }

    Write-Host ""
    Write-Host "[$created] $addr" -ForegroundColor Cyan
    Write-Host "  From:    $from"
    Write-Host "  Subject: $subj"
    if ($code) {
        Write-Host "  CODE:    $code" -ForegroundColor Green
    } else {
        Write-Host "  CODE:    (не найден)" -ForegroundColor Yellow
    }
}
Write-Host ""
