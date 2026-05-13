# Установка с нуля

## Что нужно подготовить

- Домен (любой регистратор — Beget, Namecheap, etc.)
- Аккаунт Cloudflare (бесплатный)
- Python 3.10+
- Chrome
- Node.js + npm

---

## 1. Домен и Cloudflare

1. Купи домен у регистратора
2. Зарегистрируйся на https://dash.cloudflare.com/sign-up
3. В Cloudflare → **Add a domain** → введи свой домен
4. Cloudflare покажет два nameserver'а
5. У регистратора → DNS-настройки → поставь эти NS
6. Жди статус **Active** в Cloudflare (обычно 10-30 минут)

## 2. API-токен Cloudflare

https://dash.cloudflare.com/profile/api-tokens → **Create Token** → шаблон **Edit Cloudflare Workers** → **Use template**.

Добавь дополнительные права через **+ Add more**:
- `Account → D1 → Edit`
- `Account → Email Routing Addresses → Edit`
- `Zone → Email Routing Rules → Edit`

Сохрани → скопируй токен `cfut_...` (показывают один раз).

Положи токен в переменную окружения навсегда:

```powershell
[Environment]::SetEnvironmentVariable("CLOUDFLARE_API_TOKEN", "cfut_...", "User")
```

Закрой и открой PowerShell заново.

## 3. Wrangler и pnpm

```powershell
npm install -g wrangler pnpm
```

## 4. Деплой `cloudflare_temp_email` Worker

```powershell
git clone https://github.com/dreamhunter2333/cloudflare_temp_email
cd cloudflare_temp_email\worker
```

Создай D1 базу:

```powershell
wrangler d1 create temp-email-db
```

Из вывода скопируй `database_id`.

Создай `worker/wrangler.toml` (шаблон в `wrangler.toml.template` в том же каталоге). Минимально нужно поменять:

- `database_id` — из вывода предыдущей команды
- `DEFAULT_DOMAINS` и `DOMAINS` — поставь свой домен
- `ADMIN_PASSWORDS` — придумай пароль (любая длинная строка)
- `JWT_SECRET` — случайная строка 48+ символов
- `PREFIX = "tmp"` — рекомендуется оставить именно `tmp`

Поставь зависимости и накати схему:

```powershell
pnpm install
wrangler d1 execute temp-email-db --remote --file=..\db\schema.sql
```

Деплой:

```powershell
pnpm run deploy
```

В выводе будет URL `https://<имя>.<аккаунт>.workers.dev` — сохрани его, это твой `worker_url`.

Доведи миграцию схемы:

```powershell
$W = "https://<твой-воркер>.workers.dev"
$ADMIN = "<твой-admin-password>"
curl.exe -X POST "$W/admin/db_migration" -H "x-admin-auth: $ADMIN"
```

## 5. Email Routing

В Cloudflare → твой домен → **Email Routing**:

1. **Destination Addresses** → Add → введи свой gmail → подтверди код из письма
2. **Routing rules** → у строки **Catch-all** жми три точки `...` → **Edit**
3. Action: **Send to a Worker** → выбери воркер `cloudflare_temp_email` → Save
4. Переключатель **Catch-all → Active**

Если в выборе действия нет варианта `Send to a Worker` — сначала вкладка **Destination Workers** → **Create / Add destination worker** → выбери воркер, потом возвращайся к Catch-all.

## 6. Тест почты

```powershell
$W = "https://<твой-воркер>.workers.dev"
$r = Invoke-RestMethod -Method Post -Uri "$W/api/new_address" -ContentType "application/json" -Body '{"name":"test1"}'
$r
```

Должно показать `address` и `jwt`.

Отправь себе письмо с любой почты на полученный адрес. Через 20 сек:

```powershell
$JWT = $r.jwt
Invoke-RestMethod -Uri "$W/api/mails?limit=20" -Headers @{Authorization="Bearer $JWT"}
```

Если в `results` появилось письмо — почта работает.

## 7. Клонируй авторег

```powershell
git clone https://github.com/Ibrahim-archh/aws-builder-id-ru.git aws-builder-id
cd aws-builder-id
```

## 8. Запусти автонастройку

```powershell
.\scripts\setup.ps1
```

Скрипт сам:
- проверит Python
- поставит зависимости
- определит версию Chrome и подставит её в `main.py`
- спросит `worker_url`, `domain`, `admin_password` → запишет в `config/config.yaml`
- сделает тестовый запрос к Worker

Если PowerShell ругается на политику выполнения — выполни один раз:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## 9. Запуск

Одиночная регистрация:

```powershell
python src/runners/main.py
```

Батч (несколько параллельно, с задержкой между процессами):

```powershell
python src/runners/batch_run.py
```

## 10. Результаты

| Файл | Что внутри |
|---|---|
| `accounts.jsonl` | успешные регистрации |
| `accounts_failed.jsonl` | провалы + причина (URL или exception) |

---

## Утилиты

```powershell
python scripts/switch_region.py usa         # germany / japan / usa
python scripts/switch_device.py desktop     # desktop / mobile
python scripts/check_proxy.py               # проверить прокси
python scripts/check_fingerprint.py         # посмотреть fingerprint браузера
```

## Конфиг `config/config.yaml`

```yaml
email:
  worker_url: "https://<твой-воркер>.workers.dev"
  domain: "<твой-домен>"
  prefix_length: 8
  wait_timeout: 120
  poll_interval: 5
  admin_password: "<пароль-из-wrangler.toml>"

browser:
  headless: false           # true для серверного режима без окна

region:
  current: "usa"            # germany / japan / usa
  device_type: "desktop"    # desktop / mobile
  use_proxy: false          # включи при масс-реге
  proxy_mode: "static"
  proxy_url: "socks5://user:pass@host:port"
```
