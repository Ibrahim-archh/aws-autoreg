# Решение проблем

## `ChromeDriver only supports Chrome version X, current is Y`

Скрипт прибит к фиксированной версии Chrome. Узнай свою:

```powershell
(Get-Item "C:\Program Files\Google\Chrome\Application\chrome.exe").VersionInfo.FileVersion
```

В `src/runners/main.py` найди строку `version_main=148` и поставь свою главную версию (например `152`).

Либо просто перезапусти `.\scripts\setup.ps1` — он сам выставит актуальную.

## `wrangler login` редиректит на `localhost:8976`, страница не работает

OAuth-сервер `wrangler` уже закрылся к моменту твоего захода. Используй API-токен напрямую:

```powershell
[Environment]::SetEnvironmentVariable("CLOUDFLARE_API_TOKEN", "cfut_...", "User")
```

Закрой и открой PowerShell. Затем:

```powershell
wrangler whoami
```

## `Authentication error [code: 10000]` при `wrangler d1 create`

У токена не хватает права на D1. Открой токен в дашборде → **Edit** → добавь `Account → D1 → Edit` → Save.

## Письмо приходит, но OTP не извлекается

В `src/services/email_service.py` функция `_extract_code` ищет код рядом с keyword'ами:

```
verification code | code is | your code | builder id | one-time password | otp
```

Если AWS поменял формулировку — добавь свой паттерн в массив `near_patterns`.

## `Invalid email` в стороннем сервисе при логине через Builder ID

Фронтенд-валидатор стороннего сервиса режет `.ru` TLD. AWS-бэкенд при этом адрес знает.

Обходы:
1. Войди сначала на https://profile.aws.amazon.com — внешний сервис потом подхватит сессию через SSO Cookie
2. Зарегай домен `.com` / `.io` / `.dev` и используй его
3. В настройках Builder ID поменяй primary email на адрес из whitelist'а сервиса

## AWS показывает CAPTCHA или банит при регистрации

Запускаешь с .ru-IP без прокси. Покупай SOCKS5 USA/EU-резидента (ASocks, ProxyEmpire, etc.) и пропиши в `config.yaml`:

```yaml
region:
  use_proxy: true
  proxy_mode: "static"
  proxy_url: "socks5://user:pass@host:port"
```

Проверь прокси:

```powershell
python scripts/check_proxy.py
```

## Скрипт сохраняет аккаунт в `accounts_failed.jsonl`

Регистрация не дошла до конца. В записи есть поле `reason`. Самые частые:

- `stuck at .../verify-otp` — код подтверждения не прошёл (возможно AWS не принял адрес или капча)
- `stuck at .../signup/` — застряло на форме ввода имени/email
- `exception: ...` — Selenium упал

Проверь скриншоты `debug_failed_click.png`, `error_screenshot.png` в корне проекта (если включил их в коде).

## `pnpm deploy` падает с `ERR_PNPM_CANNOT_DEPLOY`

Это встроенная команда pnpm, не наша. Запускай скрипт из package.json:

```powershell
pnpm run deploy
```

Или напрямую:

```powershell
npx wrangler deploy --minify
```

## Перевод (русификация)

После обновления оригинального репо если вдруг появятся новые куски на китайском:

```powershell
python scripts/russify.py
python scripts/russify_v2.py
```

## Стоимость

| | |
|---|---|
| Домен `.ru` | ~150₽/год |
| Cloudflare (Workers + D1 + Email Routing) | бесплатно до 100k запросов/день |
| Прокси (для масс-реги) | ~$3-5/мес |
