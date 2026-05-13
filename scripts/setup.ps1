# =====================================================================
# AWS Builder ID авторег — автоматическая настройка
#
# Использование (из корня репозитория):
#   .\scripts\setup.ps1
#
# Если PowerShell ругается на политику выполнения:
#   Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
# =====================================================================

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Write-Ok {
    param([string]$Message)
    Write-Host "  [OK] $Message" -ForegroundColor Green
}

function Write-Warn {
    param([string]$Message)
    Write-Host "  [!] $Message" -ForegroundColor Yellow
}

function Write-Err {
    param([string]$Message)
    Write-Host "  [X] $Message" -ForegroundColor Red
}

# Определяем корень проекта (родитель папки scripts/)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot

Write-Host ""
Write-Host "======================================================" -ForegroundColor Magenta
Write-Host "   AWS Builder ID Авторег — автоматическая настройка" -ForegroundColor Magenta
Write-Host "======================================================" -ForegroundColor Magenta
Write-Host "Проект: $ProjectRoot"

# ---------------------------------------------------------------------
# 1. Проверка Python
# ---------------------------------------------------------------------
Write-Step "Шаг 1/6: Проверка Python"

$pythonVer = $null
try {
    $pythonVer = (python --version 2>&1).Trim()
} catch {
    Write-Err "Python не найден в PATH"
    Write-Host "  Установи Python 3.10+ с https://python.org/downloads и поставь галку Add to PATH"
    exit 1
}

if ($pythonVer -match "Python (\d+)\.(\d+)") {
    $major = [int]$Matches[1]; $minor = [int]$Matches[2]
    if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 10)) {
        Write-Err "Нужен Python 3.10+, у тебя $pythonVer"
        exit 1
    }
    Write-Ok "$pythonVer"
}

# ---------------------------------------------------------------------
# 2. Установка зависимостей
# ---------------------------------------------------------------------
Write-Step "Шаг 2/6: Установка Python-зависимостей"

python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt --quiet
python -m pip install --upgrade undetected-chromedriver selenium --quiet
Write-Ok "pip install прошёл"

# ---------------------------------------------------------------------
# 3. Определение версии Chrome
# ---------------------------------------------------------------------
Write-Step "Шаг 3/6: Проверка версии Chrome"

$chromePaths = @(
    "C:\Program Files\Google\Chrome\Application\chrome.exe",
    "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
)

$chromeExe = $null
foreach ($p in $chromePaths) {
    if (Test-Path $p) { $chromeExe = $p; break }
}

if (-not $chromeExe) {
    Write-Warn "Chrome не найден в стандартных местах. Скрипт продолжит, но укажи version_main вручную в src/runners/main.py"
    $chromeMajor = $null
} else {
    $chromeFullVer = (Get-Item $chromeExe).VersionInfo.FileVersion
    $chromeMajor = ($chromeFullVer -split '\.')[0]
    Write-Ok "Chrome $chromeFullVer (major = $chromeMajor)"
}

# ---------------------------------------------------------------------
# 4. Обновление version_main= в main.py
# ---------------------------------------------------------------------
Write-Step "Шаг 4/6: Синхронизация version_main с твоим Chrome"

$mainPy = Join-Path $ProjectRoot "src\runners\main.py"
if ((Test-Path $mainPy) -and $chromeMajor) {
    $content = Get-Content $mainPy -Raw -Encoding UTF8
    $updated = $content -replace "version_main=\d+", "version_main=$chromeMajor"
    if ($updated -ne $content) {
        Set-Content -Path $mainPy -Value $updated -Encoding UTF8 -NoNewline
        Write-Ok "version_main установлен в $chromeMajor"
    } else {
        Write-Ok "version_main уже актуален"
    }
} else {
    Write-Warn "Пропущено"
}

# ---------------------------------------------------------------------
# 5. Конфигурация config.yaml
# ---------------------------------------------------------------------
Write-Step "Шаг 5/6: Настройка config/config.yaml"

$configPath = Join-Path $ProjectRoot "config\config.yaml"
if (-not (Test-Path $configPath)) {
    Write-Err "config/config.yaml не найден"
    exit 1
}

Write-Host ""
Write-Host "  Сейчас спрошу три значения для подключения к твоему cloudflare_temp_email Worker."
Write-Host "  Если ты ещё не разворачивал Worker — пропусти этот шаг (Ctrl+C), сначала пройди гайд в README.md, потом запусти setup.ps1 снова."
Write-Host ""

$workerUrl = Read-Host "  worker_url (например https://my-tempmail.username.workers.dev)"
$domain = Read-Host "  domain (например myrealagent.ru)"
$adminPwd = Read-Host "  admin_password (из ADMIN_PASSWORDS в wrangler.toml Worker'а)"

if ($workerUrl -and $domain -and $adminPwd) {
    $cfg = Get-Content $configPath -Raw -Encoding UTF8
    $cfg = $cfg -replace 'worker_url:\s*"[^"]*"', "worker_url: `"$workerUrl`""
    $cfg = $cfg -replace 'domain:\s*"[^"]*"', "domain: `"$domain`""
    $cfg = $cfg -replace 'admin_password:\s*"[^"]*"', "admin_password: `"$adminPwd`""
    Set-Content -Path $configPath -Value $cfg -Encoding UTF8 -NoNewline
    Write-Ok "config.yaml обновлён"
} else {
    Write-Warn "Один из ответов пустой — config.yaml не изменён. Заполни вручную и запусти заново."
}

# ---------------------------------------------------------------------
# 6. Проверка соединения с Worker
# ---------------------------------------------------------------------
Write-Step "Шаг 6/6: Проверка соединения с твоим Worker"

if ($workerUrl) {
    try {
        $resp = Invoke-RestMethod -Method Post -Uri "$workerUrl/api/new_address" `
            -ContentType "application/json" `
            -Body '{"name":"setupcheck"}' -TimeoutSec 15
        if ($resp.jwt) {
            Write-Ok "Worker ответил, JWT получен. Создан тестовый ящик: $($resp.address)"
            Write-Host "    (он останется в БД но место не жрёт)"
        } else {
            Write-Warn "Worker ответил, но без jwt. Проверь конфиг Worker'а (DOMAINS должен включать $domain)"
        }
    } catch {
        Write-Err "Не дозвонились до Worker'а: $_"
        Write-Host "    Проверь worker_url и что Worker задеплоен"
    }
}

# ---------------------------------------------------------------------
# Финал
# ---------------------------------------------------------------------
Write-Host ""
Write-Host "======================================================" -ForegroundColor Magenta
Write-Host "   Настройка завершена!" -ForegroundColor Magenta
Write-Host "======================================================" -ForegroundColor Magenta
Write-Host ""
Write-Host "Запуск одиночной регистрации:" -ForegroundColor Yellow
Write-Host "  python src/runners/main.py" -ForegroundColor White
Write-Host ""
Write-Host "Запуск батча (несколько параллельно):" -ForegroundColor Yellow
Write-Host "  python src/runners/batch_run.py" -ForegroundColor White
Write-Host ""
Write-Host "Файлы с результатами:"
Write-Host "  accounts.jsonl         — успешные регистрации"
Write-Host "  accounts_failed.jsonl  — провалы с причиной"
Write-Host ""
Write-Host "Полная инструкция: README.md" -ForegroundColor Cyan
Write-Host ""
